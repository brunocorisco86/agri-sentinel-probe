#include "captive_portal.h"
#include <ArduinoJson.h>

CaptivePortal captivePortal;

CaptivePortal::CaptivePortal() : _server(80), _running(false), _configSubmitted(false) {}

void CaptivePortal::start(const String &apSSID) {
    _apSSID = apSSID;
    _configSubmitted = false;
    
    WiFi.mode(WIFI_AP);
    IPAddress apIP(192, 168, 4, 1);
    IPAddress netMsk(255, 255, 255, 0);
    WiFi.softAPConfig(apIP, apIP, netMsk);
    WiFi.softAP(_apSSID.c_str());
    
    _dnsServer.setErrorReplyCode(DNSReplyCode::NoError);
    _dnsServer.start(53, "*", apIP);
    
    setupRoutes();
    _server.begin();
    _running = true;
}

void CaptivePortal::stop() {
    if (_running) {
        _dnsServer.stop();
        _server.stop();
        WiFi.softAPdisconnect(true);
        _running = false;
    }
}

void CaptivePortal::handleClient() {
    if (_running) {
        _dnsServer.processNextRequest();
        _server.handleClient();
    }
}

void CaptivePortal::setupRoutes() {
    _server.on("/", HTTP_GET, [this]() { handleRoot(); });
    _server.on("/scan", HTTP_GET, [this]() { handleScan(); });
    _server.on("/save", HTTP_POST, [this]() { handleSave(); });
    
    // Handlers para detecção automática de Captive Portal
    _server.on("/generate_204", HTTP_GET, [this]() { handleRoot(); });
    _server.on("/gen_204", HTTP_GET, [this]() { handleRoot(); });
    _server.on("/ncsi.txt", HTTP_GET, [this]() { handleRoot(); });
    _server.on("/hotspot-detect.html", HTTP_GET, [this]() { handleRoot(); });
    _server.on("/canonical.html", HTTP_GET, [this]() { handleRoot(); });
    _server.onNotFound([this]() { handleNotFound(); });
}

void CaptivePortal::handleRoot() {
    _server.send(200, "text/html; charset=utf-8", buildHTML());
}

void CaptivePortal::handleScan() {
    int n = WiFi.scanNetworks(false, false);
    JsonDocument doc;
    JsonArray array = doc.to<JsonArray>();
    
    for (int i = 0; i < n; ++i) {
        JsonObject obj = array.add<JsonObject>();
        obj["ssid"] = WiFi.SSID(i);
        obj["rssi"] = WiFi.RSSI(i);
        obj["secure"] = (WiFi.encryptionType(i) != WIFI_AUTH_OPEN);
    }
    
    String jsonResponse;
    serializeJson(doc, jsonResponse);
    _server.send(200, "application/json", jsonResponse);
}

