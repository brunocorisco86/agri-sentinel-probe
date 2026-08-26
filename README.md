# Keepalive Foresight 🛰️🐔

> Sistema de Diagnóstico e Monitoramento de Conectividade Rural (WAN vs LAN) para Ambientes Avícolas e Gateways LoRaWAN Dragino (C.Vale).

Consulte os documentos principais:
- 📖 [Documento de Arquitetura (`idea.md`)](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/idea.md)
- 🗺️ [Roadmap de Implementação (`ROADMAP.md`)](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/ROADMAP.md)
- 📜 [Diário de Bordo & Logs de Sessões (`docs/sessions/SESSION_LOG.md`)](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/docs/sessions/SESSION_LOG.md)

---

## 🏗️ Estrutura do Projeto
- `/firmware`: Código C++ / PlatformIO para LilyGO T-Display ESP32 (TFT ST7789, Captive Portal, ARP/TCP Probe, Heartbeat).
- `/backend`: API FastAPI assíncrona, Pydantic V2, PostgreSQL/SQLite e Dead Man's Switch worker.
- `/docker`: Configurações Docker Compose e Nginx.
- `/docs`: Manuais de instalação, especificações técnicas e diário de sessões.

