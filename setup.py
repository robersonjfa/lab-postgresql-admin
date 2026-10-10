#!/usr/bin/env python3
"""Configura e sobe o laboratório de forma interativa — Windows, Linux e macOS.

Pergunta porta/usuário/senha/banco, valida que a porta está livre, grava .env
e sobe o container. Só usa a biblioteca padrão do Python, pra não depender de
bash (que não existe nativo no Windows).

Uso:
    python3 setup.py     # Linux / macOS
    python setup.py      # Windows
"""
from __future__ import annotations

import socket
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent


def porta_livre(porta: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("localhost", porta)) != 0


def perguntar(mensagem: str, padrao: str) -> str:
    resposta = input(f"{mensagem} [{padrao}]: ").strip()
    return resposta or padrao


def main() -> int:
    print("== Laboratório de Administração PostgreSQL ==\n")

    while True:
        porta_txt = perguntar("Em qual porta expor o Postgres no seu computador?", "5433")
        if not porta_txt.isdigit():
            print("  -> digite só números.")
            continue
        if porta_livre(int(porta_txt)):
            break
        print(f"  -> porta {porta_txt} já está em uso (talvez um Postgres local na 5432?). Escolha outra.")

    usuario = perguntar("Usuário do banco", "aluno")
    senha = perguntar("Senha do banco", "aluno123")
    banco = perguntar("Nome do banco", "loja")

    (RAIZ / ".env").write_text(
        f"POSTGRES_PORT={porta_txt}\n"
        f"POSTGRES_USER={usuario}\n"
        f"POSTGRES_PASSWORD={senha}\n"
        f"POSTGRES_DB={banco}\n",
        encoding="utf-8",
    )

    print("\nConfiguração salva em .env. Subindo o container...")
    try:
        subida = subprocess.run(["docker", "compose", "up", "-d"], cwd=RAIZ)
    except FileNotFoundError:
        print("\nComando 'docker' não encontrado. Instale o Docker Desktop e tente de novo.")
        return 1
    if subida.returncode != 0:
        print("\nFalhou ao subir o container — o Docker está rodando?")
        return 1

    print("\nPronto! Conecte no DBeaver com:")
    print("  Host:     localhost")
    print(f"  Porta:    {porta_txt}")
    print(f"  Database: {banco}")
    print(f"  Usuário:  {usuario}")
    print(f"  Senha:    {senha}")
    print("\nDriver: PostgreSQL (o DBeaver detecta e baixa o driver na primeira conexão).")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except EOFError:
        sys.exit("\nEntrada encerrada antes de terminar as perguntas — rode de novo num terminal interativo.")
