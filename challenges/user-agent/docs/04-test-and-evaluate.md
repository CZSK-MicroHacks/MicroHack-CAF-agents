# Testování a evaluace

[Zpět na přehled](../README.md) | Předchozí: [Připojení specialistických agentů](03-connect-specialist-agents.md) | Další: konec

V této kapitole ověříte, že User agent správně směruje dotazy na připojené specialisty. Zároveň si můžete vyzkoušet volitelné evaluace pro hromadné testování.

## Krok 1: Potvrzení přístupů při prvním testu

Při prvním testu je potřeba potvrdit přístup do Foundry a Fabric.

<img width="680" height="470" alt="Potvrzení přístupu do Foundry a Fabric" src="https://github.com/user-attachments/assets/c59953e5-5f7e-44a7-aaa3-98ac9e7075bf" />

Foundry připojení je potřeba potvrdit v **Connection manageru**.

<img width="893" height="336" alt="Connection manager pro Foundry připojení" src="https://github.com/user-attachments/assets/8bc4c9cd-dd17-49af-981e-578469094b1a" />

## Krok 2: Ruční testování User agenta

V testovacím okně vyzkoušejte otázky, které patří do různých kategorií.

Obchodní dotazy pro Wine Analyst:

```text
Které víno mělo nejvyšší prodeje za poslední kvartál?
```

```text
Ukaž top 5 zákazníků podle tržeb.
```

Znalostní dotazy pro Wines Knowledge:

```text
Jaké jídlo se hodí ke grilovanému jehněčímu?
```

```text
Jaký je rozdíl mezi styly Chardonnay?
```

Kombinovaný dotaz pro oba specialisty:

```text
Které červené víno se prodává nejlépe a k jakému jídlu se hodí?
```

<img width="726" height="998" alt="Testování User agenta v Copilot Studiu" src="https://github.com/user-attachments/assets/237d89c2-a38e-48e8-9009-a3f925c18be5" />

## Krok 3: Volitelné evaluace

Sidequest: V části **Evaluation** můžete provádět hromadné testy agenta. Hodí se to pro ladění instrukcí, porovnání modelů a ověření, že agent správně směruje různé typy dotazů.

<img width="1314" height="925" alt="Evaluation v Copilot Studiu" src="https://github.com/user-attachments/assets/1c3e2810-c9e7-4953-99bb-8d6c7bc74133" />

Začněte přes **Create a test set**.

<img width="1421" height="728" alt="Create a test set" src="https://github.com/user-attachments/assets/76efa678-5946-4961-b321-c8e2fcd4999d" />

Můžete si vybrat, zda otázky necháte vygenerovat, nebo nahrajete vlastní otázky. Vlastní otázky mohou být vymyšlené, nebo odvozené z historického používání agenta.

Příklad vygenerovaných otázek:

<img width="2108" height="998" alt="Příklad generovaných evaluačních otázek" src="https://github.com/user-attachments/assets/0e965c1e-5fe2-43a3-93a7-e979c819ee1b" />

Nakonec vyberte testovací metodu z dostupných možností.

<img width="857" height="1037" alt="Výběr testovací metody" src="https://github.com/user-attachments/assets/7bcb6670-e6d4-4df3-aeef-2d58f9a90438" />

## Krok 4: Hotovo

Gratulujeme, máte funkční multiagentní prostředí. User agent teď může přijímat běžné uživatelské dotazy, směrovat je na správné specialisty a vracet sjednocenou odpověď.

---

[Zpět na přehled](../README.md) | Předchozí: [Připojení specialistických agentů](03-connect-specialist-agents.md) | Další: konec
