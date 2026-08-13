import os
import re

target_dirs = [
    'c:/xampp/htdocs/ifood',
    'c:/xampp/htdocs/ifood/quiz-clone'
]

# Create.php code with updated field names for frontend compatibility
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

for td in target_dirs:
    create_path = os.path.join(td, 'api/pix/create.php')
    with open(create_path, 'w', encoding='utf-8') as f:
        f.write(create_php_code)
    print(f"Updated {create_path} with paymentCode and paymentCodeBase64 fields!")

