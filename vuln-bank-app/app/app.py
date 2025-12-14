from flask import Flask, render_template, request, redirect, session, jsonify, send_from_directory
import sqlite3
import subprocess
import os
import pickle
import base64
import requests
from functools import wraps

# ================= 1. CONFIGURACIÓN INICIAL =================
app = Flask(__name__)
# Nota: En una aplicación real, esta clave debe ser compleja y estar en un secreto
app.secret_key = 'insecure_key_12345' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////app/app.db'
app.config['UPLOAD_FOLDER'] = '/app/uploads'

# ================= 2. DECORADORES Y UTILIDADES =================

def login_required(f):
    """Decorator para asegurar que el usuario está logueado."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator para asegurar que el usuario es administrador."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in') or not session.get('is_admin'):
            # Redirigir o mostrar error si no es admin
            return render_template('access_denied.html'), 403 
        return f(*args, **kwargs)
    return decorated_function

# ================= 3. INICIALIZACIÓN DE BASE DE DATOS =================

def init_db():
    conn = sqlite3.connect('/app/app.db')
    cursor = conn.cursor()
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

# ================= 4. RUTAS BASE Y AUTENTICACIÓN =================

@app.route('/')
def index():
    # Renderiza la página de inicio con los enlaces de prueba
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # VULNERABILIDAD: Broken Authentication - Consulta SQL simple
        conn = sqlite3.connect('/app/app.db')
        cursor = conn.cursor()
        
        # Consulta vulnerable a SQL Injection (además del login básico)
        # Permite ' OR '1'='1'--
        query = f"SELECT * FROM user WHERE username = '{username}' AND password = '{password}'"
        
        try:
            cursor.execute(query)
            user = cursor.fetchone()
            conn.close()
            
            if user:
                session.clear()
                session['logged_in'] = True
                session['user_id'] = user[0]
                session['username'] = user[1]
                session['is_admin'] = bool(user[4])
                session['token'] = base64.b64encode(os.urandom(12)).decode('utf-8') # Dummy token
                return redirect('/dashboard')
            else:
                return render_template('login.html', error='Invalid credentials or SQLi failed.')
        except Exception as e:
            return render_template('login.html', error=f'Database Error: {str(e)}')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/dashboard')
@login_required
def dashboard():
    # IDOR VULNERABLE: Usamos el ID de la sesión para obtener los datos
    user_id = session.get('user_id')
    conn = sqlite3.connect('/app/app.db')
    cursor = conn.cursor()
    # Consulta simple que permite IDOR si el ID es manipulable, pero aquí es de la sesión.
    # El IDOR real se prueba en /user/profile/<id>
    cursor.execute(f"SELECT username, email, balance, ssn FROM user WHERE id = {user_id}")
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data:
        user_info = {
            'username': user_data[0],
            'email': user_data[1],
            'balance': user_data[2],
            'ssn': user_data[3],
        }
        return render_template('dashboard.html', user=user_info)
    return redirect('/logout')

# ================= 5. RUTAS DE VULNERABILIDAD (INTEGRACIÓN DE PLANTILLAS) =================

# 5.1 SQL Injection (SQLi)
@app.route('/search')
def search():
    query = request.args.get('q', 'alice')
    conn = sqlite3.connect('/app/app.db')
    cursor = conn.cursor()
    results = []
    error = None
    
    # VULNERABILIDAD: SQL Injection - Concatena la entrada del usuario directamente.
    try:
        # Nota: La ruta de admin también usa esta función para inyección SQL.
        cursor.execute(f"SELECT id, username, email, balance, ssn FROM user WHERE username LIKE '%{query}%' OR email LIKE '%{query}%'")
        results_data = cursor.fetchall()
        for row in results_data:
            results.append({
                'id': row[0],
                'username': row[1],
                'email': row[2],
                'balance': f"${row[3]:.2f}",
                'ssn': row[4]
            })
    except Exception as e:
        error = f'SQL Error: {str(e)}'
        
    conn.close()
    return render_template('search.html', query=query, results=results, error=error)

# 5.2 Command Injection (CMDi)
@app.route('/ping')
@login_required
def ping():
    host = request.args.get('host', '127.0.0.1')
    output = None
    error = None

    if host:
        # VULNERABILIDAD: Command Injection - No sanitiza el input 'host'.
        try:
            # shell=True permite la inyección de comandos como ';whoami'
            # 
            output = subprocess.check_output(f"ping -c 2 {host}", shell=True, text=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            output = f"Command failed with return code {e.returncode}.\nOutput:\n{e.output}"
        except Exception as e:
            error = f"Execution Error: {str(e)}"
    
    return render_template('ping.html', host=host, output=output, error=error)

# Ruta del Admin Panel para ejecución directa de comandos (CMDi)
@app.route('/exec')
@admin_required
def exec_command():
    cmd = request.args.get('cmd', 'echo "No command specified"')
    output = None
    
    try:
        # VULNERABILIDAD: Command Injection (Igual que /ping, pero explícito para admin)
        output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT, timeout=5)
    except subprocess.CalledProcessError as e:
        output = f"Command failed (Return Code {e.returncode}):\n{e.output}"
    except Exception as e:
        output = f"Execution Error: {str(e)}"
        
    # Redirigir al panel de administración para mostrar el output
    # NOTA: Los caracteres especiales deben codificarse para la URL, pero lo pasamos simple para la prueba.
    return redirect(f'/admin?output={base64.urlsafe_b64encode(output.encode()).decode()}')

# 5.3 Local File Inclusion / Path Traversal (LFI)
@app.route('/download')
@admin_required # Restringido a admin para simular una herramienta interna
def download():
    filename = request.args.get('file', 'test.txt')
    
    # VULNERABILIDAD: Path Traversal - No sanitiza 'filename' y permite acceder al root.
    try:
        # Intentamos obtener el archivo.
        # 
        with open(filename, 'r') as f:
            content = f.read()
            # Devolver el contenido dentro de una etiqueta <pre>
            return render_template('lfi_result.html', filename=filename, content=content)
    except FileNotFoundError:
        return render_template('lfi_result.html', filename=filename, error="File not found or access denied (LFI attempt).")
    except Exception as e:
        return render_template('lfi_result.html', filename=filename, error=f"Error accessing file: {str(e)}")

# 5.4 Insecure Direct Object Reference (IDOR)
@app.route('/user/profile/<int:user_id>')
@login_required
def view_user_profile(user_id):
    # VULNERABILIDAD: IDOR - No comprueba si el 'user_id' es el mismo que 'session.user_id'
    conn = sqlite3.connect('/app/app.db')
    cursor = conn.cursor()
    # Expone todos los campos, incluyendo SSN
    cursor.execute(f"SELECT id, username, email, balance, ssn, is_admin FROM user WHERE id = {user_id}")
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data:
        user_info = {
            'id': user_data[0],
            'username': user_data[1],
            'email': user_data[2],
            'balance': f"${user_data[3]:.2f}",
            'ssn': user_data[4], # DATO SENSIBLE EXPUESTO
            'is_admin': bool(user_data[5])
        }
        # Renderiza la plantilla de perfil con los datos del usuario solicitado, no del logueado
        return render_template('profile.html', profile=user_info)
    return "User not found (IDOR access attempt failed)", 404

# 5.5 Cross-Site Scripting (XSS)
@app.route('/comments')
def view_comments():
    comments = []
    if os.path.exists('/app/comments.txt'):
        with open('/app/comments.txt', 'r') as f:
            comments = [c.strip() for c in f.readlines()]
            
    # La plantilla 'comments.html' renderiza con {{ comment|safe }} - VULNERABILIDAD
    # 
    return render_template('comments.html', comments=comments)

@app.route('/post_comment', methods=['POST'])
def post_comment():
    comment_text = request.form.get('comment')
    if comment_text:
        # VULNERABILIDAD: No sanitiza la entrada antes de almacenarla
        with open('/app/comments.txt', 'a') as f:
            f.write(comment_text + '\n')
    return redirect('/comments')

# 5.6 Cross-Site Request Forgery (CSRF)
@app.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer_funds():
    message = None
    error = None
    
    if request.method == 'POST':
        from_user_id = session.get('user_id')
        to_username = request.form.get('to_account')
        amount = request.form.get('amount')
        
        # VULNERABILIDAD: CSRF - Ausencia total de token de protección
        
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive.")
            
            # Lógica de transferencia simulada (en una app real, esto actualizaría la DB)
            if to_username == session.get('username'):
                 raise ValueError("Cannot transfer to self.")
            
            message = f"Transfer of ${amount:.2f} to {to_username} initiated. (Transfer vulnerable to CSRF attack)"
            
        except ValueError as e:
            error = str(e)
        except Exception:
            error = "An unexpected error occurred during transfer."
            
    # Renderizamos la página de transferencia
    return render_template('transfer.html', message=message, error=error)

# 5.7 Server-Side Request Forgery (SSRF)
@app.route('/fetch')
@admin_required # Restringido a admin para simular una herramienta interna
def fetch_url():
    url = request.args.get('url', 'http://example.com')
    output = None
    error = None
    
    # VULNERABILIDAD: SSRF - Usa la URL de entrada sin validación de host.
    try:
        # 
        response = requests.get(url, timeout=5, verify=False)
        output = f"Status: {response.status_code}\n\n{response.text[:1000]}"
    except requests.exceptions.Timeout:
        error = "Request timed out."
    except requests.exceptions.ConnectionError:
        error = f"Connection Error: Could not reach {url}. (Try internal IP: 127.0.0.1)"
    except Exception as e:
        error = f"SSRF Error: {str(e)}"
        
    return render_template('ssrf_result.html', url=url, output=output, error=error)

# 5.8 Insecure Deserialization
@app.route('/import_profile', methods=['GET', 'POST'])
def import_profile():
    if request.method == 'POST':
        profile_data = request.form.get('data', '')
        output = None
        error = None
        
        # VULNERABILIDAD: Insecure Deserialization - Usa pickle.loads en datos de entrada.
        try:
            # 
            profile = pickle.loads(base64.b64decode(profile_data))
            output = f'Profile loaded successfully! Details: {profile}'
        except Exception as e:
            error = f'Deserialization Error: {str(e)}'
        
        return render_template('deserialization.html', output=output, error=error)
        
    return render_template('deserialization.html')

# 5.9 Panel de Administración
@app.route('/admin')
@admin_required
def admin_dashboard():
    conn = sqlite3.connect('/app/app.db')
    cursor = conn.cursor()
    # Obtenemos todos los datos (incluyendo sensibles) para la tabla de administración
    cursor.execute("SELECT id, username, email, balance, ssn FROM user")
    all_users_data = cursor.fetchall()
    conn.close()

    # Convertir a una lista de diccionarios
    all_users = [{'id': r[0], 'username': r[1], 'email': r[2], 'balance': r[3], 'ssn': r[4]} for r in all_users_data]

    # Recuperar la salida del comando si existe (desde /exec)
    command_output_b64 = request.args.get('output', None)
    command_output = None
    if command_output_b64:
        try:
            command_output = base64.urlsafe_b64decode(command_output_b64).decode()
        except Exception:
            command_output = "Error decoding command output."
            
    # La plantilla 'admin.html' incluye las interfaces de prueba CMDi, LFI, SSRF y SQLi.
    return render_template('admin.html', all_users=all_users, command_output=command_output)

# ================= 6. INICIO DE LA APLICACIÓN =================

if __name__ == '__main__':
    # Crear directorio de uploads y archivos de prueba
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Crear archivo de prueba para path traversal
    with open(os.path.join(app.config['UPLOAD_FOLDER'], 'test.txt'), 'w') as f:
        f.write('This is a test file for path traversal.\n')
        
    # Crear archivo de comentarios (XSS persistente)
    if not os.path.exists('/app/comments.txt'):
        with open('/app/comments.txt', 'w') as f:
            f.write('<p>Welcome to the comments!</p>\n')
    
    # Inicializar base de datos
    init_db()
    
    print("\n[+] Starting Vulnerable Bank App on http://0.0.0.0:8080")
    print("[+] Default credentials: admin/admin123, alice/password123, bob/qwerty")
    app.run(host='0.0.0.0', port=8080, debug=True)
