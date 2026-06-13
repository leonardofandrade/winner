#!/usr/bin/env bash
# Deploy do Winner via Docker Compose com inicialização automática pelo systemd
# Uso: sudo bash deploy/install-docker.sh
set -euo pipefail

APP_DIR="/opt/winner"
SRC_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Winner Deploy (Docker) ==="

# 1. Instala Docker se necessário
if ! command -v docker &>/dev/null; then
    echo "Instalando Docker..."
    apt-get update -q
    apt-get install -y ca-certificates curl
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    chmod a+r /etc/apt/keyrings/docker.asc
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
        > /etc/apt/sources.list.d/docker.list
    apt-get update -q
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    systemctl enable docker
    echo "Docker instalado."
else
    echo "Docker já instalado: $(docker --version)"
fi

# 2. Copia o código para /opt/winner
echo "Copiando código para $APP_DIR..."
rsync -a --exclude='.venv' --exclude='db.sqlite3' --exclude='__pycache__' \
    "$SRC_DIR/" "$APP_DIR/"

# 3. Configura o .env
if [ ! -f "$APP_DIR/.env" ]; then
    cp "$APP_DIR/.env.example" "$APP_DIR/.env"
    chmod 600 "$APP_DIR/.env"
    echo ""
    echo "ATENÇÃO: edite $APP_DIR/.env com os valores reais e rode este script novamente."
    echo "         nano $APP_DIR/.env"
    exit 1
fi

# 4. Instala e habilita o serviço systemd
cp "$APP_DIR/deploy/winner-docker.service"       /etc/systemd/system/
cp "$APP_DIR/deploy/winner-sync-docker.service"  /etc/systemd/system/
cp "$APP_DIR/deploy/winner-sync-docker.timer"    /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now winner-docker.service
systemctl enable --now winner-sync-docker.timer

# 5. Cria superuser se ainda não existir
echo ""
echo "Aguardando containers subirem..."
sleep 10
docker compose -f "$APP_DIR/docker-compose.yml" exec -T api \
    python manage.py shell -c \
    "from django.contrib.auth import get_user_model; U=get_user_model(); print('superuser existe' if U.objects.filter(is_superuser=True).exists() else 'CRIAR: docker compose exec api python manage.py createsuperuser')"

echo ""
echo "=== Deploy concluído ==="
echo "Status:  systemctl status winner-docker"
echo "Logs:    docker compose -C $APP_DIR logs -f"
echo "Sync:    systemctl status winner-sync-docker.timer"
