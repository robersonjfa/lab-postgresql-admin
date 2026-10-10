#!/usr/bin/env python3
"""Corrige em lote as entregas do laboratório de administração PostgreSQL.

Pra cada subpasta de entregas, sobe um container Postgres isolado (efêmero),
aplica a config que o aluno entregou, restaura o dump dele, roda os mesmos
checks do check_lab.py (via labcheck.py, compartilhado) e grava o resultado
em resultados.csv.

Fica deliberadamente fora do unoesc-tools — é um script independente; o
mapeamento desse CSV pra import_diary_grades/post_diary_grades é feito por
quem for integrar, depois.

Layout esperado de cada entrega:
    <pasta_raiz>/<identificacao_do_aluno>/postgresql.conf
    <pasta_raiz>/<identificacao_do_aluno>/pg_hba.conf
    <pasta_raiz>/<identificacao_do_aluno>/roles.sql
    <pasta_raiz>/<identificacao_do_aluno>/dump_final.sql

Uso:
    pip install psycopg2-binary
    python correcao/corrige_lab.py entregas/
"""
from __future__ import annotations

import csv
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from labcheck import nota, rodar_checks  # noqa: E402

IMAGEM = "postgres:18"
CONTAINER = "corrige_lab_tmp"
PORTA = "5532"  # porta efêmera no host, só durante a correção
PGUSER = "aluno"
PGPASSWORD = "aluno123"
PGDATABASE = "loja"
CONF_PATH = "/var/lib/postgresql/18/docker/postgresql.conf"
HBA_PATH = "/var/lib/postgresql/18/docker/pg_hba.conf"


def rodar(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True)


def limpar_container() -> None:
    rodar(["docker", "rm", "-f", "-v", CONTAINER])


def esperar_pronto(timeout: int = 30) -> bool:
    inicio = time.time()
    while time.time() - inicio < timeout:
        if rodar(["docker", "exec", CONTAINER, "pg_isready", "-U", PGUSER]).returncode == 0:
            return True
        time.sleep(1)
    return False


def corrigir_um(pasta: Path) -> tuple[float, str]:
    conf = pasta / "postgresql.conf"
    hba = pasta / "pg_hba.conf"
    roles = pasta / "roles.sql"
    dump = pasta / "dump_final.sql"
    faltando = [p.name for p in (conf, hba, roles, dump) if not p.exists()]
    if faltando:
        return 0.0, f"arquivos faltando na entrega: {', '.join(faltando)}"

    limpar_container()
    subida = rodar(
        [
            "docker", "run", "-d", "--name", CONTAINER,
            "-e", f"POSTGRES_USER={PGUSER}",
            "-e", f"POSTGRES_PASSWORD={PGPASSWORD}",
            "-e", f"POSTGRES_DB={PGDATABASE}",
            "-p", f"{PORTA}:5432",
            IMAGEM,
        ]
    )
    if subida.returncode != 0:
        return 0.0, f"container não subiu: {subida.stderr.strip()[:300]}"

    if not esperar_pronto():
        return 0.0, "container não ficou pronto a tempo"

    rodar(["docker", "cp", str(conf), f"{CONTAINER}:{CONF_PATH}"])
    rodar(["docker", "cp", str(hba), f"{CONTAINER}:{HBA_PATH}"])
    reinicio = rodar(["docker", "restart", CONTAINER])
    if reinicio.returncode != 0 or not esperar_pronto():
        return 0.0, "container não voltou após aplicar a config do aluno (config inválida?)"

    # roles primeiro: GRANT dentro do dump falha silenciosamente se a role
    # referenciada ainda não existir (pg_dump não exporta roles, só os GRANT).
    with roles.open("rb") as f:
        subprocess.run(
            ["docker", "exec", "-i", CONTAINER, "psql", "-U", PGUSER, "-d", PGDATABASE],
            stdin=f, capture_output=True, text=True,
        )

    with dump.open("rb") as f:
        restauracao = subprocess.run(
            ["docker", "exec", "-i", CONTAINER, "psql", "-U", PGUSER, "-d", PGDATABASE],
            stdin=f, capture_output=True, text=True,
        )
    if restauracao.returncode != 0:
        return 0.0, f"restore falhou: {restauracao.stderr.strip()[:300]}"

    resultados = rodar_checks(
        {"host": "localhost", "port": PORTA, "user": PGUSER, "password": PGPASSWORD, "dbname": PGDATABASE}
    )
    detalhe = "; ".join(f"{r.nome}({r.peso:.2f}pt)={'ok' if r.ok else 'falhou'}" for r in resultados)
    return nota(resultados), detalhe


def main() -> int:
    if len(sys.argv) != 2:
        sys.exit("uso: python corrige_lab.py <pasta_com_entregas>")

    raiz = Path(sys.argv[1])
    pastas = sorted(p for p in raiz.iterdir() if p.is_dir())
    if not pastas:
        sys.exit(f"nenhuma subpasta de entrega encontrada em {raiz}")

    linhas = []
    for pasta in pastas:
        print(f"Corrigindo {pasta.name}...")
        try:
            nota_final, detalhe = corrigir_um(pasta)
        except Exception as exc:
            nota_final, detalhe = 0.0, f"erro inesperado: {exc}"
        print(f"  nota={nota_final:.1f}  {detalhe}")
        linhas.append({"aluno": pasta.name, "nota": f"{nota_final:.1f}", "detalhe": detalhe})

    limpar_container()

    saida = raiz.parent / "resultados.csv"
    with saida.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["aluno", "nota", "detalhe"])
        writer.writeheader()
        writer.writerows(linhas)

    print(f"\nResultados gravados em {saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
