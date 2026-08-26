import customtkinter as ctk
import logging

from application.use_cases.add_freight_transport_unit import (
    AddFreightTransportUnit
)
from application.use_cases.assign_driver_to_freight_transport_unit import (
    AssignDriverToFreightTransportUnit
)
from application.use_cases.add_freight_vehicle_record import (
    AddFreightVehicleRecord
)
from application.use_cases.calculate_closed_load_quote import (
    CalculateClosedLoadQuote
)
from application.use_cases.create_driver import (
    CreateDriver
)
from application.use_cases.create_vehicle import (
    CreateVehicle
)
from application.use_cases.get_driver import (
    GetDriver
)
from application.use_cases.get_vehicle import (
    GetVehicle
)
from application.use_cases.generate_quote_pdf import (
    GenerateQuotePdf
)
from application.use_cases.remove_freight_transport_unit import (
    RemoveFreightTransportUnit
)
from application.use_cases.remove_freight_vehicle_record import (
    RemoveFreightVehicleRecord
)
from application.use_cases.get_freight_details import (
    GetFreightDetails
)
from application.use_cases.list_freights import (
    ListFreights
)
from application.use_cases.list_drivers import (
    ListDrivers
)
from application.use_cases.search_available_freight_drivers import (
    SearchAvailableFreightDrivers
)
from application.use_cases.search_available_freight_vehicles import (
    SearchAvailableFreightVehicles
)
from application.use_cases.search_vehicles import (
    SearchVehicles
)
from application.use_cases.start_freight import (
    StartFreight
)
from application.use_cases.replace_pending_freight_driver import (
    ReplacePendingFreightDriver
)
from application.use_cases.replace_pending_freight_vehicle import (
    ReplacePendingFreightVehicle
)
from application.use_cases.update_driver import (
    UpdateDriver
)
from application.use_cases.update_vehicle import (
    UpdateVehicle
)
from config.app import (
    QUALP_EMAIL,
    QUALP_PASSWORD,
    QUALP_HEADLESS,
)
from config.database import (
    load_database_settings
)
from infrastructure.logging_config import (
    configure_logging
)
from infrastructure.pdf.reportlab_quote_pdf_generator import (
    ReportLabQuotePdfGenerator
)
from infrastructure.persistence.sqlalchemy.database import (
    create_database_engine,
    create_session_factory,
)
from infrastructure.persistence.sqlalchemy.driver_query_repository import (
    SqlAlchemyDriverQueryRepository,
)
from infrastructure.persistence.sqlalchemy.driver_unit_of_work import (
    SqlAlchemyDriverUnitOfWorkFactory,
)
from infrastructure.persistence.sqlalchemy.freight_driver_assignment_unit_of_work import (
    SqlAlchemyFreightDriverAssignmentUnitOfWorkFactory,
)
from infrastructure.persistence.sqlalchemy.freight_driver_selection_repository import (
    SqlAlchemyFreightDriverSelectionRepository,
)
from infrastructure.persistence.sqlalchemy.freight_query_repository import (
    SqlAlchemyFreightQueryRepository,
)
from infrastructure.persistence.sqlalchemy.freight_unit_of_work import (
    SqlAlchemyFreightUnitOfWorkFactory,
)
from infrastructure.persistence.sqlalchemy.freight_vehicle_record_unit_of_work import (
    SqlAlchemyFreightVehicleRecordUnitOfWorkFactory,
)
from infrastructure.persistence.sqlalchemy.freight_vehicle_selection_repository import (
    SqlAlchemyFreightVehicleSelectionRepository,
)
from infrastructure.persistence.sqlalchemy.vehicle_unit_of_work import (
    SqlAlchemyVehicleUnitOfWorkFactory,
)
from infrastructure.qualp.qualp_route_searcher import (
    QualPRouteSearcher
)
from presentation.desktop.controllers.quote_pdf_controller import (
    QuotePdfController
)
from presentation.desktop.main_menu import MainMenu


logger = logging.getLogger(
    "sistemafrete"
)


def _report_callback_exception(
    exception_type,
    exception_value,
    exception_traceback
) -> None:

    logger.critical(
        "Erro não tratado em callback da interface",
        exc_info=(
            exception_type,
            exception_value,
            exception_traceback
        )
    )


def _create_list_freights_callback(
    session_factory,
):

    def list_freights(**filters):
        with session_factory() as session:
            repository = (
                SqlAlchemyFreightQueryRepository(
                    session
                )
            )
            return ListFreights(
                repository
            ).execute(
                **filters
            )

    return list_freights


def _create_get_freight_details_callback(
    session_factory,
):

    def get_freight_details(freight_id: int):
        with session_factory() as session:
            repository = (
                SqlAlchemyFreightQueryRepository(
                    session
                )
            )
            return GetFreightDetails(
                repository
            ).execute(
                freight_id
            )

    return get_freight_details


def _create_search_available_drivers_callback(
    session_factory,
):

    def search_available_drivers(
        query: str,
        limit: int = 20,
    ):
        with session_factory() as session:
            repository = (
                SqlAlchemyFreightDriverSelectionRepository(
                    session
                )
            )
            return SearchAvailableFreightDrivers(
                repository
            ).execute(
                query=query,
                limit=limit,
            )

    return search_available_drivers


def _create_search_available_vehicles_callback(
    session_factory,
):

    def search_available_vehicles(
        query: str = "",
        limit: int = 200,
    ):
        with session_factory() as session:
            repository = SqlAlchemyFreightVehicleSelectionRepository(
                session
            )
            return SearchAvailableFreightVehicles(
                repository
            ).execute(
                query=query,
                limit=limit,
            )

    return search_available_vehicles


