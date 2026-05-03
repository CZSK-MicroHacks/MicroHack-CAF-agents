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

Vyberte Skip to configure (přeskočte konverzační nastavení wizardu).

