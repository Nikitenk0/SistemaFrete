from dataclasses import dataclass
from datetime import date, datetime

from domain.models.driver_address import (
    DriverAddress,
    DriverAddressType,
)
from domain.models.driver_bank_account import (
    DriverBankAccount,
    DriverBankAccountType,
)
from domain.models.driver_contact import (
    DriverContact,
)


ACCOUNT_TYPE_OPTIONS = {
    "Conta corrente": DriverBankAccountType.CHECKING,
    "Conta poupança": DriverBankAccountType.SAVINGS,
    "Conta de pagamento": DriverBankAccountType.PAYMENT,
}


@dataclass(frozen=True)
class DriverRegistrationData:
    name: str
    cpf: str
    rg: str
    birth_date: date
    cnh_number: str
    cnh_category: str
    cnh_expiration_date: date
    contacts: tuple[DriverContact, ...]
    addresses: tuple[DriverAddress, ...]
    bank_accounts: tuple[DriverBankAccount, ...]


def parse_driver_registration(
    *,
    name: str,
    cpf: str,
    rg: str,
    birth_date_text: str,
    cnh_number: str,
    cnh_category: str,
    cnh_expiration_date_text: str,
    phone: str,
    email: str,
    postal_code: str,
    street: str,
    number: str,
    complement: str,
    district: str,
    city: str,
    state: str,
    bank_code: str,
    agency: str,
    account: str,
    account_digit: str,
    account_type_label: str,
) -> DriverRegistrationData:
    cleaned_name = _required(name, "Nome")
    cleaned_cpf = _required(cpf, "CPF")
    cleaned_rg = _required(rg, "RG")
    cleaned_cnh = _required(cnh_number, "CNH")
    cleaned_category = _required(cnh_category, "Categoria da CNH")

    birth_date = _parse_date(
        birth_date_text,
        "Data de nascimento",
    )
    cnh_expiration_date = _parse_date(
        cnh_expiration_date_text,
        "Validade da CNH",
    )

    try:
        account_type = ACCOUNT_TYPE_OPTIONS[account_type_label]
    except KeyError as error:
        raise ValueError("Tipo de conta bancária inválido") from error

    try:
        contact = DriverContact(
            phone=_required(phone, "Telefone"),
            email=_optional(email),
            is_primary=True,
        )
        address = DriverAddress(
            postal_code=_required(postal_code, "CEP"),
            street=_required(street, "Logradouro"),
            number=_required(number, "Número"),
            complement=_optional(complement),
            district=_required(district, "Bairro"),
            city=_required(city, "Cidade"),
            state=_required(state, "UF"),
            address_type=DriverAddressType.RESIDENTIAL,
            is_primary=True,
        )
        bank_account = DriverBankAccount(
            bank_code=_required(bank_code, "Código do banco"),
            agency=_required(agency, "Agência"),
            account=_required(account, "Conta"),
            account_digit=_optional(account_digit),
            account_type=account_type,
            is_primary=True,
        )
    except ValueError as error:
        raise ValueError(str(error)) from error

    return DriverRegistrationData(
        name=cleaned_name,
        cpf=cleaned_cpf,
        rg=cleaned_rg,
        birth_date=birth_date,
        cnh_number=cleaned_cnh,
        cnh_category=cleaned_category,
        cnh_expiration_date=cnh_expiration_date,
        contacts=(contact,),
        addresses=(address,),
        bank_accounts=(bank_account,),
    )


def _parse_date(value: str, field_name: str) -> date:
    text = _required(value, field_name)
    try:
        return datetime.strptime(text, "%d/%m/%Y").date()
    except ValueError as error:
        raise ValueError(
            f"{field_name} deve estar no formato DD/MM/AAAA"
        ) from error


def _required(value: str, field_name: str) -> str:
    text = str(value).strip()
    if not text:
        raise ValueError(f"{field_name} é obrigatório")
    return text


def _optional(value: str) -> str | None:
    text = str(value).strip()
    return text or None
