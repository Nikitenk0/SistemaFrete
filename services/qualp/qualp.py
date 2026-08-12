import time
from selenium.webdriver.support.ui import WebDriverWait
from services.navegador import Navegador
from services.qualp.auth.login import Login
from services.qualp.pesquisa import Pesquisa
from services.qualp.resultados import Resultados

class QualP:

    def pesquisar(
            self,
            origem,
            destino,
            quantidade_eixos=6,
            calcular_volta=False
        ):

        driver = Navegador.iniciar()

        wait = WebDriverWait(driver, 15)

        Login.executar(
            driver,
            wait
            )
        
        try:

            localizacoes = Pesquisa.executar(
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