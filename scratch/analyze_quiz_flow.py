import sys
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/downloaded_site/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Extract questions object
q_match = re.search(r'const questions = (\{.*?\n\};)', js, re.DOTALL)
if q_match:
    print("QUESTIONS OBJECT DETECTED:")
    print(q_match.group(1))

# Extract processing steps or other quiz steps
processing_match = re.search(r'function initProcessing\(\)\s*\{([^}]+)\}', js)
if processing_match:
    print("\nPROCESSING FUNCTION:")
    print(processing_match.group(1))

