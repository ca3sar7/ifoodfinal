import subprocess
import os

php_files = [
    'c:/xampp/htdocs/ifood/config.php',
    'c:/xampp/htdocs/ifood/api/pix/db.php',
    'c:/xampp/htdocs/ifood/api/pix/create.php',
    'c:/xampp/htdocs/ifood/api/pix/status.php',
    'c:/xampp/htdocs/ifood/api/pix/webhook.php'
]

for pf in php_files:
    if os.path.exists(pf):
        res = subprocess.run(['php', '-l', pf], capture_output=True, text=True)
        print(f"Lint {os.path.basename(pf)}: {res.stdout.strip()}")

