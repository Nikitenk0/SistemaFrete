from application.ports.freight_unit_of_work import (
    FreightUnitOfWorkFactory
)
from application.use_cases.change_freight_status import (
    ChangeFreightStatus
)
from domain.models.freight import (
    Freight,
    FreightStatus
)


class CancelFreight:

    def __init__(
        self,
        freight_unit_of_work_factory:
            FreightUnitOfWorkFactory
    ):
        self._change_status = ChangeFreightStatus(
            freight_unit_of_work_factory
        )

    def execute(
        self,
        freight_id: int,
        user_id: int | None = None,
        observation: str | None = None
    ) -> Freight:
        return self._change_status.execute(
            freight_id=freight_id,
            target_status=(
                FreightStatus.CANCELLED
            ),
            user_id=user_id,
            observation=observation
        )
