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

_(As instruções de execução serão adicionadas assim que o código base estiver pronto.)_
