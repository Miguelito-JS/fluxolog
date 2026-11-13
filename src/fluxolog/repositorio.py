"""Camada de acesso a dados: guarda e busca tarefas em um banco SQLite.

O padrão Repositório separa "como os dados são salvos" do resto do sistema.
Se um dia o banco mudar (ex.: para PostgreSQL), só este arquivo precisa mudar.
"""

import sqlite3
from contextlib import closing
from dataclasses import replace

from .modelo import Tarefa

# Campos que o usuário pode alterar em uma tarefa já existente.
CAMPOS_EDITAVEIS = ("titulo", "descricao", "status")


class RepositorioTarefas:
    """Operações CRUD (Create, Read, Update, Delete) de tarefas no SQLite."""

    def __init__(self, caminho_banco: str) -> None:
        self.caminho_banco = caminho_banco
        self._criar_tabela()

    # ------------------------------------------------------------------ #
    # Funções internas
    # ------------------------------------------------------------------ #
    def _conectar(self) -> sqlite3.Connection:
        """Abre uma conexão. row_factory permite acessar colunas pelo nome."""
        conexao = sqlite3.connect(self.caminho_banco)
        conexao.row_factory = sqlite3.Row
        return conexao

    def _criar_tabela(self) -> None:
        """Cria a tabela de tarefas na primeira execução."""
        with closing(self._conectar()) as conexao, conexao:
            conexao.execute(
                """
                CREATE TABLE IF NOT EXISTS tarefas (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo    TEXT NOT NULL,
                    descricao TEXT NOT NULL DEFAULT '',
                    status    TEXT NOT NULL DEFAULT 'a_fazer',
                    criada_em TEXT NOT NULL
                )
                """
            )

    @staticmethod
    def _linha_para_tarefa(linha: sqlite3.Row) -> Tarefa:
        """Converte uma linha do banco em um objeto Tarefa."""
        return Tarefa(**dict(linha))

    # ------------------------------------------------------------------ #
    # CRUD
    # ------------------------------------------------------------------ #
    def criar(self, tarefa: Tarefa) -> Tarefa:
        """CREATE: salva uma nova tarefa e devolve ela já com o id gerado."""
        with closing(self._conectar()) as conexao, conexao:
            cursor = conexao.execute(
                "INSERT INTO tarefas (titulo, descricao, status, criada_em) "
                "VALUES (?, ?, ?, ?)",
                (tarefa.titulo, tarefa.descricao, tarefa.status, tarefa.criada_em),
            )
        return replace(tarefa, id=cursor.lastrowid)

    def listar(self, status: str | None = None) -> list[Tarefa]:
        """READ: lista as tarefas (opcionalmente só as de um status), mais antigas primeiro."""
        sql = "SELECT * FROM tarefas"
        parametros: tuple = ()
        if status:
            sql += " WHERE status = ?"
            parametros = (status,)
        sql += " ORDER BY id"
        with closing(self._conectar()) as conexao:
            linhas = conexao.execute(sql, parametros).fetchall()
        return [self._linha_para_tarefa(linha) for linha in linhas]

    def buscar(self, tarefa_id: int) -> Tarefa | None:
        """READ: busca uma tarefa pelo id. Devolve None se não existir."""
        with closing(self._conectar()) as conexao:
            linha = conexao.execute(
                "SELECT * FROM tarefas WHERE id = ?", (tarefa_id,)
            ).fetchone()
        return self._linha_para_tarefa(linha) if linha else None

    def atualizar(self, tarefa_id: int, **campos) -> Tarefa | None:
        """UPDATE: altera os campos informados. Devolve None se a tarefa não existir.

        O `replace` cria uma nova Tarefa, então a validação do modelo roda de novo
        e impede que uma alteração deixe a tarefa inválida.
        """
        atual = self.buscar(tarefa_id)
        if atual is None:
            return None
        alteracoes = {nome: valor for nome, valor in campos.items() if nome in CAMPOS_EDITAVEIS}
        nova = replace(atual, **alteracoes)
        with closing(self._conectar()) as conexao, conexao:
            conexao.execute(
                "UPDATE tarefas SET titulo = ?, descricao = ?, status = ? WHERE id = ?",
                (nova.titulo, nova.descricao, nova.status, tarefa_id),
            )
        return nova

    def remover(self, tarefa_id: int) -> bool:
        """DELETE: apaga a tarefa. Devolve True se algo foi apagado."""
        with closing(self._conectar()) as conexao, conexao:
            cursor = conexao.execute("DELETE FROM tarefas WHERE id = ?", (tarefa_id,))
        return cursor.rowcount > 0
