<?php
// ⚠️ API SIN AUTENTICACIÓN NI AUTORIZACIÓN ADECUADA

header('Content-Type: application/json');
require_once '../includes/config.php';
require_once '../includes/functions.php';

// Sin verificación de tokens CSRF
// Sin validación de origen (CORS demasiado permisivo)

$action = $_GET['action'] ?? $_POST['action'] ?? '';

switch ($action) {
    case 'get_user':
        // ⚠️ BOLA: permite consultar cualquier usuario
        $user_id = $_GET['id'] ?? 0;
        $user = get_user_data($user_id);
        
        // ⚠️ Fuga de información: devuelve todos los campos
        echo json_encode($user);
        break;
        
    case 'search_hotels':
        // ⚠️ SQL Injection en parámetros de búsqueda
        $location = $_GET['location'] ?? '';
        $price_min = $_GET['price_min'] ?? 0;
        $price_max = $_GET['price_max'] ?? 10000;
        
        $sql = "SELECT * FROM hotels 
                WHERE location LIKE '%$location%' 
                AND price BETWEEN $price_min AND $price_max";
        
        $results = unsafe_query($sql);
        echo json_encode($results);
        break;
        
    case 'make_reservation':
        // ⚠️ Manipulación de precios desde el cliente
        $data = json_decode(file_get_contents('php://input'), true);
        
        $hotel_id = $data['hotel_id'];
        $user_id = $data['user_id'];
        $price = $data['price'];  // Precio enviado por el cliente
        $dates = $data['dates'];
        
        $sql = "INSERT INTO reservations (hotel_id, user_id, price, dates) 
                VALUES ($hotel_id, $user_id, $price, '$dates')";
        
        unsafe_query($sql);
        echo json_encode(['status' => 'success']);
        break;
        
    case 'upload_review':
        // ⚠️ XSS almacenado: guarda HTML/JS sin sanitizar
        $review = $_POST['review'];
        $hotel_id = $_POST['hotel_id'];
        $user_id = $_POST['user_id'];
        
        $sql = "INSERT INTO reviews (hotel_id, user_id, content) 
                VALUES ($hotel_id, $user_id, '$review')";
        
        unsafe_query($sql);
        echo json_encode(['status' => 'success']);
        break;
        
    case 'execute':
        // ⚠️ Extremadamente peligroso: ejecución remota de código
        if (isset($_SESSION['is_admin'])) {
            $command = $_POST['command'];
            $output = execute_command($command);
            echo json_encode(['output' => $output]);
        }
        break;
        
    default:
        echo json_encode(['error' => 'Acción no válida']);
}
?>