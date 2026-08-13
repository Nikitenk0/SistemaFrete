from selenium.webdriver.support import expected_conditions as EC

import services.qualp.seletores as sel


class Volta:

    @staticmethod
    def configurar(
        driver,
        wait,
        calcular_volta: bool
    ) -> None:

        if not calcular_volta:
            return

        botao_volta = wait.until(
            EC.element_to_be_clickable(
                sel.BOTAO_CALCULAR_VOLTA
            )
        )

        driver.execute_script(
            "arguments[0].click();",
            botao_volta
        )