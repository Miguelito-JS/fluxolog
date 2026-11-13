"""Interface web do FluxoLog: páginas HTML com o quadro Kanban.

Usa formulários HTML simples (sem JavaScript). Cada ação envia um POST e,
depois, redireciona de volta para o quadro (padrão Post/Redirect/Get).
"""

from flask import (Blueprint, abort, current_app, flash, redirect, render_template,
                   request, url_for)

from .modelo import NOMES_PRIORIDADE, NOMES_STATUS, STATUS_VALIDOS, ErroValidacao, Tarefa

web_bp = Blueprint("web", __name__)


def _repositorio():
    return current_app.extensions["repositorio"]


@web_bp.get("/")
def quadro():
    """Página inicial: mostra as tarefas agrupadas nas três colunas do Kanban."""
    colunas = {status: _repositorio().listar(status=status) for status in STATUS_VALIDOS}
    return render_template("quadro.html", colunas=colunas, nomes_status=NOMES_STATUS,
                           nomes_prioridade=NOMES_PRIORIDADE)


@web_bp.post("/tarefas")
def criar():
    try:
        _repositorio().criar(
            Tarefa(
                titulo=request.form.get("titulo", ""),
                descricao=request.form.get("descricao", ""),
                prioridade=request.form.get("prioridade", "media"),
            )
        )
        flash("Tarefa criada!", "sucesso")
    except ErroValidacao as erro:
        flash(str(erro), "erro")
    return redirect(url_for("web.quadro"))


@web_bp.post("/tarefas/<int:tarefa_id>/mover")
def mover(tarefa_id: int):
    """Muda a tarefa de coluna (ex.: de A Fazer para Em Progresso)."""
    try:
        if _repositorio().atualizar(tarefa_id, status=request.form.get("status")) is None:
            abort(404)
    except ErroValidacao as erro:
        flash(str(erro), "erro")
    return redirect(url_for("web.quadro"))


@web_bp.route("/tarefas/<int:tarefa_id>/editar", methods=["GET", "POST"])
def editar(tarefa_id: int):
    tarefa = _repositorio().buscar(tarefa_id)
    if tarefa is None:
        abort(404)
    if request.method == "POST":
        try:
            _repositorio().atualizar(
                tarefa_id,
                titulo=request.form.get("titulo", ""),
                descricao=request.form.get("descricao", ""),
                status=request.form.get("status", tarefa.status),
                prioridade=request.form.get("prioridade", tarefa.prioridade),
            )
            flash("Tarefa atualizada!", "sucesso")
            return redirect(url_for("web.quadro"))
        except ErroValidacao as erro:
            flash(str(erro), "erro")
    return render_template("editar.html", tarefa=tarefa, nomes_status=NOMES_STATUS,
                           nomes_prioridade=NOMES_PRIORIDADE)


@web_bp.post("/tarefas/<int:tarefa_id>/excluir")
def excluir(tarefa_id: int):
    if not _repositorio().remover(tarefa_id):
        abort(404)
    flash("Tarefa excluída.", "sucesso")
    return redirect(url_for("web.quadro"))
