<?php
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
