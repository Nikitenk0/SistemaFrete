from selenium.webdriver.support.ui import WebDriverWait

from infrastructure.qualp.navegador import Navegador


class SessaoQualP:

    def __init__(
        self,
        timeout: int = 15
    ):
        self._timeout = timeout
        self._driver = None
        self._wait = None

    def abrir(self):
        self._driver = Navegador.iniciar()

        self._wait = WebDriverWait(
            self._driver,
            self._timeout
        )

        return (
            self._driver,
            self._wait
        )

    def fechar(self):
        if self._driver is None:
            return

        try:
            self._driver.quit()
        finally:
            self._driver = None
            self._wait = None
