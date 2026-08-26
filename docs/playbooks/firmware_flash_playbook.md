# ⚡ Playbook de Gravação (Flash) do Firmware - LilyGO T-Display ESP32

> **Objetivo:** Procedimento padronizado para compilar, gravar (flash) e validar a sonda de monitoramento no hardware **LilyGO T-Display (ESP32 com display ST7789 240x135)**.

---

## 📋 Pré-requisitos & Ferramentas
1. **Hardware:**
   - Placa LilyGO T-Display (ESP32-D0WDQ6 com display ST7789).
   - Cabo USB Type-C de dados de boa qualidade.
2. **Software Local:**
   - PlatformIO Core (`pio`) ou VS Code com extensão PlatformIO.
   - Drivers USB-Serial (chip CH9102F ou CP210x conforme a revisão da placa).
   - Permissões de porta serial no Linux (`dialout`).

---

## 🛠️ Passo a Passo de Gravação

### 1. Configuração de Permissões USB no Linux
Caso esteja em ambiente Linux/Ubuntu, garanta que o usuário pertença ao grupo `dialout`:
```bash
sudo usermod -a -G dialout $USER
# Recarregue as regras udev
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### 2. Identificação da Porta Serial
Conecte o LilyGO T-Display à porta USB e identifique o dispositivo:
```bash
ls -la /dev/ttyACM* /dev/ttyUSB* 2>/dev/null
# Exemplo de saída: /dev/ttyACM0 ou /dev/ttyUSB0
```

### 3. Compilação Limpa do Firmware
Acesse a pasta `/firmware` e execute o build do PlatformIO:
```bash
cd /home/brunoconter/Documentos/1_C.VALE/2\ -\ PROJETOS/16_Keepalive_Foresight/firmware

# Compilação limpa
pio run -e ttgo-t-display
```

### 4. Gravação do Firmware via PlatformIO
Execute o comando de upload especificando a porta identificada:
```bash
# Upload automático na porta detectada
pio run -e ttgo-t-display --target upload

# Ou especificando a porta manualmente:
pio run -e ttgo-t-display --target upload --upload-port /dev/ttyACM0
```

### 5. Monitoramento Serial e Diagnóstico de Boot
Abra o monitor serial a **115200 baud** para verificar a inicialização:
```bash
pio device monitor -b 115200
```

#### O que observar no log serial:
```
[BOOT] Keepalive Foresight v1.0.0
[HW] Hardware Watchdog WDT inicializado (30s)
[DISPLAY] ST7789 inicializado via SPI DMA (240x135)
[NVS] Lendo configuracoes de rede...
[NVS] Credenciais nao encontradas -> Entrando em modo Provisionamento SoftAP
[WIFI_AP] SoftAP Ativo: 'Keepalive-Probe-A1B2' (IP: 192.168.4.1)
[DNS] Servidor DNS Captive Portal rodando na porta 53
[HTTP] Servidor Web de configuracao ativo
```

### 6. Checklist de Validação Visual & Funcional
- [ ] **Display ST7789:** O display acende com brilho adequado (backlight no GPIO 4) e exibe a tela de boas-vindas com instruções para conectar no Wi-Fi `Keepalive-Probe-XXXX`.
- [ ] **Captive Portal:** Conectar smartphone ou notebook na rede Wi-Fi gerada pelo ESP32. O navegador deve abrir automaticamente em `http://192.168.4.1`.
- [ ] **Provisionamento:** Realizar scan das redes, selecionar o Wi-Fi da granja, preencher o IP do Dragino (`192.168.1.50`) e salvar.
- [ ] **Transição STA:** O ESP32 reinicia, conecta na rede da granja e o display passa a exibir o HUD em tempo real com RSSI, RTT do Dragino e status da nuvem.
- [ ] **Reset de Fábrica / Modo AP Forçado:** Pressionar o botão superior (**GPIO 35**) por 5 segundos deve apagar/reabrir o portal de configuração.
