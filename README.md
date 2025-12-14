# 1. Clonar aplicación vulnerable
git clone https://github.com/JdExploit/vuln-bank-app.git
cd /vuln-bank-app

# 2. Construir imagen Docker
docker-compose build --no-cache

# 3. Ejecutar contenedor
docker-compose up -d

# 4. Verificar funcionamiento
curl http://localhost:8080
