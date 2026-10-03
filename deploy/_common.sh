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

# Docker Desktop publica a porta no Windows. O ss do WSL não vê esse listener.
windows_listener() {
  local port="$1"
  command -v powershell.exe >/dev/null 2>&1 || return 0
  WIN_PORT="$port" powershell.exe -NoProfile -Command '
    $port = $env:WIN_PORT
    if (-not $port) { exit 0 }
    $pattern = "[:\.]$port\s"
    $line = netstat -ano | Select-String -Pattern $pattern | Select-String -Pattern "LISTENING" | Select-Object -First 1
    if (-not $line) { exit 0 }
    $parts = ($line.Line.Trim() -split "\s+")
    $procId = 0
    [void][int]::TryParse($parts[-1], [ref]$procId)
    if ($procId -le 0) { Write-Output "processo desconhecido"; exit 0 }
    $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
    $svc = Get-CimInstance Win32_Service -Filter "ProcessId=$procId" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($svc -and $svc.PathName) {
      Write-Output ("{0} ({1})" -f $svc.Name, $svc.PathName)
    } elseif ($svc) {
      Write-Output $svc.Name
    } elseif ($proc) {
      Write-Output ("{0} (pid {1})" -f $proc.ProcessName, $procId)
    } else {
      Write-Output ("pid {0}" -f $procId)
    }
  ' 2>/dev/null || true
}

port_in_use() {
  local port="$1"
  PORT_HOLDER=""
  if ss -ltn 2>/dev/null | awk '{print $4}' | grep -Eq "(^|:)${port}$"; then
    return 0
  fi
  if docker ps --format '{{.Ports}}' | grep -Eq "(0\\.0\\.0\\.0|\\[::\\]|:::):${port}->"; then
    return 0
  fi
  PORT_HOLDER="$(windows_listener "$port")"
  [[ -n "$PORT_HOLDER" ]]
}

require_port_free() {
  local port="$1"
  local project="$2"
  local hint="$3"
  if docker ps --filter "label=com.docker.compose.project=${project}" --format '{{.Ports}}' | grep -Eq ":${port}->"; then
    return 0
  fi
  if port_in_use "$port"; then
    if [[ -n "${PORT_HOLDER:-}" ]]; then
      die "a porta ${port} já está em uso no Windows por ${PORT_HOLDER}. ${hint}"
    fi
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
