from domain.models.freight import FreightStatus


def is_freight_completion_phase(
    status: FreightStatus,
) -> bool:
    return (
        FreightStatus(status)
        == FreightStatus.IN_PROGRESS
    )


def _completion_issue(details) -> str | None:
    if not is_freight_completion_phase(
        details.current_status
    ):
        return "Frete não está em andamento."

    if not details.transport_units:
        return (
            "Frete precisa possuir pelo menos uma unidade "
            "de transporte para concluir."
        )

    ordered_units = sorted(
        details.transport_units,
        key=lambda item: item.position,
    )

    for unit in ordered_units:
        if unit.vehicle is None:
            return (
                f"Unidade {unit.position}: informe o veículo "
                "operacional antes de concluir."
            )

        if not unit.driver_assignments:
            return (
                f"Unidade {unit.position}: precisa possuir "
                "participação operacional antes de concluir."
            )

        if any(
            assignment.is_active
            for assignment in unit.driver_assignments
        ):
            return (
                f"Unidade {unit.position}: encerre o conjunto "
                "operacional atual antes de concluir o frete."
            )

        if any(
            assignment.ended_at is None
            or assignment.actual_driver_amount is None
            for assignment in unit.driver_assignments
        ):
            return (
                f"Unidade {unit.position}: existe participação "
                "operacional sem encerramento completo."
            )

    return None


def can_complete_freight(details) -> bool:
    return _completion_issue(details) is None


def completion_readiness_message(details) -> str:
    issue = _completion_issue(details)
    if issue is not None:
        return issue

    return (
        "Operação encerrada em todas as unidades. "
        "Frete pronto para conclusão."
    )
