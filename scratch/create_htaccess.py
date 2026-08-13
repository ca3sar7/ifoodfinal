import os

htaccess_content = """<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteBase /ifood/

    # Allow direct access to existing files and directories
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteCond %{REQUEST_FILENAME} !-d

    # Map clean URLs to .html files if they exist
    RewriteCond %{REQUEST_FILENAME}.html -f
    RewriteRule ^([^/]+)/?$ $1.html [L]
</IfModule>
"""

with open('c:/xampp/htdocs/ifood/.htaccess', 'w', encoding='utf-8') as f:
    f.write(htaccess_content)

with open('c:/xampp/htdocs/ifood/quiz-clone/.htaccess', 'w', encoding='utf-8') as f:
    f.write(htaccess_content.replace('RewriteBase /ifood/', 'RewriteBase /ifood/quiz-clone/'))

print("Created .htaccess files for XAMPP Apache URL rewriting!")
