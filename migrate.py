import re
import os

with open('index.html.original', 'r', encoding='utf-8') as f:
    original_html = f.read()

# Extract dates
dates_regex = r'<button class="date-tab.*?onclick="showScreen\(\'screen-(.*?)\'\)">(.*?)</button>'
matches = re.findall(dates_regex, original_html)

entries = []
unique_ids = set()

for match in matches:
    id_val = match[0]
    label = match[1]
    
    if id_val in unique_ids:
        continue
    unique_ids.add(id_val)
    
    # Extract screen content
    long_text_regex = rf'<div class="screen.*?" id="screen-{id_val}">.*?<div class="long-text">(.*?)</div>.*?</div>'
    lt_match = re.search(long_text_regex, original_html, re.DOTALL)
    inner_content = lt_match.group(1).strip() if lt_match else ""

    entries.append({'id': id_val, 'label': label, 'content': inner_content})

print(f"Extracted {len(entries)} entries.")

saas_html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🦞 OpenClaw Diary | Flat UI SaaS</title>
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=Fira+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            /* Flat Design SaaS Dashboard Colors */
            --bg-body: #FFFBEB;
            --bg-sidebar: #FFFBEB;
            --bg-card: #FFFFFF;
            --text-main: #0F172A;
            --text-muted: #92400E;
            --border-color: #F1E8E2;
            --primary: #92400E;
            --primary-hover: #A16207;
            --accent: #6366F1;
            --sidebar-active: #F8F3F0;
            --sidebar-active-text: #92400E;
            
            --radius-md: 0px; /* Flat design often uses sharp or very slightly rounded edges */
            --radius-lg: 4px;
        }

        [data-theme="dark"] {
            --bg-body: #0F172A;
            --bg-sidebar: #0F172A;
            --bg-card: #1E293B;
            --text-main: #F8F3F0;
            --text-muted: #E2E8F0;
            --border-color: #334155;
            --sidebar-active: #1E293B;
            --sidebar-active-text: #F8F3F0;
            --primary: #A16207;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Fira Sans', sans-serif;
            transition: background-color 0.15s ease, color 0.15s ease;
        }

        body {
            background-color: var(--bg-body);
            color: var(--text-main);
            display: flex;
            height: 100vh;
            overflow: hidden;
        }

        /* Typography focused styling */
        h1, h2, h3, h4, .nav-section-title, .diary-title, .kpi-value {
            font-family: 'Fira Code', monospace;
        }

        /* Sidebar */
        .sidebar {
            width: 260px;
            background-color: var(--bg-sidebar);
            border-right: 2px solid var(--border-color);
            display: flex;
            flex-direction: column;
            flex-shrink: 0;
        }

        .sidebar-header {
            padding: 1.5rem;
            border-bottom: 2px solid var(--border-color);
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-size: 1.25rem;
            font-weight: 700;
            font-family: 'Fira Code', monospace;
            color: var(--primary);
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
            letter-spacing: 0.1em;
            color: var(--text-muted);
            font-weight: 600;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }

        .nav-item {
            display: flex;
            align-items: center;
            padding: 0.75rem 1.5rem;
            color: var(--text-main);
            text-decoration: none;
            font-size: 0.875rem;
            font-weight: 500;
            gap: 0.75rem;
            cursor: pointer;
            border-left: 4px solid transparent;
        }

        .nav-item:hover {
            background-color: var(--sidebar-active);
        }

        .nav-item.active {
            background-color: var(--sidebar-active);
            color: var(--sidebar-active-text);
            border-left-color: var(--primary);
            font-weight: 600;
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
            border-bottom: 2px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 2rem;
            flex-shrink: 0;
        }

        .breadcrumb {
            font-size: 0.875rem;
            color: var(--text-muted);
            font-family: 'Fira Code', monospace;
        }
        .breadcrumb span {
            color: var(--primary);
            font-weight: 700;
        }

        .topbar-actions {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .icon-btn {
            background: none;
            border: 2px solid var(--border-color);
            color: var(--text-main);
            font-size: 1rem;
            cursor: pointer;
            padding: 0.5rem 0.75rem;
            border-radius: var(--radius-lg);
            font-family: 'Fira Code', monospace;
        }
        .icon-btn:hover {
            border-color: var(--primary);
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
            margin-bottom: 2.5rem;
        }

        .kpi-card {
            background-color: var(--bg-card);
            border: 2px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 1.5rem;
            display: flex;
            align-items: center;
            gap: 1.25rem;
            /* No shadows in flat design */
        }

        .kpi-icon {
            width: 48px;
            height: 48px;
            background-color: var(--sidebar-active);
            color: var(--primary);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            border: 2px solid var(--primary);
        }

        .kpi-info {
            display: flex;
            flex-direction: column;
        }

        .kpi-label {
            font-size: 0.75rem;
            text-transform: uppercase;
            font-family: 'Fira Code', monospace;
            color: var(--text-muted);
            margin-bottom: 0.25rem;
            letter-spacing: 0.05em;
        }

        .kpi-value {
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--text-main);
        }

        /* Diary Screen */
        .screen {
            display: none;
        }

        .screen.active {
            display: block;
        }

        .diary-card {
            background-color: var(--bg-card);
            border: 2px solid var(--border-color);
            border-radius: var(--radius-lg);
            overflow: hidden;
            margin-bottom: 1.5rem;
        }

        .diary-header {
            padding: 1rem 1.5rem;
            border-bottom: 2px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: space-between;
            background-color: var(--sidebar-active);
        }

        .diary-title {
            font-size: 1.125rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            color: var(--primary);
        }

        .diary-status {
            font-size: 0.875rem;
            color: var(--accent);
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-family: 'Fira Code', monospace;
        }

        .diary-body {
            padding: 1.5rem;
            line-height: 1.7;
            font-size: 1rem;
        }

        .diary-body ul {
            padding-left: 1.5rem;
            margin-bottom: 1.5rem;
        }
        .diary-body li {
            margin-bottom: 0.75rem;
            padding-left: 0.5rem;
        }
        .diary-body li::marker {
            color: var(--primary);
        }
        .diary-body p {
            margin-bottom: 1.5rem;
        }

        /* Welcome Section */
        .welcome-card {
            text-align: center;
            padding: 4rem 2rem;
            border: 2px dashed var(--primary);
            background-color: transparent;
        }
        .welcome-card i {
            font-size: 3rem; 
            color: var(--primary); 
            margin-bottom: 1.5rem;
        }
        .welcome-card h2 {
            margin-bottom: 1rem;
            color: var(--text-main);
        }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="sidebar-header">
            🦞 OpenClaw Diary
        </div>
        <nav class="sidebar-nav">
            <a onclick="showOverview()" class="nav-item active" id="nav-screen-dashboard">
                <i class="fa-solid fa-server"></i> Dashboard
            </a>
            
            <div class="nav-section-title">Log Entries</div>
            <div id="date-tabs-container">
