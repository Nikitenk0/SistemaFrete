import unittest
from unittest.mock import patch

from application.exceptions import (
    DadosOrcamentoInvalidos,
    FalhaCalculoOrcamento,
    FalhaPesquisaRota,
    RotaNaoEncontrada,
)
from application.use_cases.calcular_orcamento_fechado import (
    CalcularOrcamentoFechado
)
from domain.models.resultado_orcamento import ResultadoOrcamento
from domain.models.resultado_rota import ResultadoRota


class PesquisadorRotaFake:

    def __init__(
        self,
        resultado=None,
        erro=None
    ):
        self.resultado = resultado
        self.erro = erro
        self.consulta = None

    def pesquisar(
        self,
        origem,
        destino,
        quantidade_eixos,
        calcular_volta
    ):
        self.consulta = (
            origem,
            destino,
            quantidade_eixos,
            calcular_volta
        )

        if self.erro is not None:
            raise self.erro

        return self.resultado


class TestCalcularOrcamentoFechado(unittest.TestCase):

    def test_executa_fluxo_completo(self):

        rota = ResultadoRota(
            origem="Rio Branco/Acre",
            destino="Maceió/Alagoas",
            distancia="300 km",
            pedagio="R$ 100,00",
            geral="R$ 1.000,00"
        )

        pesquisador = PesquisadorRotaFake(
            resultado=rota
        )

        caso_de_uso = CalcularOrcamentoFechado(
            pesquisador_rota=pesquisador
        )

        orcamento = ResultadoOrcamento(
            valor_nota=100000.0,
            geral=1000.0,
            pedagio=100.0,
            custo=350.0,
            subtotal=1450.0,
            impostos=(),
            total=1450.0
        )

        with patch(
            (
                "application.use_cases."
                "calcular_orcamento_fechado."
                "calcular_orcamento"
            ),
            return_value=orcamento
        ) as calcular:

            resultado = caso_de_uso.executar(
                valor_nota="R$ 100.000,00",
                origem="Rio Branco",
                destino="Maceió",
                quantidade_eixos=6,
                calcular_volta=True
            )

        self.assertEqual(
            pesquisador.consulta,
            (
                "Rio Branco",
                "Maceió",
                6,
                True
            )
        )

        calcular.assert_called_once_with(
            valor_nota=100000.0,
            geral=1000.0,
            pedagio=100.0,
            localizacao_origem="Rio Branco/Acre",
            localizacao_destino="Maceió/Alagoas"
        )

        self.assertIs(
            resultado.rota,
            rota
        )

        self.assertIs(
            resultado.orcamento,
            orcamento
        )

    def test_rejeita_valor_da_nota_invalido(self):

        pesquisador = PesquisadorRotaFake()

        caso_de_uso = CalcularOrcamentoFechado(
            pesquisador_rota=pesquisador
        )

        with self.assertRaises(
            DadosOrcamentoInvalidos
        ):
            caso_de_uso.executar(
                valor_nota="valor inválido",
                origem="Rio Branco",
                destino="Maceió",
                quantidade_eixos=6,
                calcular_volta=False
            )

        self.assertIsNone(
            pesquisador.consulta
        )

    def test_converte_falha_da_pesquisa(self):

        pesquisador = PesquisadorRotaFake(
            erro=RuntimeError(
                "Falha externa"
            )
        )

        caso_de_uso = CalcularOrcamentoFechado(
            pesquisador_rota=pesquisador
        )

        with self.assertRaises(
            FalhaPesquisaRota
        ):
            caso_de_uso.executar(
                valor_nota="100000",
                origem="Rio Branco",
                destino="Maceió",
                quantidade_eixos=6,
                calcular_volta=False
            )

    def test_informa_rota_nao_encontrada(self):

        pesquisador = PesquisadorRotaFake(
            resultado=None
        )

        caso_de_uso = CalcularOrcamentoFechado(
            pesquisador_rota=pesquisador
        )

        with self.assertRaises(
            RotaNaoEncontrada
        ):
            caso_de_uso.executar(
                valor_nota="100000",
                origem="Rio Branco",
                destino="Maceió",
                quantidade_eixos=6,
                calcular_volta=False
            )

    def test_converte_falha_do_calculo(self):

        rota = ResultadoRota(
            origem="Rio Branco/Acre",
            destino="Maceió/Alagoas",
            distancia="300 km",
            pedagio="R$ 100,00",
            geral="R$ 1.000,00"
        )

        pesquisador = PesquisadorRotaFake(
            resultado=rota
        )

        caso_de_uso = CalcularOrcamentoFechado(
            pesquisador_rota=pesquisador
        )

        with patch(
            (
                "application.use_cases."
                "calcular_orcamento_fechado."
                "calcular_orcamento"
            ),
            side_effect=RuntimeError(
                "Falha no cálculo"
            )
        ):

            with self.assertRaises(
                FalhaCalculoOrcamento
            ):
                caso_de_uso.executar(
                    valor_nota="100000",
                    origem="Rio Branco",
                    destino="Maceió",
                    quantidade_eixos=6,
                    calcular_volta=False
                )


if __name__ == "__main__":
    unittest.main()