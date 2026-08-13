import os
import re
import shutil

src_dir = 'scratch/downloaded_site'
target_dirs = [
    'c:/xampp/htdocs/ifood',
    'c:/xampp/htdocs/ifood/quiz-clone'
]

# Ensure target directories exist
for td in target_dirs:
    os.makedirs(td, exist_ok=True)
    os.makedirs(os.path.join(td, 'assets'), exist_ok=True)
    os.makedirs(os.path.join(td, 'images'), exist_ok=True)
    os.makedirs(os.path.join(td, 'css'), exist_ok=True)
    os.makedirs(os.path.join(td, 'js'), exist_ok=True)

# 1. Process and copy HTML files
html_files = [f for f in os.listdir(src_dir) if f.endswith('.html')]

for hf in html_files:
    with open(os.path.join(src_dir, hf), 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace root slashes for scripts and assets so local relative serving works
    fixed_content = content.replace('src="/backguard.js', 'src="backguard.js')
    fixed_content = fixed_content.replace('src="/assets/', 'src="assets/')
    fixed_content = fixed_content.replace('href="/assets/', 'href="assets/')
    
    for td in target_dirs:
        out_path = os.path.join(td, hf)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print(f"Saved {hf} -> {out_path}")

# 2. Process and copy style.css
with open(os.path.join(src_dir, 'style.css'), 'r', encoding='utf-8') as f:
    css_content = f.read()

fixed_css = css_content.replace('url(/assets/', 'url(../assets/').replace('url("/assets/', 'url("../assets/').replace("url('/assets/", "url('../assets/")

for td in target_dirs:
    # Save style.css at root of target and inside /css/style.css
    with open(os.path.join(td, 'style.css'), 'w', encoding='utf-8') as f:
        f.write(css_content)
    with open(os.path.join(td, 'css/style.css'), 'w', encoding='utf-8') as f:
        f.write(css_content)

# 3. Process and copy script.js and backguard.js
with open(os.path.join(src_dir, 'script.js'), 'r', encoding='utf-8') as f:
    js_content = f.read()

with open(os.path.join(src_dir, 'backguard.js'), 'r', encoding='utf-8') as f:
    bg_content = f.read()

for td in target_dirs:
    with open(os.path.join(td, 'script.js'), 'w', encoding='utf-8') as f:
        f.write(js_content)
    with open(os.path.join(td, 'js/quiz.js'), 'w', encoding='utf-8') as f:
        f.write(js_content)
    with open(os.path.join(td, 'backguard.js'), 'w', encoding='utf-8') as f:
        f.write(bg_content)

# 4. Copy all assets
assets_src = os.path.join(src_dir, 'assets')
images_src = os.path.join(src_dir, 'images')

for td in target_dirs:
    for item in os.listdir(assets_src):
        s = os.path.join(assets_src, item)
        d = os.path.join(td, 'assets', item)
        if os.path.isfile(s):
            shutil.copy2(s, d)
    
    for item in os.listdir(images_src):
        s = os.path.join(images_src, item)
        d = os.path.join(td, 'images', item)
        if os.path.isfile(s):
            shutil.copy2(s, d)

print("\n--- CLONE COPY COMPLETE ---")
