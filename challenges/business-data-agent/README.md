![](/challenges/business-data-agent/images/intro1.png)

# Úvod
Pracuješ jako datový analytik ve společnosti zabývající se prodejem a distribucí vín. 
Tvůj nový úkol je vybudovat ***prototyp*** "datového agenta", který bude schopen odpovídat na otázky psané přirozenou řečí o prodejích vín a spokojenosti našich zákazníků s nabízeným sortimentem. Zároveň agent bude připraven pro připojení do agentního workflow připravovaného naším aplikačním teamem.

Z architektonického pohledu budeš vytvářet [Lakehouse a Medallion architekturu](/challenges/business-data-agent/challenges/lakehouse-layers.md) v platformě [Microsoft Fabric](https://www.microsoft.com/en-us/microsoft-fabric/resources/data-101/what-is-fabric?msockid=37ed1b5fdff06f8b2508082bde936ec1). 
Data, která budeš postupně zpracovávat a obohacovat jsou extrakty v JSON souborech s následující strukturou:

![](/challenges/business-data-agent/images/model.png)



## Výsledek
Výsledkem bude následující workflow:
- **Get data** - získání dat z Azure Blob Storage
- **Store** - uložení zdrojových, zpracovaných a obohacených dat ve [OneLake](https://learn.microsoft.com/en-us/fabric/onelake/onelake-overview) ([Fabric - Lakehouse](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-overview))
- **Prepare** - příprava dat do struktury vhodné pro analýzy
- **Analyze and train** - obohacení dat (vytěžení uživatelských recenzí) pomocí LLM
- **Distribute** - datový agent, který podporuje NL2SQL nad daty ve [OneLake](https://learn.microsoft.com/en-us/fabric/onelake/onelake-overview) ([Fabric - Lakehouse](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-overview))
- **Track** - automatizované testování datového agenta

![](/challenges/business-data-agent/images/ch01_00.png)


## Plán

1. [Získat data z POSky a recenzí stažených z webu](/challenges/business-data-agent/challenges/01_source_data.md)
2. [Transformovat data do tabulárního datového modelu](/challenges/business-data-agent/challenges/02_curated_data.md)
3. [Procesovat text recenzí LLM modely do strukturované podoby](/challenges/business-data-agent/challenges/03_llm_ai_functions.md)
4. [Vytvořit a vyladit datového agenta](/challenges/business-data-agent/challenges/04_data_agent.md)
5. ***volitelné*** [Automatické testovaní datového agenta pomocí SDK](/challenges/business-data-agent/challenges/05_data_agent_sdk.md)




