"""Fixtures do pytest: objetos prontos reaproveitados pelos testes.

Cada teste recebe um banco SQLite novo dentro de uma pasta temporária,
então um teste nunca interfere no outro.
"""

import pytest

from fluxolog.repositorio import RepositorioTarefas


@pytest.fixture
def caminho_banco(tmp_path):
    """Caminho de um banco de dados vazio e temporário."""
    return str(tmp_path / "teste.db")


@pytest.fixture
def repositorio(caminho_banco):
    """Repositório de tarefas apontando para o banco temporário."""
    return RepositorioTarefas(caminho_banco)
