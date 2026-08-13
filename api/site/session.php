<?php
header('Content-Type: application/json');
$sessionId = 'sess_' . md5(uniqid(microtime(), true));
echo json_encode([
    'ok' => true,
    'sessionId' => $sessionId
]);
