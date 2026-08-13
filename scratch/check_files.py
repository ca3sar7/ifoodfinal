import os
import re
import shutil

src_dir = 'scratch/downloaded_site'
dst_dir = 'c:/xampp/htdocs/ifood'
dst_clone_dir = 'c:/xampp/htdocs/ifood/quiz-clone'

os.makedirs(dst_dir, exist_ok=True)
os.makedirs(dst_clone_dir, exist_ok=True)

# List all files downloaded
print("Source files:")
for root, dirs, files in os.walk(src_dir):
    rel = os.path.relpath(root, src_dir)
    print(f"  [{rel}]", files)

