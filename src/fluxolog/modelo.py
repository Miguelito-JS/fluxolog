"""Modelo de domínio do FluxoLog: a classe Tarefa e suas regras de validação.

Toda regra sobre o que é uma tarefa "válida" fica concentrada aqui. Assim, tanto a
API quanto a interface web usam exatamente as mesmas regras.
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime

# Colunas do quadro Kanban (valores guardados no banco).
STATUS_VALIDOS = ("a_fazer", "em_progresso", "concluido")

# Nome amigável de cada status, usado na interface.
NOMES_STATUS = {
    "a_fazer": "A Fazer",
    "em_progresso": "Em Progresso",
    "concluido": "Concluído",
}

# MUDANÇA DE ESCOPO (v0.2): níveis de prioridade, do mais urgente ao menos urgente.
PRIORIDADES = ("critica", "alta", "media", "baixa")

NOMES_PRIORIDADE = {
    "critica": "Crítica",
    "alta": "Alta",
    "media": "Média",
    "baixa": "Baixa",
}

TITULO_MAX = 100
DESCRICAO_MAX = 500


class ErroValidacao(ValueError):
    """Erro lançado quando os dados de uma tarefa não passam na validação."""


def _agora() -> str:
    """Data e hora atual em texto (formato ISO), usada como data de criação."""
    return datetime.now().isoformat(timespec="seconds")


@dataclass
class Tarefa:
    """Uma tarefa do quadro Kanban.

    A validação roda automaticamente sempre que um objeto Tarefa é criado,
    então nunca existe uma Tarefa inválida dentro do sistema.
    """

    titulo: str
    descricao: str = ""
    status: str = "a_fazer"
    prioridade: str = "media"
    id: int | None = None
    criada_em: str = field(default_factory=_agora)

    def __post_init__(self) -> None:
        # Remove espaços extras antes de validar (" Entrega " vira "Entrega").
        if isinstance(self.titulo, str):
            self.titulo = self.titulo.strip()
        if isinstance(self.descricao, str):
            self.descricao = self.descricao.strip()
        self.validar()

    def validar(self) -> None:
        """Confere todas as regras de negócio. Lança ErroValidacao se algo estiver errado."""
        if not isinstance(self.titulo, str) or not self.titulo:
            raise ErroValidacao("O título é obrigatório.")
        if len(self.titulo) > TITULO_MAX:
            raise ErroValidacao(f"O título deve ter no máximo {TITULO_MAX} caracteres.")
        if not isinstance(self.descricao, str):
            raise ErroValidacao("A descrição deve ser um texto.")
        if len(self.descricao) > DESCRICAO_MAX:
            raise ErroValidacao(f"A descrição deve ter no máximo {DESCRICAO_MAX} caracteres.")
        if self.status not in STATUS_VALIDOS:
            raise ErroValidacao(
                f"Status inválido: '{self.status}'. Use um destes: {', '.join(STATUS_VALIDOS)}."
            )
        if self.prioridade not in PRIORIDADES:
            raise ErroValidacao(
                f"Prioridade inválida: '{self.prioridade}'. "
                f"Use uma destas: {', '.join(PRIORIDADES)}."
            )

    def para_dict(self) -> dict:
        """Converte a tarefa em dicionário (usado para responder em JSON na API)."""
        return asdict(self)
