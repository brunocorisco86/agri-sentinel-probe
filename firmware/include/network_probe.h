#pragma once

#include "config.h"
#include <WiFi.h>
#include <WiFiClient.h>

class NetworkProbe {
public:
    NetworkProbe();
    bool probeTarget(const char *targetIP, uint16_t targetPort, float &rttMs, String &macStr);
    String discoverIPByMAC(const char *targetMAC);

private:
    WiFiClient _client;
    String queryArpTable(const IPAddress &targetIP);
};

extern NetworkProbe networkProbe;
