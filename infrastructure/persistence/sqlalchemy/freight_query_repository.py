from collections import defaultdict
from decimal import Decimal

from sqlalchemy import and_, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, aliased

from application.dtos.freight_query import (
    FreightDetails,
    FreightDriverAssignmentDetails,
    FreightEventDetails,
    FreightExpenseDetails,
    FreightFinancialDetails,
    FreightListItem,
    FreightOperationalAssignmentDetails,
    FreightQueryFilters,
    FreightTransportUnitDetails,
    FreightVehicleDetails,
)
from application.exceptions import FreightPersistenceError
from application.ports.freight_query_repository import (
    FreightQueryRepository,
)
from domain.models.freight import FreightStatus
from domain.models.freight_event import FreightEventType
from domain.models.freight_expense import FreightExpenseType
from domain.models.freight_vehicle_record import FreightVehicleType
from domain.models.vehicle import VehicleType
from domain.models.quote import QuoteStatus, QuoteType
from infrastructure.persistence.sqlalchemy.models import (
    DriverModel,
    FreightDriverAssignmentModel,
    FreightEventModel,
    FreightExpenseModel,
    FreightFinancialResultModel,
    FreightModel,
    FreightOperationalAssignmentModel,
    FreightTransportUnitModel,
    FreightVehicleRecordModel,
    QuoteModel,
    QuoteVersionModel,
)


