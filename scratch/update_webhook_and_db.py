import os

target_dirs = [
    'c:/xampp/htdocs/ifood',
    'c:/xampp/htdocs/ifood/quiz-clone'
]

# 1. New db.php content with update_pix_status_by_txid
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
                amount = CASE WHEN EXCLUDED.amount > 0 THEN EXCLUDED.amount ELSE pix_transactions.amount END,
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

function update_pix_status_by_txid($transactionId, $status) {
    if (empty($transactionId)) return false;
    $now = date('c');
    $status = strtoupper($status);
    $pdo = get_db_connection();

    if ($pdo) {
        $stmt = $pdo->prepare("UPDATE pix_transactions 
            SET status = :status, updated_at = :updated 
            WHERE transaction_id = :tx_id OR external_id = :ext_id");
        $stmt->execute([
            ':status' => $status,
            ':updated' => $now,
            ':tx_id' => $transactionId,
            ':ext_id' => $transactionId
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
            if (($item['transaction_id'] ?? '') === $transactionId || $extId === $transactionId) {
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
        $stmt = $pdo->prepare("SELECT * FROM pix_transactions WHERE external_id = :key OR transaction_id = :key LIMIT 1");
        $stmt->execute([':key' => $key]);
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
        foreach ($store as $k => $item) {
            if (($item['transaction_id'] ?? '') === $key) {
                return $item;
            }
        }
    }
    return null;
}
"""

# 2. Updated api/pix/webhook.php content
webhook_code = """<?php
header('Content-Type: application/json');
require_once __DIR__ . '/../../config.php';
require_once __DIR__ . '/db.php';

try {
    $rawInput = file_get_contents('php://input');
    $payload = json_decode($rawInput, true) ?: [];

    $event = trim($payload['event'] ?? '');
    $data = $payload['data'] ?? [];
    $transactionId = trim($data['id'] ?? '');

    // Debug logging (never expose publicly)
    error_log("BuckPay Webhook Event: [{$event}] - TxID: [{$transactionId}] - Payload: " . $rawInput);

    // Only process transaction.processed event for payment confirmation
    if ($event !== 'transaction.processed') {
        http_response_code(200);
        echo json_encode([
            'ok' => true,
            'message' => 'Event received and ignored',
            'event' => $event
        ]);
        exit;
    }

    if (empty($transactionId)) {
        http_response_code(200);
        echo json_encode([
            'ok' => true,
            'message' => 'Missing transaction id in payload'
        ]);
        exit;
    }

    // Update status to PAID for transaction.processed
    update_pix_status_by_txid($transactionId, 'PAID');

    http_response_code(200);
    echo json_encode([
        'ok' => true,
        'status' => 'PAID',
        'transaction_id' => $transactionId
    ]);

} catch (Exception $e) {
    error_log("BuckPay Webhook Exception: " . $e->getMessage());
    http_response_code(200);
    echo json_encode(['ok' => true, 'error' => $e->getMessage()]);
}
"""

for td in target_dirs:
    pix_dir = os.path.join(td, 'api/pix')
    os.makedirs(pix_dir, exist_ok=True)
    
    with open(os.path.join(pix_dir, 'db.php'), 'w', encoding='utf-8') as f:
        f.write(db_code)
        
    with open(os.path.join(pix_dir, 'webhook.php'), 'w', encoding='utf-8') as f:
        f.write(webhook_code)

print("Updated db.php and webhook.php with BuckPay event specifications!")
