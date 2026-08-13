import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/xampp/htdocs/ifood/api/pix/status.php', 'r', encoding='utf-8') as f:
    php = f.read()

print("--- api/pix/status.php ---")
print(php)

