"""Generate 1000 user reviews for Czech wines using Azure OpenAI Responses API with structured outputs."""

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

OUTPUT_PATH = SCRIPT_DIR.parent / "reviews.json"
WINES_PATH = SCRIPT_DIR.parent / "wines.json"

BATCH_SIZE = 30
TARGET_COUNT = 1000

# ---------------------------------------------------------------------------
# Pydantic models for structured output
# ---------------------------------------------------------------------------


class Review(BaseModel):
    """Single user review record."""

    ReviewId: int = Field(description="Unique sequential integer ID")
    WineCode: str = Field(description="WineCode referencing a wine from the provided wine list")
    User: str = Field(
        description="Realistic Czech email address with varied domains (gmail.com, seznam.cz, email.cz, centrum.cz, post.cz, volny.cz, atlas.cz, tiscali.cz, icloud.com, outlook.cz)"
    )
    Review: str = Field(
        description="Czech text review, 1-4 sentences, varied sentiment (positive, negative, mixed). Authentic e-shop review style."
    )


class ReviewBatch(BaseModel):
    """A batch of review records returned by the model."""

    reviews: list[Review]


# ---------------------------------------------------------------------------
# Load wines for context
# ---------------------------------------------------------------------------


def load_wines() -> list[dict]:
    """Load wines from wines.json."""
    with open(WINES_PATH, encoding="utf-8") as f:
        return json.load(f)


