"""Checks compartilhados entre a autoavaliação do aluno (check_lab.py) e a
correção em lote do professor (correcao/corrige_lab.py).

Fica um módulo só pra não duplicar a lista de regras em dois lugares.
"""
from __future__ import annotations

from dataclasses import dataclass

import psycopg2

# --- Ajuste aqui os valores esperados da atividade (o professor define por turma) ---
ESPERADO = {
    "max_connections": "50",
    "work_mem": "8MB",
}
TABELAS_ESPERADAS = {"cliente": 3, "produto": 3, "pedido": 3}
ROLE_ESPERADA = "leitor"


@dataclass
class Resultado:
    nome: str
    ok: bool
    detalhe: str = ""


def rodar_checks(conexao: dict) -> list[Resultado]:
    """Conecta no banco indicado em `conexao` e roda a bateria de checks.

    `conexao` deve ter host/port/user/password/dbname (os mesmos nomes aceitos
    por `psycopg2.connect`).
    """
    try:
        conn = psycopg2.connect(**conexao)
    except Exception as exc:
        return [Resultado("Conexão com o banco", False, str(exc))]

    resultados = [Resultado("Conexão com o banco", True)]
    with conn, conn.cursor() as cur:
        for parametro, valor_esperado in ESPERADO.items():
            cur.execute("SHOW %s" % parametro)  # nomes fixos, não vem de input externo
            valor_atual = cur.fetchone()[0]
            ok = valor_atual.strip().lower() == valor_esperado.strip().lower()
            resultados.append(
                Resultado(
                    f"Parâmetro {parametro}", ok,
                    f"esperado={valor_esperado} atual={valor_atual}",
                )
            )

        for tabela, linhas_esperadas in TABELAS_ESPERADAS.items():
            cur.execute("SELECT count(*) FROM %s" % tabela)
            total = cur.fetchone()[0]
            ok = total >= linhas_esperadas
            resultados.append(Resultado(f"Tabela {tabela} com dados", ok, f"linhas={total}"))

        cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (ROLE_ESPERADA,))
        existe_role = cur.fetchone() is not None
        resultados.append(Resultado(f"Role '{ROLE_ESPERADA}' criada", existe_role))

    return resultados


def nota(resultados: list[Resultado]) -> float:
    """Nota de 0 a 10, proporcional aos checks que passaram."""
    if not resultados:
        return 0.0
    return 10 * sum(r.ok for r in resultados) / len(resultados)
