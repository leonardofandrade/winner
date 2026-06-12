#!/usr/bin/env bash
# Script de instalação do Winner em um servidor Linux (Debian/Ubuntu)
# Uso: sudo bash deploy/install.sh
set -euo pipefail

APP_DIR="/opt/winner"
APP_USER="winner"
LOG_DIR="/var/log/winner"
REPO_URL=""  # preencha com a URL do repositório git, ou deixe vazio para copiar manualmente

echo "=== Winner Deploy ==="

# 1. Dependências do sistema
apt-get update -q
apt-get install -y python3 python3-venv python3-pip nginx git

# 2. Usuário e diretórios
if ! id "$APP_USER" &>/dev/null; then
    useradd --system --shell /bin/bash --home "$APP_DIR" --create-home "$APP_USER"
    echo "Usuário '$APP_USER' criado."
fi
mkdir -p "$LOG_DIR"
chown "$APP_USER:$APP_USER" "$LOG_DIR"

# 3. Código — clone ou aviso para copiar manualmente
if [ -n "$REPO_URL" ]; then
    if [ -d "$APP_DIR/.git" ]; then
        sudo -u "$APP_USER" git -C "$APP_DIR" pull
    else
        sudo -u "$APP_USER" git clone "$REPO_URL" "$APP_DIR"
    fi
else
    echo "AVISO: REPO_URL não definido. Copie o código para $APP_DIR manualmente."
    echo "       Exemplo: rsync -av --exclude='.venv' --exclude='db.sqlite3' ./ $APP_USER@HOST:$APP_DIR/"
fi

# 4. Virtualenv e dependências
sudo -u "$APP_USER" python3 -m venv "$APP_DIR/.venv"
sudo -u "$APP_USER" "$APP_DIR/.venv/bin/pip" install --quiet --upgrade pip
sudo -u "$APP_USER" "$APP_DIR/.venv/bin/pip" install --quiet -r "$APP_DIR/requirements/production.txt"

# 5. .env — cria a partir do exemplo se não existir
if [ ! -f "$APP_DIR/.env" ]; then
    cp "$APP_DIR/.env.example" "$APP_DIR/.env"
    chown "$APP_USER:$APP_USER" "$APP_DIR/.env"
    chmod 600 "$APP_DIR/.env"
    echo "ATENÇÃO: edite $APP_DIR/.env com os valores reais antes de continuar."
    exit 1
fi

# 6. Migrações, static e import inicial
cd "$APP_DIR"
sudo -u "$APP_USER" "$APP_DIR/.venv/bin/python" manage.py migrate --settings=config.settings.production
sudo -u "$APP_USER" "$APP_DIR/.venv/bin/python" manage.py collectstatic --noinput --settings=config.settings.production
sudo -u "$APP_USER" "$APP_DIR/.venv/bin/python" manage.py import_lotofacil --sync --settings=config.settings.production

# 7. Systemd
cp "$APP_DIR/deploy/winner-api.service"  /etc/systemd/system/
cp "$APP_DIR/deploy/winner-bot.service"  /etc/systemd/system/
cp "$APP_DIR/deploy/winner-sync.service" /etc/systemd/system/
cp "$APP_DIR/deploy/winner-sync.timer"   /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now winner-api.service
systemctl enable --now winner-bot.service
systemctl enable --now winner-sync.timer

# 8. Nginx
cp "$APP_DIR/deploy/nginx.conf" /etc/nginx/sites-available/winner
ln -sf /etc/nginx/sites-available/winner /etc/nginx/sites-enabled/winner
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

echo ""
echo "=== Deploy concluído ==="
echo "API:    http://localhost/api/"
echo "Admin:  http://localhost/admin/"
echo "Bot:    systemctl status winner-bot"
echo "Sync:   systemctl status winner-sync.timer"
echo "Logs:   journalctl -u winner-bot -f"
