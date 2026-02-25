"""Generate rich PDF documents about wine topics using Azure OpenAI."""

import argparse
import base64
import json
import os
import random
import re
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from pathlib import Path
from typing import Any
import unicodedata

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
from PIL import Image

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
load_dotenv(SCRIPT_DIR / ".env")

ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"]
MODEL = os.environ["AZURE_OPENAI_MODEL"]
WINES_PATH = SCRIPT_DIR.parent / "wines.json"
OUTPUT_DIR = SCRIPT_DIR.parent / "documents"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load wines data
with open(WINES_PATH, encoding="utf-8") as f:
    WINES = json.load(f)
WINES_SUMMARY = json.dumps(
    [{k: v for k, v in w.items() if k != "Description"} for w in WINES],
    ensure_ascii=False,
    indent=1,
)

# Azure OpenAI clients
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
)
text_client = OpenAI(
    base_url=f"{ENDPOINT.rstrip('/')}/openai/v1/",
    api_key=token_provider,
)
image_client = OpenAI(
    base_url=f"{ENDPOINT.rstrip('/')}/openai/v1/",
    api_key=token_provider,
    default_headers={"api_version": "preview"},
)

# Font paths
FONT_REGULAR = "C:/Windows/Fonts/arial.ttf"
FONT_BOLD = "C:/Windows/Fonts/arialbd.ttf"
FONT_ITALIC = "C:/Windows/Fonts/ariali.ttf"
MIN_DOC_COUNT = 1
MAX_DOC_COUNT = 10
DEFAULT_DOC_COUNT = 8
DEFAULT_CHAPTERS_PER_DOC = 8

# ---------------------------------------------------------------------------
# Retry logic
# ---------------------------------------------------------------------------


def call_with_retry(func, *args, max_retries=10, **kwargs):
    """Call func with exponential backoff on rate-limit/transient errors."""
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            err_str = str(e)
            if any(k in err_str.lower() for k in ["429", "rate", "quota", "throttl"]):
                wait = min(2 ** attempt + random.random() * 2, 120)
                print(f"  Rate limited, waiting {wait:.1f}s (attempt {attempt+1}/{max_retries})")
                time.sleep(wait)
            elif any(k in err_str.lower() for k in ["timeout", "connection", "server_error", "500", "502", "503"]):
                wait = min(5 + random.random() * 5, 30)
                print(f"  Transient error, waiting {wait:.1f}s (attempt {attempt+1}/{max_retries})")
                time.sleep(wait)
            else:
                raise
    raise Exception(f"Max retries ({max_retries}) exceeded")


# ---------------------------------------------------------------------------
# AI generation helpers
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "Jsi uznávaný český vinařský expert a autor odborných knih o víně. "
    "Píšeš profesionální, detailní a vzdělávací texty v češtině. "
    "Tvé texty jsou bohaté, podrobné a čtivé. Používáš odbornou vinařskou terminologii. "
    "Máš k dispozici katalog 60 českých vín:\n\n" + WINES_SUMMARY
)


def generate_text(user_prompt: str, system_prompt: str = SYSTEM_PROMPT) -> str:
    """Generate text using the Responses API."""
    def _call():
        resp = text_client.responses.create(
            model=MODEL,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return resp.output_text

    return call_with_retry(_call)


def generate_image(prompt: str) -> bytes:
    """Generate an image using gpt-image-1.5. Returns PNG bytes."""
    def _call():
        framed_prompt = (
            prompt
            + " Ensure ALL content fits fully within the image boundaries with generous padding/margins "
            "on every side. Nothing should be cut off or extend beyond the edges."
        )
        result = image_client.images.generate(
            model="gpt-image-1.5",
            prompt=framed_prompt,
            n=1,
            size="1536x1024",
            quality="medium",
        )
        # Try b64_json first, then fall back to URL
        b64 = getattr(result.data[0], "b64_json", None)
        if b64:
            return base64.b64decode(b64)
        url = getattr(result.data[0], "url", None)
        if url:
            import urllib.request
            with urllib.request.urlopen(url) as resp:
                return resp.read()
        raise Exception("No image data returned")

    return call_with_retry(_call)


# ---------------------------------------------------------------------------
# Structured generation helpers (hierarchical generation)
# ---------------------------------------------------------------------------

JSON_SYSTEM_PROMPT = (
    "Jsi přesný generátor JSON. Vracíš pouze validní JSON bez markdownu, "
    "bez vysvětlení a bez dodatečného textu."
)


class ChapterBlueprint(BaseModel):
    """Chapter descriptor generated for a document blueprint."""

    title: str = Field(min_length=4, max_length=180)


class DocumentBlueprint(BaseModel):
    """Document descriptor generated for top-level hierarchy."""

    title: str = Field(min_length=4, max_length=180)
    subtitle: str = Field(min_length=4, max_length=220)
    cover_prompt: str = Field(min_length=20, max_length=1200)
    chapters: list[ChapterBlueprint] = Field(min_length=3, max_length=12)


class TableSpec(BaseModel):
    """Structured table definition for chapter content."""

    caption: str = Field(min_length=4, max_length=160)
    headers: list[str] = Field(min_length=3, max_length=8)
    rows: list[list[str]] = Field(min_length=4, max_length=12)


class ChapterPackage(BaseModel):
    """Structured chapter package generated at hierarchy level 2."""

    text: str = Field(min_length=300)
    image_prompts: list[str] = Field(min_length=1, max_length=2)
    chart_spec: dict[str, Any]
    table: TableSpec


def _extract_json_payload(raw_text: str) -> dict[str, Any]:
    """Extract and parse a JSON object from an LLM response."""
    raw = raw_text.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start >= 0 and end > start:
            return json.loads(raw[start:end + 1])
        raise


def generate_json(user_prompt: str, system_prompt: str = JSON_SYSTEM_PROMPT) -> dict[str, Any]:
    """Generate and parse strict JSON from the model."""
    raw = generate_text(
        user_prompt=(
            user_prompt
            + "\n\nVrať pouze validní JSON objekt. Žádný markdown, žádný doprovodný text."
        ),
        system_prompt=system_prompt,
    )
    return _extract_json_payload(raw)


def _slugify_filename(value: str, index: int) -> str:
    """Create a filesystem-safe PDF filename."""
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "_", ascii_text.lower()).strip("_")
    if not slug:
        slug = f"wine_document_{index}"
    return f"{slug}.pdf"


