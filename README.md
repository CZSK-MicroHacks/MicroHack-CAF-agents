# MicroHack CAF Agents

MicroHack pro AI agenty připravený pro akci Cloud Architecture Forum 2026.

V tomto microhacku si projdete návrh a stavbu agentního řešení nad doménou prodeje a znalostí o víně. Cílem není vytvořit jednoho univerzálního chatbota, který se snaží odpovědět na všechno sám. Místo toho si vyzkoušíte praktičtější architekturu složenou z několika specializovaných agentů: jeden pracuje s obchodními daty, druhý se znalostní bází a třetí je uživatelský orchestrátor, který pozná záměr uživatele a pošle dotaz správným směrem.

Scénář je postavený na fiktivní vinařské firmě. Budete pracovat s prodejními daty, recenzemi zákazníků, popisy vín, dokumenty, obrázky, grafy, tabulkami, audio nahrávkami a vybraným webovým obsahem. Na konci by měl uživatel dostat jeden přirozený konverzační zážitek, ve kterém se může ptát jak na obchodní otázky typu „které víno se prodávalo nejlépe“, tak na znalostní otázky typu „co se hodí ke grilovanému jehněčímu“.

## Co budete stavět

MicroHack je rozdělený do tří navazujících částí:

1. [Business Data Agent](./challenges/business-data-agent/README.md)  
	V Microsoft Fabric připravíte lakehouse nad obchodními daty o vínech, projdete medallion architekturu, obohatíte recenze pomocí LLM funkcí a vytvoříte datového agenta schopného odpovídat na otázky nad prodeji, cenami, zákazníky a sortimentem.

2. [Knowledge Agent](./challenges/knowledge-agent/README.md)  
	V Microsoft Foundry a Foundry IQ vytvoříte znalostní bázi z multimodálních zdrojů. Budete kombinovat strukturovanější data z `wines.json`, PDF dokumenty, obrázky, grafy, audio nahrávky a vybrané webové zdroje tak, aby agent uměl vyhledávat a odpovídat na znalostní otázky o víně.

3. [User Agent](./challenges/user-agent/README.md)  
	V Copilot Studiu postavíte uživatelského orchestračního agenta, který propojí oba backendové agenty. Jeho úkolem bude rozpoznat, jestli se uživatel ptá na obchodní data nebo na znalosti o víně, zavolat správného specialistu a vrátit jednu srozumitelnou odpověď pro Microsoft 365 Copilot nebo Teams scénář.

## O co tady půjde

Celé cvičení ukazuje, jak může vypadat moderní agentní architektura v praxi. Místo izolované ukázky jednoho nástroje si projdete celý řetězec: přípravu dat, obohacení dat pomocí AI, vytvoření znalostní vrstvy, napojení specializovaných agentů a finální uživatelskou orchestraci.

Prakticky si vyzkoušíte:

- práci s daty v Microsoft Fabric a OneLake,
- tvorbu lakehouse a medallion vrstev,
- použití LLM pro obohacení zákaznických recenzí,
- vytvoření Fabric Data Agenta pro dotazy nad obchodními daty,
- vytvoření Foundry IQ znalostní báze nad multimodálním obsahem,
- vyhledávání pomocí AI Search, sémantického rankingu a agentního vyhledávání,
- propojení backendových agentů do Copilot Studia,
- návrh instrukcí, směrování dotazů a testování odpovědí orchestrátora.

Výsledkem bude prototyp řešení, ve kterém se uživatel nemusí starat o to, ve kterém systému data leží. Zeptá se přirozeným jazykem a orchestrace se postará o to, jestli odpověď přijde z Fabric datového agenta, Foundry znalostního agenta, nebo z kombinace obou.
