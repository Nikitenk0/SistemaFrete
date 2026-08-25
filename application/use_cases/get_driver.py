from application.exceptions import (
    DriverNotFoundError,
    InvalidDriverDataError
)
from application.ports.driver_unit_of_work import (
    DriverUnitOfWorkFactory
)
from domain.models.driver import (
    Driver
)


class GetDriver:

    def __init__(
        self,
        unit_of_work_factory: DriverUnitOfWorkFactory
    ):
        self._unit_of_work_factory = (
            unit_of_work_factory
        )

    def execute(
        self,
        driver_id: int
    ) -> Driver:

        if driver_id < 1:
            raise InvalidDriverDataError(
                "driver_id inválido"
            )

        with (
            self._unit_of_work_factory.create()
            as unit_of_work
        ):
            driver = unit_of_work.drivers.get_by_id(
                driver_id
            )

        if driver is None:
            raise DriverNotFoundError(
                "Motorista não encontrado"
            )

        return driver