def build_wines_context(wines: list[dict]) -> str:
    """Build compact wine list for system prompt (WineCode, WineName, Type, Category)."""
    compact = []
    for w in wines:
        compact.append({
            "WineCode": w["WineCode"],
            "WineName": w["WineName"],
            "Type": w["Type"],
            "Category": w["Category"],
            "Color": w.get("Color", ""),
            "Classification": w.get("Classification", ""),
            "UnitPrice": w.get("UnitPrice", 0),
        })
    return json.dumps(compact, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
Jsi generátor realistických uživatelských recenzí pro český e-shop s vínem.

Tvým úkolem je generovat autentické recenze vín od českých zákazníků. Recenze musí působit přirozeně, \
jako skutečné hodnocení na e-shopu — různé délky, různé styly psaní, různá úroveň znalostí o víně.

PRAVIDLA:
- Používej POUZE WineCode z následujícího seznamu vín. Žádné jiné kódy!
- Recenze musí být v češtině, 1-4 věty.
- Různý sentiment: některé velmi pozitivní (nadšené), některé negativní (zklamané), některé smíšené/neutrální.
- Recenze by měly odkazovat na skutečné vlastnosti vína (chuť, vůně, cena, příležitost, jídlo).
- Každá recenze musí být unikátní — jiná formulace, jiný úhel pohledu.
- Uživatelské emaily musí být realistické české emaily s různými doménami \
(gmail.com, seznam.cz, email.cz, centrum.cz, post.cz, volny.cz, atlas.cz, outlook.cz, icloud.com, tiscali.cz).
- Jména v emailech by měla být česká (např. jan.novak, petra.svobodova, martin.dvorak, lucie.horakova, tomas.k88 apod.).
- Některá vína by měla mít více recenzí, jiná méně — přirozená distribuce.
- Různé typy zákazníků: znalci, začátečníci, příležitostní kupující, dárkoví kupující.

PŘÍKLADY STYLŮ RECENZÍ:
- "Výborný ryzlink, přesně jak popisují. Koupím znovu!" (krátká pozitivní)
- "Za tu cenu jsem čekal víc. Víno je průměrné, nic výjimečného." (negativní)
- "Kupoval jsem jako dárek, obdarovaný byl spokojený. Pěkná láhev." (neutrální)
- "Nádherné vůně, v chuti broskev a med. Skvělé k sýrům. Jeden z nejlepších pozdních sběrů co jsem měl." (pozitivní detailní)

SEZNAM VÍN (používej POUZE tyto WineCode):
{wines_context}

Generuj přesně {batch_size} recenzí. ReviewId začíná od {start_id}."""

USER_PROMPT_WITH_CONTEXT = """\
Již vygenerované recenze (pro kontext — neopakuj formulace, zajisti rozmanitost):

Dosud vygenerováno {existing_count} recenzí.
Distribuce WineCode (počet recenzí na víno): {wine_distribution}

Poslední recenze (pro přehled stylu — piš jinak):
{recent_reviews}

Vygeneruj dalších {batch_size} unikátních recenzí s ReviewId začínajícím od {start_id}. \
Zaměř se na vína, která mají zatím méně recenzí. Měň styl, sentiment i délku."""

USER_PROMPT_INITIAL = """\
Vygeneruj {batch_size} unikátních recenzí s ReviewId začínajícím od {start_id}. \
Zajisti pestrou směs sentimentů a stylů."""

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def load_existing_reviews() -> list[dict]:
    """Load previously generated reviews from the output file."""
    if OUTPUT_PATH.exists():
        with open(OUTPUT_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []


def save_reviews(reviews: list[dict]) -> None:
    """Write review list to JSON."""
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2)


def build_summary(reviews: list[dict], wines: list[dict]) -> dict:
    """Build a compact summary of existing reviews for context."""
    from collections import Counter

    wine_counts = Counter(r["WineCode"] for r in reviews)
    # Show last 10 reviews for style reference
    recent = [
        {"WineCode": r["WineCode"], "User": r["User"], "Review": r["Review"]}
        for r in reviews[-10:]
    ]
    return {
        "wine_distribution": json.dumps(dict(wine_counts), ensure_ascii=False),
        "recent_reviews": json.dumps(recent, ensure_ascii=False, indent=2),
    }


def main() -> None:
    wines = load_wines()
    print(f"Loaded {len(wines)} wines from {WINES_PATH}")
    wines_context = build_wines_context(wines)
    valid_codes = {w["WineCode"] for w in wines}

    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    )

    client = OpenAI(
        base_url=BASE_URL,
        api_key=token_provider,
    )

    reviews = load_existing_reviews()
    # Filter out any reviews with invalid WineCodes from previous runs
    before = len(reviews)
    reviews = [r for r in reviews if r["WineCode"] in valid_codes]
    if len(reviews) < before:
        # Re-assign sequential IDs after filtering
        for i, r in enumerate(reviews):
            r["ReviewId"] = i + 1
        save_reviews(reviews)
        print(f"Filtered out {before - len(reviews)} reviews with invalid WineCodes")
    print(f"Loaded {len(reviews)} existing reviews from {OUTPUT_PATH}")

    batch_num = 0
    while len(reviews) < TARGET_COUNT:
        batch_num += 1
        start_id = len(reviews) + 1

        system = SYSTEM_PROMPT.format(
            wines_context=wines_context,
            batch_size=BATCH_SIZE,
            start_id=start_id,
        )

        if reviews:
            summary = build_summary(reviews, wines)
            user = USER_PROMPT_WITH_CONTEXT.format(
                existing_count=len(reviews),
                wine_distribution=summary["wine_distribution"],
                recent_reviews=summary["recent_reviews"],
                batch_size=BATCH_SIZE,
                start_id=start_id,
            )
        else:
            user = USER_PROMPT_INITIAL.format(batch_size=BATCH_SIZE, start_id=start_id)

        print(f"\n--- Batch {batch_num}: generating reviews {start_id}-{start_id + BATCH_SIZE - 1} ---")

        response = client.responses.parse(
            model=MODEL,
            input=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            text_format=ReviewBatch,
        )

        batch = response.output_parsed
        if batch is None:
            print("ERROR: Model returned no parsed output. Retrying...")
            continue

        new_reviews = [r.model_dump() for r in batch.reviews]

        # Filter out reviews with invalid WineCodes
        new_reviews = [r for r in new_reviews if r["WineCode"] in valid_codes]

        # Re-assign ReviewId sequentially to guarantee correctness
        for i, r in enumerate(new_reviews):
            r["ReviewId"] = len(reviews) + 1 + i

        reviews.extend(new_reviews)
        save_reviews(reviews)
        print(f"Batch {batch_num} done: +{len(new_reviews)} reviews, total: {len(reviews)}")

    print(f"\nGeneration complete! {len(reviews)} reviews saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
