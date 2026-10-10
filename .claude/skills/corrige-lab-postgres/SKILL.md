---
name: corrige-lab-postgres
description: Corrige em lote as entregas do laboratório de administração PostgreSQL deste repositório (lab-postgresql-admin) — sobe um container efêmero por aluno, aplica a config entregue, restaura o dump, roda os checks e gera resultados.csv. Use quando o professor pedir pra corrigir/avaliar as entregas do laboratório de Postgres.
---

# Corrigir laboratório de PostgreSQL

Corrige as entregas usando `correcao/corrige_lab.py`. Esse script é independente
do `unoesc-tools` — não escreve nada lá, só gera um CSV local.

## Pré-requisito de layout

As entregas baixadas do Moodle devem estar organizadas assim antes de rodar:

```
entregas/
  <aluno>/postgresql.conf
  <aluno>/pg_hba.conf
  <aluno>/roles.sql
  <aluno>/dump_final.sql
```

Se vierem do Moodle em outro layout (zip único, nomes diferentes), organize nessa
estrutura antes — pergunte ao usuário onde estão as entregas baixadas se não for
óbvio a partir do pedido.

## Rodando a correção

```bash
pip install psycopg2-binary  # só na primeira vez
python correcao/corrige_lab.py entregas/
```

Isso gera `resultados.csv` (irmão da pasta de entregas) com colunas
`aluno,nota,detalhe`. Garanta que o Docker está rodando antes (`docker info`).

## Depois de rodar

- Leia `resultados.csv` e resuma pro professor: quantos alunos, nota média,
  quem tirou 0 e por quê (geralmente `detalhe` explica: arquivo faltando,
  config inválida ou restore falhou).
- **Não** lance nota em nenhum sistema (Portal, Moodle, `unoesc-tools`)
  automaticamente — isso é decisão explícita do professor, feita por fora
  desta skill.
- Se um aluno tirou 0 por erro de infraestrutura (ex.: container não subiu
  por falta de memória/porta ocupada na máquina onde a correção está rodando,
  não por erro do aluno), avise antes de reportar a nota — pode não refletir
  o trabalho real do aluno.

## Problemas comuns

- **"container não subiu"**: geralmente porta `5532` ocupada ou Docker não
  está rodando. Verifique com `docker ps` e `docker info`.
- **"restore falhou"**: normalmente SQL malformado no dump do aluno — olhe o
  trecho de erro impresso em `detalhe`.
- **role nunca existe mesmo quando o aluno fez certo**: confirme que
  `roles.sql` foi entregue — `pg_dump` não exporta roles (são objetos do
  cluster), só os `GRANT`; sem `roles.sql` o `GRANT` do dump falha em
  silêncio. Isso está documentado em `roteiro.md`.
