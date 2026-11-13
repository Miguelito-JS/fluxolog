# FluxoLog — Gerenciador de Tarefas Ágil

Sistema web de gerenciamento de tarefas desenvolvido para uma **startup de logística** que precisa
acompanhar o fluxo de trabalho da equipe em tempo real, organizado no estilo Kanban.

> Projeto acadêmico da disciplina de Engenharia de Software (ADS — UniFECAF).

## Objetivo

Dar à equipe de operações uma ferramenta simples para registrar tarefas, ver em que etapa cada
uma está (**A Fazer → Em Progresso → Concluído**) e acompanhar o andamento do trabalho.

## Escopo inicial (versão 0.1)

- Cadastro de tarefas com título e descrição
- Listagem das tarefas separadas por status (quadro Kanban)
- Edição de tarefas e mudança de status
- Exclusão de tarefas
- Validação dos dados de entrada (título obrigatório, limites de tamanho, status válido)
- API REST (JSON) para integração com outros sistemas
- Testes automatizados e integração contínua com GitHub Actions

**Fora do escopo:** login de usuários, notificações e relatórios.

## Metodologia

O projeto segue um modelo **híbrido Scrum + Kanban**:

- **Kanban:** todo o trabalho fica visível no quadro do GitHub Projects, com as colunas
  *To Do (A Fazer)*, *In Progress (Em Progresso)* e *Done (Concluído)*.
- **Scrum:** o desenvolvimento foi dividido em sprints curtas, cada uma entregando uma parte
  funcional (modelo, banco, API, interface, CI).
- **Commits semânticos** (`feat`, `fix`, `test`, `docs`, `ci`, `chore`) para manter o histórico legível.

## Tecnologias

| Camada | Ferramenta |
|---|---|
| Linguagem | Python 3.11+ |
| Framework web | Flask |
| Banco de dados | SQLite (arquivo `fluxolog.db`, criado automaticamente) |
| Testes | pytest + pytest-cov |
| Qualidade de código | flake8 |
| Integração contínua | GitHub Actions |

## Estrutura do repositório

```
fluxolog/
├── .github/workflows/ci.yml   # pipeline de CI (flake8 + pytest)
├── docs/                      # documentação e diagramas UML
├── src/
│   ├── app.py                 # ponto de entrada (roda o servidor)
│   └── fluxolog/
│       ├── __init__.py        # criar_app(): monta o app Flask
│       ├── modelo.py          # classe Tarefa e validação de entradas
│       ├── repositorio.py     # CRUD no banco SQLite
│       ├── api.py             # API REST (JSON)
│       ├── web.py             # páginas HTML (quadro Kanban)
│       ├── templates/         # HTML (Jinja)
│       └── static/            # CSS
└── tests/                     # testes automatizados (pytest)
```

## Como executar

Pré-requisito: [Python 3.11 ou mais novo](https://www.python.org/downloads/).

```bash
# 1. Clonar o repositório
git clone https://github.com/SEU-USUARIO/fluxolog.git
cd fluxolog

# 2. Criar e ativar um ambiente virtual
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 3. Instalar as dependências
pip install -r requirements-dev.txt

# 4. Rodar o sistema
python src/app.py
```

Abra **http://127.0.0.1:5000** no navegador.

## Como rodar os testes e a verificação de qualidade

```bash
pytest -v                      # testes automatizados
pytest --cov=fluxolog          # testes + cobertura de código
flake8 src tests               # padrão de código (PEP 8)
```

Os mesmos comandos rodam automaticamente no **GitHub Actions** a cada `push` (aba *Actions*).

## API REST

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/tarefas` | Lista tarefas (filtro opcional `?status=a_fazer`) |
| POST | `/api/tarefas` | Cria tarefa — corpo: `{"titulo": "...", "descricao": "..."}` |
| GET | `/api/tarefas/<id>` | Busca uma tarefa |
| PUT | `/api/tarefas/<id>` | Atualiza título, descrição ou status |
| DELETE | `/api/tarefas/<id>` | Remove uma tarefa |

Dados inválidos retornam **400** com `{"erro": "mensagem"}`; tarefa inexistente retorna **404**.
