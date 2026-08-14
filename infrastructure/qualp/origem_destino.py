import unicodedata

from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException
)
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

import infrastructure.qualp.seletores as sel


class OrigemDestino:

    @staticmethod
    def normalizar_texto(texto):

        texto_normalizado = unicodedata.normalize(
            "NFD",
            texto
        )

        texto_sem_acentos = "".join(
            caractere
            for caractere in texto_normalizado
            if unicodedata.category(caractere) != "Mn"
        )

        return texto_sem_acentos.casefold().strip()

    @staticmethod

    def aguardar_sugestao(
        wait,
        texto_pesquisado
    ):

        texto_normalizado = (
            OrigemDestino.normalizar_texto(
                texto_pesquisado
            )
        )

        def sugestao_compativel(driver):

            try:

                item_ativo = driver.find_element(
                    *sel.AUTOCOMPLETE_ITEM_ATIVO
                )

                texto_item = (
                    OrigemDestino.normalizar_texto(
                        item_ativo.text
                    )
                )

                if (
                    texto_normalizado
                    and texto_normalizado in texto_item
                ):
                    return item_ativo

            except (
                NoSuchElementException,
                StaleElementReferenceException
            ):
                return False

            return False

        return wait.until(
            sugestao_compativel
        )

    @staticmethod
    def preencher_origem(
        driver,
        wait,
        origem
    ):

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

        input_origem.send_keys(
            origem
        )

        wait.until(
            lambda _driver:
            input_origem
            .get_attribute("value")
            .strip()
            == origem.strip()
        )

        OrigemDestino.aguardar_sugestao(
            wait,
            origem
        )

        input_origem.send_keys(
            Keys.ENTER
        )

        input_destino = (
            OrigemDestino.aguardar_destino_estavel(
                wait,
                input_origem
            )
        )

        return input_destino


    @staticmethod
    def aguardar_destino_estavel(
        wait,
        input_origem
    ):

        estado = {
            "elemento_id": None,
            "confirmacoes": 0
        }

        def destino_estavel(driver):

            elemento = (
                driver.switch_to.active_element
            )

            if elemento == input_origem:
                estado["elemento_id"] = None
                estado["confirmacoes"] = 0
                return False

            if elemento.tag_name.lower() != "input":
                estado["elemento_id"] = None
                estado["confirmacoes"] = 0
                return False

            if not elemento.is_displayed():
                estado["elemento_id"] = None
                estado["confirmacoes"] = 0
                return False

            if not elemento.is_enabled():
                estado["elemento_id"] = None
                estado["confirmacoes"] = 0
                return False

            elemento_id = elemento.id

            if (
                estado["elemento_id"]
                == elemento_id
            ):
                estado["confirmacoes"] += 1
            else:
                estado["elemento_id"] = (
                    elemento_id
                )
                estado["confirmacoes"] = 1

            if estado["confirmacoes"] >= 2:
                return elemento

            return False

        return wait.until(
            destino_estavel
        )
    @staticmethod
    def preencher_destino(
        wait,
        input_destino,
        destino
    ):

        input_destino.send_keys(
            destino
        )

        wait.until(
            lambda _driver:
            input_destino
            .get_attribute("value")
            .strip()
            == destino.strip()
        )

        OrigemDestino.aguardar_sugestao(
            wait,
            destino
        )

        input_destino.send_keys(
            Keys.ENTER
        )

        OrigemDestino.aguardar_destino_selecionado(
            wait
        )


    @staticmethod
    def aguardar_destino_selecionado(
        wait
    ):

        def destino_confirmado(driver):

            try:

                campo_destino = driver.find_element(
                    *sel.CAMPO_DESTINO
                )

                valor_destino = (
                    campo_destino
                    .get_attribute("value")
                    .strip()
                )

                itens_ativos = driver.find_elements(
                    *sel.AUTOCOMPLETE_ITEM_ATIVO
                )

                autocomplete_visivel = any(
                    item.is_displayed()
                    for item in itens_ativos
                )

                if (
                    valor_destino
                    and not autocomplete_visivel
                ):
                    return campo_destino

            except StaleElementReferenceException:
                return False

            return False

        return wait.until(
            destino_confirmado
        )

        
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