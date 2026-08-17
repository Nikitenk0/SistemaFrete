from selenium.webdriver.support import expected_conditions as EC
from .config import EMAIL, SENHA
import infrastructure.qualp.selectors as sel


class QualPAuthenticator:

    @staticmethod
    def authenticate(driver, wait):
            
            driver.get(sel.URL)

            # Aguarda o pop-up aparecer e clica no botão de fechar
            try:
                botao_fechar = wait.until(
                    EC.element_to_be_clickable(
                        sel.POPUP_CLOSE_BUTTON
                    )
                )

                botao_fechar.click()

                wait.until(
                    EC.invisibility_of_element_located(
                        sel.POPUP_CLOSE_BUTTON
                    )
                )

            except Exception as e:
                print("Pop-up não encontrado ou já estava fechado:", e)

            # Primeiro botão "Logar"
            botao_login = wait.until(
                EC.element_to_be_clickable(
                    sel.LOGIN_BUTTON
                )
            )
            botao_login.click()

            # Campo de e-mail
            email = wait.until(
                EC.visibility_of_element_located(
                    sel.EMAIL_FIELD
                )
            )
            email.send_keys(EMAIL)

            # Campo de senha
            senha = wait.until(
                EC.visibility_of_element_located(
                    sel.PASSWORD_FIELD
                )
            )
            senha.send_keys(SENHA)

            # Botão de envio do formulário
            entrar = wait.until(
                EC.element_to_be_clickable(
                    sel.LOGIN_SUBMIT_BUTTON
                )
            )

            entrar.click()

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
