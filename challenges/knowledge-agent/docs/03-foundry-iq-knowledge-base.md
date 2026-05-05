# Foundry IQ a znalostní báze

[Zpět na přehled](../README.md) | Předchozí: [Index vín v AI Search](02-wines-index.md) | Další: [Znalostní agent](04-foundry-agent.md)

Teď se vrhneme na nestrukturovaná data: PDF obsahující tabulky, obrázky s infografikou a různé grafy. Všechny tyto zdroje představují důležitou institucionální znalost: jak se víno vyrábí, jak se o něj pečuje, jaká vinařství a odrůdy existují, jak přistupovat k degustacím a podobně.

## Dokumenty jako datový zdroj

Vytvoříme nový zdroj znalostí nad kontejnerem s PDF dokumenty. Použijte managed identity a model `gpt-4.1`.

[![](../images/2026-04-24-20-02-06.png)](../images/2026-04-24-20-02-06.png)

[![](../images/2026-04-24-20-02-32.png)](../images/2026-04-24-20-02-32.png)

[![](../images/2026-04-24-20-04-28.png)](../images/2026-04-24-20-04-28.png)

Povolíme vektorizaci na políčku `Description`, aby šlo používat sémantické vyhledávání.

[![](../images/2026-04-24-20-05-03.png)](../images/2026-04-24-20-05-03.png)

[![](../images/2026-04-24-20-05-40.png)](../images/2026-04-24-20-05-40.png)

Přidáme image verbalizaci, tedy textový popis toho, co je na obrázku, infografice nebo grafu.

[![](../images/2026-04-24-20-06-31.png)](../images/2026-04-24-20-06-31.png)

[![](../images/2026-04-24-20-07-15.png)](../images/2026-04-24-20-07-15.png)

Vytvoříme zdroj. Foundry IQ ho bude nějakou dobu zpracovávat, takže se mezitím podíváme na další zdroje a pak se k němu vrátíme.

[![](../images/2026-04-24-20-08-08.png)](../images/2026-04-24-20-08-08.png)

## Přidání existujícího indexu

Do budoucí knowledge base patří i index, který jsme vytvořili v AI Search z `wines.json`. Bude to další datový zdroj.

[![](../images/2026-04-24-20-10-09.png)](../images/2026-04-24-20-10-09.png)

Pojmenujte zdroj `wines`, vyberte index `wines` a nastavte source data fields a search fields. Source data fields určují, co se má vracet. Určitě nechceme jen `Description`, protože v JSON byly další zajímavé sloupečky. Pro jednoduchost můžete označit prakticky všechno kromě textového vektoru, například `Area`, `Category`, `Classification`, `Color`, `Country`, `Producer`, `Type`, `UnitPrice`, `Vintage`, `WineCode`, `WineId` a `WineName`.

Search fields jsou pole dostupná pro vyhledávání. Pro zjednodušení můžete dát totéž a knowledge source vytvořit.

[![](../images/2026-04-24-20-14-09.png)](../images/2026-04-24-20-14-09.png)

## Přidání vybraného webového obsahu

Pro informace o víně máme vybrané prestižní časopisy a informační stránky. Chceme, aby byly pro vyhledávání dostupné, ale nechceme prohledávat celý internet.

[![](../images/2026-04-24-20-15-13.png)](../images/2026-04-24-20-15-13.png)

[![](../images/2026-04-24-20-16-20.png)](../images/2026-04-24-20-16-20.png)

Přidejte tyto domény a povolte podstránky:

- `www.wsetglobal.com`
- `courtofmastersommeliers.org`
- `www.guildsomm.com`
- `winefolly.com`
- `www.jancisrobinson.com`
- `vinepair.com`
- `www.oxfordcompaniontowine.com`
- `foodnetwork.co.uk`

Vytvořte webový knowledge source.

[![](../images/2026-04-24-20-18-20.png)](../images/2026-04-24-20-18-20.png)

## Jak zpracování PDF funguje?

Jste zvídaví a zajímá vás, jak se PDF pod kapotou zpracovávají? Prohlédněte si skill pro indexaci dokumentů.

[![](../images/2026-04-24-16-06-26.png)](../images/2026-04-24-16-06-26.png)

[![](../images/2026-04-24-16-06-05.png)](../images/2026-04-24-16-06-05.png)

Výsledkem je index z dokumentů, popisků grafů a obrázků, do textu převedených sloupců, tabulek a dalších částí obsahu.

[![](../images/2026-04-24-16-07-17.png)](../images/2026-04-24-16-07-17.png)

[![](../images/2026-04-24-16-07-52.png)](../images/2026-04-24-16-07-52.png)

## Vytvoření knowledge base

Knowledge sources máme připravené nebo se nám plní. Pojďme vytvořit knowledge base a zařadit je do ní.

Dáme jí jméno, vybereme modely a nastavíme agentic retrieval. Zajímavý je output mode. Buď můžeme zvolit vrácení samotných upravených dat, nebo nechat rovnou syntetizovat hotovou odpověď. Protože chceme použít i webové znalosti a pro ty je k dispozici pouze režim syntetizované odpovědi, použijeme syntetizovanou odpověď.

[![](../images/2026-04-24-21-07-44.png)](../images/2026-04-24-21-07-44.png)

[![](../images/2026-04-24-21-08-33.png)](../images/2026-04-24-21-08-33.png)

[![](../images/2026-04-24-21-09-08.png)](../images/2026-04-24-21-09-08.png)

[![](../images/2026-04-24-21-09-33.png)](../images/2026-04-24-21-09-33.png)

Dále nastavíme reasoning effort. Můžeme začít s **Low**, které bude fungovat ve všech použitých regionech. Později můžete vyzkoušet přepnout na intenzivnější **Medium**.

[![](../images/2026-04-24-21-11-30.png)](../images/2026-04-24-21-11-30.png)

Uložíme.

[![](../images/2026-04-24-21-12-03.png)](../images/2026-04-24-21-12-03.png)

## Ověření knowledge base

Znalostní bázi vyzkoušíme. Zadejte třeba:

> Chtěl bych nějakou Frankovku ze sprašových tratí, jaké máte? Píše se o nějaké z nich vinepair?

[![](../images/2026-04-24-21-13-45.png)](../images/2026-04-24-21-13-45.png)

Zkuste přepnout na **Medium**, dejte **New chat** a zeptejte se znovu. Výsledky budou pro takhle jednoduchý dotaz asi podobné, ale alespoň zjistíte, jestli je ve vašem regionu Medium podporováno. Pokud ano, nechte ho na Medium a uložte.

## Volitelný úkol navíc: audio

Ne všechno je zatím dostupné na kliknutí, ale řešení můžete snadno rozšířit o vlastní zpracování. Ve storage najdete také kontejner `audio` a v něm nahrávky podcastů na téma vína, například rozhovory s experty nebo trendy ve vinařství.

Pokud máte čas, můžete požádat GitHub Copilot o vytvoření skriptu, který využije službu v Microsoft Foundry pro převod MP3 souborů na text, uloží přepisy například do kontejneru `transcripts` a ten následně přidá jako další knowledge source.

---

[Zpět na přehled](../README.md) | Předchozí: [Index vín v AI Search](02-wines-index.md) | Další: [Znalostní agent](04-foundry-agent.md)
