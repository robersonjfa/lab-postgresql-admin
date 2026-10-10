# Laboratório — Administração de PostgreSQL

## Pré-requisitos
- Docker Desktop (ou Docker Engine + Compose) instalado e rodando.
- [DBeaver](https://dbeaver.io/) instalado (Community Edition é suficiente).

## 1. Subir o ambiente

```bash
./setup.sh
```

O script pergunta a porta (padrão `5433`, pra não conflitar com um Postgres que já exista
no seu computador na `5432`), usuário, senha e nome do banco. Ao final ele já sobe o
container e mostra os dados de conexão.

Pra parar: `docker compose stop`. Pra resetar tudo do zero (apaga os dados): `docker compose down -v`.

## 2. Conectar via DBeaver

Nova conexão → PostgreSQL → use os dados impressos pelo `setup.sh` (host `localhost`,
a porta que você escolheu, database, usuário e senha). Explore as tabelas `cliente`,
`produto` e `pedido` já carregadas.

## 3. Parâmetros de configuração

No PostgreSQL 18 (mudou em relação a versões anteriores), o arquivo de configuração
roda dentro do container em `/var/lib/postgresql/18/docker/postgresql.conf`.

1. Copie o arquivo pra fora pra poder editar:
   ```bash
   docker cp lab_postgres:/var/lib/postgresql/18/docker/postgresql.conf entrega/postgresql.conf
   ```
2. Edite `entrega/postgresql.conf` e ajuste (pelo menos):
   - `max_connections`
   - `shared_buffers`
   - `work_mem`
   - `log_statement` (ex.: `'all'`, pra ver todo comando executado no log)
3. Copie de volta e reinicie pra aplicar:
   ```bash
   docker cp entrega/postgresql.conf lab_postgres:/var/lib/postgresql/18/docker/postgresql.conf
   docker compose restart db
   ```
4. Confirme a mudança no DBeaver ou via `psql`:
   ```sql
   SHOW max_connections;
   SHOW work_mem;
   ```

## 4. Autenticação (`pg_hba.conf`)

Mesma mecânica do passo anterior, com `pg_hba.conf`:

```bash
docker cp lab_postgres:/var/lib/postgresql/18/docker/pg_hba.conf entrega/pg_hba.conf
```

Ajuste a regra de autenticação pra exigir `scram-sha-256` (em vez de `trust`/`md5`) e
copie de volta + `docker compose restart db`. Teste reconectando no DBeaver.

## 5. Roles e privilégios

Via DBeaver (SQL Editor) ou `psql`:

```sql
CREATE ROLE leitor LOGIN PASSWORD 'leitor123';
GRANT SELECT ON produto, cliente TO leitor;
```

Conecte uma nova conexão no DBeaver com o usuário `leitor` e confirme que:
- consegue fazer `SELECT` em `produto`;
- **não** consegue fazer `INSERT`/`UPDATE`/`DELETE`.

## 6. Backup lógico

```bash
docker compose exec db pg_dump -U aluno -d loja -F p > entrega/dump_final.sql
```

(ajuste usuário/banco se tiver mudado no `setup.sh`).

## 7. Restore (simulando perda de dados)

1. Simule um "acidente" apagando as tabelas (sem destruir o container/volume —
   **não** use `docker compose down -v` aqui, porque isso dispara de novo o
   `seed/init.sql` e colide com o restore do dump):
   ```sql
   DROP TABLE pedido, produto, cliente CASCADE;
   ```
2. Restaure a partir do dump:
   ```bash
   docker compose exec -T db psql -U aluno -d loja < entrega/dump_final.sql
   ```
3. Confirme no DBeaver que os dados voltaram.

## Entrega

Envie pelo Moodle:
- `entrega/postgresql.conf`
- `entrega/pg_hba.conf`
- `entrega/dump_final.sql`
- a saída do `check_lab.py` (rode `python check_lab.py` e anexe o resultado)
