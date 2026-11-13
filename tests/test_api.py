"""Testes de integração da API REST (/api/tarefas)."""


def _criar(cliente, **dados):
    """Atalho: cria uma tarefa pela API e devolve a resposta."""
    return cliente.post("/api/tarefas", json=dados)


def test_lista_vazia(cliente):
    resposta = cliente.get("/api/tarefas")
    assert resposta.status_code == 200
    assert resposta.get_json() == []


def test_cria_tarefa(cliente):
    resposta = _criar(cliente, titulo="Roteirizar entregas", descricao="Zona norte")
    assert resposta.status_code == 201
    corpo = resposta.get_json()
    assert corpo["id"] == 1
    assert corpo["status"] == "a_fazer"


def test_criar_sem_titulo_retorna_400(cliente):
    resposta = _criar(cliente, descricao="sem título")
    assert resposta.status_code == 400
    assert "título" in resposta.get_json()["erro"]


def test_criar_com_status_invalido_retorna_400(cliente):
    assert _criar(cliente, titulo="Ok", status="pausado").status_code == 400


def test_criar_sem_json_retorna_400(cliente):
    resposta = cliente.post("/api/tarefas", data="texto", content_type="text/plain")
    assert resposta.status_code == 400


def test_busca_por_id(cliente):
    _criar(cliente, titulo="Inventário")
    resposta = cliente.get("/api/tarefas/1")
    assert resposta.status_code == 200
    assert resposta.get_json()["titulo"] == "Inventário"


def test_busca_inexistente_retorna_404(cliente):
    assert cliente.get("/api/tarefas/99").status_code == 404


def test_filtra_por_status(cliente):
    _criar(cliente, titulo="A")
    _criar(cliente, titulo="B", status="concluido")
    resposta = cliente.get("/api/tarefas?status=concluido")
    assert [t["titulo"] for t in resposta.get_json()] == ["B"]


def test_atualiza_status(cliente):
    _criar(cliente, titulo="Carga")
    resposta = cliente.put("/api/tarefas/1", json={"status": "em_progresso"})
    assert resposta.status_code == 200
    assert resposta.get_json()["status"] == "em_progresso"


def test_atualizar_com_dado_invalido_retorna_400(cliente):
    _criar(cliente, titulo="Carga")
    assert cliente.put("/api/tarefas/1", json={"titulo": ""}).status_code == 400


def test_atualizar_inexistente_retorna_404(cliente):
    assert cliente.put("/api/tarefas/99", json={"titulo": "x"}).status_code == 404


def test_remove_tarefa(cliente):
    _criar(cliente, titulo="Temporária")
    assert cliente.delete("/api/tarefas/1").status_code == 204
    assert cliente.get("/api/tarefas/1").status_code == 404


def test_remover_inexistente_retorna_404(cliente):
    assert cliente.delete("/api/tarefas/99").status_code == 404
