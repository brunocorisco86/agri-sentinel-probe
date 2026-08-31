#include <esp_task_wdt.h>
#include "network_probe.h"
#include "lwip/etharp.h"
#include "lwip/ip_addr.h"
#include "lwip/netif.h"
#include "ping/ping_sock.h"

NetworkProbe networkProbe;

struct PingContext {
    bool success;
    uint32_t rtt_ms;
    bool done;
};

static void ping_on_ping_success(esp_ping_handle_t hdl, void *args) {
    PingContext *ctx = (PingContext *)args;
    uint32_t elapsed_time;
    esp_ping_get_profile(hdl, ESP_PING_PROF_TIMEGAP, &elapsed_time, sizeof(elapsed_time));
    ctx->success = true;
    ctx->rtt_ms = elapsed_time;
}

static void ping_on_ping_timeout(esp_ping_handle_t hdl, void *args) {
    // Timeout
}

static void ping_on_ping_end(esp_ping_handle_t hdl, void *args) {
    PingContext *ctx = (PingContext *)args;
    ctx->done = true;
}

NetworkProbe::NetworkProbe() {}

String NetworkProbe::queryArpTable(const IPAddress &targetIP) {
    ip4_addr_t ip;
    ip.addr = static_cast<uint32_t>(targetIP);
    
    struct netif *nif = netif_default;
    if (!nif) return "";
    
    // Dispara solicitacao ARP proativa na rede
    etharp_request(nif, &ip);
    delay(10);
    
    struct eth_addr *eth_ret = nullptr;
    const ip4_addr_t *ip_ret = nullptr;
    ssize_t idx = etharp_find_addr(nif, &ip, &eth_ret, &ip_ret);
    
    if (idx >= 0 && eth_ret != nullptr) {
        char macBuf[20];
        snprintf(macBuf, sizeof(macBuf), "%02X:%02X:%02X:%02X:%02X:%02X",
                 eth_ret->addr[0], eth_ret->addr[1], eth_ret->addr[2],
                 eth_ret->addr[3], eth_ret->addr[4], eth_ret->addr[5]);
        return String(macBuf);
    }
    return "";
}

String NetworkProbe::discoverIPByMAC(const char *targetMAC, int maxRetries, int delayBetweenRetriesMs) {
    if (targetMAC == nullptr || strlen(targetMAC) < 11) return "";
    
    String target = String(targetMAC);
    target.toUpperCase();
    target.replace("-", ":");
    target.trim();
    
    IPAddress localIP = WiFi.localIP();
    IPAddress baseIP = IPAddress(localIP[0], localIP[1], localIP[2], 1);
    struct netif *nif = netif_default;
    if (!nif) return "";
    
    for (int attempt = 1; attempt <= maxRetries; attempt++) {
        esp_task_wdt_reset();
        Serial.printf("[AUTO-DISCOVERY] Tentativa %d/%d: Varrendo subnet para MAC %s ...\n",
                      attempt, maxRetries, target.c_str());
        
        // Dispara rajada ARP para toda a subnet /24
        for (int i = 1; i <= 254; i++) {
            IPAddress candidate(baseIP[0], baseIP[1], baseIP[2], i);
            ip4_addr_t ip;
            ip.addr = static_cast<uint32_t>(candidate);
            etharp_request(nif, &ip);
        }
        
        delay(200); // Aguarda respostas ARP chegarem
        
        // Inspeciona tabela ARP
        for (int i = 1; i <= 254; i++) {
            IPAddress candidate(baseIP[0], baseIP[1], baseIP[2], i);
            ip4_addr_t ip;
            ip.addr = static_cast<uint32_t>(candidate);
            
            struct eth_addr *eth_ret = nullptr;
            const ip4_addr_t *ip_ret = nullptr;
            ssize_t idx = etharp_find_addr(nif, &ip, &eth_ret, &ip_ret);
            
            if (idx >= 0 && eth_ret != nullptr) {
                char macBuf[20];
                snprintf(macBuf, sizeof(macBuf), "%02X:%02X:%02X:%02X:%02X:%02X",
                         eth_ret->addr[0], eth_ret->addr[1], eth_ret->addr[2],
                         eth_ret->addr[3], eth_ret->addr[4], eth_ret->addr[5]);
                String currentMAC = String(macBuf);
                if (currentMAC.equalsIgnoreCase(target)) {
                    Serial.printf("[AUTO-DISCOVERY] SUCESSO! MAC %s encontrado no IP: %s (Tentativa %d)\n",
                                  target.c_str(), candidate.toString().c_str(), attempt);
                    return candidate.toString();
                }
            }
        }
        
        if (attempt < maxRetries) {
            delay(delayBetweenRetriesMs);
        }
    }
    
    Serial.println("[AUTO-DISCOVERY] MAC nao encontrado apos todas as tentativas.");
    return "";
}

