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
python3 setup.py   # Linux / macOS
python setup.py    # Windows
```

Siga depois o roteiro completo em [`roteiro.md`](roteiro.md) (inclui a
rubrica de avaliação). Se a máquina ainda não tem Docker/DBeaver/Python
configurados, veja antes [`preparacao-maquinas-lab.md`](preparacao-maquinas-lab.md).

## Estrutura

```
compose.yaml               # define o serviço Postgres
seed/init.sql               # dados de exemplo carregados automaticamente no 1º boot
setup.py                    # pergunta porta/usuário/senha/banco e sobe o ambiente (Windows/Linux/macOS)
roteiro.md                  # passo a passo da atividade + rubrica de avaliação
preparacao-maquinas-lab.md  # checklist pra quem prepara as máquinas do laboratório antes da aula
labcheck.py                 # checks + rubrica (pesos), compartilhado entre autoavaliação e correção
check_lab.py                # autoavaliação local do aluno (não lança nota)
correcao/                   # correção em lote do professor (independente, não toca no unoesc-tools)
entrega/                    # onde o aluno coloca os arquivos pra entregar
```

## Requisitos
- Docker + Docker Compose (Windows: Docker Desktop com backend WSL2)
- [DBeaver](https://dbeaver.io/) (Community Edition)
- Python 3 (`setup.py` e `check_lab.py`)

Testado em Linux e macOS; os comandos do `roteiro.md` evitam redirecionamento
de shell (`<`/`>`) propositalmente, pra funcionar igual no PowerShell do Windows.
