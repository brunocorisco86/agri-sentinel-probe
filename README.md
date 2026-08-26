# Keepalive Foresight 🛰️🐔

> Sistema de Diagnóstico e Monitoramento de Conectividade Rural (WAN vs LAN) para Ambientes Avícolas e Gateways LoRaWAN Dragino (C.Vale).

Consulte o documento mestre de arquitetura: [`idea.md`](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/idea.md)

---

## 🏗️ Estrutura do Projeto
- `/firmware`: Código C++ / PlatformIO para LilyGO T-Display ESP32 (TFT ST7789, Captive Portal, ARP/TCP Probe, Heartbeat).
- `/backend`: API FastAPI assíncrona, Pydantic V2, PostgreSQL/SQLite e Dead Man's Switch worker.
- `/docker`: Configurações Docker Compose e Nginx.
- `/docs`: Manuais de instalação e especificações técnicas.
