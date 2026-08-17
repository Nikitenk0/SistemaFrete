from selenium.webdriver.common.by import By

URL = "https://qualp.com.br/#/"

POPUP_CLOSE_BUTTON = (
    By.CSS_SELECTOR,
    "#q-app > div > div > main > div.antt-modal-overlay > div > button"
)
# ACESSA A TELA DE LOGIN
LOGIN_BUTTON = (
    By.XPATH,
    "//button[contains(.,'Logar')]"
)

EMAIL_FIELD = (
    By.CSS_SELECTOR,
    "input[type='email']"
)

PASSWORD_FIELD = (
    By.CSS_SELECTOR,
    "input[type='password']"
)
# CLICA NO BOTÃO DE LOGAR
LOGIN_SUBMIT_BUTTON = (
    By.XPATH,
    "//button[.//span[text()='Logar']]"
)

ACTIVE_AUTOCOMPLETE_ITEM = (
    By.CSS_SELECTOR,
    ".search-location-container "
    "[role='listitem'].q-item--active"
)

ORIGIN_FIELD = (
    By.XPATH,
    "//input[@placeholder='Origem']"
)

DESTINATION_FIELD = (
    By.XPATH,
    "//input[@placeholder='Destino']"
)

AXLE_CONTROL = (
    By.CLASS_NAME,
    "vehicle-control-axis"
)

AXLE_FIELD = (
    By.CSS_SELECTOR,
    ".vehicle-control-axis input"
)

CALCULATE_BUTTON = (
    By.XPATH,
    "//button[@type='submit']//span[contains(text(),'Calcular')]"
)

ROUND_TRIP_SWITCH = (
    By.XPATH,
    "//div[@role='switch' and @aria-label='Calcular Volta']"
)

ROUTE_TABLE = (
    By.CSS_SELECTOR,
    "div.route-table"
)

DISTANCE_VALUE = (
    By.XPATH,
    "//span[normalize-space()='Distância']/following-sibling::span"
)

TOLL_VALUE = (
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


