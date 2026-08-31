#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Keepalive Foresight - Simulador E2E de Sondas Multi-Ponto & Injetor de Falhas
Emula o envio de telemetria e testes de integridade para granjas e residencias.
"""

import sys
import time
import requests
import random

CYAN = "[96m"
GREEN = "[92m"
YELLOW = "[93m"
RED = "[91m"
BOLD = "[1m"
RESET = "[0m"

API_URL = "http://localhost:8000/api/v1/telemetry"
AUTH_TOKEN = "keepalive-secret-token-123"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {AUTH_TOKEN}"
}

VIRTUAL_PROBES = [
    {
        "device_id": "SENTINEL-GR01",
        "device_mac": "C0:4E:30:AA:11:01",
        "location_name": "Granja 01 - Aviario 1",
        "hardware_model": "LilyGO T-Display-S3",
        "wifi_ssid": "Granja_01_WiFi",
        "local_target_enabled": True,
        "local_target_ip": "192.168.1.50",
        "local_target_online": True,
        "local_target_rtt_ms": 1.4,
        "wan_online": True,
        "uptime_sec": 1240,
        "check_interval_seconds": 300
    },
    {
        "device_id": "SENTINEL-GR02",
        "device_mac": "C0:4E:30:AA:11:02",
        "location_name": "Granja 02 - Aviario 2",
        "hardware_model": "ESP32-C3 SuperMini",
        "wifi_ssid": "Granja_02_WiFi",
        "local_target_enabled": True,
        "local_target_ip": "192.168.2.50",
        "local_target_online": True,
        "local_target_rtt_ms": 2.1,
        "wan_online": True,
        "uptime_sec": 3600,
        "check_interval_seconds": 300
    },
    {
        "device_id": "SENTINEL-CASA",
        "device_mac": "C0:4E:30:AA:11:03",
        "location_name": "Minha Casa (Residencial)",
        "hardware_model": "LilyGO T-Display-S3",
        "wifi_ssid": "Fibra_Casa_5G",
        "local_target_enabled": False,
        "local_target_ip": "",
        "local_target_online": True,
        "local_target_rtt_ms": 0.0,
        "wan_online": True,
        "uptime_sec": 7200,
        "check_interval_seconds": 300
    },
    {
        "device_id": "SENTINEL-SEDE",
        "device_mac": "C0:4E:30:AA:11:04",
        "location_name": "Escritorio Central C.Vale",
        "hardware_model": "LilyGO T-Display-S3",
        "wifi_ssid": "CVale_Corp",
        "local_target_enabled": False,
        "local_target_ip": "",
        "local_target_online": True,
        "local_target_rtt_ms": 0.0,
        "wan_online": True,
        "uptime_sec": 86400,
        "check_interval_seconds": 300
    }
]

def send_probe_cycle(probe):
    if not probe["wan_online"]:
        print(f"  {RED}✕ [{probe['location_name']}] Telemetria bloqueada (Simulando Queda de WAN){RESET}")
        return False
        
    payload = {
        "device_id": probe["device_id"],
        "device_mac": probe["device_mac"],
        "location_name": probe["location_name"],
        "hardware_model": probe["hardware_model"],
        "firmware_version": "1.0.0",
        "uptime_seconds": probe["uptime_sec"],
        "check_interval_seconds": probe["check_interval_seconds"],
        "wifi_ssid": probe["wifi_ssid"],
        "wifi_rssi_dbm": random.randint(-65, -40),
        "local_target_enabled": probe["local_target_enabled"],
        "local_target_ip": probe["local_target_ip"],
        "local_target_online": probe["local_target_online"],
        "local_target_rtt_ms": probe["local_target_rtt_ms"] if probe["local_target_online"] else -1.0,
        "free_heap_bytes": random.randint(270000, 290000)
    }
    
    try:
        res = requests.post(API_URL, json=payload, headers=HEADERS, timeout=3.0)
        if res.status_code == 200:
            lan_status = "LAN OK" if probe["local_target_online"] else f"{RED}LAN FALHA{RESET}"
            print(f"  {GREEN}✓ [{probe['location_name']}] Telemetria enviada com sucesso | {lan_status} | HTTP 200{RESET}")
            return True
        else:
            print(f"  {RED}✕ [{probe['location_name']}] Erro na API: {res.status_code} - {res.text}{RESET}")
            return False
    except Exception as e:
        print(f"  {RED}✕ [{probe['location_name']}] Falha de conexao com a API: {e}{RESET}")
        return False

def print_menu():
    print(f"\n{CYAN}{BOLD}==============================================================={RESET}")
    print(f"{CYAN}{BOLD}   🧪 KEEPALIVE FORESIGHT - SIMULADOR MULTI-PONTO E2E          {RESET}")
    print(f"{CYAN}{BOLD}==============================================================={RESET}")
    print(f"  {CYAN}[1]{RESET} Disparar Telemetria Normal de Todas as 4 Sondas (100% OK)")
    print(f"  {CYAN}[2]{RESET} Injetar {YELLOW}Falha no Gateway Dragino{RESET} da Granja 01")
    print(f"  {CYAN}[3]{RESET} Injetar {RED}Queda de Link WAN (Provedor){RESET} na Granja 02")
    print(f"  {CYAN}[4]{RESET} Simular {RED}Blecaute Geral{RESET} em Todas as Granjas")
    print(f"  {CYAN}[5]{RESET} {GREEN}Normalizar / Auto-Recovery Geral{RESET}")
    print(f"  {CYAN}[6]{RESET} Executar Modo Loop Contínuo (Heartbeats automáticos a cada 5s)")
    print(f"  {CYAN}[0]{RESET} Sair")

def main():
    while True:
        print_menu()
        choice = input(f"\n{BOLD}Escolha uma acao [0-6]: {RESET}").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            print(f"\n{CYAN}Enviando telemetria de todas as sondas...{RESET}")
            for p in VIRTUAL_PROBES:
                p["uptime_sec"] += 10
                send_probe_cycle(p)
        elif choice == "2":
            print(f"\n{YELLOW}⚡ Injetando FALHA LAN no Dragino da Granja 01...{RESET}")
            VIRTUAL_PROBES[0]["local_target_online"] = False
            send_probe_cycle(VIRTUAL_PROBES[0])
        elif choice == "3":
            print(f"\n{RED}⚡ Injetando QUEDA WAN na Granja 02 (Sem resposta na nuvem)...{RESET}")
            VIRTUAL_PROBES[1]["wan_online"] = False
            print(f"{YELLOW}A sonda da Granja 02 parou de enviar batimentos. O Dead Man's Switch detectara timeout.{RESET}")
        elif choice == "4":
            print(f"\n{RED}⚡ Injetando BLECAUTE GERAL (Todas as sondas paradas)...{RESET}")
            for p in VIRTUAL_PROBES:
                p["wan_online"] = False
        elif choice == "5":
            print(f"\n{GREEN}✓ Normalizando todas as sondas (Auto-Recovery)...{RESET}")
            for p in VIRTUAL_PROBES:
                p["wan_online"] = True
                p["local_target_online"] = True
                p["uptime_sec"] += 10
                send_probe_cycle(p)
        elif choice == "6":
            print(f"\n{CYAN}Iniciando Loop Continuo (Pressione Ctrl+C para parar)...{RESET}\n")
            try:
                while True:
                    for p in VIRTUAL_PROBES:
                        p["uptime_sec"] += 5
                        send_probe_cycle(p)
                    time.sleep(5)
            except KeyboardInterrupt:
                print(f"\n{YELLOW}Loop cancelado.{RESET}")

if __name__ == "__main__":
    main()
