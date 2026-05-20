#!/bin/bash
# update_diary.sh - Converts markdown diary to index.html
MD_FILE="$1"
if [ -z "$MD_FILE" ]; then
  echo "Usage: sh update_diary.sh <markdown-file>"
  exit 1
fi
if [ ! -f "$MD_FILE" ]; then
  echo "File not found: $MD_FILE"
  exit 1
fi

# Read markdown content and convert to a simple HTML page
python3 - "$MD_FILE" << 'PYEOF'
import sys

md_file = sys.argv[1]
with open(md_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Simple markdown-to-HTML converter
lines = content.split('\n')
html_lines = []
in_list = False

html_lines.append('<!DOCTYPE html>')
html_lines.append('<html lang="zh-TW">')
html_lines.append('<head>')
html_lines.append('<meta charset="UTF-8">')
html_lines.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
html_lines.append('<title>每日學習日記</title>')
html_lines.append('<style>')
html_lines.append('body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 800px; margin: 2rem auto; padding: 0 1rem; line-height: 1.7; }')
html_lines.append('h2 { color: #1a1a2e; border-bottom: 2px solid #eee; padding-bottom: 0.3rem; }')
html_lines.append('ul { padding-left: 1.5rem; }')
html_lines.append('li { margin: 0.4rem 0; }')
html_lines.append('code { background: #f4f4f4; padding: 0.1rem 0.3rem; border-radius: 3px; }')
html_lines.append('</style>')
html_lines.append('</head>')
html_lines.append('<body>')
html_lines.append('<h1>每日學習日記</h1>')
html_lines.append('<p><em>2026 年 5 月 20 日（週三）</em></p>')

for line in lines:
    stripped = line.strip()
    if not stripped:
        if in_list:
            html_lines.append('</ul>')
            in_list = False
        continue
    if stripped.startswith('- '):
        if not in_list:
            html_lines.append('<ul>')
            in_list = True
        text = stripped[2:]
        html_lines.append(f'<li>{text}</li>')
    else:
        if in_list:
            html_lines.append('</ul>')
            in_list = False
        # Bold
        text = stripped
        html_lines.append(f'<p>{text}</p>')

if in_list:
    html_lines.append('</ul>')

html_lines.append('</body>')
html_lines.append('</html>')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write('\n'.join(html_lines))

print("index.html generated successfully.")
PYEOF