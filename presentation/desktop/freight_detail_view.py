from tkinter import messagebox

import customtkinter as ctk

from application.dtos.freight_query import (
    FreightDetails,
    FreightDriverAssignmentDetails,
    FreightExpenseDetails,
    FreightTransportUnitDetails,
)
from domain.models.freight import (
    FreightStatus,
)
from presentation.desktop.async_task_runner import (
    TkAsyncTaskRunner,
)
from presentation.desktop.freight_detail_formatting import (
    event_label,
    expense_label,
    format_currency,
    format_datetime,
    format_margin,
    optional_text,
    status_label,
    vehicle_label,
    yes_no,
)
from presentation.desktop.freight_operational_inputs import (
    can_start_freight,
    is_pending_setup_available,
    start_readiness_message,
    unit_has_active_driver,
)
from presentation.desktop.freight_operational_context_rules import (
    active_operational_context,
    can_adopt_current_operational_context,
    can_finish_current_operational_context,
    can_replace_current_operational_context,
)
from presentation.desktop.freight_completion_inputs import (
    can_complete_freight,
    completion_readiness_message,
    is_freight_completion_phase,
)
from presentation.desktop.freight_driver_dialog import (
    FreightDriverDialog,
)
from presentation.desktop.freight_finish_driver_dialog import (
    FreightFinishDriverDialog,
)
from presentation.desktop.freight_finish_operational_assignment_dialog import (
    FreightFinishOperationalAssignmentDialog,
)
from presentation.desktop.freight_operational_assignment_replace_dialog import (
    FreightOperationalAssignmentReplaceDialog,
)
from presentation.desktop.freight_vehicle_dialog import (
    FreightVehicleDialog,
)


