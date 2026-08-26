from dataclasses import dataclass

import customtkinter as ctk

from domain.models.vehicle import Vehicle, VehicleStatus, VehicleType
from presentation.desktop.vehicle_catalog_formatting import (
    VEHICLE_TYPE_LABELS,
    vehicle_type_label,
)


@dataclass(frozen=True)
class VehicleFormData:
    plate: str
    vehicle_type: VehicleType
    status: VehicleStatus


class VehicleForm:

    def __init__(
        self,
        parent,
        include_status: bool,
    ):
        self._include_status = include_status
        self.frame = ctk.CTkFrame(parent)
        self.frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            self.frame,
            text="Dados do veículo",
            font=("Arial", 18, "bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            padx=18,
            pady=(16, 14),
        )

        ctk.CTkLabel(self.frame, text="Placa").grid(
            row=1,
            column=0,
            sticky="w",
            padx=(18, 10),
            pady=8,
        )
        self.plate_entry = ctk.CTkEntry(
            self.frame,
            placeholder_text="Ex.: ABC1D23",
        )
        self.plate_entry.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=(0, 18),
            pady=8,
        )

        ctk.CTkLabel(self.frame, text="Tipo").grid(
            row=2,
            column=0,
            sticky="w",
            padx=(18, 10),
            pady=8,
        )
        type_values = list(VEHICLE_TYPE_LABELS.values())
        self.type_combo = ctk.CTkComboBox(
            self.frame,
            values=type_values,
            state="readonly",
        )
        self.type_combo.grid(
            row=2,
            column=1,
            sticky="ew",
            padx=(0, 18),
            pady=8,
        )
        self.type_combo.set(type_values[0])

        self.status_combo = None
        if include_status:
            ctk.CTkLabel(self.frame, text="Status").grid(
                row=3,
                column=0,
                sticky="w",
                padx=(18, 10),
                pady=8,
            )
            self.status_combo = ctk.CTkComboBox(
                self.frame,
                values=["Ativo", "Inativo"],
                state="readonly",
            )
            self.status_combo.grid(
                row=3,
                column=1,
                sticky="ew",
                padx=(0, 18),
                pady=(8, 16),
            )
            self.status_combo.set("Ativo")

    def parse(self) -> VehicleFormData:
        plate = self.plate_entry.get().strip()
        if not plate:
            raise ValueError("Placa é obrigatória")

        label = self.type_combo.get()
        try:
            vehicle_type = next(
                vehicle_type
                for vehicle_type, current_label
                in VEHICLE_TYPE_LABELS.items()
                if current_label == label
            )
        except StopIteration as error:
            raise ValueError("Tipo de veículo inválido") from error

        status = VehicleStatus.ACTIVE
        if self._include_status:
            status_value = self.status_combo.get()
            try:
                status = {
                    "Ativo": VehicleStatus.ACTIVE,
                    "Inativo": VehicleStatus.INACTIVE,
                }[status_value]
            except KeyError as error:
                raise ValueError("Status de veículo inválido") from error

        try:
            normalized = Vehicle(
                plate=plate,
                vehicle_type=vehicle_type,
                status=status,
            )
        except ValueError as error:
            raise ValueError(str(error)) from error

        return VehicleFormData(
            plate=normalized.plate,
            vehicle_type=normalized.vehicle_type,
            status=normalized.status,
        )

    def populate(self, vehicle: Vehicle) -> None:
        self.plate_entry.delete(0, "end")
        self.plate_entry.insert(0, vehicle.plate)
        self.type_combo.set(vehicle_type_label(vehicle.vehicle_type))
        if self.status_combo is not None:
            self.status_combo.set(
                "Ativo"
                if vehicle.status == VehicleStatus.ACTIVE
                else "Inativo"
            )

    def focus_plate(self) -> None:
        self.plate_entry.focus_set()
