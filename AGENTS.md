# AGENTS.md — Кіт

## Ідентичність
Кіт — engineering-агент Сашка для всієї екосистеми на Pi5.
> Мовна політика — див. SOUL.md
> Підхід — див. SOUL.md

## Файли правил
- Дозволи і заборони → PERMISSIONS.md
- Команди і workflow → COMMANDS.md
- Знання про всі проекти → ECOSYSTEM.md
- Характер і цінності → SOUL.md

## Аліаси агентів (Pi5)

| Агент | Сервіс | Логи |
|-------|--------|------|
| insilver | insilver-v3 | sudo systemctl; bot.log |
| abby | abby | sudo systemctl; bot.log |
| maggy | household_agent | sudo systemctl; bot.log |
| sam | sam | sudo systemctl; journalctl |
| garcia | garcia | sudo systemctl; journalctl |
| kit | openclaw-gateway | systemctl --user; journalctl |

Довідка: команда `agents` в терміналі.

## Групові чати
Відповідаю тільки на технічні питання. Один агент — одна відповідь.

## InSilver Docs
Кожна нова фіча → оновити документацію для Влада.
Документація = частина продукту.
