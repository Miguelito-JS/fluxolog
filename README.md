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

> A versão 0.2 ampliou este escopo com a **prioridade das tarefas**. Veja a seção
> [Gestão de mudanças](#gestão-de-mudanças-mudança-de-escopo-v02).

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
| GET | `/api/tarefas` | Lista tarefas, mais urgentes primeiro (filtros opcionais `?status=a_fazer&prioridade=critica`) |
| POST | `/api/tarefas` | Cria tarefa — corpo: `{"titulo": "...", "descricao": "...", "prioridade": "alta"}` |
| GET | `/api/tarefas/<id>` | Busca uma tarefa |
| PUT | `/api/tarefas/<id>` | Atualiza título, descrição, status ou prioridade |
| DELETE | `/api/tarefas/<id>` | Remove uma tarefa |

Dados inválidos retornam **400** com `{"erro": "mensagem"}`; tarefa inexistente retorna **404**.

Valores aceitos — `status`: `a_fazer`, `em_progresso`, `concluido` ·
`prioridade`: `critica`, `alta`, `media` (padrão), `baixa`.

## Gestão de mudanças (mudança de escopo v0.2)

### O que mudou

As tarefas passaram a ter **prioridade** (Crítica, Alta, Média, Baixa). O quadro mostra as
tarefas da mais urgente para a menos urgente, os cartões críticos têm destaque vermelho e a
API ganhou o filtro `?prioridade=`.

### Por que mudou (justificativa)

Depois de validar a versão 0.1, o cliente relatou que **ocorrências urgentes** — como um
veículo quebrado no meio da rota ou uma carga com prazo de entrega no mesmo dia — ficavam
misturadas com tarefas de rotina. Como a lista era ordenada só pela data de criação, uma
tarefa crítica criada depois ficava no fim da coluna e podia passar despercebida, gerando
atrasos nas entregas.

O próprio enunciado do cliente já pedia para **"priorizar tarefas críticas"**, e essa
necessidade não estava no escopo inicial. A mudança foi aceita porque:

- tem **alto valor** para o negócio (reduz atrasos em entregas);
- tem **baixo custo**: um campo novo no modelo, sem alterar a arquitetura;
- **não quebra** quem já usa o sistema (veja "Riscos" abaixo).

### Como a mudança foi gerenciada

1. **Registro:** criado o card *"Mudança de escopo: prioridade das tarefas"* na coluna
   *To Do* do Kanban, com a justificativa acima.
2. **Análise de impacto:** afeta modelo, banco de dados, API, interface e testes.
3. **Implementação:** commit `feat(prioridade): ...` com a nova funcionalidade.
4. **Controle de qualidade:** o GitHub Actions **falhou** logo após a implementação,
   porque um teste antigo não conhecia o campo novo. O problema foi corrigido no commit
   `test(prioridade): ...`, junto com 9 testes novos para a funcionalidade.
5. **Documentação:** atualização deste README e do documento teórico.
6. **Encerramento:** card movido para *Done*.

### Riscos e como foram tratados

| Risco | Tratamento |
|---|---|
| Bancos da v0.1 não têm a coluna `prioridade` | Migração automática (`_migrar()` em `repositorio.py`): a coluna é criada e as tarefas antigas recebem prioridade `media` |
| Clientes da API que não enviam prioridade | Campo opcional, com valor padrão `media` |
| Quebrar funcionalidades existentes | Toda a suíte de testes roda no CI antes de considerar a mudança concluída |

## Autor

**Miguel de Jesus Santos** — Análise e Desenvolvimento de Sistemas, UniFECAF.