def generate_document_blueprints(document_count: int, chapters_per_doc: int) -> list[dict]:
    """Generate top-level document hierarchy using LLM."""
    prompt = (
        f"Vytvoř návrh {document_count} odborných dokumentů/knih o víně v češtině. "
        "Témata drž v podobném stylu jako: česká vína, degustace, párování s jídlem, "
        "technologie výroby, chemie vína, vinařské regiony, odrůdy, historie, trendy. "
        f"Každý dokument musí mít přesně {chapters_per_doc} kapitol. "
        "Vrať JSON ve tvaru: "
        '{"documents":[{"title":"...","subtitle":"...","cover_prompt":"...","chapters":[{"title":"..."}]}]}. '
        "Cover prompt musí být vizuálně bohatý, bez dlouhého textu v obrázku. "
        "Názvy kapitol musí být odborné a konkrétní."
    )

    payload = generate_json(prompt)
    docs_raw = payload.get("documents")
    if not isinstance(docs_raw, list) or not docs_raw:
        raise ValueError("Invalid document blueprint payload")

    docs: list[dict] = []
    for idx, raw_doc in enumerate(docs_raw[:document_count], 1):
        blueprint = DocumentBlueprint.model_validate(raw_doc)
        chapters = [{"title": ch.title.strip()} for ch in blueprint.chapters[:chapters_per_doc]]
        if len(chapters) < chapters_per_doc:
            for j in range(len(chapters) + 1, chapters_per_doc + 1):
                chapters.append({"title": f"Kapitola {j}: {blueprint.title}"})
        docs.append(
            {
                "filename": _slugify_filename(blueprint.title, idx),
                "title": blueprint.title.strip(),
                "subtitle": blueprint.subtitle.strip(),
                "cover_prompt": blueprint.cover_prompt.strip(),
                "chapters": chapters,
            }
        )

    if len(docs) < document_count:
        raise ValueError("Not enough generated blueprints")
    return docs

# ---------------------------------------------------------------------------
# Chart generation helpers
# ---------------------------------------------------------------------------

plt.rcParams["font.family"] = "Arial"
sns.set_theme(style="whitegrid", font="Arial")


def _chart_to_bytes(fig) -> bytes:
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def chart_pie(labels: list[str], values: list[float], title: str) -> bytes:
    fig, ax = plt.subplots(figsize=(7, 5))
    colors = sns.color_palette("Set2", len(labels))
    ax.pie(values, labels=labels, autopct="%1.1f%%", colors=colors, startangle=140)
    ax.set_title(title, fontsize=13, fontweight="bold")
    return _chart_to_bytes(fig)


def chart_bar(labels: list[str], values: list[float], title: str, xlabel: str = "", ylabel: str = "") -> bytes:
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = sns.color_palette("muted", len(labels))
    ax.bar(labels, values, color=colors)
    ax.set_title(title, fontsize=13, fontweight="bold")
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    plt.xticks(rotation=30, ha="right", fontsize=9)
    plt.tight_layout()
    return _chart_to_bytes(fig)


