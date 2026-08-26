import customtkinter as ctk

from domain.models.driver import Driver, DriverStatus
from presentation.desktop.driver_registration_inputs import (
    ACCOUNT_TYPE_OPTIONS,
    DriverRegistrationData,
    parse_driver_registration,
)


DRIVER_FORM_STATUS_OPTIONS = {
    "Ativo": DriverStatus.ACTIVE,
    "Inativo": DriverStatus.INACTIVE,
}


class DriverForm:

    def __init__(
        self,
        parent,
        *,
        include_status: bool,
    ):
        self._entries: dict[str, ctk.CTkEntry] = {}
        self._include_status = include_status

        self.frame = ctk.CTkScrollableFrame(parent)
        self.frame.grid_columnconfigure((0, 1), weight=1)

        row = 0
        row = self._add_section(row, "Dados pessoais")
        self._add_field(row, 0, "Nome", "name")
        self._add_field(row, 1, "CPF", "cpf")
        row += 2
        self._add_field(row, 0, "RG", "rg")
        self._add_field(
            row,
            1,
            "Nascimento",
            "birth_date",
            placeholder="DD/MM/AAAA",
        )
        row += 2

        row = self._add_section(row, "CNH")
        self._add_field(row, 0, "Número da CNH", "cnh_number")
        self._add_field(row, 1, "Categoria", "cnh_category")
        row += 2
        self._add_field(
            row,
            0,
            "Validade da CNH",
            "cnh_expiration_date",
            placeholder="DD/MM/AAAA",
        )

        if include_status:
            ctk.CTkLabel(
                self.frame,
                text="Status",
            ).grid(
                row=row,
                column=1,
                sticky="w",
                padx=6,
                pady=(4, 2),
            )
            self.status_combo = ctk.CTkComboBox(
                self.frame,
                values=list(DRIVER_FORM_STATUS_OPTIONS),
                state="readonly",
            )
            self.status_combo.grid(
                row=row + 1,
                column=1,
                sticky="ew",
                padx=6,
                pady=(0, 8),
            )
            self.status_combo.set("Ativo")
        else:
            self.status_combo = None
        row += 2

        row = self._add_section(row, "Contato principal")
        self._add_field(row, 0, "Telefone", "phone")
        self._add_field(row, 1, "E-mail (opcional)", "email")
        row += 2

        row = self._add_section(row, "Endereço principal")
        self._add_field(row, 0, "CEP", "postal_code")
        self._add_field(row, 1, "UF", "state")
        row += 2
        self._add_field(row, 0, "Logradouro", "street")
        self._add_field(row, 1, "Número", "number")
        row += 2
        self._add_field(row, 0, "Bairro", "district")
        self._add_field(row, 1, "Cidade", "city")
        row += 2
        self._add_field(
            row,
            0,
            "Complemento (opcional)",
            "complement",
        )
        row += 2

        row = self._add_section(row, "Conta bancária principal")
        self._add_field(row, 0, "Código do banco", "bank_code")
        self._add_field(row, 1, "Agência", "agency")
        row += 2
        self._add_field(row, 0, "Conta", "account")
        self._add_field(
            row,
            1,
            "Dígito (opcional)",
            "account_digit",
        )
        row += 2

        ctk.CTkLabel(
            self.frame,
            text="Tipo de conta",
        ).grid(
            row=row,
            column=0,
            sticky="w",
            padx=6,
            pady=(4, 2),
        )
        self.account_type_combo = ctk.CTkComboBox(
            self.frame,
            values=list(ACCOUNT_TYPE_OPTIONS),
            state="readonly",
        )
        self.account_type_combo.grid(
            row=row + 1,
            column=0,
            sticky="ew",
            padx=6,
            pady=(0, 8),
        )
        self.account_type_combo.set("Conta corrente")

    def _add_section(self, row: int, text: str) -> int:
        ctk.CTkLabel(
            self.frame,
            text=text,
            font=("Arial", 14, "bold"),
        ).grid(
            row=row,
            column=0,
            columnspan=2,
            sticky="w",
            padx=6,
            pady=(12, 5),
        )
        return row + 1

    def _add_field(
        self,
        row: int,
        column: int,
        label: str,
        key: str,
        placeholder: str | None = None,
    ) -> None:
        ctk.CTkLabel(
            self.frame,
            text=label,
        ).grid(
            row=row,
            column=column,
            sticky="w",
            padx=6,
            pady=(4, 2),
        )
        entry = ctk.CTkEntry(
            self.frame,
            placeholder_text=placeholder or "",
        )
        entry.grid(
            row=row + 1,
            column=column,
            sticky="ew",
            padx=6,
            pady=(0, 7),
        )
        self._entries[key] = entry

    def parse(self) -> DriverRegistrationData:
        return parse_driver_registration(
            name=self._value("name"),
            cpf=self._value("cpf"),
            rg=self._value("rg"),
            birth_date_text=self._value("birth_date"),
            cnh_number=self._value("cnh_number"),
            cnh_category=self._value("cnh_category"),
            cnh_expiration_date_text=self._value(
                "cnh_expiration_date"
            ),
            phone=self._value("phone"),
            email=self._value("email"),
            postal_code=self._value("postal_code"),
            street=self._value("street"),
            number=self._value("number"),
            complement=self._value("complement"),
            district=self._value("district"),
            city=self._value("city"),
            state=self._value("state"),
            bank_code=self._value("bank_code"),
            agency=self._value("agency"),
            account=self._value("account"),
            account_digit=self._value("account_digit"),
            account_type_label=self.account_type_combo.get(),
        )

    def status(self) -> DriverStatus:
        if self.status_combo is None:
            return DriverStatus.ACTIVE
        try:
            return DRIVER_FORM_STATUS_OPTIONS[
                self.status_combo.get()
            ]
        except KeyError as error:
            raise ValueError("Status do motorista inválido") from error

    def populate(self, driver: Driver) -> None:
        primary_contact = self._single_primary(
            driver.contacts,
            "contato",
        )
        primary_address = self._single_primary(
            driver.addresses,
            "endereço",
        )
        primary_bank = self._single_primary(
            driver.bank_accounts,
            "conta bancária",
        )

        values = {
            "name": driver.name,
            "cpf": driver.cpf,
            "rg": driver.rg,
            "birth_date": driver.birth_date.strftime("%d/%m/%Y"),
            "cnh_number": driver.cnh_number,
            "cnh_category": driver.cnh_category,
            "cnh_expiration_date": (
                driver.cnh_expiration_date.strftime("%d/%m/%Y")
            ),
            "phone": primary_contact.phone,
            "email": primary_contact.email or "",
            "postal_code": primary_address.postal_code,
            "street": primary_address.street,
            "number": primary_address.number,
            "complement": primary_address.complement or "",
            "district": primary_address.district,
            "city": primary_address.city,
            "state": primary_address.state,
            "bank_code": primary_bank.bank_code,
            "agency": primary_bank.agency,
            "account": primary_bank.account,
            "account_digit": primary_bank.account_digit or "",
        }

        for key, value in values.items():
            entry = self._entries[key]
            entry.delete(0, "end")
            entry.insert(0, str(value))

        account_label = next(
            label
            for label, account_type in ACCOUNT_TYPE_OPTIONS.items()
            if account_type == primary_bank.account_type
        )
        self.account_type_combo.set(account_label)

        if self.status_combo is not None:
            status_label = next(
                label
                for label, status in DRIVER_FORM_STATUS_OPTIONS.items()
                if status == driver.status
            )
            self.status_combo.set(status_label)

    def prefill_identity(
        self,
        *,
        name: str = "",
        cpf: str = "",
        lock_cpf: bool = False,
    ) -> None:
        name_entry = self._entries["name"]
        cpf_entry = self._entries["cpf"]

        name_entry.delete(0, "end")
        name_entry.insert(0, name)

        cpf_entry.configure(state="normal")
        cpf_entry.delete(0, "end")
        cpf_entry.insert(0, cpf)

        if lock_cpf:
            cpf_entry.configure(state="disabled")

    def focus_name(self) -> None:
        self._entries["name"].focus_set()

    def _value(self, key: str) -> str:
        return self._entries[key].get()

    @staticmethod
    def _single_primary(items: tuple, label: str):
        primary_items = tuple(item for item in items if item.is_primary)
        if len(primary_items) != 1:
            raise ValueError(
                f"Motorista precisa possuir exatamente um {label} principal"
            )
        return primary_items[0]
