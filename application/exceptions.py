class ApplicationError(Exception):
    """Erro esperado durante a execução de um caso de uso."""


class InvalidQuoteDataError(ApplicationError):
    """Os dados fornecidos pelo usuário são inválidos."""


class RouteNotFoundError(ApplicationError):
    """Nenhuma rota foi encontrada para os dados informados."""


class RouteSearchError(ApplicationError):
    """Falha ao consultar o serviço responsável pela rota."""


class QuoteCalculationError(ApplicationError):
    """Falha ao processar os dados e calcular o orçamento."""

class QuotePdfGenerationError(ApplicationError):
    """Falha ao gerar o documento PDF do orçamento."""