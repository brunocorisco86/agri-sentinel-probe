#include "cloud_client.h"

CloudClient cloudClient;

CloudClient::CloudClient() {}

bool CloudClient::sendTelemetry(const AppConfig &config, ProbeMetrics &metrics) {
    if (WiFi.status() != WL_CONNECTED) {
        metrics.cloud_online = false;
        metrics.cloud_rtt_ms = -1.0f;
        metrics.last_http_code = -1;
        metrics.packets_lost++;
        return false;
    }
    
    if (strlen(config.cloud_url) == 0) {
        metrics.cloud_online = false;
        metrics.last_http_code = 0;
        return false;
    }
    
    JsonDocument doc;
    doc["device_id"] = metrics.device_id;
    doc["device_mac"] = metrics.device_mac;
    doc["location_name"] = config.location_name;
    doc["hardware_model"] = metrics.hardware_model;
    doc["firmware_version"] = FIRMWARE_VERSION;
    doc["uptime_seconds"] = metrics.uptime_sec;
    doc["wifi_ssid"] = metrics.wifi_connected ? WiFi.SSID() : "N/A";
    doc["wifi_rssi_dbm"] = metrics.wifi_rssi;
    
    doc["local_target_enabled"] = metrics.local_target_enabled;
    doc["local_target_ip"] = config.target_lan_ip;
    doc["local_target_online"] = metrics.local_target_online;
    doc["local_target_rtt_ms"] = metrics.local_target_rtt_ms;
    doc["local_target_mac"] = metrics.local_target_mac;
    doc["free_heap_bytes"] = ESP.getFreeHeap();
    
    String payload;
    serializeJson(doc, payload);
    
    _http.begin(_client, config.cloud_url);
    _http.addHeader("Content-Type", "application/json");
    _http.setTimeout(2500); // 2.5s timeout
    
    if (strlen(config.api_token) > 0) {
        _http.addHeader("Authorization", "Bearer " + String(config.api_token));
    }
    
    unsigned long start = micros();
    int httpCode = _http.POST(payload);
    unsigned long elapsed = micros() - start;
    
    metrics.last_http_code = httpCode;
    metrics.packets_sent++;
    
    if (httpCode >= 200 && httpCode < 300) {
        metrics.cloud_online = true;
        metrics.cloud_rtt_ms = elapsed / 1000.0f;
        _http.end();
        return true;
    } else {
        metrics.cloud_online = false;
        metrics.cloud_rtt_ms = -1.0f;
        metrics.packets_lost++;
        _http.end();
        return false;
    }
}
