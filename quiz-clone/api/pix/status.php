<?php
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