class FreightDetailView:

    _TAB_NAMES = (
        "Geral",
        "Unidades",
        "Despesas",
        "Histórico",
        "Financeiro",
    )

    def __init__(
        self,
        parent,
        freight_id: int,
        get_freight_details_callback,
        add_transport_unit_callback,
        remove_transport_unit_callback,
        add_vehicle_callback,
        remove_vehicle_callback,
        replace_vehicle_callback,
        search_available_vehicles_callback,
        search_available_drivers_callback,
        search_transport_providers_callback,
        get_transport_provider_details_callback,
        assign_driver_callback,
        replace_driver_callback,
        finish_driver_callback,
        adopt_current_operational_assignment_callback,
        replace_in_progress_operational_assignment_callback,
        start_freight_callback,
        complete_freight_callback,
        navigate_back,
    ):
        self.parent = parent
        self.freight_id = freight_id
        self._get_freight_details_callback = (
            get_freight_details_callback
        )
        self._add_transport_unit_callback = (
            add_transport_unit_callback
        )
        self._remove_transport_unit_callback = (
            remove_transport_unit_callback
        )
        self._add_vehicle_callback = add_vehicle_callback
        self._remove_vehicle_callback = remove_vehicle_callback
        self._replace_vehicle_callback = replace_vehicle_callback
        self._search_available_vehicles_callback = (
            search_available_vehicles_callback
        )
        self._search_available_drivers_callback = (
            search_available_drivers_callback
        )
        self._search_transport_providers_callback = (
            search_transport_providers_callback
        )
        self._get_transport_provider_details_callback = (
            get_transport_provider_details_callback
        )
        self._assign_driver_callback = assign_driver_callback
        self._replace_driver_callback = replace_driver_callback
        self._finish_driver_callback = finish_driver_callback
        self._adopt_current_operational_assignment_callback = (
            adopt_current_operational_assignment_callback
        )
        self._replace_in_progress_operational_assignment_callback = (
            replace_in_progress_operational_assignment_callback
        )
        self._start_freight_callback = start_freight_callback
        self._complete_freight_callback = complete_freight_callback
        self._navigate_back = navigate_back
        self._is_loading = False
        self._is_operation_running = False
        self._operation_buttons = []
        self._current_details: FreightDetails | None = None
        self._task_runner = TkAsyncTaskRunner(
            scheduler=parent
        )

        self._build()
        self.load()

    def _build(self) -> None:
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(
            self.parent,
            fg_color="transparent",
        )
        self.main_frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=24,
            pady=18,
        )
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(3, weight=1)

        header = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent",
        )
        header.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 8),
        )
        header.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            header,
            text=f"FRETE #{self.freight_id}",
            font=("Arial", 22, "bold"),
        )
        self.title_label.grid(
            row=0,
            column=0,
            sticky="w",
        )

        self.status_label = ctk.CTkLabel(
            header,
            text="",
            font=("Arial", 12, "bold"),
        )
        self.status_label.grid(
            row=1,
            column=0,
            sticky="w",
            pady=(3, 0),
        )

        self.refresh_button = ctk.CTkButton(
            header,
            text="Atualizar",
            width=100,
            command=self.load,
        )
        self.refresh_button.grid(
            row=0,
            column=1,
            rowspan=2,
            padx=(8, 8),
        )

        ctk.CTkButton(
            header,
            text="← Fretes",
            width=100,
            command=self._navigate_back,
        ).grid(
            row=0,
            column=2,
            rowspan=2,
        )

        self.loading_label = ctk.CTkLabel(
            self.main_frame,
            text="",
        )
        self.loading_label.grid(
            row=1,
            column=0,
            sticky="w",
            pady=(0, 6),
        )

        self.operation_frame = ctk.CTkFrame(
            self.main_frame,
        )
        self.operation_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            pady=(0, 8),
        )
        self.operation_frame.grid_columnconfigure(
            0,
            weight=1,
        )

        ctk.CTkLabel(
            self.operation_frame,
            text="Preparação operacional",
            font=("Arial", 12, "bold"),
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=10,
            pady=8,
        )

        self.add_unit_button = ctk.CTkButton(
            self.operation_frame,
            text="Adicionar unidade",
            width=130,
            command=self._add_transport_unit,
        )
        self.add_unit_button.grid(
            row=0,
            column=1,
            padx=(10, 6),
            pady=8,
        )

        self.start_freight_button = ctk.CTkButton(
            self.operation_frame,
            text="Iniciar frete",
            width=120,
            state="disabled",
            command=self._start_freight,
        )
        self.start_freight_button.grid(
            row=0,
            column=2,
            padx=(6, 10),
            pady=8,
        )

        self.complete_freight_button = ctk.CTkButton(
            self.operation_frame,
            text="Concluir frete",
            width=120,
            state="disabled",
            command=self._complete_freight,
        )
        self.complete_freight_button.grid(
            row=0,
            column=2,
            padx=(6, 10),
            pady=8,
        )
        self.complete_freight_button.grid_remove()

        self.readiness_label = ctk.CTkLabel(
            self.operation_frame,
            text="",
            anchor="w",
        )
        self.readiness_label.grid(
            row=1,
            column=0,
            columnspan=3,
            sticky="ew",
            padx=10,
            pady=(0, 8),
        )

        self.tabs = ctk.CTkTabview(
            self.main_frame,
        )
        self.tabs.grid(
            row=3,
            column=0,
            sticky="nsew",
        )

        self._tab_frames = {}
        for tab_name in self._TAB_NAMES:
            tab = self.tabs.add(tab_name)
            tab.grid_rowconfigure(0, weight=1)
            tab.grid_columnconfigure(0, weight=1)

            scroll = ctk.CTkScrollableFrame(
                tab,
                fg_color="transparent",
            )
            scroll.grid(
                row=0,
                column=0,
                sticky="nsew",
                padx=4,
                pady=4,
            )
            scroll.grid_columnconfigure(0, weight=1)
            self._tab_frames[tab_name] = scroll

    def load(self) -> None:
        if self._is_loading:
            return

        self._set_loading(True)
        self._task_runner.run(
            task=lambda: self._get_freight_details_callback(
                self.freight_id
            ),
            on_success=self._on_load_success,
            on_error=self._on_load_error,
        )

    def _on_load_success(
        self,
        details: FreightDetails,
    ) -> None:
        if not self._view_exists():
            return

        self._current_details = details
        self._render(details)
        self._set_loading(False)

    def _on_load_error(
        self,
        error: Exception,
    ) -> None:
        if not self._view_exists():
            return

        self._set_loading(False)
        messagebox.showerror(
            "Erro",
            "Não foi possível consultar o frete.\n\n"
            f"{error}",
        )

    def _render(
        self,
        details: FreightDetails,
    ) -> None:
        self.status_label.configure(
            text=(
                f"{status_label(details.current_status)}  •  "
                f"Financeiro: "
                f"{'Fechado' if details.financially_closed else 'Aberto'}"
            )
        )

        pending_phase = is_pending_setup_available(
            details.current_status
        )
        completion_phase = is_freight_completion_phase(
            details.current_status
        )

        if pending_phase or completion_phase:
            self.operation_frame.grid()
        else:
            self.operation_frame.grid_remove()

        if pending_phase:
            self.add_unit_button.grid()
            self.start_freight_button.grid()
            self.complete_freight_button.grid_remove()
            self.readiness_label.configure(
                text=start_readiness_message(details)
            )
        elif completion_phase:
            self.add_unit_button.grid_remove()
            self.start_freight_button.grid_remove()
            self.complete_freight_button.grid()
            self.readiness_label.configure(
                text=completion_readiness_message(details)
            )
        else:
            self.add_unit_button.grid_remove()
            self.start_freight_button.grid_remove()
            self.complete_freight_button.grid_remove()
            self.readiness_label.configure(
                text=""
            )

        self._operation_buttons = [
            self.add_unit_button,
            self.start_freight_button,
            self.complete_freight_button,
        ]

        for frame in self._tab_frames.values():
            for widget in frame.winfo_children():
                widget.destroy()

        self._render_general(details)
        self._render_units(details)
        self._render_expenses(details)
        self._render_history(details)
        self._render_financial(details)
        self._apply_operation_button_states()

    def _render_general(
        self,
        details: FreightDetails,
    ) -> None:
        frame = self._tab_frames["Geral"]
        customer_name = (
            details.customer_trade_name
            or details.customer_legal_name
            or "--"
        )

        rows = (
            ("Cliente", customer_name),
            ("Cliente ID", str(details.customer_id)),
            ("Orçamento principal", details.primary_quote_number),
            ("Origem", details.origin),
            ("Destino", details.destination),
            ("Status", status_label(details.current_status)),
            ("Receita contratada", format_currency(details.contracted_revenue)),
            (
                "Complementares aprovados",
                str(details.approved_complementary_quote_count),
            ),
            ("Fechado financeiramente", yes_no(details.financially_closed)),
            ("Criado em", format_datetime(details.created_at)),
            ("Iniciado em", format_datetime(details.started_at)),
            ("Concluído em", format_datetime(details.completed_at)),
            ("Cancelado em", format_datetime(details.cancelled_at)),
        )

        self._render_key_value_rows(frame, rows)

    def _render_units(
        self,
        details: FreightDetails,
    ) -> None:
        frame = self._tab_frames["Unidades"]

        if not details.transport_units:
            self._empty_message(
                frame,
                "Nenhuma unidade de transporte registrada.",
            )
            return

        allow_pending_actions = (
            is_pending_setup_available(
                details.current_status
            )
        )
        allow_in_progress_actions = (
            details.current_status == FreightStatus.IN_PROGRESS
        )

        last_unit_id = max(
            details.transport_units,
            key=lambda item: item.position,
        ).freight_transport_unit_id

        for unit in details.transport_units:
            allow_remove = (
                allow_pending_actions
                and unit.freight_transport_unit_id == last_unit_id
                and unit.vehicle is None
                and not unit.driver_assignments
            )
            self._render_unit_card(
                frame,
                unit,
                allow_pending_actions,
                allow_in_progress_actions,
                allow_remove,
            )

    def _render_unit_card(
        self,
        parent,
        unit: FreightTransportUnitDetails,
        allow_pending_actions: bool,
        allow_in_progress_actions: bool,
        allow_remove: bool,
    ) -> None:
        card = ctk.CTkFrame(parent)
        card.pack(fill="x", pady=(0, 10))

        unit_header = ctk.CTkFrame(
            card,
            fg_color="transparent",
        )
        unit_header.pack(
            fill="x",
            padx=12,
            pady=(10, 6),
        )

        ctk.CTkLabel(
            unit_header,
            text=f"Unidade {unit.position}",
            font=("Arial", 14, "bold"),
        ).pack(side="left")

        active_context = active_operational_context(unit)

        if (
            active_context is None
            and can_adopt_current_operational_context(
                status=self._current_details.current_status,
                has_vehicle=unit.vehicle is not None,
                has_active_driver=unit_has_active_driver(unit),
            )
        ):
            adopt_button = ctk.CTkButton(
                unit_header,
                text="Reconhecer conjunto atual",
                width=175,
                command=lambda current_unit=unit: (
                    self._adopt_current_operational_assignment(
                        current_unit
                    )
                ),
            )
            adopt_button.pack(
                side="right",
                padx=(8, 0),
            )
            self._operation_buttons.append(
                adopt_button
            )

        if active_context is not None:
            if (
                allow_in_progress_actions
                and can_replace_current_operational_context(
                    status=self._current_details.current_status,
                    active_context=active_context,
                )
            ):
                replace_context_button = ctk.CTkButton(
                    unit_header,
                    text="Trocar conjunto operacional",
                    width=190,
                    command=lambda current_unit=unit: (
                        self._replace_operational_assignment(
                            current_unit
                        )
                    ),
                )
                replace_context_button.pack(
                    side="right",
                    padx=(8, 0),
                )
                self._operation_buttons.append(
                    replace_context_button
                )

            if can_finish_current_operational_context(
                status=self._current_details.current_status,
                active_context=active_context,
                has_active_driver=unit_has_active_driver(unit),
            ):
                finish_context_button = ctk.CTkButton(
                    unit_header,
                    text="Encerrar conjunto operacional",
                    width=200,
                    command=lambda current_unit=unit: (
                        self._finish_operational_assignment(
                            current_unit
                        )
                    ),
                )
                finish_context_button.pack(
                    side="right",
                    padx=(8, 0),
                )
                self._operation_buttons.append(
                    finish_context_button
                )

            ctk.CTkLabel(
                unit_header,
                text=(
                    "Conjunto atual: "
                    f"{active_context.provider_name_snapshot} | "
                    f"{active_context.driver_name_snapshot} | "
                    f"{active_context.vehicle_plate_snapshot}"
                ),
                font=("Arial", 11, "bold"),
            ).pack(
                side="right",
                padx=(8, 0),
            )

        if allow_remove:
            remove_button = ctk.CTkButton(
                unit_header,
                text="Remover unidade",
                width=120,
                command=lambda current_unit=unit: (
                    self._remove_transport_unit(current_unit)
                ),
            )
            remove_button.pack(side="right")
            self._operation_buttons.append(remove_button)

        if unit.vehicle is None:
            vehicle_row = ctk.CTkFrame(
                card,
                fg_color="transparent",
            )
            vehicle_row.pack(
                fill="x",
                padx=12,
                pady=(0, 6),
            )

            ctk.CTkLabel(
                vehicle_row,
                text="Veículo: não informado",
            ).pack(side="left")

            if allow_pending_actions:
                button = ctk.CTkButton(
                    vehicle_row,
                    text="Selecionar veículo",
                    width=125,
                    command=lambda current_unit=unit: (
                        self._add_vehicle(current_unit)
                    ),
                )
                button.pack(side="right")
                self._operation_buttons.append(button)
        else:
            vehicle = unit.vehicle
            ctk.CTkLabel(
                card,
                text=(
                    "Veículo: "
                    f"{vehicle_label(vehicle.vehicle_type)} | "
                    f"Placa {vehicle.plate} | "
                    f"{vehicle.axle_count} eixos | "
                    f"{vehicle.payload_capacity_kg} kg"
                ),
            ).pack(anchor="w", padx=12, pady=(0, 6))

            pallet_text = (
                str(vehicle.pallet_capacity_min)
                if (
                    vehicle.pallet_capacity_min
                    == vehicle.pallet_capacity_max
                )
                else (
                    f"{vehicle.pallet_capacity_min}–"
                    f"{vehicle.pallet_capacity_max}"
                )
            )
            ctk.CTkLabel(
                card,
                text=f"Capacidade de pallets: {pallet_text}",
            ).pack(anchor="w", padx=12, pady=(0, 5))

            if allow_pending_actions:
                vehicle_actions = ctk.CTkFrame(
                    card,
                    fg_color="transparent",
                )
                vehicle_actions.pack(
                    fill="x",
                    padx=12,
                    pady=(0, 8),
                )

                replace_vehicle_button = ctk.CTkButton(
                    vehicle_actions,
                    text="Trocar veículo",
                    width=115,
                    command=lambda current_unit=unit: (
                        self._replace_vehicle(current_unit)
                    ),
                )
                replace_vehicle_button.pack(
                    side="right",
                    padx=(8, 0),
                )

                remove_vehicle_button = ctk.CTkButton(
                    vehicle_actions,
                    text="Remover veículo",
                    width=120,
                    command=lambda current_unit=unit: (
                        self._remove_vehicle(current_unit)
                    ),
                )
                remove_vehicle_button.pack(side="right")

                self._operation_buttons.extend(
                    (replace_vehicle_button, remove_vehicle_button)
                )

        driver_header = ctk.CTkFrame(
            card,
            fg_color="transparent",
        )
        driver_header.pack(
            fill="x",
            padx=12,
            pady=(2, 4),
        )

        ctk.CTkLabel(
            driver_header,
            text="Motoristas",
            font=("Arial", 12, "bold"),
        ).pack(side="left")

        if allow_pending_actions:
            if unit_has_active_driver(unit):
                replace_driver_button = ctk.CTkButton(
                    driver_header,
                    text="Trocar motorista",
                    width=135,
                    command=lambda current_unit=unit: (
                        self._replace_driver(current_unit)
                    ),
                )
                replace_driver_button.pack(side="right")
                self._operation_buttons.append(
                    replace_driver_button
                )
            else:
                assign_button = ctk.CTkButton(
                    driver_header,
                    text="Atribuir motorista",
                    width=135,
                    command=lambda current_unit=unit: (
                        self._assign_driver(current_unit)
                    ),
                )
                assign_button.pack(side="right")
                self._operation_buttons.append(assign_button)


        if not unit.driver_assignments:
            ctk.CTkLabel(
                card,
                text="Nenhuma participação de motorista.",
            ).pack(anchor="w", padx=12, pady=(0, 10))
            return

        for assignment in unit.driver_assignments:
            state = "Ativo" if assignment.is_active else "Encerrado"
            amount = format_currency(
                assignment.actual_driver_amount
            )
            context = assignment.operational_context
            context_text = (
                (
                    f" | Prestador "
                    f"{context.provider_name_snapshot}"
                    f" | Veículo "
                    f"{context.vehicle_plate_snapshot}"
                )
                if context is not None
                else ""
            )

            ctk.CTkLabel(
                card,
                text=(
                    f"• {assignment.driver_name} | {state} | "
                    f"Início {format_datetime(assignment.started_at)} | "
                    f"Fim {format_datetime(assignment.ended_at)} | "
                    f"Realizado {amount}"
                    f"{context_text}"
                ),
                justify="left",
                anchor="w",
                wraplength=780,
            ).pack(
                fill="x",
                anchor="w",
                padx=12,
                pady=(0, 5),
            )

        ctk.CTkLabel(card, text="").pack(pady=(0, 2))

    def _add_transport_unit(self) -> None:
        if (
            self._is_loading
            or self._is_operation_running
            or self._current_details is None
            or not is_pending_setup_available(
                self._current_details.current_status
            )
        ):
            return

        if not messagebox.askyesno(
            "Adicionar unidade",
            "Adicionar uma nova unidade de transporte a este frete?",
        ):
            return

        self._run_operation(
            task=lambda: self._add_transport_unit_callback(
                freight_id=self.freight_id
            ),
            success_message="Unidade de transporte adicionada.",
        )

    def _remove_transport_unit(
        self,
        unit: FreightTransportUnitDetails,
    ) -> None:
        if (
            self._is_loading
            or self._is_operation_running
            or self._current_details is None
            or not is_pending_setup_available(
                self._current_details.current_status
            )
            or unit.vehicle is not None
            or unit.driver_assignments
        ):
            return

        if not messagebox.askyesno(
            "Remover unidade",
            (
                f"Remover a Unidade {unit.position}?\n\n"
                "Use esta opção somente para desfazer uma "
                "unidade adicionada por engano."
            ),
        ):
            return

        self._run_operation(
            task=lambda: self._remove_transport_unit_callback(
                freight_transport_unit_id=(
                    unit.freight_transport_unit_id
                )
            ),
            success_message="Unidade de transporte removida.",
        )

    def _add_vehicle(
        self,
        unit: FreightTransportUnitDetails,
    ) -> None:
        if (
            self._is_loading
            or self._is_operation_running
            or self._current_details is None
            or not is_pending_setup_available(
                self._current_details.current_status
            )
            or unit.vehicle is not None
        ):
            return

        dialog = FreightVehicleDialog(
            parent=self.parent,
            unit_position=unit.position,
            search_vehicles_callback=(
                self._search_available_vehicles_callback
            ),
        )

        if dialog.result is None:
            return

        selected_vehicle = dialog.result

        self._run_operation(
            task=lambda: self._add_vehicle_callback(
                freight_transport_unit_id=(
                    unit.freight_transport_unit_id
                ),
                vehicle_id=selected_vehicle.vehicle_id,
            ),
            success_message=(
                f"Veículo {selected_vehicle.plate} selecionado "
                f"para a Unidade {unit.position}."
            ),
        )

    def _replace_vehicle(
        self,
        unit: FreightTransportUnitDetails,
    ) -> None:
        if (
            self._is_loading
            or self._is_operation_running
            or self._current_details is None
            or not is_pending_setup_available(
                self._current_details.current_status
            )
            or unit.vehicle is None
        ):
            return

        dialog = FreightVehicleDialog(
            parent=self.parent,
            unit_position=unit.position,
            search_vehicles_callback=(
                self._search_available_vehicles_callback
            ),
        )

        if dialog.result is None:
            return

        selected_vehicle = dialog.result
        current_vehicle = unit.vehicle

        if not messagebox.askyesno(
            "Trocar veículo",
            (
                f"Trocar o veículo {current_vehicle.plate} pelo "
                f"{selected_vehicle.plate} na Unidade "
                f"{unit.position}?\n\n"
                "A troca é permitida somente enquanto o frete "
                "estiver pendente."
            ),
            parent=self.parent,
        ):
            return

        self._run_operation(
            task=lambda: self._replace_vehicle_callback(
                freight_transport_unit_id=(
                    unit.freight_transport_unit_id
                ),
                vehicle_id=selected_vehicle.vehicle_id,
            ),
            success_message=(
                f"Veículo da Unidade {unit.position} trocado "
                f"para {selected_vehicle.plate}."
            ),
        )

    def _remove_vehicle(
        self,
        unit: FreightTransportUnitDetails,
    ) -> None:
        if (
            self._is_loading
            or self._is_operation_running
            or self._current_details is None
            or not is_pending_setup_available(
                self._current_details.current_status
            )
            or unit.vehicle is None
        ):
            return

        vehicle = unit.vehicle

        if not messagebox.askyesno(
            "Remover veículo",
            (
                f"Remover o veículo {vehicle.plate} da "
                f"Unidade {unit.position}?\n\n"
                "Esta ação remove somente o registro operacional "
                "deste frete. O veículo continua disponível em "
                "Cadastros > Veículos."
            ),
            parent=self.parent,
        ):
            return

        self._run_operation(
            task=lambda: self._remove_vehicle_callback(
                freight_transport_unit_id=(
                    unit.freight_transport_unit_id
                )
            ),
            success_message=(
                f"Veículo {vehicle.plate} removido da "
                f"Unidade {unit.position}."
            ),
        )

    def _assign_driver(
        self,
        unit: FreightTransportUnitDetails,
    ) -> None:
        if (
            self._is_loading
            or self._is_operation_running
            or self._current_details is None
            or self._current_details.current_status not in {
                FreightStatus.PENDING,
                FreightStatus.IN_PROGRESS,
            }
            or unit_has_active_driver(unit)
        ):
            return

        dialog = FreightDriverDialog(
            parent=self.parent,
            unit_position=unit.position,
            search_drivers_callback=(
                self._search_available_drivers_callback
            ),
        )

        if dialog.result is None:
            return

        selected_driver = dialog.result

        self._run_operation(
            task=lambda: self._assign_driver_callback(
                freight_transport_unit_id=(
                    unit.freight_transport_unit_id
                ),
                driver_id=selected_driver.driver_id,
            ),
            success_message=(
                f"Motorista {selected_driver.name} atribuído "
                f"à Unidade {unit.position}."
            ),
        )

    def _replace_driver(
        self,
        unit: FreightTransportUnitDetails,
    ) -> None:
        if (
            self._is_loading
            or self._is_operation_running
            or self._current_details is None
            or not is_pending_setup_available(
                self._current_details.current_status
            )
            or not unit_has_active_driver(unit)
        ):
            return

        current_assignment = next(
            (
                assignment
                for assignment in unit.driver_assignments
                if assignment.is_active
            ),
            None,
        )
        if current_assignment is None:
            return

        dialog = FreightDriverDialog(
            parent=self.parent,
            unit_position=unit.position,
            search_drivers_callback=(
                self._search_available_drivers_callback
            ),
        )

        if dialog.result is None:
            return

        selected_driver = dialog.result

        if not messagebox.askyesno(
            "Trocar motorista",
            (
                f"Trocar o motorista {current_assignment.driver_name} "
                f"por {selected_driver.name} na Unidade "
                f"{unit.position}?\n\n"
                "A troca é permitida somente enquanto o frete "
                "estiver pendente."
            ),
            parent=self.parent,
        ):
            return

        self._run_operation(
            task=lambda: self._replace_driver_callback(
                freight_transport_unit_id=(
                    unit.freight_transport_unit_id
                ),
                driver_id=selected_driver.driver_id,
            ),
            success_message=(
                f"Motorista da Unidade {unit.position} trocado "
                f"para {selected_driver.name}."
            ),
        )

    def _finish_operational_assignment(
        self,
        unit: FreightTransportUnitDetails,
    ) -> None:
        if (
            self._is_loading
            or self._is_operation_running
            or self._current_details is None
        ):
            return

        current_context = active_operational_context(
            unit
        )
        active_assignment = next(
            (
                assignment
                for assignment in unit.driver_assignments
                if assignment.is_active
            ),
            None,
        )

        if (
            active_assignment is None
            or not can_finish_current_operational_context(
                status=self._current_details.current_status,
                active_context=current_context,
                has_active_driver=True,
            )
        ):
            return

        dialog = FreightFinishOperationalAssignmentDialog(
            parent=self.parent,
            unit_position=unit.position,
            current_context=current_context,
        )

        if dialog.result is None:
            return

        actual_transport_amount = dialog.result

        if not messagebox.askyesno(
            "Encerrar conjunto operacional",
            (
                "Encerrar o conjunto atual:\n"
                f"{current_context.provider_name_snapshot} | "
                f"{current_context.driver_name_snapshot} | "
                f"{current_context.vehicle_plate_snapshot}\n\n"
                "Valor realizado pelo conjunto: "
                f"R$ {actual_transport_amount:.2f}\n\n"
                "Depois desta operação a unidade ficará sem "
                "conjunto operacional ativo."
            ),
            parent=self.parent.winfo_toplevel(),
        ):
            return

        self._run_operation(
            task=lambda: self._finish_driver_callback(
                freight_driver_assignment_id=(
                    active_assignment
                    .freight_driver_assignment_id
                ),
                actual_driver_amount=(
                    actual_transport_amount
                ),
            ),
            success_message=(
                f"Conjunto operacional da Unidade "
                f"{unit.position} encerrado."
            ),
        )

    def _replace_operational_assignment(
        self,
        unit: FreightTransportUnitDetails,
    ) -> None:
        if (
            self._is_loading
            or self._is_operation_running
            or self._current_details is None
        ):
            return

        current_context = active_operational_context(
            unit
        )
        if not can_replace_current_operational_context(
            status=self._current_details.current_status,
            active_context=current_context,
        ):
            return

        dialog = FreightOperationalAssignmentReplaceDialog(
            parent=self.parent,
            unit_position=unit.position,
            current_context=current_context,
            search_transport_providers_callback=(
                self._search_transport_providers_callback
            ),
            get_transport_provider_details_callback=(
                self._get_transport_provider_details_callback
            ),
        )

        if dialog.result is None:
            return

        selection = dialog.result

        if not messagebox.askyesno(
            "Trocar conjunto operacional",
            (
                "Encerrar o conjunto atual:\n"
                f"{current_context.provider_name_snapshot} | "
                f"{current_context.driver_name_snapshot} | "
                f"{current_context.vehicle_plate_snapshot}\n"
                f"Valor realizado: R$ "
                f"{selection.actual_transport_amount:.2f}\n\n"
                "E iniciar o novo conjunto:\n"
                f"{selection.provider_name} | "
                f"{selection.driver_name} | "
                f"{selection.vehicle_plate}?"
            ),
            parent=self.parent.winfo_toplevel(),
        ):
            return

        self._run_operation(
            task=lambda: (
                self._replace_in_progress_operational_assignment_callback(
                    freight_transport_unit_id=(
                        unit.freight_transport_unit_id
                    ),
                    transport_provider_id=(
                        selection.transport_provider_id
                    ),
                    driver_id=selection.driver_id,
                    vehicle_id=selection.vehicle_id,
                    actual_transport_amount=(
                        selection.actual_transport_amount
                    ),
                )
            ),
            success_message=(
                f"Conjunto operacional da Unidade "
                f"{unit.position} trocado para "
                f"{selection.provider_name} | "
                f"{selection.driver_name} | "
                f"{selection.vehicle_plate}."
            ),
        )

    def _adopt_current_operational_assignment(
        self,
        unit: FreightTransportUnitDetails,
    ) -> None:
        if (
            self._is_loading
            or self._is_operation_running
            or self._current_details is None
            or not can_adopt_current_operational_context(
                status=self._current_details.current_status,
                has_vehicle=unit.vehicle is not None,
                has_active_driver=unit_has_active_driver(unit),
            )
        ):
            return

        if not messagebox.askyesno(
            "Reconhecer conjunto atual",
            (
                f"Reconhecer o motorista e o veículo atuais "
                f"da Unidade {unit.position} como um único "
                "conjunto operacional?\n\n"
                "O prestador será identificado pelos vínculos "
                "cadastrais atuais do motorista e do veículo."
            ),
            parent=self.parent.winfo_toplevel(),
        ):
            return

        self._run_operation(
            task=lambda: (
                self._adopt_current_operational_assignment_callback(
                    freight_transport_unit_id=(
                        unit.freight_transport_unit_id
                    ),
                )
            ),
            success_message=(
                f"Conjunto operacional da Unidade "
                f"{unit.position} reconhecido."
            ),
        )

    def _finish_driver(
        self,
        assignment: FreightDriverAssignmentDetails,
    ) -> None:
        if (
            self._is_loading
            or self._is_operation_running
            or self._current_details is None
            or self._current_details.current_status
            != FreightStatus.IN_PROGRESS
            or not assignment.is_active
        ):
            return

        dialog = FreightFinishDriverDialog(
            parent=self.parent,
            driver_name=assignment.driver_name,
        )

        if dialog.result is None:
            return

        actual_driver_amount = dialog.result

        if not messagebox.askyesno(
            "Encerrar motorista",
            (
                f"Encerrar a participação de "
                f"{assignment.driver_name}?\n\n"
                f"Valor realizado: R$ "
                f"{actual_driver_amount:.2f}"
            ),
            parent=self.parent,
        ):
            return

        self._run_operation(
            task=lambda: self._finish_driver_callback(
                freight_driver_assignment_id=(
                    assignment.freight_driver_assignment_id
                ),
                actual_driver_amount=actual_driver_amount,
            ),
            success_message=(
                f"Participação de {assignment.driver_name} "
                "encerrada."
            ),
        )

    def _complete_freight(self) -> None:
        if (
            self._is_loading
            or self._is_operation_running
            or self._current_details is None
            or not can_complete_freight(
                self._current_details
            )
        ):
            return

        if not messagebox.askyesno(
            "Concluir frete",
            (
                "Todas as unidades estão operacionalmente "
                "encerradas.\n\n"
                "Concluir este frete?\n\n"
                "Após a conclusão, o status operacional será "
                "terminal."
            ),
            parent=self.parent.winfo_toplevel(),
        ):
            return

        self._run_operation(
            task=lambda: self._complete_freight_callback(
                freight_id=self.freight_id
            ),
            success_message="Frete concluído.",
        )

    def _start_freight(self) -> None:
        if (
            self._is_loading
            or self._is_operation_running
            or self._current_details is None
            or not can_start_freight(
                self._current_details
            )
        ):
            return

        if not messagebox.askyesno(
            "Iniciar frete",
            (
                "Todas as unidades possuem veículo e motorista "
                "ativo. Iniciar a operação deste frete?"
            ),
        ):
            return

        self._run_operation(
            task=lambda: self._start_freight_callback(
                freight_id=self.freight_id
            ),
            success_message="Frete iniciado.",
        )

    def _run_operation(
        self,
        task,
        success_message: str,
    ) -> None:
        self._set_operation_running(True)
        self._task_runner.run(
            task=task,
            on_success=lambda _result: (
                self._on_operation_success(
                    success_message
                )
            ),
            on_error=self._on_operation_error,
        )

    def _on_operation_success(
        self,
        success_message: str,
    ) -> None:
        if not self._view_exists():
            return

        self._set_operation_running(False)
        messagebox.showinfo(
            "Operação concluída",
            success_message,
        )
        self.load()

    def _on_operation_error(
        self,
        error: Exception,
    ) -> None:
        if not self._view_exists():
            return

        self._set_operation_running(False)
        messagebox.showerror(
            "Operação não realizada",
            str(error),
        )

    def _set_operation_running(
        self,
        value: bool,
    ) -> None:
        self._is_operation_running = value

        self.refresh_button.configure(
            state=(
                "disabled"
                if value
                else "normal"
            ),
        )

        if value:
            for button in self._operation_buttons:
                try:
                    button.configure(
                        state="disabled"
                    )
                except Exception:
                    pass
        else:
            self._apply_operation_button_states()

        self.loading_label.configure(
            text=(
                "Executando operação..."
                if value
                else ""
            )
        )

    def _apply_operation_button_states(
        self,
    ) -> None:
        if self._is_operation_running:
            return

        for button in self._operation_buttons:
            try:
                button.configure(
                    state="normal"
                )
            except Exception:
                pass

        if self._current_details is None:
            self.start_freight_button.configure(
                state="disabled"
            )
            return

        self.start_freight_button.configure(
            state=(
                "normal"
                if can_start_freight(
                    self._current_details
                )
                else "disabled"
            )
        )
        self.complete_freight_button.configure(
            state=(
                "normal"
                if can_complete_freight(
                    self._current_details
                )
                else "disabled"
            )
        )

    def _render_expenses(
        self,
        details: FreightDetails,
    ) -> None:
        frame = self._tab_frames["Despesas"]

        if not details.expenses:
            self._empty_message(
                frame,
                "Nenhuma despesa realizada registrada.",
            )
            return

        for expense in details.expenses:
            self._render_expense_card(frame, expense)

    def _render_expense_card(
        self,
        parent,
        expense: FreightExpenseDetails,
    ) -> None:
        card = ctk.CTkFrame(parent)
        card.pack(fill="x", pady=(0, 8))

        description = (
            expense.custom_description
            if expense.custom_description
            else expense_label(expense.expense_type)
        )
        ctk.CTkLabel(
            card,
            text=(
                f"{description} — {format_currency(expense.value)}"
            ),
            font=("Arial", 12, "bold"),
        ).pack(anchor="w", padx=12, pady=(8, 3))

        ctk.CTkLabel(
            card,
            text=(
                f"Ocorrência: {format_datetime(expense.occurred_at)} | "
                f"Considerada no resultado: {yes_no(expense.is_considered)}"
            ),
        ).pack(anchor="w", padx=12, pady=(0, 3))

        ctk.CTkLabel(
            card,
            text=f"Observação: {optional_text(expense.observation)}",
            justify="left",
            anchor="w",
            wraplength=780,
        ).pack(fill="x", padx=12, pady=(0, 8))

    def _render_history(
        self,
        details: FreightDetails,
    ) -> None:
        frame = self._tab_frames["Histórico"]

        if not details.events:
            self._empty_message(
                frame,
                "Nenhum evento operacional registrado.",
            )
            return

        for event in details.events:
            previous = (
                status_label(event.previous_status)
                if event.previous_status is not None
                else "--"
            )
            card = ctk.CTkFrame(frame)
            card.pack(fill="x", pady=(0, 8))

            ctk.CTkLabel(
                card,
                text=(
                    f"{event_label(event.event_type)} — "
                    f"{format_datetime(event.occurred_at)}"
                ),
                font=("Arial", 12, "bold"),
            ).pack(anchor="w", padx=12, pady=(8, 3))

            ctk.CTkLabel(
                card,
                text=(
                    f"Status: {previous} → "
                    f"{status_label(event.new_status)} | "
                    f"Usuário ID: {event.user_id or '--'}"
                ),
            ).pack(anchor="w", padx=12, pady=(0, 3))

            ctk.CTkLabel(
                card,
                text=f"Observação: {optional_text(event.observation)}",
                justify="left",
                anchor="w",
                wraplength=780,
            ).pack(fill="x", padx=12, pady=(0, 8))

    def _render_financial(
        self,
        details: FreightDetails,
    ) -> None:
        frame = self._tab_frames["Financeiro"]
        result = details.financial_result

        if result is None:
            self._empty_message(
                frame,
                "Frete ainda não possui fechamento financeiro.",
            )
            return

        rows = (
            ("Receita contratada", format_currency(result.contracted_revenue)),
            ("Motoristas realizados", format_currency(result.actual_driver_amount)),
            ("Pedágio", format_currency(result.toll_amount)),
            ("Despesas realizadas", format_currency(result.actual_expenses_total)),
            ("Seguro de frete", format_currency(result.freight_insurance_total)),
            ("Impostos", format_currency(result.tax_total)),
            (
                "Administrativo alocado",
                format_currency(result.administrative_cost_allocated),
            ),
            ("Custo total", format_currency(result.total_cost)),
            ("Resultado realizado", format_currency(result.realized_result)),
            ("Margem realizada", format_margin(result.realized_margin)),
            ("Fechado em", format_datetime(result.finalized_at)),
        )

        self._render_key_value_rows(frame, rows)

    @staticmethod
    def _render_key_value_rows(
        parent,
        rows,
    ) -> None:
        for label, value in rows:
            row = ctk.CTkFrame(
                parent,
                fg_color="transparent",
            )
            row.pack(fill="x", pady=3)
            row.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                row,
                text=f"{label}:",
                font=("Arial", 12, "bold"),
                width=190,
                anchor="w",
            ).grid(
                row=0,
                column=0,
                sticky="w",
            )
            ctk.CTkLabel(
                row,
                text=value,
                anchor="w",
                justify="left",
                wraplength=600,
            ).grid(
                row=0,
                column=1,
                sticky="ew",
            )

    @staticmethod
    def _empty_message(
        parent,
        text: str,
    ) -> None:
        ctk.CTkLabel(
            parent,
            text=text,
        ).pack(anchor="w", padx=8, pady=8)

    def _set_loading(
        self,
        value: bool,
    ) -> None:
        self._is_loading = value
        self.refresh_button.configure(
            state=(
                "disabled"
                if value or self._is_operation_running
                else "normal"
            ),
        )
        self.loading_label.configure(
            text=(
                "Carregando detalhes..."
                if value
                else "Executando operação..."
                if self._is_operation_running
                else ""
            ),
        )

    def _view_exists(self) -> bool:
        try:
            return bool(self.main_frame.winfo_exists())
        except Exception:
            return False
