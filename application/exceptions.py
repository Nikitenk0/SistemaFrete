class ErroAplicacao(Exception):
    """Erro esperado durante a execução de um caso de uso."""


class DadosOrcamentoInvalidos(ErroAplicacao):
    """Os dados fornecidos pelo usuário são inválidos."""


class RotaNaoEncontrada(ErroAplicacao):
    """Nenhuma rota foi encontrada para os dados informados."""


class FalhaPesquisaRota(ErroAplicacao):
    """Falha ao consultar o serviço responsável pela rota."""


class FalhaCalculoOrcamento(ErroAplicacao):
    """Falha ao processar os dados e calcular o orçamento."""