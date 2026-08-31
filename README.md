# Keepalive Foresight 🛰️🐔 (Agri Sentinel Probe)

<div align="center">

![Firmware PlatformIO](https://img.shields.io/badge/Firmware-PlatformIO%20%2F%20Arduino%20C%2B%2B-blue?logo=platformio)
![ESP32 Multi-Hardware](https://img.shields.io/badge/Hardware-ESP32--S3%20%7C%20ESP32--C3%20%7C%20ESP32-green?logo=espressif)
![Backend Cloud](https://img.shields.io/badge/Backend-FastAPI%20%2B%20SQLAlchemy%20WAL-teal?logo=fastapi)
![Docker Ready](https://img.shields.io/badge/Deploy-Docker%20Compose%20%28VPS%29-blue?logo=docker)
![Telegram Bot](https://img.shields.io/badge/Alerts-Telegram%20Bot%20%40ForesightAnai__bot-blue?logo=telegram)
![AI Engine](https://img.shields.io/badge/AI%20Insights-Google%20Gemini%20Flash-orange?logo=google)

**Sistema de Diagnóstico e Monitoramento de Conectividade Rural (WAN vs LAN) para Ambientes Avícolas e Gateways LoRaWAN Dragino (C.Vale)**

[Acessar Dashboard Web](http://179.197.73.80:8016/dashboard) • [Documentação](docs/sessions/SESSION_LOG.md) • [Playbook de Gravação](flash_playbook.py)

</div>

---

## 🎯 Contexto de Negócio & Motivação

Na avicultura de precisão integrada da **C.Vale**, a gestão do fornecimento de ração nos aviários depende diretamente da leitura contínua dos sensores de nível instalados nos silos, que transmitem dados via protocolo **LoRaWAN** para concentradores **Gateway Dragino**.

Quando ocorre uma interrupção na telemetria, as equipes de logística e transporte (TMS) enfrentam um dilema crítico: **a internet da granja caiu (WAN) ou o concentrador local Dragino travou (LAN)?**

Para sanar as falhas na entrega de ração, a arquitetura do **Keepalive Foresight** apoia-se em três pilares fundamentais:
1. **Comunicação Eficiente:** Plataforma centralizada com dashboard NOC em tempo real, relatórios executivos em PDF e mensageria instantânea via Telegram.
2. **Processos Otimizados:** Redesenho de fluxo de confirmação e disparo de ordens de entrega de ração integrado ao TMS logístico.
3. **Tecnologia Habilitadora:** Sondas embarcadas de baixo custo com auto-discovery por MAC, ICMP Ping nativo, e inteligência na nuvem com princípio de Dead Man's Switch.

---

## 🧠 Matriz Booleana de 4 Estados (Classificação Determinística)

A sonda edge e o motor de nuvem classificam qualquer anomalia de comunicação em **4 estados determinísticos**:

```
                              ┌──────────────────────────────────┐
                              │  Sonda Enviou Telemetria à Nuvem?│
                              └─────────────────┬────────────────┘
                                                │
                       ┌────────────────────────┴────────────────────────┐
                      SIM                                               NÃO
                       │                                                 │
          ┌────────────┴────────────┐                     ┌──────────────┴──────────────┐
          │ Gateway LAN Respondeu?  │                     │  Múltiplas Granjas Caíram?  │
          └─────┬─────────────┬─────┘                     └──────┬──────────────┬───────┘
               SIM           NÃO                                SIM            NÃO
                │             │                                  │              │
         ┌──────▼──────┐┌─────▼──────┐                    ┌──────▼──────┐┌──────▼──────┐
         │ 🟢 ONLINE   ││⚠️ FALHA LAN│                    │ ⚡ BLECAUTE  ││🚨 QUEDA WAN │
         │ Tudo 100%   ││ Dragino    │                    │  Geral      ││ Provedor    │
         │ Operacional ││ Travado    │                    │  Regional   ││ Granja      │
         └─────────────┘└────────────┘                    └─────────────┘└─────────────┘
```

| Estado | Nuvem (WAN) | Gateway Local (LAN) | Diagnóstico da Engenharia | Ação Recomendada |
| :--- | :---: | :---: | :--- | :--- |
| **`ONLINE`** | ✅ OK | ✅ OK | Link rural e concentrador LoRaWAN 100% operacionais | Nenhuma. Operação normal. |
| **`LAN_FAILURE`** | ✅ OK | ❌ Falha | Internet rural ativa, porém Gateway Dragino sem resposta | Reiniciar Gateway Dragino no aviário. |
| **`WAN_TIMEOUT`** | ❌ Timeout | ❓ Desconhecido | Sem batimento da sonda há > 2.5x o intervalo de heartbeat | Verificar roteador, fibra ou rádio do provedor. |
| **`BLACKOUT_GENERAL`** | ❌ Timeout | ❌ Timeout | Múltiplas granjas da mesma região caem no mesmo minuto | Alerta de corte de energia Copel ou queda de torre. |

---

## ⚡ Recursos Principais do Sistema

### 1. 📟 Firmware Embarcado Multi-Hardware (Edge C++)
- **Auto-Discovery Dinâmico por MAC Address:** Varredura ARP em tempo real na sub-rede `/24` (`lwip/etharp.h`) com política de 5 retries no boot e auto-reconexão caso o Gateway mude de IP pelo DHCP.
- **Ping ICMP Nativo (ESP-IDF):** Disparos assíncronos de pacotes ICMP Echo Request medindo latência com precisão de milissegundos.
- **Sincronização NTP UTC-3 Oficial:** Relógio oficial de Brasília sincronizado via servidores NTP (`a.st1.ntp.br`, `pool.ntp.org`) com cálculo de Uptime.
- **Captive Portal Responsivo (SoftAP):** Interface web moderna em `http://192.168.4.1` para configuração inicial com scan automático de redes Wi-Fi e persistência Flash NVS (`Preferences.h`).

### 2. ☁️ Backend Cloud & Dead Man's Switch (FastAPI)
- **Persistência Assíncrona Ultra-Leve:** SQLite em modo WAL (`aiosqlite`) com pegada de memória < 60MB, ideal para VPS de baixo recurso.
- **Motor Dead Man's Switch Assíncrono:** Worker em background verificando o relógio de silêncio e histerese anti-flapping.
- **Auto-Recovery:** Fechamento automático de incidentes e envio de notificação verde assim que a sonda restabelece comunicação.

### 3. 🖥️ Painel Web Dashboard NOC em Tempo Real (`/dashboard`)
- **Acesso Direto:** `http://179.197.73.80:8016/dashboard`
- **Dark Mode Moderno:** Interface de alta densidade informativa com auto-sync a cada 5 segundos.
- **Seleção Dinâmica por Checkboxes:** Permite filtrar e selecionar pontos específicos para geração de laudos ou emitir relatórios individuais por linha.
- **Favicon SVG:** Vetor estilizado integrado (`/static/favicon.svg`).
- **Módulo de Administração:** Botão protegido por senha (`blurbang`) para zerar a base de dados no início oficial de produção.

### 4. 📑 Relatórios Executivos em PDF de 7 e 30 Dias
- **1 Ponto por Página (`PageBreak`):** Laudos individuais ou consolidados construídos com `reportlab`.
- **Séries Temporais com Matplotlib:** Curvas históricas da latência no Gateway (ms) e intensidade do sinal Wi-Fi (dBm).
- **Parecer Técnico Corporativo:** Análise elaborada com modelo `gemini-3.6-flash` em tom 100% humano de Engenharia de Redes C.Vale (sem termos de IA).

### 5. 🤖 Integração com Hermes Agent (VPS Hostinger)
- **Skill Especializada:** Instalada no diretório `/root/projetos/hermes-agent/config/skills/devops/keepalive-foresight/SKILL.md`.
- **Interação em Linguagem Natural:** O Hermes Agent consulta as APIs REST do Keepalive Foresight e responde dúvidas sobre status das granjas, gateways offline e resumos de saúde da rede.

---

## 🛠️ Tabela de Hardwares Suportados

| Opção no Playbook | Modelo da Placa | Processador / Clock | Display & Feedback | Pinos de Controle |
| :--- | :--- | :--- | :--- | :--- |
| **`[1]`** | **LilyGO T-Display-S3** | ESP32-S3 Dual-Core LX7 (240MHz) | Display ST7789 320x170 Paralelo (8-bit) | Power: `IO15` • BL: `IO38` • AP: `IO14` |
| **`[2]`** | **LilyGO T-Display Clássico** | ESP32 D0WDQ6 Dual-Core (240MHz) | Display ST7789 240x135 SPI DMA | Backlight: `IO4` • AP: `IO35` |
| **`[3]`** | **ESP32-C3 SuperMini** | ESP32-C3 Single-Core RISC-V (160MHz) | Sem Tela • LED Diagnóstico Azul no `IO8` | LED: `IO8` (Active LOW) • AP/Boot: `IO9` |

---

## 🚀 Guia Rápido de Instalação & Execução

### 1. Clonar o Repositório no seu Computador / Notebook

```bash
# Via SSH (Recomendado)
git clone git@github.com:brunocorisco86/agri-sentinel-probe.git
cd agri-sentinel-probe

# Ou via HTTPS
git clone https://github.com/brunocorisco86/agri-sentinel-probe.git
cd agri-sentinel-probe
```

### 2. Configurar o Ambiente Python

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 3. Gravar Qualquer Placa ESP32 via Playbook Interativo

```bash
python3 flash_playbook.py
```

O playbook detecta automaticamente as portas `/dev/ttyACM*` ou `/dev/ttyUSB*`, compila o firmware no PlatformIO e realiza o upload via `esptool`.

---

## 🐳 Execução do Backend & Deploy na VPS

### Localmente (Desenvolvimento):
```bash
python3 run_backend.py
# Acesso local: http://localhost:8000/dashboard
```

### Em Produção (Docker Compose na VPS):
```bash
docker compose up -d --build
# Acesso em produção: http://179.197.73.80:8016/dashboard
```

---

## 🧪 Suíte de Testes Automatizados

O projeto conta com suíte de testes com **13/13 testes aprovados** cobrindo classificação booleana, ingestão de telemetria, autenticação Bearer Token, mensageria Telegram, geração de PDF e reset administrativo:

```bash
PYTHONPATH=backend pytest backend/tests/ -v
```

---

## 📚 Documentação & Playbooks

* 📜 **[Diário de Bordo & Logs de Sessões (`docs/sessions/SESSION_LOG.md`)](docs/sessions/SESSION_LOG.md)**
* 🗺️ **[Roadmap de Implementação (`ROADMAP.md`)](ROADMAP.md)**
* 📖 **[Documento Mestre de Arquitetura (`idea.md`)](idea.md)**
* 🚀 **[Playbook de Comissionamento da VPS (`docs/playbooks/vps_commissioning_playbook.md`)](docs/playbooks/vps_commissioning_playbook.md)**
* ⚡ **[Playbook de Flash do Firmware (`docs/playbooks/firmware_flash_playbook.md`)](docs/playbooks/firmware_flash_playbook.md)**
* 🤖 **[Skill do Hermes Agent (`docs/hermes_skills/keepalive-foresight/SKILL.md`)](docs/hermes_skills/keepalive-foresight/SKILL.md)**

---

<div align="center">
  <sub>Keepalive Foresight • Desenvolvido para Confiabilidade e Excelência em Conectividade Rural C.Vale</sub>
</div>
