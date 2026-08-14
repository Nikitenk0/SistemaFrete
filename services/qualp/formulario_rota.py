from selenium.webdriver.support import expected_conditions as EC

from services.qualp.origem_destino import OrigemDestino
from services.qualp.eixos import Eixos
from services.qualp.volta import Volta

import services.qualp.seletores as sel


class FormularioRota:

    @staticmethod
    def preencher_e_calcular(
        driver,
        wait,
        origem,
        destino,
        quantidade_eixos,
        calcular_volta
    ):

        input_destino = OrigemDestino.preencher_origem(
            driver,
            wait,
            origem
        )

        OrigemDestino.preencher_destino(
            driver,
            wait,
            input_destino,
            destino
        )

        Eixos.definir_eixos(
            wait,
            quantidade_eixos
        )

        Volta.configurar(
            driver,
            wait,
            calcular_volta
        )

        FormularioRota.clicar_calcular(
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