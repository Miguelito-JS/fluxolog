"""Fixtures do pytest: objetos prontos reaproveitados pelos testes.

Cada teste recebe um banco SQLite novo dentro de uma pasta temporária,
então um teste nunca interfere no outro.
"""

import pytest

from fluxolog import criar_app
from fluxolog.repositorio import RepositorioTarefas


@pytest.fixture
def caminho_banco(tmp_path):
    """Caminho de um banco de dados vazio e temporário."""
    return str(tmp_path / "teste.db")


@pytest.fixture
def repositorio(caminho_banco):
    """Repositório de tarefas apontando para o banco temporário."""
    return RepositorioTarefas(caminho_banco)


@pytest.fixture
def cliente(caminho_banco):
    """Cliente HTTP de teste do Flask: faz requisições sem subir o servidor."""
    app = criar_app({"DATABASE": caminho_banco, "TESTING": True})
    return app.test_client()
