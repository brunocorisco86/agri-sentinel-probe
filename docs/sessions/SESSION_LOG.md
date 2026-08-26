# 📜 Diário de Bordo e Logs de Sessões - Keepalive Foresight

Este documento registra cronologicamente todas as sessões de planejamento, arquitetura, desenvolvimento, testes e decisões técnicas do projeto.

---

## 📌 Diretrizes de Ambiente e Infraestrutura

- **Máquina Local (Host de Desenvolvimento):**
  - Ambiente primário de codificação, compilação de firmware PlatformIO e execução de testes automatizados com `pytest`.
  - Todas as validações unitárias, integração de schemas e simulações E2E de rede devem ser executadas e aprovadas localmente antes de qualquer implantação.
- **Ambiente de Produção (VPS Externa):**
  - O endereço IP/domínio da VPS e as credenciais de acesso via SSH serão fornecidos pelo usuário **após a conclusão e validação de todas as milestones** do [`ROADMAP.md`](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/ROADMAP.md).
  - Nenhum deploy remoto prematuro deve ser executado.

---

## 🗓️ Sessão 01 — 26/08/2026

### 🎯 Objetivos da Sessão
1. Estruturação inicial do projeto Keepalive Foresight.
2. Definição completa do documento mestre de arquitetura ([`idea.md`](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/idea.md)).
3. Especificação do servidor web embarcado com Captive Portal no ESP32.
4. Criação da árvore de diretórios do Monorepo e arquivos base.
5. Definição e registro dos subagentes especializados (`firmware-engineer`, `backend-cloud-engineer`, `qa-simulation-engineer`).
6. Configuração e inicialização da engine de grafo de conhecimento **Graphify**.
7. Elaboração do [`ROADMAP.md`](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/ROADMAP.md) detalhado em 4 fases.

### 🛠️ Decisões Técnicas Tomadas
- **Hardware & Edge:** LilyGO T-Display ESP32 com display ST7789 240x135 via SPI DMA. Uso mandatório de `TFT_eSprite` para eliminar flicker. Detecção local do Gateway Dragino através de varredura ARP (`lwip/etharp.h`) e abertura de socket TCP rápido (porta 80).
- **Web Provisioning:** SoftAP nativo (`Keepalive-Probe-XXXX`) associado a servidor DNS (porta 53) para Captive Portal automático em smartphones, permitindo provisionamento sem computador de campo.
- **Backend:** FastAPI assíncrono com Uvicorn, validação estrita com Pydantic V2, persistência em PostgreSQL 16 (ou SQLite local) e motor em background de *Dead Man's Switch* a cada 10s.
- **Diagnóstico Booleano:** Matriz lógica de 4 estados para isolar:
  1. *Tudo Operacional* (Verde).
  2. *Falha Local Gateway Dragino* (Laranja/Vermelho - WAN OK, Dragino LAN inacessível).
  3. *Queda Link WAN Provedor* (Amarelo - Dragino LAN OK, timeout VPS).
  4. *Queda Geral de Energia/Blecaute* (Preto/Vermelho - timeout geral VPS).

### 📁 Artefatos Criados & Modificados
- [`idea.md`](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/idea.md): Documento de arquitetura detalhado.
- [`ROADMAP.md`](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/ROADMAP.md): Planejamento detalhado em 4 fases de execução.
- [`firmware/platformio.ini`](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/firmware/platformio.ini): Build flags para TTGO T-Display com TFT_eSPI.
- [`backend/requirements.txt`](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/backend/requirements.txt): Dependências FastAPI, SQLAlchemy, Pydantic, HTTPX.
- [`docker/docker-compose.yml`](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/docker/docker-compose.yml): Stack FastAPI + PostgreSQL.
- [`graphify-out/`](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/graphify-out/): Grafo de conhecimento com visualizador `graph.html`.

### 🔄 Próximos Passos (Standby)
Aguardando sinalização do usuário para início da **Fase 1** (Firmware ESP32, Captive Portal e Display HUD) ou **Fase 2** (Backend FastAPI e testes unitários com pytest no ambiente local).
