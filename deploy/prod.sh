#!/usr/bin/env bash
# Sobe o Winner em modo produção local no Docker Desktop, a partir do WSL.
# Uso:
#   deploy/prod.sh up|down|ps|logs
# Nginx na porta 80. O MySQL não é publicado no Windows.
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_common.sh"

COMPOSE=(docker compose --env-file "$ROOT_DIR/.env" -p winner -f "$ROOT_DIR/docker-compose.yml")

usage() {
  cat <<'EOF'
Uso: deploy/prod.sh <up|down|ps|logs> [opções]

  up              build e sobe MySQL, API, nginx e o bot
  down            para este ambiente e mantém os volumes
  ps              mostra os containers deste ambiente
  logs [serviço]  acompanha os logs

Sem TELEGRAM_BOT_TOKEN válido, o bot fica de fora. Os outros containers não são alterados.
EOF
}

ensure_env() {
  if [[ ! -f "$ROOT_DIR/.env" ]]; then
    cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
    chmod 600 "$ROOT_DIR/.env"
    echo "criei .env a partir de .env.example; revise SECRET_KEY e as senhas."
  fi
  check_database_env "$ROOT_DIR/.env"
  warn_secret_key "$ROOT_DIR/.env"
}

cmd_up() {
  [[ $# -eq 0 ]] || die "argumento desconhecido: $1"
  require_docker
  ensure_env
  require_port_free 80 winner "A produção local publica o nginx na porta 80."

  local scale=()
  if ! token_configured "$ROOT_DIR/.env"; then
    echo "aviso: TELEGRAM_BOT_TOKEN ausente ou de exemplo. O bot não será iniciado."
    scale=(--scale bot=0)
  fi

  cd "$ROOT_DIR"
  if ! "${COMPOSE[@]}" up -d --build --wait --wait-timeout 300 "${scale[@]}"; then
    "${COMPOSE[@]}" logs --tail 80 || true
    die "o ambiente de produção local não ficou saudável"
  fi

  wait_http "http://127.0.0.1/api/contests/"
  wait_http "http://127.0.0.1/admin/login/"
  "${COMPOSE[@]}" ps
  cat <<'EOF'

Produção local no ar.
  API:    http://localhost/api/contests/
  Admin:  http://localhost/admin/
  MySQL:  só na rede Docker (host db, porta 3306 interna)

  Superusuário: docker compose --env-file .env -p winner -f docker-compose.yml exec api python manage.py createsuperuser
  Concursos:    docker compose --env-file .env -p winner -f docker-compose.yml exec api python manage.py import_lotofacil --latest
EOF
}

cmd_down() {
  require_docker
  cd "$ROOT_DIR"
  "${COMPOSE[@]}" down
}

cmd_ps() {
  require_docker
  "${COMPOSE[@]}" ps
}

cmd_logs() {
  require_docker
  "${COMPOSE[@]}" logs -f "$@"
}

if [[ $# -eq 0 ]]; then
  set -- up
fi

case "$1" in
  up) shift; cmd_up "$@" ;;
  down) shift; cmd_down "$@" ;;
  ps) shift; cmd_ps "$@" ;;
  logs) shift; cmd_logs "$@" ;;
  *) usage; exit 1 ;;
esac