void CaptivePortal::handleSave() {
    if (_server.hasArg("ssid") && _server.arg("ssid").length() > 0) {
        memset(&_pendingConfig, 0, sizeof(AppConfig));
        
        strncpy(_pendingConfig.wifi_ssid, _server.arg("ssid").c_str(), sizeof(_pendingConfig.wifi_ssid) - 1);
        strncpy(_pendingConfig.wifi_pass, _server.arg("pass").c_str(), sizeof(_pendingConfig.wifi_pass) - 1);
        
        String loc = _server.hasArg("location") && _server.arg("location").length() > 0 ? _server.arg("location") : "Ponto 01";
        strncpy(_pendingConfig.location_name, loc.c_str(), sizeof(_pendingConfig.location_name) - 1);
        
        String lan = _server.hasArg("lan_ip") ? _server.arg("lan_ip") : "";
        strncpy(_pendingConfig.target_lan_ip, lan.c_str(), sizeof(_pendingConfig.target_lan_ip) - 1);
        
        _pendingConfig.target_lan_port = _server.hasArg("lan_port") ? _server.arg("lan_port").toInt() : 80;
        
        String cloud = _server.hasArg("cloud_url") ? _server.arg("cloud_url") : "http://192.168.1.90:8000/api/v1/telemetry";
        strncpy(_pendingConfig.cloud_url, cloud.c_str(), sizeof(_pendingConfig.cloud_url) - 1);
        
        String token = _server.hasArg("api_token") ? _server.arg("api_token") : "keepalive-default-token";
        strncpy(_pendingConfig.api_token, token.c_str(), sizeof(_pendingConfig.api_token) - 1);
        
        uint16_t interval = _server.hasArg("interval") ? _server.arg("interval").toInt() : 10;
        _pendingConfig.check_interval_sec = (interval < 3) ? 10 : interval;
        _pendingConfig.configured = true;
        
        _configSubmitted = true;
        
        String successHtml = R"rawhtml(
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Configuração Salva</title>
    <style>
        body { background: #0f172a; color: #f8fafc; font-family: system-ui, -apple-system, sans-serif; text-align: center; padding: 40px 16px; margin: 0; }
        .card { background: #1e293b; border-radius: 16px; padding: 28px 20px; max-width: 400px; margin: 0 auto; border: 1px solid #334155; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        h2 { color: #22c55e; margin: 0 0 12px 0; font-size: 22px; }
        p { color: #94a3b8; font-size: 15px; line-height: 1.5; margin: 8px 0; }
        .spinner { border: 4px solid rgba(255,255,255,0.1); width: 44px; height: 44px; border-radius: 50%; border-left-color: #38bdf8; animation: spin 1s linear infinite; margin: 24px auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="card">
        <h2>✓ Configuração Salva!</h2>
        <div class="spinner"></div>
        <p>A sonda está reiniciando e conectando à sua rede Wi-Fi.</p>
        <p>O display já está atualizando com o status em tempo real.</p>
    </div>
</body>
</html>
)rawhtml";
        _server.send(200, "text/html; charset=utf-8", successHtml);
    } else {
        _server.send(400, "text/plain", "O campo SSID do Wi-Fi é obrigatório.");
    }
}

void CaptivePortal::handleNotFound() {
    _server.sendHeader("Location", String("http://192.168.4.1/"), true);
    _server.send(302, "text/plain", "Redirecionando para Captive Portal");
}

String CaptivePortal::buildHTML() {
    return R"rawhtml(
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Keepalive Foresight - Provisionamento</title>
    <style>
        :root { --bg: #0f172a; --card: #1e293b; --primary: #0284c7; --text: #f8fafc; --muted: #94a3b8; --border: #334155; --green: #22c55e; }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: var(--bg); color: var(--text); font-family: system-ui, -apple-system, sans-serif; padding: 16px 12px; }
        .container { max-width: 480px; margin: 0 auto; background: var(--card); border-radius: 16px; padding: 20px 18px; border: 1px solid var(--border); box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
        .header { text-align: center; margin-bottom: 20px; }
        .header h1 { font-size: 20px; font-weight: 700; color: #38bdf8; }
        .header p { font-size: 13px; color: var(--muted); margin-top: 4px; }
        .section-title { font-size: 13px; text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em; color: #38bdf8; margin: 20px 0 10px 0; border-bottom: 1px solid var(--border); padding-bottom: 4px; }
        label { display: block; font-size: 13px; font-weight: 600; color: var(--text); margin-bottom: 4px; }
        input, select { width: 100%; padding: 12px; border-radius: 8px; background: #0f172a; border: 1px solid var(--border); color: #fff; font-size: 15px; margin-bottom: 12px; outline: none; -webkit-appearance: none; }
        input:focus, select:focus { border-color: var(--primary); }
        .row-scan { display: flex; gap: 8px; margin-bottom: 8px; }
        .btn-scan { background: #334155; color: #38bdf8; border: 1px solid var(--border); padding: 10px 14px; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; white-space: nowrap; }
        .btn-submit { width: 100%; background: #0284c7; color: #fff; font-weight: 700; font-size: 16px; padding: 14px; border-radius: 8px; border: none; cursor: pointer; margin-top: 16px; }
        .btn-submit:active { background: #0369a1; }
        .help-text { font-size: 11px; color: var(--muted); margin-top: -6px; margin-bottom: 12px; line-height: 1.4; }
        .badge-opt { display: inline-block; background: #334155; color: #94a3b8; font-size: 10px; padding: 2px 6px; border-radius: 4px; margin-left: 4px; }
        #scan-status { font-size: 12px; color: #38bdf8; margin-bottom: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AGRI-SENTINEL PROBE</h1>
            <p>Configuração do Ponto de Verificação</p>
        </div>
        
        <form action="/save" method="POST">
            <!-- 1. Identificação -->
            <div class="section-title">1. Identificação do Ponto</div>
            <label for="location">Nome do Local</label>
            <input type="text" id="location" name="location" value="Minha Casa" placeholder="Ex: Minha Casa, Granja 01, Escritorio">
            <p class="help-text">Nome amigável para identificar esta sonda no painel e alertas.</p>

            <!-- 2. Wi-Fi -->
            <div class="section-title">2. Conexão Wi-Fi</div>
            <label for="ssid">Rede Wi-Fi (SSID)</label>
            <div class="row-scan">
                <select id="wifi_select" onchange="onSelectWifi(this.value)" style="display:none;"></select>
                <input type="text" id="ssid" name="ssid" placeholder="Digite o nome da sua rede Wi-Fi" required>
                <button type="button" class="btn-scan" onclick="scanNetworks()">🔍 Buscar</button>
            </div>
            <div id="scan-status"></div>
            
            <label for="pass">Senha do Wi-Fi</label>
            <input type="password" id="pass" name="pass" placeholder="Senha do Wi-Fi (se houver)">

            <!-- 3. Alvo Local LAN -->
            <div class="section-title">3. Alvo Local na Rede <span class="badge-opt">Opcional</span></div>
            <label for="lan_ip">IP do Gateway Dragino ou Roteador</label>
            <input type="text" id="lan_ip" name="lan_ip" placeholder="Ex: 192.168.1.50">
            <p class="help-text">💡 <b>Para sua casa (WAN-Only):</b> Pode deixar este campo <b>em branco</b>. A sonda monitorará a conexão geral com a internet.</p>

            <!-- 4. Servidor Central VPS -->
            <div class="section-title">4. Servidor Central (VPS) <span class="badge-opt">Pré-configurado</span></div>
            <label for="cloud_url">Endpoint de Telemetria (FastAPI)</label>
            <input type="text" id="cloud_url" name="cloud_url" value="http://192.168.1.90:8000/api/v1/telemetry">

            <label for="api_token">Token da API</label>
            <input type="text" id="api_token" name="api_token" value="keepalive-secret-token-123">

            <button type="submit" class="btn-submit">Salvar & Iniciar Sonda</button>
        </form>
    </div>

    <script>
        function scanNetworks() {
            const statusDiv = document.getElementById('scan-status');
            const select = document.getElementById('wifi_select');
            const input = document.getElementById('ssid');
            statusDiv.innerText = 'Buscando redes próximas...';
            
            fetch('/scan')
                .then(r => r.json())
                .then(data => {
                    select.innerHTML = '<option value="">-- Selecione uma rede encontrada --</option>';
                    data.forEach(item => {
                        if (item.ssid && item.ssid.length > 0) {
                            const opt = document.createElement('option');
                            opt.value = item.ssid;
                            opt.text = item.ssid + ' (' + item.rssi + ' dBm)';
                            select.appendChild(opt);
                        }
                    });
                    select.style.display = 'block';
                    statusDiv.innerText = data.length + ' redes encontradas! Escolha no menu acima ou digite.';
                })
                .catch(e => {
                    statusDiv.innerText = 'Digite o nome da rede manualmente.';
                });
        }
        
        function onSelectWifi(val) {
            if (val) {
                document.getElementById('ssid').value = val;
            }
        }
    </script>
</body>
</html>
)rawhtml";
}
