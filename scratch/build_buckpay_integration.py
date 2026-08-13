import os

target_dirs = [
    'c:/xampp/htdocs/ifood',
    'c:/xampp/htdocs/ifood/quiz-clone'
]

# 1. config.php content
config_code = """<?php
// config.php — Credenciais BuckPay
if (basename($_SERVER['PHP_SELF']) === 'config.php') {
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
"""

# 2. api/pix/db.php content (Data store abstraction)
db_code = """<?php
// Store helper using SQLite PDO with JSON fallback
require_once __DIR__ . '/../../config.php';

function get_pix_db_dir() {
    $dir = __DIR__ . '/../../data';
    if (!file_exists($dir)) {
        @mkdir($dir, 0755, true);
    }
    return $dir;
}

function get_db_connection() {
    static $pdo = null;
    if ($pdo !== null) return $pdo;

    if (extension_loaded('pdo_sqlite')) {
        try {
            $dbPath = get_pix_db_dir() . '/pix.db';
            $pdo = new PDO('sqlite:' . $dbPath);
            $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
            $pdo->exec("CREATE TABLE IF NOT EXISTS pix_transactions (
                external_id TEXT PRIMARY KEY,
                transaction_id TEXT,
                status TEXT,
                amount REAL,
                code TEXT,
                qr_code TEXT,
                created_at TEXT,
                updated_at TEXT
            )");
            return $pdo;
        } catch (Exception $e) {
            error_log("SQLite Connection Error: " . $e->getMessage());
        }
    }
    return null;
}

function save_pix_transaction($externalId, $data) {
    $pdo = get_db_connection();
    $now = date('c');
    
    $transactionId = $data['transaction_id'] ?? $data['id'] ?? '';
    $status = strtoupper($data['status'] ?? 'PENDING');
    $amount = floatval($data['amount'] ?? 0);
    $code = $data['code'] ?? $data['pixCode'] ?? '';
    $qrCode = $data['qrCode'] ?? $data['qrCodeUrl'] ?? '';

    if ($pdo) {
        $stmt = $pdo->prepare("INSERT INTO pix_transactions 
            (external_id, transaction_id, status, amount, code, qr_code, created_at, updated_at) 
            VALUES (:ext_id, :tx_id, :status, :amount, :code, :qr, :created, :updated)
            ON CONFLICT(external_id) DO UPDATE SET 
                transaction_id = COALESCE(NULLIF(EXCLUDED.transaction_id, ''), pix_transactions.transaction_id),
                status = EXCLUDED.status,
                amount = EXCLUDED.amount,
                code = COALESCE(NULLIF(EXCLUDED.code, ''), pix_transactions.code),
                qr_code = COALESCE(NULLIF(EXCLUDED.qr_code, ''), pix_transactions.qr_code),
                updated_at = EXCLUDED.updated_at");
        $stmt->execute([
            ':ext_id' => $externalId,
            ':tx_id' => $transactionId,
            ':status' => $status,
            ':amount' => $amount,
            ':code' => $code,
            ':qr' => $qrCode,
            ':created' => $now,
            ':updated' => $now
        ]);
        return;
    }

    // JSON Fallback with atomic flock
    $jsonPath = get_pix_db_dir() . '/pix-transactions.json';
    $fp = fopen($jsonPath, 'c+');
    if ($fp && flock($fp, LOCK_EX)) {
        $content = stream_get_contents($fp);
        $store = json_decode($content, true) ?: [];
        
        $existing = $store[$externalId] ?? [];
        $store[$externalId] = [
            'external_id' => $externalId,
            'transaction_id' => $transactionId ?: ($existing['transaction_id'] ?? ''),
            'status' => $status,
            'amount' => $amount ?: ($existing['amount'] ?? 0),
            'code' => $code ?: ($existing['code'] ?? ''),
            'qr_code' => $qrCode ?: ($existing['qr_code'] ?? ''),
            'created_at' => $existing['created_at'] ?? $now,
            'updated_at' => $now
        ];
        
        ftruncate($fp, 0);
        rewind($fp);
        fwrite($fp, json_encode($store, JSON_PRETTY_PRINT));
        fflush($fp);
        flock($fp, LOCK_UN);
        fclose($fp);
    }
}

function get_pix_transaction($externalId) {
    if (empty($externalId)) return null;

    $pdo = get_db_connection();
    if ($pdo) {
        $stmt = $pdo->prepare("SELECT * FROM pix_transactions WHERE external_id = :ext_id OR transaction_id = :tx_id LIMIT 1");
        $stmt->execute([':ext_id' => $externalId, ':tx_id' => $externalId]);
        $row = $stmt->fetch(PDO::FETCH_ASSOC);
        return $row ?: null;
    }

    $jsonPath = get_pix_db_dir() . '/pix-transactions.json';
    if (file_exists($jsonPath)) {
        $content = file_get_contents($jsonPath);
        $store = json_decode($content, true) ?: [];
        if (isset($store[$externalId])) {
            return $store[$externalId];
        }
        foreach ($store as $k => $item) {
            if (($item['transaction_id'] ?? '') === $externalId) {
                return $item;
            }
        }
    }
    return null;
}
"""

