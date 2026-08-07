from selenium.webdriver.support import expected_conditions as EC
import services.qualp.seletores as sel


class Resultados:

    @staticmethod
    def obter(driver, wait):

        wait.until(
            EC.visibility_of_element_located(
                sel.TABELA_ROTAS
            )
        )

        distancia = driver.find_element(
            *sel.DISTANCIA
        ).text

        pedagio = driver.find_element(
            *sel.PEDAGIO
        ).text

        wait.until(
            EC.visibility_of_element_located(
                sel.GERAL_TITULO
            )
        )

        geral = driver.find_element(
            *sel.GERAL
        ).text

        return {
            "distancia": distancia,
            "pedagio": pedagio,
            "geral": geral,
            "total": ""
        }