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
    digitalWrite(_ledPin, _ledInverted ? HIGH : LOW);
#endif

#if defined(HAS_TFT_DISPLAY)
    #if defined(PIN_POWER_ON)
        pinMode(PIN_POWER_ON, OUTPUT);
        digitalWrite(PIN_POWER_ON, HIGH);
    #endif

    _tft.init();
    #if defined(ENV_T_DISPLAY_S3)
        _tft.setRotation(1); // 320x170
    #else
        _tft.setRotation(1); // 240x135
    #endif
    _tft.fillScreen(TFT_BLACK);
    
    #if defined(TFT_BL)
        pinMode(TFT_BL, OUTPUT);
        digitalWrite(TFT_BL, TFT_BACKLIGHT_ON);
    #endif

    _spr.setColorDepth(8); // 8-bit sprite para economizar RAM
    _spr.createSprite(_tft.width(), _tft.height());
    _initialized = true;
#endif
}

void DisplayHUD::showBootScreen(const String &version, const String &model) {
#if defined(HAS_TFT_DISPLAY)
    if (!_initialized) return;
    int w = _tft.width();
    int h = _tft.height();
    _spr.fillSprite(TFT_BLACK);
    
    // Header
    _spr.fillRoundRect(5, 5, w - 10, 24, 4, TFT_DARKCYAN);
    _spr.setTextColor(TFT_WHITE, TFT_DARKCYAN);
    _spr.setTextDatum(MC_DATUM);
    _spr.drawString("KEEPALIVE FORESIGHT", w / 2, 17, 2);
    
    // Body
    _spr.setTextColor(TFT_GREENYELLOW, TFT_BLACK);
    _spr.setTextDatum(MC_DATUM);
    _spr.drawString("AGRI-SENTINEL PROBE", w / 2, h * 0.38, 2);
    
    _spr.setTextColor(TFT_LIGHTGREY, TFT_BLACK);
    _spr.drawString("Ver: " + version, w / 2, h * 0.56, 2);
    _spr.drawString(model, w / 2, h * 0.72, 2);
    
    // Footer
    _spr.setTextColor(TFT_CYAN, TFT_BLACK);
    _spr.drawString("Iniciando subsistemas...", w / 2, h - 14, 1);
    
    _spr.pushSprite(0, 0);
#endif
}

void DisplayHUD::showConfigAPScreen(const String &apSSID, const String &apIP) {
#if defined(HAS_TFT_DISPLAY)
    if (!_initialized) return;
    int w = _tft.width();
    int h = _tft.height();
    _spr.fillSprite(TFT_BLACK);
    
    // Header Modo AP
    _spr.fillRoundRect(5, 5, w - 10, 24, 4, TFT_ORANGE);
    _spr.setTextColor(TFT_BLACK, TFT_ORANGE);
    _spr.setTextDatum(MC_DATUM);
    _spr.drawString("MODO PROVISIONAMENTO", w / 2, 17, 2);
    
    // Instruções
    _spr.setTextColor(TFT_WHITE, TFT_BLACK);
    _spr.setTextDatum(TL_DATUM);
    _spr.drawString("1. Conecte ao Wi-Fi:", 12, h * 0.26, 2);
    
    _spr.setTextColor(TFT_YELLOW, TFT_BLACK);
    _spr.drawString(apSSID, 24, h * 0.40, 2);
    
    _spr.setTextColor(TFT_WHITE, TFT_BLACK);
    _spr.drawString("2. Abra o navegador em:", 12, h * 0.58, 2);
    
    _spr.setTextColor(TFT_CYAN, TFT_BLACK);
    _spr.drawString("http://" + apIP, 24, h * 0.72, 2);
    
    _spr.setTextColor(TFT_DARKGREY, TFT_BLACK);
    _spr.setTextDatum(MC_DATUM);
    _spr.drawString("Aguardando configuracao web...", w / 2, h - 12, 1);
    
    _spr.pushSprite(0, 0);
#endif
}

