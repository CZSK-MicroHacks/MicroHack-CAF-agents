"""Generate a list of 200 Czech wines using Azure OpenAI Responses API with structured outputs."""

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

OUTPUT_PATH = SCRIPT_DIR.parent / "wines.json"

BATCH_SIZE = 10
TARGET_COUNT = 60

# ---------------------------------------------------------------------------
# Pydantic models for structured output
# ---------------------------------------------------------------------------


class Wine(BaseModel):
    """Single wine record."""

    WineId: int = Field(description="Unique sequential integer ID")
    WineCode: str = Field(
        description="Short alphanumeric code derived from wine attributes, e.g. 'rv2024flpzs'"
    )
    WineName: str = Field(
        description="Full wine name in Czech including vintage, classification, and producer"
    )
    Category: str = Field(description="Suché / Polosuché / Polosladké / Sladké")
    Color: str = Field(description="Bílé / Červené / Růžové")
    Type: str = Field(description="Grape variety, e.g. Ryzlink vlašský, Pálava, Frankovka")
    Classification: str = Field(
        description="Czech wine classification: Kabinet / Pozdní sběr / Výběr z hroznů / Výběr z bobulí / Výběr z cibéb / Ledové víno / Slámové víno / Zemské víno / Jakostní víno"
    )
    Vintage: int = Field(description="Vintage year")
    Country: str = Field(description="Country of origin")
    Area: str = Field(description="Wine region, e.g. Mikulov, Velké Pavlovice, Znojmo")
    Producer: str = Field(description="Winery / producer name")
    UnitPrice: int = Field(description="Price in CZK")
    Description: str = Field(
        description=(
            "Rich, detailed Czech paragraph (150-250 words) covering: history and tradition "
            "of the winery/region, detailed tasting notes (aroma, flavor profile, body, finish), "
            "terroir and winemaking process highlights, food pairing recommendations, "
            "and any interesting facts or awards."
        )
    )


class WineBatch(BaseModel):
    """A batch of wine records returned by the model."""

    wines: list[Wine]


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
Jsi expert na česká a moravská vína s hlubokou znalostí vinařství, odrůd, terroir a vinařských klasifikací.

Tvým úkolem je generovat realistická a unikátní data o vínech. KAŽDÉ víno musí být unikátní — nesmí se opakovat \
kombinace odrůdy, ročníku, producenta a klasifikace. Data musí dávat smysl:
- Použij skutečné vinařské oblasti (Mikulov, Velké Pavlovice, Znojmo, Slovácko, Čechy, ale i zahraniční).
- Použij reálné odrůdy (Ryzlink vlašský, Ryzlink rýnský, Pálava, Tramín červený, Veltlínské zelené, \
Rulandské šedé, Rulandské bílé, Sauvignon, Chardonnay, Müller Thurgau, Frankovka, Svatovavřinecké, \
Zweigeltrebe, Cabernet Sauvignon, Merlot, Modrý Portugal, André, Dornfelder, Hibernal, Muškát moravský a další).
- Klasifikace musí odpovídat české vinařské legislativě.
- Ceny musí být realistické (80-2000 CZK podle klasifikace a kvality).
- Producenti by měli být věrohodní (můžeš použít skutečné i fiktivní, ale věrohodné názvy vinařství).
- WineCode je krátký alfanumerický kód odvozený z atributů vína (iniciály odrůdy, ročník, klasifikace, producent).

DESCRIPTION musí být bohatý, podrobný český text o 150-250 slovech pokrývající:
- Historii a tradici vinařství nebo regionu
- Detailní degustační poznámky (vůně, chuťový profil, tělo, závěr)
- Terroir a zvláštnosti vinařského procesu
- Doporučení k jídlu
- Zajímavosti nebo ocenění

Generuj přesně {batch_size} vín. WineId začíná od {start_id}. \
Zajisti maximální rozmanitost odrůd, oblastí, producentů, klasifikací, barev a kategorií."""

USER_PROMPT_WITH_CONTEXT = """\
Zde jsou vína, která už byla vygenerována (neopakuj je, generuj pouze nová unikátní vína):

{existing_wines_json}

Vygeneruj dalších {batch_size} unikátních vín s WineId začínajícím od {start_id}."""

USER_PROMPT_INITIAL = """\
Vygeneruj {batch_size} unikátních vín s WineId začínajícím od {start_id}."""

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def load_existing_wines() -> list[dict]:
    """Load previously generated wines from the output file."""
    if OUTPUT_PATH.exists():
        with open(OUTPUT_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []


def save_wines(wines: list[dict]) -> None:
    """Write wine list to JSON."""
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(wines, f, ensure_ascii=False, indent=2)


def build_summary(wines: list[dict]) -> str:
    """Build a compact summary of existing wines for context (exclude Description to save tokens)."""
    summary = []
    for w in wines:
        summary.append(
            {k: v for k, v in w.items() if k != "Description"}
        )
    return json.dumps(summary, ensure_ascii=False, indent=2)


def main() -> None:
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    )

    client = OpenAI(
        base_url=BASE_URL,
        api_key=token_provider,
    )

    wines = load_existing_wines()
    print(f"Loaded {len(wines)} existing wines from {OUTPUT_PATH}")

    batch_num = 0
    while len(wines) < TARGET_COUNT:
        batch_num += 1
        start_id = len(wines) + 1

        system = SYSTEM_PROMPT.format(batch_size=BATCH_SIZE, start_id=start_id)

        if wines:
            user = USER_PROMPT_WITH_CONTEXT.format(
                existing_wines_json=build_summary(wines),
                batch_size=BATCH_SIZE,
                start_id=start_id,
            )
        else:
            user = USER_PROMPT_INITIAL.format(batch_size=BATCH_SIZE, start_id=start_id)

        print(f"\n--- Batch {batch_num}: generating wines {start_id}-{start_id + BATCH_SIZE - 1} ---")

        response = client.responses.parse(
            model=MODEL,
            input=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            text_format=WineBatch,
        )

        batch = response.output_parsed
        if batch is None:
            print("ERROR: Model returned no parsed output. Retrying...")
            continue

        new_wines = [w.model_dump() for w in batch.wines]

        # Re-assign WineId sequentially to guarantee correctness
        for i, w in enumerate(new_wines):
            w["WineId"] = start_id + i

        wines.extend(new_wines)
        save_wines(wines)
        print(f"Batch {batch_num} done: +{len(new_wines)} wines, total: {len(wines)}")

    print(f"\nGeneration complete! {len(wines)} wines saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
