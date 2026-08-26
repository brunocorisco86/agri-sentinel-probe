# 🚀 Playbook de Comissionamento da VPS (Nuvem) - Keepalive Foresight

> **Objetivo:** Guia passo a passo e automatizável para provisionar, endurecer (hardening) e subir a stack Docker do backend FastAPI na VPS de produção assim que todas as milestones locais forem aprovadas.

---

## 📋 Pré-requisitos & Dados de Entrada
Antes de iniciar, tenha em mãos:
- **IP Público ou Domínio da VPS:** Ex: `telemetry.cvale.com.br` / `203.0.113.10`
- **Usuário SSH:** Ex: `deployer` ou `root`
- **Chave SSH Privada:** `~/.ssh/id_rsa_cvale`
- **Secrets de Produção:**
  - `DATABASE_URL` (PostgreSQL)
  - `SECRET_KEY` (Chave de assinatura de tokens)
  - `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID`

---

## 🛠️ Passo a Passo de Comissionamento

### 1. Conexão SSH & Atualização do Sistema Operacional
```bash
ssh -i ~/.ssh/id_rsa_cvale root@<IP_DA_VPS>

# Atualizar pacotes do sistema
apt-get update && apt-get upgrade -y
apt-get install -y ufw curl wget git fail2ban htop ca-certificates gnupg lsb-release
```

### 2. Hardening e Configuração de Firewall (UFW)
```bash
# Permitir SSH, HTTP e HTTPS
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment 'SSH'
ufw allow 80/tcp comment 'HTTP (Certbot)'
ufw allow 443/tcp comment 'HTTPS API'
ufw enable
```

### 3. Instalação do Docker & Docker Compose Plugin
```bash
# Adicionar chave oficial do Docker
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

# Configurar repositório
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker Engine e plugins
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable --now docker
```

### 4. Criação do Usuário de Deploy e Clonagem do Repositório
```bash
useradd -m -s /bin/bash deployer
usermod -aG docker deployer
mkdir -p /home/deployer/.ssh
cp /root/.ssh/authorized_keys /home/deployer/.ssh/
chown -R deployer:deployer /home/deployer/.ssh
chmod 700 /home/deployer/.ssh
chmod 600 /home/deployer/.ssh/authorized_keys

# Clonar repositório no diretório de produção
su - deployer
git clone <URL_DO_REPOSITORIO> /home/deployer/keepalive-foresight
cd /home/deployer/keepalive-foresight/docker
```

### 5. Configuração das Variáveis de Ambiente (`.env`)
Criar o arquivo `/home/deployer/keepalive-foresight/docker/.env`:
```env
ENVIRONMENT=production
POSTGRES_USER=keepalive_admin
POSTGRES_PASSWORD=GERAR_SENHA_FORTE_AQUI_123!
POSTGRES_DB=keepalive_production
DATABASE_URL=postgresql+asyncpg://keepalive_admin:GERAR_SENHA_FORTE_AQUI_123!@db:5432/keepalive_production

SECRET_KEY=GERAR_CHAVE_HEX_64_CHARS
DEADMAN_TIMEOUT_SECONDS=90
HEARTBEAT_TOLERANCE_FAILS=3

TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRstuVWXyz
TELEGRAM_CHAT_ID=-1001234567890
```

### 6. Emissão de Certificado SSL (Let's Encrypt / Certbot)
```bash
apt-get install -y certbot python3-certbot-nginx
certbot certonly --standalone -d <SEU_DOMINIO_VPS> --non-interactive --agree-tos -m suporte@cvale.com.br
```

### 7. Inicialização dos Containers & Migrações de Banco
```bash
cd /home/deployer/keepalive-foresight/docker
docker compose --env-file .env up -d --build

# Executar migrações do Alembic (criação das tabelas)
docker compose exec backend alembic upgrade head
```

### 8. Validação e Teste de Healthcheck
```bash
# Testar endpoint local e externo
curl -f http://localhost:8000/health || echo "Falha no healthcheck"
curl -f https://<SEU_DOMINIO_VPS>/health

# Monitorar logs do Dead Man's Switch
docker compose logs -f backend
```
