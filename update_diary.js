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

// 1. Remove active classes from old tabs and screens
html = html.replace(/class="date-tab active"/g, 'class="date-tab"');
html = html.replace(/class="screen active"/g, 'class="screen"');

// 2. Add date tab
const newTab = `<button class="date-tab active" onclick="showScreen('screen-${dateStr}')">${dateStr}</button>`;
if (!html.includes(`'screen-${dateStr}'`)) {
  // Replace the closing div of tabs with the new tab and closing div
  html = html.replace(/<\/button>\s*<\/div>/, `</button>\n            ${newTab}\n        </div>`);
  // If it failed, try another match
  if (!html.includes(newTab)) {
    console.error("Failed to insert date tab. Is the HTML structure correct?");
  }
}

// 3. Format content to HTML
// Basic markdown parsing
const formattedContent = content.split('\n\n').map(p => {
  if (p.startsWith('- ')) {
    return '<ul>' + p.split('\n').filter(Boolean).map(li => `<li>${li.replace(/^- /, '')}</li>`).join('') + '</ul>';
  }
  return `<p>${p}</p>`;
}).join('\n');

// 4. Add screen div
const newScreen = `
            <!-- ${dateStr} -->
            <div class="screen active" id="screen-${dateStr}">
                <div class="entry">
                    <div class="entry-bar">
                        <span class="entry-filename">~/${dateStr}/learning.md</span>
                        <span class="entry-status">✓</span>
                    </div>
                    <div class="entry-body">
                        <div class="quote-box">
                            <div class="quote-title">💡 今天的學習總結</div>
                            <div class="long-text">
${formattedContent}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
`;

// Insert before the placeholder
if (!html.includes(`id="screen-${dateStr}"`)) {
  html = html.replace('<!-- Placeholder -->', `${newScreen}\n            <!-- Placeholder -->`);
}

fs.writeFileSync('index.html', html);
console.log(`Successfully updated index.html with entry for ${dateStr}`);
