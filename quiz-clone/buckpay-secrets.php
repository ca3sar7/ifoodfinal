<?php
// buckpay-secrets.php — Credenciais BuckPay
if (basename($_SERVER['PHP_SELF']) === 'buckpay-secrets.php') {
    http_response_code(403);
    exit('Acesso proibido');
}

define('BUCKPAY_TOKEN', 'sk_live_e77fe478f994c90fb5951f6c396adfb6');
define('BUCKPAY_USER_AGENT', 'Buckpay API');
define('BUCKPAY_BASE_URL', 'https://api.realtechdev.com.br');

// URL base do webhook
$scheme = (isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on') ? 'https' : 'http';
$host = $_SERVER['HTTP_HOST'] ?? 'localhost';
define('WEBHOOK_PUBLIC_URL', $scheme . '://' . $host . '/api/pix/webhook');
