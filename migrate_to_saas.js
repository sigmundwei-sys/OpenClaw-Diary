const fs = require('fs');

const originalHtml = fs.readFileSync('index.html.original', 'utf8');

// Extract dates
const datesRegex = /<button class="date-tab.*?onclick="showScreen\\('screen-(.*?)'\\)">(.*?)<\\/button>/g;
let match;
const entries = [];

while ((match = datesRegex.exec(originalHtml)) !== null) {
    const id = match[1];
    const label = match[2];
    
    const longTextRegex = new RegExp(`<div class="screen.*?" id="screen-${id}">[\\s\\S]*?<div class="long-text">([\\s\\S]*?)</div>[\\s\\S]*?</div>`);
    const ltMatch = originalHtml.match(longTextRegex);
    const innerContent = ltMatch ? ltMatch[1].trim() : "";

    entries.push({ id, label, innerContent });
}

const uniqueEntriesMap = new Map();
entries.forEach(e => {
    if (!uniqueEntriesMap.has(e.id)) {
        uniqueEntriesMap.set(e.id, e);
    }
});
const uniqueEntries = Array.from(uniqueEntriesMap.values());

console.log(`Extracted ${uniqueEntries.length} entries.`);

const saasHtmlTemplate = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🦞 小龍的學習日記 | OpenClaw Diary</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --bg-body: #f3f4f6;
            --bg-sidebar: #ffffff;
            --bg-card: #ffffff;
            --text-main: #111827;
            --text-muted: #6b7280;
            --border-color: #e5e7eb;
            --primary: #4f46e5;
            --primary-hover: #4338ca;
            --sidebar-active: #e0e7ff;
            --sidebar-active-text: #4f46e5;
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            --radius-md: 0.5rem;
            --radius-lg: 0.75rem;
        }

        [data-theme="dark"] {
            --bg-body: #111827;
            --bg-sidebar: #1f2937;
            --bg-card: #1f2937;
            --text-main: #f9fafb;
            --text-muted: #9ca3af;
            --border-color: #374151;
            --sidebar-active: #374151;
            --sidebar-active-text: #818cf8;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Inter', sans-serif;
            transition: background-color 0.3s ease, color 0.3s ease;
        }

        body {
            background-color: var(--bg-body);
            color: var(--text-main);
            display: flex;
            height: 100vh;
            overflow: hidden;
        }

        /* Sidebar */
        .sidebar {
            width: 260px;
            background-color: var(--bg-sidebar);
            border-right: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            flex-shrink: 0;
        }

        .sidebar-header {
            padding: 1.5rem;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-size: 1.25rem;
            font-weight: 700;
        }

        .sidebar-nav {
            padding: 1rem 0;
            overflow-y: auto;
            flex-grow: 1;
        }

        .nav-section-title {
            padding: 0 1.5rem;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            font-weight: 600;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }

        .nav-item {
            display: flex;
            align-items: center;
            padding: 0.75rem 1.5rem;
            color: var(--text-muted);
            text-decoration: none;
            font-size: 0.875rem;
            font-weight: 500;
            gap: 0.75rem;
            cursor: pointer;
            border-left: 3px solid transparent;
        }

        .nav-item:hover {
            background-color: rgba(0,0,0,0.02);
            color: var(--text-main);
        }
        [data-theme="dark"] .nav-item:hover {
            background-color: rgba(255,255,255,0.02);
        }

        .nav-item.active {
            background-color: var(--sidebar-active);
            color: var(--sidebar-active-text);
            border-left-color: var(--primary);
        }

        /* Main Content */
        .main-content {
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .topbar {
            height: 64px;
            background-color: var(--bg-card);
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 2rem;
            flex-shrink: 0;
        }

        .breadcrumb {
            font-size: 0.875rem;
            color: var(--text-muted);
        }
        .breadcrumb span {
            color: var(--text-main);
            font-weight: 600;
        }

        .topbar-actions {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .icon-btn {
            background: none;
            border: none;
            color: var(--text-muted);
            font-size: 1.25rem;
            cursor: pointer;
            padding: 0.5rem;
            border-radius: var(--radius-md);
        }
        .icon-btn:hover {
            color: var(--primary);
            background-color: var(--sidebar-active);
        }

        .content-scroll {
            flex-grow: 1;
            padding: 2rem;
            overflow-y: auto;
        }

        /* KPIs */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .kpi-card {
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 1.5rem;
            display: flex;
            align-items: center;
            gap: 1.25rem;
            box-shadow: var(--shadow-sm);
        }

        .kpi-icon {
            width: 48px;
            height: 48px;
            border-radius: var(--radius-md);
            background-color: var(--sidebar-active);
            color: var(--primary);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
        }

        .kpi-info {
            display: flex;
            flex-direction: column;
        }

        .kpi-label {
            font-size: 0.875rem;
            color: var(--text-muted);
            margin-bottom: 0.25rem;
        }

        .kpi-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--text-main);
        }

        /* Diary Screen */
        .screen {
            display: none;
            animation: fadeIn 0.3s ease;
        }

        .screen.active {
            display: block;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .diary-card {
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-sm);
            overflow: hidden;
            margin-bottom: 1rem;
        }

        .diary-header {
            padding: 1.25rem 1.5rem;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: space-between;
            background-color: rgba(0,0,0,0.01);
        }
        [data-theme="dark"] .diary-header { background-color: rgba(255,255,255,0.01); }

        .diary-title {
            font-size: 1.125rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .diary-status {
            font-size: 0.875rem;
            color: #10b981;
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }

        .diary-body {
            padding: 1.5rem;
            line-height: 1.7;
            font-size: 0.95rem;
        }

        .diary-body ul {
            padding-left: 1.5rem;
            margin-bottom: 1rem;
        }
        .diary-body li {
            margin-bottom: 0.5rem;
        }
        .diary-body p {
            margin-bottom: 1rem;
        }

    </style>
</head>
<body>
    <div class="sidebar">
        <div class="sidebar-header">
            🦞 OpenClaw
        </div>
        <nav class="sidebar-nav">
            <a onclick="showOverview()" class="nav-item active" id="nav-screen-dashboard">
                <i class="fa-solid fa-chart-line"></i> Dashboard
            </a>
            
            <div class="nav-section-title">Recent Entries</div>
            <div id="date-tabs-container">
<!-- DIARY_NAV_PLACEHOLDER -->
            </div>
        </nav>
    </div>

    <div class="main-content">
        <header class="topbar">
            <div class="breadcrumb">Overview / <span id="current-date-display">Dashboard</span></div>
            <div class="topbar-actions">
                <button id="theme-toggle" class="icon-btn" onclick="toggleTheme()">
                    <i class="fa-solid fa-moon"></i>
                </button>
            </div>
        </header>

        <div class="content-scroll">
            <div class="kpi-grid" id="dashboard-kpis">
                <div class="kpi-card">
                    <div class="kpi-icon"><i class="fa-solid fa-book-open"></i></div>
                    <div class="kpi-info">
                        <div class="kpi-label">Total Entries</div>
                        <div class="kpi-value" id="kpi-total-entries">0</div>
                    </div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-icon"><i class="fa-solid fa-fire"></i></div>
                    <div class="kpi-info">
                        <div class="kpi-label">Current Streak</div>
                        <div class="kpi-value" id="kpi-streak">0 Days</div>
                    </div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-icon"><i class="fa-brands fa-github"></i></div>
                    <div class="kpi-info">
                        <div class="kpi-label">GitHub Stars</div>
                        <div class="kpi-value">136</div>
                    </div>
                </div>
            </div>

            <div id="screens-container">
<!-- DIARY_CONTENT_PLACEHOLDER -->
            </div>
            
            <div class="screen active" id="screen-dashboard">
                <div class="diary-card" style="text-align: center; padding: 4rem 2rem;">
                    <i class="fa-solid fa-rocket" style="font-size: 3rem; color: var(--primary); margin-bottom: 1rem;"></i>
                    <h2 style="margin-bottom: 0.5rem;">Welcome to the SaaS Diary</h2>
                    <p style="color: var(--text-muted);">Select an entry from the sidebar to view your learning logs.</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        const totalEntries = document.querySelectorAll('.nav-date-item').length;
        document.getElementById('kpi-total-entries').textContent = totalEntries;
        document.getElementById('kpi-streak').textContent = totalEntries > 0 ? '5 Days' : '0 Days';

        function hideAllScreens() {
            document.querySelectorAll('.screen').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
            document.getElementById('dashboard-kpis').style.display = 'none';
        }

        function showScreen(id) {
            hideAllScreens();
            const screen = document.getElementById(id);
            if(screen) screen.classList.add('active');
            
            const nav = document.getElementById('nav-' + id);
            if(nav) nav.classList.add('active');
            
            if(id !== 'screen-dashboard') {
                const dateStr = id.replace('screen-', '');
                document.getElementById('current-date-display').textContent = dateStr;
            } else {
                document.getElementById('current-date-display').textContent = 'Dashboard';
                document.getElementById('dashboard-kpis').style.display = 'grid';
            }
        }

        function showOverview() {
            showScreen('screen-dashboard');
        }

        // Theme toggle
        function toggleTheme() {
            const body = document.documentElement;
            const isDark = body.getAttribute('data-theme') === 'dark';
            body.setAttribute('data-theme', isDark ? 'light' : 'dark');
            const icon = document.querySelector('#theme-toggle i');
            if(isDark) {
                icon.className = 'fa-solid fa-moon';
                localStorage.setItem('theme', 'light');
            } else {
                icon.className = 'fa-solid fa-sun';
                localStorage.setItem('theme', 'dark');
            }
        }

        // Load theme
        if (localStorage.getItem('theme') === 'dark' || (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
            document.documentElement.setAttribute('data-theme', 'dark');
            document.querySelector('#theme-toggle i').className = 'fa-solid fa-sun';
        }

        // Initialize first screen if exists
        const firstNav = document.querySelector('.nav-date-item');
        if(firstNav) {
            firstNav.click();
        } else {
            showOverview();
        }
    </script>
</body>
</html>`;

let navPlaceholder = "";
let contentPlaceholder = "";

uniqueEntries.forEach(e => {
    navPlaceholder += `                <a onclick="showScreen('screen-${e.id}')" class="nav-item nav-date-item" id="nav-screen-${e.id}">
                    <i class="fa-regular fa-calendar"></i> ${e.label}
                </a>\n`;
    
    contentPlaceholder += `                <!-- ${e.label} -->
                <div class="screen" id="screen-${e.id}">
                    <div class="diary-card">
                        <div class="diary-header">
                            <div class="diary-title">
                                <i class="fa-regular fa-lightbulb" style="color: #f59e0b;"></i> 今天的學習總結
                            </div>
                            <div class="diary-status">
                                <i class="fa-solid fa-check"></i> 同步完成
                            </div>
                        </div>
                        <div class="diary-body">
                            ${e.innerContent}
                        </div>
                    </div>
                </div>\n`;
});

const finalHtml = saasHtmlTemplate
    .replace('<!-- DIARY_NAV_PLACEHOLDER -->', navPlaceholder + '<!-- DIARY_NAV_PLACEHOLDER -->')
    .replace('<!-- DIARY_CONTENT_PLACEHOLDER -->', contentPlaceholder + '<!-- DIARY_CONTENT_PLACEHOLDER -->');

fs.writeFileSync('index.html.new', finalHtml);

const newUpdateDiaryJs = `const fs = require('fs');
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
const newNav = \`                <a onclick="showScreen('screen-\${dateStr}')" class="nav-item nav-date-item" id="nav-screen-\${dateStr}">
                    <i class="fa-regular fa-calendar"></i> \${dateStr}
                </a>\`;

if (!html.includes(\`id="nav-screen-\${dateStr}"\`)) {
  html = html.replace('<!-- DIARY_NAV_PLACEHOLDER -->', \`\${newNav}\\n<!-- DIARY_NAV_PLACEHOLDER -->\`);
}

// 2. Format content to HTML
const formattedContent = content.split('\\n\\n').map(p => {
  if (p.startsWith('- ')) {
    return '<ul>' + p.split('\\n').filter(Boolean).map(li => \`<li>\${li.replace(/^- /, '')}</li>\`).join('') + '</ul>';
  }
  return \`<p>\${p}</p>\`;
}).join('\\n');

// 3. Add screen div
const newScreen = \`
                <!-- \${dateStr} -->
                <div class="screen" id="screen-\${dateStr}">
                    <div class="diary-card">
                        <div class="diary-header">
                            <div class="diary-title">
                                <i class="fa-regular fa-lightbulb" style="color: #f59e0b;"></i> 今天的學習總結
                            </div>
                            <div class="diary-status">
                                <i class="fa-solid fa-check"></i> 同步完成
                            </div>
                        </div>
                        <div class="diary-body">
                            \${formattedContent}
                        </div>
                    </div>
                </div>
\`;

// Insert before the placeholder
if (!html.includes(\`id="screen-\${dateStr}"\`)) {
  html = html.replace('<!-- DIARY_CONTENT_PLACEHOLDER -->', \`\${newScreen}\\n<!-- DIARY_CONTENT_PLACEHOLDER -->\`);
}

fs.writeFileSync('index.html', html);
console.log(\`Successfully updated index.html with SaaS layout entry for \${dateStr}\`);
`;

fs.writeFileSync('update_diary.js.new', newUpdateDiaryJs);
console.log("Migration finished.");
