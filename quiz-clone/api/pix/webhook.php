<?php
header('Content-Type: application/json');
require_once __DIR__ . '/../../buckpay-secrets.php';
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
