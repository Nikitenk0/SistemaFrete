from selenium.webdriver.support import expected_conditions as EC
from .config import EMAIL, SENHA
import infrastructure.qualp.seletores as sel


class Login:

    @staticmethod
    def executar(driver, wait):
            
            driver.get(sel.URL)

            # Aguarda o pop-up aparecer e clica no botão de fechar
            try:
                botao_fechar = wait.until(
                    EC.element_to_be_clickable(
                        sel.POPUP_FECHAR
                    )
                )

                botao_fechar.click()

                wait.until(
                    EC.invisibility_of_element_located(
                        sel.POPUP_FECHAR
                    )
                )

            except Exception as e:
                print("Pop-up não encontrado ou já estava fechado:", e)

            # Primeiro botão "Logar"
            botao_login = wait.until(
                EC.element_to_be_clickable(
                    sel.BOTAO_LOGIN
                )
            )
            botao_login.click()

            # Campo de e-mail
            email = wait.until(
                EC.visibility_of_element_located(
                    sel.CAMPO_EMAIL
                )
            )
            email.send_keys(EMAIL)

            # Campo de senha
            senha = wait.until(
                EC.visibility_of_element_located(
                    sel.CAMPO_SENHA
                )
            )
            senha.send_keys(SENHA)

            # Botão de envio do formulário
            entrar = wait.until(
                EC.element_to_be_clickable(
                    sel.BOTAO_ENTRAR
                )
            )

            entrar.click()

            # Espera o formulário de login desaparecer
            wait.until(
                EC.invisibility_of_element_located(
                    sel.CAMPO_SENHA
                )
            )

            # Espera o campo Origem aparecer
            wait.until(
                EC.visibility_of_element_located(
                    sel.CAMPO_ORIGEM
                )
            )