void DisplayHUD::showConnectingScreen(const String &targetSSID, uint8_t attempt) {
#if defined(HAS_TFT_DISPLAY)
    if (!_initialized) return;
    int w = _tft.width();
    int h = _tft.height();
    _spr.fillSprite(TFT_BLACK);
    
    _spr.fillRoundRect(5, 5, w - 10, 24, 4, TFT_NAVY);
    _spr.setTextColor(TFT_WHITE, TFT_NAVY);
    _spr.setTextDatum(MC_DATUM);
    _spr.drawString("CONECTANDO WI-FI", w / 2, 17, 2);
    
    _spr.setTextColor(TFT_WHITE, TFT_BLACK);
    _spr.setTextDatum(MC_DATUM);
    _spr.drawString("Rede Alvo:", w / 2, h * 0.36, 2);
    
    _spr.setTextColor(TFT_CYAN, TFT_BLACK);
    _spr.drawString(targetSSID, w / 2, h * 0.52, 4);
    
    _spr.setTextColor(TFT_YELLOW, TFT_BLACK);
    _spr.drawString("Tentativa: " + String(attempt) + "/20", w / 2, h * 0.78, 2);
    
    _spr.pushSprite(0, 0);
#endif
}

void DisplayHUD::updateHUD(const ProbeMetrics &metrics, const AppConfig &config) {
#if defined(HAS_TFT_DISPLAY)
    if (!_initialized) return;
    int w = _tft.width();
    int h = _tft.height();
    _spr.fillSprite(TFT_BLACK);
    
    // 1. Barra Superior (Header de Status)
    uint16_t headerBg = metrics.cloud_online ? TFT_DARKGREEN : TFT_MAROON;
    _spr.fillRect(0, 0, w, 22, headerBg);
    
    _spr.setTextColor(TFT_WHITE, headerBg);
    _spr.setTextDatum(TL_DATUM);
    _spr.drawString("Ponto: " + String(config.location_name), 6, 4, 2);
    
    _spr.setTextDatum(TR_DATUM);
    _spr.drawString(String(metrics.wifi_rssi) + "dBm | " + String(metrics.uptime_sec) + "s", w - 6, 4, 2);
    
    // Dimensões dos blocos centrais
    int blockW = (w - 18) / 2;
    int blockH = h - 58;
    int topY = 26;
    
    // 2. Bloco Central: Alvo Local (Gateway / Dragino)
    int leftX = 6;
    _spr.drawRoundRect(leftX, topY, blockW, blockH, 4, TFT_DARKGREY);
    _spr.setTextColor(TFT_SILVER, TFT_BLACK);
    _spr.setTextDatum(TC_DATUM);
    _spr.drawString("ALVO LAN", leftX + blockW / 2, topY + 4, 1);
    
    if (metrics.local_target_enabled) {
        if (metrics.local_target_online) {
            _spr.setTextColor(TFT_GREEN, TFT_BLACK);
            _spr.drawString("ONLINE", leftX + blockW / 2, topY + 16, 2);
            _spr.setTextColor(TFT_WHITE, TFT_BLACK);
            _spr.drawString(String(metrics.local_target_rtt_ms, 1) + " ms", leftX + blockW / 2, topY + 38, 4);
        } else {
            _spr.setTextColor(TFT_RED, TFT_BLACK);
            _spr.drawString("OFFLINE", leftX + blockW / 2, topY + 20, 2);
            _spr.setTextColor(TFT_DARKGREY, TFT_BLACK);
            _spr.drawString("Falha LAN", leftX + blockW / 2, topY + 44, 1);
        }
        _spr.setTextColor(TFT_SKYBLUE, TFT_BLACK);
        _spr.drawString(config.target_lan_ip, leftX + blockW / 2, topY + blockH - 14, 1);
    } else {
        _spr.setTextColor(TFT_DARKGREY, TFT_BLACK);
        _spr.drawString("DESABILITADO", leftX + blockW / 2, topY + 24, 1);
        _spr.drawString("Modo WAN-Only", leftX + blockW / 2, topY + 44, 1);
    }
    
    // 3. Bloco Central: Nuvem (VPS / FastAPI)
    int rightX = leftX + blockW + 6;
    _spr.drawRoundRect(rightX, topY, blockW, blockH, 4, TFT_DARKGREY);
    _spr.setTextColor(TFT_SILVER, TFT_BLACK);
    _spr.setTextDatum(TC_DATUM);
    _spr.drawString("NUVEM (VPS)", rightX + blockW / 2, topY + 4, 1);
    
    if (metrics.cloud_online) {
        _spr.setTextColor(TFT_GREEN, TFT_BLACK);
        _spr.drawString("CONECTADO", rightX + blockW / 2, topY + 16, 2);
        _spr.setTextColor(TFT_WHITE, TFT_BLACK);
        _spr.drawString(String(metrics.cloud_rtt_ms, 1) + " ms", rightX + blockW / 2, topY + 38, 4);
        _spr.setTextColor(TFT_SKYBLUE, TFT_BLACK);
        _spr.drawString("HTTP 200 OK", rightX + blockW / 2, topY + blockH - 14, 1);
    } else {
        _spr.setTextColor(TFT_RED, TFT_BLACK);
        _spr.drawString("FALHA WAN", rightX + blockW / 2, topY + 20, 2);
        _spr.setTextColor(TFT_DARKGREY, TFT_BLACK);
        _spr.drawString("HTTP: " + String(metrics.last_http_code), rightX + blockW / 2, topY + 42, 1);
        _spr.drawString("Sem resposta", rightX + blockW / 2, topY + blockH - 14, 1);
    }
    
    // 4. Rodapé Diagnóstico (Matriz Booleana de Estados)
    int footerH = 26;
    int footerY = h - footerH;
    _spr.fillRect(0, footerY, w, footerH, TFT_NAVY);
    _spr.setTextDatum(MC_DATUM);
    
    if (metrics.cloud_online && (!metrics.local_target_enabled || metrics.local_target_online)) {
        _spr.setTextColor(TFT_GREENYELLOW, TFT_NAVY);
        _spr.drawString("ESTADO: 100% OPERACIONAL", w / 2, footerY + 13, 2);
    } else if (metrics.cloud_online && metrics.local_target_enabled && !metrics.local_target_online) {
        _spr.setTextColor(TFT_YELLOW, TFT_NAVY);
        _spr.drawString("ESTADO: FALHA NO GATEWAY LOCAL", w / 2, footerY + 13, 2);
    } else if (!metrics.cloud_online && metrics.wifi_connected) {
        _spr.setTextColor(TFT_RED, TFT_NAVY);
        _spr.drawString("ESTADO: QUEDA DE LINK WAN PROVEDOR", w / 2, footerY + 13, 2);
    } else {
        _spr.setTextColor(TFT_RED, TFT_NAVY);
        _spr.drawString("ESTADO: SEM CONEXAO WI-FI LOCAL", w / 2, footerY + 13, 2);
    }
    
    _spr.pushSprite(0, 0);
#endif
}

