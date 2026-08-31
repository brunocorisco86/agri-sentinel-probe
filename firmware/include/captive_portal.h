#pragma once

#include "config.h"
#include <WiFi.h>
#include <WebServer.h>
#include <DNSServer.h>

class CaptivePortal {
public:
    CaptivePortal();
    void start(const String &apSSID);
    void stop();
    void handleClient();
    bool isConfigurationSubmitted() const { return _configSubmitted; }
    const AppConfig& getNewConfig() const { return _pendingConfig; }

private:
    WebServer _server;
    DNSServer _dnsServer;
    bool _running;
    bool _configSubmitted;
    AppConfig _pendingConfig;
    String _apSSID;
    
    void setupRoutes();
    void handleRoot();
    void handleScan();
    void handleSave();
    void handleNotFound();
    String buildHTML();
};

extern CaptivePortal captivePortal;
