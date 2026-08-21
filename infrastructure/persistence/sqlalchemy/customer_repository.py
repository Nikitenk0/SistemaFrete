from sqlalchemy import (
    or_,
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
    CustomerAlreadyExistsError,
    CustomerPersistenceError
)
from application.ports.customer_repository import (
    CustomerRepository
)
from domain.models.customer import (
    Customer,
    CustomerPersonType,
    CustomerStatus
)
from domain.models.customer_address import (
    CustomerAddress,
    CustomerAddressType
)
from domain.models.customer_contact import (
    CustomerContact
)
from domain.models.customer_operational_location import (
    CustomerOperationalLocation
)
from infrastructure.persistence.sqlalchemy.models import (
    CustomerAddressModel,
    CustomerContactModel,
    CustomerModel,
    CustomerOperationalLocationModel
)


class SqlAlchemyCustomerRepository(
    CustomerRepository
):

    def __init__(
        self,
        session: Session
    ):
        self._session = session

    def add(
        self,
        customer: Customer
    ) -> Customer:

        if customer.customer_id is not None:
            raise ValueError(
                "Cliente já possui customer_id"
            )

        model = self._to_model(
            customer
        )

        self._session.add(
            model
        )

        try:

            self._session.flush()

        except IntegrityError as error:

            constraint_name = (
                self._get_constraint_name(
                    error
                )
            )

            if (
                constraint_name
                == "uq_customers_document"
            ):
                raise CustomerAlreadyExistsError(
                    "CPF/CNPJ já cadastrado"
                ) from error

            raise CustomerPersistenceError(
                "Não foi possível salvar o cliente"
            ) from error

        except SQLAlchemyError as error:

            raise CustomerPersistenceError(
                "Não foi possível salvar o cliente"
            ) from error

        return self._to_domain(
            model
        )

    def get_by_id(
        self,
        customer_id: int
    ) -> Customer | None:

        try:

            model = self._session.scalar(
                select(
                    CustomerModel
                )
                .options(
                    *self._load_options()
                )
                .where(
                    CustomerModel.customer_id
                    == customer_id
                )
            )

        except SQLAlchemyError as error:

            raise CustomerPersistenceError(
                "Não foi possível consultar o cliente"
            ) from error

        if model is None:
            return None

        return self._to_domain(
            model
        )

    def get_by_document(
        self,
        document: str
    ) -> Customer | None:

        normalized_document = (
            self._normalize_document(
                document
            )
        )

        try:

            model = self._session.scalar(
                select(
                    CustomerModel
                )
                .options(
                    *self._load_options()
                )
                .where(
                    CustomerModel.document
                    == normalized_document
                )
            )

        except SQLAlchemyError as error:

            raise CustomerPersistenceError(
                "Não foi possível consultar o cliente"
            ) from error

        if model is None:
            return None

        return self._to_domain(
            model
        )

    def search(
        self,
        query: str,
        limit: int = 20
    ) -> tuple[Customer, ...]:

        query = query.strip()

        if not query:
            return ()

        normalized_document = (
            self._normalize_document(
                query
            )
        )

        conditions = [
            CustomerModel.legal_name.ilike(
                f"%{query}%"
            ),
            CustomerModel.trade_name.ilike(
                f"%{query}%"
            )
        ]

        if normalized_document:
            conditions.append(
                CustomerModel.document.contains(
                    normalized_document
                )
            )

        try:

            models = self._session.scalars(
                select(
                    CustomerModel
                )
                .options(
                    *self._load_options()
                )
                .where(
                    or_(
                        *conditions
                    )
                )
                .order_by(
                    CustomerModel.legal_name,
                    CustomerModel.trade_name,
                    CustomerModel.customer_id
                )
                .limit(
                    limit
                )
            ).all()

        except SQLAlchemyError as error:

            raise CustomerPersistenceError(
                "Não foi possível pesquisar clientes"
            ) from error

        return tuple(
            self._to_domain(
                model
            )
            for model in models
        )

    @staticmethod
    def _load_options():

        return (
            selectinload(
                CustomerModel.contacts
            ),
            selectinload(
                CustomerModel.addresses
            ),
            selectinload(
                CustomerModel.operational_locations
            )
        )

    @classmethod
    def _to_model(
        cls,
        customer: Customer
    ) -> CustomerModel:

        model = CustomerModel(
            customer_group_id=(
                customer.customer_group_id
            ),
            person_type=(
                customer.person_type.value
            ),
            document=customer.document,
            legal_name=customer.legal_name,
            trade_name=customer.trade_name,
            state_registration=(
                customer.state_registration
            ),
            status=customer.status.value,
            general_observation=(
                customer.general_observation
            ),
            created_by=customer.created_by,
            updated_by=customer.updated_by
        )

        if customer.created_at is not None:
            model.created_at = (
                customer.created_at
            )

        if customer.updated_at is not None:
            model.updated_at = (
                customer.updated_at
            )

        model.contacts = [
            cls._to_contact_model(
                contact
            )
            for contact in customer.contacts
        ]

        model.addresses = [
            cls._to_address_model(
                address
            )
            for address in customer.addresses
        ]

        model.operational_locations = [
            cls._to_operational_location_model(
                location
            )
            for location
            in customer.operational_locations
        ]

        return model

    @staticmethod
    def _to_contact_model(
        contact: CustomerContact
    ) -> CustomerContactModel:

        model = CustomerContactModel(
            name=contact.name,
            phone=contact.phone,
            whatsapp=contact.whatsapp,
            email=contact.email,
            position_or_department=(
                contact.position_or_department
            ),
            is_primary=contact.is_primary,
            created_by=contact.created_by,
            updated_by=contact.updated_by
        )

        if contact.created_at is not None:
            model.created_at = (
                contact.created_at
            )

        if contact.updated_at is not None:
            model.updated_at = (
                contact.updated_at
            )

        return model

    @staticmethod
    def _to_address_model(
        address: CustomerAddress
    ) -> CustomerAddressModel:

        model = CustomerAddressModel(
            address_type=(
                address.address_type.value
            ),
            postal_code=address.postal_code,
            street=address.street,
            number=address.number,
            complement=address.complement,
            district=address.district,
            city=address.city,
            state=address.state,
            is_primary=address.is_primary,
            created_by=address.created_by,
            updated_by=address.updated_by
        )

        if address.created_at is not None:
            model.created_at = (
                address.created_at
            )

        if address.updated_at is not None:
            model.updated_at = (
                address.updated_at
            )

        return model

    @staticmethod
    def _to_operational_location_model(
        location: CustomerOperationalLocation
    ) -> CustomerOperationalLocationModel:

        model = CustomerOperationalLocationModel(
            name=location.name,
            postal_code=location.postal_code,
            street=location.street,
            number=location.number,
            complement=location.complement,
            district=location.district,
            city=location.city,
            state=location.state,
            observation=location.observation,
            is_active=location.is_active,
            created_by=location.created_by,
            updated_by=location.updated_by
        )

        if location.created_at is not None:
            model.created_at = (
                location.created_at
            )

        if location.updated_at is not None:
            model.updated_at = (
                location.updated_at
            )

        return model

    @staticmethod
    def _to_domain(
        model: CustomerModel
    ) -> Customer:

        contacts = tuple(
            CustomerContact(
                customer_contact_id=(
                    contact.customer_contact_id
                ),
                customer_id=(
                    contact.customer_id
                ),
                name=contact.name,
                phone=contact.phone,
                whatsapp=contact.whatsapp,
                email=contact.email,
                position_or_department=(
                    contact.position_or_department
                ),
                is_primary=contact.is_primary,
                created_at=contact.created_at,
                created_by=contact.created_by,
                updated_at=contact.updated_at,
                updated_by=contact.updated_by
            )
            for contact in model.contacts
        )

        addresses = tuple(
            CustomerAddress(
                customer_address_id=(
                    address.customer_address_id
                ),
                customer_id=(
                    address.customer_id
                ),
                address_type=(
                    CustomerAddressType(
                        address.address_type
                    )
                ),
                postal_code=address.postal_code,
                street=address.street,
                number=address.number,
                complement=address.complement,
                district=address.district,
                city=address.city,
                state=address.state,
                is_primary=address.is_primary,
                created_at=address.created_at,
                created_by=address.created_by,
                updated_at=address.updated_at,
                updated_by=address.updated_by
            )
            for address in model.addresses
        )

        operational_locations = tuple(
            CustomerOperationalLocation(
                operational_location_id=(
                    location.operational_location_id
                ),
                customer_id=(
                    location.customer_id
                ),
                name=location.name,
                postal_code=location.postal_code,
                street=location.street,
                number=location.number,
                complement=location.complement,
                district=location.district,
                city=location.city,
                state=location.state,
                observation=location.observation,
                is_active=location.is_active,
                created_at=location.created_at,
                created_by=location.created_by,
                updated_at=location.updated_at,
                updated_by=location.updated_by
            )
            for location
            in model.operational_locations
        )

        return Customer(
            customer_id=model.customer_id,
            customer_group_id=(
                model.customer_group_id
            ),
            person_type=CustomerPersonType(
                model.person_type
            ),
            document=model.document,
            legal_name=model.legal_name,
            trade_name=model.trade_name,
            state_registration=(
                model.state_registration
            ),
            status=CustomerStatus(
                model.status
            ),
            general_observation=(
                model.general_observation
            ),
            contacts=contacts,
            addresses=addresses,
            operational_locations=(
                operational_locations
            ),
            created_at=model.created_at,
            created_by=model.created_by,
            updated_at=model.updated_at,
            updated_by=model.updated_by
        )

    @staticmethod
    def _normalize_document(
        document: str
    ) -> str:

        return "".join(
            character
            for character in document
            if character.isdigit()
        )

    @staticmethod
    def _get_constraint_name(
        error: IntegrityError
    ) -> str | None:

        original_error = getattr(
            error,
            "orig",
            None
        )

        diagnostics = getattr(
            original_error,
            "diag",
            None
        )

        return getattr(
            diagnostics,
            "constraint_name",
            None
        )