from application.dtos.resultado_orcamento_fechado import (
    ResultadoOrcamentoFechado
)
from application.ports.pesquisador_rota import PesquisadorRota
from application.exceptions import (
    DadosOrcamentoInvalidos,
    FalhaCalculoOrcamento,
    FalhaPesquisaRota,
    RotaNaoEncontrada,
)
from domain.calculo.orcamento import calcular_orcamento
from domain.models.resultado_rota import ResultadoRota
from utils.conversao_monetaria import converter_valor_monetario


class CalcularOrcamentoFechado:

    def __init__(
        self,
        pesquisador_rota: PesquisadorRota
    ):
        self._pesquisador_rota = pesquisador_rota

    def executar(
        self,
        valor_nota: str | int | float,
        origem: str,
        destino: str,
        quantidade_eixos: int,
        calcular_volta: bool
    ) -> ResultadoOrcamentoFechado:

        try:
            valor_nota_convertido = converter_valor_monetario(
                valor_nota
            )

        except ValueError as erro:
            raise DadosOrcamentoInvalidos(
                "Valor da nota inválido"
            ) from erro

        try:
            resultado_rota = self._pesquisador_rota.pesquisar(
                origem,
                destino,
                quantidade_eixos,
                calcular_volta
            )

        except Exception as erro:
            raise FalhaPesquisaRota(
                "Não foi possível pesquisar a rota"
            ) from erro

        if resultado_rota is None:
            raise RotaNaoEncontrada(
                "Nenhuma rota encontrada"
            )

        try:
            geral = converter_valor_monetario(
                resultado_rota.geral
            )

            pedagio = converter_valor_monetario(
                resultado_rota.pedagio
            )

            resultado_orcamento = calcular_orcamento(
                valor_nota=valor_nota_convertido,
                geral=geral,
                pedagio=pedagio,
                localizacao_origem=resultado_rota.origem,
                localizacao_destino=resultado_rota.destino
            )

        except Exception as erro:
            raise FalhaCalculoOrcamento(
                "Não foi possível calcular o orçamento"
            ) from erro

        return ResultadoOrcamentoFechado(
            rota=resultado_rota,
            orcamento=resultado_orcamento
        )