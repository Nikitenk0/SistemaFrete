from domain.models.resultado_rota import ResultadoRota
from infrastructure.qualp.auth.login import Login
from infrastructure.qualp.formulario_rota import FormularioRota
from infrastructure.qualp.resultados import Resultados
from infrastructure.qualp.sessao import SessaoQualP


class PesquisadorRotaQualP:

    def __init__(
        self,
        sessao: SessaoQualP | None = None
    ):
        self._sessao = (
            sessao
            if sessao is not None
            else SessaoQualP()
        )

    def pesquisar(
        self,
        origem: str,
        destino: str,
        quantidade_eixos: int = 6,
        calcular_volta: bool = False
    ) -> ResultadoRota:

        driver, wait = self._sessao.abrir()

        try:

            Login.executar(
                driver,
                wait
            )

            FormularioRota.preencher_e_calcular(
                driver,
                wait,
                origem,
                destino,
                quantidade_eixos,
                calcular_volta
            )

            resultado = Resultados.obter(
                driver,
                wait
            )

            return resultado

        finally:

            self._sessao.fechar()
