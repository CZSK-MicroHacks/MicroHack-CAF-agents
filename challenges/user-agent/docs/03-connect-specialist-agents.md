# Připojení specialistických agentů

[Zpět na přehled](../README.md) | Předchozí: [Instrukce a orchestrace](02-agent-instructions.md) | Další: [Testování a evaluace](04-test-and-evaluate.md)

V této kapitole připojíte k User agentovi dva specialisty: Fabric Data Agenta pro obchodní data a Foundry Agenta pro znalosti o víně.

## Krok 1: Připojení agenta Wine Analyst z Fabric

V Copilot Studiu otevřete záložku **Tools** a vyberte **+ Add tool**. Potom zvolte **Agent** a následně **Fabric Data Agent**.

<img width="724" height="570" alt="Přidání Fabric Data Agenta" src="https://github.com/user-attachments/assets/6b929c4d-8066-43af-a4a7-0af685bf62f1" />

V rozbalovacím okně vyberte **Connect to an external agent** a zvolte **Fabric**.

<img width="1433" height="879" alt="Připojení externího agenta z Fabric" src="https://github.com/user-attachments/assets/0b0f3f20-cbe6-4aae-9ac0-b063e29f555f" />

V dalším kroku potvrďte připojení k Fabric prostředí.

<img width="1463" height="1009" alt="Připojení Fabric prostředí" src="https://github.com/user-attachments/assets/d2ae2ed6-0305-46d1-bc3b-70729161b0d8" />

Ze seznamu vyberte **Wine_analyst** a klikněte na **Next**.

<img width="1015" height="719" alt="Výběr agenta Wine_analyst" src="https://github.com/user-attachments/assets/b83e65db-bfe9-4b29-bae3-fd3d7d41d0db" />

## Krok 2: Popis agenta Wine Analyst

Popis připojeného agenta je důležitý. User agent se podle něj rozhoduje, kdy má Wine Analyst použít. Popis můžete později upravovat a ladit.

Zkopírujte tento popis do pole pro description připojovaného agenta:

```text
Wine Analyst returns sales and business data about wines from Fabric / Power BI: revenue, quantities sold, prices, margins, top and bottom performers, customer breakdowns, time-series trends, and comparisons across wines, regions, or periods. Use for questions like: "Which wine sold best?" "How many bottles of Riesling did we sell this year?" "Top 5 customers by revenue" "Pinot Noir price trend over the last 12 months" "Which wine region generates the most revenue?" Do not use for questions about wine taste, food pairing, history, or grape characteristics - that's Wines Knowledge.
```

Potom dokončete přidání pomocí **Add to configure**.

<img width="1014" height="717" alt="Popis a dokončení připojení Wine Analyst" src="https://github.com/user-attachments/assets/f6e29a06-68e1-41ef-982e-ee0883dde4e0" />

## Krok 3: Připojení agenta Wines Knowledge z Foundry

V Copilot Studiu otevřete záložku **Tools**, vyberte **+ Add tool**, potom **Agent** a následně **Azure AI Foundry Agent**.

<img width="1523" height="1049" alt="Přidání Azure AI Foundry Agenta" src="https://github.com/user-attachments/assets/1ea432b4-108c-4f28-b715-f70a79fae87c" />

Vytvořte nové připojení.

<img width="1539" height="1060" alt="Vytvoření nového připojení do Foundry" src="https://github.com/user-attachments/assets/7589d42e-abd5-4b71-82a5-1d69c0bc031b" />

Project endpoint pro ukázkové prostředí:

```text
https://aif-user-testfszjsz.services.ai.azure.com/api/projects/project-user-test
```

Pokud používáte vlastní prostředí z Azure tracku, získejte údaje pro propojení v Azure AI Foundry na [ai.azure.com](https://ai.azure.com/). V portálu je potřeba přepnout na **New Foundry**.

<img width="591" height="189" alt="Přepnutí na New Foundry" src="https://github.com/user-attachments/assets/8a80c6e1-b5f0-4cad-98de-e486a384103c" />

Vyberte svůj projekt.

<img width="960" height="693" alt="Výběr Foundry projektu" src="https://github.com/user-attachments/assets/f82c9cff-2cc0-48c3-8ba9-327c59bba96f" />

V sekci **Agents** vyberte správného agenta. Pokud pokračujete z Azure tracku, můžete vybrat vlastního agenta.

<img width="1327" height="892" alt="Výběr Foundry agenta" src="https://github.com/user-attachments/assets/c5273c6d-3dc0-47d3-95ef-1fa0470394dc" />

Pro připojení zkopírujte ID z řádku prohlížeče a použijte ho v Copilot Studiu pro propojení s Foundry prostředím. Potom klikněte na **Next**.

## Krok 4: Agent ID

Agent ID najdete v detailu agenta ve Foundry. V labu používáme tuto hodnotu:

```text
wines-knowledge-agent
```

<img width="1778" height="803" alt="Agent ID ve Foundry" src="https://github.com/user-attachments/assets/01dd306a-2aa6-473c-987d-20d4a48b66aa" />

V Copilot Studiu potvrďte připojení.

<img width="1155" height="791" alt="Potvrzení Foundry agenta v Copilot Studiu" src="https://github.com/user-attachments/assets/81795f1d-0941-4671-a3af-753de47b253f" />
Popis: Wines Knowledge provides expert knowledge about wine as a product and cultural topic: food pairing, grape varietal characteristics, terroir, wine regions, vinification and aging, history, serving temperature, glassware, and tasting notes.  Use for questions like:  "What pairs with grilled lamb?" "Tell me about Barolo" "Difference between Chablis and Californian Chardonnay" "What temperature to serve red wine at?" "What grapes grow in the Mikulov sub-region?" Do not use for questions about sales, pricing, volumes, or customers — that's Wine Analyst.

Po dokončení byste měli v Copilot Studiu vidět dva připojené agenty.

<img width="1388" height="500" alt="Dva připojení agenti v Copilot Studiu" src="https://github.com/user-attachments/assets/dc6c9507-eedb-42cd-b68c-95d7c47f7c0e" />

---

[Zpět na přehled](../README.md) | Předchozí: [Instrukce a orchestrace](02-agent-instructions.md) | Další: [Testování a evaluace](04-test-and-evaluate.md)
