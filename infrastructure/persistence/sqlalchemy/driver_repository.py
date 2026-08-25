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
    DriverAlreadyExistsError,
    DriverPersistenceError
)
from application.ports.driver_repository import (
    DriverRepository
)
from domain.models.driver import (
    Driver,
    DriverStatus
)
from domain.models.driver_address import (
    DriverAddress,
    DriverAddressType
)
from domain.models.driver_bank_account import (
    DriverBankAccount,
    DriverBankAccountType,
    DriverPixKeyType
)
from domain.models.driver_contact import (
    DriverContact
)
from infrastructure.persistence.sqlalchemy.models import (
    DriverAddressModel,
    DriverBankAccountModel,
    DriverContactModel,
    DriverModel
)


class SqlAlchemyDriverRepository(
    DriverRepository
):

    def __init__(
        self,
        session: Session
    ):
        self._session = session

    def add(
        self,
        driver: Driver
    ) -> Driver:

        if driver.driver_id is not None:
            raise ValueError(
                "Motorista já possui driver_id"
            )

        model = self._to_model(
            driver
        )

        self._session.add(
            model
        )

        try:
            self._session.flush()

        except IntegrityError as error:

            constraint_name = self._get_constraint_name(
                error
            )

            if constraint_name == "uq_drivers_cpf":
                raise DriverAlreadyExistsError(
                    "CPF já cadastrado para outro motorista"
                ) from error

            raise DriverPersistenceError(
                "Não foi possível salvar o motorista"
            ) from error

        except SQLAlchemyError as error:
            raise DriverPersistenceError(
                "Não foi possível salvar o motorista"
            ) from error

        return self._to_domain(
            model
        )

    def get_by_id(
        self,
        driver_id: int
    ) -> Driver | None:

        try:
            model = self._session.scalar(
                select(
                    DriverModel
                )
                .options(
                    *self._load_options()
                )
                .where(
                    DriverModel.driver_id
                    == driver_id
                )
            )

        except SQLAlchemyError as error:
            raise DriverPersistenceError(
                "Não foi possível consultar o motorista"
            ) from error

        if model is None:
            return None

        return self._to_domain(
            model
        )

    def get_by_cpf(
        self,
        cpf: str
    ) -> Driver | None:

        normalized_cpf = self._normalize_cpf(
            cpf
        )

        try:
            model = self._session.scalar(
                select(
                    DriverModel
                )
                .options(
                    *self._load_options()
                )
                .where(
                    DriverModel.cpf
                    == normalized_cpf
                )
            )

        except SQLAlchemyError as error:
            raise DriverPersistenceError(
                "Não foi possível consultar o motorista"
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
    ) -> tuple[Driver, ...]:

        query = query.strip()

        if not query:
            return ()

        normalized_cpf = self._normalize_cpf(
            query
        )

        conditions = [
            DriverModel.name.ilike(
                f"%{query}%"
            ),
            DriverModel.rg.ilike(
                f"%{query}%"
            ),
            DriverModel.cnh_number.ilike(
                f"%{query}%"
            )
        ]

        if normalized_cpf:
            conditions.append(
                DriverModel.cpf.contains(
                    normalized_cpf
                )
            )

        try:
            models = self._session.scalars(
                select(
                    DriverModel
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
                    DriverModel.name,
                    DriverModel.driver_id
                )
                .limit(
                    limit
                )
            ).all()

        except SQLAlchemyError as error:
            raise DriverPersistenceError(
                "Não foi possível pesquisar motoristas"
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
                DriverModel.contacts
            ),
            selectinload(
                DriverModel.addresses
            ),
            selectinload(
                DriverModel.bank_accounts
            )
        )

    @classmethod
    def _to_model(
        cls,
        driver: Driver
    ) -> DriverModel:

        model = DriverModel(
            name=driver.name,
            cpf=driver.cpf,
            rg=driver.rg,
            birth_date=driver.birth_date,
            cnh_number=driver.cnh_number,
            cnh_category=driver.cnh_category,
            cnh_expiration_date=(
                driver.cnh_expiration_date
            ),
            status=driver.status.value,
            created_by=driver.created_by,
            updated_by=driver.updated_by
        )

        if driver.created_at is not None:
            model.created_at = driver.created_at

        if driver.updated_at is not None:
            model.updated_at = driver.updated_at

        model.contacts = [
            cls._to_contact_model(
                contact
            )
            for contact in driver.contacts
        ]

        model.addresses = [
            cls._to_address_model(
                address
            )
            for address in driver.addresses
        ]

        model.bank_accounts = [
            cls._to_bank_account_model(
                bank_account
            )
            for bank_account in driver.bank_accounts
        ]

        return model

    @staticmethod
    def _to_contact_model(
        contact: DriverContact
    ) -> DriverContactModel:

        model = DriverContactModel(
            phone=contact.phone,
            secondary_phone=contact.secondary_phone,
            email=contact.email,
            is_primary=contact.is_primary,
            created_by=contact.created_by,
            updated_by=contact.updated_by
        )

        if contact.created_at is not None:
            model.created_at = contact.created_at

        if contact.updated_at is not None:
            model.updated_at = contact.updated_at

        return model

    @staticmethod
    def _to_address_model(
        address: DriverAddress
    ) -> DriverAddressModel:

        model = DriverAddressModel(
            address_type=address.address_type.value,
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
            model.created_at = address.created_at

        if address.updated_at is not None:
            model.updated_at = address.updated_at

        return model

    @staticmethod
    def _to_bank_account_model(
        bank_account: DriverBankAccount
    ) -> DriverBankAccountModel:

        model = DriverBankAccountModel(
            bank_code=bank_account.bank_code,
            agency=bank_account.agency,
            account=bank_account.account,
            account_digit=bank_account.account_digit,
            account_type=bank_account.account_type.value,
            pix_key_type=(
                bank_account.pix_key_type.value
                if bank_account.pix_key_type is not None
                else None
            ),
            pix_key=bank_account.pix_key,
            is_primary=bank_account.is_primary,
            created_by=bank_account.created_by,
            updated_by=bank_account.updated_by
        )

        if bank_account.created_at is not None:
            model.created_at = bank_account.created_at

        if bank_account.updated_at is not None:
            model.updated_at = bank_account.updated_at

        return model

    @staticmethod
    def _to_domain(
        model: DriverModel
    ) -> Driver:

        contacts = tuple(
            DriverContact(
                driver_contact_id=(
                    contact.driver_contact_id
                ),
                driver_id=contact.driver_id,
                phone=contact.phone,
                secondary_phone=contact.secondary_phone,
                email=contact.email,
                is_primary=contact.is_primary,
                created_at=contact.created_at,
                created_by=contact.created_by,
                updated_at=contact.updated_at,
                updated_by=contact.updated_by
            )
            for contact in model.contacts
        )

        addresses = tuple(
            DriverAddress(
                driver_address_id=(
                    address.driver_address_id
                ),
                driver_id=address.driver_id,
                address_type=DriverAddressType(
                    address.address_type
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

        bank_accounts = tuple(
            DriverBankAccount(
                driver_bank_account_id=(
                    bank_account.driver_bank_account_id
                ),
                driver_id=bank_account.driver_id,
                bank_code=bank_account.bank_code,
                agency=bank_account.agency,
                account=bank_account.account,
                account_digit=bank_account.account_digit,
                account_type=DriverBankAccountType(
                    bank_account.account_type
                ),
                pix_key_type=(
                    DriverPixKeyType(
                        bank_account.pix_key_type
                    )
                    if bank_account.pix_key_type is not None
                    else None
                ),
                pix_key=bank_account.pix_key,
                is_primary=bank_account.is_primary,
                created_at=bank_account.created_at,
                created_by=bank_account.created_by,
                updated_at=bank_account.updated_at,
                updated_by=bank_account.updated_by
            )
            for bank_account in model.bank_accounts
        )

        return Driver(
            driver_id=model.driver_id,
            name=model.name,
            cpf=model.cpf,
            rg=model.rg,
            birth_date=model.birth_date,
            cnh_number=model.cnh_number,
            cnh_category=model.cnh_category,
            cnh_expiration_date=(
                model.cnh_expiration_date
            ),
            status=DriverStatus(
                model.status
            ),
            contacts=contacts,
            addresses=addresses,
            bank_accounts=bank_accounts,
            created_at=model.created_at,
            created_by=model.created_by,
            updated_at=model.updated_at,
            updated_by=model.updated_by
        )

    @staticmethod
    def _normalize_cpf(
        cpf: str
    ) -> str:

        return "".join(
            character
            for character in cpf
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
