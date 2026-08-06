import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class QualP:

    def pesquisar(
            self,
            origem,
            destino,
            quantidade_eixos=6,
            calcular_volta=False
        ):

        chrome_options = Options()
#       chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")

        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 15)

        try:

            driver.get("https://qualp.com.br/#/")

            # Aguarda o pop-up aparecer e clica no botão de fechar
            try:
                botao_fechar = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (
                            By.CSS_SELECTOR,
                            "#q-app > div > div > main > div.antt-modal-overlay > div > button"
                        )
                    )
                )

                botao_fechar.click()

                WebDriverWait(driver, 10).until(
                    EC.invisibility_of_element_located(
                        (By.CSS_SELECTOR, "div.antt-modal-overlay")
                    )
                )

            except Exception as e:
                print("Pop-up não encontrado ou já estava fechado:", e)

            # Primeiro botão "Logar"
            botao_login = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(.,'Logar')]")
                )
            )
            botao_login.click()

            # Campo de e-mail
            email = wait.until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "input[type='email']")
                )
            )
            email.send_keys("v2transportes.br@gmail.com")

            # Campo de senha
            senha = wait.until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "input[type='password']")
                )
            )
            senha.send_keys("br88173314")

            # Botão de envio do formulário
            entrar = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[.//span[text()='Logar']]")
                )
            )

            entrar.click()

            # Espera o formulário de login desaparecer
            wait.until(
                EC.invisibility_of_element_located(
                    (By.CSS_SELECTOR, "input[type='password']")
                )
            )

            # Espera o campo Origem aparecer
            wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//input[@placeholder='Origem']")
                )
            )

            # =========================
            # ORIGEM
            # =========================

            caixa_origem = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//input[@placeholder='Origem']")
                )
            )

            caixa_origem.click()

            input_origem = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//input[@placeholder='Origem']")
                )
            )

            input_origem.send_keys(origem)

            time.sleep(2)

            input_origem.send_keys(Keys.ENTER)
            time.sleep(2)
            
            # =========================
            # DESTINO
            # =========================

            input_destino = driver.switch_to.active_element
            input_destino.send_keys(destino)

            time.sleep(2)

#           input_destino.send_keys(Keys.ARROW_DOWN)
            input_destino.send_keys(Keys.ENTER)
            # =========================
            # QUANTIDADE DE EIXOS
            # =========================

            # Aqui alteraremos a quantidade de eixos

            # Localiza o controle de eixos
            controle_eixos = wait.until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "vehicle-control-axis")
                )
            )

            # Localiza os dois botões (0 = diminuir, 1 = aumentar)
            botoes = controle_eixos.find_elements(By.CLASS_NAME, "q-icon")

            botao_diminuir = botoes[0]
            botao_aumentar = botoes[1]

            # Como o site inicia em 6 eixos
            eixos_atuais = 6

            while eixos_atuais < quantidade_eixos:
                botao_aumentar.click()
                eixos_atuais += 1
                time.sleep(0.3)

            while eixos_atuais > quantidade_eixos:
                botao_diminuir.click()
                eixos_atuais -= 1
                time.sleep(0.3)

            # ==========================================
            # Calcular Volta
            # ==========================================

            if calcular_volta:

                botao_volta = wait.until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "//div[@role='switch' and @aria-label='Calcular Volta']"
                        )
                    )
                )

                driver.execute_script(
                    "arguments[0].click();",
                    botao_volta
                )
            # ==========================================
            # Botão Calcular
            # ==========================================

            botao_calcular = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//button[@type='submit']//span[contains(text(),'Calcular')]"
                    )
                )
            )

            driver.execute_script(
                "arguments[0].click();",
                botao_calcular
            )

            # Aguarda a tabela aparecer
            wait.until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "div.route-table")
                )
            )

            distancia = driver.find_element(
                By.XPATH,
                "//span[normalize-space()='Distância']/following-sibling::span"
            ).text

            pedagio = driver.find_element(
                By.XPATH,
                "//span[normalize-space()='Pedágio']/following-sibling::span"
            ).text

            print(distancia)
            print(pedagio)


            return {
                "distancia": distancia,
                "pedagio": pedagio,
                "total": ""
            }

        finally:
            time.sleep(300)
            #input("Pressione ENTER para fechar o navegador...")
            #driver.quit()