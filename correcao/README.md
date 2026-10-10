# Correção em lote (lado do professor)

Script independente — não depende do `unoesc-tools` nem escreve nada nele.
Pega as entregas dos alunos, corrige automaticamente e gera um CSV com a nota
de cada um. O que fazer com esse CSV (lançar no Portal, importar no Moodle
via `unoesc-tools`) é um passo manual/separado, por decisão do professor.

## Uso

1. Organize as entregas baixadas do Moodle assim:
   ```
   entregas/
     joao.silva/
       postgresql.conf
       pg_hba.conf
       roles.sql
       dump_final.sql
     maria.souza/
       postgresql.conf
       pg_hba.conf
       roles.sql
       dump_final.sql
   ```
2. Rode:
   ```bash
   pip install psycopg2-binary
   python correcao/corrige_lab.py entregas/
   ```
3. O resultado fica em `resultados.csv` (irmão da pasta `entregas/`), com
   colunas `aluno,nota,detalhe`.

## Como funciona

Pra cada aluno, o script sobe um container `postgres:18` isolado e **efêmero**,
aplica a config entregue, restaura o dump entregue, roda os mesmos checks do
`check_lab.py` (compartilhados via `labcheck.py` na raiz do projeto) e depois
destrói o container — nada fica persistido entre um aluno e o próximo.

Se a config do aluno for inválida (ex.: erro de sintaxe no `postgresql.conf`)
ou o restore falhar, a nota fica `0.0` com o motivo registrado em `detalhe`,
em vez de travar a correção dos demais.
