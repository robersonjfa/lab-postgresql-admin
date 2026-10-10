#!/usr/bin/env python3
"""Autoavaliação do laboratório: roda os checks (ver labcheck.py) contra o
Postgres do próprio aluno e imprime o que passou/falhou. Não lança nota em
lugar nenhum — isso é feito do lado do professor, em correcao/corrige_lab.py,
de forma independente desse resultado autodeclarado.

Uso:
    pip install psycopg2-binary python-dotenv
    python check_lab.py
"""
from __future__ import annotations

import os
import sys

try:
    from dotenv import dotenv_values
except ImportError:
    dotenv_values = None

from labcheck import nota, rodar_checks


def carregar_conexao() -> dict:
    env = dotenv_values(".env") if dotenv_values else {}
    return {
        "host": "localhost",
        "port": env.get("POSTGRES_PORT", os.environ.get("POSTGRES_PORT", "5433")),
        "user": env.get("POSTGRES_USER", os.environ.get("POSTGRES_USER", "aluno")),
        "password": env.get("POSTGRES_PASSWORD", os.environ.get("POSTGRES_PASSWORD", "aluno123")),
        "dbname": env.get("POSTGRES_DB", os.environ.get("POSTGRES_DB", "loja")),
    }


def main() -> int:
    resultados = rodar_checks(carregar_conexao())
    for r in resultados:
        status = "OK " if r.ok else "FALHOU"
        print(f"[{status}] {r.nome}" + (f" — {r.detalhe}" if r.detalhe else ""))

    print()
    total_ok = sum(r.ok for r in resultados)
    print(f"{total_ok}/{len(resultados)} checks passaram.")
    return 0 if all(r.ok for r in resultados) else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ImportError:
        sys.exit("Instale as dependências primeiro: pip install psycopg2-binary python-dotenv")
