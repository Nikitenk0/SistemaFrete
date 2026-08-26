from domain.models.freight import FreightStatus


def active_operational_context(unit):
    for assignment in unit.driver_assignments:
        if assignment.is_active:
            return assignment.operational_context
    return None


def can_adopt_current_operational_context(
    *,
    status: FreightStatus,
    has_vehicle: bool,
    has_active_driver: bool,
) -> bool:
    return (
        FreightStatus(status) == FreightStatus.IN_PROGRESS
        and has_vehicle
        and has_active_driver
    )


def can_replace_current_operational_context(
    *,
    status: FreightStatus,
    active_context,
) -> bool:
    return (
        FreightStatus(status) == FreightStatus.IN_PROGRESS
        and active_context is not None
    )


def can_finish_current_operational_context(
    *,
    status: FreightStatus,
    active_context,
    has_active_driver: bool,
) -> bool:
    return (
        FreightStatus(status) == FreightStatus.IN_PROGRESS
        and active_context is not None
        and has_active_driver
    )