void DisplayHUD::showErrorScreen(const String &errorMessage) {
#if defined(HAS_TFT_DISPLAY)
    if (!_initialized) return;
    int w = _tft.width();
    int h = _tft.height();
    _spr.fillSprite(TFT_BLACK);
    
    _spr.fillRoundRect(5, 5, w - 10, 24, 4, TFT_RED);
    _spr.setTextColor(TFT_WHITE, TFT_RED);
    _spr.setTextDatum(MC_DATUM);
    _spr.drawString("FALHA CRITICA", w / 2, 17, 2);
    
    _spr.setTextColor(TFT_YELLOW, TFT_BLACK);
    _spr.setTextDatum(MC_DATUM);
    _spr.drawString(errorMessage, w / 2, h * 0.48, 2);
    
    _spr.setTextColor(TFT_DARKGREY, TFT_BLACK);
    _spr.drawString("Pressione AP para reconfigurar", w / 2, h - 14, 1);
    
    _spr.pushSprite(0, 0);
#endif
}

void DisplayHUD::updateStatusLED(DeviceState state, bool heartbeatTick) {
#if defined(HAS_STATUS_LED)
    switch (state) {
        case STATE_CONFIG_AP:
            digitalWrite(_ledPin, (millis() % 200 < 100) ? (_ledInverted ? LOW : HIGH) : (_ledInverted ? HIGH : LOW));
            break;
            
        case STATE_CONNECTING:
            digitalWrite(_ledPin, (millis() % 600 < 300) ? (_ledInverted ? LOW : HIGH) : (_ledInverted ? HIGH : LOW));
            break;
            
        case STATE_MONITORING:
            if (heartbeatTick) {
                digitalWrite(_ledPin, _ledInverted ? LOW : HIGH);
            } else {
                digitalWrite(_ledPin, _ledInverted ? HIGH : LOW);
            }
            break;
            
        case STATE_ERROR:
        default:
            uint32_t t = millis() % 1000;
            bool on = (t < 100) || (t >= 200 && t < 300);
            digitalWrite(_ledPin, on ? (_ledInverted ? LOW : HIGH) : (_ledInverted ? HIGH : LOW));
            break;
    }
#endif
}
