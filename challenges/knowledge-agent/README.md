# Znalostní agent s Foundry IQ

V této části MicroHacku vytvoříte znalostní vrstvu nad multimodálním obsahem o víně a postavíte nad ní Foundry Agenta. Cílem není jen jednorázové vyhledávání, ale znovupoužitelný znalostní agent, který umí kombinovat strukturovanější data, dokumenty, vybrané webové zdroje a agentní vyhledávání ve Foundry IQ.

Foundry IQ zde používáme jako specializovanou knowledge base pro doménové znalosti. Uživatelský orchestrátor se tak později nemusí snažit přímo procházet zdrojová data, ale může volat připraveného znalostního specialistu.

## Co postavíte

- AI Search index nad `wines.json` s vektorizací a semantic rankingem.
- Foundry IQ knowledge sources nad PDF dokumenty, existujícím AI Search indexem a vybranými weby o víně.
- Foundry IQ knowledge base, která tyto zdroje spojí do jednoho agentního vyhledávání.
- Foundry Agenta, který knowledge base používá jako nástroj pro odpovědi na otázky o víně.
- Volitelně evaluace a red-team kontroly pro měření kvality, stylu a bezpečnosti odpovědí.

## Průchod challenge

1. [Přehled dat a scénáře](docs/01-data-overview.md)
2. [Index vín v AI Search](docs/02-wines-index.md)
3. [Foundry IQ a znalostní báze](docs/03-foundry-iq-knowledge-base.md)
4. [Znalostní agent ve Foundry Agent Service](docs/04-foundry-agent.md)
5. [Evaluace a red teaming](docs/05-evaluations-optional.md) *(volitelné)*

## Data a podklady

V lab prostředí budete pracovat se storage účtem, který obsahuje:

- kontejner `wines` se souborem `wines.json`,
- kontejner `documents` s PDF soubory o víně, výrobě, degustaci a vinařských regionech,
- kontejner `audio` s MP3 nahrávkami pro volitelné rozšíření.

Soubory pro volitelné evaluace jsou připravené ve složce [evals](evals/).

## Doporučený postup

Nejdřív projděte povinnou část až po funkčního znalostního agenta. Evaluace berte jako navazující bonus: jsou užitečné pro ladění promptu, porovnání verzí a bezpečnostní testování, ale nejsou nutné pro základní dokončení challenge.

Začněte kapitolou [Přehled dat a scénáře](docs/01-data-overview.md).
