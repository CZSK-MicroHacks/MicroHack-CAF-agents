# Vytvoření User agenta

[Zpět na přehled](../README.md) | Předchozí: přehled | Další: [Instrukce a orchestrace](02-agent-instructions.md)

V této kapitole založíte nového User agenta v Copilot Studiu a nastavíte jeho základní vlastnosti. V ukázkách používáme jméno **Bobulák**, ale v labu můžete zvolit vlastní název.

## Krok 1: Otevření Copilot Studia

Otevřete [Copilot Studio](https://copilotstudio.microsoft.com/) a po přihlášení zkontrolujte, že pracujete v environmentu **MicroHackPro**.

<img width="517" height="560" alt="Výběr prostředí MicroHackPro" src="https://github.com/user-attachments/assets/842a273f-008a-44c6-ab3c-f2c7c40e3bd2" />

## Krok 2: Vytvoření blank agenta

V levém menu zvolte **Agents** a potom v levém horním rohu vyberte **Create blank agent**.

<img width="1806" height="546" alt="Create blank agent v Copilot Studiu" src="https://github.com/user-attachments/assets/b18650c0-70bb-44c4-be34-799e4c2e1dcb" />

## Krok 3: Základní nastavení

Vyplňte základní údaje agenta.

| Pole | Hodnota |
| --- | --- |
| Name | `Bobulák` nebo vlastní název |
| Description | Použijte popis níže nebo vlastní upravenou verzi |

Zkopírujte tento popis do pole **Description**:

```text
Wine Orchestrator brings together two specialists: a Wine Analyst that surfaces sales, pricing, and performance data from Fabric, and a Wines Knowledge agent that provides pairing advice, tasting notes, varietal characteristics, and wine history from Foundry. Ask anything from "Which wines sold best last quarter?" to "What pairs well with grilled lamb?" - the orchestrator routes your question to the right expert and returns a single, coherent answer.
```

<img width="875" height="388" alt="Základní nastavení agenta" src="https://github.com/user-attachments/assets/1a6fbb87-bd2b-485d-b444-12c7d4d4faa5" />

Volitelně můžete nahrát ikonu agenta. Pro lab můžete použít tuto:

<img width="192" height="192" alt="Ikona CAGWine" src="https://github.com/user-attachments/assets/e0bc9a7e-529e-46ec-a4c1-23f20063fa0b" />

## Krok 4: Zapnutí generativní orchestrace

V pravém horním rohu otevřete **Settings** a zkontrolujte, že je zapnutá volba **Generative orchestration**.

- **Generative orchestration**: `On`

<img width="853" height="157" alt="Nastavení generativní orchestrace" src="https://github.com/user-attachments/assets/ad16fe29-b29a-4683-a187-7f9f0c3aaf21" />

## Krok 5: Výběr jazykového modelu

Doporučené nastavení pro lab je **GPT-5 Auto**.

Sidequest: Zkuste později vybrat jiný model a porovnat kvalitu směrování, styl odpovědi a konzistenci výsledku.

<img width="843" height="430" alt="Výběr jazykového modelu" src="https://github.com/user-attachments/assets/234ed8f5-9d94-4aa4-bc21-b89a91afea0d" />

---

[Zpět na přehled](../README.md) | Předchozí: přehled | Další: [Instrukce a orchestrace](02-agent-instructions.md)
