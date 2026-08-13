import os

target_dirs = [
    'c:/xampp/htdocs/ifood',
    'c:/xampp/htdocs/ifood/quiz-clone'
]

# 1. Updated create.php
create_php_code = """<?php
header('Content-Type: application/json');
require_once __DIR__ . '/../../buckpay-secrets.php';
require_once __DIR__ . '/db.php';

try {
    $rawInput = file_get_contents('php://input');
    $input = json_decode($rawInput, true) ?: [];

    $sessionId = trim($input['sessionId'] ?? '');
    $amountRaw = floatval($input['amount'] ?? 0);
    $personal = $input['personal'] ?? [];
    $rewardObj = $input['reward'] ?? [];
    $rewardId = trim($rewardObj['id'] ?? 'bag');
    
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

    // 3. Sanitization & Unique external_id per session + reward + amount
    $sanitizedSessionId = preg_replace('/[^a-zA-Z0-9_\-]/', '', $sessionId);
    $sanitizedRewardId = preg_replace('/[^a-zA-Z0-9_\-]/', '', $rewardId);
    $externalId = $sanitizedSessionId . '_' . $sanitizedRewardId . '_' . $amountCentavos;
    
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
            
            $pixCode = $stored['code'] ?? $tx['pix']['code'] ?? '';
            $rawBase64 = $stored['qr_base64'] ?? $tx['pix']['qrcode_base64'] ?? '';
            
            // Clean pure base64 (remove data:image/png;base64, if stored previously)
            $pureBase64 = preg_replace('/^data:image\/[a-z]+;base64,/', '', $rawBase64);
            $qrCodeUrl = $pureBase64 ? 'data:image/png;base64,' . $pureBase64 : null;

            if (!empty($pixCode)) {
                echo json_encode([
                    'ok' => true,
                    'id' => $tx['id'],
                    'idTransaction' => $tx['id'],
                    'txid' => $tx['id'],
                    'code' => $pixCode,
                    'pixCode' => $pixCode,
                    'paymentCode' => $pixCode,
                    'paymentCodeBase64' => $pureBase64,
                    'paymentQrUrl' => null,
                    'qrCode' => $qrCodeUrl,
                    'qrCodeUrl' => $qrCodeUrl,
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
    
    // Clean pure base64
    $pureBase64 = preg_replace('/^data:image\/[a-z]+;base64,/', '', $qrBase64);
    $qrCodeUrl = $pureBase64 ? 'data:image/png;base64,' . $pureBase64 : null;

    $saveData = [
        'transaction_id' => $txId,
        'status' => 'PENDING',
        'amount' => $amountRaw,
        'code' => $pixCode,
        'qr_base64' => $pureBase64,
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
        'paymentCode' => $pixCode,
        'paymentCodeBase64' => $pureBase64,
        'paymentQrUrl' => null,
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

# 2. Updated db.php
db_code = """<?php
// Store helper using SQLite PDO with JSON fallback
require_once __DIR__ . '/../../buckpay-secrets.php';

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
                qr_base64 TEXT,
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
    $code = $data['code'] ?? $data['pixCode'] ?? $data['paymentCode'] ?? '';
    $qrCode = $data['qrCode'] ?? $data['qrCodeUrl'] ?? '';
    $qrBase64 = $data['qr_base64'] ?? $data['paymentCodeBase64'] ?? '';

    if ($pdo) {
        $stmt = $pdo->prepare("INSERT INTO pix_transactions 
            (external_id, transaction_id, status, amount, code, qr_code, qr_base64, created_at, updated_at) 
            VALUES (:ext_id, :tx_id, :status, :amount, :code, :qr, :qr_b64, :created, :updated)
            ON CONFLICT(external_id) DO UPDATE SET 
                transaction_id = COALESCE(NULLIF(EXCLUDED.transaction_id, ''), pix_transactions.transaction_id),
                status = EXCLUDED.status,
                amount = CASE WHEN EXCLUDED.amount > 0 THEN EXCLUDED.amount ELSE pix_transactions.amount END,
                code = COALESCE(NULLIF(EXCLUDED.code, ''), pix_transactions.code),
                qr_code = COALESCE(NULLIF(EXCLUDED.qr_code, ''), pix_transactions.qr_code),
                qr_base64 = COALESCE(NULLIF(EXCLUDED.qr_base64, ''), pix_transactions.qr_base64),
                updated_at = EXCLUDED.updated_at");
        $stmt->execute([
            ':ext_id' => $externalId,
            ':tx_id' => $transactionId,
            ':status' => $status,
            ':amount' => $amount,
            ':code' => $code,
            ':qr' => $qrCode,
            ':qr_b64' => $qrBase64,
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
            'qr_base64' => $qrBase64 ?: ($existing['qr_base64'] ?? ''),
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

function update_pix_status_by_txid($transactionId, $status) {
    if (empty($transactionId)) return false;
    $now = date('c');
    $status = strtoupper($status);
    $pdo = get_db_connection();

    if ($pdo) {
        $stmt = $pdo->prepare("UPDATE pix_transactions 
            SET status = :status, updated_at = :updated 
            WHERE transaction_id = :tx_id OR external_id = :ext_id OR external_id LIKE :prefix");
        $stmt->execute([
            ':status' => $status,
            ':updated' => $now,
            ':tx_id' => $transactionId,
            ':ext_id' => $transactionId,
            ':prefix' => $transactionId . '%'
        ]);
        return $stmt->rowCount() > 0;
    }

    $jsonPath = get_pix_db_dir() . '/pix-transactions.json';
    $fp = fopen($jsonPath, 'c+');
    $updatedCount = 0;
    if ($fp && flock($fp, LOCK_EX)) {
        $content = stream_get_contents($fp);
        $store = json_decode($content, true) ?: [];
        foreach ($store as $extId => &$item) {
            if (($item['transaction_id'] ?? '') === $transactionId || $extId === $transactionId || strpos($extId, $transactionId) === 0) {
                $item['status'] = $status;
                $item['updated_at'] = $now;
                $updatedCount++;
            }
        }
        if ($updatedCount > 0) {
            ftruncate($fp, 0);
            rewind($fp);
            fwrite($fp, json_encode($store, JSON_PRETTY_PRINT));
            fflush($fp);
        }
        flock($fp, LOCK_UN);
        fclose($fp);
    }
    return $updatedCount > 0;
}

function get_pix_transaction($key) {
    if (empty($key)) return null;

    $pdo = get_db_connection();
    if ($pdo) {
        $stmt = $pdo->prepare("SELECT * FROM pix_transactions 
            WHERE external_id = :key OR transaction_id = :key OR external_id LIKE :prefix 
            ORDER BY updated_at DESC LIMIT 1");
        $stmt->execute([':key' => $key, ':prefix' => $key . '%']);
        $row = $stmt->fetch(PDO::FETCH_ASSOC);
        return $row ?: null;
    }

    $jsonPath = get_pix_db_dir() . '/pix-transactions.json';
    if (file_exists($jsonPath)) {
        $content = file_get_contents($jsonPath);
        $store = json_decode($content, true) ?: [];
        if (isset($store[$key])) {
            return $store[$key];
        }
        $matches = [];
        foreach ($store as $k => $item) {
            if (($item['transaction_id'] ?? '') === $key || strpos($k, $key) === 0) {
                $matches[] = $item;
            }
        }
        if (!empty($matches)) {
            usort($matches, function($a, $b) {
                return strtotime($b['updated_at'] ?? 0) - strtotime($a['updated_at'] ?? 0);
            });
            return $matches[0];
        }
    }
    return null;
}
"""

# 3. Updated status.php
status_php_code = """<?php
header('Content-Type: application/json');
require_once __DIR__ . '/../../buckpay-secrets.php';
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
    $queryKey = !empty($tx['external_id']) ? $tx['external_id'] : $sanitizedId;
    $ch = curl_init(BUCKPAY_BASE_URL . '/v1/transactions/external_id/' . urlencode($queryKey));
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
            save_pix_transaction($queryKey, ['status' => 'PAID']);
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
    pix_dir = os.path.join(td, 'api/pix')
    os.makedirs(pix_dir, exist_ok=True)
    
    with open(os.path.join(pix_dir, 'create.php'), 'w', encoding='utf-8') as f:
        f.write(create_php_code)

    with open(os.path.join(pix_dir, 'db.php'), 'w', encoding='utf-8') as f:
        f.write(db_code)

    with open(os.path.join(pix_dir, 'status.php'), 'w', encoding='utf-8') as f:
        f.write(status_php_code)

print("--- UNIQUE EXTERNAL_ID FIX APPLIED TO CREATE, DB, AND STATUS ---")
