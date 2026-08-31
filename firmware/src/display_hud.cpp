#include "display_hud.h"

DisplayHUD hud;

DisplayHUD::DisplayHUD()
#if defined(HAS_TFT_DISPLAY)
    : _tft(TFT_eSPI()), _spr(&_tft), _initialized(false)
#endif
{
#if defined(HAS_STATUS_LED)
    _ledPin = STATUS_LED_PIN;
    #if defined(STATUS_LED_INVERTED)
        _ledInverted = true;
    #else
        _ledInverted = false;
    #endif
#endif
}

void DisplayHUD::begin() {
#if defined(HAS_STATUS_LED)
    pinMode(_ledPin, OUTPUT);
    digitalWrite(_ledPin, _ledInverted ? HIGH : LOW); // Desliga inicial
#endif

#if defined(HAS_TFT_DISPLAY)
    _tft.init();
    _tft.setRotation(1); // Paisagem (Landscape 240x135)
    _tft.fillScreen(TFT_BLACK);
    
    #if defined(TFT_BL)
        pinMode(TFT_BL, OUTPUT);
        digitalWrite(TFT_BL, TFT_BACKLIGHT_ON);
    #endif

    _spr.setColorDepth(8); // 8-bit color sprite para economizar RAM
    _spr.createSprite(240, 135);
    _initialized = true;
#endif
}

void DisplayHUD::showBootScreen(const String &version, const String &model) {
#if defined(HAS_TFT_DISPLAY)
    if (!_initialized) return;
    _spr.fillSprite(TFT_BLACK);
    
    // Header
    _spr.fillRoundRect(5, 5, 230, 24, 4, TFT_DARKCYAN);
    _spr.setTextColor(TFT_WHITE, TFT_DARKCYAN);
    _spr.setTextDatum(MC_DATUM);
    _spr.drawString("KEEPALIVE FORESIGHT", 120, 17, 2);
    
    // Body
    _spr.setTextColor(TFT_GREENYELLOW, TFT_BLACK);
    _spr.setTextDatum(MC_DATUM);
    _spr.drawString("AGRI-SENTINEL PROBE", 120, 52, 2);
    
    _spr.setTextColor(TFT_LIGHTGREY, TFT_BLACK);
    _spr.drawString("Ver: " + version, 120, 75, 2);
    _spr.drawString(model, 120, 95, 1);
    
    // Footer
    _spr.setTextColor(TFT_CYAN, TFT_BLACK);
    _spr.drawString("Iniciando subsistemas...", 120, 120, 1);
    
    _spr.pushSprite(0, 0);
#endif
}

void DisplayHUD::showConfigAPScreen(const String &apSSID, const String &apIP) {
#if defined(HAS_TFT_DISPLAY)
    if (!_initialized) return;
    _spr.fillSprite(TFT_BLACK);
    
    // Header Modo AP
    _spr.fillRoundRect(5, 5, 230, 24, 4, TFT_ORANGE);
    _spr.setTextColor(TFT_BLACK, TFT_ORANGE);
    _spr.setTextDatum(MC_DATUM);
    _spr.drawString("MODO PROVISIONAMENTO", 120, 17, 2);
    
    // Instruções
    _spr.setTextColor(TFT_WHITE, TFT_BLACK);
    _spr.setTextDatum(TL_DATUM);
    _spr.drawString("1. Conecte ao Wi-Fi:", 10, 36, 2);
    
    _spr.setTextColor(TFT_YELLOW, TFT_BLACK);
    _spr.drawString(apSSID, 20, 55, 2);
    
    _spr.setTextColor(TFT_WHITE, TFT_BLACK);
    _spr.drawString("2. Abra o navegador em:", 10, 76, 2);
    
    _spr.setTextColor(TFT_CYAN, TFT_BLACK);
    _spr.drawString("http://" + apIP, 20, 95, 2);
    
    _spr.setTextColor(TFT_DARKGREY, TFT_BLACK);
    _spr.setTextDatum(MC_DATUM);
    _spr.drawString("Aguardando configuracao web...", 120, 122, 1);
    
    _spr.pushSprite(0, 0);
#endif
}

