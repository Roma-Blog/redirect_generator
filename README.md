# Redirect Rules Generator

Утилита для генерации правил редиректа `.htaccess` из CSV-файла.

> Создано для себя, чтобы быстро решать задачи по настройке редиректов на работе.

## Описание

Программа принимает CSV-файл с парами URL (исходный → целевой) и генерирует готовые правила `RewriteRule` для Apache `.htaccess`.

## Установка

Убедитесь, что у вас установлен Python 3.12+. Дополнительные зависимости не требуются — используются только стандартные библиотеки.

## Использование

### Базовый формат CSV

CSV-файл должен содержать минимум 2 столбца:
- **Первый(ые) столбец(ы)** — исходный URL (поддерживаются форматы: `https://kipvalve.ru/kvng`, `kipvalve.ru/kvng`, `/kvng`)
- **Последний столбец** — целевой URL (полный, куда редиректить)

Пример `redirects.csv`:
```csv
/old-page,https://kipvalve.ru/new-page
kipvalve.ru/legacy,https://kipvalve.ru/modern
```

### Команды

```bash
# Полный вывод (с IfModule обёрткой)
python main.py redirects.csv

# Сохранить в файл
python main.py redirects.csv -o .htaccess

# Указать домен по умолчанию
python main.py redirects.csv -d example.com -o .htaccess

# Упрощённый вывод (только правила)
python main.py redirects.csv -s -o .htaccess
```

### Аргументы

| Аргумент | Описание |
|----------|----------|
| `csv_file` | Путь к CSV-файлу (обязательный) |
| `-o, --output` | Выходной файл |
| `-d, --domain` | Домен по умолчанию (по умолчанию: `kipvalve.ru`) |
| `-s, --simple` | Упрощённый вывод без `<IfModule>` обёртки |

