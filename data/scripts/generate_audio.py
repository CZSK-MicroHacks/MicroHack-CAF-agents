"""Generate 5 MP3 audio files about Czech wine topics using Azure OpenAI."""

import base64
import json
import os
import random
import re
import tempfile
import time
from pathlib import Path

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
from openai import AzureOpenAI, OpenAI
from pydub import AudioSegment

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
load_dotenv(SCRIPT_DIR / ".env")

ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"]
MODEL = os.environ["AZURE_OPENAI_MODEL"]  # gpt-5.2
TTS_MODEL = "gpt-audio-1.5"
BASE_URL = f"{ENDPOINT.rstrip('/')}/openai/v1/"

WINES_PATH = SCRIPT_DIR.parent / "wines.json"
OUTPUT_DIR = SCRIPT_DIR.parent / "documents"

CHUNK_CHAR_LIMIT = 3500  # chat completions audio input should stay reasonable

# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------


def _build_clients():
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    )
    # Text generation client (responses API works via OpenAI client)
    text_client = OpenAI(base_url=BASE_URL, api_key=token_provider)
    # Audio client (AzureOpenAI for chat completions with audio modality)
    audio_client = AzureOpenAI(
        azure_endpoint=ENDPOINT,
        azure_ad_token_provider=token_provider,
        api_version="2025-04-01-preview",
    )
    return text_client, audio_client


# ---------------------------------------------------------------------------
# Retry helper
# ---------------------------------------------------------------------------


