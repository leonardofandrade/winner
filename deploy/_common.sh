#!/usr/bin/env bash
# Funções compartilhadas pelos deploys locais no WSL + Docker Desktop.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

die() {
  echo "erro: $*" >&2
  exit 1
}

require_docker() {
  command -v docker >/dev/null 2>&1 || die "docker não encontrado no WSL. Ative a integração desta distro no Docker Desktop."
  docker info >/dev/null 2>&1 || die "o Docker Desktop não está respondendo."
  command -v curl >/dev/null 2>&1 || die "curl não encontrado no WSL."
}

port_in_use() {
  local port="$1"
  if ss -ltn 2>/dev/null | awk '{print $4}' | grep -Eq "(^|:)${port}$"; then
    return 0
  fi
  if docker ps --format '{{.Ports}}' | grep -Eq "(0\\.0\\.0\\.0|\\[::\\]|:::):${port}->"; then
    return 0
  fi
  return 1
}

require_port_free() {
  local port="$1"
  local project="$2"
  local hint="$3"
  if docker ps --filter "label=com.docker.compose.project=${project}" --format '{{.Ports}}' | grep -Eq ":${port}->"; then
    return 0
  fi
  if port_in_use "$port"; then
    die "a porta ${port} já está em uso. ${hint}"
  fi
}

env_value() {
  local file="$1"
  local key="$2"
  local line
  line="$(grep -E "^${key}=" "$file" 2>/dev/null | tail -n 1 || true)"
  line="${line#*=}"
  line="${line%$'\r'}"
  line="${line#\"}"
  line="${line%\"}"
  line="${line#\'}"
  line="${line%\'}"
  printf '%s' "$line"
}

db_url_password() {
  local rest="${1#*://}"
  rest="${rest#*:}"
  printf '%s' "${rest%%@*}"
}

check_database_env() {
  local file="$1"
  local url pass url_pass
  url="$(env_value "$file" DATABASE_URL)"
  pass="$(env_value "$file" MYSQL_PASSWORD)"
  url_pass="$(db_url_password "$url")"
  [[ "$url" == mysql://winner:*@db:3306/winner ]] || die "DATABASE_URL em ${file} precisa ser mysql://winner:<senha>@db:3306/winner"
  [[ -n "$pass" && "$url_pass" == "$pass" ]] || die "MYSQL_PASSWORD e a senha de DATABASE_URL diferem em ${file}"
}

warn_secret_key() {
  local file="$1"
  local secret
  secret="$(env_value "$file" SECRET_KEY)"
  if [[ -z "$secret" || "$secret" == troque-* || "$secret" == dev-only-* ]]; then
    echo "aviso: SECRET_KEY em ${file} ainda é um valor de exemplo."
  fi
}

token_configured() {
  local token
  token="$(env_value "$1" TELEGRAM_BOT_TOKEN)"
  [[ -n "$token" && "$token" != "seu-token-aqui" ]]
}

wait_http() {
  local url="$1"
  local i code=""
  for i in $(seq 1 30); do
    code="$(curl -sS -o /dev/null -w '%{http_code}' -L --max-time 5 "$url" || true)"
    if [[ "$code" == "200" ]]; then
      echo "ok ${url}"
      return 0
    fi
    sleep 2
  done
  die "${url} respondeu ${code:-sem conexão}"
}
