# 🚀 Playbook de Comissionamento da VPS (Alpine Linux - Baixo Recurso)

> **Objetivo:** Guia passo a passo para provisionar e endurecer uma VPS de baixos recursos (512MB - 1GB RAM, 1 vCPU) rodando **Alpine Linux**, espremendo ao máximo o desempenho de CPU e consumo de memória RAM.

---

## 💡 Filosofia de Arquitetura para VPS de Baixa Renda
Para operar com estabilidade e consumo inferior a **100MB de RAM totais no servidor**:
1. **Host Alpine Linux:** Sem systemd, sem glibc pesada; uso de OpenRC e musl libc (~30MB de RAM base do SO).
2. **Sem Daemon Separado de PostgreSQL:** O backend utiliza **SQLite assíncrono com WAL Mode (`aiosqlite`)**, eliminando o consumo de 150-250MB de RAM de um container de banco tradicional.
3. **Single Worker Async Uvicorn:** 1 único processo de evento assíncrono consome menos de 35MB de RAM e atende centenas de requisições por minuto com latência < 5ms.
4. **ZRAM / Swapfile de Proteção:** Criação de swap leve para proteger contra OOM (Out-of-Memory) em picos de compilação ou inicialização de containers.
5. **Limites Cgroups no Docker:** Limite rígido de 128MB de RAM para o container.

---

## 📋 Pré-requisitos & Dados de Entrada
- **IP / Domínio da VPS Alpine:** Ex: `telemetry.cvale.com.br` / `203.0.113.10`
- **Usuário SSH:** `root`
- **Chave SSH Privada:** `~/.ssh/id_rsa_cvale`

---

## 🛠️ Passo a Passo de Comissionamento no Alpine Linux

### 1. Conexão SSH & Atualização de Repositórios Alpine (`apk`)
```bash
ssh -i ~/.ssh/id_rsa_cvale root@<IP_DA_VPS>

# Habilitar repositorio community se ainda nao estiver habilitado
sed -i 's/^#\(.*\/community\)/\1/' /etc/apk/repositories

# Atualizar pacotes
apk update && apk upgrade

# Instalar utilitarios essenciais leves
apk add curl wget git htop ca-certificates tzdata iptables ip6tables
```

### 2. Criação de Swapfile de Segurança (Para VPS de 512MB/1GB)
```bash
# Criar swapfile de 512MB para evitar OOM
dd if=/dev/zero of=/swapfile bs=1M count=512 status=progress
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# Persistir no fstab do Alpine
echo "/swapfile none swap sw 0 0" >> /etc/fstab

# Ajustar agressividade do swap (swappiness baixo para economizar I/O)
echo "vm.swappiness=10" >> /etc/sysctl.d/01-swappiness.conf
sysctl -p /etc/sysctl.d/01-swappiness.conf
```

### 3. Instalação e Ativação do Docker via OpenRC
No Alpine Linux, o serviço é gerenciado pelo **OpenRC** (não systemd):
```bash
# Instalar Docker e Docker Compose plugin
apk add docker docker-cli-compose

# Habilitar e iniciar o servico Docker no boot
rc-update add docker boot
rc-service docker start

# Verificar status do Docker
rc-service docker status
```

### 4. Firewall Leve com iptables no Alpine
```bash
# Regras basicas: Permitir Loopback, Estabelecidas, SSH (22), HTTP (80), HTTPS (443)
iptables -F
iptables -A INPUT -i lo -j ACCEPT
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
iptables -A INPUT -p tcp --dport 8000 -j ACCEPT # Porta da API (ou fechar se usar reverse proxy local)
iptables -P INPUT DROP
iptables -P FORWARD ACCEPT # Necessario para a rede de containers do Docker

# Salvar regras de firewall no Alpine
rc-update add iptables boot
/etc/init.d/iptables save
```

### 5. Clonagem do Repositório e Configuração de Ambiente
```bash
mkdir -p /opt/cvale
cd /opt/cvale

# Clonar o repositorio
git clone <URL_DO_REPOSITORIO> keepalive-foresight
cd keepalive-foresight/docker
```

Criar o arquivo de variáveis `.env` otimizado:
```bash
cat << 'EOF' > .env
ENVIRONMENT=production
DATABASE_URL=sqlite+aiosqlite:////data/keepalive.db
SQLITE_WAL_MODE=true
SECRET_KEY=GERAR_CHAVE_HEX_64_CHARS_AQUI
DEADMAN_TIMEOUT_SECONDS=90
HEARTBEAT_TOLERANCE_FAILS=3
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
EOF
```

### 6. Subir a Aplicação com Docker Compose
```bash
# Build e inicializacao em background
docker compose --env-file .env up -d --build

# Verificar uso real de memoria do container (< 35MB RAM)
docker stats --no-stream
```

### 7. Validação de Saúde (Healthcheck)
```bash
# Testar endpoint local
curl -i http://localhost:8000/health

# Visualizar logs da aplicacao e do worker Deadman
docker compose logs -f --tail=50 backend
```

