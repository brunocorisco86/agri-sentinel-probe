# Keepalive Foresight 🛰️🐔 (Agri Sentinel Probe)

> Sistema de Diagnóstico e Monitoramento de Conectividade Rural (WAN vs LAN) para Ambientes Avícolas e Gateways LoRaWAN Dragino (C.Vale).  
> **Repositório GitHub:** [`https://github.com/brunocorisco86/agri-sentinel-probe`](https://github.com/brunocorisco86/agri-sentinel-probe)

---

## 📚 Documentos de Referência
- 📖 [Documento Mestre de Arquitetura (`idea.md`)](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/idea.md)
- 🗺️ [Roadmap de Implementação (`ROADMAP.md`)](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/ROADMAP.md)
- 📜 [Diário de Bordo & Logs de Sessões (`docs/sessions/SESSION_LOG.md`)](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/docs/sessions/SESSION_LOG.md)
- 🚀 [Playbook de Comissionamento da VPS Alpine](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/docs/playbooks/vps_commissioning_playbook.md)
- ⚡ [Playbook de Flash do Firmware ESP32](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/docs/playbooks/firmware_flash_playbook.md)

---

## 🏗️ Estrutura do Projeto
- `/firmware`: Código C++ / PlatformIO para LilyGO T-Display ESP32 (TFT ST7789, Captive Portal, ARP/TCP Probe, Heartbeat).
- `/backend`: API FastAPI assíncrona, Pydantic V2, SQLite WAL e Dead Man's Switch worker.
- `/docker`: Configurações Docker Compose e Dockerfile para Alpine Linux.
- `/docs`: Playbooks operacionais, manuais de instalação e diário de sessões.


