import time

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

import services.qualp.seletores as sel


class OrigemDestino:

    @staticmethod
    def preencher_origem(wait, origem):

        caixa_origem = wait.until(
            EC.element_to_be_clickable(
                sel.CAMPO_ORIGEM
            )
        )

        caixa_origem.click()

        input_origem = wait.until(
            EC.element_to_be_clickable(
                sel.CAMPO_ORIGEM
            )
        )

        input_origem.send_keys(origem)

        time.sleep(2)

        input_origem.send_keys(Keys.ENTER)

        time.sleep(2)

    @staticmethod
    def preencher_destino(driver, destino):

        input_destino = (
            driver.switch_to.active_element
        )

        input_destino.send_keys(destino)

        time.sleep(2)

        input_destino.send_keys(Keys.ENTER)

        time.sleep(2)

    @staticmethod
    def obter_origem(driver):

        input_origem = driver.find_element(
            *sel.CAMPO_ORIGEM
        )

        return input_origem.get_attribute(
            "value"
        )

    @staticmethod
    def obter_destino(driver):

        input_destino = driver.find_element(
            *sel.CAMPO_DESTINO
        )

        return input_destino.get_attribute(
            "value"
        )