def _create_list_drivers_callback(
    session_factory,
):

    def list_drivers(**filters):
        with session_factory() as session:
            repository = SqlAlchemyDriverQueryRepository(
                session
            )
            return ListDrivers(
                repository
            ).execute(
                **filters
            )

    return list_drivers


def create_application():

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    window = ctk.CTk()
    window.report_callback_exception = (
        _report_callback_exception
    )

    database_settings = (
        load_database_settings()
    )
    database_engine = (
        create_database_engine(
            database_settings
        )
    )
    session_factory = (
        create_session_factory(
            database_engine
        )
    )

    route_searcher = QualPRouteSearcher(
        email=QUALP_EMAIL,
        password=QUALP_PASSWORD,
        headless=QUALP_HEADLESS
    )

    calculate_closed_load_quote = (
        CalculateClosedLoadQuote(
            route_searcher=route_searcher
        )
    )

    quote_pdf_generator = (
        ReportLabQuotePdfGenerator()
    )

    generate_quote_pdf = GenerateQuotePdf(
        pdf_generator=quote_pdf_generator
    )

    quote_pdf_controller = QuotePdfController(
        generate_quote_pdf=generate_quote_pdf
    )

    freight_unit_of_work_factory = (
        SqlAlchemyFreightUnitOfWorkFactory(
            session_factory
        )
    )
    freight_vehicle_unit_of_work_factory = (
        SqlAlchemyFreightVehicleRecordUnitOfWorkFactory(
            session_factory
        )
    )
    driver_unit_of_work_factory = (
        SqlAlchemyDriverUnitOfWorkFactory(
            session_factory
        )
    )
    vehicle_unit_of_work_factory = (
        SqlAlchemyVehicleUnitOfWorkFactory(
            session_factory
        )
    )
    freight_driver_assignment_unit_of_work_factory = (
        SqlAlchemyFreightDriverAssignmentUnitOfWorkFactory(
            session_factory
        )
    )

    create_driver = CreateDriver(
        driver_unit_of_work_factory
    )
    get_driver = GetDriver(
        driver_unit_of_work_factory
    )
    update_driver = UpdateDriver(
        driver_unit_of_work_factory
    )
    create_vehicle = CreateVehicle(
        vehicle_unit_of_work_factory
    )
    get_vehicle = GetVehicle(
        vehicle_unit_of_work_factory
    )
    search_vehicles = SearchVehicles(
        vehicle_unit_of_work_factory
    )
    update_vehicle = UpdateVehicle(
        vehicle_unit_of_work_factory
    )
    add_transport_unit = AddFreightTransportUnit(
        freight_unit_of_work_factory
    )
    remove_transport_unit = RemoveFreightTransportUnit(
        freight_unit_of_work_factory
    )
    add_vehicle = AddFreightVehicleRecord(
        freight_vehicle_unit_of_work_factory
    )
    remove_vehicle = RemoveFreightVehicleRecord(
        freight_vehicle_unit_of_work_factory
    )
    replace_vehicle = ReplacePendingFreightVehicle(
        freight_vehicle_unit_of_work_factory
    )
    assign_driver = AssignDriverToFreightTransportUnit(
        freight_driver_assignment_unit_of_work_factory
    )
    replace_driver = ReplacePendingFreightDriver(
        freight_driver_assignment_unit_of_work_factory
    )
    start_freight = StartFreight(
        freight_unit_of_work_factory
    )

    MainMenu(
        master=window,
        calculate_quote_callback=(
            calculate_closed_load_quote.execute
        ),
        generate_pdf_callback=(
            quote_pdf_controller.generate
        ),
        list_freights_callback=(
            _create_list_freights_callback(
                session_factory
            )
        ),
        get_freight_details_callback=(
            _create_get_freight_details_callback(
                session_factory
            )
        ),
        add_transport_unit_callback=(
            add_transport_unit.execute
        ),
        remove_transport_unit_callback=(
            remove_transport_unit.execute
        ),
        add_vehicle_callback=(
            add_vehicle.execute
        ),
        remove_vehicle_callback=(
            remove_vehicle.execute
        ),
        replace_vehicle_callback=(
            replace_vehicle.execute
        ),
        search_available_vehicles_callback=(
            _create_search_available_vehicles_callback(
                session_factory
            )
        ),
        search_available_drivers_callback=(
            _create_search_available_drivers_callback(
                session_factory
            )
        ),
        create_driver_callback=(
            create_driver.execute
        ),
        list_drivers_callback=(
            _create_list_drivers_callback(
                session_factory
            )
        ),
        get_driver_callback=(
            get_driver.execute
        ),
        update_driver_callback=(
            update_driver.execute
        ),
        create_vehicle_callback=(
            create_vehicle.execute
        ),
        search_vehicles_callback=(
            search_vehicles.execute
        ),
        get_vehicle_callback=(
            get_vehicle.execute
        ),
        update_vehicle_callback=(
            update_vehicle.execute
        ),
        assign_driver_callback=(
            assign_driver.execute
        ),
        replace_driver_callback=(
            replace_driver.execute
        ),
        start_freight_callback=(
            start_freight.execute
        ),
    )

    def close_application() -> None:
        database_engine.dispose()
        window.destroy()

    window.protocol(
        "WM_DELETE_WINDOW",
        close_application,
    )

    return window


def main():

    configure_logging()

    logger.info(
        "Aplicação iniciada"
    )

    window = create_application()

    window.mainloop()


if __name__ == "__main__":
    main()
