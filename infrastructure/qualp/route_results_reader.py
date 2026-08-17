from selenium.webdriver.support import expected_conditions as EC
from infrastructure.qualp.route_location_fields import (
    RouteLocationFields
)
from domain.models.route_result import RouteResult
import infrastructure.qualp.selectors as sel

class RouteResultsReader:

    @staticmethod
    def read(driver, wait) -> RouteResult:

        selected_origin = RouteLocationFields.get_origin(
            driver
        )

        selected_destination = RouteLocationFields.get_destination(
            driver
        )

        wait.until(
            EC.visibility_of_element_located(
                sel.ROUTE_TABLE
            )
        )

        distance = driver.find_element(
            *sel.DISTANCE_VALUE
        ).text

        toll = driver.find_element(
            *sel.TOLL_VALUE
        ).text

        wait.until(
            EC.visibility_of_element_located(
                sel.GERAL_TITULO
            )
        )

        geral = driver.find_element(
            *sel.GERAL
        ).text

        return RouteResult(
            origem=selected_origin,
            destino=selected_destination,
            distancia=distance,
            pedagio=toll,
            geral=geral
        )