void DisplayHUD::showConnectingScreen(const String &targetSSID, uint8_t attempt) {
#if defined(HAS_TFT_DISPLAY)
    if (!_initialized) return;
    _spr.fillSprite(TFT_BLACK);
    
    _spr.fillRoundRect(5, 5, 230, 24, 4, TFT_NAVY);
    _spr.setTextColor(TFT_WHITE, TFT_NAVY);
    _spr.setTextDatum(MC_DATUM);
    _spr.drawString("CONECTANDO WI-FI", 120, 17, 2);
    
    _spr.setTextColor(TFT_WHITE, TFT_BLACK);
    _spr.setTextDatum(MC_DATUM);
    _spr.drawString("Rede Alvo:", 120, 50, 2);
    
    _spr.setTextColor(TFT_CYAN, TFT_BLACK);
    _spr.drawString(targetSSID, 120, 72, 4);
    
    _spr.setTextColor(TFT_YELLOW, TFT_BLACK);
    _spr.drawString("Tentativa: " + String(attempt) + "/20", 120, 105, 2);
    
    _spr.pushSprite(0, 0);
#endif
}

void DisplayHUD::updateHUD(const ProbeMetrics &metrics, const AppConfig &config) {
#if defined(HAS_TFT_DISPLAY)
    if (!_initialized) return;
    _spr.fillSprite(TFT_BLACK);
    
    // 1. Barra Superior (Header de Status)
    uint16_t headerBg = metrics.cloud_online ? TFT_DARKGREEN : TFT_MAROON;
    _spr.fillRect(0, 0, 240, 20, headerBg);
    
    _spr.setTextColor(TFT_WHITE, headerBg);
    _spr.setTextDatum(TL_DATUM);
    _spr.drawString("Ponto: " + String(config.location_name), 6, 3, 2);
    
    _spr.setTextDatum(TR_DATUM);
    _spr.drawString(String(metrics.wifi_rssi) + "dBm | " + String(metrics.uptime_sec) + "s", 234, 3, 2);
    
    // 2. Bloco Central: Alvo Local (Gateway / Dragino)
    _spr.drawRoundRect(5, 24, 112, 80, 4, TFT_DARKGREY);
    _spr.setTextColor(TFT_SILVER, TFT_BLACK);
    _spr.setTextDatum(TC_DATUM);
    _spr.drawString("ALVO LAN", 61, 28, 1);
    
    if (metrics.local_target_enabled) {
        if (metrics.local_target_online) {
            _spr.setTextColor(TFT_GREEN, TFT_BLACK);
            _spr.drawString("ONLINE", 61, 40, 2);
            _spr.setTextColor(TFT_WHITE, TFT_BLACK);
            _spr.drawString(String(metrics.local_target_rtt_ms, 1) + " ms", 61, 60, 4);
        } else {
            _spr.setTextColor(TFT_RED, TFT_BLACK);
            _spr.drawString("OFFLINE", 61, 44, 2);
            _spr.setTextColor(TFT_DARKGREY, TFT_BLACK);
            _spr.drawString("Falha LAN", 61, 66, 1);
        }
        _spr.setTextColor(TFT_SKYBLUE, TFT_BLACK);
        _spr.drawString(config.target_lan_ip, 61, 88, 1);
    } else {
        _spr.setTextColor(TFT_DARKGREY, TFT_BLACK);
        _spr.drawString("DESABILITADO", 61, 48, 1);
        _spr.drawString("Modo WAN-Only", 61, 68, 1);
    }
    
    // 3. Bloco Central: Nuvem (VPS / FastAPI)
    _spr.drawRoundRect(123, 24, 112, 80, 4, TFT_DARKGREY);
    _spr.setTextColor(TFT_SILVER, TFT_BLACK);
    _spr.setTextDatum(TC_DATUM);
    _spr.drawString("NUVEM (VPS)", 179, 28, 1);
    
    if (metrics.cloud_online) {
        _spr.setTextColor(TFT_GREEN, TFT_BLACK);
        _spr.drawString("CONECTADO", 179, 40, 2);
        _spr.setTextColor(TFT_WHITE, TFT_BLACK);
        _spr.drawString(String(metrics.cloud_rtt_ms, 1) + " ms", 179, 60, 4);
        _spr.setTextColor(TFT_SKYBLUE, TFT_BLACK);
        _spr.drawString("HTTP 200 OK", 179, 88, 1);
    } else {
        _spr.setTextColor(TFT_RED, TFT_BLACK);
        _spr.drawString("FALHA WAN", 179, 44, 2);
        _spr.setTextColor(TFT_DARKGREY, TFT_BLACK);
        _spr.drawString("HTTP: " + String(metrics.last_http_code), 179, 66, 1);
        _spr.drawString("Sem resposta", 179, 88, 1);
    }
    
    // 4. Rodapé Diagnóstico (Matriz Booleana de Estados)
    _spr.fillRect(0, 108, 240, 27, TFT_NAVY);
    _spr.setTextDatum(MC_DATUM);
    
    if (metrics.cloud_online && (!metrics.local_target_enabled || metrics.local_target_online)) {
        _spr.setTextColor(TFT_GREENYELLOW, TFT_NAVY);
        _spr.drawString("ESTADO: 100% OPERACIONAL", 120, 121, 2);
    } else if (metrics.cloud_online && metrics.local_target_enabled && !metrics.local_target_online) {
        _spr.setTextColor(TFT_YELLOW, TFT_NAVY);
        _spr.drawString("ESTADO: FALHA NO GATEWAY LOCAL", 120, 121, 2);
    } else if (!metrics.cloud_online && metrics.wifi_connected) {
        _spr.setTextColor(TFT_RED, TFT_NAVY);
        _spr.drawString("ESTADO: QUEDA DE LINK WAN PROVEDOR", 120, 121, 2);
    } else {
        _spr.setTextColor(TFT_RED, TFT_NAVY);
        _spr.drawString("ESTADO: SEM CONEXAO WI-FI LOCAL", 120, 121, 2);
    }
    
    _spr.pushSprite(0, 0);
#endif
}

