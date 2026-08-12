from selenium.webdriver.support import expected_conditions as EC
import services.qualp.seletores as sel


class calcVolta:

    @staticmethod
    def calcular_volta(
        driver,
        wait,
        calcular_volta
    ):
        if calcular_volta:

            botao_volta = wait.until(
                EC.element_to_be_clickable(
                    sel.BOTAO_CALCULAR_VOLTA
                )
            )

            driver.execute_script(
                "arguments[0].click();",
                botao_volta
            )        

