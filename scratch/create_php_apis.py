import os

dirs = [
    'c:/xampp/htdocs/ifood/api',
    'c:/xampp/htdocs/ifood/quiz-clone/api'
]

for d in dirs:
    os.makedirs(os.path.join(d, 'site'), exist_ok=True)
    os.makedirs(os.path.join(d, 'lead'), exist_ok=True)
    os.makedirs(os.path.join(d, 'pix'), exist_ok=True)

    # 1. /api/site/config
    with open(os.path.join(d, 'site/config.php'), 'w', encoding='utf-8') as f:
        f.write('''<?php
header('Content-Type: application/json');
echo json_encode([
    'ok' => true,
    'siteName' => 'iFood Entregador',
    'features' => ['pix' => true, 'coupon' => true]
]);
''')

    # 2. /api/site/session
    with open(os.path.join(d, 'site/session.php'), 'w', encoding='utf-8') as f:
        f.write('''<?php
header('Content-Type: application/json');
$sessionId = 'sess_' . md5(uniqid(microtime(), true));
echo json_encode([
    'ok' => true,
    'sessionId' => $sessionId
]);
''')

    # 3. /api/lead/track.php & pageview.php
    with open(os.path.join(d, 'lead/track.php'), 'w', encoding='utf-8') as f:
        f.write('''<?php
header('Content-Type: application/json');
echo json_encode(['ok' => true]);
''')
    with open(os.path.join(d, 'lead/pageview.php'), 'w', encoding='utf-8') as f:
        f.write('''<?php
header('Content-Type: application/json');
echo json_encode(['ok' => true]);
''')

    # 4. /api/pix/create.php
    with open(os.path.join(d, 'pix/create.php'), 'w', encoding='utf-8') as f:
        f.write('''<?php
header('Content-Type: application/json');
$raw = file_get_contents('php://input');
$data = json_decode($raw, true) ?: [];

$amount = isset($data['amount']) ? floatval($data['amount']) : 29.90;
if ($amount <= 0) $amount = 29.90;

$pixId = 'pix_' . rand(100000, 999999);
$pixCode = '00020101021226880014br.gov.bcb.pix0136' . md5($pixId) . '520400005303986540' . sprintf("%.2f", $amount) . '5802BR5915IFOOD PARCEIRO6009SAO PAULO6304E2CA';
$qrUrl = 'https://quickchart.io/qr?text=' . urlencode($pixCode);

echo json_encode([
    'ok' => true,
    'id' => $pixId,
    'pixId' => $pixId,
    'code' => $pixCode,
    'pixCode' => $pixCode,
    'qrCode' => $qrUrl,
    'qrCodeUrl' => $qrUrl,
    'status' => 'PENDING',
    'amount' => $amount,
    'expiresAt' => date('c', time() + 600)
]);
''')

    # 5. /api/pix/status.php
    with open(os.path.join(d, 'pix/status.php'), 'w', encoding='utf-8') as f:
        f.write('''<?php
header('Content-Type: application/json');
echo json_encode([
    'ok' => true,
    'status' => 'PENDING',
    'paid' => false
]);
''')

print("Created PHP API endpoints for local XAMPP backend!")
