const fs = require('fs');

const mdFile = process.argv[2];
if (!mdFile) {
  console.error("Usage: node update_diary.js <content.md> [YYYY-MM-DD]");
  process.exit(1);
}

const content = fs.readFileSync(mdFile, 'utf8');
const dateStr = process.argv[3] || new Date().toISOString().split('T')[0];

const MONTHS = ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月'];
const d = new Date(dateStr + 'T12:00:00');
const dayNum = String(d.getDate()).padStart(2, '0');
const dateLabel = `${MONTHS[d.getMonth()]} ${d.getDate()} 日`;

let html = fs.readFileSync('index.html', 'utf8');

const newNav = `                <a onclick="showScreen('screen-${dateStr}')" class="nav-item nav-date-item" id="nav-screen-${dateStr}">
                    <span class="nav-day">${dayNum}</span><span class="nav-date">${dateLabel}</span>
                </a>`;

if (!html.includes(`id="nav-screen-${dateStr}"`)) {
  html = html.replace('<!-- DIARY_NAV_PLACEHOLDER -->', `${newNav}\n<!-- DIARY_NAV_PLACEHOLDER -->`);
}

const formattedContent = content.split('\n\n').map(p => {
  if (p.startsWith('- ')) {
    return '<ul>' + p.split('\n').filter(Boolean).map(li => `<li>${li.replace(/^- /, '')}</li>`).join('') + '</ul>';
  }
  return `<p>${p}</p>`;
}).join('\n');

const newScreen = `
                <!-- ${dateStr} -->
                <div class="screen" id="screen-${dateStr}">
                    <div class="diary-card">
                        <div class="diary-header">
                            <div class="diary-title">${dateLabel}<time datetime="${dateStr}">${dateStr}</time></div>
                            <div class="diary-status"><i class="fa-solid fa-check"></i> 已儲存</div>
                        </div>
                        <div class="diary-body">
                            ${formattedContent}
                        </div>
                    </div>
                </div>
`;

if (!html.includes(`id="screen-${dateStr}"`)) {
  html = html.replace('<!-- DIARY_CONTENT_PLACEHOLDER -->', `${newScreen}\n<!-- DIARY_CONTENT_PLACEHOLDER -->`);
}

fs.writeFileSync('index.html', html);
console.log(`Successfully updated index.html with entry for ${dateStr}`);
