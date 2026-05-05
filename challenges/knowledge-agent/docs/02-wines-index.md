# Index vín v AI Search

[Zpět na přehled](../README.md) | Předchozí: [Přehled dat a scénáře](01-data-overview.md) | Další: [Foundry IQ a znalostní báze](03-foundry-iq-knowledge-base.md)

Nejprve zpracujeme soubor `wines.json` a vytvoříme index v **AI Search**. Pracovat budeme v [Azure portálu](https://portal.azure.com).

## Import dat

Ve své resource group najděte AI Search a importujte data.

[![](../images/2026-04-10-13-15-49.png)](../images/2026-04-10-13-15-49.png)

[![](../images/2026-04-10-13-16-27.png)](../images/2026-04-10-13-16-27.png)

[![](../images/2026-04-10-13-16-54.png)](../images/2026-04-10-13-16-54.png)

Vyberte storage account, kontejner `wines` a formát **JSON array**. Ověřovat se budeme přes managed identity.

[![](../images/2026-04-24-15-06-54.png)](../images/2026-04-24-15-06-54.png)

Detailní nestrukturovaný popis vína je ve sloupečku `Description`. Ten budeme chtít vektorizovat a provádět nad ním semantické vyhledávání.

[![](../images/2026-04-24-15-07-55.png)](../images/2026-04-24-15-07-55.png)

## Sémantické vyhledávání

Povolíme semantic ranker pro pokročilejší hybridní vyhledávání a dojdeme na konec průvodce.

[![](../images/2026-04-10-13-22-49.png)](../images/2026-04-10-13-22-49.png)

[![](../images/2026-04-10-13-23-25.png)](../images/2026-04-10-13-23-25.png)

Zpracování souboru provádí indexer. Zkontrolujte, že doběhl v pořádku.

[![](../images/2026-04-10-13-24-46.png)](../images/2026-04-10-13-24-46.png)

## Ověření indexu

Podívejte se do indexu a zkuste vyhledávání.

[![](../images/2026-04-10-13-26-01.png)](../images/2026-04-10-13-26-01.png)

[![](../images/2026-04-10-13-27-36.png)](../images/2026-04-10-13-27-36.png)

Data o vínech máme připravené a jsme schopni hledat v jejich textových popisech. To se bude v naší knowledge base hodit.

---

[Zpět na přehled](../README.md) | Předchozí: [Přehled dat a scénáře](01-data-overview.md) | Další: [Foundry IQ a znalostní báze](03-foundry-iq-knowledge-base.md)
