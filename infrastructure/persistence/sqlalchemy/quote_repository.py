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
from domain.models.quote_transport_composition import (
    QuoteTransportComposition
)
from domain.models.quote_version import (
    QuoteVersion
)
from domain.quote_audit import (
    validate_quote_audit_consistency
)
from domain.quote_history_integrity import (
    validate_persisted_event_unchanged,
    validate_persisted_quote_state_update,
    validate_persisted_version_update
)
from infrastructure.persistence.sqlalchemy.models import (
    QuoteAdditionalModel,
    QuoteEventModel,
    QuoteInsuranceComponentModel,
    QuoteModel,
    QuoteTransportCompositionModel,
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
        self._validate_audit_consistency(
        quote
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

    def save(
        self,
        quote: Quote
    ) -> Quote:

        if quote.quote_id is None:
            raise ValueError(
                "Orçamento precisa possuir quote_id"
            )
        self._validate_audit_consistency(
        quote
    )
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
                    == quote.quote_id
                )
            )

            if model is None:
                raise QuotePersistenceError(
                    "Orçamento não encontrado para atualização"
                )

            self._validate_identity(
                model,
                quote
            )

            self._validate_history_integrity(
                model,
                quote
            )

            self._apply_quote(
                model,
                quote
            )

            self._sync_versions(
                model,
                quote.versions
            )

            self._session.flush()

            self._sync_events(
                model,
                quote.events
            )

            self._session.flush()

        except QuotePersistenceError:
            raise

        except IntegrityError as error:
            raise QuotePersistenceError(
                "Não foi possível atualizar o orçamento"
            ) from error

        except SQLAlchemyError as error:
            raise QuotePersistenceError(
                "Não foi possível atualizar o orçamento"
            ) from error

        saved_quote = self.get_by_id(
            quote.quote_id
        )

        if saved_quote is None:
            raise QuotePersistenceError(
                "Orçamento atualizado não pôde ser recuperado"
            )

        return saved_quote

    @staticmethod
    def _validate_identity(
        model: QuoteModel,
        quote: Quote
    ) -> None:

        if model.quote_number != quote.quote_number:
            raise QuotePersistenceError(
                "Número do orçamento não pode ser alterado"
            )

        if model.customer_id != quote.customer_id:
            raise QuotePersistenceError(
                "Cliente do orçamento não pode ser alterado"
            )

        if model.quote_type != quote.quote_type.value:
            raise QuotePersistenceError(
                "Tipo do orçamento não pode ser alterado"
            )

        if model.primary_quote_id != quote.primary_quote_id:
            raise QuotePersistenceError(
                "Vínculo com orçamento principal não pode ser alterado"
            )
    @staticmethod
    def _validate_audit_consistency(
        quote: Quote
    ) -> None:

        try:
            validate_quote_audit_consistency(
                quote
            )
        except ValueError as error:
            raise QuotePersistenceError(
                str(error)
            ) from error


    @classmethod
    def _validate_history_integrity(
        cls,
        model: QuoteModel,
        quote: Quote
    ) -> None:

        try:
            validate_persisted_quote_state_update(
                persisted_status=QuoteStatus(
                    model.current_status
                ),
                persisted_approved_version_id=(
                    model.approved_version_id
                ),
                candidate_status=quote.current_status,
                candidate_approved_version_id=(
                    quote.approved_version_id
                )
            )

            existing_versions = {
                item.quote_version_id: item
                for item in model.versions
            }

            for version in quote.versions:
                if version.quote_version_id is None:
                    continue

                version_model = existing_versions.get(
                    version.quote_version_id
                )

                if version_model is None:
                    continue

                validate_persisted_version_update(
                    cls._version_to_domain(
                        version_model
                    ),
                    version
                )

            existing_events = {
                item.quote_event_id: item
                for item in model.events
            }

            for event in quote.events:
                if event.quote_event_id is None:
                    continue

                event_model = existing_events.get(
                    event.quote_event_id
                )

                if event_model is None:
                    continue

                validate_persisted_event_unchanged(
                    cls._event_to_domain(
                        event_model
                    ),
                    event
                )

        except ValueError as error:
            raise QuotePersistenceError(
                str(error)
            ) from error

    @classmethod
    def _apply_quote(
        cls,
        model: QuoteModel,
        quote: Quote
    ) -> None:

        model.freight_id = quote.freight_id
        model.current_status = quote.current_status.value
        model.approved_version_id = quote.approved_version_id

    @classmethod
    def _sync_versions(
        cls,
        model: QuoteModel,
        versions: tuple[QuoteVersion, ...]
    ) -> None:

        existing_by_id = {
            version.quote_version_id: version
            for version in model.versions
        }

        received_existing_ids = {
            version.quote_version_id
            for version in versions
            if version.quote_version_id is not None
        }

        if set(existing_by_id) - received_existing_ids:
            raise QuotePersistenceError(
                "Versões persistidas do orçamento não podem ser removidas"
            )

        for version in versions:

            if version.quote_version_id is None:
                model.versions.append(
                    cls._version_to_model(
                        version
                    )
                )
                continue

            version_model = existing_by_id.get(
                version.quote_version_id
            )

            if version_model is None:
                raise QuotePersistenceError(
                    "Versão do orçamento não pertence ao agregado persistido"
                )

            cls._apply_version(
                version_model,
                version
            )

    @classmethod
    def _apply_version(
        cls,
        model: QuoteVersionModel,
        version: QuoteVersion
    ) -> None:

        model.version_number = version.version_number
        model.customer_person_type_snapshot = (
            version.customer_person_type_snapshot.value
        )
        model.customer_document_snapshot = (
            version.customer_document_snapshot
        )
        model.customer_legal_name_snapshot = (
            version.customer_legal_name_snapshot
        )
        model.customer_trade_name_snapshot = (
            version.customer_trade_name_snapshot
        )
        model.modality = version.modality
        model.origin = version.origin
        model.destination = version.destination
        model.invoice_value = version.invoice_value
        model.tracking_required = version.tracking_required
        model.driver_amount = version.driver_amount
        model.toll_amount = version.toll_amount
        model.additional_total = version.additional_total
        model.freight_insurance_total = (
            version.freight_insurance_total
        )
        model.bp01 = version.bp01
        model.administrative_rate = version.administrative_rate
        model.administrative_minimum = (
            version.administrative_minimum
        )
        model.administrative_cost = version.administrative_cost
        model.bp02 = version.bp02
        model.margin_band_minimum = version.margin_band_minimum
        model.margin_band_maximum = version.margin_band_maximum
        model.standard_margin_rate = version.standard_margin_rate
        model.standard_margin_value = version.standard_margin_value
        model.target_net_value = version.target_net_value
        model.tax_rate = version.tax_rate
        model.tax_value = version.tax_value
        model.calculated_price = version.calculated_price
        model.rounded_price = version.rounded_price
        model.offered_price = version.offered_price
        model.contracted_price = version.contracted_price
        model.offered_margin_value = version.offered_margin_value
        model.offered_margin_rate = version.offered_margin_rate
        model.contracted_margin_value = (
            version.contracted_margin_value
        )
        model.contracted_margin_rate = (
            version.contracted_margin_rate
        )
        model.validity_days_snapshot = (
            version.validity_days_snapshot
        )
        model.valid_until = version.valid_until
        model.internal_observation = version.internal_observation
        model.proposal_observation = version.proposal_observation

        cls._sync_transport_compositions(
            model,
            version.transport_compositions
        )

        cls._sync_additionals(
            model,
            version.additionals
        )

        cls._sync_insurance_components(
            model,
            version.insurance_components
        )

    @classmethod
    def _sync_transport_compositions(
        cls,
        model: QuoteVersionModel,
        compositions: tuple[QuoteTransportComposition, ...]
    ) -> None:

        existing_by_id = {
            item.quote_transport_composition_id: item
            for item in model.transport_compositions
        }
        existing_by_position = {
            item.position: item
            for item in model.transport_compositions
        }

        synchronized: list[QuoteTransportCompositionModel] = []
        used_ids: set[int] = set()

        for composition in compositions:

            composition_model = None

            if composition.quote_transport_composition_id is not None:
                composition_model = existing_by_id.get(
                    composition.quote_transport_composition_id
                )

            if composition_model is None:
                candidate = existing_by_position.get(
                    composition.position
                )
                if (
                    candidate is not None
                    and candidate.quote_transport_composition_id
                    not in used_ids
                ):
                    composition_model = candidate

            if composition_model is None:
                composition_model = (
                    cls._transport_composition_to_model(
                        composition
                    )
                )
            else:
                composition_model.position = composition.position
                composition_model.axle_count = composition.axle_count
                composition_model.include_return_trip = (
                    composition.include_return_trip
                )
                composition_model.distance_km = composition.distance_km
                composition_model.driver_amount = composition.driver_amount
                composition_model.toll_amount = composition.toll_amount

            if composition_model.quote_transport_composition_id is not None:
                used_ids.add(
                    composition_model.quote_transport_composition_id
                )

            synchronized.append(
                composition_model
            )

        model.transport_compositions = synchronized

    @classmethod
    def _sync_additionals(
        cls,
        model: QuoteVersionModel,
        additionals: tuple[QuoteAdditional, ...]
    ) -> None:

        existing_by_id = {
            item.quote_additional_id: item
            for item in model.additionals
        }
        existing_by_position = {
            item.position: item
            for item in model.additionals
        }

        synchronized: list[QuoteAdditionalModel] = []
        used_ids: set[int] = set()

        for additional in additionals:

            additional_model = None

            if additional.quote_additional_id is not None:
                additional_model = existing_by_id.get(
                    additional.quote_additional_id
                )

            if additional_model is None:
                candidate = existing_by_position.get(
                    additional.position
                )
                if (
                    candidate is not None
                    and candidate.quote_additional_id not in used_ids
                ):
                    additional_model = candidate

            if additional_model is None:
                additional_model = cls._additional_to_model(
                    additional
                )
            else:
                additional_model.additional_type = (
                    additional.additional_type.value
                )
                additional_model.custom_description = (
                    additional.custom_description
                )
                additional_model.value = additional.value
                additional_model.position = additional.position

            if additional_model.quote_additional_id is not None:
                used_ids.add(
                    additional_model.quote_additional_id
                )

            synchronized.append(
                additional_model
            )

        model.additionals = synchronized

    @classmethod
    def _sync_insurance_components(
        cls,
        model: QuoteVersionModel,
        components: tuple[QuoteInsuranceComponent, ...]
    ) -> None:

        existing_by_id = {
            item.quote_insurance_component_id: item
            for item in model.insurance_components
        }
        existing_by_position = {
            item.position: item
            for item in model.insurance_components
        }

        synchronized: list[QuoteInsuranceComponentModel] = []
        used_ids: set[int] = set()

        for component in components:

            component_model = None

            if component.quote_insurance_component_id is not None:
                component_model = existing_by_id.get(
                    component.quote_insurance_component_id
                )

            if component_model is None:
                candidate = existing_by_position.get(
                    component.position
                )
                if (
                    candidate is not None
                    and candidate.quote_insurance_component_id
                    not in used_ids
                ):
                    component_model = candidate

            if component_model is None:
                component_model = cls._insurance_to_model(
                    component
                )
            else:
                component_model.insurance_type = (
                    component.insurance_type.value
                )
                component_model.calculation_base = (
                    component.calculation_base
                )
                component_model.rate = component.rate
                component_model.value = component.value
                component_model.position = component.position

            if component_model.quote_insurance_component_id is not None:
                used_ids.add(
                    component_model.quote_insurance_component_id
                )

            synchronized.append(
                component_model
            )

        model.insurance_components = synchronized

    @classmethod
    def _sync_events(
        cls,
        model: QuoteModel,
        events: tuple[QuoteEvent, ...]
    ) -> None:

        existing_ids = {
            event.quote_event_id
            for event in model.events
        }

        received_existing_ids = {
            event.quote_event_id
            for event in events
            if event.quote_event_id is not None
        }

        if existing_ids - received_existing_ids:
            raise QuotePersistenceError(
                "Eventos persistidos do orçamento não podem ser removidos"
            )

        for event in events:

            if event.quote_event_id is not None:
                if event.quote_event_id not in existing_ids:
                    raise QuotePersistenceError(
                        "Evento não pertence ao orçamento persistido"
                    )
                continue

            model.events.append(
                cls._event_to_model(
                    event
                )
            )

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

    def get_by_id_for_update(
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
                .with_for_update()
            )

        except SQLAlchemyError as error:

            raise QuotePersistenceError(
                "Não foi possível bloquear "
                "o orçamento para atualização"
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
                QuoteVersionModel.transport_compositions
            ),
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

        model.transport_compositions = [
            cls._transport_composition_to_model(
                composition
            )
            for composition
            in version.transport_compositions
        ]

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
    def _transport_composition_to_model(
        composition: QuoteTransportComposition
    ) -> QuoteTransportCompositionModel:

        return QuoteTransportCompositionModel(
            position=composition.position,
            axle_count=composition.axle_count,
            include_return_trip=(
                composition.include_return_trip
            ),
            distance_km=composition.distance_km,
            driver_amount=composition.driver_amount,
            toll_amount=composition.toll_amount
        )

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

        transport_compositions = tuple(
            QuoteTransportComposition(
                quote_transport_composition_id=(
                    composition
                    .quote_transport_composition_id
                ),
                quote_version_id=(
                    composition.quote_version_id
                ),
                position=composition.position,
                axle_count=composition.axle_count,
                include_return_trip=(
                    composition.include_return_trip
                ),
                distance_km=composition.distance_km,
                driver_amount=composition.driver_amount,
                toll_amount=composition.toll_amount
            )
            for composition
            in model.transport_compositions
        )

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
            transport_compositions=(
                transport_compositions
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