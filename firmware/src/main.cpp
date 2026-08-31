#include <Arduino.h>
#include <WiFi.h>
#include <esp_task_wdt.h>

#include "config.h"
#include "storage_manager.h"
#include "display_hud.h"
#include "captive_portal.h"
#include "network_probe.h"
#include "cloud_client.h"

// Instâncias Globais
AppConfig appConfig;
ProbeMetrics probeMetrics;
DeviceState currentState = STATE_BOOT;

// Controle Temporal
unsigned long lastTelemetryMillis = 0;
unsigned long lastHudUpdateMillis = 0;
unsigned long btnPressStartTime = 0;
bool btnPressed = false;
uint32_t bootTimestamp = 0;

void setupIdentifiers() {
    uint8_t mac[6];
    WiFi.macAddress(mac);
    char macBuf[20];
    snprintf(macBuf, sizeof(macBuf), "%02X:%02X:%02X:%02X:%02X:%02X",
             mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
    probeMetrics.device_mac = String(macBuf);
    
    char idBuf[32];
    snprintf(idBuf, sizeof(idBuf), "SENTINEL-%02X%02X", mac[4], mac[5]);
    probeMetrics.device_id = String(idBuf);
    probeMetrics.hardware_model = HARDWARE_MODEL;
}

void enterConfigMode() {
    currentState = STATE_CONFIG_AP;
    String apSSID = "Keepalive-" + probeMetrics.device_id;
    Serial.println("[PROVISIONAMENTO] Entrando em Modo SoftAP: " + apSSID);
    
    hud.showConfigAPScreen(apSSID, "192.168.4.1");
    captivePortal.start(apSSID);
}

void checkButtonTrigger() {
    bool isDown = (digitalRead(BTN_AP_TRIGGER) == LOW);
    
    if (isDown) {
        if (!btnPressed) {
            btnPressed = true;
            btnPressStartTime = millis();
        } else if (millis() - btnPressStartTime > BTN_HOLD_TIME_MS) {
            Serial.println("[BOTAO] Botao pressionado por 3s. Forcando Modo AP!");
            enterConfigMode();
            btnPressed = false;
            while (digitalRead(BTN_AP_TRIGGER) == LOW) { delay(10); }
        }
    } else {
        btnPressed = false;
    }
}

void setup() {
    Serial.begin(115200);
    delay(500);
    Serial.println();
    Serial.println("======================================");
    Serial.println("   KEEPALIVE FORESIGHT - SENTINEL     ");
    Serial.println("   Hardware: " HARDWARE_MODEL);
    Serial.println("   Versao: " FIRMWARE_VERSION);
    Serial.println("======================================");
    Serial.println();
    
    pinMode(BTN_AP_TRIGGER, INPUT_PULLUP);
    
    // Inicializa Display e LED
    hud.begin();
    hud.showBootScreen(FIRMWARE_VERSION, HARDWARE_MODEL);
    
    // Configura Hardware Watchdog Timer (30 segundos)
    #if ESP_IDF_VERSION >= ESP_IDF_VERSION_VAL(5, 0, 0)
        esp_task_wdt_config_t twdt_config = {
            .timeout_ms = 30000,
            .idle_core_mask = 0,
            .trigger_panic = false
        };
        esp_task_wdt_reconfigure(&twdt_config);
    #else
        esp_task_wdt_init(30, false);
        esp_task_wdt_add(NULL);
    #endif

    setupIdentifiers();
    Serial.println("[ID] Device ID: " + probeMetrics.device_id);
    Serial.println("[ID] Device MAC: " + probeMetrics.device_mac);
    
    delay(1000);
    
    // Carrega configuracoes da NVS
    bool isConfigured = storage.loadConfig(appConfig);
    
    if (!isConfigured || strlen(appConfig.wifi_ssid) == 0) {
        Serial.println("[NVS] Nenhuma rede configurada. Iniciando Portal Captive...");
        enterConfigMode();
    } else {
        Serial.println("[NVS] Configuracao carregada!");
        Serial.println("      Ponto: " + String(appConfig.location_name));
        Serial.println("      SSID: " + String(appConfig.wifi_ssid));
        Serial.println("      Alvo LAN: " + String(appConfig.target_lan_ip));
        Serial.println("      Cloud URL: " + String(appConfig.cloud_url));
        
        currentState = STATE_CONNECTING;
        WiFi.mode(WIFI_STA);
        WiFi.begin(appConfig.wifi_ssid, appConfig.wifi_pass);
    }
    
    bootTimestamp = millis();
}

void loop() {
    esp_task_wdt_reset();
    checkButtonTrigger();
    
    // Atualizacao de Uptime
    probeMetrics.uptime_sec = (millis() - bootTimestamp) / 1000;
    probeMetrics.free_heap_bytes = ESP.getFreeHeap();
    
    // -------------------------------------------------------------
    // ESTADO 1: MODO CONFIGURACAO / AP CAPTIVE PORTAL
    // -------------------------------------------------------------
    if (currentState == STATE_CONFIG_AP) {
        captivePortal.handleClient();
        hud.updateStatusLED(STATE_CONFIG_AP, false);
        
        if (captivePortal.isConfigurationSubmitted()) {
            AppConfig newConf = captivePortal.getNewConfig();
            storage.saveConfig(newConf);
            appConfig = newConf;
            
            Serial.println("[PROVISIONAMENTO] Nova configuracao recebida! Conectando em STA...");
            delay(1500);
            captivePortal.stop();
            
            currentState = STATE_CONNECTING;
            WiFi.mode(WIFI_STA);
            WiFi.begin(appConfig.wifi_ssid, appConfig.wifi_pass);
        }
        return;
    }
    
    // -------------------------------------------------------------
    // ESTADO 2: CONECTANDO AO WI-FI LOCAL
    // -------------------------------------------------------------
    if (currentState == STATE_CONNECTING) {
        uint8_t attempts = 0;
        hud.showConnectingScreen(appConfig.wifi_ssid, attempts);
        
        while (WiFi.status() != WL_CONNECTED && attempts < 20) {
            esp_task_wdt_reset();
            checkButtonTrigger();
            if (currentState == STATE_CONFIG_AP) return;
            
            delay(500);
            attempts++;
            hud.showConnectingScreen(appConfig.wifi_ssid, attempts);
            hud.updateStatusLED(STATE_CONNECTING, false);
            Serial.print(".");
        }
        
        if (WiFi.status() == WL_CONNECTED) {
            Serial.println();
            Serial.println("[WIFI] Conectado com sucesso!");
            Serial.println("[WIFI] IP Local: " + WiFi.localIP().toString());
            Serial.println("[WIFI] RSSI: " + String(WiFi.RSSI()) + " dBm");
            
            probeMetrics.wifi_connected = true;
            probeMetrics.ip_address = WiFi.localIP().toString();
            probeMetrics.gateway_ip = WiFi.gatewayIP().toString();
            probeMetrics.wifi_rssi = WiFi.RSSI();
            
            currentState = STATE_MONITORING;
            lastTelemetryMillis = 0; // Forca execucao imediata do primeiro ciclo
        } else {
            Serial.println();
            Serial.println("[WIFI] Falha ao conectar. Reabrindo modo AP...");
            enterConfigMode();
            return;
        }
    }
    
    // -------------------------------------------------------------
    // ESTADO 3: MONITORAMENTO ATIVO (PROBE & TELEMETRIA)
    // -------------------------------------------------------------
    if (currentState == STATE_MONITORING) {
        // Verifica se a conexao Wi-Fi caiu
        if (WiFi.status() != WL_CONNECTED) {
            probeMetrics.wifi_connected = false;
            probeMetrics.wifi_rssi = 0;
            Serial.println("[WIFI] Conexao perdida! Tentando reconectar...");
            currentState = STATE_CONNECTING;
            WiFi.disconnect();
            WiFi.begin(appConfig.wifi_ssid, appConfig.wifi_pass);
            return;
        }
        
        probeMetrics.wifi_connected = true;
        probeMetrics.wifi_rssi = WiFi.RSSI();
        
        unsigned long intervalMs = appConfig.check_interval_sec * 1000UL;
        if (millis() - lastTelemetryMillis >= intervalMs) {
            lastTelemetryMillis = millis();
            
            // 1. Probe LAN (Alvo Local)
            if (strlen(appConfig.target_lan_ip) > 0 && strcmp(appConfig.target_lan_ip, "0.0.0.0") != 0) {
                probeMetrics.local_target_enabled = true;
                float rtt = 0;
                String mac = "";
                bool online = networkProbe.probeTarget(appConfig.target_lan_ip, appConfig.target_lan_port, rtt, mac);
                
                probeMetrics.local_target_online = online;
                probeMetrics.local_target_rtt_ms = rtt;
                probeMetrics.local_target_mac = mac;
                
                Serial.printf("[PROBE LAN] Alvo: %s:%d | Status: %s | RTT: %.1fms | MAC: %s\n",
                              appConfig.target_lan_ip, appConfig.target_lan_port,
                              online ? "ONLINE" : "OFFLINE", rtt, mac.c_str());
            } else {
                probeMetrics.local_target_enabled = false;
                probeMetrics.local_target_online = true; // No WAN-only mode, bypass LAN fail
                probeMetrics.local_target_rtt_ms = 0;
                probeMetrics.local_target_mac = "WAN-ONLY";
            }
            
            // 2. Telemetria Cloud (VPS)
            bool cloudOk = cloudClient.sendTelemetry(appConfig, probeMetrics);
            Serial.printf("[CLOUD] URL: %s | Status: %s | RTT: %.1fms | HTTP: %d\n",
                          appConfig.cloud_url, cloudOk ? "OK" : "FAIL",
                          probeMetrics.cloud_rtt_ms, probeMetrics.last_http_code);
            
            // Feedback LED de Heartbeat
            hud.updateStatusLED(STATE_MONITORING, true);
        } else {
            hud.updateStatusLED(STATE_MONITORING, false);
        }
        
        // Atualiza HUD a cada 500ms
        if (millis() - lastHudUpdateMillis >= 500) {
            lastHudUpdateMillis = millis();
            hud.updateHUD(probeMetrics, appConfig);
        }
    }
    
    delay(20);
}
