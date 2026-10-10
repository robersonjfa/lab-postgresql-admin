# Preparação das máquinas do laboratório

Documento separado do `roteiro.md` — este aqui é pra quem prepara as máquinas
**antes** da aula (professor, técnico do laboratório, ou o próprio aluno na
máquina dele), não pra ser seguido durante a atividade. Se as máquinas do
laboratório da universidade já tiverem tudo isso, nada a fazer; o objetivo é
ter uma lista única pra checar antes de uma turma usar o laboratório, em vez
de descobrir isso em cima da hora com 30 alunos esperando.

## Checklist rápido por máquina

- [ ] Docker instalado e **rodando** (serviço ativo, não só instalado)
- [ ] `docker compose version` funciona (Compose v2, vem embutido no Docker
  atual — se a máquina tiver um Docker muito antigo, pode faltar)
- [ ] Imagem `postgres:18` já baixada (ver "Pré-baixar a imagem" abaixo)
- [ ] [DBeaver Community](https://dbeaver.io/) instalado
- [ ] Python 3 instalado e no PATH (`python3 --version` ou `python --version`)
- [ ] Usuário do laboratório consegue rodar `docker` **sem precisar de
  administrador/sudo** a cada comando (ver "Permissões" abaixo)
- [ ] Pelo menos ~2 GB livres em disco por máquina (imagem + volume de dados)

## Por sistema operacional

### Windows
- Precisa de **Docker Desktop** com o backend **WSL2** (não o backend Hyper-V
  antigo). O próprio instalador do Docker Desktop guia a ativação do WSL2 —
  normalmente exige um reboot.
- Em máquinas corporativas/de laboratório, confirme que a virtualização está
  habilitada na BIOS/UEFI (`Intel VT-x`/`AMD-V`) — sem isso o WSL2 não roda e
  o Docker Desktop nem inicia. Isso costuma estar desabilitado por padrão em
  imagens corporativas "travadas".
- Depois de instalado, abra o Docker Desktop **uma vez** antes da aula pra
  confirmar que ele realmente inicia (ícone da bandeja fica "Engine running").
- Terminal recomendado pros alunos: PowerShell (vem padrão). O roteiro já foi
  escrito evitando comandos que só funcionam em bash (sem `<` de redirecionamento).

### Linux
- Docker Engine + plugin `docker compose` (`sudo apt install docker.io
  docker-compose-v2` em Debian/Ubuntu, ou seguir o guia oficial do Docker pra
  outras distros).
- **Permissões**: adicione o usuário do laboratório ao grupo `docker`
  (`sudo usermod -aG docker $USER`) e **faça logout/login** (ou reboot) pra
  o grupo valer — senão todo comando `docker` exige `sudo`, o que quebra o
  fluxo interativo do `setup.py` (ele chama `docker compose` sem `sudo`).

### macOS
- Docker Desktop (ou OrbStack, mais leve e com o mesmo CLI `docker`) —
  qualquer um funciona, o roteiro só depende do comando `docker`, não de qual
  app fornece o daemon.
- Nada de WSL2/virtualização manual aqui, o instalador cuida disso.

## Pré-baixar a imagem (evita depender da rede da sala no dia da aula)

A imagem `postgres:18` tem ~450 MB. Numa sala com Wi-Fi compartilhado entre
30 alunos baixando ao mesmo tempo, isso sozinho pode consumir a aula toda.
Baixe com antecedência em cada máquina (ou numa imagem/clone que será
distribuído pras máquinas do laboratório):

```bash
docker pull postgres:18
```

## Testando que uma máquina está pronta

Depois do checklist, valide com o próprio projeto (clona o repositório e roda
o setup uma vez, escolhendo uma porta de teste):

```bash
git clone https://github.com/robersonjfa/lab-postgresql-admin.git
cd lab-postgresql-admin
python3 setup.py   # ou: python setup.py
```

Se conectar no DBeaver com os dados impressos no final, a máquina está pronta.
Depois: `docker compose down -v` pra deixar limpo pra aula de verdade.

## Problemas comuns

- **"docker: command not found" logo após instalar (Linux)**: faltou abrir um
  terminal novo (ou reboot) depois da instalação — o PATH só atualiza em
  sessões novas.
- **"permission denied" ao rodar `docker ...` (Linux)**: usuário não está no
  grupo `docker`, ou entrou no grupo mas não relogou. `sudo` resolve na hora
  mas não é o que queremos pro `setup.py` interativo.
- **Docker Desktop não inicia no Windows**: geralmente é virtualização
  desabilitada na BIOS ou WSL2 não instalado — reinstalar o Docker Desktop
  não resolve isso, é configuração da máquina.
- **Porta já em uso**: normal se a máquina já tiver outro Postgres instalado
  (ex.: alguma disciplina anterior) — o `setup.py` já pergunta a porta e
  valida que está livre antes de subir o container; é só escolher outra.
