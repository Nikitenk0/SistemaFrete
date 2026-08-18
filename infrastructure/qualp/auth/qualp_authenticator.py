from selenium.webdriver.support import expected_conditions as EC

import infrastructure.qualp.selectors as sel


class QualPAuthenticator:

    @staticmethod
    def authenticate(
        driver,
        wait,
        email: str | None,
        password: str | None
    ):

        if not email or not password:
            raise RuntimeError(
                "Credenciais do QualP não configuradas"
            )

        driver.get(sel.URL)

        # O pop-up pode ou não existir.
        try:
            close_button = wait.until(
                EC.element_to_be_clickable(
                    sel.POPUP_CLOSE_BUTTON
                )
            )

            close_button.click()

            wait.until(
                EC.invisibility_of_element_located(
                    sel.POPUP_CLOSE_BUTTON
                )
            )

        except Exception as error:
            print(
                "Pop-up não encontrado ou já estava fechado:",
                error
            )

        login_button = wait.until(
            EC.element_to_be_clickable(
                sel.LOGIN_BUTTON
            )
        )
        login_button.click()

        email_field = wait.until(
            EC.visibility_of_element_located(
                sel.EMAIL_FIELD
            )
        )
        email_field.send_keys(email)

        password_field = wait.until(
            EC.visibility_of_element_located(
                sel.PASSWORD_FIELD
            )
        )
        password_field.send_keys(password)

        submit_button = wait.until(
            EC.element_to_be_clickable(
                sel.LOGIN_SUBMIT_BUTTON
            )
        )
        submit_button.click()

        wait.until(
            EC.invisibility_of_element_located(
                sel.PASSWORD_FIELD
            )
        )

        wait.until(
            EC.visibility_of_element_located(
                sel.ORIGIN_FIELD
            )
        )