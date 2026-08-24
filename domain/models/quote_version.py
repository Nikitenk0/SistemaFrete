from dataclasses import dataclass
from datetime import (
    date,
    datetime
)
from decimal import Decimal

from domain.models.customer import (
    CustomerPersonType
)
from domain.models.quote_additional import (
    QuoteAdditional
)
from domain.models.quote_insurance_component import (
    QuoteInsuranceComponent
)
from domain.models.quote_transport_composition import (
    QuoteTransportComposition
)


@dataclass(frozen=True)
class QuoteVersion:

    version_number: int

    customer_person_type_snapshot: CustomerPersonType
    customer_document_snapshot: str

    customer_legal_name_snapshot: str | None = None
    customer_trade_name_snapshot: str | None = None

    modality: str | None = None

    origin: str | None = None
    destination: str | None = None

    invoice_value: Decimal | None = None

    tracking_required: bool = False

    driver_amount: Decimal | None = None
    toll_amount: Decimal | None = None

    additional_total: Decimal | None = None

    freight_insurance_total: Decimal | None = None

    bp01: Decimal | None = None

    administrative_rate: Decimal | None = None
    administrative_minimum: Decimal | None = None
    administrative_cost: Decimal | None = None

    bp02: Decimal | None = None

    margin_band_minimum: Decimal | None = None
    margin_band_maximum: Decimal | None = None

    standard_margin_rate: Decimal | None = None
    standard_margin_value: Decimal | None = None

    target_net_value: Decimal | None = None

    tax_rate: Decimal | None = None
    tax_value: Decimal | None = None

    calculated_price: Decimal | None = None
    rounded_price: Decimal | None = None
    offered_price: Decimal | None = None
    contracted_price: Decimal | None = None

    offered_margin_value: Decimal | None = None
    offered_margin_rate: Decimal | None = None

    contracted_margin_value: Decimal | None = None
    contracted_margin_rate: Decimal | None = None

    validity_days_snapshot: int | None = None
    valid_until: date | None = None

    internal_observation: str | None = None
    proposal_observation: str | None = None

    transport_compositions: tuple[
        QuoteTransportComposition,
        ...
    ] = ()

    additionals: tuple[
        QuoteAdditional,
        ...
    ] = ()

    insurance_components: tuple[
        QuoteInsuranceComponent,
        ...
    ] = ()

    quote_version_id: int | None = None
    quote_id: int | None = None

    created_at: datetime | None = None
    created_by: int | None = None

    def __post_init__(
        self
    ) -> None:

        if self.version_number < 1:
            raise ValueError(
                "Número da versão inválido"
            )

        document = "".join(
            character
            for character
            in self.customer_document_snapshot
            if character.isdigit()
        )

        expected_length = (
            11
            if self.customer_person_type_snapshot
            == CustomerPersonType.INDIVIDUAL
            else 14
        )

        if len(document) != expected_length:
            raise ValueError(
                "Documento do snapshot "
                "do cliente é inválido"
            )

        legal_name = self._clean_optional_text(
            self.customer_legal_name_snapshot
        )

        trade_name = self._clean_optional_text(
            self.customer_trade_name_snapshot
        )

        if not legal_name and not trade_name:
            raise ValueError(
                "Snapshot do cliente precisa "
                "possuir identificação"
            )

        non_negative_values = (
            self.invoice_value,
            self.driver_amount,
            self.toll_amount,
            self.additional_total,
            self.freight_insurance_total,
            self.bp01,
            self.administrative_rate,
            self.administrative_minimum,
            self.administrative_cost,
            self.bp02,
            self.margin_band_minimum,
            self.margin_band_maximum,
            self.standard_margin_rate,
            self.standard_margin_value,
            self.target_net_value,
            self.tax_rate,
            self.tax_value,
            self.calculated_price,
            self.rounded_price,
            self.offered_price,
            self.contracted_price
        )

        if any(
            value is not None
            and value < 0
            for value in non_negative_values
        ):
            raise ValueError(
                "Valores financeiros do orçamento "
                "não podem ser negativos"
            )

        if (
            self.validity_days_snapshot is not None
            and self.validity_days_snapshot < 0
        ):
            raise ValueError(
                "Validade do orçamento inválida"
            )

        self._validate_unique_positions(
            (
                composition.position
                for composition
                in self.transport_compositions
            ),
            "composições de transporte"
        )

        self._validate_unique_positions(
            (
                additional.position
                for additional
                in self.additionals
            ),
            "adicionais"
        )

        self._validate_unique_positions(
            (
                component.position
                for component
                in self.insurance_components
            ),
            "seguros"
        )

        object.__setattr__(
            self,
            "customer_document_snapshot",
            document
        )

        object.__setattr__(
            self,
            "customer_legal_name_snapshot",
            legal_name
        )

        object.__setattr__(
            self,
            "customer_trade_name_snapshot",
            trade_name
        )

    @staticmethod
    def _validate_unique_positions(
        positions,
        item_name: str
    ) -> None:

        position_list = list(
            positions
        )

        if (
            len(position_list)
            != len(set(position_list))
        ):
            raise ValueError(
                f"Existem {item_name} "
                "com posição duplicada"
            )

    @staticmethod
    def _clean_optional_text(
        value: str | None
    ) -> str | None:

        if value is None:
            return None

        cleaned_value = value.strip()

        return (
            cleaned_value
            if cleaned_value
            else None
        )
