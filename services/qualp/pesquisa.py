
from selenium.webdriver.support import expected_conditions as EC
from services.qualp.origem_destino import OrigemDestino
from services.qualp.eixos import Eixos
from services.qualp.volta import calcVolta
import services.qualp.seletores as sel

class Pesquisa:

    @staticmethod
    def executar(
        driver,
        wait,
        origem,
        destino,
        quantidade_eixos,
        calcular_volta
    ):

        OrigemDestino.preencher_origem(
            wait,
            origem
        )

        OrigemDestino.preencher_destino(
            driver,
            destino
        )

        # ========================================== # Continua o processo normalmente # ==========================================

        Eixos.definir_eixos(
            wait,
            quantidade_eixos
        )

        calcVolta.calcular_volta(
            driver,
            wait,
            calcular_volta
        )

        Pesquisa.clicar_calcular(
            driver,
            wait
        )
    

    @staticmethod
    def clicar_calcular(
        driver,
        wait
    ):
        botao_calcular = wait.until(
            EC.element_to_be_clickable(
                sel.BOTAO_CALCULAR
            )
        )

        driver.execute_script(
            "arguments[0].click();",
            botao_calcular
        )
        