def chart_line(x: list, y: list, title: str, xlabel: str = "", ylabel: str = "") -> bytes:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x, y, marker="o", linewidth=2, color=sns.color_palette("deep")[0])
    ax.set_title(title, fontsize=13, fontweight="bold")
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return _chart_to_bytes(fig)


def chart_heatmap(data: list[list[float]], xlabels: list[str], ylabels: list[str], title: str) -> bytes:
    import numpy as np
    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(np.array(data), annot=True, fmt=".0f", xticklabels=xlabels,
                yticklabels=ylabels, cmap="YlOrRd", ax=ax, linewidths=0.5)
    ax.set_title(title, fontsize=13, fontweight="bold")
    plt.tight_layout()
    return _chart_to_bytes(fig)


# ---------------------------------------------------------------------------
# Dynamic chapter asset generation
# ---------------------------------------------------------------------------

def _as_str_list(values: Any, field_name: str) -> list[str]:
    source = values
    if isinstance(source, dict):
        source = _first_present(source, ["labels", "values", "data"]) or list(source.keys())
    if isinstance(source, str):
        source = [part.strip() for part in source.split(",")]
    if isinstance(source, tuple | set):
        source = list(source)
    if not isinstance(source, list):
        source = [source]
    cleaned = [str(v).strip() for v in source if str(v).strip()]
    if not cleaned:
        raise ValueError(f"{field_name} must contain at least one value")
    return cleaned


def _as_float_list(values: Any, field_name: str) -> list[float]:
    source = values
    if isinstance(source, dict):
        source = _first_present(source, ["values", "data", "y_values", "y"]) or list(source.values())
    if isinstance(source, str):
        source = [part.strip() for part in source.split(",")]
    if isinstance(source, tuple | set):
        source = list(source)
    if not isinstance(source, list):
        source = [source]

    parsed: list[float] = []
    for item in source:
        if isinstance(item, dict):
            item = _first_present(item, ["value", "y", "count", "x"])
        try:
            parsed.append(float(item))
        except (TypeError, ValueError):
            continue
    if not parsed:
        raise ValueError(f"{field_name} must contain numeric values")
    return parsed


def _first_present(source: dict[str, Any], keys: list[str]) -> Any:
    for key in keys:
        if key in source and source[key] is not None:
            return source[key]
    return None


def _normalize_chart_spec(chart_spec: dict[str, Any]) -> dict[str, Any]:
    """Normalize variant LLM chart keys to the expected schema."""
    spec = dict(chart_spec or {})
    chart_type = str(_first_present(spec, ["chart_type", "type", "chart"]) or "").strip().lower()
    normalized: dict[str, Any] = {
        "chart_type": chart_type,
        "title": str(_first_present(spec, ["title", "chart_title", "name"]) or "").strip(),
        "x_label": str(_first_present(spec, ["x_label", "xlabel", "x_axis_label"]) or "").strip(),
        "y_label": str(_first_present(spec, ["y_label", "ylabel", "y_axis_label"]) or "").strip(),
    }

    if chart_type == "bar":
        normalized["labels"] = _first_present(spec, ["labels", "categories", "x_labels", "x_values"])
        normalized["values"] = _first_present(spec, ["values", "y_values", "data", "counts"])
    elif chart_type in {"line", "scatter"}:
        normalized["x_values"] = _first_present(spec, ["x_values", "x", "labels", "x_labels", "categories"])
        normalized["y_values"] = _first_present(spec, ["y_values", "y", "values", "data"])
    elif chart_type == "hist":
        normalized["values"] = _first_present(spec, ["values", "data", "samples", "y_values"])
    elif chart_type == "heatmap":
        normalized["x_labels"] = _first_present(spec, ["x_labels", "columns", "x_values", "labels_x"])
        normalized["y_labels"] = _first_present(spec, ["y_labels", "rows", "y_values", "labels_y"])
        normalized["matrix"] = _first_present(spec, ["matrix", "data", "values", "grid"])
    return normalized


