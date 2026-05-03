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
Vlevo zvolte Agents → + New agent.
Vyberte Skip to configure (přeskočte konverzační nastavení wizardu).

