import os

target_dirs = [
    'c:/xampp/htdocs/ifood',
    'c:/xampp/htdocs/ifood/quiz-clone'
]

vercel_json_content = """{
  "version": 2,
  "functions": {
    "api/**/*.php": {
      "runtime": "vercel-php@0.7.0"
    }
  },
  "routes": [
    { "src": "/api/site/config", "dest": "/api/site/config.php" },
    { "src": "/api/site/session", "dest": "/api/site/session.php" },
    { "src": "/api/lead/track", "dest": "/api/lead/track.php" },
    { "src": "/api/lead/pageview", "dest": "/api/lead/pageview.php" },
    { "src": "/api/pix/create", "dest": "/api/pix/create.php" },
    { "src": "/api/pix/status", "dest": "/api/pix/status.php" },
    { "src": "/api/pix/webhook", "dest": "/api/pix/webhook.php" },
    { "src": "/quiz", "dest": "/quiz.html" },
    { "src": "/dados", "dest": "/dados.html" },
    { "src": "/endereco", "dest": "/endereco.html" },
    { "src": "/processando", "dest": "/processando.html" },
    { "src": "/sucesso", "dest": "/sucesso.html" },
    { "src": "/checkout", "dest": "/checkout.html" },
    { "src": "/orderbump", "dest": "/orderbump.html" },
    { "src": "/pix-loading", "dest": "/pix-loading.html" },
    { "src": "/pix", "dest": "/pix.html" },
    { "src": "/upsell", "dest": "/upsell.html" },
    { "src": "/upsell-correios", "dest": "/upsell-correios.html" },
    { "src": "/upsell-iof", "dest": "/upsell-iof.html" }
  ]
}
"""

for td in target_dirs:
    v_path = os.path.join(td, 'vercel.json')
    with open(v_path, 'w', encoding='utf-8') as f:
        f.write(vercel_json_content)
    print(f"Created vercel.json in {td}")

