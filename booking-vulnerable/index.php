<?php
// Router vulnerable a LFI
session_start();

// Configuración de sesión insegura
ini_set('session.cookie_httponly', '0');
ini_set('session.cookie_secure', '0');
ini_set('session.use_only_cookies', '0');

// Incluir archivos sin validación
require_once 'includes/config.php';
require_once 'includes/functions.php';

// Determinar página a cargar (vulnerable a LFI)
$page = isset($_GET['page']) ? $_GET['page'] : 'home';

// Lista blanca muy permisiva
$allowed_pages = ['home', 'search', 'hotel-details', 'booking', 'reviews', 
                  'profile', 'admin', 'login', 'register', 'config-view'];

if (in_array($page, $allowed_pages)) {
    // Pero luego se usa include directamente con la variable
    include("pages/$page.php");
} else {
    // Fallback peligroso
    if (file_exists("pages/$page.php")) {
        include("pages/$page.php");  // ⚠️ LFI aquí
    } else {
        include("pages/home.php");
    }
}

// Cargar footer
include('templates/footer.php');
?>