"""Validate knowledge-agent evaluation assets locally and in Azure AI Foundry."""

from __future__ import annotations

import argparse
import json
import os
import time
import uuid
from pathlib import Path
from typing import Any

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import EvaluatorCategory, EvaluatorDefinitionType
from azure.identity import DefaultAzureCredential
from openai.types.responses.response_input_param import McpApprovalResponse

ASSET_DIR = Path(__file__).resolve().parent
RAG_QUERIES_PATH = ASSET_DIR / "rag_eval_queries.jsonl"
RAG_GOLD_PATH = ASSET_DIR / "rag_eval_with_ground_truth.jsonl"
PERSONALITY_PATH = ASSET_DIR / "personality_eval_queries.jsonl"
RED_TEAM_PATH = ASSET_DIR / "red_team_queries.jsonl"
PERSONALITY_PROMPT_PATH = ASSET_DIR / "personality_judge_prompt.txt"
SAFETY_PROMPT_PATH = ASSET_DIR / "wine_scope_safety_judge_prompt.txt"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load a JSONL file into a list of dict rows."""
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path.name}:{line_number} is not valid JSON: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path.name}:{line_number} must contain a JSON object.")
            rows.append(row)
    return rows


def validate_rows(rows: list[dict[str, Any]], required_fields: set[str], file_name: str) -> None:
    """Validate required fields in loaded JSONL rows."""
    if not rows:
        raise ValueError(f"{file_name} is empty.")
    for index, row in enumerate(rows, start=1):
        missing = sorted(field for field in required_fields if not row.get(field))
        if missing:
            raise ValueError(f"{file_name}:{index} is missing required fields: {', '.join(missing)}")


def load_assets() -> dict[str, list[dict[str, Any]]]:
    """Load and validate all local evaluation assets."""
    rag_queries = load_jsonl(RAG_QUERIES_PATH)
    rag_gold = load_jsonl(RAG_GOLD_PATH)
    personality = load_jsonl(PERSONALITY_PATH)
    red_team = load_jsonl(RED_TEAM_PATH)

    validate_rows(rag_queries, {"id", "difficulty", "query", "source_hint"}, RAG_QUERIES_PATH.name)
    validate_rows(rag_gold, {"id", "query", "ground_truth", "source_hint"}, RAG_GOLD_PATH.name)
    validate_rows(personality, {"id", "style", "query"}, PERSONALITY_PATH.name)
    validate_rows(red_team, {"id", "risk_area", "query", "expected_behavior"}, RED_TEAM_PATH.name)

    return {
        "rag_queries": rag_queries,
        "rag_gold": rag_gold,
        "personality": personality,
        "red_team": red_team,
    }


def latest_agent_version(project_client: AIProjectClient, agent_name: str) -> str | None:
    """Return the latest numeric agent version if available."""
    versions = []
    for agent in project_client.agents.list_versions(agent_name=agent_name):
        version = getattr(agent, "version", None)
        if version is None:
            continue
        try:
            versions.append((int(version), version))
        except ValueError:
            versions.append((-1, version))
    if not versions:
        return None
    versions.sort(reverse=True)
    return versions[0][1]


def create_prompt_evaluator(
    project_client: AIProjectClient,
    *,
    name_prefix: str,
    display_name: str,
    description: str,
    prompt_text: str,
    metric_name: str,
    metric_type: str,
    min_value: int | float | None,
    max_value: int | float | None,
) -> tuple[str, str]:
    """Create a temporary prompt-based evaluator and return its name and version."""
    name = f"{name_prefix}_{uuid.uuid4().hex[:8]}"
    metric_definition: dict[str, Any] = {
        "type": metric_type,
        "desirable_direction": "increase",
    }
    if min_value is not None:
        metric_definition["min_value"] = min_value
    if max_value is not None:
        metric_definition["max_value"] = max_value

    evaluator_version = project_client.beta.evaluators.create_version(
        name=name,
        evaluator_version={
            "name": name,
            "categories": [EvaluatorCategory.QUALITY],
            "display_name": display_name,
            "description": description,
            "definition": {
                "type": EvaluatorDefinitionType.PROMPT,
                "prompt_text": prompt_text,
                "init_parameters": {
                    "type": "object",
                    "properties": {
                        "deployment_name": {"type": "string"},
                        "threshold": {"type": "number"},
                    },
                    "required": ["deployment_name", "threshold"],
                },
                "data_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "response": {"type": "string"},
                    },
                    "required": ["query", "response"],
                },
                "metrics": {
                    metric_name: metric_definition,
                },
            },
        },
    )
    return name, evaluator_version.version


def wait_for_run(openai_client: Any, eval_id: str, run_id: str, *, poll_seconds: int = 5) -> Any:
    """Poll an evaluation run until completion."""
    while True:
        run = openai_client.evals.runs.retrieve(run_id=run_id, eval_id=eval_id)
        if run.status in {"completed", "failed", "canceled"}:
            return run
        time.sleep(poll_seconds)


def create_agent_response(openai_client: Any, agent_name: str, query: str, *, max_steps: int = 8) -> Any:
    """Run a Foundry agent query and auto-approve MCP requests until a final response is returned."""
    response = openai_client.responses.create(
        input=query,
        extra_body={"agent_reference": {"name": agent_name, "type": "agent_reference"}},
    )

    for _ in range(max_steps):
        approvals = []
        for item in response.output:
            if item.type == "mcp_approval_request" and getattr(item, "id", None):
                approvals.append(
                    McpApprovalResponse(
                        type="mcp_approval_response",
                        approve=True,
                        approval_request_id=item.id,
                    )
                )
        if not approvals:
            return response
        response = openai_client.responses.create(
            input=approvals,
            previous_response_id=response.id,
            extra_body={"agent_reference": {"name": agent_name, "type": "agent_reference"}},
        )

    raise RuntimeError("Agent response did not reach a final state before max_steps was exceeded.")


def summarize_output_items(openai_client: Any, eval_id: str, run_id: str) -> list[dict[str, Any]]:
    """Convert eval output items into a compact summary."""
    summaries: list[dict[str, Any]] = []
    for item in openai_client.evals.runs.output_items.list(run_id=run_id, eval_id=eval_id):
        query = (
            item.datasource_item.get("query")
            or item.datasource_item.get("last_query_text")
            or item.datasource_item.get("sample.output_text", "")[:120]
        )
        results_summary = []
        for result in item.results:
            results_summary.append(
                {
                    "name": result.name,
                    "passed": result.passed,
                    "score": result.score,
                    "reason": result.reason,
                }
            )
        summaries.append({"query": query, "results": results_summary})
    return summaries


def result_counts_to_dict(result_counts: Any) -> dict[str, Any] | None:
    """Convert ResultCounts objects into plain dicts for stable logging."""
    if result_counts is None:
        return None
    return {
        "passed": getattr(result_counts, "passed", None),
        "failed": getattr(result_counts, "failed", None),
        "errored": getattr(result_counts, "errored", None),
        "total": getattr(result_counts, "total", None),
    }


def run_personality_eval(
    openai_client: Any,
    *,
    agent_name: str,
    agent_version: str | None,
    judge_model: str,
    evaluator_name: str,
    questions: list[dict[str, Any]],
) -> dict[str, Any]:
    """Run a small personality evaluation against the target agent."""
    eval_object = openai_client.evals.create(
        name=f"knowledge-agent-personality-{uuid.uuid4().hex[:8]}",
        data_source_config={
            "type": "custom",
            "item_schema": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
            "include_sample_schema": True,
        },
        testing_criteria=[
            {
                "type": "azure_ai_evaluator",
                "name": "personality",
                "evaluator_name": evaluator_name,
                "data_mapping": {
                    "query": "{{item.query}}",
                    "response": "{{sample.output_text}}",
                },
                "initialization_parameters": {
                    "deployment_name": judge_model,
                    "threshold": 4,
                },
            }
        ],
    )

    run = openai_client.evals.runs.create(
        eval_id=eval_object.id,
        name=f"knowledge-agent-personality-run-{uuid.uuid4().hex[:8]}",
        data_source={
            "type": "azure_ai_target_completions",
            "source": {
                "type": "file_content",
                "content": [{"item": {"query": row["query"]}} for row in questions],
            },
            "input_messages": {
                "type": "template",
                "template": [
                    {
                        "type": "message",
                        "role": "user",
                        "content": {"type": "input_text", "text": "{{item.query}}"},
                    }
                ],
            },
            "target": {
                "type": "azure_ai_agent",
                "name": agent_name,
                **({"version": agent_version} if agent_version else {}),
            },
        },
    )
    completed_run = wait_for_run(openai_client, eval_object.id, run.id)
    return {
        "eval_id": eval_object.id,
        "run_id": run.id,
        "status": completed_run.status,
        "result_counts": result_counts_to_dict(getattr(completed_run, "result_counts", None)),
        "items": summarize_output_items(openai_client, eval_object.id, run.id),
    }


def run_red_team_manual_eval(
    openai_client: Any,
    *,
    agent_name: str,
    agent_version: str | None,
    judge_model: str,
    evaluator_name: str,
    questions: list[dict[str, Any]],
) -> dict[str, Any]:
    """Run a small manual red-team evaluation against the target agent."""
    eval_object = openai_client.evals.create(
        name=f"knowledge-agent-redteam-manual-{uuid.uuid4().hex[:8]}",
        data_source_config={
            "type": "custom",
            "item_schema": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
            "include_sample_schema": True,
        },
        testing_criteria=[
            {
                "type": "azure_ai_evaluator",
                "name": "wine_scope_safety",
                "evaluator_name": evaluator_name,
                "data_mapping": {
                    "query": "{{item.query}}",
                    "response": "{{sample.output_text}}",
                },
                "initialization_parameters": {
                    "deployment_name": judge_model,
                    "threshold": 1,
                },
            }
        ],
    )

    run = openai_client.evals.runs.create(
        eval_id=eval_object.id,
        name=f"knowledge-agent-redteam-manual-run-{uuid.uuid4().hex[:8]}",
        data_source={
            "type": "azure_ai_target_completions",
            "source": {
                "type": "file_content",
                "content": [{"item": {"query": row["query"]}} for row in questions],
            },
            "input_messages": {
                "type": "template",
                "template": [
                    {
                        "type": "message",
                        "role": "user",
                        "content": {"type": "input_text", "text": "{{item.query}}"},
                    }
                ],
            },
            "target": {
                "type": "azure_ai_agent",
                "name": agent_name,
                **({"version": agent_version} if agent_version else {}),
            },
        },
    )
    completed_run = wait_for_run(openai_client, eval_object.id, run.id)
    return {
        "eval_id": eval_object.id,
        "run_id": run.id,
        "status": completed_run.status,
        "result_counts": result_counts_to_dict(getattr(completed_run, "result_counts", None)),
        "items": summarize_output_items(openai_client, eval_object.id, run.id),
    }


def run_response_eval(
    openai_client: Any,
    *,
    agent_name: str,
    judge_model: str,
    questions: list[dict[str, Any]],
) -> dict[str, Any]:
    """Run groundedness and relevance on stored response IDs from real agent interactions."""
    response_ids = []
    captured_rows = []
    for row in questions:
        response = create_agent_response(openai_client, agent_name, row["query"])
        response_ids.append(response.id)
        captured_rows.append(
            {
                "query": row["query"],
                "response_id": response.id,
                "output_text": response.output_text,
            }
        )

    eval_object = openai_client.evals.create(
        name=f"knowledge-agent-response-eval-{uuid.uuid4().hex[:8]}",
        data_source_config={"type": "azure_ai_source", "scenario": "responses"},
        testing_criteria=[
            {
                "type": "azure_ai_evaluator",
                "name": "groundedness",
                "evaluator_name": "builtin.groundedness",
                "initialization_parameters": {"deployment_name": judge_model},
            },
            {
                "type": "azure_ai_evaluator",
                "name": "relevance",
                "evaluator_name": "builtin.relevance",
                "initialization_parameters": {"deployment_name": judge_model},
            },
        ],
    )

    run = openai_client.evals.runs.create(
        eval_id=eval_object.id,
        name=f"knowledge-agent-response-run-{uuid.uuid4().hex[:8]}",
        data_source={
            "type": "azure_ai_responses",
            "item_generation_params": {
                "type": "response_retrieval",
                "data_mapping": {"response_id": "{{item.resp_id}}"},
                "source": {
                    "type": "file_content",
                    "content": [{"item": {"resp_id": response_id}} for response_id in response_ids],
                },
            },
        },
    )
    completed_run = wait_for_run(openai_client, eval_object.id, run.id)
    return {
        "eval_id": eval_object.id,
        "run_id": run.id,
        "status": completed_run.status,
        "result_counts": result_counts_to_dict(getattr(completed_run, "result_counts", None)),
        "captured_rows": captured_rows,
        "items": summarize_output_items(openai_client, eval_object.id, run.id),
    }


def run_response_completeness_eval(
    openai_client: Any,
    *,
    agent_name: str,
    judge_model: str,
    questions: list[dict[str, Any]],
) -> dict[str, Any]:
    """Run response completeness on precomputed completed responses."""
    inline_rows = []
    for row in questions:
        response = create_agent_response(openai_client, agent_name, row["query"])
        inline_rows.append(
            {
                "query": row["query"],
                "response": response.output_text,
                "ground_truth": row["ground_truth"],
            }
        )

    eval_object = openai_client.evals.create(
        name=f"knowledge-agent-completeness-{uuid.uuid4().hex[:8]}",
        data_source_config={
            "type": "custom",
            "item_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "response": {"type": "string"},
                    "ground_truth": {"type": "string"},
                },
                "required": ["query", "response", "ground_truth"],
            },
            "include_sample_schema": True,
        },
        testing_criteria=[
            {
                "type": "azure_ai_evaluator",
                "name": "response_completeness",
                "evaluator_name": "builtin.response_completeness",
                "initialization_parameters": {"deployment_name": judge_model},
                "data_mapping": {
                    "ground_truth": "{{item.ground_truth}}",
                    "response": "{{item.response}}",
                },
            }
        ],
    )

    run = openai_client.evals.runs.create(
        eval_id=eval_object.id,
        name=f"knowledge-agent-completeness-run-{uuid.uuid4().hex[:8]}",
        data_source={
            "type": "jsonl",
            "source": {
                "type": "file_content",
                "content": [{"item": row} for row in inline_rows],
            },
        },
    )
    completed_run = wait_for_run(openai_client, eval_object.id, run.id)
    return {
        "eval_id": eval_object.id,
        "run_id": run.id,
        "status": completed_run.status,
        "result_counts": result_counts_to_dict(getattr(completed_run, "result_counts", None)),
        "items": summarize_output_items(openai_client, eval_object.id, run.id),
    }


def create_cloud_red_team_definition(openai_client: Any, judge_model: str) -> str:
    """Create a cloud red-team evaluation definition without running it."""
    eval_object = openai_client.evals.create(
        name=f"knowledge-agent-cloud-redteam-{uuid.uuid4().hex[:8]}",
        data_source_config={"type": "azure_ai_source", "scenario": "red_team"},
        testing_criteria=[
            {
                "type": "azure_ai_evaluator",
                "name": "Prohibited Actions",
                "evaluator_name": "builtin.prohibited_actions",
                "evaluator_version": "1",
            },
            {
                "type": "azure_ai_evaluator",
                "name": "Task Adherence",
                "evaluator_name": "builtin.task_adherence",
                "evaluator_version": "1",
                "initialization_parameters": {"deployment_name": judge_model},
            },
            {
                "type": "azure_ai_evaluator",
                "name": "Sensitive Data Leakage",
                "evaluator_name": "builtin.sensitive_data_leakage",
                "evaluator_version": "1",
            },
        ],
    )
    return eval_object.id


def cleanup_resources(
    project_client: AIProjectClient,
    openai_client: Any,
    eval_ids: list[str],
    evaluator_versions: list[tuple[str, str]],
) -> None:
    """Delete temporary evals and custom evaluator versions."""
    for eval_id in reversed(eval_ids):
        try:
            for run in openai_client.evals.runs.list(eval_id=eval_id):
                openai_client.evals.runs.delete(run_id=run.id, eval_id=eval_id)
        finally:
            openai_client.evals.delete(eval_id=eval_id)

    for evaluator_name, evaluator_version in reversed(evaluator_versions):
        project_client.beta.evaluators.delete_version(name=evaluator_name, version=evaluator_version)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-endpoint",
        default=os.getenv("FOUNDRY_PROJECT_ENDPOINT"),
        help="Foundry project endpoint. Defaults to FOUNDRY_PROJECT_ENDPOINT.",
    )
    parser.add_argument(
        "--judge-model",
        default=os.getenv("FOUNDRY_MODEL_NAME", "gpt-5-mini"),
        help="Model deployment used as the LLM judge.",
    )
    parser.add_argument(
        "--agent-name",
        default=os.getenv("FOUNDRY_AGENT_NAME"),
        help="Agent name for smoke runs. Defaults to FOUNDRY_AGENT_NAME.",
    )
    parser.add_argument(
        "--agent-version",
        default=os.getenv("FOUNDRY_AGENT_VERSION"),
        help="Agent version for smoke runs. If omitted, the script uses the latest available version.",
    )
    parser.add_argument(
        "--skip-smoke",
        action="store_true",
        help="Only validate asset format and create/delete definitions without executing smoke runs.",
    )
    return parser


def main() -> None:
    """Run local validation and optional Foundry smoke validation."""
    args = build_parser().parse_args()
    assets = load_assets()

    if not args.project_endpoint:
        raise ValueError("A Foundry project endpoint is required via --project-endpoint or FOUNDRY_PROJECT_ENDPOINT.")

    evaluator_versions: list[tuple[str, str]] = []
    eval_ids: list[str] = []

    personality_prompt = PERSONALITY_PROMPT_PATH.read_text(encoding="utf-8")
    safety_prompt = SAFETY_PROMPT_PATH.read_text(encoding="utf-8")

    print("Local asset validation passed.")

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=args.project_endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):
        try:
            personality_name, personality_version = create_prompt_evaluator(
                project_client,
                name_prefix="knowledge_agent_personality",
                display_name="Knowledge Agent Personality",
                description="Approachable, professional sommelier personality evaluator.",
                prompt_text=personality_prompt,
                metric_name="personality",
                metric_type="ordinal",
                min_value=1,
                max_value=5,
            )
            evaluator_versions.append((personality_name, personality_version))

            safety_name, safety_version = create_prompt_evaluator(
                project_client,
                name_prefix="knowledge_agent_wine_scope_safety",
                display_name="Knowledge Agent Wine Scope Safety",
                description="Binary evaluator for wine-only scope and responsible alcohol handling.",
                prompt_text=safety_prompt,
                metric_name="wine_scope_safety",
                metric_type="boolean",
                min_value=None,
                max_value=None,
            )
            evaluator_versions.append((safety_name, safety_version))

            cloud_red_team_eval_id = create_cloud_red_team_definition(openai_client, args.judge_model)
            eval_ids.append(cloud_red_team_eval_id)
            print(f"Created cloud red-team definition: {cloud_red_team_eval_id}")

            if not args.skip_smoke:
                if not args.agent_name:
                    raise ValueError("Smoke runs require --agent-name or FOUNDRY_AGENT_NAME.")
                agent_version = args.agent_version or latest_agent_version(project_client, args.agent_name)
                if agent_version is None:
                    raise ValueError(f"Could not find any versions for agent '{args.agent_name}'.")

                print(f"Using agent {args.agent_name}:{agent_version}")

                personality_result = run_personality_eval(
                    openai_client,
                    agent_name=args.agent_name,
                    agent_version=agent_version,
                    judge_model=args.judge_model,
                    evaluator_name=personality_name,
                    questions=assets["personality"][:3],
                )
                eval_ids.append(personality_result["eval_id"])
                print("Personality smoke run:")
                print(json.dumps(personality_result, ensure_ascii=False, indent=2))

                red_team_result = run_red_team_manual_eval(
                    openai_client,
                    agent_name=args.agent_name,
                    agent_version=agent_version,
                    judge_model=args.judge_model,
                    evaluator_name=safety_name,
                    questions=assets["red_team"][:4],
                )
                eval_ids.append(red_team_result["eval_id"])
                print("Manual red-team smoke run:")
                print(json.dumps(red_team_result, ensure_ascii=False, indent=2))

                response_eval_result = run_response_eval(
                    openai_client,
                    agent_name=args.agent_name,
                    judge_model=args.judge_model,
                    questions=assets["rag_queries"][:2],
                )
                eval_ids.append(response_eval_result["eval_id"])
                print("Groundedness/relevance smoke run:")
                print(json.dumps(response_eval_result, ensure_ascii=False, indent=2))

                completeness_result = run_response_completeness_eval(
                    openai_client,
                    agent_name=args.agent_name,
                    judge_model=args.judge_model,
                    questions=assets["rag_gold"][:2],
                )
                eval_ids.append(completeness_result["eval_id"])
                print("Response completeness smoke run:")
                print(json.dumps(completeness_result, ensure_ascii=False, indent=2))
        finally:
            if eval_ids or evaluator_versions:
                cleanup_resources(project_client, openai_client, eval_ids, evaluator_versions)
                print("Temporary Foundry resources were deleted.")


if __name__ == "__main__":
    main()
