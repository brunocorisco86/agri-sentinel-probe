#pragma once

#include "config.h"
#include <HTTPClient.h>
#include <ArduinoJson.h>

class CloudClient {
public:
    CloudClient();
    bool sendTelemetry(const AppConfig &config, ProbeMetrics &metrics);

private:
    HTTPClient _http;
    WiFiClient _client;
};

extern CloudClient cloudClient;
