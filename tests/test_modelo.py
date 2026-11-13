"""Testes unitários da validação de entradas do modelo Tarefa."""

import pytest

from fluxolog.modelo import DESCRICAO_MAX, TITULO_MAX, ErroValidacao, Tarefa


def test_cria_tarefa_valida_com_valores_padrao():
    tarefa = Tarefa(titulo="Separar pedidos do galpão 2")
    assert tarefa.titulo == "Separar pedidos do galpão 2"
    assert tarefa.descricao == ""
    assert tarefa.status == "a_fazer"
    assert tarefa.id is None
    assert tarefa.criada_em  # data preenchida automaticamente


def test_remove_espacos_extras_do_titulo_e_descricao():
    tarefa = Tarefa(titulo="  Conferir nota fiscal  ", descricao="  urgente ")
    assert tarefa.titulo == "Conferir nota fiscal"
    assert tarefa.descricao == "urgente"


@pytest.mark.parametrize("titulo_invalido", ["", "   ", None, 123])
def test_rejeita_titulo_vazio_ou_que_nao_e_texto(titulo_invalido):
    with pytest.raises(ErroValidacao, match="título é obrigatório"):
        Tarefa(titulo=titulo_invalido)


def test_aceita_titulo_no_limite_maximo():
    assert len(Tarefa(titulo="a" * TITULO_MAX).titulo) == TITULO_MAX


def test_rejeita_titulo_acima_do_limite():
    with pytest.raises(ErroValidacao, match="no máximo"):
        Tarefa(titulo="a" * (TITULO_MAX + 1))


def test_rejeita_descricao_acima_do_limite():
    with pytest.raises(ErroValidacao, match="descrição"):
        Tarefa(titulo="Ok", descricao="x" * (DESCRICAO_MAX + 1))


def test_rejeita_status_inexistente():
    with pytest.raises(ErroValidacao, match="Status inválido"):
        Tarefa(titulo="Ok", status="pausado")


def test_para_dict_contem_todos_os_campos():
    dados = Tarefa(titulo="Ok").para_dict()
    assert set(dados) == {"id", "titulo", "descricao", "status", "prioridade", "criada_em"}
