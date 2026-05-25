const fs = require('fs');
const path = require('path');

const mdFile = process.argv[2];
if (!mdFile) {
  console.error("Usage: node update_diary.js <content.md>");
  process.exit(1);
}

const content = fs.readFileSync(mdFile, 'utf8');
const dateStr = process.argv[3] || new Date().toISOString().split('T')[0];

let html = fs.readFileSync('index.html', 'utf8');

// 1. Add date nav item
const newNav = `                <a onclick="showScreen('screen-${dateStr}')" class="nav-item nav-date-item" id="nav-screen-${dateStr}">
                    <i class="fa-regular fa-folder-open"></i> ${dateStr}
                </a>`;

if (!html.includes(`id="nav-screen-${dateStr}"`)) {
  html = html.replace('<!-- DIARY_NAV_PLACEHOLDER -->', `${newNav}\n<!-- DIARY_NAV_PLACEHOLDER -->`);
}

// 2. Format content to HTML
const formattedContent = content.split('\n\n').map(p => {
  if (p.startsWith('- ')) {
    return '<ul>' + p.split('\n').filter(Boolean).map(li => `<li>${li.replace(/^- /, '')}</li>`).join('') + '</ul>';
  }
  return `<p>${p}</p>`;
}).join('\n');

// 3. Add screen div
const newScreen = `
                <!-- ${dateStr} -->
                <div class="screen" id="screen-${dateStr}">
                    <div class="diary-card">
                        <div class="diary-header">
                            <div class="diary-title">
                                <i class="fa-solid fa-code-commit"></i> LOG ENTRY
                            </div>
                            <div class="diary-status">
                                <i class="fa-solid fa-check"></i> SYNCED
                            </div>
                        </div>
                        <div class="diary-body">
                            ${formattedContent}
                        </div>
                    </div>
                </div>
`;

// Insert before the placeholder
if (!html.includes(`id="screen-${dateStr}"`)) {
  html = html.replace('<!-- DIARY_CONTENT_PLACEHOLDER -->', `${newScreen}\n<!-- DIARY_CONTENT_PLACEHOLDER -->`);
}

fs.writeFileSync('index.html', html);
console.log(`Successfully updated index.html with Flat SaaS layout entry for ${dateStr}`);
