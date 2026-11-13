"""Pacote principal do FluxoLog.

`criar_app` é uma "app factory" (fábrica de aplicação): monta e devolve o app Flask.
Isso permite criar um app separado para os testes, com um banco temporário.
"""

import os

from flask import Flask

from .repositorio import RepositorioTarefas


def criar_app(configuracao: dict | None = None) -> Flask:
    """Cria o app Flask, conecta o banco e registra as rotas."""
    app = Flask(__name__)
    app.config.update(
        DATABASE=os.environ.get("FLUXOLOG_DB", "fluxolog.db"),
        # Chave usada pelo Flask para as mensagens de aviso (flash).
        # Em produção, defina a variável de ambiente FLUXOLOG_SECRET.
        SECRET_KEY=os.environ.get("FLUXOLOG_SECRET", "chave-de-desenvolvimento"),
    )
    if configuracao:
        app.config.update(configuracao)

    # Um único repositório para o app inteiro, acessível pelas rotas.
    app.extensions["repositorio"] = RepositorioTarefas(app.config["DATABASE"])

    from .api import api_bp
    from .web import web_bp

    app.register_blueprint(api_bp)
    app.register_blueprint(web_bp)
    return app
