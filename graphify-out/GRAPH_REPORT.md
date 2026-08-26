# Graph Report - 16_Keepalive_Foresight  (2026-08-26)

## Corpus Check
- Corpus is ~3,857 words - fits in a single context window. You may not need a graph.

## Summary
- 12 nodes · 14 edges · 3 communities (2 shown, 1 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 1,200 input · 850 output

## Community Hubs (Navigation)
- Documentação & SSOT
- Firmware ESP32 & Rede Local
- Backend Cloud & Motor Deadman

## God Nodes (most connected - your core abstractions)
1. `FastAPI Cloud Backend` - 6 edges
2. `ESP32 Sentinel Firmware` - 5 edges
3. `Architecture SSOT (idea.md)` - 4 edges
4. `Docker Compose Stack` - 3 edges
5. `ARP & TCP Probe Engine` - 2 edges
6. `PostgreSQL / SQLite Storage` - 2 edges
7. `Project Overview` - 1 edges
8. `TFT_eSprite HUD Display` - 1 edges
9. `SoftAP & Captive Portal Web Server` - 1 edges
10. `Dead Man's Switch Engine` - 1 edges

## Surprising Connections (you probably didn't know these)
- `Architecture SSOT (idea.md)` --specifies--> `FastAPI Cloud Backend`  [EXTRACTED]
  idea.md → backend/requirements.txt
- `Architecture SSOT (idea.md)` --specifies--> `Docker Compose Stack`  [EXTRACTED]
  idea.md → docker/docker-compose.yml
- `Architecture SSOT (idea.md)` --specifies--> `ESP32 Sentinel Firmware`  [EXTRACTED]
  idea.md → firmware/platformio.ini
- `ESP32 Sentinel Firmware` --sends_telemetry--> `FastAPI Cloud Backend`  [EXTRACTED]
  firmware/platformio.ini → backend/requirements.txt
- `FastAPI Cloud Backend` --persists_to--> `PostgreSQL / SQLite Storage`  [EXTRACTED]
  backend/requirements.txt → docker/docker-compose.yml

## Communities (3 total, 1 thin omitted)

### Community 0 - "Documentação & SSOT"
Cohesion: 0.50
Nodes (5): FastAPI Cloud Backend, PostgreSQL / SQLite Storage, Dead Man's Switch Engine, Docker Compose Stack, Telegram Bot Alerter

### Community 1 - "Firmware ESP32 & Rede Local"
Cohesion: 0.40
Nodes (5): TFT_eSprite HUD Display, Dragino LoRaWAN Gateway (Target), ESP32 Sentinel Firmware, ARP & TCP Probe Engine, SoftAP & Captive Portal Web Server

## Knowledge Gaps
- **6 isolated node(s):** `Project Overview`, `TFT_eSprite HUD Display`, `SoftAP & Captive Portal Web Server`, `Dead Man's Switch Engine`, `Telegram Bot Alerter` (+1 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ESP32 Sentinel Firmware` connect `Firmware ESP32 & Rede Local` to `Documentação & SSOT`, `Backend Cloud & Motor Deadman`?**
  _High betweenness centrality (0.600) - this node is a cross-community bridge._
- **Why does `FastAPI Cloud Backend` connect `Documentação & SSOT` to `Firmware ESP32 & Rede Local`, `Backend Cloud & Motor Deadman`?**
  _High betweenness centrality (0.500) - this node is a cross-community bridge._
- **Why does `Architecture SSOT (idea.md)` connect `Backend Cloud & Motor Deadman` to `Documentação & SSOT`, `Firmware ESP32 & Rede Local`?**
  _High betweenness centrality (0.227) - this node is a cross-community bridge._
- **What connects `Project Overview`, `TFT_eSprite HUD Display`, `SoftAP & Captive Portal Web Server` to the rest of the system?**
  _6 weakly-connected nodes found - possible documentation gaps or missing edges._