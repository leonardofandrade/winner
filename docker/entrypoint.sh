#!/bin/sh
set -e

# O ping do MySQL pode passar antes do banco aceitar conexão.
attempt=0
until python manage.py migrate --noinput; do
  attempt=$((attempt + 1))
  if [ "$attempt" -ge 30 ]; then
    echo "migrate falhou após 30 tentativas"
    exit 1
  fi
  echo "banco ainda não está pronto, nova tentativa em 2s..."
  sleep 2
done

# No dev o runserver serve os estáticos. O bot não publica arquivos.
if [ "${DJANGO_COLLECTSTATIC:-1}" = "1" ]; then
  python manage.py collectstatic --noinput --clear
fi

exec "$@"
