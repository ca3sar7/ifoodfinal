import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/downloaded_site/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Find all object keys in questions
print("--- QUESTIONS KEYS AND STRUCTURE ---")
questions_block = re.search(r'const questions = (\{.*?\n\};)', js, re.DOTALL)
if questions_block:
    q_text = questions_block.group(1)
    print("Found questions block! Length:", len(q_text))
    with open('scratch/questions_block.js', 'w', encoding='utf-8') as f:
        f.write(q_text)
    print("Saved questions_block.js")

# Look for DOM elements, render functions, screens, step containers
screens = re.findall(r'<section[^\>]*>.*?</section>', js, re.DOTALL)
print("Sections in script.js:", len(screens))

# Look for HTML strings inside JS
html_strings = re.findall(r'`([^`]*<div[^`]*)`', js, re.DOTALL)
print("HTML template strings count:", len(html_strings))

# Look for video tags, iframe tags, video players, vsl, etc.
video_tags = re.findall(r'<video[^>]*>.*?</video>', js, re.DOTALL | re.IGNORECASE)
print("Video tags count in script.js:", len(video_tags))
if video_tags:
    for vt in video_tags:
        print("VIDEO TAG:", vt[:300])

iframes = re.findall(r'<iframe[^>]*>', js, re.IGNORECASE)
print("Iframes in script.js:", iframes)

# Check all functions in JS
funcs = re.findall(r'function ([a-zA-Z0-9_$]+)\s*\(', js)
print("\nFunctions defined in script.js:", set(funcs))

