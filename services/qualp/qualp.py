from selenium.webdriver.support.ui import WebDriverWait
from services.qualp.navegador import Navegador
from services.qualp.auth.login import Login
from services.qualp.pesquisa import Pesquisa
from services.qualp.resultados import Resultados
from domain.models.resultado_rota import ResultadoRota
class QualP:

    def pesquisar(
            self,
            origem,
            destino,
            quantidade_eixos=6,
            calcular_volta=False
        ) -> ResultadoRota:

        driver = Navegador.iniciar()

        wait = WebDriverWait(driver, 15)

        Login.executar(
            driver,
            wait
            )
        
        try:

            Pesquisa.executar(
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
            pass