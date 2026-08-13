import os
import shutil

target_dirs = [
    'c:/xampp/htdocs/ifood',
    'c:/xampp/htdocs/ifood/quiz-clone'
]

# Delete any file with # or ? in scratch or downloaded_site
for td in target_dirs:
    scratch_dir = os.path.join(td, 'scratch')
    if os.path.exists(scratch_dir):
        # Find and remove invalid filename files like '#'
        hash_file = os.path.join(scratch_dir, 'downloaded_site', '#')
        if os.path.exists(hash_file):
            try:
                os.remove(hash_file)
                print(f"Removed invalid file {hash_file}")
            except Exception as e:
                print(f"Error removing hash file: {e}")

# Create .netlifyignore in both target directories
netlify_ignore_content = """scratch/
scratch/*
*.py
*.txt
.git/
"""

for td in target_dirs:
    ignore_path = os.path.join(td, '.netlifyignore')
    with open(ignore_path, 'w', encoding='utf-8') as f:
        f.write(netlify_ignore_content)
    print(f"Created .netlifyignore in {td}")

