# Znalostní agent s Foundry IQ

Foundry IQ je navržené pro vytváření znalostní báze, která reprezentuje institucionální znalosti firmy kombinací různých částečně strukturovaných nebo nestrukturovaných multimodálních zdrojů. Poskytuje AI zpracování textu, dokumentů, obrázků a zvukových vstupů a také agentní vyhledávání pomocí hledání podle klíčových slov, sémantického vyhledávání, sémantického přerovnání výsledků, plánování a přepisování dotazů a agentních iterací pro dosažení co nejlepších výsledků. Hlavní myšlenkou je vytvořit řešení zaměřené na konkrétní doménové znalosti a poskytnout znovupoužitelného, testovatelného datového agenta, kterého mohou později využívat uživatelské agenti.

Lidé, kteří rozumějí datům, jsou odpovědní za vytváření Foundry IQ a za poskytování testovatelného, spolehlivého a kvalitního agentního vyhledávání. Různí uživatelsky zaměření agenti se pak mohou soustředit na interakce s uživatelem a integrace namísto toho, aby se zbytečně snažili přímo procházet zdrojová data bez odpovídajících nástrojů a znalostí.

Během této výzvy budete:
- používat prostředí Azure s Microsoft Foundry, Foundry IQ, Blob Storage, AI Search a souvisejícími službami,
- vytvářet indexer importem `wines.json`, aby vznikl index připravený pro hledání podle klíčových slov i sémantické vyhledávání,
- přidávat sémantickou konfiguraci a ověřovat, že vyhledávání funguje od začátku do konce,
- vytvářet znalostní bázi ve Foundry a propojit s ní index,
- přidávat zpracování zvukových souborů,
- přidávat pokročilé zpracování PDF pro text, tabulky, obrázky a grafy,
- přidávat webové vyhledávání pomocí vybraných webů zaměřených na víno,
- spojovat všechny zdroje do jedné znalostní báze a vytvořit Foundry Agenta, který ji používá,
- importovat evaluace a ověřit, že agent projde funkčními i red-team testy.

## Přehled dat, se kterými budeme pracovat
Ve svém storage účtu najdete PDF soubory s obrázky, infografikami, grafy a tabulkami.

[![](images/2026-04-10-11-04-37.png){:class="img-fluid"}](images/2026-04-10-11-04-37.png)

[![](images/2026-04-10-11-05-48.png){:class="img-fluid"}](images/2026-04-10-11-05-48.png)

Máme také `wines.json`, který obsahuje data o vínech včetně bohatého textového nestrukturovaného pole s popisem vinařství, chuti, historie, barvy a dalších vlastností.

[![](images/2026-04-10-11-11-03.png){:class="img-fluid"}](images/2026-04-10-11-11-03.png)

Posledním zdrojem dat jsou nahrávky podcastů s klíčovými hosty z vinařského odvětví.

[![](images/2026-04-10-11-12-40.png){:class="img-fluid"}](images/2026-04-10-11-12-40.png)

