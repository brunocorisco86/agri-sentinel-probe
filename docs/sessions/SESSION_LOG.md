# 📜 Diário de Bordo e Logs de Sessões - Keepalive Foresight

Este documento registra cronologicamente todas as sessões de planejamento, arquitetura, desenvolvimento, testes e decisões técnicas do projeto.

---

## 📌 Diretrizes de Ambiente e Infraestrutura

- **Máquina Local (Host de Desenvolvimento):**
  - Ambiente primário de codificação, compilação de firmware PlatformIO e execução de testes automatizados com `pytest`.
  - Todas as validações unitárias, integração de schemas e simulações E2E de rede devem ser executadas e aprovadas localmente antes de qualquer implantação.
- **Ambiente de Produção (VPS Alpine Linux - Baixo Recurso):**
  - VPS de baixa renda / baixo recurso (512MB - 1GB RAM, 1 vCPU) rodando **Alpine Linux** (OpenRC + musl libc).
  - **Decisão de Containerização:** Execução em **Container Docker** com imagem enxuta baseada em `python:3.11-alpine` e limite de memória em 128MB.
  - **Persistência Ultra-Otimizada:** Uso mandatório de **SQLite assíncrono com WAL Mode (`aiosqlite`)** em volume Docker, eliminando o consumo de um daemon de banco tradicional.
  - **Consumo Total Projetado do Servidor:** < 100MB RAM (Alpine base + Docker daemon + FastAPI backend).
- **Estratégia de Deploy & Controle de Versão (GitHub):**
  - Antes do Go-Live e da conexão SSH com a VPS, será disponibilizado um repositório remoto no **GitHub** (`git remote add origin <url>`) para orquestrar o clone e deploy automatizado na nuvem.

---

## 🗓️ Sessão 01 — 26/08/2026 (Inicialização & Arquitetura Completa)

### 🎯 Objetivos da Sessão
1. Estruturação inicial do projeto Keepalive Foresight.
2. Definição completa do documento mestre de arquitetura ([`idea.md`](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/idea.md)).
3. Especificação do servidor web embarcado com Captive Portal no ESP32.
4. Criação da árvore de diretórios do Monorepo e arquivos base (`/firmware`, `/backend`, `/docker`, `/docs`).
5. Definição e registro dos subagentes especializados (`firmware-engineer`, `backend-cloud-engineer`, `qa-simulation-engineer`).
6. Configuração e inicialização da engine de grafo de conhecimento **Graphify**.
7. Elaboração do [`ROADMAP.md`](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/ROADMAP.md) detalhado em 4 fases.
8. Criação dos Playbooks de **Comissionamento da VPS Alpine** e **Gravação Flash do ESP32**.
9. Validação do modelo de containerização e otimização para VPS de baixos recursos.

### 🛠️ Decisões Técnicas Consolidadas
- **Hardware & Edge:** LilyGO T-Display ESP32 (display ST7789 240x135 via SPI DMA, `TFT_eSprite` double buffering). Varredura ARP (`lwip/etharp.h`) e socket TCP probe (porta 80) para detecção de presença e saúde do Gateway Dragino.
- **Web Provisioning:** SoftAP nativo (`Keepalive-Probe-XXXX`) com servidor DNS (porta 53) redirecionando para portal web responsivo (`192.168.4.1`) e persistência Flash (`Preferences.h`).
- **Backend Cloud:** FastAPI assíncrono, Pydantic V2, motor de *Dead Man's Switch* (10s), notificações Telegram Bot e SQLite WAL em container Docker Alpine com footprint < 60MB.
- **Matriz Booleana de 4 Estados:** Classificação temporal exata de anomalias (Tudo OK, Falha Dragino LAN, Queda WAN Provedor e Blecaute Rural).

### 📁 Artefatos Criados & Estruturados
- [`idea.md`](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/idea.md): Documento mestre de arquitetura e especificação.
- [`ROADMAP.md`](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/ROADMAP.md): Planejamento detalhado em 4 fases de execução.
- [`docs/playbooks/vps_commissioning_playbook.md`](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/docs/playbooks/vps_commissioning_playbook.md): Playbook de setup e hardening para VPS Alpine Linux de baixo recurso.
- [`docs/playbooks/firmware_flash_playbook.md`](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/docs/playbooks/firmware_flash_playbook.md): Playbook de compilação, upload e validação de boot do ESP32.
- [`docker/docker-compose.yml`](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/docker/docker-compose.yml) & [`docker/Dockerfile.backend`](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/docker/Dockerfile.backend): Configurações de containerização ultra-enxuta.
- [`firmware/platformio.ini`](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/firmware/platformio.ini): Setup PlatformIO para TTGO T-Display com TFT_eSPI.
- [`backend/requirements.txt`](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/backend/requirements.txt): Dependências Python leves.
- [`graphify-out/`](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/graphify-out/): Base de conhecimento em grafo com visualizador interativo `graph.html`.

### 🏁 Status do Projeto ao Final da Sessão 01
- **Status:** Planejamento, Arquitetura, Playbooks e Infraestrutura 100% concluídos e auditados.
- **Próxima Sessão (Sessão 02):**
  1. Conexão do repositório remoto no GitHub (`git remote add origin ...`).
  2. Inicialização do desenvolvimento do firmware ESP32 (Fase 1) e/ou backend FastAPI (Fase 2) na máquina local com testes automatizados (`pytest`).


