from dataclasses import dataclass


@dataclass(frozen=True)
class FreightDriverSelectionItem:
    driver_id: int
    name: str
    cpf: str
    cnh_number: str
    cnh_category: str