def call_with_retry(func, *args, max_retries=10, **kwargs):
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "rate" in err_str.lower() or "quota" in err_str.lower():
                wait = min(2 ** attempt + random.random() * 2, 120)
                print(f"  Rate limited, waiting {wait:.1f}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait)
            elif "timeout" in err_str.lower() or "connection" in err_str.lower():
                wait = min(5 + random.random() * 5, 30)
                print(f"  Connection error, retrying (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait)
            else:
                raise
    raise Exception(f"Max retries ({max_retries}) exceeded")


# ---------------------------------------------------------------------------
# Wine data loading
# ---------------------------------------------------------------------------


def load_wines_context() -> str:
    with open(WINES_PATH, encoding="utf-8") as f:
        wines = json.load(f)
    # Compact summary without long descriptions
    summary = [{k: v for k, v in w.items() if k != "Description"} for w in wines[:30]]
    return json.dumps(summary, ensure_ascii=False, indent=1)


# ---------------------------------------------------------------------------
# Text generation
# ---------------------------------------------------------------------------


def generate_script(client: OpenAI, system_prompt: str, user_prompt: str) -> str:
    print("  Generating text script...")
    response = call_with_retry(
        client.responses.create,
        model=MODEL,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    text = response.output_text
    word_count = len(text.split())
    print(f"  Script generated: {word_count} words, {len(text)} chars")
    return text


# ---------------------------------------------------------------------------
# Text chunking at sentence boundaries
# ---------------------------------------------------------------------------


def split_into_chunks(text: str, max_chars: int = CHUNK_CHAR_LIMIT) -> list[str]:
    sentences = re.split(r'(?<=[.!?…])\s+', text)
    chunks = []
    current = ""
    for sentence in sentences:
        if len(current) + len(sentence) + 1 > max_chars and current:
            chunks.append(current.strip())
            current = sentence
        else:
            current = current + " " + sentence if current else sentence
    if current.strip():
        chunks.append(current.strip())
    return chunks


# ---------------------------------------------------------------------------
# TTS generation
# ---------------------------------------------------------------------------


def generate_audio_chunk(audio_client: AzureOpenAI, text: str, output_path: Path, voice: str = "alloy"):
    """Generate audio for a text chunk using chat completions with audio modality."""
    response = call_with_retry(
        audio_client.chat.completions.create,
        model=TTS_MODEL,
        modalities=["text", "audio"],
        audio={"voice": voice, "format": "mp3"},
        messages=[
            {
                "role": "system",
                "content": "Jsi profesionální český hlasový herec. Přečti následující text nahlas, "
                "přirozeně a srozumitelně. Čti PŘESNĚ to, co dostaneš – nic nepřidávej ani neměň.",
            },
            {"role": "user", "content": f"Přečti nahlas tento text:\n\n{text}"},
        ],
    )
    audio_data = response.choices[0].message.audio
    if not audio_data or not audio_data.data:
        raise Exception("No audio data in response")
    audio_bytes = base64.b64decode(audio_data.data)
    with open(output_path, "wb") as f:
        f.write(audio_bytes)


def generate_full_audio(audio_client: AzureOpenAI, text: str, output_path: Path, voice: str = "alloy"):
    """Generate audio from text, splitting into chunks if needed."""
    chunks = split_into_chunks(text)
    print(f"  Text split into {len(chunks)} chunks for TTS")

    if len(chunks) == 1:
        print("  Generating audio (single chunk)...")
        generate_audio_chunk(audio_client, chunks[0], output_path, voice)
        return

    chunk_files = []
    tmp_dir = Path(tempfile.mkdtemp(prefix="wine_audio_"))
    try:
        for i, chunk in enumerate(chunks):
            chunk_path = tmp_dir / f"chunk_{i:03d}.mp3"
            print(f"  Generating audio chunk {i + 1}/{len(chunks)} ({len(chunk)} chars)...")
            generate_audio_chunk(audio_client, chunk, chunk_path, voice)
            chunk_files.append(chunk_path)
            # Small delay between chunks to avoid rate limits
            if i < len(chunks) - 1:
                time.sleep(1)

        # Concatenate
        print("  Concatenating audio chunks...")
        combined = AudioSegment.empty()
        for cf in chunk_files:
            combined += AudioSegment.from_mp3(str(cf))
        combined.export(str(output_path), format="mp3")
    finally:
        # Cleanup temp files
        for cf in chunk_files:
            if cf.exists():
                cf.unlink()
        if tmp_dir.exists():
            tmp_dir.rmdir()


# ---------------------------------------------------------------------------
# Audio file definitions
# ---------------------------------------------------------------------------


def get_audio_definitions(wines_context: str) -> list[dict]:
    base_system = (
        "Jsi uznávaný český sommelier a vinařský publicista. Píšeš scénáře pro audio nahrávky o vínech. "
        "Piš přirozenou mluvenou češtinou – tak, jak by mluvil vzdělaný, ale přátelský člověk. "
        "Nepoužívej formální knižní styl, ale ani slang. Text musí znít dobře při předčítání nahlas.\n\n"
        "DŮLEŽITÉ: Piš POUZE text scénáře. Žádné poznámky, instrukce nebo metadata.\n\n"
        f"Kontext – naše kolekce vín:\n{wines_context}\n"
    )

    return [
        {
            "filename": "uvod_ceska_vina",
            "title": "Úvod do světa českých vín",
            "voice": "alloy",
            "system": base_system + (
                "Styl: Vzdělávací nahrávka s jedním vypravěčem. "
                "Tón je nadšený, ale odborný. Jako by mluvil průvodce na vinici."
            ),
            "user": (
                "Napiš scénář pro audio nahrávku 'Úvod do světa českých vín' (asi 1800 slov).\n\n"
                "Obsah:\n"
                "- Historie českého a moravského vinařství (stručně, od středověku po současnost)\n"
                "- Hlavní vinařské oblasti: Morava (podoblasti Mikulov, Velké Pavlovice, Slovácko, Znojmo) "
                "a Čechy (Litoměřicko, Mělnicko)\n"
                "- Klíčové odrůdy hroznů – bílé i červené\n"
                "- Český klasifikační systém vín (zemské, jakostní, kabinet, pozdní sběr, výběr z hroznů atd.)\n"
                "- Odkazuj na konkrétní vína z naší kolekce – zmiň jména producentů, názvy vín a oblasti.\n\n"
                "Text musí znít přirozeně při předčítání. Jeden plynulý monolog, bez nadpisů a odrážek."
            ),
        },
        {
            "filename": "degustace_pruvodce",
            "title": "Degustace vín pro začátečníky",
            "voice": "nova",
            "system": base_system + (
                "Styl: Podcastový rozhovor dvou lidí. "
                "Moderátor (zvědavý, pokládá otázky) a Expert (zkušený sommelier, odpovídá s humorem). "
                "Piš ve formátu dialogu: 'Moderátor: ...' / 'Expert: ...'\n"
                "DŮLEŽITÉ: Při generování textu piš CELÝ dialog jako souvislý text. "
                "Bude to čtené jedním hlasem, takže přidej krátké uvozovací věty typu "
                "'říká moderátor' nebo 'odpovídá expert' pro orientaci posluchače."
            ),
            "user": (
                "Napiš scénář pro audio nahrávku 'Degustace vín pro začátečníky' (asi 1800 slov).\n\n"
                "Obsah podcastového rozhovoru:\n"
                "- Jak správně ochutnávat víno – zrakem (barva, čirost), čichem (aroma, kytice), chutí\n"
                "- Běžné deskriptory vín (ovocné, květinové, minerální, kořeněné...)\n"
                "- Jak používat degustační list\n"
                "- Časté chyby začátečníků\n"
                "- Praktické tipy a příklady z naší kolekce vín\n\n"
                "Formát: Plynulý dialog mezi Moderátorem a Expertem. "
                "Text bude čten jedním hlasem, proto piš tak, aby to fungovalo jako vyprávění dialogu."
            ),
        },
        {
            "filename": "moravske_pribehy",
            "title": "Vinařské příběhy z Moravy",
            "voice": "echo",
            "system": base_system + (
                "Styl: Vyprávění, narativní tón. Jako by někdo vyprávěl příběhy u sklenky vína. "
                "Jeden vypravěč, poetický ale přístupný jazyk."
            ),
            "user": (
                "Napiš scénář pro audio nahrávku 'Vinařské příběhy z Moravy' (asi 1800 slov).\n\n"
                "Obsah:\n"
                "- Příběhy moravských vinařů a jejich vín\n"
                "- Terroir moravských podoblastí – jak půda, klima a tradice formují charakter vín\n"
                "- Konkrétní producenty a vína z naší kolekce – vyprávěj o nich jako o postavách příběhu\n"
                "- Tradice vinařství na Moravě – sklepy, vinobraní, vinařské stezky\n"
                "- Propoj fakta s emocemi a atmosférou\n\n"
                "Text musí být souvislý monolog vhodný k nahrání. Bez nadpisů a odrážek."
            ),
        },
        {
            "filename": "trendy_vinarstvi",
            "title": "Trendy ve vinařství 2025",
            "voice": "fable",
            "system": base_system + (
                "Styl: Podcastový rozhovor dvou moderátorů – Honza (nadšenec do technologií) a "
                "Petra (sommelier se zaměřením na přírodní vína). "
                "Piš jako plynulý dialog, ale protože to bude čtené jedním hlasem, "
                "uvozuj repliky jmény: 'Honza říká:' / 'Petra dodává:' apod."
            ),
            "user": (
                "Napiš scénář pro audio nahrávku 'Trendy ve vinařství 2025' (asi 1800 slov).\n\n"
                "Obsah podcastového rozhovoru Honzy a Petry:\n"
                "- Udržitelnost a ekologické vinařství\n"
                "- Přírodní vína a minimální intervence\n"
                "- Technologie ve vinicích (drony, senzory, AI)\n"
                "- Vliv klimatické změny na české vinařství\n"
                "- Zrání v amforách, oranžová vína, skin-contact bílá\n"
                "- Jak se tyto trendy projevují v české vinařské scéně\n"
                "- Odkazy na vína z naší kolekce, kde to dává smysl\n\n"
                "Formát: Přirozený dialog, ale čitelný jedním hlasem."
            ),
        },
        {
            "filename": "nas_vyber",
            "title": "Náš výběr – průvodce naší kolekcí",
            "voice": "shimmer",
            "system": base_system + (
                "Styl: Propagační/recenzní nahrávka. Jeden vypravěč, elegantní ale přátelský tón. "
                "Jako sommelier, který vám představuje vinný lístek."
            ),
            "user": (
                "Napiš scénář pro audio nahrávku 'Náš výběr – průvodce naší kolekcí' (asi 1800 slov).\n\n"
                "Obsah:\n"
                "- Vyber 10-15 zajímavých vín z naší kolekce a podrobně je představ\n"
                "- Rozděl podle barvy: bílá, červená, růžová\n"
                "- U každého vína popiš: degustační charakter, k čemu se hodí, na jakou příležitost\n"
                "- Zmiň producenta, oblast, ročník a klasifikaci\n"
                "- Závěrečné shrnutí a doporučení\n\n"
                "Text musí být plynulý monolog. Bez tabulek, odrážek nebo nadpisů."
            ),
        },
    ]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading wine data...")
    wines_context = load_wines_context()

    print("Initializing Azure OpenAI clients...")
    text_client, audio_client = _build_clients()

    definitions = get_audio_definitions(wines_context)

    for idx, defn in enumerate(definitions, 1):
        filename = defn["filename"]
        mp3_path = OUTPUT_DIR / f"{filename}.mp3"
        txt_path = OUTPUT_DIR / f"{filename}.txt"

        print(f"\n{'=' * 60}")
        print(f"[{idx}/5] {defn['title']}")
        print(f"  Output: {mp3_path.name}")
        print(f"{'=' * 60}")

        # Step 1: Generate text script
        script_text = generate_script(text_client, defn["system"], defn["user"])

        if not script_text or len(script_text) < 100:
            print(f"  WARNING: Script too short ({len(script_text)} chars), skipping")
            continue

        # Save text script
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(script_text)
        print(f"  Text saved to {txt_path.name}")

        # Step 2: Generate audio
        generate_full_audio(audio_client, script_text, mp3_path, voice=defn["voice"])

        # Verify
        if mp3_path.exists():
            size_mb = mp3_path.stat().st_size / (1024 * 1024)
            print(f"  ✓ Audio saved: {mp3_path.name} ({size_mb:.1f} MB)")
        else:
            print(f"  ✗ FAILED to create {mp3_path.name}")

    # Final summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    for defn in definitions:
        mp3_path = OUTPUT_DIR / f"{defn['filename']}.mp3"
        if mp3_path.exists():
            size_mb = mp3_path.stat().st_size / (1024 * 1024)
            print(f"  ✓ {mp3_path.name} ({size_mb:.1f} MB)")
        else:
            print(f"  ✗ {mp3_path.name} MISSING")


if __name__ == "__main__":
    main()
