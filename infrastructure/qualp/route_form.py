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

        destination_input = RouteLocationFields.fill_origin(
            driver,
            wait,
            origem
        )

        RouteLocationFields.fill_destination(
            wait,
            destination_input,
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

        calculate_button = wait.until(
            EC.element_to_be_clickable(
                sel.CALCULATE_BUTTON
            )
        )

        driver.execute_script(
            "arguments[0].click();",
            calculate_button
        )