# 3. api/pix/create.php content
create_code = """<?php
header('Content-Type: application/json');
require_once __DIR__ . '/../../config.php';
require_once __DIR__ . '/db.php';

try {
    $rawInput = file_get_contents('php://input');
    $input = json_decode($rawInput, true) ?: [];

    $sessionId = trim($input['sessionId'] ?? '');
    $amountRaw = floatval($input['amount'] ?? 0);
    $personal = $input['personal'] ?? [];
    
    $name = trim($personal['name'] ?? '');
    $email = trim($personal['email'] ?? '');
    $cpfRaw = trim($personal['cpf'] ?? '');
    $phoneRaw = trim($personal['phone'] ?? '');

    // 1. Validation
    if (empty($sessionId) || empty($amountRaw) || empty($name) || empty($email)) {
        http_response_code(400);
        echo json_encode([
            'ok' => false,
            'error' => 'Preencha todos os campos obrigatorios (nome, e-mail e dados da sessao).'
        ]);
        exit;
    }

    // 2. Amount Validation (in centavos)
    $amountCentavos = (int) round($amountRaw * 100);
    if ($amountCentavos < 600 || $amountCentavos > 300000) {
        http_response_code(400);
        echo json_encode([
            'ok' => false,
            'error' => 'O valor do pagamento deve estar entre R$ 6,00 e R$ 3.000,00.'
        ]);
        exit;
    }

    // 3. Sanitization
    $externalId = preg_replace('/[^a-zA-Z0-9_\-]/', '', $sessionId);
    $cpfDigits = preg_replace('/\D/', '', $cpfRaw);
    $phoneDigits = preg_replace('/\D/', '', $phoneRaw);
    
    // Add country code 55 if missing
    if (strlen($phoneDigits) === 10 || strlen($phoneDigits) === 11) {
        $phoneDigits = '55' . $phoneDigits;
    }

    // Prepare BuckPay Payload
    $postbackUrl = defined('WEBHOOK_PUBLIC_URL') ? WEBHOOK_PUBLIC_URL : '';
    $payload = [
        'external_id' => $externalId,
        'payment_method' => 'pix',
        'amount' => $amountCentavos,
        'buyer' => [
            'name' => $name,
            'email' => $email,
            'document' => $cpfDigits,
            'phone' => $phoneDigits
        ],
        'postbackUrl' => $postbackUrl
    ];

    // Helper for BuckPay cURL
    function call_buckpay($endpoint, $method = 'GET', $data = null) {
        $url = BUCKPAY_BASE_URL . $endpoint;
        $ch = curl_init($url);
        
        $headers = [
            'Authorization: Bearer ' . BUCKPAY_TOKEN,
            'User-Agent: ' . BUCKPAY_USER_AGENT,
            'Content-Type: application/json'
        ];

        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 20);

        if ($method === 'POST') {
            curl_setopt($ch, CURLOPT_POST, true);
            curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
        }

        $resText = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $err = curl_error($ch);
        curl_close($ch);

        if ($err) {
            error_log("BuckPay cURL Error: " . $err);
        }

        $resJson = json_decode($resText, true) ?: [];
        return ['code' => $httpCode, 'data' => $resJson, 'raw' => $resText];
    }

    // Call BuckPay Create Transaction
    $res = call_buckpay('/v1/transactions', 'POST', $payload);

    // Handle Idempotency / Duplicate Transaction Error
    if ($res['code'] === 400 && (strpos($res['raw'], 'transaction_already_exists') !== false)) {
        // Query existing transaction
        $queryRes = call_buckpay('/v1/transactions/external_id/' . $externalId, 'GET');
        if ($queryRes['code'] === 200 && !empty($queryRes['data']['data'])) {
            $tx = $queryRes['data']['data'];
            $stored = get_pix_transaction($externalId);
            
            $code = $stored['code'] ?? $tx['pix']['code'] ?? '';
            $qrCode = $stored['qr_code'] ?? $tx['pix']['qrcode_base64'] ?? '';
            if ($qrCode && strpos($qrCode, 'data:') !== 0 && !stristr($qrCode, 'http')) {
                $qrCode = 'data:image/png;base64,' . $qrCode;
            }

            if (!empty($code)) {
                echo json_encode([
                    'ok' => true,
                    'id' => $tx['id'],
                    'idTransaction' => $tx['id'],
                    'txid' => $tx['id'],
                    'code' => $code,
                    'pixCode' => $code,
                    'qrCode' => $qrCode,
                    'qrCodeUrl' => $qrCode,
                    'status' => strtoupper($tx['status'] ?? 'PENDING'),
                    'amount' => $amountRaw
                ]);
                exit;
            }
        }

        http_response_code(400);
        echo json_encode([
            'ok' => false,
            'error' => 'Transacao ja existente. Tente novamente em instantes.'
        ]);
        exit;
    }

    if ($res['code'] !== 201 || empty($res['data']['data'])) {
        error_log("BuckPay Error Response: " . $res['raw']);
        http_response_code(500);
        echo json_encode([
            'ok' => false,
            'error' => 'Nao foi possivel gerar a cobranca PIX no momento. Tente novamente.'
        ]);
        exit;
    }

    // Success 201
    $txData = $res['data']['data'];
    $txId = $txData['id'] ?? '';
    $pixCode = $txData['pix']['code'] ?? '';
    $qrBase64 = $txData['pix']['qrcode_base64'] ?? '';
    
    $qrCodeUrl = $qrBase64;
    if ($qrBase64 && strpos($qrBase64, 'data:') !== 0 && !stristr($qrBase64, 'http')) {
        $qrCodeUrl = 'data:image/png;base64,' . $qrBase64;
    }

    $saveData = [
        'transaction_id' => $txId,
        'status' => 'PENDING',
        'amount' => $amountRaw,
        'code' => $pixCode,
        'qrCode' => $qrCodeUrl
    ];
    save_pix_transaction($externalId, $saveData);

    echo json_encode([
        'ok' => true,
        'id' => $txId,
        'idTransaction' => $txId,
        'txid' => $txId,
        'code' => $pixCode,
        'pixCode' => $pixCode,
        'qrCode' => $qrCodeUrl,
        'qrCodeUrl' => $qrCodeUrl,
        'status' => 'PENDING',
        'amount' => $amountRaw
    ]);

} catch (Exception $e) {
    error_log("BuckPay Create Exception: " . $e->getMessage());
    http_response_code(500);
    echo json_encode([
        'ok' => false,
        'error' => 'Ocorreu um erro interno ao processar a solicitacao.'
    ]);
}
"""

