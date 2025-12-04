# VULNERABILITIES.md

## SQL Injection
- ✅ `includes/functions.php` - `unsafe_query()`
- ✅ `pages/search.php` - Búsqueda sin parámetros
- ✅ `api/hotels.php` - Consultas concatenadas
- ✅ Procedimientos almacenados en `database.sql`

## Cross-Site Scripting (XSS)
- ✅ Almacenado: `pages/reviews.php` - Reseñas sin sanitizar
- ✅ Reflejado: `pages/search.php` - Echo de parámetros GET
- ✅ DOM-based: `assets/js/main.js` - `innerHTML` con user input

## Local File Inclusion (LFI)
- ✅ `index.php` - Include dinámico sin validación
- ✅ `includes/functions.php` - `include_file()`

## Broken Object Level Authorization (BOLA)
- ✅ `api/users.php` - Acceso a cualquier usuario por ID
- ✅ `pages/profile.php` - Visualización de perfiles sin verificación

## Command Injection
- ✅ `includes/functions.php` - `execute_command()`
- ✅ `api/index.php` - Endpoint `execute`

## Insecure Deserialization
- ✅ `includes/functions.php` - `unserialize_data()`

## Server-Side Request Forgery (SSRF)
- ✅ `includes/functions.php` - `make_http_request()`

## Cross-Site Request Forgery (CSRF)
- ✅ `assets/js/main.js` - Peticiones sin tokens
- ✅ Formularios sin `csrf_token`

## Clickjacking
- ✅ Sin cabeceras `X-Frame-Options`
- ✅ JavaScript para crear iframes ocultos

## Security Misconfiguration
- ✅ `.htaccess` - Configuración insegura
- ✅ `includes/config.php` - Exposición de datos
- ✅ PHP.ini con configuraciones peligrosas

## Sensitive Data Exposure
- ✅ `database.sql` - Contraseñas en texto plano
- ✅ JSON responses con todos los campos
- ✅ Logs con información sensible

## XML External Entities (XXE)
- ❌ No implementado (no hay procesamiento XML)

## Broken Authentication
- ✅ `includes/auth.php` - Autenticación débil
- ✅ Sesiones no regeneradas
- ✅ Contraseñas en MD5

## Insecure Direct Object References (IDOR)
- ✅ URLs con IDs secuenciales
- ✅ No verificación de permisos

## Business Logic Flaws
- ✅ Manipulación de precios desde cliente
- ✅ Estado de reservas modificable

## Cross-Origin Resource Sharing (CORS)
- ✅ Configuración demasiado permisiva

## Server-Side Template Injection (SSTI)
- ✅ `includes/functions.php` - `load_template()`

## Subresource Integrity (SRI)
- ❌ Scripts de terceros sin integridad

## File Upload Vulnerabilities
- ✅ `api/upload.php` - Validación solo por extensión
- ✅ Directorio `uploads/` con permisos 777
