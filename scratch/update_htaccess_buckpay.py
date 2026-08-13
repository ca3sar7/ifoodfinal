import os

htaccess_ifood = """<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteBase /ifood/

    # Direct API rewrites
    RewriteRule ^api/site/config/?$ api/site/config.php [L,QSA]
    RewriteRule ^api/site/session/?$ api/site/session.php [L,QSA]
    RewriteRule ^api/lead/track/?$ api/lead/track.php [L,QSA]
    RewriteRule ^api/lead/pageview/?$ api/lead/pageview.php [L,QSA]
    RewriteRule ^api/pix/create/?$ api/pix/create.php [L,QSA]
    RewriteRule ^api/pix/status/?$ api/pix/status.php [L,QSA]
    RewriteRule ^api/pix/webhook/?$ api/pix/webhook.php [L,QSA]

    # Protect config.php
    <Files "config.php">
        Order allow,deny
        Deny from all
    </Files>

    # Allow direct access to existing files and directories
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteCond %{REQUEST_FILENAME} !-d

    # Map clean URLs to .html files if they exist
    RewriteCond %{REQUEST_FILENAME}.html -f
    RewriteRule ^([^/]+)/?$ $1.html [L]
</IfModule>

# Prevent directory listing
Options -Indexes
"""

htaccess_clone = htaccess_ifood.replace('RewriteBase /ifood/', 'RewriteBase /ifood/quiz-clone/')

with open('c:/xampp/htdocs/ifood/.htaccess', 'w', encoding='utf-8') as f:
    f.write(htaccess_ifood)

with open('c:/xampp/htdocs/ifood/quiz-clone/.htaccess', 'w', encoding='utf-8') as f:
    f.write(htaccess_clone)

# Create data/.htaccess to deny public web access to SQLite/JSON data store
os.makedirs('c:/xampp/htdocs/ifood/data', exist_ok=True)
os.makedirs('c:/xampp/htdocs/ifood/quiz-clone/data', exist_ok=True)

data_htaccess = "Order allow,deny\nDeny from all\n"

with open('c:/xampp/htdocs/ifood/data/.htaccess', 'w', encoding='utf-8') as f:
    f.write(data_htaccess)

with open('c:/xampp/htdocs/ifood/quiz-clone/data/.htaccess', 'w', encoding='utf-8') as f:
    f.write(data_htaccess)

print("Updated .htaccess files with BuckPay routes and security protections!")
