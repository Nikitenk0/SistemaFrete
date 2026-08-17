from selenium.webdriver.support import expected_conditions as EC

import infrastructure.qualp.selectors as sel


class RoundTripSelector:

    @staticmethod
    def configure(
        driver,
        wait,
        enabled: bool
    ) -> None:

        if not enabled:
            return

        round_trip_switch = wait.until(
            EC.element_to_be_clickable(
                sel.ROUND_TRIP_SWITCH
            )
        )

        driver.execute_script(
            "arguments[0].click();",
            round_trip_switch
        )