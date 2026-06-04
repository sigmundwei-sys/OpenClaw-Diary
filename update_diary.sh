#!/bin/bash
# update_diary.sh - Converts markdown diary to index.html (sidebar layout)
MD_FILE="$1"
if [ -z "$MD_FILE" ]; then
  echo "Usage: sh update_diary.sh <markdown-file> [YYYY-MM-DD]"
  exit 1
fi
if [ ! -f "$MD_FILE" ]; then
  echo "File not found: $MD_FILE"
  exit 1
fi

DATE_STR="${2:-$(date +%Y-%m-%d)}"

python3 - "$MD_FILE" "$DATE_STR" << 'PYEOF'
import sys
import re
from datetime import datetime

md_file = sys.argv[1]
date_str = sys.argv[2]

MONTHS = ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月']
d = datetime.strptime(date_str, '%Y-%m-%d')
day_num = f'{d.day:02d}'
date_label = f'{MONTHS[d.month - 1]} {d.day} 日'

with open(md_file, 'r', encoding='utf-8') as f:
    content = f.read().strip()

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remove old active classes
html = re.sub(r'class="screen active"', 'class="screen"', html)
html = re.sub(r'class="nav-item nav-home active"', 'class="nav-item nav-home"', html)
html = re.sub(r'class="nav-item active"', 'class="nav-item"', html)

# 1. Collect all nav items
nav_matches = list(re.finditer(r'<a onclick="showScreen\(\'screen-(\d{4}-\d{2}-\d{2})\'\)" class="nav-item nav-date-item.*?" id="nav-screen-\1">\s*<span class="nav-day">\d+</span><span class="nav-date">.*?</span>\s*</a>', html, flags=re.DOTALL))

items = {}
for m in nav_matches:
    ds = m.group(1)
    items[ds] = m.group(0).replace('nav-item nav-date-item active', 'nav-item nav-date-item').replace('nav-item active nav-date-item', 'nav-item nav-date-item')

# add the new entry
new_nav = f'''                <a onclick="showScreen('screen-{date_str}')" class="nav-item nav-date-item" id="nav-screen-{date_str}">
                    <span class="nav-day">{day_num}</span><span class="nav-date">{date_label}</span>
                </a>'''
items[date_str] = new_nav

# 2. Rebuild the accordion
groups = {}
for ds in sorted(items.keys(), reverse=True):
    ym = ds[:7]
    if ym not in groups:
        groups[ym] = []
    groups[ym].append((ds, items[ds]))

new_nav_html = ""
for i, ym in enumerate(sorted(groups.keys(), reverse=True)):
    year, month = ym.split('-')
    month_name = MONTHS[int(month)-1]
    
    is_open = (i == 0)
    
    active_cls = " active" if is_open else ""
    display_style = "block" if is_open else "none"
    icon = "fa-chevron-down" if is_open else "fa-chevron-right"
    
    new_nav_html += f'''            <div class="month-group" data-month="{ym}">
                <div class="month-header{active_cls}" onclick="toggleMonth(this)">
                    {month_name} {year} <i class="fa-solid {icon}"></i>
                </div>
                <div class="month-items" style="display: {display_style};">\n'''
    for ds, m_str in groups[ym]:
        if ds == date_str:
            m_str = m_str.replace('class="nav-item nav-date-item"', 'class="nav-item nav-date-item active"')
        new_nav_html += m_str + "\n"
    new_nav_html += "                </div>\n            </div>\n"

# replace the entire date-tabs-container
html = re.sub(r'<div id="date-tabs-container">.*?</div>\s*</nav>', f'<div id="date-tabs-container">\n{new_nav_html}            </div>\n        </nav>', html, flags=re.DOTALL)

# Handle content payload
formatted_content = []
for p in content.split('\n\n'):
    if p.startswith('- '):
        lines = [line.lstrip('- ').strip() for line in p.split('\n') if line.strip()]
        formatted_content.append('<ul>' + ''.join([f'<li>{li}</li>' for li in lines]) + '</ul>')
    else:
        formatted_content.append(f'<p>{p}</p>')
formatted_html = '\n'.join(formatted_content)

new_screen = f'''
                <!-- {date_str} -->
                <div class="screen active" id="screen-{date_str}">
                    <div class="diary-card">
                        <div class="diary-header">
                            <div class="diary-title">{date_label}<time datetime="{date_str}">{date_str}</time></div>
                            <div class="diary-status"><i class="fa-solid fa-check"></i> 已儲存</div>
                        </div>
                        <div class="diary-body">
{formatted_html}
                        </div>
                    </div>
                </div>
'''

if f'id="screen-{date_str}"' not in html:
    html = html.replace('<!-- DIARY_CONTENT_PLACEHOLDER -->', f'{new_screen}\n<!-- DIARY_CONTENT_PLACEHOLDER -->')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f'index.html updated for {date_str}.')
PYEOF
