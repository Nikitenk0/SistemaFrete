from sqlalchemy import (
    select
)
from sqlalchemy.exc import (
    IntegrityError,
    SQLAlchemyError
)
from sqlalchemy.orm import (
    Session,
    selectinload
)

from application.exceptions import (
    QuotePersistenceError
)
from application.ports.quote_repository import (
    QuoteRepository
)
from domain.models.customer import (
    CustomerPersonType
)
from domain.models.quote import (
    Quote,
    QuoteStatus,
    QuoteType
)
from domain.models.quote_additional import (
    QuoteAdditional,
    QuoteAdditionalType
)
from domain.models.quote_event import (
    QuoteEvent,
    QuoteEventType
)
from domain.models.quote_insurance_component import (
    QuoteInsuranceComponent,
    QuoteInsuranceType
)
from domain.models.quote_version import (
    QuoteVersion
)
from infrastructure.persistence.sqlalchemy.models import (
    QuoteAdditionalModel,
    QuoteEventModel,
    QuoteInsuranceComponentModel,
    QuoteModel,
    QuoteVersionModel
)


class SqlAlchemyQuoteRepository(
    QuoteRepository
):

    def __init__(
        self,
        session: Session
    ):
        self._session = session

    def add(
        self,
        quote: Quote
    ) -> Quote:

        if quote.quote_id is not None:
            raise ValueError(
                "Orçamento já possui quote_id"
            )

        model = self._to_model(
            quote
        )

        self._session.add(
            model
        )

        try:

            self._session.flush()

        except IntegrityError as error:

            raise QuotePersistenceError(
                "Não foi possível salvar "
                "o orçamento"
            ) from error

        except SQLAlchemyError as error:

            raise QuotePersistenceError(
                "Não foi possível salvar "
                "o orçamento"
            ) from error

        created_quote = self.get_by_id(
            model.quote_id
        )

        if created_quote is None:
            raise QuotePersistenceError(
                "Orçamento salvo não pôde "
                "ser recuperado"
            )

        return created_quote

    def get_by_id(
        self,
        quote_id: int
    ) -> Quote | None:

        try:

            model = self._session.scalar(
                select(
                    QuoteModel
                )
                .options(
                    *self._load_options()
                )
                .where(
                    QuoteModel.quote_id
                    == quote_id
                )
            )

        except SQLAlchemyError as error:

            raise QuotePersistenceError(
                "Não foi possível consultar "
                "o orçamento"
            ) from error

        if model is None:
            return None

        return self._to_domain(
            model
        )

    def get_by_number(
        self,
        quote_number: str
    ) -> Quote | None:

        try:

            model = self._session.scalar(
                select(
                    QuoteModel
                )
                .options(
                    *self._load_options()
                )
                .where(
                    QuoteModel.quote_number
                    == quote_number
                )
            )

        except SQLAlchemyError as error:

            raise QuotePersistenceError(
                "Não foi possível consultar "
                "o orçamento"
            ) from error

        if model is None:
            return None

        return self._to_domain(
            model
        )

    @staticmethod
    def _load_options():

        return (
            selectinload(
                QuoteModel.versions
            ).selectinload(
                QuoteVersionModel.additionals
            ),
            selectinload(
                QuoteModel.versions
            ).selectinload(
                QuoteVersionModel.insurance_components
            ),
            selectinload(
                QuoteModel.events
            )
        )

    @classmethod
    def _to_model(
        cls,
        quote: Quote
    ) -> QuoteModel:

        model = QuoteModel(
            quote_number=quote.quote_number,
            quote_type=quote.quote_type.value,
            customer_id=quote.customer_id,
            primary_quote_id=(
                quote.primary_quote_id
            ),
            freight_id=quote.freight_id,
            current_status=(
                quote.current_status.value
            ),
            approved_version_id=(
                quote.approved_version_id
            ),
            created_by=quote.created_by
        )

        if quote.created_at is not None:
            model.created_at = quote.created_at

        model.versions = [
            cls._version_to_model(
                version
            )
            for version in quote.versions
        ]

        model.events = [
            cls._event_to_model(
                event
            )
            for event in quote.events
        ]

        return model

    @classmethod
    def _version_to_model(
        cls,
        version: QuoteVersion
    ) -> QuoteVersionModel:

        model = QuoteVersionModel(
            version_number=(
                version.version_number
            ),
            customer_person_type_snapshot=(
                version
                .customer_person_type_snapshot
                .value
            ),
            customer_document_snapshot=(
                version
                .customer_document_snapshot
            ),
            customer_legal_name_snapshot=(
                version
                .customer_legal_name_snapshot
            ),
            customer_trade_name_snapshot=(
                version
                .customer_trade_name_snapshot
            ),
            modality=version.modality,
            origin=version.origin,
            destination=version.destination,
            distance_km=version.distance_km,
            axle_count=version.axle_count,
            include_return_trip=(
                version.include_return_trip
            ),
            invoice_value=version.invoice_value,
            tracking_required=(
                version.tracking_required
            ),
            driver_amount=version.driver_amount,
            toll_amount=version.toll_amount,
            additional_total=(
                version.additional_total
            ),
            freight_insurance_total=(
                version.freight_insurance_total
            ),
            bp01=version.bp01,
            administrative_rate=(
                version.administrative_rate
            ),
            administrative_minimum=(
                version.administrative_minimum
            ),
            administrative_cost=(
                version.administrative_cost
            ),
            bp02=version.bp02,
            margin_band_minimum=(
                version.margin_band_minimum
            ),
            margin_band_maximum=(
                version.margin_band_maximum
            ),
            standard_margin_rate=(
                version.standard_margin_rate
            ),
            standard_margin_value=(
                version.standard_margin_value
            ),
            target_net_value=(
                version.target_net_value
            ),
            tax_rate=version.tax_rate,
            tax_value=version.tax_value,
            calculated_price=(
                version.calculated_price
            ),
            rounded_price=(
                version.rounded_price
            ),
            offered_price=(
                version.offered_price
            ),
            contracted_price=(
                version.contracted_price
            ),
            offered_margin_value=(
                version.offered_margin_value
            ),
            offered_margin_rate=(
                version.offered_margin_rate
            ),
            contracted_margin_value=(
                version.contracted_margin_value
            ),
            contracted_margin_rate=(
                version.contracted_margin_rate
            ),
            validity_days_snapshot=(
                version.validity_days_snapshot
            ),
            valid_until=version.valid_until,
            internal_observation=(
                version.internal_observation
            ),
            proposal_observation=(
                version.proposal_observation
            ),
            created_by=version.created_by
        )

        if version.created_at is not None:
            model.created_at = version.created_at

        model.additionals = [
            cls._additional_to_model(
                additional
            )
            for additional
            in version.additionals
        ]

        model.insurance_components = [
            cls._insurance_to_model(
                component
            )
            for component
            in version.insurance_components
        ]

        return model

    @staticmethod
    def _additional_to_model(
        additional: QuoteAdditional
    ) -> QuoteAdditionalModel:

        return QuoteAdditionalModel(
            additional_type=(
                additional.additional_type.value
            ),
            custom_description=(
                additional.custom_description
            ),
            value=additional.value,
            position=additional.position
        )

    @staticmethod
    def _insurance_to_model(
        component: QuoteInsuranceComponent
    ) -> QuoteInsuranceComponentModel:

        return QuoteInsuranceComponentModel(
            insurance_type=(
                component.insurance_type.value
            ),
            calculation_base=(
                component.calculation_base
            ),
            rate=component.rate,
            value=component.value,
            position=component.position
        )

    @staticmethod
    def _event_to_model(
        event: QuoteEvent
    ) -> QuoteEventModel:

        model = QuoteEventModel(
            quote_version_id=(
                event.quote_version_id
            ),
            event_type=event.event_type.value,
            previous_status=(
                event.previous_status.value
                if event.previous_status
                is not None
                else None
            ),
            new_status=(
                event.new_status.value
                if event.new_status
                is not None
                else None
            ),
            previous_amount=(
                event.previous_amount
            ),
            new_amount=event.new_amount,
            reason_code=event.reason_code,
            observation=event.observation,
            user_id=event.user_id
        )

        if event.occurred_at is not None:
            model.occurred_at = (
                event.occurred_at
            )

        return model

    @classmethod
    def _to_domain(
        cls,
        model: QuoteModel
    ) -> Quote:

        versions = tuple(
            cls._version_to_domain(
                version
            )
            for version in model.versions
        )

        events = tuple(
            cls._event_to_domain(
                event
            )
            for event in model.events
        )

        return Quote(
            quote_id=model.quote_id,
            quote_number=model.quote_number,
            customer_id=model.customer_id,
            quote_type=QuoteType(
                model.quote_type
            ),
            primary_quote_id=(
                model.primary_quote_id
            ),
            freight_id=model.freight_id,
            current_status=QuoteStatus(
                model.current_status
            ),
            approved_version_id=(
                model.approved_version_id
            ),
            versions=versions,
            events=events,
            created_at=model.created_at,
            created_by=model.created_by
        )

    @classmethod
    def _version_to_domain(
        cls,
        model: QuoteVersionModel
    ) -> QuoteVersion:

        additionals = tuple(
            QuoteAdditional(
                quote_additional_id=(
                    additional.quote_additional_id
                ),
                quote_version_id=(
                    additional.quote_version_id
                ),
                additional_type=(
                    QuoteAdditionalType(
                        additional.additional_type
                    )
                ),
                custom_description=(
                    additional.custom_description
                ),
                value=additional.value,
                position=additional.position
            )
            for additional
            in model.additionals
        )

        insurance_components = tuple(
            QuoteInsuranceComponent(
                quote_insurance_component_id=(
                    component
                    .quote_insurance_component_id
                ),
                quote_version_id=(
                    component.quote_version_id
                ),
                insurance_type=(
                    QuoteInsuranceType(
                        component.insurance_type
                    )
                ),
                calculation_base=(
                    component.calculation_base
                ),
                rate=component.rate,
                value=component.value,
                position=component.position
            )
            for component
            in model.insurance_components
        )

        return QuoteVersion(
            quote_version_id=(
                model.quote_version_id
            ),
            quote_id=model.quote_id,
            version_number=(
                model.version_number
            ),
            customer_person_type_snapshot=(
                CustomerPersonType(
                    model
                    .customer_person_type_snapshot
                )
            ),
            customer_document_snapshot=(
                model.customer_document_snapshot
            ),
            customer_legal_name_snapshot=(
                model
                .customer_legal_name_snapshot
            ),
            customer_trade_name_snapshot=(
                model
                .customer_trade_name_snapshot
            ),
            modality=model.modality,
            origin=model.origin,
            destination=model.destination,
            distance_km=model.distance_km,
            axle_count=model.axle_count,
            include_return_trip=(
                model.include_return_trip
            ),
            invoice_value=model.invoice_value,
            tracking_required=(
                model.tracking_required
            ),
            driver_amount=model.driver_amount,
            toll_amount=model.toll_amount,
            additional_total=(
                model.additional_total
            ),
            freight_insurance_total=(
                model.freight_insurance_total
            ),
            bp01=model.bp01,
            administrative_rate=(
                model.administrative_rate
            ),
            administrative_minimum=(
                model.administrative_minimum
            ),
            administrative_cost=(
                model.administrative_cost
            ),
            bp02=model.bp02,
            margin_band_minimum=(
                model.margin_band_minimum
            ),
            margin_band_maximum=(
                model.margin_band_maximum
            ),
            standard_margin_rate=(
                model.standard_margin_rate
            ),
            standard_margin_value=(
                model.standard_margin_value
            ),
            target_net_value=(
                model.target_net_value
            ),
            tax_rate=model.tax_rate,
            tax_value=model.tax_value,
            calculated_price=(
                model.calculated_price
            ),
            rounded_price=(
                model.rounded_price
            ),
            offered_price=(
                model.offered_price
            ),
            contracted_price=(
                model.contracted_price
            ),
            offered_margin_value=(
                model.offered_margin_value
            ),
            offered_margin_rate=(
                model.offered_margin_rate
            ),
            contracted_margin_value=(
                model.contracted_margin_value
            ),
            contracted_margin_rate=(
                model.contracted_margin_rate
            ),
            validity_days_snapshot=(
                model.validity_days_snapshot
            ),
            valid_until=model.valid_until,
            internal_observation=(
                model.internal_observation
            ),
            proposal_observation=(
                model.proposal_observation
            ),
            additionals=additionals,
            insurance_components=(
                insurance_components
            ),
            created_at=model.created_at,
            created_by=model.created_by
        )

    @staticmethod
    def _event_to_domain(
        model: QuoteEventModel
    ) -> QuoteEvent:

        return QuoteEvent(
            quote_event_id=(
                model.quote_event_id
            ),
            quote_id=model.quote_id,
            quote_version_id=(
                model.quote_version_id
            ),
            event_type=QuoteEventType(
                model.event_type
            ),
            previous_status=(
                QuoteStatus(
                    model.previous_status
                )
                if model.previous_status
                is not None
                else None
            ),
            new_status=(
                QuoteStatus(
                    model.new_status
                )
                if model.new_status
                is not None
                else None
            ),
            previous_amount=(
                model.previous_amount
            ),
            new_amount=model.new_amount,
            reason_code=model.reason_code,
            observation=model.observation,
            user_id=model.user_id,
            occurred_at=model.occurred_at
        )