void DisplayHUD::showErrorScreen(const String &errorMessage) {
#if defined(HAS_TFT_DISPLAY)
    if (!_initialized) return;
    _spr.fillSprite(TFT_BLACK);
    
    _spr.fillRoundRect(5, 5, 230, 24, 4, TFT_RED);
    _spr.setTextColor(TFT_WHITE, TFT_RED);
    _spr.setTextDatum(MC_DATUM);
    _spr.drawString("FALHA CRITICA", 120, 17, 2);
    
    _spr.setTextColor(TFT_YELLOW, TFT_BLACK);
    _spr.setTextDatum(MC_DATUM);
    _spr.drawString(errorMessage, 120, 67, 2);
    
    _spr.setTextColor(TFT_DARKGREY, TFT_BLACK);
    _spr.drawString("Pressione AP para reconfigurar", 120, 110, 1);
    
    _spr.pushSprite(0, 0);
#endif
}

void DisplayHUD::updateStatusLED(DeviceState state, bool heartbeatTick) {
#if defined(HAS_STATUS_LED)
    switch (state) {
        case STATE_CONFIG_AP:
            // Piscando rápido no modo AP
            digitalWrite(_ledPin, (millis() % 200 < 100) ? (_ledInverted ? LOW : HIGH) : (_ledInverted ? HIGH : LOW));
            break;
            
        case STATE_CONNECTING:
            // Piscando médio enquanto conecta
            digitalWrite(_ledPin, (millis() % 600 < 300) ? (_ledInverted ? LOW : HIGH) : (_ledInverted ? HIGH : LOW));
            break;
            
        case STATE_MONITORING:
            // Pulso curto a cada tick de heartbeat
            if (heartbeatTick) {
                digitalWrite(_ledPin, _ledInverted ? LOW : HIGH);
            } else {
                digitalWrite(_ledPin, _ledInverted ? HIGH : LOW);
            }
            break;
            
        case STATE_ERROR:
        default:
            // Duplo flash rápido de erro
            uint32_t t = millis() % 1000;
            bool on = (t < 100) || (t >= 200 && t < 300);
            digitalWrite(_ledPin, on ? (_ledInverted ? LOW : HIGH) : (_ledInverted ? HIGH : LOW));
            break;
    }
#endif
}
