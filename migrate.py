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
    <title>☕ 小龍的生活日記 | Lifestyle Diary</title>
    <link href="https://fonts.googleapis.com/css2?family=Caveat:wght@400;500;600;700&family=Quicksand:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            /* Lifestyle & Soft UI Evolution Colors */
            --bg-body: #FAFAFA;
            --bg-sidebar: #FAFAFA;
            --bg-card: #FFFFFF;
            --text-main: #09090B;
            --text-muted: #71717A;
            --border-color: #E4E4E7;
            --primary: #18181B;
            --primary-hover: #3F3F46;
            --accent: #2563EB;
            --sidebar-active: #F4F4F5;
            --sidebar-active-text: #18181B;
            
            --radius-md: 12px; 
            --radius-lg: 20px;
            --radius-full: 9999px;
            
            --shadow-soft: 0 4px 20px -2px rgba(0, 0, 0, 0.05);
            --shadow-hover: 0 10px 30px -4px rgba(0, 0, 0, 0.08);
        }

        [data-theme="dark"] {
            --bg-body: #09090B;
            --bg-sidebar: #09090B;
            --bg-card: #18181B;
            --text-main: #FAFAFA;
            --text-muted: #A1A1AA;
            --border-color: #27272A;
            --sidebar-active: #27272A;
            --sidebar-active-text: #FAFAFA;
            --primary: #FAFAFA;
            --primary-hover: #D4D4D8;
            --shadow-soft: 0 4px 20px -2px rgba(0, 0, 0, 0.4);
            --shadow-hover: 0 10px 30px -4px rgba(0, 0, 0, 0.6);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Quicksand', sans-serif;
            transition: background-color 0.3s ease, color 0.3s ease, box-shadow 0.3s ease;
        }

        body {
            background-color: var(--bg-body);
            color: var(--text-main);
            display: flex;
            height: 100vh;
            overflow: hidden;
            letter-spacing: 0.02em;
        }

        /* Typography */
        h1, h2, h3, .diary-title, .welcome-title {
            font-family: 'Caveat', cursive;
            letter-spacing: 0.05em;
        }

        /* Sidebar */
        .sidebar {
            width: 280px;
            background-color: var(--bg-sidebar);
            border-right: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            flex-shrink: 0;
        }

        .sidebar-header {
            padding: 2rem 1.5rem 1rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-size: 2.25rem;
            font-weight: 700;
            font-family: 'Caveat', cursive;
            color: var(--primary);
        }

        .sidebar-nav {
            padding: 1rem 1rem;
            overflow-y: auto;
            flex-grow: 1;
        }

        .nav-section-title {
            padding: 0 1rem;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.15em;
            color: var(--text-muted);
            font-weight: 700;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
        }

        .nav-item {
            display: flex;
            align-items: center;
            padding: 0.875rem 1rem;
            color: var(--text-muted);
            text-decoration: none;
            font-size: 0.95rem;
            font-weight: 600;
            gap: 0.875rem;
            cursor: pointer;
            border-radius: var(--radius-md);
            margin-bottom: 0.25rem;
        }

        .nav-item i {
            font-size: 1.1rem;
            color: var(--text-muted);
            transition: color 0.3s ease;
        }

        .nav-item:hover {
            background-color: var(--sidebar-active);
            color: var(--primary);
        }
        
        .nav-item:hover i {
            color: var(--accent);
        }

        .nav-item.active {
            background-color: var(--primary);
            color: var(--bg-body);
        }
        
        .nav-item.active i {
            color: var(--bg-body);
        }

        /* Main Content */
        .main-content {
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            background-color: var(--bg-body);
        }

        .topbar {
            height: 72px;
            background-color: transparent;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 2.5rem;
            flex-shrink: 0;
        }

        .breadcrumb {
            font-size: 0.95rem;
            color: var(--text-muted);
            font-weight: 500;
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
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            font-size: 1.1rem;
            cursor: pointer;
            padding: 0.6rem;
            border-radius: var(--radius-full);
            box-shadow: var(--shadow-soft);
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .icon-btn:hover {
            color: var(--accent);
            border-color: var(--accent);
            transform: translateY(-2px);
            box-shadow: var(--shadow-hover);
        }

        .content-scroll {
            flex-grow: 1;
            padding: 1rem 2.5rem 3rem;
            overflow-y: auto;
        }

        /* KPIs */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2.5rem;
        }

        .kpi-card {
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 1.75rem;
            display: flex;
            align-items: center;
            gap: 1.25rem;
            box-shadow: var(--shadow-soft);
        }
        .kpi-card:hover {
            box-shadow: var(--shadow-hover);
        }

        .kpi-icon {
            width: 54px;
            height: 54px;
            background-color: var(--bg-body);
            color: var(--accent);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            border-radius: var(--radius-full);
        }

        .kpi-info {
            display: flex;
            flex-direction: column;
        }

        .kpi-label {
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-muted);
            margin-bottom: 0.25rem;
        }

        .kpi-value {
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--primary);
        }

        /* Diary Screen */
        .screen {
            display: none;
            animation: fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        }

        .screen.active {
            display: block;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(15px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .diary-card {
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            overflow: hidden;
            margin-bottom: 2rem;
            box-shadow: var(--shadow-soft);
            max-width: 900px;
            margin-left: auto;
            margin-right: auto;
        }

        .diary-header {
            padding: 2rem 2.5rem 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid var(--bg-body);
        }

        .diary-title {
            font-size: 2.25rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 1rem;
            color: var(--primary);
        }

        .diary-status {
            font-size: 0.9rem;
            color: var(--accent);
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-weight: 600;
            background: rgba(37, 99, 235, 0.1);
            padding: 0.4rem 0.8rem;
            border-radius: var(--radius-full);
        }

        .diary-body {
            padding: 2rem 2.5rem 3rem;
            line-height: 1.8;
            font-size: 1.1rem;
            color: var(--text-main);
        }

        .diary-body ul {
            padding-left: 1.5rem;
            margin-bottom: 1.5rem;
            list-style-type: none;
        }
        .diary-body li {
            margin-bottom: 1rem;
            position: relative;
        }
        .diary-body li::before {
            content: '✿';
            position: absolute;
            left: -1.5rem;
            color: var(--accent);
            font-size: 0.8em;
            top: 0.2rem;
        }
        .diary-body p {
            margin-bottom: 1.5rem;
        }

        /* Welcome Section */
        .welcome-card {
            text-align: center;
            padding: 6rem 2rem;
            border: none;
            background-color: transparent;
            box-shadow: none;
        }
        .welcome-card i {
            font-size: 3.5rem; 
            color: var(--accent); 
            margin-bottom: 1.5rem;
        }
        .welcome-title {
            margin-bottom: 1rem;
            color: var(--primary);
            font-size: 3rem;
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
                <i class="fa-solid fa-house"></i> Home
            </a>
            
            <div class="nav-section-title">My Journal</div>
            <div id="date-tabs-container">
<!-- DIARY_NAV_PLACEHOLDER -->
            </div>
        </nav>
    </div>

    <div class="main-content">
        <header class="topbar">
            <div class="breadcrumb">My Journal / <span id="current-date-display">Home</span></div>
            <div class="topbar-actions">
                <button id="theme-toggle" class="icon-btn" onclick="toggleTheme()" title="Toggle Theme">
                    <i class="fa-solid fa-moon"></i>
                </button>
            </div>
        </header>

        <div class="content-scroll">
            <div class="kpi-grid" id="dashboard-kpis">
                <div class="kpi-card">
                    <div class="kpi-icon"><i class="fa-solid fa-book-open"></i></div>
                    <div class="kpi-info">
                        <div class="kpi-label">Entries Written</div>
                        <div class="kpi-value" id="kpi-total-entries">0</div>
                    </div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-icon"><i class="fa-solid fa-seedling"></i></div>
                    <div class="kpi-info">
                        <div class="kpi-label">Current Streak</div>
                        <div class="kpi-value" id="kpi-streak">0 Days</div>
                    </div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-icon"><i class="fa-regular fa-star"></i></div>
                    <div class="kpi-info">
                        <div class="kpi-label">Stars Reached</div>
                        <div class="kpi-value">136</div>
                    </div>
                </div>
            </div>

            <div id="screens-container">
<!-- DIARY_CONTENT_PLACEHOLDER -->
            </div>
            
            <div class="screen active" id="screen-dashboard">
                <div class="diary-card welcome-card">
                    <i class="fa-solid fa-leaf"></i>
                    <h2 class="welcome-title">Welcome to Your Space</h2>
                    <p style="color: var(--text-muted); font-size: 1.1rem;">Take a deep breath and select an entry to reflect on your journey.</p>
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
                document.getElementById('current-date-display').textContent = 'Home';
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
                localStorage.setItem('theme', 'light');
                icon.className = 'fa-solid fa-moon';
            } else {
                localStorage.setItem('theme', 'dark');
                icon.className = 'fa-solid fa-sun';
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
</html>
"""

nav_placeholder = ""
content_placeholder = ""

for e in entries:
    nav_placeholder += f"""                <a onclick="showScreen('screen-{e['id']}')" class="nav-item nav-date-item" id="nav-screen-{e['id']}">
                    <i class="fa-regular fa-calendar-heart"></i> {e['label']}
                </a>\n"""
    
    content_placeholder += f"""                <!-- {e['label']} -->
                <div class="screen" id="screen-{e['id']}">
                    <div class="diary-card">
                        <div class="diary-header">
                            <div class="diary-title">
                                <i class="fa-solid fa-pen-nib"></i> Dear Diary
                            </div>
                            <div class="diary-status">
                                <i class="fa-solid fa-cloud-arrow-up"></i> Saved
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
                    <i class="fa-regular fa-calendar-heart"></i> ${dateStr}
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
                                <i class="fa-solid fa-pen-nib"></i> Dear Diary
                            </div>
                            <div class="diary-status">
                                <i class="fa-solid fa-cloud-arrow-up"></i> Saved
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
console.log(`Successfully updated index.html with Lifestyle layout entry for ${dateStr}`);
"""

with open('update_diary.js.new', 'w', encoding='utf-8') as f:
    f.write(new_update_diary_js)

print("Migration generated index.html.new and update_diary.js.new successfully.")
