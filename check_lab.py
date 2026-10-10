#!/usr/bin/env python3
"""Autoavaliação do laboratório: roda alguns checks contra o Postgres do próprio aluno
e imprime o que passou/falhou. Não lança nota em lugar nenhum — isso é feito do lado
do professor (módulo separado), de forma independente desse resultado autodeclarado.

Uso:
    pip install psycopg2-binary python-dotenv
    python check_lab.py
"""
from __future__ import annotations

import os
import sys

try:
    import psycopg2
except ImportError:
    sys.exit("Instale a dependência primeiro: pip install psycopg2-binary python-dotenv")

try:
    from dotenv import dotenv_values
except ImportError:
    dotenv_values = None


# --- Ajuste aqui os valores esperados da atividade (o professor define por turma) ---
ESPERADO = {
    "max_connections": "50",
    "work_mem": "8MB",
}
TABELAS_ESPERADAS = {"cliente": 3, "produto": 3, "pedido": 3}
ROLE_ESPERADA = "leitor"


def carregar_conexao() -> dict:
    env = dotenv_values(".env") if dotenv_values else {}
    return {
        "host": "localhost",
        "port": env.get("POSTGRES_PORT", os.environ.get("POSTGRES_PORT", "5433")),
        "user": env.get("POSTGRES_USER", os.environ.get("POSTGRES_USER", "aluno")),
        "password": env.get("POSTGRES_PASSWORD", os.environ.get("POSTGRES_PASSWORD", "aluno123")),
        "dbname": env.get("POSTGRES_DB", os.environ.get("POSTGRES_DB", "loja")),
    }


def checar(nome: str, ok: bool, detalhe: str = "") -> bool:
    status = "OK " if ok else "FALHOU"
    print(f"[{status}] {nome}" + (f" — {detalhe}" if detalhe else ""))
    return ok


def main() -> int:
    conexao = carregar_conexao()
    resultados = []

    try:
        conn = psycopg2.connect(**conexao)
    except Exception as exc:
        checar("Conexão com o banco", False, str(exc))
        return 1

    with conn, conn.cursor() as cur:
        resultados.append(checar("Conexão com o banco", True))

        for parametro, valor_esperado in ESPERADO.items():
            cur.execute("SHOW %s" % parametro)  # nomes fixos, não vem de input externo
            valor_atual = cur.fetchone()[0]
            ok = valor_atual.strip().lower() == valor_esperado.strip().lower()
            resultados.append(
                checar(f"Parâmetro {parametro}", ok, f"esperado={valor_esperado} atual={valor_atual}")
            )

        for tabela, linhas_esperadas in TABELAS_ESPERADAS.items():
            cur.execute("SELECT count(*) FROM %s" % tabela)
            total = cur.fetchone()[0]
            ok = total >= linhas_esperadas
            resultados.append(checar(f"Tabela {tabela} com dados", ok, f"linhas={total}"))

        cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (ROLE_ESPERADA,))
        existe_role = cur.fetchone() is not None
        resultados.append(checar(f"Role '{ROLE_ESPERADA}' criada", existe_role))

    print()
    total_ok = sum(resultados)
    print(f"{total_ok}/{len(resultados)} checks passaram.")
    return 0 if all(resultados) else 1


if __name__ == "__main__":
    raise SystemExit(main())
