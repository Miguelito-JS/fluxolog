"""Testes da mudança de escopo v0.2: prioridade das tarefas."""

import sqlite3

import pytest

from fluxolog.modelo import ErroValidacao, Tarefa
from fluxolog.repositorio import RepositorioTarefas


def test_prioridade_padrao_e_media():
    assert Tarefa(titulo="Ok").prioridade == "media"


def test_rejeita_prioridade_invalida():
    with pytest.raises(ErroValidacao, match="Prioridade inválida"):
        Tarefa(titulo="Ok", prioridade="urgentissima")


def test_lista_ordena_da_mais_urgente_para_a_menos_urgente(repositorio):
    for titulo, prioridade in [("B", "baixa"), ("C", "critica"), ("M", "media"), ("A", "alta")]:
        repositorio.criar(Tarefa(titulo=titulo, prioridade=prioridade))
    assert [t.titulo for t in repositorio.listar()] == ["C", "A", "M", "B"]


def test_mesma_prioridade_mantem_ordem_de_criacao(repositorio):
    repositorio.criar(Tarefa(titulo="1", prioridade="critica"))
    repositorio.criar(Tarefa(titulo="2", prioridade="critica"))
    assert [t.titulo for t in repositorio.listar()] == ["1", "2"]


def test_filtra_por_status_e_prioridade_juntos(repositorio):
    repositorio.criar(Tarefa(titulo="Alvo", prioridade="critica"))
    repositorio.criar(Tarefa(titulo="Outro status", prioridade="critica", status="concluido"))
    repositorio.criar(Tarefa(titulo="Outra prioridade"))
    resultado = repositorio.listar(status="a_fazer", prioridade="critica")
    assert [t.titulo for t in resultado] == ["Alvo"]


def test_migra_banco_da_versao_anterior(caminho_banco):
    """Um banco criado na v0.1 (sem a coluna prioridade) continua funcionando."""
    with sqlite3.connect(caminho_banco) as conexao:
        conexao.execute(
            "CREATE TABLE tarefas (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT NOT NULL, "
            "descricao TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'a_fazer', "
            "criada_em TEXT NOT NULL)"
        )
        conexao.execute(
            "INSERT INTO tarefas (titulo, criada_em) VALUES ('Tarefa antiga', '2026-01-01')"
        )
    conexao.close()

    repositorio = RepositorioTarefas(caminho_banco)
    tarefa_antiga = repositorio.buscar(1)
    assert tarefa_antiga.titulo == "Tarefa antiga"
    assert tarefa_antiga.prioridade == "media"


def test_api_cria_e_filtra_por_prioridade(cliente):
    cliente.post("/api/tarefas", json={"titulo": "Normal"})
    resposta = cliente.post(
        "/api/tarefas", json={"titulo": "Pane no caminhão", "prioridade": "critica"}
    )
    assert resposta.status_code == 201
    assert resposta.status_code == 201
    criticas = cliente.get("/api/tarefas?prioridade=critica").get_json()
    assert [t["titulo"] for t in criticas] == ["Pane no caminhão"]


def test_api_rejeita_prioridade_invalida(cliente):
    resposta = cliente.post("/api/tarefas", json={"titulo": "X", "prioridade": "maxima"})
    assert resposta.status_code == 400


def test_quadro_mostra_etiqueta_de_prioridade(cliente):
    cliente.post("/tarefas", data={"titulo": "Atraso na rota", "prioridade": "critica"})
    html = cliente.get("/").get_data(as_text=True)
    assert "etiqueta-critica" in html
    assert "Crítica" in html
