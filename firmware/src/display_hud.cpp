#include "display_hud.h"

static String formatUptime(uint32_t s) {
    uint32_t days = s / 86400;
    s %= 86400;
    uint32_t hours = s / 3600;
    s %= 3600;
    uint32_t mins = s / 60;
    uint32_t secs = s % 60;
    
    if (days > 0) {
        return String(days) + "d " + String(hours) + "h";
    } else if (hours > 0) {
        return String(hours) + "h " + String(mins) + "m";
    } else if (mins > 0) {
        return String(mins) + "m " + String(secs) + "s";
    } else {
        return String(secs) + "s";
    }
}


DisplayHUD hud;

DisplayHUD::DisplayHUD()
#if defined(HAS_TFT_DISPLAY)
    : _tft(nullptr), _initialized(false)
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
        delay(150);
    #endif

    if (!_tft) {
        _tft = new TFT_eSPI();
    }
    _tft->init();
    #if defined(ENV_T_DISPLAY_S3)
        _tft->setRotation(1); // 320x170
    #else
        _tft->setRotation(1); // 240x135
    #endif
    _tft->fillScreen(TFT_BLACK);
    
    #if defined(TFT_BL)
        pinMode(TFT_BL, OUTPUT);
        digitalWrite(TFT_BL, TFT_BACKLIGHT_ON);
    #endif

    _initialized = true;
#endif
}

void DisplayHUD::showBootScreen(const String &version, const String &model) {
#if defined(HAS_TFT_DISPLAY)
    if (!_initialized || !_tft) return;
    int w = _tft->width();
    int h = _tft->height();
    _tft->fillScreen(TFT_BLACK);
    
    // Header
    _tft->fillRoundRect(5, 5, w - 10, 24, 4, TFT_DARKCYAN);
    _tft->setTextColor(TFT_WHITE, TFT_DARKCYAN);
    _tft->setTextDatum(MC_DATUM);
    _tft->drawString("KEEPALIVE FORESIGHT", w / 2, 17, 2);
    
    // Body
    _tft->setTextColor(TFT_GREENYELLOW, TFT_BLACK);
    _tft->setTextDatum(MC_DATUM);
    _tft->drawString("AGRI-SENTINEL PROBE", w / 2, h * 0.38, 2);
    
    _tft->setTextColor(TFT_LIGHTGREY, TFT_BLACK);
    _tft->drawString("Ver: " + version, w / 2, h * 0.56, 2);
    _tft->drawString(model, w / 2, h * 0.72, 2);
    
    // Footer
    _tft->setTextColor(TFT_CYAN, TFT_BLACK);
    _tft->drawString("Iniciando subsistemas...", w / 2, h - 14, 1);
#endif
}

void DisplayHUD::showConfigAPScreen(const String &apSSID, const String &apIP) {
#if defined(HAS_TFT_DISPLAY)
    if (!_initialized || !_tft) return;
    int w = _tft->width();
    int h = _tft->height();
    _tft->fillScreen(TFT_BLACK);
    
    // Header Modo AP
    _tft->fillRoundRect(5, 5, w - 10, 24, 4, TFT_ORANGE);
    _tft->setTextColor(TFT_BLACK, TFT_ORANGE);
    _tft->setTextDatum(MC_DATUM);
    _tft->drawString("MODO PROVISIONAMENTO", w / 2, 17, 2);
    
    // Instruções
    _tft->setTextColor(TFT_WHITE, TFT_BLACK);
    _tft->setTextDatum(TL_DATUM);
    _tft->drawString("1. Conecte ao Wi-Fi:", 12, h * 0.26, 2);
    
    _tft->setTextColor(TFT_YELLOW, TFT_BLACK);
    _tft->drawString(apSSID, 24, h * 0.40, 2);
    
    _tft->setTextColor(TFT_WHITE, TFT_BLACK);
    _tft->drawString("2. Abra o navegador em:", 12, h * 0.58, 2);
    
    _tft->setTextColor(TFT_CYAN, TFT_BLACK);
    _tft->drawString("http://" + apIP, 24, h * 0.72, 2);
    
    _tft->setTextColor(TFT_DARKGREY, TFT_BLACK);
    _tft->setTextDatum(MC_DATUM);
    _tft->drawString("Aguardando configuracao web...", w / 2, h - 12, 1);
#endif
}

