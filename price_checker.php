<?php
// Crypto Nexus Ultra - Price Checker API
// Intentionally vulnerable to SSRF

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *'); // CORS inseguro
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: *');

// Vulnerabilidad 1: SSRF directo
if(isset($_GET['api_url'])) {
    $url = $_GET['api_url'];
    
    // ¡NO HAY VALIDACIÓN!
    $data = @file_get_contents($url);
    
    if($data === FALSE) {
        echo json_encode([
            'status' => 'error',
            'message' => 'Failed to fetch data',
            'error' => error_get_last()['message'] ?? 'Unknown error'
        ]);
    } else {
        // ¡PELIGROSO! Devuelve cualquier contenido
        echo $data;
    }
    exit;
}

// Vulnerabilidad 2: SSRF a través de parámetros
if(isset($_GET['symbol'])) {
    $symbol = $_GET['symbol'];
    
    // Construye URL dinámicamente sin sanitización
    $api_url = "http://api.coingecko.com/api/v3/simple/price?ids=$symbol&vs_currencies=usd";
    
    // Permite override del host (¡SSRF!)
    if(isset($_GET['custom_host'])) {
        $api_url = str_replace('api.coingecko.com', $_GET['custom_host'], $api_url);
    }
    
    $response = @file_get_contents($api_url);
    echo $response ?: '{"error":"Failed to fetch"}';
    exit;
}

// Vulnerabilidad 3: Fetch de cualquier URL POST
if($_SERVER['REQUEST_METHOD'] === 'POST') {
    $input = json_decode(file_get_contents('php://input'), true);
    
    if(isset($input['url'])) {
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $input['url']);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true); // ¡Peligroso!
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false); // SSL vulnerable
        curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
        
        // Headers personalizados (¡SSRF avanzado!)
        if(isset($input['headers'])) {
            curl_setopt($ch, CURLOPT_HTTPHEADER, $input['headers']);
        }
        
        $result = curl_exec($ch);
        $info = curl_getinfo($ch);
        curl_close($ch);
        
        echo json_encode([
            'data' => $result,
            'info' => $info,
            'vulnerable' => 'SSRF_CVE_2025_001'
        ]);
        exit;
    }
}

// Endpoint para AWS metadata (¡explícitamente vulnerable!)
if(isset($_GET['metadata'])) {
    $metadata_path = $_GET['metadata'] ?? 'latest/meta-data/';
    
    // AWS Metadata URL fija
    $aws_url = "http://169.254.169.254/$metadata_path";
    
    $context = stream_context_create([
        'http' => [
            'method' => 'GET',
            'header' => "User-Agent: CryptoNexus/1.0\r\n"
        ]
    ]);
    
    $data = @file_get_contents($aws_url, false, $context);
    
    if($data) {
        // ¡Flag para CTF!
        if(strpos($data, 'iam/security-credentials/') !== false) {
            $data .= "\n<!-- FLAG: CTF{SSRF_AWS_Metadata_Success} -->\n";
        }
        
        header('Content-Type: text/plain');
        echo $data;
    } else {
        echo "Failed to access metadata. Are we in AWS?";
    }
    exit;
}

// Default response
echo json_encode([
    'status' => 'ready',
    'vulnerabilities' => [
        'SSRF' => 'Enabled',
        'CORS' => 'Misconfigured',
        'Auth' => 'None',
        'Endpoints' => [
            'GET /api/price_checker.php?api_url=URL',
            'GET /api/price_checker.php?metadata=PATH',
            'POST /api/price_checker.php with {"url": "TARGET"}'
        ]
    ],
    'warning' => 'This endpoint is intentionally vulnerable for educational purposes'
]);
?>
