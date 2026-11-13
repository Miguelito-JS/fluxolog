"""Testes da interface web (páginas HTML e formulários)."""


def test_quadro_mostra_as_tres_colunas(cliente):
    html = cliente.get("/").get_data(as_text=True)
    assert "A Fazer" in html
    assert "Em Progresso" in html
    assert "Concluído" in html


def test_criar_pelo_formulario(cliente):
    resposta = cliente.post("/tarefas", data={"titulo": "Descarregar doca 3"},
                            follow_redirects=True)
    assert resposta.status_code == 200
    assert "Descarregar doca 3" in resposta.get_data(as_text=True)


def test_formulario_sem_titulo_mostra_erro(cliente):
    resposta = cliente.post("/tarefas", data={"titulo": "  "}, follow_redirects=True)
    assert "O título é obrigatório." in resposta.get_data(as_text=True)


def test_mover_tarefa_de_coluna(cliente):
    cliente.post("/tarefas", data={"titulo": "Mover"})
    cliente.post("/tarefas/1/mover", data={"status": "concluido"})
    assert cliente.get("/api/tarefas/1").get_json()["status"] == "concluido"


def test_editar_tarefa(cliente):
    cliente.post("/tarefas", data={"titulo": "Antigo"})
    assert cliente.get("/tarefas/1/editar").status_code == 200
    cliente.post("/tarefas/1/editar",
                 data={"titulo": "Novo", "descricao": "", "status": "em_progresso"})
    tarefa = cliente.get("/api/tarefas/1").get_json()
    assert (tarefa["titulo"], tarefa["status"]) == ("Novo", "em_progresso")


def test_excluir_tarefa(cliente):
    cliente.post("/tarefas", data={"titulo": "Excluir"})
    cliente.post("/tarefas/1/excluir")
    assert cliente.get("/api/tarefas/1").status_code == 404


def test_paginas_de_tarefa_inexistente_retornam_404(cliente):
    assert cliente.get("/tarefas/99/editar").status_code == 404
    assert cliente.post("/tarefas/99/excluir").status_code == 404
    assert cliente.post("/tarefas/99/mover", data={"status": "concluido"}).status_code == 404
