from application.dtos.route_result import RouteResult
from infrastructure.qualp.auth.qualp_authenticator import (
    QualPAuthenticator
)
from infrastructure.qualp.route_form import RouteForm
from infrastructure.qualp.route_results_reader import (
    RouteResultsReader
)
from infrastructure.qualp.qualp_session import QualPSession


class QualPRouteSearcher:

    def __init__(
        self,
        session: QualPSession | None = None,
        email: str | None = None,
        password: str | None = None,
        headless: bool = False
    ):
        self._session = (
            session
            if session is not None
            else QualPSession(
                headless=headless
            )
        )
        self._email = email
        self._password = password

    def search(
        self,
        origem: str,
        destino: str,
        quantidade_eixos: int = 6,
        calcular_volta: bool = False
    ) -> RouteResult:

        driver, wait = self._session.open()

        try:

            QualPAuthenticator.authenticate(
                driver,
                wait,
                self._email,
                self._password
            )

            RouteForm.fill_and_calculate(
                driver,
                wait,
                origem,
                destino,
                quantidade_eixos,
                calcular_volta
            )

            route_result = RouteResultsReader.read(
                driver,
                wait
            )

            return route_result

        finally:

            self._session.close()