# 4. api/pix/webhook.php content
webhook_code = """<?php
header('Content-Type: application/json');
require_once __DIR__ . '/../../config.php';
require_once __DIR__ . '/db.php';

try {
    $rawInput = file_get_contents('php://input');
    $data = json_decode($rawInput, true) ?: [];

    error_log("BuckPay Webhook Payload: " . $rawInput);

    $externalId = trim($data['external_id'] ?? $data['data']['external_id'] ?? '');
    $txId = trim($data['id'] ?? $data['data']['id'] ?? '');
    $rawStatus = strtolower(trim($data['status'] ?? $data['data']['status'] ?? ''));

    if (empty($externalId) && empty($txId)) {
        http_response_code(400);
        echo json_encode(['ok' => false, 'error' => 'Invalid webhook payload']);
        exit;
    }

    $lookupKey = $externalId ?: $txId;
    $targetStatus = 'PENDING';
    if (in_array($rawStatus, ['paid', 'approved', 'completed', 'success'])) {
        $targetStatus = 'PAID';
    } elseif (in_array($rawStatus, ['canceled', 'cancelled', 'expired', 'failed', 'refunded'])) {
        $targetStatus = 'EXPIRED';
    }

    // Save/Update status
    save_pix_transaction($lookupKey, [
        'transaction_id' => $txId,
        'status' => $targetStatus
    ]);

    http_response_code(200);
    echo json_encode(['ok' => true, 'status' => $targetStatus]);

} catch (Exception $e) {
    error_log("BuckPay Webhook Exception: " . $e->getMessage());
    http_response_code(500);
    echo json_encode(['ok' => false, 'error' => $e->getMessage()]);
}
"""

