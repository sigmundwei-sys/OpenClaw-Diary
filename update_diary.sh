#!/bin/bash
# update_diary.sh - Converts markdown diary to index.html safely
MD_FILE="$1"
if [ -z "$MD_FILE" ]; then
  echo "Usage: sh update_diary.sh <markdown-file>"
  exit 1
fi
if [ ! -f "$MD_FILE" ]; then
  echo "File not found: $MD_FILE"
  exit 1
fi

DATE_STR=$(date +%Y-%m-%d)

# Use Python to update index.html preserving the UI structure
python3 - "$MD_FILE" "$DATE_STR" << 'PYEOF'
import sys
import re

md_file = sys.argv[1]
date_str = sys.argv[2]

with open(md_file, 'r', encoding='utf-8') as f:
    content = f.read().strip()

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Remove active classes
html = re.sub(r'class="date-tab active"', 'class="date-tab"', html)
html = re.sub(r'class="screen active"', 'class="screen"', html)

# 2. Add date tab
new_tab = f'<button class="date-tab active" onclick="showScreen(\'screen-{date_str}\')">{date_str}</button>'
if f"'screen-{date_str}'" not in html:
    html = re.sub(r'</button>\s*</div>', f'</button>\n            {new_tab}\n        </div>', html)

# 3. Format content to HTML
formatted_content = []
paragraphs = content.split('\n\n')
for p in paragraphs:
    if p.startswith('- '):
        lines = [line.lstrip('- ').strip() for line in p.split('\n') if line.strip()]
        formatted_content.append('<ul>' + ''.join([f'<li>{li}</li>' for li in lines]) + '</ul>')
    else:
        formatted_content.append(f'<p>{p}</p>')
formatted_html = '\n'.join(formatted_content)

# 4. Add screen div
new_screen = f"""
            <!-- {date_str} -->
            <div class="screen active" id="screen-{date_str}">
                <div class="entry">
                    <div class="entry-bar">
                        <span class="entry-filename">~/{date_str}/learning.md</span>
                        <span class="entry-status">✓</span>
                    </div>
                    <div class="entry-body">
                        <div class="quote-box">
                            <div class="quote-title">💡 今天的學習總結</div>
                            <div class="long-text">
{formatted_html}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
"""

if f'id="screen-{date_str}"' not in html:
    # Find the last screen div to append after, or use placeholder if exists
    if '<!-- Placeholder -->' in html:
        html = html.replace('<!-- Placeholder -->', f'{new_screen}\n            <!-- Placeholder -->')
    else:
        # Fallback: insert before the closing screen-container div
        html = re.sub(r'(</div>\s*<!-- Screen Container --> end)?\s*</div>\s*<script>', f'{new_screen}\n        </div>\n        <script>', html, count=1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"index.html generated successfully for {date_str}.")
PYEOF