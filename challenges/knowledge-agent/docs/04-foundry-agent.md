# Znalostní agent ve Foundry Agent Service

[Zpět na přehled](../README.md) | Předchozí: [Foundry IQ a znalostní báze](03-foundry-iq-knowledge-base.md) | Další: [Evaluace a red teaming](05-evaluations-optional.md)

Pojďme vytvořit agenta nad znalostní bází a použijeme Agenty ve Foundry. Mohli bychom agenta napsat v kódu, například pomocí Microsoft Agent Framework nebo LangGraph a ve Foundry ho provozovat, ale dnes pro jednoduchost zvolíme naklikaného agenta.

## Vytvoření agenta

Přejděte na [https://ai.azure.com](https://ai.azure.com) a ujistěte se, že máte vybraný správný projekt a že je váš AI Search připojený do Foundry.

[![](../images/2026-04-24-21-20-08.png)](../images/2026-04-24-21-20-08.png)

Přejděte do části agentů.

[![](../images/2026-04-24-16-39-59.png)](../images/2026-04-24-16-39-59.png)

[![](../images/2026-04-24-16-41-23.png)](../images/2026-04-24-16-41-23.png)

Použijeme model `gpt-4.1` a začneme s velmi jednoduchým promptem.

[![](../images/2026-04-24-21-21-36.png)](../images/2026-04-24-21-21-36.png)

Z nástrojů odebereme **Web search**. Nechceme neomezené prohledávání internetu, protože vybrané webové zdroje už máme jako součást knowledge base.

[![](../images/2026-04-24-21-22-35.png)](../images/2026-04-24-21-22-35.png)

## Připojení knowledge base

Přidáme naši knowledge base.

[![](../images/2026-04-24-16-43-19.png)](../images/2026-04-24-16-43-19.png)

[![](../images/2026-04-24-16-43-47.png)](../images/2026-04-24-16-43-47.png)

Uložíme a můžeme otestovat.

[![](../images/2026-04-24-16-45-19.png)](../images/2026-04-24-16-45-19.png)

Zeptejte se například:

> Chtěl bych nějakou Frankovku ze sprašových tratí, jaké máte? Nevím ale jestli má Frankovka i nějaké světové jméno, přijde mi, že je jen v Čechách a pro různá vinná párování ji v zahraničí nepoužívají, je to tak?

[![](../images/2026-04-24-21-26-05.png)](../images/2026-04-24-21-26-05.png)

Podívejme se na zabudovanou observabilitu, ať máme představu, co se dělo.

[![](../images/2026-04-24-21-26-39.png)](../images/2026-04-24-21-26-39.png)

## Výsledek povinné části

V tuto chvíli máte hotový znalostní agent, který používá Foundry IQ knowledge base kombinující strukturovanější data z `wines.json`, PDF dokumenty a vybrané webové zdroje.

Další krok s evaluacemi je doporučený, ale volitelný. Hodí se hlavně tehdy, když chcete systematicky měřit kvalitu odpovědí, ladit prompt nebo si vyzkoušet red-team scénáře.

---

[Zpět na přehled](../README.md) | Předchozí: [Foundry IQ a znalostní báze](03-foundry-iq-knowledge-base.md) | Další: [Evaluace a red teaming](05-evaluations-optional.md)
