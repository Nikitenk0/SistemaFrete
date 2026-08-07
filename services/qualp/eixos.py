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

        botoes = controle_eixos.find_elements(
            By.CLASS_NAME,
            "q-icon"
        )

        botao_diminuir = botoes[0]
        botao_aumentar = botoes[1]

        eixos_atuais = 6

        while eixos_atuais < quantidade_eixos:
            botao_aumentar.click()
            eixos_atuais += 1
            time.sleep(0.3)

        while eixos_atuais > quantidade_eixos:
            botao_diminuir.click()
            eixos_atuais -= 1
            time.sleep(0.3)


