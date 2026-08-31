#include "network_probe.h"
#include "lwip/etharp.h"
#include "lwip/ip_addr.h"
#include "lwip/netif.h"

NetworkProbe networkProbe;

NetworkProbe::NetworkProbe() {}

String NetworkProbe::queryArpTable(const IPAddress &targetIP) {
    ip4_addr_t ip;
    ip.addr = static_cast<uint32_t>(targetIP);
    
    struct netif *nif = netif_default;
    if (!nif) return "";
    
    // Dispara solicitacao ARP proativa na rede
    etharp_request(nif, &ip);
    
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
    
    // 1. Tenta resolucao ARP
    macStr = queryArpTable(ip);
    if (macStr.length() == 0) {
        macStr = "ARP_PENDING";
    }
    
    // 2. Tenta abertura de Socket TCP rapido
    _client.setTimeout(400); // 400ms max timeout
    unsigned long start = micros();
    bool connected = _client.connect(ip, targetPort);
    unsigned long elapsed = micros() - start;
    
    if (connected) {
        rttMs = elapsed / 1000.0f;
        _client.stop();
        
        // Se conectou, consulta ARP novamente para atualizar MAC
        String resolvedMac = queryArpTable(ip);
        if (resolvedMac.length() > 0) {
            macStr = resolvedMac;
        }
        return true;
    }
    
    // Se a porta TCP estiver fechada (RST recebido rápido), o host ainda assim está ONLINE na LAN!
    // No ESP32, se a tentativa falhar em < 50ms com ARP resolvido, o dispositivo respondeu na camada de rede.
    if (macStr != "ARP_PENDING" && elapsed < 80000) {
        rttMs = elapsed / 1000.0f;
        return true;
    }
    
    rttMs = -1.0f;
    return false;
}