def generate_chart_from_spec(chart_spec: dict[str, Any]) -> bytes:
    """Generate a seaborn chart from LLM-provided spec."""
    spec = _normalize_chart_spec(chart_spec)
    chart_type = str(spec.get("chart_type", "")).strip().lower()
    title = str(spec.get("title", "")).strip() or "Datový přehled kapitoly"
    xlabel = str(spec.get("x_label", "")).strip()
    ylabel = str(spec.get("y_label", "")).strip()

    if chart_type == "bar":
        labels = _as_str_list(spec.get("labels"), "labels")
        values = _as_float_list(spec.get("values"), "values")
        n = min(len(labels), len(values))
        if n < 2:
            raise ValueError("bar chart needs at least 2 values")
        return chart_bar(labels[:n], values[:n], title, xlabel, ylabel)

    if chart_type == "line":
        x_axis = _as_str_list(spec.get("x_values"), "x_values")
        y_axis = _as_float_list(spec.get("y_values"), "y_values")
        n = min(len(x_axis), len(y_axis))
        if n < 2:
            raise ValueError("line chart needs at least 2 values")
        return chart_line(x_axis[:n], y_axis[:n], title, xlabel, ylabel)

    if chart_type == "scatter":
        x_vals = _as_float_list(spec.get("x_values"), "x_values")
        y_vals = _as_float_list(spec.get("y_values"), "y_values")
        n = min(len(x_vals), len(y_vals))
        if n < 3:
            raise ValueError("scatter chart needs at least 3 points")
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.scatterplot(x=x_vals[:n], y=y_vals[:n], ax=ax, s=80, color=sns.color_palette("deep")[0])
        ax.set_title(title, fontsize=13, fontweight="bold")
        if xlabel:
            ax.set_xlabel(xlabel)
        if ylabel:
            ax.set_ylabel(ylabel)
        plt.tight_layout()
        return _chart_to_bytes(fig)

    if chart_type == "hist":
        values = _as_float_list(spec.get("values"), "values")
        if len(values) < 6:
            raise ValueError("hist chart needs at least 6 values")
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.histplot(values, bins=min(10, max(5, len(values) // 2)), kde=True, ax=ax, color=sns.color_palette("muted")[2])
        ax.set_title(title, fontsize=13, fontweight="bold")
        if xlabel:
            ax.set_xlabel(xlabel)
        if ylabel:
            ax.set_ylabel(ylabel)
        plt.tight_layout()
        return _chart_to_bytes(fig)

    if chart_type == "heatmap":
        xlabels = _as_str_list(spec.get("x_labels"), "x_labels")
        ylabels = _as_str_list(spec.get("y_labels"), "y_labels")
        matrix = spec.get("matrix")
        if not (isinstance(matrix, list) and matrix and isinstance(matrix[0], list)):
            raise ValueError("heatmap matrix must be a 2D list")
        cleaned_matrix = []
        for row in matrix[: len(ylabels)]:
            cleaned_row = _as_float_list(row, "matrix_row")
            if len(cleaned_row) < len(xlabels):
                raise ValueError("heatmap row shorter than x_labels")
            cleaned_matrix.append(cleaned_row[: len(xlabels)])
        if len(cleaned_matrix) < len(ylabels):
            raise ValueError("heatmap rows shorter than y_labels")
        return chart_heatmap(cleaned_matrix, xlabels, ylabels, title)

    raise ValueError(f"Unsupported chart_type: {chart_type}")


def _normalize_table_for_pdf(table: TableSpec) -> list[list[str]]:
    """Convert table model into rectangular PDF table rows."""
    headers = [str(h).strip()[:40] for h in table.headers]
    rows: list[list[str]] = []
    width = len(headers)
    for row in table.rows:
        normalized = [str(cell).strip()[:40] for cell in row[:width]]
        if len(normalized) < width:
            normalized.extend([""] * (width - len(normalized)))
        rows.append(normalized)
    return [headers] + rows


def _table_text_block(table_data: list[list[str]], caption: str) -> str:
    """Create short plain-text table summary for chapter text."""
    if len(table_data) < 2:
        return ""
    lines = [f"{caption}"]
    lines.append(" | ".join(table_data[0]))
    for row in table_data[1:6]:
        lines.append(" | ".join(row))
    return "\n".join(lines)


def generate_chapter_package(doc_title: str, chapter_title: str) -> dict[str, Any]:
    """Generate chapter text + image prompts + chart spec + table data."""
    prompt = (
        f"Vygeneruj obsah kapitoly '{chapter_title}' pro dokument '{doc_title}'. "
        "Vrať JSON objekt s klíči: text, image_prompts, chart_spec, table. "
        "Požadavky:\n"
        "- text: 900-1300 slov v češtině, odborný styl, bez markdownu.\n"
        "- image_prompts: 1 až 2 prompty pro informačně bohaté vizuály "
        "(procesní diagramy, části systému, kroky postupu); v obrázku jen krátké popisky 1-3 slova. "
        "Obrázek musí mít dostatek okrajů (padding) aby žádný obsah nebyl oříznutý na krajích.\n"
        "- chart_spec: objekt s klíči chart_type (bar|line|scatter|hist|heatmap), title, x_label, y_label "
        "a daty odpovídajícími typu (labels/values nebo x_values/y_values nebo x_labels/y_labels/matrix).\n"
        "  V chart_spec vrať konkrétní datové hodnoty, žádné placeholdery typu A/B/C.\n"
        "- table: objekt s klíči caption, headers, rows (alespoň 4 řádky).\n"
        "Text drž tematicky u českého a evropského vinařství, degustace, technologie výroby, chemie vína a praxe."
    )
    payload = generate_json(prompt)
    package = ChapterPackage.model_validate(payload)
    table_data = _normalize_table_for_pdf(package.table)
    text_with_table = package.text.strip()
    text_with_table += "\n\nTabulkové shrnutí:\n" + _table_text_block(table_data, package.table.caption)
    prompts = [p.strip() for p in package.image_prompts if p.strip()][:2]
    if not prompts:
        prompts = [
            (
                f"Educational process diagram for '{chapter_title}' in Czech wine context, "
                "component labels with 1-3 words, clean infographic style, no long text"
            )
        ]
    return {
        "text": text_with_table,
        "image_prompts": prompts,
        "chart_spec": package.chart_spec,
        "table_data": table_data,
        "table_caption": package.table.caption.strip(),
    }


# ---------------------------------------------------------------------------
# Chapter recovery helpers
# ---------------------------------------------------------------------------

def generate_chart_spec_only(doc_title: str, chapter_title: str) -> dict[str, Any]:
    """Request chart content from LLM when primary chart spec is invalid."""
    prompt = (
        f"Vrať pouze JSON chart_spec pro kapitolu '{chapter_title}' v dokumentu '{doc_title}'. "
        "chart_spec musí obsahovat klíče chart_type, title, x_label, y_label "
        "a data odpovídající typu. Povolené chart_type: bar, line, scatter, hist, heatmap. "
        "Použij konkrétní realistická čísla, ne placeholdery. "
        "Pro bar: labels + values (min 4). "
        "Pro line/scatter: x_values + y_values (min 6). "
        "Pro hist: values (min 12). "
        "Pro heatmap: x_labels + y_labels + matrix. "
        "Použij přesně názvy klíčů uvedené výše."
    )
    payload = generate_json(prompt)
    chart_spec = payload.get("chart_spec")
    if isinstance(chart_spec, dict):
        return chart_spec
    if isinstance(payload, dict):
        return payload
    raise ValueError("LLM chart_spec response is invalid")


def generate_chapter_recovery_package(doc_title: str, chapter_title: str) -> dict[str, Any]:
    """Generate a smaller structured package if the full chapter package fails."""
    prompt = (
        f"Pro kapitolu '{chapter_title}' v dokumentu '{doc_title}' vrať JSON objekt "
        "s klíči: text, image_prompts, chart_spec, table. "
        "- text: 450-700 slov.\n"
        "- image_prompts: 1 až 2 prompty (informační diagram, krátké popisky).\n"
        "- chart_spec: konkrétní datové hodnoty.\n"
        "- table: caption, headers, rows (alespoň 4 řádky).\n"
        "Bez markdownu, pouze JSON."
    )
    payload = generate_json(prompt)
    package = ChapterPackage.model_validate(payload)
    table_data = _normalize_table_for_pdf(package.table)
    text_with_table = package.text.strip() + "\n\nTabulkové shrnutí:\n" + _table_text_block(table_data, package.table.caption)
    prompts = [p.strip() for p in package.image_prompts if p.strip()][:2]
    if not prompts:
        prompts = [
            (
                f"Educational process diagram for '{chapter_title}' in Czech wine context, "
                "component labels with 1-3 words, clean infographic style, no long text"
            )
        ]
    return {
        "text": text_with_table,
        "image_prompts": prompts,
        "chart_spec": package.chart_spec,
        "table_data": table_data,
        "table_caption": package.table.caption.strip(),
    }


# ---------------------------------------------------------------------------
# Parallel chapter worker
# ---------------------------------------------------------------------------

def build_chapter_data(filename: str, doc_title: str, chapter_title: str, chapter_index: int, total_chapters: int) -> tuple[int, dict]:
    """Generate all assets for one chapter and return ordered result tuple."""
    print(f"  [{filename}] Chapter {chapter_index}/{total_chapters}: {chapter_title}")
    print("    Generating chapter package (text + image prompts + chart + table)...")
    try:
        package = generate_chapter_package(doc_title, chapter_title)
        text = package["text"]
        word_count = len(text.split())
        print(f"    Chapter package generated ({word_count} words)")
    except Exception as e:
        print(f"    Chapter package generation failed: {e}")
        package = generate_chapter_recovery_package(doc_title, chapter_title)
        text = package["text"]
        print("    Recovery chapter package generated")

    ch_images: list[bytes] = []
    for prompt_idx, image_prompt in enumerate(package["image_prompts"], 1):
        print(f"    Generating chapter image {prompt_idx}/{len(package['image_prompts'])}...")
        try:
            full_prompt = (
                f"{image_prompt}. "
                "Make the visual educational and information-rich with components/steps. "
                "Use only very short labels, no long sentences."
            )
            ch_image = generate_image(full_prompt)
            ch_images.append(ch_image)
            print(f"    Image generated ({len(ch_image)} bytes)")
        except Exception as e:
            print(f"    Image generation failed: {e}")

    ch_chart = None
    print("    Generating seaborn chart...")
    try:
        ch_chart = generate_chart_from_spec(package["chart_spec"])
        print(f"    Chart generated ({len(ch_chart)} bytes)")
    except Exception as e:
        print(f"    Chart generation failed: {e}")
        try:
            retry_chart_spec = generate_chart_spec_only(doc_title, chapter_title)
            ch_chart = generate_chart_from_spec(retry_chart_spec)
            print(f"    Chart generated on retry ({len(ch_chart)} bytes)")
        except Exception as retry_error:
            print(f"    Chart retry failed: {retry_error}")

    return chapter_index, {
        "title": chapter_title,
        "text": text,
        "images": ch_images,
        "chart": ch_chart,
        "table": package["table_data"],
        "table_caption": package["table_caption"],
    }


# ---------------------------------------------------------------------------
# PDF Builder
# ---------------------------------------------------------------------------

class WinePDF(FPDF):
    """Custom PDF with header/footer support."""

    def __init__(self, doc_title: str):
        super().__init__()
        self.doc_title = doc_title
        self.add_font("Arial", "", FONT_REGULAR)
        self.add_font("Arial", "B", FONT_BOLD)
        self.add_font("Arial", "I", FONT_ITALIC)
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Arial", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, self.doc_title, align="C", new_x="LMARGIN", new_y="NEXT")
        self.line(10, 14, 200, 14)
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Strana {self.page_no()}", align="C")

    def add_title_page(self, title: str, subtitle: str, image_bytes: bytes | None):
        self.add_page()
        self.set_y(18)
        self.set_font("Arial", "B", 28)
        self.set_text_color(80, 20, 20)
        self.multi_cell(0, 14, title, align="C")
        self.ln(6)
        self.set_font("Arial", "I", 14)
        self.set_text_color(100, 100, 100)
        self.multi_cell(0, 8, subtitle, align="C")
        self.set_text_color(0, 0, 0)
        if image_bytes:
            self.ln(8)
            image_y = max(self.get_y(), 80)
            self._insert_image(image_bytes, x=25, y=image_y, w=160)

    def add_chapter(self, number: int, title: str, text: str,
                    image_bytes: bytes | None = None, image_caption: str = "",
                    chart_bytes: bytes | None = None, chart_caption: str = "",
                    table_data: list[list[str]] | None = None, table_caption: str = ""):
        """Add a full chapter to the PDF."""
        self.add_page()
        # Chapter heading
        self.set_font("Arial", "B", 18)
        self.set_text_color(80, 20, 20)
        self.cell(0, 12, f"{number}. {title}", new_x="LMARGIN", new_y="NEXT")
        self.ln(4)
        self.set_text_color(0, 0, 0)

        # Chapter image (if any) - placed at beginning
        if image_bytes:
            self._insert_image(image_bytes, x=25, w=160)
            if image_caption:
                self.set_font("Arial", "I", 9)
                self.set_text_color(80, 80, 80)
                self.multi_cell(0, 5, image_caption, align="C")
                self.set_text_color(0, 0, 0)
            self.ln(4)

        # Chapter text - split into paragraphs
        self.set_font("Arial", "", 11)
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        for para in paragraphs:
            # Check if this is a subheading (short, no period at end)
            if len(para) < 80 and not para.endswith(".") and not para.endswith(":") and para[0].isupper():
                if len(para) < 50:
                    self.ln(3)
                    self.set_font("Arial", "B", 13)
                    self.multi_cell(0, 7, para)
                    self.set_font("Arial", "", 11)
                    self.ln(2)
                    continue
            self.multi_cell(0, 6, para)
            self.ln(2)

        # Chart (if any)
        if chart_bytes:
            self.ln(4)
            self._insert_image(chart_bytes, x=15, w=180)
            if chart_caption:
                self.set_font("Arial", "I", 9)
                self.set_text_color(80, 80, 80)
                self.multi_cell(0, 5, chart_caption, align="C")
                self.set_text_color(0, 0, 0)
            self.ln(4)

        # Table (if any)
        if table_data and len(table_data) > 1:
            self.ln(4)
            if table_caption:
                self.set_font("Arial", "B", 10)
                self.multi_cell(0, 6, table_caption)
                self.ln(2)
            self._add_table(table_data)
            self.ln(4)

    def _insert_image(self, img_bytes: bytes, x: float = 10, y: float | None = None,
                      w: float = 170):
        """Insert image bytes into the PDF."""
        # Convert to PNG via Pillow to ensure compatibility
        try:
            img = Image.open(BytesIO(img_bytes))
            buf = BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            png_bytes = buf.read()
        except Exception:
            png_bytes = img_bytes

        tmp_path = os.path.join(tempfile.gettempdir(), f"wine_pdf_{id(self)}_{random.randint(0,999999)}.png")
        with open(tmp_path, "wb") as f:
            f.write(png_bytes)
        try:
            # Get dimensions without keeping file handle open
            with Image.open(tmp_path) as img_pil:
                aspect = img_pil.height / img_pil.width
            h = w * aspect
            if self.get_y() + h > 270:
                self.add_page()
            if y is not None:
                self.image(tmp_path, x=x, y=y, w=w)
                self.set_y(y + h + 5)
            else:
                self.image(tmp_path, x=x, w=w)
                self.ln(3)
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass  # Windows file locking - will be cleaned up later

    def _add_table(self, data: list[list[str]]):
        """Add a simple table. First row is header."""
        if not data:
            return
        num_cols = len(data[0])
        page_width = 190
        col_w = page_width / num_cols

        # Header
        self.set_font("Arial", "B", 9)
        self.set_fill_color(80, 20, 20)
        self.set_text_color(255, 255, 255)
        for cell_text in data[0]:
            self.cell(col_w, 7, str(cell_text)[:40], border=1, fill=True, align="C")
        self.ln()

        # Rows
        self.set_font("Arial", "", 9)
        self.set_text_color(0, 0, 0)
        for i, row in enumerate(data[1:]):
            if i % 2 == 0:
                self.set_fill_color(245, 240, 235)
            else:
                self.set_fill_color(255, 255, 255)
            for cell_text in row:
                self.cell(col_w, 6, str(cell_text)[:40], border=1, fill=True)
            self.ln()


# ---------------------------------------------------------------------------
# Generate a single document
# ---------------------------------------------------------------------------

def generate_document(doc_def: dict) -> str:
    """Generate a single PDF document. Returns the output file path."""
    filename = doc_def["filename"]
    title = doc_def["title"]
    subtitle = doc_def["subtitle"]
    print(f"\n{'='*60}")
    print(f"Starting: {filename} – {title}")
    print(f"{'='*60}")

    # 1. Generate cover image
    print(f"  [{filename}] Generating cover image...")
    try:
        cover_image = generate_image(doc_def["cover_prompt"])
        print(f"  [{filename}] Cover image generated ({len(cover_image)} bytes)")
    except Exception as e:
        print(f"  [{filename}] Cover image failed: {e}")
        cover_image = None

    # 2. Generate chapter content/assets in parallel and keep chapter order
    chapters = doc_def["chapters"]
    chapter_count = len(chapters)
    chapter_workers = min(6, max(1, chapter_count))
    chapter_data_by_index: dict[int, dict] = {}
    with ThreadPoolExecutor(max_workers=chapter_workers) as chapter_executor:
        chapter_futures = {
            chapter_executor.submit(
                build_chapter_data,
                filename,
                title,
                ch["title"],
                idx,
                chapter_count,
            ): idx
            for idx, ch in enumerate(chapters, 1)
        }
        for future in as_completed(chapter_futures):
            idx = chapter_futures[future]
            chapter_index, chapter_result = future.result()
            chapter_data_by_index[chapter_index] = chapter_result
            if idx != chapter_index:
                print(f"  [{filename}] Warning: chapter index mismatch ({idx} vs {chapter_index})")

    chapter_data = [chapter_data_by_index[i] for i in range(1, chapter_count + 1)]

    # 3. Assemble PDF
    print(f"  [{filename}] Assembling PDF...")
    pdf = WinePDF(title)

    # Title page
    pdf.add_title_page(title, subtitle, cover_image)

    # Add chapters
    for i, ch in enumerate(chapter_data, 1):
        pdf.add_page()

        # Chapter heading
        pdf.set_font("Arial", "B", 18)
        pdf.set_text_color(80, 20, 20)
        pdf.cell(0, 12, f"{i}. {ch['title']}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)
        pdf.set_text_color(0, 0, 0)

        # Chapter image(s)
        for img_idx, img in enumerate(ch["images"], 1):
            try:
                pdf._insert_image(img, x=20, w=170)
                pdf.set_font("Arial", "I", 9)
                pdf.set_text_color(80, 80, 80)
                pdf.multi_cell(0, 5, f"Schéma {img_idx} ke kapitole: {ch['title']}", align="C")
                pdf.set_text_color(0, 0, 0)
                pdf.ln(4)
            except Exception as e:
                print(f"    Warning: Could not insert chapter image {img_idx}: {e}")

        # Chapter text
        pdf.set_font("Arial", "", 11)
        paragraphs = [p.strip() for p in ch["text"].split("\n") if p.strip()]
        for para in paragraphs:
            # Detect subheadings
            if len(para) < 80 and not para.endswith(".") and not para.endswith(",") and len(para) > 3:
                # Check if it looks like a heading (short, capitalized)
                if len(para) < 55 and para[0].isupper() and not any(c in para for c in [".", ",", ";"]):
                    pdf.ln(3)
                    pdf.set_font("Arial", "B", 13)
                    pdf.multi_cell(0, 7, para)
                    pdf.set_font("Arial", "", 11)
                    pdf.ln(2)
                    continue
            pdf.multi_cell(0, 6, para)
            pdf.ln(2)

        # Chart
        if ch["chart"]:
            try:
                pdf.ln(4)
                pdf._insert_image(ch["chart"], x=15, w=180)
                pdf.ln(4)
            except Exception as e:
                print(f"    Warning: Could not insert chart: {e}")

        # Table
        if ch["table"] and len(ch["table"]) > 1:
            try:
                pdf.ln(4)
                if ch["table_caption"]:
                    pdf.set_font("Arial", "B", 10)
                    pdf.multi_cell(0, 6, ch["table_caption"])
                    pdf.ln(2)
                pdf._add_table(ch["table"])
                pdf.ln(4)
            except Exception as e:
                print(f"    Warning: Could not insert table: {e}")

    # Save
    output_path = OUTPUT_DIR / filename
    pdf.output(str(output_path))
    file_size = output_path.stat().st_size
    print(f"  [{filename}] DONE! Saved to {output_path} ({file_size/1024:.0f} KB, {pdf.pages_count} pages)")
    return str(output_path)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Generate AI-authored wine PDF documents.")
    parser.add_argument(
        "--documents",
        type=int,
        default=DEFAULT_DOC_COUNT,
        help=f"Number of documents to generate ({MIN_DOC_COUNT}-{MAX_DOC_COUNT}).",
    )
    parser.add_argument(
        "--chapters-per-document",
        type=int,
        default=DEFAULT_CHAPTERS_PER_DOC,
        help="Number of chapters per generated document.",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=10,
        help="Parallel workers for document generation.",
    )
    args = parser.parse_args()
    if not MIN_DOC_COUNT <= args.documents <= MAX_DOC_COUNT:
        parser.error(f"--documents must be between {MIN_DOC_COUNT} and {MAX_DOC_COUNT}.")
    if args.chapters_per_document < 3:
        parser.error("--chapters-per-document must be at least 3.")
    if args.max_workers < 1:
        parser.error("--max-workers must be >= 1.")
    return args


def prepare_documents(document_count: int, chapters_per_doc: int) -> list[dict]:
    """Generate top-level document hierarchy and ensure unique filenames."""
    docs = generate_document_blueprints(document_count, chapters_per_doc)
    print(f"Generated {len(docs)} document blueprints via LLM.")

    name_counts: dict[str, int] = {}
    for doc in docs:
        filename = doc["filename"]
        stem = Path(filename).stem
        suffix = Path(filename).suffix or ".pdf"
        count = name_counts.get(filename, 0)
        if count:
            doc["filename"] = f"{stem}_{count + 1}{suffix}"
        name_counts[filename] = count + 1
    return docs


def main():
    args = parse_args()
    documents = prepare_documents(args.documents, args.chapters_per_document)

    print("=" * 60)
    print("Wine PDF Document Generator")
    print(f"Generating {len(documents)} documents")
    print(f"Chapters per document: {args.chapters_per_document}")
    print(f"Workers: {args.max_workers}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Wines loaded: {len(WINES)}")
    print("=" * 60)

    results = {}
    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        futures = {
            executor.submit(generate_document, doc): doc["filename"]
            for doc in documents
        }
        for future in as_completed(futures):
            filename = futures[future]
            try:
                path = future.result()
                results[filename] = ("OK", path)
                print(f"\n✓ {filename} completed successfully")
            except Exception as e:
                results[filename] = ("FAILED", str(e))
                print(f"\n✗ {filename} FAILED: {e}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for filename, (status, detail) in sorted(results.items()):
        icon = "✓" if status == "OK" else "✗"
        print(f"  {icon} {filename}: {status}")
        if status == "OK":
            try:
                size = Path(detail).stat().st_size
                print(f"    Size: {size/1024:.0f} KB")
            except Exception:
                pass

    ok_count = sum(1 for s, _ in results.values() if s == "OK")
    print(f"\n{ok_count}/{len(documents)} documents generated successfully.")


if __name__ == "__main__":
    main()
