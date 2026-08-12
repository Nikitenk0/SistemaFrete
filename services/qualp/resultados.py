from selenium.webdriver.support import expected_conditions as EC
import services.qualp.seletores as sel
from services.qualp.origem_destino import OrigemDestino

class Resultados:

    @staticmethod
    def obter(driver, wait):

        origem_selecionada = OrigemDestino.obter_origem(
            driver
            )

        destino_selecionado = OrigemDestino.obter_destino(
            driver
            )

        print( "Origem selecionada pelo QualP:", origem_selecionada )
        print( "Destino selecionado pelo QualP:", destino_selecionado )
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
            "origem": origem_selecionada,
            "destino": destino_selecionado,
            "distancia": distancia,
            "pedagio": pedagio,
            "geral": geral,
            "total": ""
        }