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

---

## 🗓️ Sessão 02 — 31/08/2026 (Implementação do Firmware Multi-Ponto & Dual-Hardware)

### 🎯 Objetivos da Sessão
1. Expandir a arquitetura para suporte a **múltiplos pontos de verificação** (Casa, Granja, Escritório, etc.) e **múltiplos hardwares** (LilyGO T-Display ESP32 e ESP32-C3 SuperMini).
2. Codificação completa de todos os módulos C++ do firmware em [`firmware/include/`](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/firmware/include) e [`firmware/src/`](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/firmware/src).
3. Instalação e configuração do `esptool` e `platformio` no ambiente local de desenvolvimento.
4. Compilação e geração dos binários de flash para ambos os targets (`ttgo-t-display` e `esp32-c3-supermini`).
5. Atualização dos playbooks de flash com comandos diretos do `esptool`.

### 🛠️ Decisões Técnicas Consolidadas
- **Multi-Ponto (WAN-Only vs LAN Gateway):**
  - Configuração de `location_name` amigável via Captive Portal.
  - Caso o campo `target_lan_ip` seja preenchido (ex: `192.168.1.50`), a sonda executa varredura ARP + TCP probe no gateway. Se deixado em branco, a sonda opera em modo **WAN-Only** (ideal para monitorar a conexão residencial ou outros pontos de teste).
- **Dual-Hardware Abstraction:**
  - `LilyGO T-Display (ESP32)`: HUD gráfico 240x135 em `TFT_eSprite` 8-bit double buffer, display ST7789, backlight GPIO 4, trigger AP no GPIO 35.
  - `ESP32-C3 SuperMini (RISC-V)`: Footprint ultra-compacto, USB CDC nativo, controle visual por LED de status azul no GPIO 8 (piscamento codificado por estado) e trigger AP no GPIO 9.
- **Armazenamento NVS (`Preferences.h`):** Persistência segura e não volátil de Wi-Fi, Nome do Ponto, IP Alvo, Cloud URL, Token e Intervalo de envio.

### 📁 Artefatos Criados & Atualizados
- [`firmware/include/config.h`](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/firmware/include/config.h): Definições de hardware, estados e estruturas `AppConfig` e `ProbeMetrics`.
- [`firmware/include/storage_manager.h`](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/firmware/include/storage_manager.h) / [`.cpp`](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/firmware/src/storage_manager.cpp): Gerenciamento da NVS.
- [`firmware/include/display_hud.h`](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/firmware/include/display_hud.h) / [`.cpp`](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/firmware/src/display_hud.cpp): Renderização gráfica para ST7789 e controle de LED para ESP32-C3.
- [`firmware/include/captive_portal.h`](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/firmware/include/captive_portal.h) / [`.cpp`](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/firmware/src/captive_portal.cpp): Portal Web responsivo Dark UI com scan Wi-Fi dinâmico e suporte a Captive Portal em iOS/Android/Windows.
- [`firmware/include/network_probe.h`](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/firmware/include/network_probe.h) / [`.cpp`](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/firmware/src/network_probe.cpp): Engine de probe ARP (`etharp_request`) e TCP socket RTT.
- [`firmware/include/cloud_client.h`](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/firmware/include/cloud_client.h) / [`.cpp`](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/firmware/src/cloud_client.cpp): Cliente HTTP REST com payload JSON de telemetria.
- [`firmware/src/main.cpp`](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/firmware/src/main.cpp): Loop principal com watchdog WDT de 30s e máquina de estados.
- [`docs/playbooks/firmware_flash_playbook.md`](file:///home/brunoconter/Documentos/1_C.VALE/2%20-%20PROJETOS/16_Keepalive_Foresight/docs/playbooks/firmware_flash_playbook.md): Playbook atualizado com suporte dual e comandos `esptool`.

### 🏁 Status Atual
- **Fase 1 (Edge Firmware):** 100% implementada e compilada com sucesso para `ttgo-t-display` e `esp32-c3-supermini`.
- **Próximos Passos:**
  1. Realização do upload/flash para as placas conectadas.
  2. Implementação e testes unitários do Backend FastAPI (Fase 2).



---

## 📅 Sessão 03 — 31/08/2026

### 🎯 Objetivos da Sessão
1. Resolver o bootloop e o pânico de memória (`LoadProhibited`) no hardware **LilyGO T-Display-S3 (ESP32-S3)**.
2. Validar o fluxo de provisionamento SoftAP / Captive Portal no dispositivo físico e conexão Wi-Fi real.
3. Desenvolver e homologar a **Fase 2 (Backend Cloud FastAPI & Dead Man's Switch)**.

### 🛠️ Ações Executadas
1. **Correção de Boot & Display no ESP32-S3:**
   - Identificada a necessidade de gravar `boot_app0.bin` no offset `0xe000` após erase flash.
   - Ajustado modo de gravação para `DIO` (80MHz / 16MB).
   - Eliminado uso do `TFT_eSprite` no display ST7789 paralelo de 8 bits, adotando renderização direta via `TFT_eSPI` sem consumo excessivo de heap.
   - Habilitação de energia via GPIO 15 (`PIN_POWER_ON`).
2. **Homologação Edge em Campo:**
   - A placa conectou à rede Wi-Fi local do usuário com sucesso.
   - Inicializado o ciclo de telemetria HTTP assíncrono a cada 10 segundos.
3. **Desenvolvimento Completo da Fase 2 (Backend FastAPI Cloud):**
   - Implementado ORM assíncrono SQLAlchemy com suporte a SQLite WAL (`aiosqlite`) e PostgreSQL (`asyncpg`).
   - Criados modelos `Device`, `Telemetry` e `Incident`.
   - Implementados endpoints `POST /api/v1/telemetry`, `GET /api/v1/devices`, `GET /api/v1/devices/summary`, `GET /api/v1/incidents` e `GET /health`.
   - Implementado worker assíncrono `deadman_switch_worker` com verificação de timeouts a cada 10s e auto-recovery de incidentes.
   - Desenvolvida suíte automatizada `pytest` com 8 testes cobrindo matriz booleana, ingestão, autenticação e criação de incidentes (100% aprovada).
   - Criado launcher `run_backend.py`.

### 📊 Resultados Alcançados
- **Fase 1 (Edge Firmware & Provisionamento):** 100% Concluída e homologada no hardware real.
- **Fase 2 (Backend Cloud & Dead Man's Switch):** 100% Concluída e testada.
