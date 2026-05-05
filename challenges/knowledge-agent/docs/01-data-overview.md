# Přehled dat a scénáře

[Zpět na přehled](../README.md) | Předchozí: přehled | Další: [Index vín v AI Search](02-wines-index.md)

Foundry IQ je navržené pro vytváření znalostní báze, která reprezentuje institucionální znalosti firmy kombinací různých částečně strukturovaných nebo nestrukturovaných multimodálních zdrojů. Poskytuje AI zpracování textu, dokumentů, obrázků a zvukových vstupů a také agentní vyhledávání pomocí hledání podle klíčových slov, sémantického vyhledávání, sémantického přerovnání výsledků, plánování a přepisování dotazů a agentních iterací pro dosažení co nejlepších výsledků.

Hlavní myšlenkou je vytvořit řešení zaměřené na konkrétní doménové znalosti a poskytnout znovupoužitelného, testovatelného znalostního agenta, kterého mohou později využívat uživatelské agenti.

## Role znalostního týmu

Lidé, kteří rozumějí datům, jsou odpovědní za vytváření Foundry IQ a za poskytování testovatelného, spolehlivého a kvalitního agentního vyhledávání. Různí uživatelsky zaměření agenti se pak mohou soustředit na interakce s uživatelem a integrace namísto toho, aby se zbytečně snažili přímo procházet zdrojová data bez odpovídajících nástrojů a znalostí.

## Přehled dat

Ve svém storage účtu najdete PDF soubory s obrázky, infografikami, grafy a tabulkami.

[![](../images/2026-04-10-11-04-37.png)](../images/2026-04-10-11-04-37.png)

[![](../images/2026-04-10-11-05-48.png)](../images/2026-04-10-11-05-48.png)

Máme také `wines.json`, který obsahuje data o vínech včetně bohatého textového nestrukturovaného pole s popisem vinařství, chuti, historie, barvy a dalších vlastností.

[![](../images/2026-04-10-11-11-03.png)](../images/2026-04-10-11-11-03.png)

Posledním zdrojem dat jsou nahrávky podcastů s klíčovými hosty z vinařského odvětví.

[![](../images/2026-04-10-11-12-40.png)](../images/2026-04-10-11-12-40.png)

## Co vytvoříte

Během této části MicroHacku budete:

- používat prostředí Azure s Microsoft Foundry, Foundry IQ, Blob Storage, AI Search a souvisejícími službami,
- vytvářet indexer importem `wines.json`, aby vznikl index připravený pro hledání podle klíčových slov i sémantické vyhledávání,
- přidávat sémantickou konfiguraci a ověřovat, že vyhledávání funguje od začátku do konce,
- vytvářet znalostní bázi ve Foundry a propojit s ní index,
- přidávat pokročilé zpracování PDF pro text, tabulky, obrázky a grafy,
- přidávat webové vyhledávání pomocí vybraných webů zaměřených na víno,
- spojovat všechny zdroje do jedné znalostní báze a vytvořit Foundry Agenta, který ji používá,
- volitelně importovat evaluace a ověřit, že agent odpovídá kvalitně a bezpečně.

---

[Zpět na přehled](../README.md) | Předchozí: přehled | Další: [Index vín v AI Search](02-wines-index.md)
