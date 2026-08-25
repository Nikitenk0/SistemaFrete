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
            self._raise_integrity_error(
                error,
                "Não foi possível salvar o motorista"
            )

        except SQLAlchemyError as error:
            raise DriverPersistenceError(
                "Não foi possível salvar o motorista"
            ) from error

        return self._to_domain(
            model
        )

    def save(
        self,
        driver: Driver
    ) -> Driver:

        if driver.driver_id is None:
            raise ValueError(
                "Motorista precisa possuir driver_id"
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
                    DriverModel.driver_id
                    == driver.driver_id
                )
            )

            if model is None:
                raise DriverPersistenceError(
                    "Motorista não encontrado para atualização"
                )

            model.name = driver.name
            model.cpf = driver.cpf
            model.rg = driver.rg
            model.birth_date = driver.birth_date
            model.cnh_number = driver.cnh_number
            model.cnh_category = driver.cnh_category
            model.cnh_expiration_date = (
                driver.cnh_expiration_date
            )
            model.status = driver.status.value
            model.updated_at = driver.updated_at
            model.updated_by = driver.updated_by

            self._clear_primary_flags(
                model
            )
            self._session.flush()

            self._sync_contacts(
                model,
                driver.contacts
            )
            self._sync_addresses(
                model,
                driver.addresses
            )
            self._sync_bank_accounts(
                model,
                driver.bank_accounts
            )

            self._session.flush()

        except IntegrityError as error:
            self._raise_integrity_error(
                error,
                "Não foi possível atualizar o motorista"
            )

        except DriverPersistenceError:
            raise

        except SQLAlchemyError as error:
            raise DriverPersistenceError(
                "Não foi possível atualizar o motorista"
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

    def get_by_id_for_update(
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
                .with_for_update()
            )

        except SQLAlchemyError as error:
            raise DriverPersistenceError(
                "Não foi possível bloquear o motorista para atualização"
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

    @staticmethod
    def _clear_primary_flags(
        model: DriverModel
    ) -> None:

        for contact in model.contacts:
            contact.is_primary = False

        for address in model.addresses:
            address.is_primary = False

        for bank_account in model.bank_accounts:
            bank_account.is_primary = False

    def _sync_contacts(
        self,
        model: DriverModel,
        contacts: tuple[DriverContact, ...]
    ) -> None:

        existing = {
            item.driver_contact_id: item
            for item in model.contacts
        }
        synchronized: list[DriverContactModel] = []

        for contact in contacts:
            if contact.driver_contact_id is None:
                child = self._to_contact_model(
                    contact
                )
            else:
                child = existing.get(
                    contact.driver_contact_id
                )
                if child is None:
                    raise DriverPersistenceError(
                        "Contato não pertence ao motorista"
                    )
                self._apply_contact(
                    child,
                    contact
                )

            synchronized.append(
                child
            )

        model.contacts = synchronized

    def _sync_addresses(
        self,
        model: DriverModel,
        addresses: tuple[DriverAddress, ...]
    ) -> None:

        existing = {
            item.driver_address_id: item
            for item in model.addresses
        }
        synchronized: list[DriverAddressModel] = []

        for address in addresses:
            if address.driver_address_id is None:
                child = self._to_address_model(
                    address
                )
            else:
                child = existing.get(
                    address.driver_address_id
                )
                if child is None:
                    raise DriverPersistenceError(
                        "Endereço não pertence ao motorista"
                    )
                self._apply_address(
                    child,
                    address
                )

            synchronized.append(
                child
            )

        model.addresses = synchronized

    def _sync_bank_accounts(
        self,
        model: DriverModel,
        bank_accounts: tuple[DriverBankAccount, ...]
    ) -> None:

        existing = {
            item.driver_bank_account_id: item
            for item in model.bank_accounts
        }
        synchronized: list[DriverBankAccountModel] = []

        for bank_account in bank_accounts:
            if bank_account.driver_bank_account_id is None:
                child = self._to_bank_account_model(
                    bank_account
                )
            else:
                child = existing.get(
                    bank_account.driver_bank_account_id
                )
                if child is None:
                    raise DriverPersistenceError(
                        "Conta bancária não pertence ao motorista"
                    )
                self._apply_bank_account(
                    child,
                    bank_account
                )

            synchronized.append(
                child
            )

        model.bank_accounts = synchronized

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
    def _apply_contact(
        model: DriverContactModel,
        contact: DriverContact
    ) -> None:

        model.phone = contact.phone
        model.secondary_phone = contact.secondary_phone
        model.email = contact.email
        model.is_primary = contact.is_primary
        model.updated_at = contact.updated_at
        model.updated_by = contact.updated_by

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
    def _apply_address(
        model: DriverAddressModel,
        address: DriverAddress
    ) -> None:

        model.address_type = address.address_type.value
        model.postal_code = address.postal_code
        model.street = address.street
        model.number = address.number
        model.complement = address.complement
        model.district = address.district
        model.city = address.city
        model.state = address.state
        model.is_primary = address.is_primary
        model.updated_at = address.updated_at
        model.updated_by = address.updated_by

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
    def _apply_bank_account(
        model: DriverBankAccountModel,
        bank_account: DriverBankAccount
    ) -> None:

        model.bank_code = bank_account.bank_code
        model.agency = bank_account.agency
        model.account = bank_account.account
        model.account_digit = bank_account.account_digit
        model.account_type = bank_account.account_type.value
        model.pix_key_type = (
            bank_account.pix_key_type.value
            if bank_account.pix_key_type is not None
            else None
        )
        model.pix_key = bank_account.pix_key
        model.is_primary = bank_account.is_primary
        model.updated_at = bank_account.updated_at
        model.updated_by = bank_account.updated_by

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

    @classmethod
    def _raise_integrity_error(
        cls,
        error: IntegrityError,
        fallback_message: str
    ) -> None:

        constraint_name = cls._get_constraint_name(
            error
        )

        if constraint_name in {
            "uq_drivers_cpf",
            "drivers_cpf_key"
        }:
            raise DriverAlreadyExistsError(
                "CPF já cadastrado para outro motorista"
            ) from error

        raise DriverPersistenceError(
            fallback_message
        ) from error

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
