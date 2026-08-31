---
name: keepalive-foresight
description: Monitora a saúde e telemetria das sondas de conectividade rural (Keepalive Foresight / Agri-Sentinel Probe) nas granjas e residências da C.Vale. Consulta status de links WAN, saúde dos Gateways Dragino LAN e dispara relatórios executivos.
---

# Keepalive Foresight - Sondas de Conectividade Rural C.Vale

## Quando Acionar
Utilize esta skill sempre que o usuário perguntar sobre:
- Saúde das granjas, aviários ou residências monitoradas ("Como estão as granjas?", "Qual o status da sonda Granja 01?").
- Status de conectividade do Gateway Dragino (LoRaWAN) ou alvos locais.
- Relatórios de incidentes, quedas de internet rural, perda de pacotes ou latência.
- Solicitação para disparar relatório no Telegram ou consultar o Dashboard NOC.

## Endpoints da API (Produção na VPS Hostinger)
A API do Keepalive Foresight roda na mesma VPS na porta **8016** (ou acessível via rede Docker interna `http://keepalive-api:8000` / `http://179.197.73.80:8016`):

- **Resumo Geral (KPIs & Lista de Dispositivos):**
  ```bash
  curl -s http://179.197.73.80:8016/api/v1/devices/summary
  ```
- **Histórico de Incidentes:**
  ```bash
  curl -s http://179.197.73.80:8016/api/v1/incidents
  ```
- **Disparar Relatório Executivo no Telegram:**
  ```bash
  curl -s -X POST http://179.197.73.80:8016/api/v1/reports/daily-telegram
  ```
- **Dashboard Web NOC:** `http://179.197.73.80:8016/dashboard`

## Procedimento de Consulta & Geração de Relatório

### 1. Consultar a API
Execute a chamada `curl` para obter o JSON consolidado:
```bash
curl -s http://179.197.73.80:8016/api/v1/devices/summary
```

### 2. Interpretar a Matriz Booleana de 4 Estados
- **`ONLINE` (🟢 100% Operacional):** Link de internet rural ativo E Gateway Dragino respondendo a Ping ICMP local (< 10ms).
- **`LAN_FAILURE` (⚠️ Falha no Gateway Dragino):** Sonda consegue falar com a nuvem, mas o Gateway Dragino está travado ou desligado na granja (necessita reinício do Dragino).
- **`WAN_TIMEOUT` (🚨 Queda de Link WAN):** Sonda sem enviar telemetria há mais de 2.5x o intervalo configurado (queda de fibra/rádio da operadora ou falta de energia).
- **`BLACKOUT_GENERAL` (⚡ Blecaute Rural):** Múltiplas granjas na mesma região caem no mesmo minuto.

### 3. Formatar a Resposta para o Usuário
Apresente um resumo claro e executivo:
- **Cabeçalho:** Total de granjas, percentual de saúde (% online) e horário da consulta em fuso **BRT (UTC-3)**.
- **Destaques:** Se houver falha de Dragino ou queda WAN, aponte exatamente o nome da granja, IP e tempo offline.
- **Tabela Consolidada (se solicitado):** Ponto, Status, Wi-Fi RSSI, Latência e Uptime.

## Exemplo de Resposta
> "📊 **Relatório de Conectividade Rural Keepalive Foresight (08:30 BRT):**
> • **Total de Pontos:** 1 sonda ativa
> • **Status Geral:** 🟢 100% Operacional (Índice de Saúde: 100%)
>
> 📍 **Minha Casa / Granja:**
> • **ID:** `SENTINEL-6E38` | **IP Dragino:** `192.168.1.111` (MAC: `5C:CF:7F:B7:59:D2`)
> • **Latência Ping LAN:** `4.0 ms` | **Sinal Wi-Fi:** `-33 dBm` (Excelente)
> • **Uptime:** `1h 45m`
>
> 🔗 Acesse o Dashboard em tempo real: http://179.197.73.80:8016/dashboard"
