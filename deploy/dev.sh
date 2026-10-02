#!/usr/bin/env bash
# Sobe o Winner em desenvolvimento no Docker Desktop, a partir do WSL.
# Uso:
#   deploy/dev.sh up              API em http://localhost:8080 e MySQL em localhost:3307
#   deploy/dev.sh up --with-bot   inclui o bot (exige TELEGRAM_BOT_TOKEN em .env.dev)
#   deploy/dev.sh down|ps|logs
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_common.sh"

COMPOSE=(docker compose --env-file "$ROOT_DIR/.env.dev" -p winner-dev -f "$ROOT_DIR/docker-compose.dev.yml")

usage() {
  cat <<'EOF'
Uso: deploy/dev.sh <up|down|ps|logs> [opções]

  up              sobe MySQL e API com o código montado e reload
  up --with-bot   também sobe o Telegram bot
  down            para o ambiente de dev e mantém o volume do banco
  ps              mostra os containers deste ambiente
  logs [serviço]  acompanha os logs
EOF
}

ensure_env() {
  if [[ ! -f "$ROOT_DIR/.env.dev" ]]; then
    cp "$ROOT_DIR/.env.dev.example" "$ROOT_DIR/.env.dev"
    echo "criei .env.dev a partir de .env.dev.example"
  fi
  check_database_env "$ROOT_DIR/.env.dev"
  warn_secret_key "$ROOT_DIR/.env.dev"
}

cmd_up() {
  local with_bot=0 arg
  for arg in "$@"; do
    case "$arg" in
      --with-bot) with_bot=1 ;;
      *) die "argumento desconhecido: $arg" ;;
    esac
  done

  require_docker
  ensure_env
  require_port_free 8080 winner-dev "A API de dev usa 8080. A 8200 permanece com o Extractor."
  require_port_free 3307 winner-dev "O MySQL de dev usa 3307. A 3306 permanece com o Extractor."

  local profiles=()
  if [[ "$with_bot" -eq 1 ]]; then
    token_configured "$ROOT_DIR/.env.dev" || die "defina TELEGRAM_BOT_TOKEN em .env.dev antes de usar --with-bot"
    profiles=(--profile bot)
  fi

  cd "$ROOT_DIR"
  if ! "${COMPOSE[@]}" "${profiles[@]}" up -d --build --wait --wait-timeout 300; then
    "${COMPOSE[@]}" --profile bot logs --tail 80 || true
    die "o ambiente de dev não ficou saudável"
  fi

  wait_http "http://127.0.0.1:8080/api/contests/"
  wait_http "http://127.0.0.1:8080/admin/login/"
  "${COMPOSE[@]}" --profile bot ps
  cat <<'EOF'

Dev no ar.
  API:    http://localhost:8080/api/contests/
  Admin:  http://localhost:8080/admin/
  MySQL:  127.0.0.1:3307  (usuário winner, banco winner)
  Código montado em /app: o runserver recarrega ao salvar.

  Superusuário: docker compose --env-file .env.dev -p winner-dev -f docker-compose.dev.yml exec api python manage.py createsuperuser
EOF
}

cmd_down() {
  require_docker
  cd "$ROOT_DIR"
  "${COMPOSE[@]}" --profile bot down
}

cmd_ps() {
  require_docker
  "${COMPOSE[@]}" --profile bot ps
}

cmd_logs() {
  require_docker
  "${COMPOSE[@]}" --profile bot logs -f "$@"
}

if [[ $# -eq 0 ]]; then
  set -- up
elif [[ "${1:-}" == "--with-bot" ]]; then
  set -- up --with-bot
fi

case "$1" in
  up) shift; cmd_up "$@" ;;
  down) shift; cmd_down "$@" ;;
  ps) shift; cmd_ps "$@" ;;
  logs) shift; cmd_logs "$@" ;;
  *) usage; exit 1 ;;
esac
