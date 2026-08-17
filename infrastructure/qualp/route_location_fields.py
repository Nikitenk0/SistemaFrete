import unicodedata

from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException
)
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

import infrastructure.qualp.selectors as sel


class RouteLocationFields:

    @staticmethod
    def normalize_text(text):

        normalized_text = unicodedata.normalize(
            "NFD",
            text
        )

        text_without_accents = "".join(
            character
            for character in normalized_text
            if unicodedata.category(character) != "Mn"
        )

        return text_without_accents.casefold().strip()

    @staticmethod
    def wait_for_suggestion(
        wait,
        searched_text
    ):

        normalized_text = (
            RouteLocationFields.normalize_text(
                searched_text
            )
        )

        def matching_suggestion(driver):

            try:

                active_item = driver.find_element(
                    *sel.ACTIVE_AUTOCOMPLETE_ITEM
                )

                item_text = (
                    RouteLocationFields.normalize_text(
                        active_item.text
                    )
                )

                if (
                    normalized_text
                    and normalized_text in item_text
                ):
                    return active_item

            except (
                NoSuchElementException,
                StaleElementReferenceException
            ):
                return False

            return False

        return wait.until(
            matching_suggestion
        )

    @staticmethod
    def fill_origin(
        driver,
        wait,
        origem
    ):

        origin_box = wait.until(
            EC.element_to_be_clickable(
                sel.ORIGIN_FIELD
            )
        )

        origin_box.click()

        origin_input = wait.until(
            EC.element_to_be_clickable(
                sel.ORIGIN_FIELD
            )
        )

        origin_input.send_keys(
            origem
        )

        wait.until(
            lambda _driver:
            origin_input
            .get_attribute("value")
            .strip()
            == origem.strip()
        )

        RouteLocationFields.wait_for_suggestion(
            wait,
            origem
        )

        origin_input.send_keys(
            Keys.ENTER
        )

        destination_input = (
            RouteLocationFields.wait_for_stable_destination(
                wait,
                origin_input
            )
        )

        return destination_input

    @staticmethod
    def wait_for_stable_destination(
        wait,
        origin_input
    ):

        state = {
            "element_id": None,
            "confirmations": 0
        }

        def stable_destination(driver):

            element = (
                driver.switch_to.active_element
            )

            if element == origin_input:
                state["element_id"] = None
                state["confirmations"] = 0
                return False

            if element.tag_name.lower() != "input":
                state["element_id"] = None
                state["confirmations"] = 0
                return False

            if not element.is_displayed():
                state["element_id"] = None
                state["confirmations"] = 0
                return False

            if not element.is_enabled():
                state["element_id"] = None
                state["confirmations"] = 0
                return False

            element_id = element.id

            if (
                state["element_id"]
                == element_id
            ):
                state["confirmations"] += 1
            else:
                state["element_id"] = (
                    element_id
                )
                state["confirmations"] = 1

            if state["confirmations"] >= 2:
                return element

            return False

        return wait.until(
            stable_destination
        )
    @staticmethod
    def fill_destination(
        wait,
        destination_input,
        destino
    ):

        destination_input.send_keys(
            destino
        )

        wait.until(
            lambda _driver:
            destination_input
            .get_attribute("value")
            .strip()
            == destino.strip()
        )

        RouteLocationFields.wait_for_suggestion(
            wait,
            destino
        )

        destination_input.send_keys(
            Keys.ENTER
        )

        RouteLocationFields.wait_for_selected_destination(
            wait
        )

    @staticmethod
    def wait_for_selected_destination(
        wait
    ):

        def confirmed_destination(driver):

            try:

                destination_field = driver.find_element(
                    *sel.DESTINATION_FIELD
                )

                destination_value = (
                    destination_field
                    .get_attribute("value")
                    .strip()
                )

                active_items = driver.find_elements(
                    *sel.ACTIVE_AUTOCOMPLETE_ITEM
                )

                autocomplete_visible = any(
                    item.is_displayed()
                    for item in active_items
                )

                if (
                    destination_value
                    and not autocomplete_visible
                ):
                    return destination_field

            except StaleElementReferenceException:
                return False

            return False

        return wait.until(
            confirmed_destination
        )

    @staticmethod
    def get_origin(driver):

        origin_input = driver.find_element(
            *sel.ORIGIN_FIELD
        )

        return origin_input.get_attribute(
            "value"
        )

    @staticmethod
    def get_destination(driver):

        destination_input = driver.find_element(
            *sel.DESTINATION_FIELD
        )

        return destination_input.get_attribute(
            "value"
        )