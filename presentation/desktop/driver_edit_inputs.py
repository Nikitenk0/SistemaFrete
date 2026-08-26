from dataclasses import dataclass, replace

from domain.models.driver import Driver, DriverStatus
from domain.models.driver_address import DriverAddress
from domain.models.driver_bank_account import DriverBankAccount
from domain.models.driver_contact import DriverContact
from presentation.desktop.driver_registration_inputs import (
    DriverRegistrationData,
)


@dataclass(frozen=True)
class DriverUpdateFormData:
    driver_id: int
    name: str
    cpf: str
    rg: str
    birth_date: object
    cnh_number: str
    cnh_category: str
    cnh_expiration_date: object
    contacts: tuple[DriverContact, ...]
    addresses: tuple[DriverAddress, ...]
    bank_accounts: tuple[DriverBankAccount, ...]
    status: DriverStatus


def build_driver_update_form_data(
    driver: Driver,
    registration: DriverRegistrationData,
    status: DriverStatus,
) -> DriverUpdateFormData:
    if driver.driver_id is None or driver.driver_id < 1:
        raise ValueError("Motorista precisa estar persistido para edição")

    normalized_status = DriverStatus(status)

    primary_contact = _single_primary(
        driver.contacts,
        "contato",
    )
    primary_address = _single_primary(
        driver.addresses,
        "endereço",
    )
    primary_bank_account = _single_primary(
        driver.bank_accounts,
        "conta bancária",
    )

    form_contact = registration.contacts[0]
    form_address = registration.addresses[0]
    form_bank_account = registration.bank_accounts[0]

    updated_primary_contact = replace(
        primary_contact,
        phone=form_contact.phone,
        email=form_contact.email,
        is_primary=True,
    )
    updated_primary_address = replace(
        primary_address,
        postal_code=form_address.postal_code,
        street=form_address.street,
        number=form_address.number,
        complement=form_address.complement,
        district=form_address.district,
        city=form_address.city,
        state=form_address.state,
        is_primary=True,
    )
    updated_primary_bank_account = replace(
        primary_bank_account,
        bank_code=form_bank_account.bank_code,
        agency=form_bank_account.agency,
        account=form_bank_account.account,
        account_digit=form_bank_account.account_digit,
        account_type=form_bank_account.account_type,
        is_primary=True,
    )

    contacts = _replace_primary(
        driver.contacts,
        updated_primary_contact,
    )
    addresses = _replace_primary(
        driver.addresses,
        updated_primary_address,
    )
    bank_accounts = _replace_primary(
        driver.bank_accounts,
        updated_primary_bank_account,
    )

    return DriverUpdateFormData(
        driver_id=driver.driver_id,
        name=registration.name,
        cpf=registration.cpf,
        rg=registration.rg,
        birth_date=registration.birth_date,
        cnh_number=registration.cnh_number,
        cnh_category=registration.cnh_category,
        cnh_expiration_date=registration.cnh_expiration_date,
        contacts=contacts,
        addresses=addresses,
        bank_accounts=bank_accounts,
        status=normalized_status,
    )


def _single_primary(items: tuple, label: str):
    primary_items = tuple(
        item for item in items if item.is_primary
    )
    if len(primary_items) != 1:
        raise ValueError(
            f"Motorista precisa possuir exatamente um {label} principal"
        )
    return primary_items[0]


def _replace_primary(items: tuple, updated_primary):
    return tuple(
        updated_primary if item.is_primary else item
        for item in items
    )
