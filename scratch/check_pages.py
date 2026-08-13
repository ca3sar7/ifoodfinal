import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/downloaded_site/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Search for html files referenced or page names
html_files = re.findall(r'[\'"]([a-zA-Z0-9_\-]+\.html)[\'"]', js)
print("HTML files referenced in script.js:", set(html_files))

# Search for window.location.href or redirect targets
redirects = re.findall(r'redirect\([\'"]([^\'"]+)[\'"]\)', js)
print("Redirect targets in script.js:", set(redirects))

# Search for data-page or page names in script.js
pages = re.findall(r'data-page=[\'"]?([a-zA-Z0-9_\-]+)[\'"]?', js)
print("Data pages found:", set(pages))

# Search for init functions and what page they handle
inits = re.findall(r'function (init[a-zA-Z0-9_]+)', js)
print("Init functions found:", set(inits))

