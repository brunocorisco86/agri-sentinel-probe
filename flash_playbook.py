#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Keepalive Foresight - Playbook Interativo de Gravacao Flash & Comissionamento
Suporte Multi-Hardware com Auto-Detecção:
  • LilyGO T-Display-S3 (ESP32-S3)
  • LilyGO T-Display Clássico (ESP32)
  • ESP32-C3 SuperMini (RISC-V)
"""

import os
import sys
import glob
import time
import subprocess
import getpass
import shutil
from pathlib import Path

CYAN = "[96m"
GREEN = "[92m"
YELLOW = "[93m"
RED = "[91m"
BOLD = "[1m"
DIM = "[2m"
RESET = "[0m"

PROJECT_ROOT = Path(__file__).resolve().parent
FIRMWARE_DIR = PROJECT_ROOT / "firmware"
BUILD_DIR = FIRMWARE_DIR / ".pio" / "build"
BOOT_APP0 = FIRMWARE_DIR / "boot_app0.bin"

HARDWARE_CONFIGS = {
    "1": {
        "name": "LilyGO T-Display-S3 (ESP32-S3 Dual-Core LX7)",
        "env": "t-display-s3",
        "chip": "esp32s3",
        "bootloader_offset": "0x0",
        "flash_mode": "dio",
        "flash_size": "16MB",
        "flash_freq": "80m",
        "display": "ST7789 320x170 8-bit Parallel (Power PIN 15, BL 38)",
        "buttons_guide": (
            f"{BOLD}Instrucoes de Hardware & Botoes (LilyGO T-Display-S3):{RESET}\n"
            f"  • {CYAN}Botao KEY / Lateral (GPIO 14):{RESET} Segure por 3 segundos para forcar o Modo Captive Portal (Wi-Fi de configuracao).\n"
            f"  • {CYAN}Botao BOOT (GPIO 0):{RESET} Se o upload falhar, segure BOOT enquanto clica no botao RESET lateral para entrar em modo bootloader manual.\n"
            f"  • {CYAN}Display ST7789 (320x170):{RESET} Apos a gravacao, o display acendera exibindo o HUD em alta resolucao com diagnostico em tempo real."
        )
    },
    "2": {
        "name": "LilyGO T-Display Classico (ESP32 D0WDQ6)",
        "env": "ttgo-t-display",
        "chip": "esp32",
        "bootloader_offset": "0x1000",
        "flash_mode": "dio",
        "flash_size": "4MB",
        "flash_freq": "40m",
        "display": "ST7789 240x135 SPI DMA (Backlight GPIO 4)",
        "buttons_guide": (
            f"{BOLD}Instrucoes de Hardware & Botoes (LilyGO T-Display Classico):{RESET}\n"
            f"  • {CYAN}Botao Superior (GPIO 35):{RESET} Segure por 3 segundos para forcar o Modo Captive Portal.\n"
            f"  • {CYAN}Botao Inferior (GPIO 0 / Boot):{RESET} Segure durante o reset se o upload falhar.\n"
            f"  • {CYAN}Display ST7789 (240x135):{RESET} Exibe o HUD em tempo real."
        )
    },
    "3": {
        "name": "ESP32-C3 SuperMini (RISC-V Single-Core)",
        "env": "esp32-c3-supermini",
        "chip": "esp32c3",
        "bootloader_offset": "0x0",
        "flash_mode": "dio",
        "flash_size": "4MB",
        "flash_freq": "40m",
        "display": "Sem Display (LED de Status Azul no GPIO 8)",
        "buttons_guide": (
            f"{BOLD}Instrucoes de Hardware & Gravacao Flash (ESP32-C3 SuperMini):{RESET}\n"
            f"  • {YELLOW}{BOLD}Como Colocar em Modo Download / Bootloader para Gravar:{RESET}\n"
            f"      1. Mantenha pressionado o botao {CYAN}BOOT (GPIO 9){RESET}.\n"
            f"      2. De um clique rapido no botao {CYAN}RESET (RST){RESET}.\n"
            f"      3. Solte o botao {CYAN}BOOT{RESET}.\n"
            f"      (Ou conecte o cabo USB no computador mantendo o botao BOOT pressionado).\n"
            f"  • {CYAN}Apos a Gravacao (Operacao Normal):{RESET}\n"
            f"      - Segure {CYAN}BOOT por 3 segundos{RESET} para abrir o Captive Portal Wi-Fi.\n"
            f"      - {CYAN}LED Azul (GPIO 8):{RESET} Pisca rapido no provisionamento, pulso no envio e flash duplo se houver erro."
        )
    }
}

def print_banner():
    print(f"\n{CYAN}{BOLD}==============================================================={RESET}")
    print(f"{CYAN}{BOLD}   ⚡ KEEPALIVE FORESIGHT - FLASH & COMMISSIONING PLAYBOOK     {RESET}")
    print(f"{CYAN}{BOLD}   Plataforma de Monitoramento & Sondas WAN/LAN (C.Vale)       {RESET}")
    print(f"{CYAN}{BOLD}==============================================================={RESET}\n")

def find_esptool():
    candidates = [
        Path.home() / ".local/share/pipx/venvs/esptool/bin/esptool",
        Path.home() / ".local/bin/esptool",
        Path.home() / ".local/bin/esptool.py",
        shutil.which("esptool"),
        shutil.which("esptool.py"),
    ]
    for c in candidates:
        if c and Path(c).exists() and os.access(str(c), os.X_OK):
            return str(c)
    return "esptool.py"

def find_serial_ports():
    ports = sorted(glob.glob("/dev/ttyACM*") + glob.glob("/dev/ttyUSB*"))
    return ports

def fix_port_permission(port):
    print(f"\n{YELLOW}🔍 Verificando permissoes de acesso para {port}...{RESET}")
    if os.access(port, os.R_OK | os.W_OK):
        print(f"{GREEN}✓ Permissao de leitura e escrita confirmada em {port}!{RESET}")
        return True
    
    print(f"{RED}⚠ Sem permissao direta para acessar {port}.{RESET}")
    print(f"{YELLOW}Vamos ajustar as permissoes via sudo (chmod 666 e grupo dialout).{RESET}")
    
    password = getpass.getpass("Digite sua senha de sudo (nao sera exibida na tela): ")
    if not password:
        print(f"{RED}❌ Senha nao fornecida.{RESET}")
        return False
    
    user = os.environ.get("USER", "brunoconter")
    commands = [
        f"echo '{password}' | sudo -S chmod 666 {port}",
        f"echo '{password}' | sudo -S usermod -a -G dialout {user}",
        f"echo '{password}' | sudo -S udevadm control --reload-rules",
    ]
    
    for cmd in commands:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if res.returncode != 0 and "incorrect password" in res.stderr.lower():
            print(f"{RED}❌ Senha sudo incorreta.{RESET}")
            return False
            
    if os.access(port, os.R_OK | os.W_OK):
        print(f"{GREEN}✓ Permissoes aplicadas com sucesso em {port}!{RESET}")
        return True
    else:
        print(f"{RED}❌ Nao foi possivel liberar {port}. Tente executar: sudo chmod 666 {port}{RESET}")
        return False

def detect_chip_type(esptool_bin, port):
    cmd = [esptool_bin, "-p", port, "chip-id"]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        out = (res.stdout + res.stderr).lower()
        if "esp32-s3" in out or "esp32s3" in out:
            return "1"
        elif "esp32-c3" in out or "esp32c3" in out:
            return "3"
        elif "esp32" in out:
            return "2"
    except Exception:
        pass
    return None

def select_hardware(detected_key=None):
    print(f"{BOLD}Escolha a placa que voce deseja gravar:{RESET}")
    print(f"  {CYAN}[1]{RESET} {BOLD}LilyGO T-Display-S3{RESET} (ESP32-S3 Dual-Core LX7 - 320x170)")
    print(f"  {CYAN}[2]{RESET} {BOLD}LilyGO T-Display Classico{RESET} (ESP32 D0WDQ6 - 240x135)")
    print(f"  {CYAN}[3]{RESET} {BOLD}ESP32-C3 SuperMini{RESET} (RISC-V compacto com LED azul GPIO 8)")
    
    default_opt = detected_key if detected_key in HARDWARE_CONFIGS else "1"
    
    while True:
        choice = input(f"\n{BOLD}Selecione a opcao [1-3] (Sugerido: {default_opt}): {RESET}").strip()
        if choice == "":
            choice = default_opt
        if choice in HARDWARE_CONFIGS:
            return HARDWARE_CONFIGS[choice]
        print(f"{RED}Opcao invalida. Digite 1, 2 ou 3.{RESET}")

def select_port(ports):
    if not ports:
        print(f"\n{RED}⚠ Nenhuma placa serial (/dev/ttyACM* ou /dev/ttyUSB*) foi detectada!{RESET}")
        print(f"{YELLOW}Conecte a placa via cabo USB-C e pressione Enter para tentar novamente.{RESET}")
        input("Pressione Enter...")
        ports = find_serial_ports()
        if not ports:
            manual = input(f"{YELLOW}Digite a porta manualmente (ex: /dev/ttyACM0): {RESET}").strip()
            return manual if manual else "/dev/ttyACM0"
            
    if len(ports) == 1:
        selected = ports[0]
        print(f"\n{GREEN}✓ Porta serial detectada automaticamente: {BOLD}{selected}{RESET}")
        confirm = input(f"Usar esta porta? [S/n]: ").strip().lower()
        if confirm in ["", "s", "sim", "y", "yes"]:
            return selected
            
    print(f"\n{BOLD}Portas seriais encontradas:{RESET}")
    for idx, p in enumerate(ports, 1):
        print(f"  [{idx}] {p}")
    while True:
        choice = input(f"Selecione o numero da porta [1-{len(ports)}]: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(ports):
            return ports[int(choice)-1]
        print(f"{RED}Opcao invalida.{RESET}")

def check_or_compile(hw_config):
    env = hw_config["env"]
    bin_dir = BUILD_DIR / env
    bootloader = bin_dir / "bootloader.bin"
    partitions = bin_dir / "partitions.bin"
    firmware = bin_dir / "firmware.bin"
    
    need_build = not (bootloader.exists() and partitions.exists() and firmware.exists())
    
    if need_build:
        print(f"\n{YELLOW}⚙ Binarios para {hw_config['name']} nao encontrados. Iniciando compilacao...{RESET}")
    else:
        print(f"\n{GREEN}✓ Binarios compilados encontrados em:{RESET} {bin_dir}")
        rebuild = input(f"Deseja recompilar o codigo antes de gravar? [s/N]: ").strip().lower()
        need_build = rebuild in ["s", "sim", "y", "yes"]
        
    if need_build:
        pio_bin = shutil.which("pio") or str(Path.home() / ".local/bin/pio")
        cmd = [pio_bin, "run", "-d", str(FIRMWARE_DIR), "-e", env]
        print(f"\n{CYAN}Executando: {' '.join(cmd)}{RESET}")
        res = subprocess.run(cmd)
        if res.returncode != 0:
            print(f"\n{RED}❌ Falha na compilacao do PlatformIO! Verifique os erros acima.{RESET}")
            sys.exit(1)
        print(f"\n{GREEN}✓ Compilacao concluida com sucesso!{RESET}")
        
    return {
        "bootloader": str(bootloader),
        "partitions": str(partitions),
        "boot_app0": str(BOOT_APP0),
        "firmware": str(firmware)
    }

def flash_chip(esptool_bin, port, hw_config, bins, erase_first=False):
    chip = hw_config["chip"]
    boot_offset = hw_config["bootloader_offset"]
    f_mode = hw_config.get("flash_mode", "dio")
    f_size = hw_config.get("flash_size", "4MB")
    f_freq = hw_config.get("flash_freq", "40m")
    
    if chip == "esp32c3":
        print(f"\n{YELLOW}{BOLD}┌─────────────────────────────────────────────────────────────┐{RESET}")
        print(f"{YELLOW}{BOLD}│ 📌 PROCEDIMENTO PARA ENTRAR EM MODO GRAVACAO (ESP32-C3):    │{RESET}")
        print(f"{YELLOW}{BOLD}│                                                             │{RESET}")
        print(f"{YELLOW}{BOLD}│ 1. Mantenha pressionado o botao BOOT (GPIO 9).              │{RESET}")
        print(f"{YELLOW}{BOLD}│ 2. De um clique rapido no botao RESET (RST).                │{RESET}")
        print(f"{YELLOW}{BOLD}│ 3. Solte o botao BOOT.                                      │{RESET}")
        print(f"{YELLOW}{BOLD}│                                                             │{RESET}")
        print(f"{YELLOW}{BOLD}│ (Ou: segure o botao BOOT enquanto pluga o cabo USB no PC)   │{RESET}")
        print(f"{YELLOW}{BOLD}└─────────────────────────────────────────────────────────────┘{RESET}\n")
        input(f"{CYAN}Pressione [ENTER] quando o ESP32-C3 estiver em modo Bootloader para gravar...{RESET}")
    
    if erase_first:
        print(f"\n{YELLOW}🧹 Executando apagamento completo da Flash (Erase Flash)...{RESET}")
        erase_cmd = [esptool_bin, "-p", port, "-b", "460800", "--chip", chip, "erase-flash"]
        print(f"{DIM}Comando: {' '.join(erase_cmd)}{RESET}")
        res = subprocess.run(erase_cmd)
        if res.returncode != 0:
            erase_cmd[-1] = "erase_flash"
            res = subprocess.run(erase_cmd)
            if res.returncode != 0:
                print(f"\n{RED}❌ Erro durante o erase_flash. Verifique a conexao do cabo ou feche o monitor serial.{RESET}")
                return False
            
    print(f"\n{CYAN}⚡ Gravando Firmware via esptool ({hw_config['name']})...{RESET}")
    print(f"{DIM}Parametros: Chip={chip}, Mode={f_mode}, Size={f_size}, Freq={f_freq}{RESET}")
    
    flash_cmd = [
        esptool_bin,
        "-p", port,
        "-b", "460800",
        "--chip", chip,
        "write-flash",
        "--flash-mode", f_mode,
        "--flash-size", f_size,
        "--flash-freq", f_freq,
        boot_offset, bins["bootloader"],
        "0x8000", bins["partitions"],
        "0xe000", bins["boot_app0"],
        "0x10000", bins["firmware"]
    ]
    
    print(f"{DIM}Comando: {' '.join(flash_cmd)}{RESET}\n")
    res = subprocess.run(flash_cmd)
    
    if res.returncode != 0:
        # Fallback para opcoes antigas com underscore
        flash_cmd[6] = "write_flash"
        flash_cmd[7] = "--flash_mode"
        flash_cmd[9] = "--flash_size"
        flash_cmd[11] = "--flash_freq"
        res = subprocess.run(flash_cmd)
    
    if res.returncode == 0:
        print(f"\n{GREEN}{BOLD}🎉 GRAVACAO CONCLUIDA COM SUCESSO! 🎉{RESET}")
        return True
    else:
        print(f"\n{RED}{BOLD}❌ Falha na gravacao do firmware.{RESET}")
        print(f"{YELLOW}Dica: Feche outros monitores seriais ou segure BOOT ao conectar.{RESET}")
        return False

def open_serial_monitor(port):
    print(f"\n{CYAN}Iniciando Monitor Serial a 115200 baud em {port}...{RESET}")
    print(f"{YELLOW}(Pressione Ctrl+C ou Ctrl+] para sair do monitor){RESET}\n")
    time.sleep(1)
    
    pio_bin = shutil.which("pio") or str(Path.home() / ".local/bin/pio")
    try:
        subprocess.run([pio_bin, "device", "monitor", "-b", "115200", "-p", port])
    except KeyboardInterrupt:
        print(f"\n{GREEN}Monitor serial encerrado.{RESET}")

def main():
    print_banner()
    esptool_bin = find_esptool()
    print(f"{DIM}Utilitario esptool: {esptool_bin}{RESET}")
    
    ports = find_serial_ports()
    selected_port = select_port(ports)
    
    if not fix_port_permission(selected_port):
        print(f"{RED}Impossivel prosseguir sem permissao de acesso a porta.{RESET}")
        sys.exit(1)
        
    detected_chip = detect_chip_type(esptool_bin, selected_port)
    if detected_chip:
        print(f"{GREEN}✓ Chip detectado automaticamente na porta: {BOLD}{HARDWARE_CONFIGS[detected_chip]['name']}{RESET}\n")
        
    hw_config = select_hardware(detected_chip)
    print(f"\n{GREEN}✓ Placa selecionada: {BOLD}{hw_config['name']}{RESET}")
    
    print(f"\n" + "-"*63)
    print(hw_config["buttons_guide"])
    print("-"*63 + "\n")
    
    bins = check_or_compile(hw_config)
    
    print(f"\n{BOLD}Opcoes de Gravacao:{RESET}")
    print(f"  {CYAN}[1]{RESET} {BOLD}Gravacao Completa via esptool{RESET} (Com boot_app0 OTA + NVS limpa)")
    print(f"  {CYAN}[2]{RESET} {BOLD}Erase Flash + Gravacao Limpa{RESET} ({YELLOW}Recomendado{RESET} para primeiro uso)")
    print(f"  {CYAN}[3]{RESET} Apenas Abrir Monitor Serial")
    
    choice = input(f"\n{BOLD}Escolha uma opcao [1-3] (Padrao: 2): {RESET}").strip()
    if choice == "":
        choice = "2"
        
    if choice == "3":
        open_serial_monitor(selected_port)
        return
        
    erase = (choice == "2")
    success = flash_chip(esptool_bin, selected_port, hw_config, bins, erase_first=erase)
    
    if success:
        print(f"\n{CYAN}{BOLD}📲 PROXIMOS PASSOS (PROVISIONAMENTO DO PONTO):{RESET}")
        print(f"  1. A placa inicializou e gerou o Wi-Fi: {BOLD}Keepalive-SENTINEL-XXXX{RESET}")
        print(f"  2. Conecte seu smartphone ou PC nesta rede Wi-Fi.")
        print(f"  3. O navegador abrira automaticamente em {BOLD}http://192.168.4.1{RESET}")
        print(f"  4. Cadastre o nome do local (Ex: 'Minha Casa' ou 'Granja 01'), a senha do Wi-Fi e salve.\n")
        
        mon = input(f"Deseja abrir o monitor serial agora para acompanhar o boot? [S/n]: ").strip().lower()
        if mon in ["", "s", "sim", "y", "yes"]:
            open_serial_monitor(selected_port)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Operacao cancelada pelo usuario.{RESET}")
        sys.exit(0)
