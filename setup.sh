#!/usr/bin/env bash
# Configura e sobe o laboratório de forma interativa.
# Pergunta porta/usuário/senha/banco, valida porta livre, grava .env e sobe o container.
set -euo pipefail

cd "$(dirname "$0")"

echo "== Laboratório de Administração PostgreSQL =="
echo

porta_esta_livre() {
    local porta="$1"
    if command -v nc >/dev/null 2>&1; then
        ! nc -z localhost "$porta" >/dev/null 2>&1
    else
        # fallback sem netcat: tenta abrir /dev/tcp (bash)
        ! (exec 3<>"/dev/tcp/localhost/$porta") 2>/dev/null
    fi
}

while true; do
    read -rp "Em qual porta expor o Postgres no seu computador? [5433]: " PORTA
    PORTA="${PORTA:-5433}"
    if porta_esta_livre "$PORTA"; then
        break
    else
        echo "  -> porta $PORTA já está em uso (talvez um Postgres local na 5432?). Escolha outra."
    fi
done

read -rp "Usuário do banco [aluno]: " PGUSER
PGUSER="${PGUSER:-aluno}"

read -rp "Senha do banco [aluno123]: " PGPASSWORD
PGPASSWORD="${PGPASSWORD:-aluno123}"

read -rp "Nome do banco [loja]: " PGDATABASE
PGDATABASE="${PGDATABASE:-loja}"

cat > .env <<EOF
POSTGRES_PORT=${PORTA}
POSTGRES_USER=${PGUSER}
POSTGRES_PASSWORD=${PGPASSWORD}
POSTGRES_DB=${PGDATABASE}
EOF

echo
echo "Configuração salva em .env. Subindo o container..."
docker compose up -d

echo
echo "Pronto! Conecte no DBeaver com:"
echo "  Host:     localhost"
echo "  Porta:    ${PORTA}"
echo "  Database: ${PGDATABASE}"
echo "  Usuário:  ${PGUSER}"
echo "  Senha:    ${PGPASSWORD}"
echo
echo "Driver: PostgreSQL (o DBeaver detecta e baixa o driver na primeira conexão)."
