<?php
header('Content-Type: application/json');
echo json_encode([
    'ok' => true,
    'siteName' => 'iFood Entregador',
    'features' => ['pix' => true, 'coupon' => true]
]);
