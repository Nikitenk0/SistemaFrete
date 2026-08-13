from selenium.webdriver.support.ui import WebDriverWait

from domain.models.resultado_rota import ResultadoRota
from services.qualp.auth.login import Login
from services.qualp.navegador import Navegador
from services.qualp.formulario_rota import FormularioRota
from services.qualp.resultados import Resultados


class PesquisadorRotaQualP:

    def pesquisar(
        self,
        origem: str,
        destino: str,
        quantidade_eixos: int = 6,
        calcular_volta: bool = False
    ) -> ResultadoRota:

        driver = Navegador.iniciar()

        wait = WebDriverWait(
            driver,
            15
        )

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