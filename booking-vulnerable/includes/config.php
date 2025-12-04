<?php
// ⚠️ ARCHIVO DE CONFIGURACIÓN CON DATOS SENSIBLES

// Configuración de base de datos
define('DB_HOST', 'localhost');
define('DB_USER', 'booking_admin');
define('DB_PASS', 'SuperSecret123!');  // ⚠️ Contraseña en texto plano
define('DB_NAME', 'booking_vulnerable');

// Configuración de correo
define('SMTP_HOST', 'smtp.gmail.com');
define('SMTP_USER', 'admin@booking.com');
define('SMTP_PASS', 'EmailPassword456');

// Claves de API expuestas
define('STRIPE_SECRET_KEY', 'sk_live_1234567890abcdef');
define('GOOGLE_MAPS_API_KEY', 'AIzaSyABCDEFGHIJKLMNOPQRSTUVWXYZ123456');
define('PAYPAL_CLIENT_SECRET', 'EFGHIJKLMNOP_123456_secret');

// Configuración de sesión insegura
ini_set('session.cookie_lifetime', 86400);  // 24 horas
ini_set('session.gc_maxlifetime', 86400);
ini_set('session.save_path', __DIR__ . '/../temp/sessions');  // ⚠️ Sesiones en archivo

// Deshabilitar protecciones
ini_set('allow_url_fopen', '1');
ini_set('allow_url_include', '1');

// Mostrar errores en producción
error_reporting(E_ALL);
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);

// Logging inseguro
define('LOG_FILE', __DIR__ . '/../logs/app.log');

// Configuración de subida de archivos
define('UPLOAD_DIR', __DIR__ . '/../assets/uploads/');
define('MAX_FILE_SIZE', 100 * 1024 * 1024);  // 100MB (demasiado grande)
define('ALLOWED_EXTENSIONS', ['jpg', 'png', 'gif', 'jpeg', 'pdf', 'doc', 'docx', 'php']);  // ⚠️ Permite PHP

// Configuración de CORS insegura
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: *');
header('Access-Control-Allow-Credentials: true');

// Sin cabeceras de seguridad
// X-Frame-Options: DENY (NO está presente - Clickjacking)
// Content-Security-Policy (NO está presente - XSS)
// X-XSS-Protection (NO está presente)
?>