void DisplayHUD::showConnectingScreen(const String &targetSSID, uint8_t attempt) {
#if defined(HAS_TFT_DISPLAY)
    if (!_initialized || !_tft) return;
    int w = _tft->width();
    int h = _tft->height();
    _tft->fillScreen(TFT_BLACK);
    
    _tft->fillRoundRect(5, 5, w - 10, 24, 4, TFT_NAVY);
    _tft->setTextColor(TFT_WHITE, TFT_NAVY);
    _tft->setTextDatum(MC_DATUM);
    _tft->drawString("CONECTANDO WI-FI", w / 2, 17, 2);
    
    _tft->setTextColor(TFT_WHITE, TFT_BLACK);
    _tft->setTextDatum(MC_DATUM);
    _tft->drawString("Rede Alvo:", w / 2, h * 0.36, 2);
    
    _tft->setTextColor(TFT_CYAN, TFT_BLACK);
    _tft->drawString(targetSSID, w / 2, h * 0.52, 4);
    
    _tft->setTextColor(TFT_YELLOW, TFT_BLACK);
    _tft->drawString("Tentativa: " + String(attempt) + "/20", w / 2, h * 0.78, 2);
#endif
}

void DisplayHUD::updateHUD(const ProbeMetrics &metrics, const AppConfig &config) {
#if defined(HAS_TFT_DISPLAY)
    if (!_initialized || !_tft) return;
    int w = _tft->width();
    int h = _tft->height();
    
    // 1. Barra Superior (Header de Status)
    uint16_t headerBg = metrics.cloud_online ? TFT_DARKGREEN : TFT_MAROON;
    _tft->fillRect(0, 0, w, 22, headerBg);
    
    _tft->setTextColor(TFT_WHITE, headerBg);
    _tft->setTextDatum(TL_DATUM);
    _tft->drawString("Ponto: " + String(config.location_name), 6, 4, 2);
    
    _tft->setTextDatum(TR_DATUM);
    _tft->drawString(String(metrics.wifi_rssi) + "dBm | " + formatUptime(metrics.uptime_sec), w - 6, 4, 2);
    
    // Dimensões dos blocos centrais
    int blockW = (w - 18) / 2;
    int blockH = h - 58;
    int topY = 26;
    
    // 2. Bloco Central: Alvo Local (Gateway / Dragino)
    int leftX = 6;
    _tft->fillRect(leftX, topY, blockW, blockH, TFT_BLACK);
    _tft->drawRoundRect(leftX, topY, blockW, blockH, 4, TFT_DARKGREY);
    _tft->setTextColor(TFT_SILVER, TFT_BLACK);
    _tft->setTextDatum(TC_DATUM);
    _tft->drawString("ALVO LAN", leftX + blockW / 2, topY + 4, 1);
    
    if (metrics.local_target_enabled) {
        if (metrics.local_target_online) {
            _tft->setTextColor(TFT_GREEN, TFT_BLACK);
            _tft->drawString("ONLINE", leftX + blockW / 2, topY + 16, 2);
            _tft->setTextColor(TFT_WHITE, TFT_BLACK);
            _tft->drawString(String(metrics.local_target_rtt_ms, 1) + " ms", leftX + blockW / 2, topY + 38, 4);
        } else {
            _tft->setTextColor(TFT_RED, TFT_BLACK);
            _tft->drawString("OFFLINE", leftX + blockW / 2, topY + 20, 2);
            _tft->setTextColor(TFT_DARKGREY, TFT_BLACK);
            _tft->drawString("Falha LAN", leftX + blockW / 2, topY + 44, 1);
        }
        _tft->setTextColor(TFT_SKYBLUE, TFT_BLACK);
        _tft->drawString(config.target_lan_ip, leftX + blockW / 2, topY + blockH - 14, 1);
    } else {
        _tft->setTextColor(TFT_DARKGREY, TFT_BLACK);
        _tft->drawString("DESABILITADO", leftX + blockW / 2, topY + 24, 1);
        _tft->drawString("Modo WAN-Only", leftX + blockW / 2, topY + 44, 1);
    }
    
    // 3. Bloco Central: Nuvem (VPS / FastAPI)
    int rightX = leftX + blockW + 6;
    _tft->fillRect(rightX, topY, blockW, blockH, TFT_BLACK);
    _tft->drawRoundRect(rightX, topY, blockW, blockH, 4, TFT_DARKGREY);
    _tft->setTextColor(TFT_SILVER, TFT_BLACK);
    _tft->setTextDatum(TC_DATUM);
    _tft->drawString("NUVEM (VPS)", rightX + blockW / 2, topY + 4, 1);
    
    if (metrics.cloud_online) {
        _tft->setTextColor(TFT_GREEN, TFT_BLACK);
        _tft->drawString("CONECTADO", rightX + blockW / 2, topY + 16, 2);
        _tft->setTextColor(TFT_WHITE, TFT_BLACK);
        _tft->drawString(String(metrics.cloud_rtt_ms, 1) + " ms", rightX + blockW / 2, topY + 38, 4);
        _tft->setTextColor(TFT_SKYBLUE, TFT_BLACK);
        _tft->drawString("HTTP 200 OK", rightX + blockW / 2, topY + blockH - 14, 1);
    } else {
        _tft->setTextColor(TFT_RED, TFT_BLACK);
        _tft->drawString("FALHA WAN", rightX + blockW / 2, topY + 20, 2);
        _tft->setTextColor(TFT_DARKGREY, TFT_BLACK);
        _tft->drawString("HTTP: " + String(metrics.last_http_code), rightX + blockW / 2, topY + 42, 1);
        _tft->drawString("Sem resposta", rightX + blockW / 2, topY + blockH - 14, 1);
    }
    
    // 4. Rodapé Diagnóstico (Matriz Booleana de Estados)
    int footerH = 26;
    int footerY = h - footerH;
    _tft->fillRect(0, footerY, w, footerH, TFT_NAVY);
    _tft->setTextDatum(MC_DATUM);
    
    if (metrics.cloud_online && (!metrics.local_target_enabled || metrics.local_target_online)) {
        _tft->setTextColor(TFT_GREENYELLOW, TFT_NAVY);
        _tft->drawString("ESTADO: 100% OPERACIONAL", w / 2, footerY + 13, 2);
    } else if (metrics.cloud_online && metrics.local_target_enabled && !metrics.local_target_online) {
        _tft->setTextColor(TFT_YELLOW, TFT_NAVY);
        _tft->drawString("ESTADO: FALHA NO GATEWAY LOCAL", w / 2, footerY + 13, 2);
    } else if (!metrics.cloud_online && metrics.wifi_connected) {
        _tft->setTextColor(TFT_RED, TFT_NAVY);
        _tft->drawString("ESTADO: QUEDA DE LINK WAN PROVEDOR", w / 2, footerY + 13, 2);
    } else {
        _tft->setTextColor(TFT_RED, TFT_NAVY);
        _tft->drawString("ESTADO: SEM CONEXAO WI-FI LOCAL", w / 2, footerY + 13, 2);
    }
#endif
}

void DisplayHUD::showErrorScreen(const String &errorMessage) {
#if defined(HAS_TFT_DISPLAY)
    if (!_initialized || !_tft) return;
    int w = _tft->width();
    int h = _tft->height();
    _tft->fillScreen(TFT_BLACK);
    
    _tft->fillRoundRect(5, 5, w - 10, 24, 4, TFT_RED);
    _tft->setTextColor(TFT_WHITE, TFT_RED);
    _tft->setTextDatum(MC_DATUM);
    _tft->drawString("FALHA CRITICA", w / 2, 17, 2);
    
    _tft->setTextColor(TFT_YELLOW, TFT_BLACK);
    _tft->setTextDatum(MC_DATUM);
    _tft->drawString(errorMessage, w / 2, h * 0.48, 2);
    
    _tft->setTextColor(TFT_DARKGREY, TFT_BLACK);
    _tft->drawString("Pressione AP para reconfigurar", w / 2, h - 14, 1);
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