## Zpracování vín a jejich popisů
Nejprve zpracujeme soubor `wines.json` a vytvoříme index v **AI Search**. Pracovat budeme v [Azure portálu](https://portal.azure.com). 

Ve své resource group najděte AI search a pojďme importovat data.

[![](images/2026-04-10-13-15-49.png){:class="img-fluid"}](images/2026-04-10-13-15-49.png)

[![](images/2026-04-10-13-16-27.png){:class="img-fluid"}](images/2026-04-10-13-16-27.png)

[![](images/2026-04-10-13-16-54.png){:class="img-fluid"}](images/2026-04-10-13-16-54.png)

Vyberte storage account, wines kontejner a formát bude JSON array. Ověřovat se budeme přes managed identity.

[![](images/2026-04-24-15-06-54.png){:class="img-fluid"}](images/2026-04-24-15-06-54.png)

Detailní nestrukturovaný popis vína je ve sloupečku Description - to budeme chtít vektorizovat a provádět nad ním semantické vyhledávání.

[![](images/2026-04-24-15-07-55.png){:class="img-fluid"}](images/2026-04-24-15-07-55.png)

Povolíme semantický ranker pro pokročilejší hybridní vyhledávání a dojdeme na konec.

[![](images/2026-04-10-13-22-49.png){:class="img-fluid"}](images/2026-04-10-13-22-49.png)

[![](images/2026-04-10-13-23-25.png){:class="img-fluid"}](images/2026-04-10-13-23-25.png)

Zpracování souboru provádí Indexer - doběhl vám v pořádku?

[![](images/2026-04-10-13-24-46.png){:class="img-fluid"}](images/2026-04-10-13-24-46.png)

Podívejte se do indexu a zkuste vyhledávání.

[![](images/2026-04-10-13-26-01.png){:class="img-fluid"}](images/2026-04-10-13-26-01.png)

[![](images/2026-04-10-13-27-36.png){:class="img-fluid"}](images/2026-04-10-13-27-36.png)

Perfektní, data o vínech máme připravené a jsme schopni hledat v jejich textových popisech. To se bude v naší Knowledge Base určitě hodit.

## Vytvoření FoundryIQ a zpracování multimediálního obsahu

### Dokumenty jako datový zdroj
Teď se vrhneme na nestrukturovaná data - PDF obsahující tabulky, obrázky s infografikou, různé grafy a také na audio záznamy podcastů. Všechny tyto představují důležitou institucionální znalost - jak se víno vyrábí, jak se o něj pečuje, jaká vinařství a odrůdy existují, jak přistupovat k degustacím a tak podobně.

Vytvoříme nový zdroj znalostí - kontejnerem s PDF dokumenty. Použijte managed identity a model gpt-4.1.

[![](images/2026-04-24-20-02-06.png){:class="img-fluid"}](images/2026-04-24-20-02-06.png)

[![](images/2026-04-24-20-02-32.png){:class="img-fluid"}](images/2026-04-24-20-02-32.png)

[![](images/2026-04-24-20-04-28.png){:class="img-fluid"}](images/2026-04-24-20-04-28.png)

Povolíme vektorizaci na políčku Description (sémantické vyhledávání)

[![](images/2026-04-24-20-05-03.png){:class="img-fluid"}](images/2026-04-24-20-05-03.png)

[![](images/2026-04-24-20-05-40.png){:class="img-fluid"}](images/2026-04-24-20-05-40.png)

Přidáme image verbalizaci, tedy textový popis co na obrázku, infografice nebo grafu je.

[![](images/2026-04-24-20-06-31.png){:class="img-fluid"}](images/2026-04-24-20-06-31.png)

[![](images/2026-04-24-20-07-15.png){:class="img-fluid"}](images/2026-04-24-20-07-15.png)

Vytvoříme - Foundry IQ to bude nějakou dobu zpracovávat a my se mezitím podíváme na něco dalšího a pak se k tomu vrátíme.

[![](images/2026-04-24-20-08-08.png){:class="img-fluid"}](images/2026-04-24-20-08-08.png)

### Přidání indexu
Do naší budoucí knowledge base ale určitě patří i index, který jsme vytvořili v AI Search z našeho `wines.json`. Bude to další datový zdroj.

[![](images/2026-04-24-20-10-09.png){:class="img-fluid"}](images/2026-04-24-20-10-09.png)

Pojmenujeme wines, vybereme wines index a budeme chtít nastavit source data files a search fields. To první je co chceme, aby se nám vracelo - určitě ne jen Description, v JSON byly další zajímavé sloupečky a tak můžete označit prakticky všechno kromě text vektoru, takže Area, Category, Classification, Color, Country, Producer, Type, UnitPrice, Vintage, WineCode, WineId, WineName. Search fields jsou pole, které chceme mít dostupné pro vyhledávání - tam můžeme pro zjednodušení dát klidně totéž a knowledge source vytvořit.

[![](images/2026-04-24-20-14-09.png){:class="img-fluid"}](images/2026-04-24-20-14-09.png)

### Přidání vybraného webového obsahu
Pro informace o víně máme vybrané prestižní časopisy a informační stránky a ty chceme aby byly pro vyhledávání dostupné, ale ne celý internet. Přidáme.

[![](images/2026-04-24-20-15-13.png){:class="img-fluid"}](images/2026-04-24-20-15-13.png)

[![](images/2026-04-24-20-16-20.png){:class="img-fluid"}](images/2026-04-24-20-16-20.png)

Nasázejte tam tyto stránky a dovolte podstránky:

- www.wsetglobal.com
- courtofmastersommeliers.org
- www.guildsomm.com
- winefolly.com
- www.jancisrobinson.com
- vinepair.com
- www.oxfordcompaniontowine.com
- foodnetwork.co.uk

Vytvořte.

[![](images/2026-04-24-20-18-20.png){:class="img-fluid"}](images/2026-04-24-20-18-20.png)

### Jak zpracování PDF funguje?
Jste zvídaví a zajímá vás jak se PDF pod kapotou zpracovávají? Pokud ano, prohlédněte si skill pro indexaci vašich dokumentů.

[![](images/2026-04-24-16-06-26.png){:class="img-fluid"}](images/2026-04-24-16-06-26.png)

[![](images/2026-04-24-16-06-05.png){:class="img-fluid"}](images/2026-04-24-16-06-05.png)

Výsledkem je index z toho všeho - dokumenty, popisky grafů a obrázků, do textu převedené sloupce a tabulky apod.

[![](images/2026-04-24-16-07-17.png){:class="img-fluid"}](images/2026-04-24-16-07-17.png)

[![](images/2026-04-24-16-07-52.png){:class="img-fluid"}](images/2026-04-24-16-07-52.png)


### Vytvoření Knowledge Base

Knowledge zdroje máme připravené nebo se nám plní, pojďme vytvořit Knowledge Base a zařadit je do ní. Dáme jí jméno, vybereme modely, dáme maximální effor na přemýšlení s agentic retrieval. Zajímavý je output mode. Buď můžeme zvolit vrácení samotných upravených dat nebo nechat rovnou syntetizovat hotovou odpověď - nicméně my chceme použít i webové znalosti a pro ty je k dispozici pouze režim syntetizované odpovědi, ale to nám nevadí.

[![](images/2026-04-24-21-07-44.png){:class="img-fluid"}](images/2026-04-24-21-07-44.png)

[![](images/2026-04-24-21-08-33.png){:class="img-fluid"}](images/2026-04-24-21-08-33.png)

[![](images/2026-04-24-21-09-08.png){:class="img-fluid"}](images/2026-04-24-21-09-08.png)

[![](images/2026-04-24-21-09-33.png){:class="img-fluid"}](images/2026-04-24-21-09-33.png)

Dále nastavíme reasoning effort. Můžeme začít s Low, které bude fungovat ve všech použitých regionech. Později můžete vyzkoušet přepnout na mnohem intenzivnější Medium.

[![](images/2026-04-24-21-11-30.png){:class="img-fluid"}](images/2026-04-24-21-11-30.png)

Uložíme.

[![](images/2026-04-24-21-12-03.png){:class="img-fluid"}](images/2026-04-24-21-12-03.png)

Znalostní bázi vyzkoušíme. Zadejte třeba

> Chtěl bych nějakou Frankovku ze sprašových tratí, jaké máte? Píše se o nějaké znich vinepair.

[![](images/2026-04-24-21-13-45.png){:class="img-fluid"}](images/2026-04-24-21-13-45.png)

Zkuste přepnout na **Medium**, dejte New chat a zeptejte se znova. Výsledky budou pro takhle jednoduchý dotaz asi podobné, ale alespoň zjistíte, jestli ve vašem regionu je Medium podporováno. Pokud ano, nechte to na Medium a uložte.

### Úkol navíc
Ne všechno je zatím dostupné na kliknutí, ale řešení můžete snadno rozšířit o vlastní zpracování. Ve storage najdete také kontejner `audio` a v něm jsou nahrávky podcastů na téma o víně, například rozhovory s vašimi experty o vašem víně nebo trendy ve vinařství. Pokud máte čas, můžete požádat GitHub Copilot o vytvoření skriptu, který by využil nějakou službu v Microsoft Foundry pro převod těchto MP3 souborů na text, jejich umístění například do nějakého `transcripts` kontejneru a ten následně přidejte jako další knowledge source.

## Vytvoření znalostního agenta ve Foundry Agent Service
Pojďme teď vytvořit agenta nad znalostní bází a použijeme Agenty ve Foundry. Mohli bychom agenta napsat v kódu, například Microsoft Agent Framework nebo LangGraph a ve Foundry je provozovat, ale my dnes pro jednoduchost zvolíme naklikaného agenta.

Přejděte na [https://ai.azure.com](https://ai.azure.com) a ujistěte se, že máte vybraný správný projekt a váš AI Search je připojen do Foundry.

[![](images/2026-04-24-21-20-08.png){:class="img-fluid"}](images/2026-04-24-21-20-08.png)

Přejdeme do části agentů.

[![](images/2026-04-24-16-39-59.png){:class="img-fluid"}](images/2026-04-24-16-39-59.png)

[![](images/2026-04-24-16-41-23.png){:class="img-fluid"}](images/2026-04-24-16-41-23.png)

Použijeme model gpt-4.1 a začneme s velmi jednoduchým promptem.

[![](images/2026-04-24-21-21-36.png){:class="img-fluid"}](images/2026-04-24-21-21-36.png)

Z nástrojů odebereme Web search - nechceme neomezené prohledávání Internetu, máme vybrané zdroje jako součást naší Knowledge base.

[![](images/2026-04-24-21-22-35.png){:class="img-fluid"}](images/2026-04-24-21-22-35.png)

Přidáme naší knowledge base.

[![](images/2026-04-24-16-43-19.png){:class="img-fluid"}](images/2026-04-24-16-43-19.png)

[![](images/2026-04-24-16-43-47.png){:class="img-fluid"}](images/2026-04-24-16-43-47.png)

Uložíme a můžeme otestovat.

[![](images/2026-04-24-16-45-19.png){:class="img-fluid"}](images/2026-04-24-16-45-19.png)

> Chtěl bych nějakou Frankovku ze sprašových tratí, jaké máte? Nevím ale jestli má Frankovka i nějaké světové jméno, přijde mi, že je jen v čechách a pro různá vinná párování ji v zahraničí nepoužívají, je to tak?

[![](images/2026-04-24-21-26-05.png){:class="img-fluid"}](images/2026-04-24-21-26-05.png)

Podívejme se na zabudovanou observabilitu, ať máme představu co se dělo.

[![](images/2026-04-24-21-26-39.png){:class="img-fluid"}](images/2026-04-24-21-26-39.png)



## Otestování agenta s evaluations
V challenge složce najdete připravené podklady v `evals/`. Pro znalostního agenta má smysl začít hlavně evaluátory **Groundedness**, **Relevance** a jako třetí metrikou klidně **Response Completeness**, protože právě ty nejlépe odhalí, jestli agent odpovídá k věci, drží se zdrojů a nic důležitého z nich nevynechává.

- `rag_eval_queries.jsonl` je sada dotazů pro agent target eval.
- `rag_eval_with_ground_truth.jsonl` je menší sada se zlatými odpověďmi pro Response Completeness.
- `personality_eval_queries.jsonl` a `personality_judge_prompt.txt` jsou připravené pro vlastní prompt-based evaluator osobnosti.
- `validate_foundry_assets.py` umí lokálně zkontrolovat formát, v projektu dočasně založit evaluace a zase je smazat.

Prompt pro osobnost míří na styl sommeliéra z dobré restaurace: vřelý, profesionální, přesný, bez přehnané neformálnosti i bez studeného tónu.

## Red teaming
V `evals/red_team_queries.jsonl` je jednoduchá sada manuálních útoků na scope a bezpečnost: off-topic dotazy, nezletilí, pití před řízením, těhotenství, binge drinking nebo alkohol jako coping. K tomu je připravený i `wine_scope_safety_judge_prompt.txt` pro vlastní binární evaluator.

Pokud chcete použít i cloudový Foundry red teaming, validační skript vytvoří správný základ evaluace pro `red_team` scénář s built-in kontrolami jako **Prohibited Actions**, **Task Adherence** a **Sensitive Data Leakage**. Po kontrole se vše zase smaže, aby studentům zůstal čistý projekt.
