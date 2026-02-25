"""Generate ~8000 sales records (500/month × 16 months) using Azure OpenAI Responses API with structured outputs."""

import calendar
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
TARGET_PER_MONTH = 500

# 16 months: Jan 2025 – Apr 2026
MONTHS = [(2025, m) for m in range(1, 13)] + [(2026, m) for m in range(1, 5)]

# ---------------------------------------------------------------------------
# Pydantic models for structured output
# ---------------------------------------------------------------------------


class Sale(BaseModel):
    """Single sale record."""

    SalesId: int = Field(description="Unique sequential integer ID")
    Date: str = Field(description="Sale date in DD.MM.YYYY format")
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
- Date format: DD.MM.YYYY — all dates MUST fall between {date_start} and {date_end}.
- Quantity: 1-50 (most sales are 1-10, larger quantities are rarer).
- Discount: 0-15 (most sales have 0-5% discount, higher discounts are rarer).
- PaymentMethod: Card / Cash / Online (Card is most common, then Cash, then Online).
- Generate diverse, realistic data: vary stores, dates, wines, quantities, discounts, and payment methods.
- Popular wines (lower prices) should appear more often than expensive ones.
- Each sale must be unique — no exact duplicate combinations of Date + Store + WineId + Quantity.

Generate exactly {batch_size} sales for {month_name} {year}. SalesId starts from {start_id}."""

USER_PROMPT = """\
Generate {batch_size} unique sales for {month_name} {year} with SalesId starting from {start_id}. \
All dates must be between {date_start} and {date_end}."""

# ---------------------------------------------------------------------------
# Helpers
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


def count_sales_for_month(sales: list[dict], year: int, month: int) -> int:
    """Count how many existing sales fall in the given month."""
    suffix = f".{month:02d}.{year}"
    return sum(1 for s in sales if s["Date"].endswith(suffix))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


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

    total_batches = 0

    for year, month in MONTHS:
        month_name = calendar.month_name[month]
        days_in_month = calendar.monthrange(year, month)[1]
        date_start = f"01.{month:02d}.{year}"
        date_end = f"{days_in_month:02d}.{month:02d}.{year}"

        existing_for_month = count_sales_for_month(sales, year, month)
        needed = TARGET_PER_MONTH - existing_for_month

        if needed <= 0:
            print(f"\n=== {month_name} {year}: already has {existing_for_month} sales, skipping ===")
            continue

        print(f"\n=== {month_name} {year}: {existing_for_month} existing, generating {needed} more ===")

        generated_for_month = 0
        while generated_for_month < needed:
            batch_size = min(BATCH_SIZE, needed - generated_for_month)
            total_batches += 1
            start_id = len(sales) + 1

            system = SYSTEM_PROMPT.format(
                wines_json=wines_json,
                batch_size=batch_size,
                start_id=start_id,
                month_name=month_name,
                year=year,
                date_start=date_start,
                date_end=date_end,
            )

            user = USER_PROMPT.format(
                batch_size=batch_size,
                start_id=start_id,
                month_name=month_name,
                year=year,
                date_start=date_start,
                date_end=date_end,
            )

            print(
                f"  Batch {total_batches} ({month_name} {year}): "
                f"generating sales {start_id}-{start_id + batch_size - 1} ..."
            )

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
                print("  ERROR: Model returned no parsed output. Retrying...")
                continue

            new_sales = [s.model_dump() for s in batch.sales]

            # Re-assign SalesId sequentially to guarantee correctness
            for i, s in enumerate(new_sales):
                s["SalesId"] = start_id + i

            sales.extend(new_sales)
            generated_for_month += len(new_sales)
            save_sales(sales)
            print(
                f"  Batch {total_batches} done: +{len(new_sales)} sales, "
                f"month total: {existing_for_month + generated_for_month}, overall: {len(sales)}"
            )

    print(f"\nGeneration complete! {len(sales)} sales saved to {OUTPUT_PATH}")

    # Print per-month summary
    for year, month in MONTHS:
        count = count_sales_for_month(sales, year, month)
        print(f"  {calendar.month_name[month]} {year}: {count} sales")


if __name__ == "__main__":
    main()
