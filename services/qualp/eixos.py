import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import services.qualp.seletores as sel


class Eixos:


    @staticmethod
    def definir_eixos(
        wait,
        quantidade_eixos
    ):
        controle_eixos = wait.until(
            EC.presence_of_element_located(
                sel.CONTROLE_EIXOS
            )
        )

        campo_eixos = controle_eixos.find_element(
            *sel.CAMPO_EIXOS
        )

        botoes = controle_eixos.find_elements(
            By.CLASS_NAME,
            "q-icon"
        )

        botao_diminuir = botoes[0]
        botao_aumentar = botoes[1]

        def obter_valor():
            return int(
                campo_eixos.get_attribute("value").split()[0]
            )
        
        eixos_atuais = obter_valor()

        while eixos_atuais < quantidade_eixos:

            valor_anterior = obter_valor()

            botao_aumentar.click()

            wait.until(
                lambda driver:
                obter_valor() > valor_anterior
            )

            eixos_atuais = obter_valor()

        while eixos_atuais > quantidade_eixos:

            valor_anterior = obter_valor()

            botao_diminuir.click()

            wait.until(
                lambda driver:
                obter_valor() < valor_anterior
            )

            eixos_atuais = obter_valor()
