from selenium.webdriver.support import expected_conditions as EC
from services.qualp.origem_destino import OrigemDestino
from domain.models.resultado_rota import ResultadoRota
import services.qualp.seletores as sel

class Resultados:

    @staticmethod
    def obter(driver, wait) -> ResultadoRota:

        origem_selecionada = OrigemDestino.obter_origem(
            driver
            )

        destino_selecionado = OrigemDestino.obter_destino(
            driver
            )

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

        return ResultadoRota(
            origem=origem_selecionada,
            destino=destino_selecionado,
            distancia=distancia,
            pedagio=pedagio,
            geral=geral
        )