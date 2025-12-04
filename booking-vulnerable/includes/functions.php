<?php
// ⚠️ FUNCIONES CON MÚLTIPLES VULNERABILIDADES

function unsafe_query($sql) {
    // ⚠️ SQL Injection: ejecuta consultas sin parámetros
    global $pdo;
    try {
        $stmt = $pdo->query($sql);
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    } catch (Exception $e) {
        // ⚠️ Fuga de información: muestra errores detallados
        die("Error en consulta: " . $e->getMessage() . "<br>SQL: " . $sql);
    }
}

function execute_command($cmd) {
    // ⚠️ Inyección de comandos: ejecuta comandos del sistema
    return shell_exec($cmd . " 2>&1");
}

function load_template($template, $data = []) {
    // ⚠️ SSTI (Server-Side Template Injection): evalúa código PHP
    extract($data);
    ob_start();
    eval('?>' . file_get_contents($template));
    return ob_get_clean();
}

function include_file($filepath) {
    // ⚠️ LFI: incluye archivos sin validación
    if (file_exists($filepath)) {
        return include($filepath);
    }
    return false;
}

function sanitize_input($input) {
    // ⚠️ Sanitización débil: solo elimina tags básicos
    return strip_tags($input);
}

function get_user_data($user_id) {
    // ⚠️ BOLA: no verifica permisos
    $sql = "SELECT * FROM users WHERE id = $user_id";
    $result = unsafe_query($sql);
    return $result[0] ?? null;
}

function process_payment($data) {
    // ⚠️ Manipulación de lógica de negocio: confía en datos del cliente
    $amount = $data['amount'];  // Podría ser manipulado
    $user_id = $data['user_id'];
    
    $sql = "INSERT INTO payments (user_id, amount, status) 
            VALUES ($user_id, $amount, 'completed')";
    return unsafe_query($sql);
}

function upload_file($file) {
    // ⚠️ Subida de archivos insegura
    $filename = $file['name'];
    $tmp_name = $file['tmp_name'];
    
    // Solo verifica extensión
    $ext = strtolower(pathinfo($filename, PATHINFO_EXTENSION));
    $allowed = ['jpg', 'png', 'gif', 'php', 'phtml'];  // ⚠️ Permite PHP
    
    if (in_array($ext, $allowed)) {
        move_uploaded_file($tmp_name, UPLOAD_DIR . $filename);
        return $filename;
    }
    return false;
}

function make_http_request($url) {
    // ⚠️ SSRF: hace requests a URLs proporcionadas por el usuario
    return file_get_contents($url);
}

function unserialize_data($data) {
    // ⚠️ Deserialización insegura
    return unserialize($data);
}

function get_config($key) {
    // ⚠️ Expone configuración sensible
    global $config;
    return $config[$key] ?? null;
}
?>