<!-- DIARY_NAV_PLACEHOLDER -->
            </div>
        </nav>
    </div>

    <div class="main-content">
        <header class="topbar">
            <div class="breadcrumb">Workspace / <span id="current-date-display">Dashboard</span></div>
            <div class="topbar-actions">
                <button id="theme-toggle" class="icon-btn" onclick="toggleTheme()" title="Toggle Theme">
                    <i class="fa-solid fa-circle-half-stroke"></i> Theme
                </button>
            </div>
        </header>

        <div class="content-scroll">
            <div class="kpi-grid" id="dashboard-kpis">
                <div class="kpi-card">
                    <div class="kpi-icon"><i class="fa-solid fa-terminal"></i></div>
                    <div class="kpi-info">
                        <div class="kpi-label">Total Logs</div>
                        <div class="kpi-value" id="kpi-total-entries">0</div>
                    </div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-icon"><i class="fa-solid fa-bolt"></i></div>
                    <div class="kpi-info">
                        <div class="kpi-label">Active Streak</div>
                        <div class="kpi-value" id="kpi-streak">0 Days</div>
                    </div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-icon"><i class="fa-brands fa-github-alt"></i></div>
                    <div class="kpi-info">
                        <div class="kpi-label">Repo Impact</div>
                        <div class="kpi-value">136</div>
                    </div>
                </div>
            </div>

            <div id="screens-container">
<!-- DIARY_CONTENT_PLACEHOLDER -->
            </div>
            
            <div class="screen active" id="screen-dashboard">
                <div class="diary-card welcome-card">
                    <i class="fa-solid fa-satellite-dish"></i>
                    <h2>System Online</h2>
                    <p style="color: var(--text-muted);">Select a log entry from the sidebar to inspect learning events.</p>
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
            if(isDark) {
                localStorage.setItem('theme', 'light');
            } else {
                localStorage.setItem('theme', 'dark');
            }
        }

        // Load theme
        if (localStorage.getItem('theme') === 'dark' || (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
            document.documentElement.setAttribute('data-theme', 'dark');
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
</html>
"""

nav_placeholder = ""
content_placeholder = ""

for e in entries:
    nav_placeholder += f"""                <a onclick="showScreen('screen-{e['id']}')" class="nav-item nav-date-item" id="nav-screen-{e['id']}">
                    <i class="fa-regular fa-folder-open"></i> {e['label']}
                </a>\n"""
    
    content_placeholder += f"""                <!-- {e['label']} -->
                <div class="screen" id="screen-{e['id']}">
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
                            {e['content']}
                        </div>
                    </div>
                </div>\n"""

final_html = saas_html_template.replace('<!-- DIARY_NAV_PLACEHOLDER -->', nav_placeholder + '<!-- DIARY_NAV_PLACEHOLDER -->')
final_html = final_html.replace('<!-- DIARY_CONTENT_PLACEHOLDER -->', content_placeholder + '<!-- DIARY_CONTENT_PLACEHOLDER -->')

with open('index.html.new', 'w', encoding='utf-8') as f:
    f.write(final_html)

new_update_diary_js = """const fs = require('fs');
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
  html = html.replace('<!-- DIARY_NAV_PLACEHOLDER -->', `${newNav}\\n<!-- DIARY_NAV_PLACEHOLDER -->`);
}

// 2. Format content to HTML
const formattedContent = content.split('\\n\\n').map(p => {
  if (p.startsWith('- ')) {
    return '<ul>' + p.split('\\n').filter(Boolean).map(li => `<li>${li.replace(/^- /, '')}</li>`).join('') + '</ul>';
  }
  return `<p>${p}</p>`;
}).join('\\n');

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
  html = html.replace('<!-- DIARY_CONTENT_PLACEHOLDER -->', `${newScreen}\\n<!-- DIARY_CONTENT_PLACEHOLDER -->`);
}

fs.writeFileSync('index.html', html);
console.log(`Successfully updated index.html with Flat SaaS layout entry for ${dateStr}`);
"""

with open('update_diary.js.new', 'w', encoding='utf-8') as f:
    f.write(new_update_diary_js)

print("Migration generated index.html.new and update_diary.js.new successfully.")
