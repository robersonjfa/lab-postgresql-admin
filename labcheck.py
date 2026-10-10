"""Checks compartilhados entre a autoavaliação do aluno (check_lab.py) e a
correção em lote do professor (correcao/corrige_lab.py).

Fica um módulo só pra não duplicar a lista de regras em dois lugares.

Cada check tem um peso (a rubrica) — a soma de todos os pesos dá 10.0.
A tabela com o significado de cada peso está documentada em roteiro.md,
na seção "Critério de avaliação". Mudar peso aqui sem atualizar lá (ou
vice-versa) desalinha o que o aluno lê do que é realmente cobrado.
"""
from __future__ import annotations

from dataclasses import dataclass

import psycopg2

# --- Ajuste aqui os valores esperados e os pesos da atividade (o professor
# define por turma) — a soma de todos os pesos usados em rodar_checks deve
# dar 10.0 pra nota() funcionar como "nota de 0 a 10". ---
PARAMETROS_ESPERADOS = {
    # parâmetro: (valor esperado, peso)
    "max_connections": ("50", 1.0),
    "work_mem": ("8MB", 1.0),
}
TABELAS_ESPERADAS = {
    # tabela: (linhas esperadas, peso)
    "cliente": (3, 1.67),
    "produto": (3, 1.67),
    "pedido": (3, 1.66),
}
PESO_AUTENTICACAO = 1.5
PESO_ROLE = 1.5
ROLE_ESPERADA = "leitor"


@dataclass
class Resultado:
    nome: str
    ok: bool
    peso: float
    detalhe: str = ""


def rodar_checks(conexao: dict) -> list[Resultado]:
    """Conecta no banco indicado em `conexao` e roda a bateria de checks.

    `conexao` deve ter host/port/user/password/dbname (os mesmos nomes aceitos
    por `psycopg2.connect`).
    """
    try:
        conn = psycopg2.connect(**conexao)
    except Exception as exc:
        # Peso 0: se nem conecta, não há o que pesar — nota() trata isso como 0.
        return [Resultado("Conexão com o banco", False, peso=0.0, detalhe=str(exc))]

    resultados = [Resultado("Conexão com o banco", True, peso=0.0)]
    with conn, conn.cursor() as cur:
        for parametro, (valor_esperado, peso) in PARAMETROS_ESPERADOS.items():
            cur.execute("SHOW %s" % parametro)  # nomes fixos, não vem de input externo
            valor_atual = cur.fetchone()[0]
            ok = valor_atual.strip().lower() == valor_esperado.strip().lower()
            resultados.append(
                Resultado(
                    f"Parâmetro {parametro}", ok, peso,
                    f"esperado={valor_esperado} atual={valor_atual}",
                )
            )

        for tabela, (linhas_esperadas, peso) in TABELAS_ESPERADAS.items():
            cur.execute("SELECT count(*) FROM %s" % tabela)
            total = cur.fetchone()[0]
            ok = total >= linhas_esperadas
            resultados.append(Resultado(f"Tabela {tabela} com dados", ok, peso, f"linhas={total}"))

        # Autenticação: a imagem oficial já publica "host all all all
        # scram-sha-256" por padrão (cobre a porta exposta no host) — ISSO
        # NÃO é evidência de que o aluno editou nada. O antes/depois real
        # está nas regras local/127.0.0.1/::1, que vêm como "trust" (sem
        # senha) por padrão. O check certo é: nenhuma regra "trust" restante.
        cur.execute("SELECT count(*) FROM pg_hba_file_rules WHERE auth_method = 'trust'")
        sem_trust = cur.fetchone()[0] == 0
        resultados.append(Resultado("pg_hba.conf sem regras 'trust'", sem_trust, PESO_AUTENTICACAO))

        cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (ROLE_ESPERADA,))
        existe_role = cur.fetchone() is not None
        resultados.append(Resultado(f"Role '{ROLE_ESPERADA}' criada", existe_role, PESO_ROLE))

    return resultados


def nota(resultados: list[Resultado]) -> float:
    """Nota de 0 a 10, proporcional ao peso dos checks que passaram (rubrica)."""
    peso_total = sum(r.peso for r in resultados)
    if not peso_total:
        return 0.0
    return 10 * sum(r.peso for r in resultados if r.ok) / peso_total