# 5. api/pix/status.php content
status_code = """<?php
header('Content-Type: application/json');
require_once __DIR__ . '/../../config.php';
require_once __DIR__ . '/db.php';

try {
    $rawInput = file_get_contents('php://input');
    $input = json_decode($rawInput, true) ?: [];

    $sessionId = trim($input['sessionId'] ?? $input['external_id'] ?? $input['txid'] ?? $_GET['sessionId'] ?? $_GET['external_id'] ?? $_GET['txid'] ?? '');
    
    if (empty($sessionId)) {
        echo json_encode(['ok' => true, 'status' => 'PENDING', 'paid' => false]);
        exit;
    }

    $sanitizedId = preg_replace('/[^a-zA-Z0-9_\-]/', '', $sessionId);
    $tx = get_pix_transaction($sanitizedId);

    if ($tx && strtoupper($tx['status'] ?? '') === 'PAID') {
        echo json_encode([
            'ok' => true,
            'status' => 'PAID',
            'paid' => true,
            'amount' => floatval($tx['amount'] ?? 0)
        ]);
        exit;
    }

    // Optional query to BuckPay API as fallback check
    $ch = curl_init(BUCKPAY_BASE_URL . '/v1/transactions/external_id/' . urlencode($sanitizedId));
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Authorization: Bearer ' . BUCKPAY_TOKEN,
        'User-Agent: ' . BUCKPAY_USER_AGENT,
        'Content-Type: application/json'
    ]);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 5);

    $resText = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    if ($httpCode === 200 && !empty($resText)) {
        $resJson = json_decode($resText, true) ?: [];
        $apiStatus = strtolower($resJson['data']['status'] ?? '');
        if (in_array($apiStatus, ['paid', 'approved', 'completed'])) {
            save_pix_transaction($sanitizedId, ['status' => 'PAID']);
            echo json_encode([
                'ok' => true,
                'status' => 'PAID',
                'paid' => true
            ]);
            exit;
        }
    }

    $currentStatus = strtoupper($tx['status'] ?? 'PENDING');
    echo json_encode([
        'ok' => true,
        'status' => $currentStatus,
        'paid' => ($currentStatus === 'PAID')
    ]);

} catch (Exception $e) {
    error_log("Pix Status Exception: " . $e->getMessage());
    echo json_encode(['ok' => true, 'status' => 'PENDING', 'paid' => false]);
}
"""

for td in target_dirs:
    # Save config.php at root
    with open(os.path.join(td, 'config.php'), 'w', encoding='utf-8') as f:
        f.write(config_code)
    
    # Ensure api/pix directory exists
    pix_dir = os.path.join(td, 'api/pix')
    os.makedirs(pix_dir, exist_ok=True)
    
    # Save db.php
    with open(os.path.join(pix_dir, 'db.php'), 'w', encoding='utf-8') as f:
        f.write(db_code)
        
    # Save create.php
    with open(os.path.join(pix_dir, 'create.php'), 'w', encoding='utf-8') as f:
        f.write(create_code)

    # Save webhook.php
    with open(os.path.join(pix_dir, 'webhook.php'), 'w', encoding='utf-8') as f:
        f.write(webhook_code)

    # Save status.php
    with open(os.path.join(pix_dir, 'status.php'), 'w', encoding='utf-8') as f:
        f.write(status_code)

print("--- BUCKPAY INTEGRATION BACKEND FILES CREATED ---")
