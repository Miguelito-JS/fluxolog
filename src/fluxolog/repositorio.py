"""Camada de acesso a dados: guarda e busca tarefas em um banco SQLite.

O padrão Repositório separa "como os dados são salvos" do resto do sistema.
Se um dia o banco mudar (ex.: para PostgreSQL), só este arquivo precisa mudar.
"""

import sqlite3
from contextlib import closing
from dataclasses import replace

from .modelo import Tarefa

# Campos que o usuário pode alterar em uma tarefa já existente.
CAMPOS_EDITAVEIS = ("titulo", "descricao", "status", "prioridade")

# Ordena do mais urgente para o menos urgente; empates ficam na ordem de criação.
ORDEM_PRIORIDADE = (
    "CASE prioridade WHEN 'critica' THEN 0 WHEN 'alta' THEN 1 "
    "WHEN 'media' THEN 2 ELSE 3 END, id"
)


class RepositorioTarefas:
    """Operações CRUD (Create, Read, Update, Delete) de tarefas no SQLite."""

    def __init__(self, caminho_banco: str) -> None:
        self.caminho_banco = caminho_banco
        self._criar_tabela()
        self._migrar()

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

    def _migrar(self) -> None:
        """MUDANÇA DE ESCOPO (v0.2): adiciona a coluna `prioridade` em bancos antigos.

        Quem já usava a versão 0.1 tem um banco sem essa coluna. Em vez de apagar
        os dados, a coluna é criada e as tarefas existentes recebem prioridade "media".
        """
        with closing(self._conectar()) as conexao, conexao:
            colunas = [linha["name"] for linha in conexao.execute("PRAGMA table_info(tarefas)")]
            if "prioridade" not in colunas:
                conexao.execute(
                    "ALTER TABLE tarefas ADD COLUMN prioridade TEXT NOT NULL DEFAULT 'media'"
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
                "INSERT INTO tarefas (titulo, descricao, status, prioridade, criada_em) "
                "VALUES (?, ?, ?, ?, ?)",
                (tarefa.titulo, tarefa.descricao, tarefa.status, tarefa.prioridade,
                 tarefa.criada_em),
            )
        return replace(tarefa, id=cursor.lastrowid)

    def listar(self, status: str | None = None,
               prioridade: str | None = None) -> list[Tarefa]:
        """READ: lista as tarefas, das mais urgentes para as menos urgentes.

        Os filtros `status` e `prioridade` são opcionais e podem ser combinados.
        """
        filtros = []
        parametros: list = []
        if status:
            filtros.append("status = ?")
            parametros.append(status)
        if prioridade:
            filtros.append("prioridade = ?")
            parametros.append(prioridade)
        sql = "SELECT * FROM tarefas"
        if filtros:
            sql += " WHERE " + " AND ".join(filtros)
        sql += " ORDER BY " + ORDEM_PRIORIDADE
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
                "UPDATE tarefas SET titulo = ?, descricao = ?, status = ?, prioridade = ? "
                "WHERE id = ?",
                (nova.titulo, nova.descricao, nova.status, nova.prioridade, tarefa_id),
            )
        return nova

    def remover(self, tarefa_id: int) -> bool:
        """DELETE: apaga a tarefa. Devolve True se algo foi apagado."""
        with closing(self._conectar()) as conexao, conexao:
            cursor = conexao.execute("DELETE FROM tarefas WHERE id = ?", (tarefa_id,))
        return cursor.rowcount > 0
