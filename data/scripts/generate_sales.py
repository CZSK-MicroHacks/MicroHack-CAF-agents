"""Generate 1000 sales records using Azure OpenAI Responses API with structured outputs."""

import json
import os
from pathlib import Path

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
BASE_URL = f"{ENDPOINT.rstrip('/')}/openai/v1/"

OUTPUT_PATH = SCRIPT_DIR.parent / "sales.json"
WINES_PATH = SCRIPT_DIR.parent / "wines.json"

BATCH_SIZE = 30
TARGET_COUNT = 1000

# ---------------------------------------------------------------------------
# Pydantic models for structured output
# ---------------------------------------------------------------------------


class Sale(BaseModel):
    """Single sale record."""

    SalesId: int = Field(description="Unique sequential integer ID")
    Date: str = Field(description="Sale date in DD.MM.YYYY format, between 01.01.2025 and 28.02.2026")
    Store: str = Field(description="Czech city name where the sale occurred")
    WineId: int = Field(description="Reference to a valid WineId from the wine catalogue (1-60)")
    Quantity: int = Field(description="Number of bottles sold, 1-50")
    Discount: int = Field(description="Discount percentage, 0-15")
    PaymentMethod: str = Field(description="Payment method: Card / Cash / Online")


class SalesBatch(BaseModel):
    """A batch of sale records returned by the model."""

    sales: list[Sale]


# ---------------------------------------------------------------------------
# Load wines catalogue
# ---------------------------------------------------------------------------


def load_wines_catalogue() -> list[dict]:
    """Load wine catalogue and return compact summaries for the system prompt."""
    with open(WINES_PATH, encoding="utf-8") as f:
        wines = json.load(f)
    return [
        {"WineId": w["WineId"], "WineCode": w["WineCode"], "WineName": w["WineName"], "UnitPrice": w["UnitPrice"]}
        for w in wines
    ]


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are a data generator for a Czech wine retail company. Your task is to generate realistic sales records.

WINE CATALOGUE (use ONLY these WineIds):
{wines_json}

RULES:
- Each sale must reference a valid WineId from the catalogue above (1-60).
- Store must be a Czech city: Praha, Brno, Ostrava, Plzeň, Olomouc, Liberec, České Budějovice, \
Hradec Králové, Znojmo, Mikulov, Karlovy Vary, Zlín, Jihlava, Pardubice, Opava.
- Date format: DD.MM.YYYY, dates must fall between 01.01.2025 and 28.02.2026.
- Quantity: 1-50 (most sales are 1-10, larger quantities are rarer).
- Discount: 0-15 (most sales have 0-5% discount, higher discounts are rarer).
- PaymentMethod: Card / Cash / Online (Card is most common, then Cash, then Online).
- Generate diverse, realistic data: vary stores, dates, wines, quantities, discounts, and payment methods.
- Seasonal patterns: more sales around holidays (Christmas, Easter, summer), fewer in quiet months.
- Popular wines (lower prices) should appear more often than expensive ones.
- Each sale must be unique — no exact duplicate combinations of Date + Store + WineId + Quantity.

Generate exactly {batch_size} sales. SalesId starts from {start_id}."""

USER_PROMPT_WITH_CONTEXT = """\
Here is a compact summary of existing sales (avoid exact duplicate Date+Store+WineId+Quantity combinations):

Existing sales count: {existing_count}
Date range covered: {date_range}
Store distribution: {store_dist}
Recent SalesIds: {recent_ids}

Generate {batch_size} new unique sales with SalesId starting from {start_id}."""

USER_PROMPT_INITIAL = """\
Generate {batch_size} unique sales with SalesId starting from {start_id}."""

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def load_existing_sales() -> list[dict]:
    """Load previously generated sales from the output file."""
    if OUTPUT_PATH.exists():
        with open(OUTPUT_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []


def save_sales(sales: list[dict]) -> None:
    """Write sales list to JSON."""
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(sales, f, ensure_ascii=False, indent=2)


def build_summary(sales: list[dict]) -> dict:
    """Build a compact summary of existing sales for context."""
    if not sales:
        return {}
    dates = [s["Date"] for s in sales]
    stores = {}
    for s in sales:
        stores[s["Store"]] = stores.get(s["Store"], 0) + 1
    top_stores = sorted(stores.items(), key=lambda x: -x[1])[:10]
    recent_ids = [s["SalesId"] for s in sales[-10:]]
    return {
        "existing_count": len(sales),
        "date_range": f"{min(dates)} - {max(dates)}",
        "store_dist": ", ".join(f"{name}: {count}" for name, count in top_stores),
        "recent_ids": str(recent_ids),
    }


def main() -> None:
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    )

    client = OpenAI(
        base_url=BASE_URL,
        api_key=token_provider,
    )

    wines_catalogue = load_wines_catalogue()
    wines_json = json.dumps(wines_catalogue, ensure_ascii=False, indent=2)
    print(f"Loaded {len(wines_catalogue)} wines from catalogue")

    sales = load_existing_sales()
    print(f"Loaded {len(sales)} existing sales from {OUTPUT_PATH}")

    batch_num = 0
    while len(sales) < TARGET_COUNT:
        batch_num += 1
        start_id = len(sales) + 1

        system = SYSTEM_PROMPT.format(
            wines_json=wines_json,
            batch_size=BATCH_SIZE,
            start_id=start_id,
        )

        if sales:
            summary = build_summary(sales)
            user = USER_PROMPT_WITH_CONTEXT.format(
                batch_size=BATCH_SIZE,
                start_id=start_id,
                **summary,
            )
        else:
            user = USER_PROMPT_INITIAL.format(batch_size=BATCH_SIZE, start_id=start_id)

        print(f"\n--- Batch {batch_num}: generating sales {start_id}-{start_id + BATCH_SIZE - 1} ---")

        response = client.responses.parse(
            model=MODEL,
            input=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            text_format=SalesBatch,
        )

        batch = response.output_parsed
        if batch is None:
            print("ERROR: Model returned no parsed output. Retrying...")
            continue

        new_sales = [s.model_dump() for s in batch.sales]

        # Re-assign SalesId sequentially to guarantee correctness
        for i, s in enumerate(new_sales):
            s["SalesId"] = start_id + i

        sales.extend(new_sales)
        save_sales(sales)
        print(f"Batch {batch_num} done: +{len(new_sales)} sales, total: {len(sales)}")

    print(f"\nGeneration complete! {len(sales)} sales saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
