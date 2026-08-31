#pragma once

#include "config.h"
#include <WiFi.h>
#include <WiFiClient.h>

class NetworkProbe {
public:
    NetworkProbe();
    bool probeTarget(const char *targetIP, uint16_t targetPort, float &rttMs, String &macStr);
    String discoverIPByMAC(const char *targetMAC, int maxRetries = 1, int delayBetweenRetriesMs = 1500);

private:
    WiFiClient _client;
    String queryArpTable(const IPAddress &targetIP);
};

extern NetworkProbe networkProbe;
