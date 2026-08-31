#include "storage_manager.h"

StorageManager storage;

StorageManager::StorageManager() {}

bool StorageManager::begin() {
    return _prefs.begin("sentinel", false);
}

bool StorageManager::loadConfig(AppConfig &config) {
    if (!_prefs.begin("sentinel", true)) {
        return false;
    }
    
    config.configured = _prefs.getBool("configured", false);
    
    String ssid = _prefs.getString("ssid", "");
    String pass = _prefs.getString("pass", "");
    String loc = _prefs.getString("location", "Ponto Nao Identificado");
    String lan_ip = _prefs.getString("lan_ip", "");
    uint16_t lan_port = _prefs.getUShort("lan_port", 80);
    String cloud = _prefs.getString("cloud_url", "http://179.197.73.80:8016/api/v1/telemetry");
    String token = _prefs.getString("api_token", "keepalive-secret-token-123");
    uint16_t interval = _prefs.getUShort("interval", 10);
    
    _prefs.end();
    
    strncpy(config.wifi_ssid, ssid.c_str(), sizeof(config.wifi_ssid) - 1);
    strncpy(config.wifi_pass, pass.c_str(), sizeof(config.wifi_pass) - 1);
    strncpy(config.location_name, loc.c_str(), sizeof(config.location_name) - 1);
    strncpy(config.target_lan_ip, lan_ip.c_str(), sizeof(config.target_lan_ip) - 1);
    config.target_lan_port = lan_port;
    strncpy(config.cloud_url, cloud.c_str(), sizeof(config.cloud_url) - 1);
    strncpy(config.api_token, token.c_str(), sizeof(config.api_token) - 1);
    config.check_interval_sec = (interval < 3) ? 10 : interval;
    
    return config.configured;
}

bool StorageManager::saveConfig(const AppConfig &config) {
    if (!_prefs.begin("sentinel", false)) {
        return false;
    }
    
    _prefs.putBool("configured", true);
    _prefs.putString("ssid", config.wifi_ssid);
    _prefs.putString("pass", config.wifi_pass);
    _prefs.putString("location", config.location_name);
    _prefs.putString("lan_ip", config.target_lan_ip);
    _prefs.putUShort("lan_port", config.target_lan_port);
    _prefs.putString("cloud_url", config.cloud_url);
    _prefs.putString("api_token", config.api_token);
    _prefs.putUShort("interval", config.check_interval_sec);
    
    _prefs.end();
    return true;
}

void StorageManager::resetConfig() {
    if (_prefs.begin("sentinel", false)) {
        _prefs.clear();
        _prefs.end();
    }
}
