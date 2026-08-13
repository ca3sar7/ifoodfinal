import os
import re

target_dirs = [
    'c:/xampp/htdocs/ifood',
    'c:/xampp/htdocs/ifood/quiz-clone'
]

# 1. Update config.js
config_js_content = """// js/config.js — Configuração de rota da API e pasta base
if (typeof BASE_FOLDER === 'undefined') {
    var BASE_FOLDER = (function() {
        if (typeof window === 'undefined' || !window.location) return '';
        var p = String(window.location.pathname || '');
        if (p.includes('/ifood/quiz-clone')) return '/ifood/quiz-clone';
        if (p.includes('/ifood/')) return '/ifood';
        if (p.startsWith('/ifood')) return '/ifood';
        return '';
    })();
}

if (typeof API_BASE === 'undefined') {
    var API_BASE = BASE_FOLDER + '/api';
}

if (typeof window !== 'undefined') {
    window.BASE_FOLDER = BASE_FOLDER;
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

print("Updated config.js files with dynamic BASE_FOLDER!")

# 2. Patch backguard.js to prepend BASE_FOLDER to root route targets
for td in target_dirs:
    bg_path = os.path.join(td, 'backguard.js')
    if os.path.exists(bg_path):
        with open(bg_path, 'r', encoding='utf-8') as f:
            bg_content = f.read()

        # Update BASE_FOLDER header in backguard.js
        if 'var BASE_FOLDER' not in bg_content:
            bg_content = config_js_content + "\n" + bg_content

        # Update formatRoute logic in backguard.js
        # Replace window.location.replace(target) with window.location.replace(formatRoute(target))
        patch_helper = """
        var formatRoute = function (targetUrl) {
            if (!targetUrl) return '';
            var str = String(targetUrl).trim();
            if (/^(?:[a-z][a-z0-9+.-]*:|\/\/)/i.test(str) || str.startsWith('#')) return str;
            var clean = str.startsWith('/') ? str : '/' + str;
            return (typeof BASE_FOLDER !== 'undefined' ? BASE_FOLDER : '') + clean;
        };
        """
        if 'var formatRoute' not in bg_content:
            bg_content = bg_content.replace('var normalizePath = function', patch_helper + '\n        var normalizePath = function')

        # Replace window.location.replace(target); with window.location.replace(formatRoute(target));
        bg_content = bg_content.replace('window.location.replace(target);', 'window.location.replace(formatRoute(target));')
        bg_content = bg_content.replace('window.location.href = target;', 'window.location.href = formatRoute(target);')
        
        with open(bg_path, 'w', encoding='utf-8') as f:
            f.write(bg_content)
        print(f"Patched backguard.js in {td}")

# 3. Patch script.js and js/quiz.js for toRootRelativePath
for td in target_dirs:
    for jf in ['script.js', 'js/quiz.js']:
        js_path = os.path.join(td, jf)
        if os.path.exists(js_path):
            with open(js_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'var BASE_FOLDER' not in content:
                content = config_js_content + "\n" + content
            
            # Patch toRootRelativePath
            patch_to_root = """function toRootRelativePath(rawUrl = '') {
    const text = String(rawUrl || '').trim();
    if (!text) return '';
    if (/^(?:[a-z][a-z0-9+.-]*:|\/\/)/i.test(text) || text.startsWith('#')) {
        return text;
    }
    if (text.startsWith('?')) {
        return `${window.location.pathname}${text}`;
    }

    let normalized = text.replace(/^\.\/+/, '').replace(/^\//, '');
    if (normalized === '' || normalized === 'index') return `${BASE_FOLDER}/index.html`;
    
    // Split search/query params if present
    const parts = normalized.split('?');
    let pathPart = parts[0];
    const queryPart = parts.length > 1 ? `?${parts.slice(1).join('?')}` : '';

    if (!pathPart.endsWith('.html')) {
        pathPart = `${pathPart}.html`;
    }
    return `${BASE_FOLDER}/${pathPart}${queryPart}`;
}"""
            pattern = r'function toRootRelativePath\(rawUrl = \'\'\) \{.*?\n\}'
            content = re.sub(pattern, patch_to_root, content, flags=re.DOTALL)

            with open(js_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Patched toRootRelativePath in {js_path}")

