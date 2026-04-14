#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import re
from urllib.parse import urlparse

def parse_source_url(url):
    """
    Парсит исходный URL в любом формате:
    - https://kipvalve.ru/kvng
    - kipvalve.ru/kvng
    - /kvng
    Возвращает (домен, путь)
    """
    url = url.strip()
    
    # Убираем протокол если есть
    if url.startswith('http://') or url.startswith('https://'):
        parsed = urlparse(url)
        domain = parsed.netloc
        path = parsed.path.strip('/')
    elif url.startswith('/'):
        # Относительный путь
        domain = None
        path = url.strip('/')
    else:
        # Формат без протокола: kipvalve.ru/kvng
        parts = url.split('/', 1)
        domain = parts[0]
        path = parts[1].strip('/') if len(parts) > 1 else ''
    
    return domain, path

def generate_redirect_rule(source_url, target_url, default_domain='kipvalve.ru'):
    """
    Генерирует правило редиректа для .htaccess
    """
    source_domain, source_path = parse_source_url(source_url)
    
    # Если домен не указан, используем домен по умолчанию
    if not source_domain:
        source_domain = default_domain
    
    # Если путь пустой, используем корень
    if not source_path:
        source_path = ''
    
    # Экранируем путь для regex
    escaped_path = re.escape(source_path)
    
    # Генерируем правило
    rule = f"""# Редирект с {source_url} на {target_url}
RewriteCond %{{HTTP_HOST}} ^{re.escape(source_domain)}$ [NC]
RewriteRule ^{escaped_path}/?$ {target_url} [R=301,L]"""
    
    return rule

def generate_from_csv(csv_file, output_file=None, default_domain='kipvalve.ru'):
    """
    Генерирует правила из CSV файла
    
    CSV может содержать:
    - 2 столбца: source, target
    - Или несколько столбцов, где последний - target
    """
    rules = []
    seen_paths = set()  # Для предотвращения дубликатов
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        for row_num, row in enumerate(reader, start=1):
            # Пропускаем пустые строки
            if not row or not any(cell.strip() for cell in row):
                continue
            
            # Очищаем от пустых ячеек
            row = [cell.strip() for cell in row if cell.strip()]
            
            if len(row) < 2:
                print(f"Строка {row_num}: недостаточно данных, пропущена")
                continue
            
            # Последний столбец - целевой URL
            target_url = row[-1]
            
            # Все предыдущие - исходные URL
            source_urls = row[:-1]
            
            for source_url in source_urls:
                # Проверяем, не было ли уже такое правило
                _, source_path = parse_source_url(source_url)
                
                if source_path in seen_paths:
                    print(f"Строка {row_num}: дубликат пути '{source_path}' пропущен")
                    continue
                
                seen_paths.add(source_path)
                
                # Генерируем правило
                rule = generate_redirect_rule(source_url, target_url, default_domain)
                rules.append(rule)
    
    # Формируем вывод
    output = []
    output.append("# Автоматически сгенерированные правила редиректа")
    output.append(f"# Из файла: {csv_file}")
    output.append(f"# Всего правил: {len(rules)}")
    output.append("")
    output.append("<IfModule mod_rewrite.c>")
    output.append("  RewriteEngine On")
    output.append("")
    
    for rule in rules:
        for line in rule.split('\n'):
            output.append(f"  {line}")
        output.append("")
    
    output.append("</IfModule>")
    
    # Сохраняем или выводим
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output))
        print(f"Сохранено {len(rules)} правил в {output_file}")
    else:
        print('\n'.join(output))
    
    return rules

def generate_simple(csv_file, output_file=None):
    """
    Упрощенная версия - только правила, без IfModule обертки
    """
    rules = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        for row in reader:
            if len(row) >= 2 and row[0].strip():
                source = row[0].strip()
                target = row[1].strip()
                
                # Извлекаем путь из source
                if '/' in source:
                    if '://' in source:
                        path = source.split('/', 3)[-1] if len(source.split('/')) > 3 else ''
                    else:
                        path = source.split('/', 1)[-1] if '/' in source else ''
                else:
                    path = source
                
                path = path.strip('/')
                escaped_path = re.escape(path)
                
                rule = f"""# {source} -> {target}
RewriteCond %{{HTTP_HOST}} ^kipvalve\.ru$ [NC]
RewriteRule ^{escaped_path}/?$ {target} [R=301,L]"""
                
                rules.append(rule)
    
    output = "\n\n".join(rules)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Сохранено в {output_file}")
    else:
        print(output)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Генератор правил редиректа из CSV')
    parser.add_argument('csv_file', help='Путь к CSV файлу')
    parser.add_argument('-o', '--output', help='Выходной файл')
    parser.add_argument('-d', '--domain', default='kipvalve.ru', help='Домен по умолчанию')
    parser.add_argument('-s', '--simple', action='store_true', help='Упрощенный вывод без IfModule')
    
    args = parser.parse_args()
    
    if args.simple:
        generate_simple(args.csv_file, args.output)
    else:
        generate_from_csv(args.csv_file, args.output, args.domain)