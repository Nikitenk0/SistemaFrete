from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import infrastructure.qualp.selectors as sel


class AxleSelector:

    @staticmethod
    def select(
        wait,
        axle_count
    ):
        axle_control = wait.until(
            EC.presence_of_element_located(
                sel.AXLE_CONTROL
            )
        )

        axle_field = axle_control.find_element(
            *sel.AXLE_FIELD
        )

        buttons = axle_control.find_elements(
            By.CLASS_NAME,
            "q-icon"
        )

        decrease_button = buttons[0]
        increase_button = buttons[1]

        def get_axle_count():
            return int(
                axle_field
                .get_attribute("value")
                .split()[0]
            )

        current_axle_count = get_axle_count()

        while current_axle_count < axle_count:

            previous_axle_count = get_axle_count()

            increase_button.click()

            wait.until(
                lambda _driver:
                get_axle_count() > previous_axle_count
            )

            current_axle_count = get_axle_count()

        while current_axle_count > axle_count:

            previous_axle_count = get_axle_count()

            decrease_button.click()

            wait.until(
                lambda _driver:
                get_axle_count() < previous_axle_count
            )

            current_axle_count = get_axle_count()