bool NetworkProbe::probeTarget(const char *targetIP, uint16_t targetPort, float &rttMs, String &macStr) {
    if (targetIP == nullptr || strlen(targetIP) == 0 || strcmp(targetIP, "0.0.0.0") == 0) {
        rttMs = 0.0f;
        macStr = "N/A";
        return false;
    }
    
    IPAddress ip;
    if (!ip.fromString(targetIP)) {
        rttMs = 0.0f;
        macStr = "INVALID_IP";
        return false;
    }
    
    // 1. Tenta ICMP Ping nativo (ESP-IDF)
    ip_addr_t target_addr;
    target_addr.type = IPADDR_TYPE_V4;
    target_addr.u_addr.ip4.addr = static_cast<uint32_t>(ip);
    
    PingContext pingCtx = {false, 0, false};
    
    esp_ping_config_t ping_config = ESP_PING_DEFAULT_CONFIG();
    ping_config.target_addr = target_addr;
    ping_config.count = 2;              // Envia 2 pings
    ping_config.interval_ms = 100;      // 100ms entre pings
    ping_config.timeout_ms = 400;       // 400ms timeout
    
    esp_ping_callbacks_t cbs;
    cbs.on_ping_success = ping_on_ping_success;
    cbs.on_ping_timeout = ping_on_ping_timeout;
    cbs.on_ping_end = ping_on_ping_end;
    cbs.cb_args = &pingCtx;
    
    esp_ping_handle_t ping_hdl = nullptr;
    if (esp_ping_new_session(&ping_config, &cbs, &ping_hdl) == ESP_OK) {
        esp_ping_start(ping_hdl);
        
        unsigned long startWait = millis();
        while (!pingCtx.done && (millis() - startWait < 1000)) {
            delay(10);
        }
        
        esp_ping_stop(ping_hdl);
        esp_ping_delete_session(ping_hdl);
        
        if (pingCtx.success) {
            rttMs = (float)pingCtx.rtt_ms;
            macStr = queryArpTable(ip);
            if (macStr.length() == 0) macStr = "PING-OK";
            return true;
        }
    }
    
    // 2. Fallback: Tenta abertura de Socket TCP na porta configurada
    _client.setTimeout(400);
    unsigned long start = micros();
    bool connected = _client.connect(ip, targetPort);
    unsigned long elapsed = micros() - start;
    
    if (connected) {
        rttMs = elapsed / 1000.0f;
        _client.stop();
        macStr = queryArpTable(ip);
        if (macStr.length() == 0) macStr = "TCP-OK";
        return true;
    }
    
    // 3. Fallback: Consulta tabela ARP
    macStr = queryArpTable(ip);
    if (macStr.length() > 0 && macStr != "00:00:00:00:00:00") {
        rttMs = 1.0f;
        return true;
    }
    
    macStr = "OFFLINE";
    rttMs = -1.0f;
    return false;
}
