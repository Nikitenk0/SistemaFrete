from selenium.webdriver.support.ui import WebDriverWait

from domain.models.resultado_rota import ResultadoRota
from infrastructure.qualp.auth.login import Login
from infrastructure.qualp.navegador import Navegador
from infrastructure.qualp.formulario_rota import FormularioRota
from infrastructure.qualp.resultados import Resultados


class PesquisadorRotaQualP:

    def pesquisar(
        self,
        origem: str,
        destino: str,
        quantidade_eixos: int = 6,
        calcular_volta: bool = False
    ) -> ResultadoRota:

        driver = Navegador.iniciar()

        try:

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

        finally:

            driver.quit()