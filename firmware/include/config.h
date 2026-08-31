#pragma once

#include <Arduino.h>

// Identificação da Versão do Firmware
#define FIRMWARE_VERSION "1.0.0"

// Determinação do modelo de hardware
#if defined(ENV_T_DISPLAY_S3)
    #define HARDWARE_MODEL "LilyGO T-Display-S3 (ESP32-S3)"
#elif defined(ENV_TTGO_T_DISPLAY)
    #define HARDWARE_MODEL "LilyGO T-Display (ESP32)"
#elif defined(ENV_ESP32_C3_SUPERMINI)
    #define HARDWARE_MODEL "ESP32-C3 SuperMini"
#else
    #define HARDWARE_MODEL "ESP32 Generic"
#endif

// Botão de reset de fábrica / Forçar modo AP
#ifndef BTN_AP_TRIGGER
    #if defined(ENV_T_DISPLAY_S3)
        #define BTN_AP_TRIGGER 14
    #elif defined(ENV_TTGO_T_DISPLAY)
        #define BTN_AP_TRIGGER 35
    #elif defined(ENV_ESP32_C3_SUPERMINI)
        #define BTN_AP_TRIGGER 9
    #else
        #define BTN_AP_TRIGGER 0
    #endif
#endif

#define BTN_HOLD_TIME_MS 3000

// Estados da Máquina de Estados
enum DeviceState {
    STATE_BOOT,
    STATE_CONFIG_AP,
    STATE_CONNECTING,
    STATE_MONITORING,
    STATE_ERROR
};

// Estrutura de Configuração Persistente (NVS)
struct AppConfig {
    char wifi_ssid[64];
    char wifi_pass[64];
    char location_name[64];      // Nome amigável do ponto (Ex: 'Casa Bruno', 'Granja Aviario 01')
    char target_lan_ip[32];      // IP do alvo local (Ex: '192.168.1.50' ou vazio para WAN-only)
    char target_lan_mac[24];     // MAC Address para Auto-Discovery DHCP (Ex: 'A8:40:41:xx:xx:xx')
    uint16_t target_lan_port;    // Porta TCP (Ex: 80)
    char cloud_url[128];         // URL do Backend FastAPI (Ex: 'http://vps-ip:8000/api/v1/telemetry')
    char api_token[128];         // Token de autenticação Bearer
    uint16_t check_interval_sec; // Intervalo de envio (Default: 10s)
    bool configured;             // Flag indicando se já foi configurado via Portal
};

// Métricas e Diagnóstico em Tempo Real
struct ProbeMetrics {
    bool wifi_connected;
    int8_t wifi_rssi;
    String ip_address;
    String gateway_ip;
    
    // Status do Alvo LAN
    bool local_target_enabled;
    bool local_target_online;
    float local_target_rtt_ms;
    String local_target_mac;
    
    // Status da Nuvem (WAN / VPS)
    bool cloud_online;
    float cloud_rtt_ms;
    int last_http_code;
    
    // Métricas do Sistema
    uint32_t uptime_sec;
    uint32_t packets_sent;
    uint32_t packets_lost;
    uint32_t free_heap_bytes;
    
    // Identificadores Únicos e Relógio NTP
    String device_id;
    String device_mac;
    String hardware_model;
    String current_time_str;
};
