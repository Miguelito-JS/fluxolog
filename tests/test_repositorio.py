"""Testes do CRUD no banco SQLite."""

import pytest

from fluxolog.modelo import ErroValidacao, Tarefa


def test_criar_gera_id_e_salva(repositorio):
    tarefa = repositorio.criar(Tarefa(titulo="Agendar coleta"))
    assert tarefa.id is not None
    assert repositorio.buscar(tarefa.id).titulo == "Agendar coleta"


def test_listar_retorna_na_ordem_de_criacao(repositorio):
    repositorio.criar(Tarefa(titulo="Primeira"))
    repositorio.criar(Tarefa(titulo="Segunda"))
    assert [t.titulo for t in repositorio.listar()] == ["Primeira", "Segunda"]


def test_listar_filtra_por_status(repositorio):
    repositorio.criar(Tarefa(titulo="Pendente"))
    repositorio.criar(Tarefa(titulo="Feita", status="concluido"))
    concluidas = repositorio.listar(status="concluido")
    assert [t.titulo for t in concluidas] == ["Feita"]


def test_buscar_inexistente_retorna_none(repositorio):
    assert repositorio.buscar(999) is None


def test_atualizar_muda_status(repositorio):
    tarefa = repositorio.criar(Tarefa(titulo="Rota zona sul"))
    atualizada = repositorio.atualizar(tarefa.id, status="em_progresso")
    assert atualizada.status == "em_progresso"
    assert repositorio.buscar(tarefa.id).status == "em_progresso"


def test_atualizar_ignora_campos_nao_editaveis(repositorio):
    tarefa = repositorio.criar(Tarefa(titulo="Original"))
    atualizada = repositorio.atualizar(tarefa.id, id=42, titulo="Novo")
    assert atualizada.id == tarefa.id
    assert atualizada.titulo == "Novo"


def test_atualizar_com_dado_invalido_nao_altera_banco(repositorio):
    tarefa = repositorio.criar(Tarefa(titulo="Original"))
    with pytest.raises(ErroValidacao):
        repositorio.atualizar(tarefa.id, titulo="")
    assert repositorio.buscar(tarefa.id).titulo == "Original"


def test_atualizar_inexistente_retorna_none(repositorio):
    assert repositorio.atualizar(999, titulo="x") is None


def test_remover(repositorio):
    tarefa = repositorio.criar(Tarefa(titulo="Apagar"))
    assert repositorio.remover(tarefa.id) is True
    assert repositorio.buscar(tarefa.id) is None
    assert repositorio.remover(tarefa.id) is False
