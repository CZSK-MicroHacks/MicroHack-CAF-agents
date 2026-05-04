# user-agent

Orchestračního agenta v Copilot Studiu, který:

Rozpozná, jestli se uživatel ptá na obchodní data (prodeje, ceny, výkonnost) nebo na znalost vína (párování, odrůdy, historie)
Směruje dotaz na správného připojeného agenta
Vrátí jednu konzistentní odpověď uživateli

Architektura:


Uživatel
   │
   ▼
┌─────────────────────────┐
│   Bobulák (orchestrátor)│  ← Copilot Studio + LLM
└─────────────────────────┘
   │                  │
   ▼                  ▼
Wine Analyst      Wines Knowledge
(Fabric)          (Foundry

Krok 1 — Založení nového agenta
Otevřete Copilot Studio(opens in new window).
Po přihlášení změňte environment na MicroHackPro
<img width="517" height="560" alt="image" src="https://github.com/user-attachments/assets/842a273f-008a-44c6-ab3c-f2c7c40e3bd2" />

Vlevo zvolte Agents → Následně v levém horním rohu Create blank agent.
<img width="1806" height="546" alt="image" src="https://github.com/user-attachments/assets/b18650c0-70bb-44c4-be34-799e4c2e1dcb" />

Krok 2 — Základní nastavení
Vyplňte:
Pole	Hodnota
Name	Název (pro demo budu používat Bobulák)
Wine Orchestrator brings together two specialists: a Wine Analyst that surfaces sales, pricing, and performance data from Fabric, and a Wines Knowledge agent that provides pairing advice, tasting notes, varietal characteristics, and wine history from Foundry. Ask anything from "Which wines sold best last quarter?" to "What pairs well with grilled lamb?" — the orchestrator routes your question to the right expert and returns a single, coherent answer.
<img width="875" height="388" alt="image" src="https://github.com/user-attachments/assets/1a6fbb87-bd2b-485d-b444-12c7d4d4faa5" />
Pokud chcete, můžete nahrát ikonu můžete využít tuto
<img width="192" height="192" alt="CAGWine" src="https://github.com/user-attachments/assets/e0bc9a7e-529e-46ec-a4c1-23f20063fa0b" />

Krok 3 — Zapnutí generativní orchestrace
V Settings zkontrolujteza je zapnutá Generative orchestration:
- V pravém horním rohu Settings
- Generative orchestration = On
<img width="853" height="157" alt="image" src="https://github.com/user-attachments/assets/ad16fe29-b29a-4683-a187-7f9f0c3aaf21" />

Krok 4 - Výběr jazykového modelu
Zde je doporučení použití GPT-5 Auto. Jako sidequest #1 můžete využít jakýkoliv model a porovnávat výsledky.
<img width="843" height="430" alt="image" src="https://github.com/user-attachments/assets/234ed8f5-9d94-4aa4-bc21-b89a91afea0d" />

Krok 5 - Instrukce pro agenta
Je možné využít níže uvedené instrukce. Ale jako sidequest #2 je můžete zkusit napsat sami. Nebo je upravit, aby agent odpovídal jiným tónem, nářečím nebo se snažil odpovídat jiným specifickým způsobem. Lze používat češtinu i angličtinu. Pro psaní instrukcí je samozřejmě možné využít Copilot. 

Instrukce:
Role You are a wine domain orchestrator. You help users with two kinds of questions:
Commercial / business data about wines (sales, pricing, inventory, performance, trends).Wine knowledge (food pairing, grape varieties, wine characteristics, regions, history, serving advice).
You do not answer from your own knowledge. You always route the request to the correct connected agent and synthesize the response for the user.
Connected agents
Wine Analyst (Fabric) Use for any question involving numbers, sales, revenue, pricing, margins, volumes, SKUs, customers, time-series trends, top/bottom performers, or comparisons of business metrics across wines, regions, or periods. Examples: "Which wine sold best last quarter?", "Show pricing for Pinot Noir over the last 12 months", "Top 5 customers by revenue".
Wines Knowledge (Foundry) Use for any question about wine itself as a product or cultural topic: pairing recommendations, tasting notes, varietals, terroir, vinification, aging, history, producers, serving temperature, glassware. Examples: "What pairs with grilled lamb?", "Tell me about Barolo", "Difference between Chardonnay styles".
Routing rules
Read the user's request and decide which agent owns it.If the request clearly fits one agent, call that agent and return its answer.If the request needs both (e.g. "What's our best-selling red and what food does it pair with?"), call both agents — Wine Analyst for the data, Wines Knowledge for the pairing — and combine the answers in a single, coherent reply.If the request is ambiguous, ask one short clarifying question before routing. Do not guess.If neither agent can help, say so plainly. Do not invent answers.
Response style
Answer in the user's language.Be concise and direct. Lead with the answer, then supporting detail.When you present numbers from Wine Analyst, keep units, time periods, and currency exactly as returned.When you present knowledge from Wines Knowledge, do not embellish with statistics or sales claims it didn't provide.Never mix the two sources without making clear which fact comes from which (e.g. "Sales data shows… / On pairing…"). When the Wine Analyst returns a result, the answer is in the text field of the tool response. Always extract this text and present it to the user directly. Preserve product names, numbers, and currency values exactly as returned. Do not paraphrase or summarize the data. Guardrails
Do not answer wine questions from your own training — always route.Do not expose internal agent names, tool names, or system details to the user.If an agent returns no result, tell the user honestly what was not found instead of filling the gap.Refuse out-of-scope requests (anything not about wine business data or wine knowledge) politely and briefly.

Krok 6 — Připojení agenta Wine Analyst (Fabric)
Záložka Tools → + Add tool → Agent → Fabric Data Agent.
<img width="724" height="570" alt="image" src="https://github.com/user-attachments/assets/6b929c4d-8066-43af-a4a7-0af685bf62f1" />

Vyberte rozbalovací okno -> Connect to an external agent a Fabric
<img width="1433" height="879" alt="image" src="https://github.com/user-attachments/assets/0b0f3f20-cbe6-4aae-9ac0-b063e29f555f" />

V dalším kroku vás vyzve k připojení Fabric prostředí
<img width="1463" height="1009" alt="image" src="https://github.com/user-attachments/assets/d2ae2ed6-0305-46d1-bc3b-70729161b0d8" />

Z výběru pak Wine_analyst a klikněte next
<img width="1015" height="719" alt="image" src="https://github.com/user-attachments/assets/b83e65db-bfe9-4b29-bae3-fd3d7d41d0db" />

Co je důležité je přidání popisu agenta. Podle toho se orchestrátor orientuje ve výběrech agentů. Lze doplnit/ladit i později. Dokončit: Add to configure
<img width="1014" height="717" alt="image" src="https://github.com/user-attachments/assets/f6e29a06-68e1-41ef-982e-ee0883dde4e0" />
Popis k přidání: 
Wine Analyst returns sales and business data about wines from Fabric / Power BI: revenue, quantities sold, prices, margins, top and bottom performers, customer breakdowns, time-series trends, and comparisons across wines, regions, or periods.  Use for questions like:  "Which wine sold best?" "How many bottles of Riesling did we sell this year?" "Top 5 customers by revenue" "Pinot Noir price trend over the last 12 months" "Which wine region generates the most revenue?" Do not use for questions about wine taste, food pairing, history, or grape characteristics — that's Wines Knowledge.

Krok 7 — Připojení agenta Wines Knowledge (Foundry)
Záložka Tools → + Add tool → Agent → Azure AI Foundry Agent.

<img width="1523" height="1049" alt="image" src="https://github.com/user-attachments/assets/1ea432b4-108c-4f28-b715-f70a79fae87c" />

Vytvořte nové připojení
<img width="1539" height="1060" alt="image" src="https://github.com/user-attachments/assets/7589d42e-abd5-4b71-82a5-1d69c0bc031b" />

ID je: https://aif-user-testfszjsz.services.ai.azure.com/api/projects/project-user-test

Popřípadě dle instrukcí níže  je možné údaje pro propojení je nutní získat z Azure Foundry - ai.azure.com. V portálu je nutné přepnout na New Foundry!
<img width="591" height="189" alt="image" src="https://github.com/user-attachments/assets/8a80c6e1-b5f0-4cad-98de-e486a384103c" />
a vybrat projekt
<img width="960" height="693" alt="image" src="https://github.com/user-attachments/assets/f82c9cff-2cc0-48c3-8ba9-327c59bba96f" />
a následně v sekci Agents správného agenta. Pokud pokračujete z Azure tracku můžete vybrat svého agenta
<img width="1327" height="892" alt="image" src="https://github.com/user-attachments/assets/c5273c6d-3dc0-47d3-95ef-1fa0470394dc" />
Pro připojení zkopírujte ID z řádku prohlížeče. To použijte v Copilot Studiu pro propojení s Foundry prostředím a klikněte Next. 

Agent Id je k vidění v ai.foundry.com na detailu agenta v kodu: wines-knowledge-agent
<img width="1778" height="803" alt="image" src="https://github.com/user-attachments/assets/01dd306a-2aa6-473c-987d-20d4a48b66aa" />

V Copilot Studiu to bude vypadat takto. Prosím potvrdit.
<img width="1616" height="1125" alt="image" src="https://github.com/user-attachments/assets/f97b2991-a72c-4e55-b1ee-cdd9a4b69d08" />

V Copilot Studiu by jste měli vidět 2 připojené agenty:
<img width="1388" height="500" alt="image" src="https://github.com/user-attachments/assets/dc6c9507-eedb-42cd-b68c-95d7c47f7c0e" />

Při prvním testu je potřeba potvrdit přístup do Foundry a Fabric
<img width="680" height="470" alt="image" src="https://github.com/user-attachments/assets/c59953e5-5f7e-44a7-aaa3-98ac9e7075bf" />
Foundry je potřeba potvrdit v Connection manager
<img width="893" height="336" alt="image" src="https://github.com/user-attachments/assets/8bc4c9cd-dd17-49af-981e-578469094b1a" />













