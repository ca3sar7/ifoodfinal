import os
import re

target_files = [
    'c:/xampp/htdocs/ifood/script.js',
    'c:/xampp/htdocs/ifood/js/quiz.js',
    'c:/xampp/htdocs/ifood/quiz-clone/script.js',
    'c:/xampp/htdocs/ifood/quiz-clone/js/quiz.js'
]

old_fn = """function toRootRelativePath(rawUrl = '') {
    const text = String(rawUrl || '').trim();
    if (!text) return '';
    if (/^(?:[a-z][a-z0-9+.-]*:|\/\/)/i.test(text) || text.startsWith('#')) {
        return text;
    }
    if (text.startsWith('?')) {
        return `${window.location.pathname}${text}`;
    }

    let normalized = text.replace(/^\.\/+/, '');
    if (normalized === 'index' || normalized === 'index.html') {
        return '/';
    }
    normalized = normalized.replace(/\.html(?=$|\?)/i, '');
    return normalized.startsWith('/') ? normalized : `/${normalized}`;
}"""

new_fn = """function toRootRelativePath(rawUrl = '') {
    const text = String(rawUrl || '').trim();
    if (!text) return '';
    if (/^(?:[a-z][a-z0-9+.-]*:|\/\/)/i.test(text) || text.startsWith('#')) {
        return text;
    }
    if (text.startsWith('?')) {
        return `${window.location.pathname}${text}`;
    }

    let normalized = text.replace(/^\.\/+/, '').replace(/^\//, '');
    if (normalized === '' || normalized === 'index') return 'index.html';
    
    // Split search/query params if present
    const parts = normalized.split('?');
    let pathPart = parts[0];
    const queryPart = parts.length > 1 ? `?${parts.slice(1).join('?')}` : '';

    if (!pathPart.endsWith('.html')) {
        pathPart = `${pathPart}.html`;
    }
    return `${pathPart}${queryPart}`;
}"""

for tf in target_files:
    if os.path.exists(tf):
        with open(tf, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if old_fn in content:
            updated = content.replace(old_fn, new_fn)
            with open(tf, 'w', encoding='utf-8') as f:
                f.write(updated)
            print(f"Patched relative redirect in {tf}")
        else:
            print(f"old_fn not found in {tf}, replacing using regex...")
            updated = re.sub(r'function toRootRelativePath\(rawUrl = \'\'\) \{.*?\n\}', new_fn, content, flags=re.DOTALL)
            with open(tf, 'w', encoding='utf-8') as f:
                f.write(updated)
            print(f"Regex patched relative redirect in {tf}")

