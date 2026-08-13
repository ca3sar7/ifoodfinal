import os
import re

target_dirs = [
    'c:/xampp/htdocs/ifood',
    'c:/xampp/htdocs/ifood/quiz-clone'
]

# 1. Create js/config.js
config_js_content = """// js/config.js — Base URL da API do projeto
if (typeof API_BASE === 'undefined') {
    var API_BASE = (function() {
        if (typeof window !== 'undefined' && window.API_BASE) return window.API_BASE;
        const path = (typeof window !== 'undefined' && window.location) ? window.location.pathname : '';
        if (path.includes('/ifood/quiz-clone')) return '/ifood/quiz-clone/api';
        if (path.includes('/ifood')) return '/ifood/api';
        return '/ifood/api';
    })();
}
if (typeof window !== 'undefined') {
    window.API_BASE = API_BASE;
}
"""

for td in target_dirs:
    js_dir = os.path.join(td, 'js')
    os.makedirs(js_dir, exist_ok=True)
    with open(os.path.join(js_dir, 'config.js'), 'w', encoding='utf-8') as f:
        f.write(config_js_content)
    with open(os.path.join(td, 'config.js'), 'w', encoding='utf-8') as f:
        f.write(config_js_content)

print("Created config.js in target directories!")

# 2. Add <script src="js/config.js"></script> to all HTML files before script.js
for td in target_dirs:
    html_files = [f for f in os.listdir(td) if f.endswith('.html')]
    for hf in html_files:
        path = os.path.join(td, hf)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'config.js' not in content:
            # Insert config.js before script.js or in head
            if '<script src="script.js' in content:
                content = content.replace('<script src="script.js', '<script src="js/config.js"></script>\n    <script src="script.js')
            elif '</head>' in content:
                content = content.replace('</head>', '    <script src="js/config.js"></script>\n</head>')
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Added config.js script tag to {path}")

# 3. Replace all fetch('/api/...') in JS files with `${API_BASE}/...`
for td in target_dirs:
    js_files = ['script.js', 'js/quiz.js', 'backguard.js']
    for jf in js_files:
        path = os.path.join(td, jf)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Prepend var API_BASE fallback to top of JS file if missing
            if 'var API_BASE' not in content and 'const API_BASE' not in content:
                content = config_js_content + "\n" + content
            
            # Replace '/api/ with `${API_BASE}/
            # Replace "/api/ with `${API_BASE}/
            # Replace `fetch('/api/ with `fetch(`${API_BASE}/
            # Replace `fetch("/api/ with `fetch(`${API_BASE}/
            
            # Matches fetch('/api/...', or fetch("/api/...", or url '/api/...'
            content = re.sub(r"fetch\(['\"]/api/([^'\"]+)['\"]", r"fetch(`${API_BASE}/\1`", content)
            content = re.sub(r"['\"]/api/([^'\"]+)['\"]", r"`${API_BASE}/\1`", content)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated API_BASE references in {path}")

