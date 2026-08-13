import os
import re

target_dirs = [
    'c:/xampp/htdocs/ifood',
    'c:/xampp/htdocs/ifood/quiz-clone'
]

# 1. Rename config.php -> buckpay-secrets.php
for td in target_dirs:
    old_config = os.path.join(td, 'config.php')
    new_config = os.path.join(td, 'buckpay-secrets.php')
    
    if os.path.exists(old_config):
        if os.path.exists(new_config):
            os.remove(new_config)
        os.rename(old_config, new_config)
        print(f"Renamed {old_config} -> {new_config}")

# 2. Update require_once references in PHP files
for td in target_dirs:
    for root, dirs, files in os.walk(td):
        for f in files:
            if f.endswith('.php'):
                fp = os.path.join(root, f)
                with open(fp, 'r', encoding='utf-8', errors='ignore') as pfile:
                    content = pfile.read()
                
                # Replace require_once for root config.php to buckpay-secrets.php
                if 'config.php' in content and 'api/site/config.php' not in content:
                    updated = content.replace("config.php", "buckpay-secrets.php")
                    with open(fp, 'w', encoding='utf-8') as pfile:
                        pfile.write(updated)
                    print(f"Updated PHP require in {fp}")

# 3. Update .htaccess files
for td in target_dirs:
    ht_path = os.path.join(td, '.htaccess')
    if os.path.exists(ht_path):
        with open(ht_path, 'r', encoding='utf-8') as hfile:
            ht_content = hfile.read()
        
        # Replace <Files "config.php"> with <Files "buckpay-secrets.php">
        if 'Files "config.php"' in ht_content:
            ht_content = ht_content.replace('Files "config.php"', 'Files "buckpay-secrets.php"')
            with open(ht_path, 'w', encoding='utf-8') as hfile:
                hfile.write(ht_content)
            print(f"Updated .htaccess rule in {ht_path}")

