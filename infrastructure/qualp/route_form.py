from selenium.webdriver.support import expected_conditions as EC

from infrastructure.qualp.route_location_fields import (
    RouteLocationFields
)
from infrastructure.qualp.axle_selector import AxleSelector
from infrastructure.qualp.round_trip_selector import (
    RoundTripSelector
)
import infrastructure.qualp.selectors as sel


class RouteForm:

    @staticmethod
    def fill_and_calculate(
        driver,
        wait,
        origem,
        destino,
        quantidade_eixos,
        calcular_volta
    ):

        input_destino = RouteLocationFields.fill_origin(
            driver,
            wait,
            origem
        )

        RouteLocationFields.fill_destination(
            wait,
            input_destino,
            destino
        )

        AxleSelector.select(
            wait,
            quantidade_eixos
        )

        RoundTripSelector.configure(
            driver,
            wait,
            calcular_volta
        )

        RouteForm.click_calculate(
            driver,
            wait
        )

    @staticmethod
    def click_calculate(
        driver,
        wait
    ):

        botao_calcular = wait.until(
            EC.element_to_be_clickable(
                sel.CALCULATE_BUTTON
            )
        )

        driver.execute_script(
            "arguments[0].click();",
            botao_calcular
        )