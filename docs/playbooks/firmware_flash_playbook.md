# ⚡ Playbook de Gravação (Flash) do Firmware - LilyGO T-Display & ESP32-C3 SuperMini

> **Objetivo:** Procedimento padronizado para compilar, gravar (flash) via `esptool` ou PlatformIO, e validar a sonda de monitoramento no hardware **LilyGO T-Display (ESP32 ST7789)** e **ESP32-C3 SuperMini (RISC-V)**.

---

## 📋 Pré-requisitos & Ferramentas
1. **Hardware Suportado:**
   - **Placa A:** LilyGO T-Display (ESP32-D0WDQ6 com display ST7789 240x135 via SPI DMA).
   - **Placa B:** ESP32-C3 SuperMini (RISC-V 160MHz com LED azul no GPIO 8 e USB CDC nativo).
   - Cabo USB Type-C de boa qualidade com suporte a dados.
2. **Software Local:**
   - PlatformIO Core (`pio`) instalado via pipx (`pipx install platformio`).
   - `esptool` v5.3.1 instalado via pipx (`pipx install esptool`).
   - Permissões de porta serial no Linux (`dialout`).

---

## 🛠️ Passo a Passo de Gravação

### 1. Configuração de Permissões USB no Linux
Garanta que o seu usuário pertença ao grupo `dialout` para acessar `/dev/ttyACM*` e `/dev/ttyUSB*`:
```bash
sudo usermod -a -G dialout $USER
sudo udevadm control --reload-rules && sudo udevadm trigger
```
*(Caso necessário temporariamente na sessão: `sudo chmod 666 /dev/ttyACM0`)*

### 2. Identificação da Porta Serial
Conecte a placa à porta USB e identifique o dispositivo:
```bash
ls -la /dev/ttyACM* /dev/ttyUSB* 2>/dev/null
# Exemplo de saída: /dev/ttyACM0 ou /dev/ttyUSB0
```

### 3. Compilação dos Binários

Acesse a pasta `/firmware` e execute a compilação para o seu modelo de placa:

```bash
cd "/home/brunoconter/Documentos/1_C.VALE/2 - PROJETOS/16_Keepalive_Foresight/firmware"

# Para LilyGO T-Display:
pio run -e ttgo-t-display

# Para ESP32-C3 SuperMini:
pio run -e esp32-c3-supermini
```

---

### 4. Gravação Flash (Opção 1: Via `esptool`)

#### A. LilyGO T-Display (ESP32):
```bash
esptool.py -p /dev/ttyACM0 -b 460800 --chip esp32 \
  write_flash --flash_mode dio --flash_size 4MB --flash_freq 40m \
  0x1000 .pio/build/ttgo-t-display/bootloader.bin \
  0x8000 .pio/build/ttgo-t-display/partitions.bin \
  0x10000 .pio/build/ttgo-t-display/firmware.bin
```

#### B. ESP32-C3 SuperMini (RISC-V):
```bash
esptool.py -p /dev/ttyACM0 -b 460800 --chip esp32c3 \
  write_flash --flash_mode dio --flash_size 4MB --flash_freq 40m \
  0x0 .pio/build/esp32-c3-supermini/bootloader.bin \
  0x8000 .pio/build/esp32-c3-supermini/partitions.bin \
  0x10000 .pio/build/esp32-c3-supermini/firmware.bin
```

---

### 5. Gravação Flash (Opção 2: Via PlatformIO Automático)

```bash
# LilyGO T-Display:
pio run -e ttgo-t-display --target upload --upload-port /dev/ttyACM0

# ESP32-C3 SuperMini:
pio run -e esp32-c3-supermini --target upload --upload-port /dev/ttyACM0
```

---

### 6. Monitoramento Serial e Diagnóstico de Boot
Abra o monitor serial a **115200 baud**:
```bash
pio device monitor -b 115200 -p /dev/ttyACM0
```

#### Log Serial Esperado:
```
======================================
   KEEPALIVE FORESIGHT - SENTINEL     
   Hardware: LilyGO T-Display (ESP32)
   Versao: 1.0.0
======================================

[ID] Device ID: SENTINEL-A1B2
[ID] Device MAC: AA:BB:CC:DD:A1:B2
[NVS] Nenhuma rede configurada. Iniciando Portal Captive...
[PROVISIONAMENTO] Entrando em Modo SoftAP: Keepalive-SENTINEL-A1B2
```

---

### 7. Checklist de Validação Visual & Funcional (Multi-Ponto)
- [ ] **Provisionamento Web (Captive Portal):** Conectar no Wi-Fi `Keepalive-SENTINEL-XXXX`. O navegador abre automaticamente em `http://192.168.4.1`.
- [ ] **Cadastro do Ponto:** Cadastrar o nome do local (Ex: `Minha Casa`, `Granja Aviário 1`, `Escritório`).
- [ ] **Modo LAN vs WAN-Only:** Se for monitorar o gateway Dragino ou roteador, preencher o IP (`192.168.1.50` ou `192.168.0.1`). Se for apenas sonda de internet na sua casa, deixar em branco (Modo WAN-Only).
- [ ] **Transição STA:** Salvar e verificar no display o HUD em tempo real com RSSI, RTT da Nuvem e RTT Local.
- [ ] **Botão Físico Modo AP:** Segurar o botão (GPIO 35 no TTGO / GPIO 9 no C3) por 3 segundos para reabrir o portal a qualquer momento.
