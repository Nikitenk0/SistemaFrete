from selenium.webdriver.common.by import By

URL = "https://qualp.com.br/#/"

POPUP_FECHAR = (
    By.CSS_SELECTOR,
    "#q-app > div > div > main > div.antt-modal-overlay > div > button"
)
# ACESSA A TELA DE LOGIN
BOTAO_LOGIN = (
    By.XPATH,
    "//button[contains(.,'Logar')]"
)

CAMPO_EMAIL = (
    By.CSS_SELECTOR,
    "input[type='email']"
)

CAMPO_SENHA = (
    By.CSS_SELECTOR,
    "input[type='password']"
)
# CLICA NO BOTÃO DE LOGAR
BOTAO_ENTRAR = (
    By.XPATH,
    "//button[.//span[text()='Logar']]"
)

CAMPO_ORIGEM = (
    By.XPATH,
    "//input[@placeholder='Origem']"
)

CAMPO_DESTINO = (
    By.XPATH,
    "//input[@placeholder='Destino']"
)

CONTROLE_EIXOS = (
    By.CLASS_NAME,
    "vehicle-control-axis"
)

CAMPO_EIXOS = (
    By.CSS_SELECTOR,
    ".vehicle-control-axis input"
)

BOTAO_CALCULAR = (
    By.XPATH,
    "//button[@type='submit']//span[contains(text(),'Calcular')]"
)

BOTAO_CALCULAR_VOLTA = (
    By.XPATH,
    "//div[@role='switch' and @aria-label='Calcular Volta']"
)

TABELA_ROTAS = (
    By.CSS_SELECTOR,
    "div.route-table"
)

DISTANCIA = (
    By.XPATH,
    "//span[normalize-space()='Distância']/following-sibling::span"
)

PEDAGIO = (
    By.XPATH,
    "//span[normalize-space()='Pedágio']/following-sibling::span"
)

GERAL_TITULO = (
    By.XPATH,
    "//td[normalize-space()='Geral']"
)
GERAL = (
    By.XPATH,
    "//td[normalize-space()='Geral']/following-sibling::td"
)