class SqlAlchemyFreightQueryRepository(
    FreightQueryRepository
):

    def __init__(
        self,
        session: Session,
    ):
        self._session = session

    def list(
        self,
        filters: FreightQueryFilters,
    ) -> tuple[FreightListItem, ...]:

        statement = self._base_statement()

        if filters.customer_id is not None:
            statement = statement.where(
                FreightModel.customer_id
                == filters.customer_id
            )

        if filters.status is not None:
            statement = statement.where(
                FreightModel.current_status
                == filters.status.value
            )

        if filters.completed_from is not None:
            statement = statement.where(
                FreightModel.completed_at
                >= filters.completed_from
            )

        if filters.completed_to is not None:
            statement = statement.where(
                FreightModel.completed_at
                <= filters.completed_to
            )

        statement = statement.order_by(
            FreightModel.created_at.desc(),
            FreightModel.freight_id.desc(),
        )

        try:
            rows = (
                self._session.execute(statement)
                .mappings()
                .all()
            )
        except SQLAlchemyError as error:
            raise FreightPersistenceError(
                "Não foi possível consultar a lista de fretes"
            ) from error

        return tuple(
            self._to_list_item(row)
            for row in rows
        )

    def get_by_id(
        self,
        freight_id: int,
    ) -> FreightDetails | None:

        try:
            row = (
                self._session.execute(
                    self._base_statement().where(
                        FreightModel.freight_id == freight_id
                    )
                )
                .mappings()
                .one_or_none()
            )

            if row is None:
                return None

            transport_units = self._load_transport_units(
                freight_id
            )
            expenses = self._load_expenses(
                freight_id
            )
            events = self._load_events(
                freight_id
            )
            financial_result = self._load_financial_result(
                freight_id
            )

        except SQLAlchemyError as error:
            raise FreightPersistenceError(
                "Não foi possível consultar os detalhes do frete"
            ) from error

        return self._to_details(
            row,
            transport_units=transport_units,
            expenses=expenses,
            events=events,
            financial_result=financial_result,
        )

    def _load_transport_units(
        self,
        freight_id: int,
    ) -> tuple[FreightTransportUnitDetails, ...]:

        unit_rows = (
            self._session.execute(
                select(
                    FreightTransportUnitModel
                    .freight_transport_unit_id.label(
                        "freight_transport_unit_id"
                    ),
                    FreightTransportUnitModel.position.label(
                        "position"
                    ),
                    FreightVehicleRecordModel
                    .freight_vehicle_record_id.label(
                        "freight_vehicle_record_id"
                    ),
                    FreightVehicleRecordModel.vehicle_type.label(
                        "vehicle_type"
                    ),
                    FreightVehicleRecordModel.plate.label(
                        "plate"
                    ),
                    FreightVehicleRecordModel.axle_count.label(
                        "axle_count"
                    ),
                    FreightVehicleRecordModel
                    .pallet_capacity_min.label(
                        "pallet_capacity_min"
                    ),
                    FreightVehicleRecordModel
                    .pallet_capacity_max.label(
                        "pallet_capacity_max"
                    ),
                    FreightVehicleRecordModel
                    .payload_capacity_kg.label(
                        "payload_capacity_kg"
                    ),
                )
                .select_from(FreightTransportUnitModel)
                .outerjoin(
                    FreightVehicleRecordModel,
                    FreightVehicleRecordModel
                    .freight_transport_unit_id
                    == FreightTransportUnitModel
                    .freight_transport_unit_id,
                )
                .where(
                    FreightTransportUnitModel.freight_id
                    == freight_id
                )
                .order_by(
                    FreightTransportUnitModel.position,
                    FreightTransportUnitModel
                    .freight_transport_unit_id,
                )
            )
            .mappings()
            .all()
        )

        assignment_rows = (
            self._session.execute(
                select(
                    FreightDriverAssignmentModel
                    .freight_driver_assignment_id.label(
                        "freight_driver_assignment_id"
                    ),
                    FreightDriverAssignmentModel
                    .freight_transport_unit_id.label(
                        "freight_transport_unit_id"
                    ),
                    FreightDriverAssignmentModel.driver_id.label(
                        "driver_id"
                    ),
                    DriverModel.name.label(
                        "driver_name"
                    ),
                    FreightDriverAssignmentModel.started_at.label(
                        "started_at"
                    ),
                    FreightDriverAssignmentModel.ended_at.label(
                        "ended_at"
                    ),
                    FreightDriverAssignmentModel
                    .actual_driver_amount.label(
                        "actual_driver_amount"
                    ),
                    FreightOperationalAssignmentModel
                    .freight_operational_assignment_id.label(
                        "freight_operational_assignment_id"
                    ),
                    FreightOperationalAssignmentModel
                    .transport_provider_id.label(
                        "operational_transport_provider_id"
                    ),
                    FreightOperationalAssignmentModel
                    .vehicle_id.label(
                        "operational_vehicle_id"
                    ),
                    FreightOperationalAssignmentModel
                    .provider_name_snapshot.label(
                        "provider_name_snapshot"
                    ),
                    FreightOperationalAssignmentModel
                    .provider_tax_document_snapshot.label(
                        "provider_tax_document_snapshot"
                    ),
                    FreightOperationalAssignmentModel
                    .driver_name_snapshot.label(
                        "driver_name_snapshot"
                    ),
                    FreightOperationalAssignmentModel
                    .driver_cpf_snapshot.label(
                        "driver_cpf_snapshot"
                    ),
                    FreightOperationalAssignmentModel
                    .vehicle_plate_snapshot.label(
                        "vehicle_plate_snapshot"
                    ),
                    FreightOperationalAssignmentModel
                    .vehicle_type_snapshot.label(
                        "vehicle_type_snapshot"
                    ),
                    FreightOperationalAssignmentModel
                    .created_at.label(
                        "operational_context_created_at"
                    ),
                )
                .select_from(FreightDriverAssignmentModel)
                .join(
                    FreightTransportUnitModel,
                    FreightTransportUnitModel
                    .freight_transport_unit_id
                    == FreightDriverAssignmentModel
                    .freight_transport_unit_id,
                )
                .join(
                    DriverModel,
                    DriverModel.driver_id
                    == FreightDriverAssignmentModel.driver_id,
                )
                .outerjoin(
                    FreightOperationalAssignmentModel,
                    FreightOperationalAssignmentModel
                    .freight_driver_assignment_id
                    == FreightDriverAssignmentModel
                    .freight_driver_assignment_id,
                )
                .where(
                    FreightTransportUnitModel.freight_id
                    == freight_id
                )
                .order_by(
                    FreightTransportUnitModel.position,
                    FreightDriverAssignmentModel.started_at,
                    FreightDriverAssignmentModel
                    .freight_driver_assignment_id,
                )
            )
            .mappings()
            .all()
        )

        assignments_by_unit: dict[
            int,
            list[FreightDriverAssignmentDetails]
        ] = defaultdict(list)

        for assignment_row in assignment_rows:
            operational_context = None
            if (
                assignment_row[
                    "freight_operational_assignment_id"
                ]
                is not None
            ):
                operational_context = (
                    FreightOperationalAssignmentDetails(
                        freight_operational_assignment_id=(
                            assignment_row[
                                "freight_operational_assignment_id"
                            ]
                        ),
                        transport_provider_id=(
                            assignment_row[
                                "operational_transport_provider_id"
                            ]
                        ),
                        vehicle_id=assignment_row[
                            "operational_vehicle_id"
                        ],
                        provider_name_snapshot=(
                            self._required_text(
                                assignment_row[
                                    "provider_name_snapshot"
                                ],
                                "nome do prestador operacional",
                            )
                        ),
                        provider_tax_document_snapshot=(
                            self._required_text(
                                assignment_row[
                                    "provider_tax_document_snapshot"
                                ],
                                "documento do prestador operacional",
                            )
                        ),
                        driver_name_snapshot=(
                            self._required_text(
                                assignment_row[
                                    "driver_name_snapshot"
                                ],
                                "nome do motorista operacional",
                            )
                        ),
                        driver_cpf_snapshot=(
                            self._required_text(
                                assignment_row[
                                    "driver_cpf_snapshot"
                                ],
                                "CPF do motorista operacional",
                            )
                        ),
                        vehicle_plate_snapshot=(
                            self._required_text(
                                assignment_row[
                                    "vehicle_plate_snapshot"
                                ],
                                "placa do veículo operacional",
                            )
                        ),
                        vehicle_type_snapshot=VehicleType(
                            assignment_row[
                                "vehicle_type_snapshot"
                            ]
                        ),
                        created_at=assignment_row[
                            "operational_context_created_at"
                        ],
                    )
                )

            assignments_by_unit[
                assignment_row["freight_transport_unit_id"]
            ].append(
                FreightDriverAssignmentDetails(
                    freight_driver_assignment_id=(
                        assignment_row[
                            "freight_driver_assignment_id"
                        ]
                    ),
                    driver_id=assignment_row["driver_id"],
                    driver_name=self._required_text(
                        assignment_row["driver_name"],
                        "nome do motorista",
                    ),
                    started_at=assignment_row["started_at"],
                    ended_at=assignment_row["ended_at"],
                    actual_driver_amount=(
                        self._optional_decimal(
                            assignment_row[
                                "actual_driver_amount"
                            ]
                        )
                    ),
                    operational_context=operational_context,
                )
            )

        units: list[FreightTransportUnitDetails] = []

        for unit_row in unit_rows:
            unit_id = unit_row[
                "freight_transport_unit_id"
            ]
            vehicle_id = unit_row[
                "freight_vehicle_record_id"
            ]

            vehicle = None
            if vehicle_id is not None:
                vehicle = FreightVehicleDetails(
                    freight_vehicle_record_id=vehicle_id,
                    vehicle_type=FreightVehicleType(
                        unit_row["vehicle_type"]
                    ),
                    plate=self._required_text(
                        unit_row["plate"],
                        "placa do veículo",
                    ),
                    axle_count=unit_row["axle_count"],
                    pallet_capacity_min=(
                        unit_row["pallet_capacity_min"]
                    ),
                    pallet_capacity_max=(
                        unit_row["pallet_capacity_max"]
                    ),
                    payload_capacity_kg=(
                        unit_row["payload_capacity_kg"]
                    ),
                )

            units.append(
                FreightTransportUnitDetails(
                    freight_transport_unit_id=unit_id,
                    position=unit_row["position"],
                    vehicle=vehicle,
                    driver_assignments=tuple(
                        assignments_by_unit.get(
                            unit_id,
                            (),
                        )
                    ),
                )
            )

        return tuple(units)

    def _load_expenses(
        self,
        freight_id: int,
    ) -> tuple[FreightExpenseDetails, ...]:

        rows = (
            self._session.execute(
                select(
                    FreightExpenseModel.freight_expense_id.label(
                        "freight_expense_id"
                    ),
                    FreightExpenseModel.expense_type.label(
                        "expense_type"
                    ),
                    FreightExpenseModel.custom_description.label(
                        "custom_description"
                    ),
                    FreightExpenseModel.value.label(
                        "value"
                    ),
                    FreightExpenseModel.occurred_at.label(
                        "occurred_at"
                    ),
                    FreightExpenseModel.observation.label(
                        "observation"
                    ),
                    FreightExpenseModel.is_considered.label(
                        "is_considered"
                    ),
                )
                .where(
                    FreightExpenseModel.freight_id == freight_id
                )
                .order_by(
                    FreightExpenseModel.occurred_at,
                    FreightExpenseModel.freight_expense_id,
                )
            )
            .mappings()
            .all()
        )

        return tuple(
            FreightExpenseDetails(
                freight_expense_id=row["freight_expense_id"],
                expense_type=FreightExpenseType(
                    row["expense_type"]
                ),
                value=self._decimal(row["value"]),
                occurred_at=row["occurred_at"],
                custom_description=self._optional_text(
                    row["custom_description"]
                ),
                observation=self._optional_text(
                    row["observation"]
                ),
                is_considered=bool(row["is_considered"]),
            )
            for row in rows
        )

    def _load_events(
        self,
        freight_id: int,
    ) -> tuple[FreightEventDetails, ...]:

        rows = (
            self._session.execute(
                select(
                    FreightEventModel.freight_event_id.label(
                        "freight_event_id"
                    ),
                    FreightEventModel.event_type.label(
                        "event_type"
                    ),
                    FreightEventModel.previous_status.label(
                        "previous_status"
                    ),
                    FreightEventModel.new_status.label(
                        "new_status"
                    ),
                    FreightEventModel.observation.label(
                        "observation"
                    ),
                    FreightEventModel.occurred_at.label(
                        "occurred_at"
                    ),
                    FreightEventModel.user_id.label(
                        "user_id"
                    ),
                )
                .where(
                    FreightEventModel.freight_id == freight_id
                )
                .order_by(
                    FreightEventModel.occurred_at,
                    FreightEventModel.freight_event_id,
                )
            )
            .mappings()
            .all()
        )

        return tuple(
            FreightEventDetails(
                freight_event_id=row["freight_event_id"],
                event_type=FreightEventType(
                    row["event_type"]
                ),
                previous_status=(
                    FreightStatus(row["previous_status"])
                    if row["previous_status"] is not None
                    else None
                ),
                new_status=FreightStatus(
                    row["new_status"]
                ),
                observation=self._optional_text(
                    row["observation"]
                ),
                occurred_at=row["occurred_at"],
                user_id=row["user_id"],
            )
            for row in rows
        )

    def _load_financial_result(
        self,
        freight_id: int,
    ) -> FreightFinancialDetails | None:

        row = (
            self._session.execute(
                select(
                    FreightFinancialResultModel
                    .freight_financial_result_id.label(
                        "freight_financial_result_id"
                    ),
                    FreightFinancialResultModel
                    .contracted_revenue.label(
                        "contracted_revenue"
                    ),
                    FreightFinancialResultModel
                    .actual_driver_amount.label(
                        "actual_driver_amount"
                    ),
                    FreightFinancialResultModel.toll_amount.label(
                        "toll_amount"
                    ),
                    FreightFinancialResultModel
                    .actual_expenses_total.label(
                        "actual_expenses_total"
                    ),
                    FreightFinancialResultModel
                    .freight_insurance_total.label(
                        "freight_insurance_total"
                    ),
                    FreightFinancialResultModel.tax_total.label(
                        "tax_total"
                    ),
                    FreightFinancialResultModel
                    .administrative_cost_allocated.label(
                        "administrative_cost_allocated"
                    ),
                    FreightFinancialResultModel.total_cost.label(
                        "total_cost"
                    ),
                    FreightFinancialResultModel.realized_result.label(
                        "realized_result"
                    ),
                    FreightFinancialResultModel.realized_margin.label(
                        "realized_margin"
                    ),
                    FreightFinancialResultModel.finalized_at.label(
                        "finalized_at"
                    ),
                )
                .where(
                    FreightFinancialResultModel.freight_id
                    == freight_id
                )
            )
            .mappings()
            .one_or_none()
        )

        if row is None:
            return None

        return FreightFinancialDetails(
            freight_financial_result_id=(
                row["freight_financial_result_id"]
            ),
            contracted_revenue=self._decimal(
                row["contracted_revenue"]
            ),
            actual_driver_amount=self._decimal(
                row["actual_driver_amount"]
            ),
            toll_amount=self._decimal(
                row["toll_amount"]
            ),
            actual_expenses_total=self._decimal(
                row["actual_expenses_total"]
            ),
            freight_insurance_total=self._decimal(
                row["freight_insurance_total"]
            ),
            tax_total=self._decimal(
                row["tax_total"]
            ),
            administrative_cost_allocated=self._decimal(
                row["administrative_cost_allocated"]
            ),
            total_cost=self._decimal(
                row["total_cost"]
            ),
            realized_result=self._decimal(
                row["realized_result"]
            ),
            realized_margin=self._optional_decimal(
                row["realized_margin"]
            ),
            finalized_at=row["finalized_at"],
        )

    @staticmethod
    def _base_statement():
        primary_quote = aliased(
            QuoteModel,
            name="primary_quote",
        )
        primary_version = aliased(
            QuoteVersionModel,
            name="primary_version",
        )
        approved_quote = aliased(
            QuoteModel,
            name="approved_quote",
        )
        approved_version = aliased(
            QuoteVersionModel,
            name="approved_version",
        )

        contracted_revenue = (
            select(
                func.coalesce(
                    func.sum(
                        approved_version.contracted_price
                    ),
                    Decimal("0"),
                )
            )
            .select_from(approved_quote)
            .join(
                approved_version,
                and_(
                    approved_version.quote_id
                    == approved_quote.quote_id,
                    approved_version.quote_version_id
                    == approved_quote.approved_version_id,
                ),
            )
            .where(
                approved_quote.freight_id
                == FreightModel.freight_id,
                approved_quote.current_status
                == QuoteStatus.APPROVED.value,
            )
            .correlate(FreightModel)
            .scalar_subquery()
        )

        approved_complementary_quote_count = (
            select(
                func.count(
                    approved_quote.quote_id
                )
            )
            .select_from(approved_quote)
            .where(
                approved_quote.freight_id
                == FreightModel.freight_id,
                approved_quote.current_status
                == QuoteStatus.APPROVED.value,
                approved_quote.quote_type
                == QuoteType.COMPLEMENTARY.value,
            )
            .correlate(FreightModel)
            .scalar_subquery()
        )

        customer_name = func.coalesce(
            primary_version.customer_trade_name_snapshot,
            primary_version.customer_legal_name_snapshot,
        )

        return (
            select(
                FreightModel.freight_id.label(
                    "freight_id"
                ),
                FreightModel.customer_id.label(
                    "customer_id"
                ),
                primary_quote.quote_id.label(
                    "primary_quote_id"
                ),
                primary_quote.quote_number.label(
                    "primary_quote_number"
                ),
                primary_version.customer_legal_name_snapshot.label(
                    "customer_legal_name"
                ),
                primary_version.customer_trade_name_snapshot.label(
                    "customer_trade_name"
                ),
                customer_name.label(
                    "customer_name"
                ),
                primary_version.origin.label(
                    "origin"
                ),
                primary_version.destination.label(
                    "destination"
                ),
                FreightModel.current_status.label(
                    "current_status"
                ),
                contracted_revenue.label(
                    "contracted_revenue"
                ),
                approved_complementary_quote_count.label(
                    "approved_complementary_quote_count"
                ),
                FreightFinancialResultModel
                .freight_financial_result_id.label(
                    "financial_result_id"
                ),
                FreightModel.created_at.label(
                    "created_at"
                ),
                FreightModel.started_at.label(
                    "started_at"
                ),
                FreightModel.completed_at.label(
                    "completed_at"
                ),
                FreightModel.cancelled_at.label(
                    "cancelled_at"
                ),
            )
            .select_from(FreightModel)
            .join(
                primary_quote,
                and_(
                    primary_quote.quote_id
                    == FreightModel.primary_quote_id,
                    primary_quote.quote_type
                    == QuoteType.PRIMARY.value,
                ),
            )
            .join(
                primary_version,
                and_(
                    primary_version.quote_id
                    == primary_quote.quote_id,
                    primary_version.quote_version_id
                    == primary_quote.approved_version_id,
                ),
            )
            .outerjoin(
                FreightFinancialResultModel,
                FreightFinancialResultModel.freight_id
                == FreightModel.freight_id,
            )
        )

    @classmethod
    def _to_list_item(
        cls,
        row,
    ) -> FreightListItem:
        return FreightListItem(
            freight_id=row["freight_id"],
            customer_id=row["customer_id"],
            customer_name=cls._required_text(
                row["customer_name"],
                "identificação histórica do cliente",
            ),
            primary_quote_id=row["primary_quote_id"],
            primary_quote_number=cls._required_text(
                row["primary_quote_number"],
                "número do orçamento principal",
            ),
            origin=cls._required_text(
                row["origin"],
                "origem",
            ),
            destination=cls._required_text(
                row["destination"],
                "destino",
            ),
            current_status=FreightStatus(
                row["current_status"]
            ),
            contracted_revenue=cls._decimal(
                row["contracted_revenue"]
            ),
            financially_closed=(
                row["financial_result_id"] is not None
            ),
            created_at=row["created_at"],
            started_at=row["started_at"],
            completed_at=row["completed_at"],
            cancelled_at=row["cancelled_at"],
        )

    @classmethod
    def _to_details(
        cls,
        row,
        *,
        transport_units: tuple[
            FreightTransportUnitDetails,
            ...
        ],
        expenses: tuple[FreightExpenseDetails, ...],
        events: tuple[FreightEventDetails, ...],
        financial_result: FreightFinancialDetails | None,
    ) -> FreightDetails:
        return FreightDetails(
            freight_id=row["freight_id"],
            customer_id=row["customer_id"],
            customer_legal_name=cls._optional_text(
                row["customer_legal_name"]
            ),
            customer_trade_name=cls._optional_text(
                row["customer_trade_name"]
            ),
            primary_quote_id=row["primary_quote_id"],
            primary_quote_number=cls._required_text(
                row["primary_quote_number"],
                "número do orçamento principal",
            ),
            origin=cls._required_text(
                row["origin"],
                "origem",
            ),
            destination=cls._required_text(
                row["destination"],
                "destino",
            ),
            current_status=FreightStatus(
                row["current_status"]
            ),
            contracted_revenue=cls._decimal(
                row["contracted_revenue"]
            ),
            approved_complementary_quote_count=(
                row[
                    "approved_complementary_quote_count"
                ]
            ),
            financially_closed=(
                row["financial_result_id"] is not None
            ),
            financial_result_id=row[
                "financial_result_id"
            ],
            created_at=row["created_at"],
            started_at=row["started_at"],
            completed_at=row["completed_at"],
            cancelled_at=row["cancelled_at"],
            transport_units=transport_units,
            expenses=expenses,
            events=events,
            financial_result=financial_result,
        )

    @staticmethod
    def _required_text(
        value: str | None,
        field_name: str,
    ) -> str:
        if value is None or not value.strip():
            raise FreightPersistenceError(
                "Consulta de frete retornou "
                f"{field_name} ausente"
            )
        return value.strip()

    @staticmethod
    def _optional_text(
        value: str | None,
    ) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @staticmethod
    def _decimal(value) -> Decimal:
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))

    @classmethod
    def _optional_decimal(
        cls,
        value,
    ) -> Decimal | None:
        if value is None:
            return None
        return cls._decimal(value)
