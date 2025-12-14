import sqlite3
import os

# Define la ruta de la base de datos para que coincida con el mapeo del volumen en Docker-Compose
DATABASE_PATH = '/app/data/app.db'

def init_database():
    """
    Inicializa la base de datos con las tablas y datos de prueba.
    """
    # Intentar crear el directorio si no existe (importante para el volumen /app/data)
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Crear la tabla de usuarios con datos sensibles (SSN)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            email TEXT,
            is_admin INTEGER,
            balance REAL,
            ssn TEXT
        )
    ''')
    
    # Insertar usuarios de prueba si no existen
    cursor.execute("SELECT COUNT(*) FROM user")
    if cursor.fetchone()[0] == 0:
        users = [
            (1, 'admin', 'admin123', 'admin@securebank.com', 1, 1000000.0, '123-45-6789'),
            (2, 'alice', 'password123', 'alice@securebank.com', 0, 5000.0, '987-65-4321'),
            (3, 'bob', 'qwerty', 'bob@securebank.com', 0, 3000.0, '456-78-9123')
        ]
        cursor.executemany('INSERT INTO user VALUES (?,?,?,?,?,?,?)', users)
        
    conn.commit()
    conn.close()

def unsafe_query(query):
    """
    Función intencionalmente vulnerable a SQLi (Inyección SQL).
    
    """
    # VULNERABILIDAD: Ejecución directa de consulta sin sanitización ni parámetros.
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute(query) 
        results = cursor.fetchall()
    except sqlite3.OperationalError as e:
        results = None
        raise Exception(f"SQL Error during execution: {e} | Query: {query}")
        
    conn.close()
    return results

def get_user_by_id(user_id):
    """
    Función para IDOR, usando parámetros seguros para evitar SQLi en el ID,
    pero vulnerable a IDOR si no hay chequeo de sesión.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    # Usamos ? para el ID, pero la consulta está mal protegida en la app principal.
    cursor.execute("SELECT id, username, email, balance, ssn, is_admin FROM user WHERE id = ?", (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data

def get_all_users():
    """
    Función para el panel de administración.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, balance, ssn, is_admin FROM user")
    users = cursor.fetchall()
    conn.close()
    return users
