# TOOLS.md — Технічний довідник

## SSH патчинг (стандарт Сашка)

### Для невеликих змін
sed -i 's/old/new/g' file.py

### Для великих блоків — через Python patch
cat > /tmp/patch.py << 'EOF'
content = """..."""
with open('path/to/file', 'w') as f:
    f.write(content)
EOF
python3 /tmp/patch.py

Всередині triple quotes пиши \n замість 
 щоб уникнути SyntaxError.
НІКОЛИ не використовувати base64 або scp для патчингу.

## Перевірка після змін
tail -f [шлях_до_логів]
journalctl -u [сервіс] -f --no-pager
Завжди запускай логи ПЕРЕД тестовим повідомленням боту.

## Git workflow
git status && git log --oneline -3
git add -A && git commit -m "feat: [опис]" && git push
Швидкі команди: гіт / гіткіт / фікс / чкп — див. COMMANDS.md

## Системні утиліти Pi5
free -m          # RAM
df -h            # диск
uptime           # навантаження
ps aux | grep main.py | grep -v grep   # дублікати процесів

## Граматичні підказки (українська)
- Майбутній час: напишеш (не "писатимеш")
- Дієслова руху: йди (не "ходи")
- гарний/добрий (не "хороший")

> Мовна політика — див. SOUL.md
> Аліаси і логи по ботах — див. ECOSYSTEM.md
> Команди гіт/чкп/фікс — див. COMMANDS.md
