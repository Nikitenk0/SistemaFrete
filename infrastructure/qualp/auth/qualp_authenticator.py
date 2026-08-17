from selenium.webdriver.support import expected_conditions as EC
from .config import EMAIL, SENHA
import infrastructure.qualp.selectors as sel


class QualPAuthenticator:

    @staticmethod
    def authenticate(driver, wait):
            
            driver.get(sel.URL)

            # Aguarda o pop-up aparecer e clica no botão de fechar
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
                print("Pop-up não encontrado ou já estava fechado:", e)

            # Primeiro botão "Logar"
            login_button = wait.until(
                EC.element_to_be_clickable(
                    sel.LOGIN_BUTTON
                )
            )
            login_button.click()

            # Campo de e-mail
            email = wait.until(
                EC.visibility_of_element_located(
                    sel.EMAIL_FIELD
                )
            )
            email.send_keys(EMAIL)

            # Campo de senha
            password_field = wait.until(
                EC.visibility_of_element_located(
                    sel.PASSWORD_FIELD
                )
            )
            password_field.send_keys(SENHA)

            # Botão de envio do formulário
            submit_button = wait.until(
                EC.element_to_be_clickable(
                    sel.LOGIN_SUBMIT_BUTTON
                )
            )

            submit_button.click()

            # Espera o formulário de login desaparecer
            wait.until(
                EC.invisibility_of_element_located(
                    sel.PASSWORD_FIELD
                )
            )

            # Espera o campo Origem aparecer
            wait.until(
                EC.visibility_of_element_located(
                    sel.ORIGIN_FIELD
                )
            )
