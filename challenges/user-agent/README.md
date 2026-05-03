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


CAGWine.png
Language	Czech (cs-CZ)


