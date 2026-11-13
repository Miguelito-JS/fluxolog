"""API REST do FluxoLog: rotas que recebem e devolvem JSON.

| Método | Rota                | Ação                          |
|--------|---------------------|-------------------------------|
| GET    | /api/tarefas        | lista tarefas (?status=...)   |
| POST   | /api/tarefas        | cria uma tarefa               |
| GET    | /api/tarefas/<id>   | busca uma tarefa              |
| PUT    | /api/tarefas/<id>   | atualiza uma tarefa           |
| DELETE | /api/tarefas/<id>   | remove uma tarefa             |
"""

from flask import Blueprint, current_app, jsonify, request

from .modelo import ErroValidacao, Tarefa
from .repositorio import CAMPOS_EDITAVEIS

api_bp = Blueprint("api", __name__, url_prefix="/api/tarefas")


def _repositorio():
    """Atalho para o repositório criado em criar_app()."""
    return current_app.extensions["repositorio"]


def _erro(mensagem: str, codigo: int):
    """Resposta de erro padronizada: {"erro": "..."} com o código HTTP."""
    return jsonify({"erro": mensagem}), codigo


def _ler_json() -> dict | None:
    """Lê o corpo da requisição. Devolve None se não for um objeto JSON."""
    dados = request.get_json(silent=True)
    return dados if isinstance(dados, dict) else None


@api_bp.errorhandler(ErroValidacao)
def _tratar_erro_validacao(erro):
    """Qualquer ErroValidacao lançado nas rotas vira uma resposta 400 (Bad Request)."""
    return _erro(str(erro), 400)


@api_bp.get("")
def listar_tarefas():
    tarefas = _repositorio().listar(status=request.args.get("status"))
    return jsonify([t.para_dict() for t in tarefas])


@api_bp.post("")
def criar_tarefa():
    dados = _ler_json()
    if dados is None:
        return _erro("Envie um objeto JSON no corpo da requisição.", 400)
    campos = {nome: dados[nome] for nome in CAMPOS_EDITAVEIS if nome in dados}
    tarefa = _repositorio().criar(Tarefa(**{"titulo": "", **campos}))
    return jsonify(tarefa.para_dict()), 201


@api_bp.get("/<int:tarefa_id>")
def buscar_tarefa(tarefa_id: int):
    tarefa = _repositorio().buscar(tarefa_id)
    if tarefa is None:
        return _erro("Tarefa não encontrada.", 404)
    return jsonify(tarefa.para_dict())


@api_bp.put("/<int:tarefa_id>")
def atualizar_tarefa(tarefa_id: int):
    dados = _ler_json()
    if dados is None:
        return _erro("Envie um objeto JSON no corpo da requisição.", 400)
    campos = {nome: dados[nome] for nome in CAMPOS_EDITAVEIS if nome in dados}
    tarefa = _repositorio().atualizar(tarefa_id, **campos)
    if tarefa is None:
        return _erro("Tarefa não encontrada.", 404)
    return jsonify(tarefa.para_dict())


@api_bp.delete("/<int:tarefa_id>")
def remover_tarefa(tarefa_id: int):
    if not _repositorio().remover(tarefa_id):
        return _erro("Tarefa não encontrada.", 404)
    return "", 204
