# Laboratório — Administração de PostgreSQL

Ambiente de laboratório (PostgreSQL 18) pra ensinar administração de PostgreSQL (parâmetros de
configuração, autenticação, roles/privilégios, backup e restore lógico) sem a
fricção de instalar/distribuir uma VM por aluno.

Cada aluno sobe o próprio ambiente localmente com Docker, numa porta configurável
(evita conflito com um Postgres que já exista na máquina) e acessa via DBeaver.

## Início rápido

```bash
git clone <este-repositório>
cd lab-postgresql-admin
./setup.sh
```

Siga depois o roteiro completo em [`roteiro.md`](roteiro.md).

## Estrutura

```
compose.yaml       # define o serviço Postgres
seed/init.sql       # dados de exemplo carregados automaticamente no 1º boot
setup.sh            # pergunta porta/usuário/senha/banco e sobe o ambiente
roteiro.md          # passo a passo da atividade
check_lab.py        # autoavaliação local (não lança nota)
entrega/            # onde o aluno coloca os arquivos pra entregar
```

## Requisitos
- Docker + Docker Compose
- [DBeaver](https://dbeaver.io/) (Community Edition)
- Python 3 (só pra rodar `check_lab.py`)
