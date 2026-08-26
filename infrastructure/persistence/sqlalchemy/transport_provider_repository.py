from sqlalchemy import or_, select
from sqlalchemy.exc import (
    IntegrityError,
    SQLAlchemyError,
)
from sqlalchemy.orm import Session

from application.exceptions import (
    TransportProviderAlreadyExistsError,
    TransportProviderPersistenceError,
)
from application.ports.transport_provider_repository import (
    TransportProviderRepository,
)
from domain.models.transport_provider import (
    TransportProvider,
    TransportProviderStatus,
    TransportProviderType,
    normalize_transport_provider_document,
)
from infrastructure.persistence.sqlalchemy.models import (
    TransportProviderModel,
)


class SqlAlchemyTransportProviderRepository(
    TransportProviderRepository
):

    def __init__(self, session: Session):
        self._session = session

    def add(
        self,
        provider: TransportProvider,
    ) -> TransportProvider:
        if provider.transport_provider_id is not None:
            raise ValueError(
                "Prestador já possui transport_provider_id"
            )

        model = self._to_model(provider)
        self._session.add(model)

        try:
            self._session.flush()
            self._session.refresh(model)
        except IntegrityError as error:
            self._raise_integrity_error(error)
        except SQLAlchemyError as error:
            raise TransportProviderPersistenceError(
                "Não foi possível salvar o prestador"
            ) from error

        return self._to_domain(model)

    def save(
        self,
        provider: TransportProvider,
    ) -> TransportProvider:
        if provider.transport_provider_id is None:
            raise ValueError(
                "Prestador precisa possuir transport_provider_id"
            )

        try:
            model = self._session.scalar(
                select(TransportProviderModel)
                .where(
                    TransportProviderModel.transport_provider_id
                    == provider.transport_provider_id
                )
                .with_for_update()
            )

            if model is None:
                raise TransportProviderPersistenceError(
                    "Prestador não encontrado durante atualização"
                )

            model.legal_name = provider.legal_name
            model.trade_name = provider.trade_name
            model.tax_document = provider.tax_document
            model.provider_type = provider.provider_type.value
            model.status = provider.status.value
            model.updated_by = provider.updated_by

            if provider.updated_at is not None:
                model.updated_at = provider.updated_at

            self._session.flush()
            self._session.refresh(model)

        except IntegrityError as error:
            self._raise_integrity_error(error)
        except TransportProviderPersistenceError:
            raise
        except SQLAlchemyError as error:
            raise TransportProviderPersistenceError(
                "Não foi possível atualizar o prestador"
            ) from error

        return self._to_domain(model)

    def get_by_id(
        self,
        transport_provider_id: int,
    ) -> TransportProvider | None:
        return self._get_by_id(
            transport_provider_id,
            for_update=False,
        )

    def get_by_id_for_update(
        self,
        transport_provider_id: int,
    ) -> TransportProvider | None:
        return self._get_by_id(
            transport_provider_id,
            for_update=True,
        )

    def _get_by_id(
        self,
        transport_provider_id: int,
        for_update: bool,
    ) -> TransportProvider | None:
        statement = select(
            TransportProviderModel
        ).where(
            TransportProviderModel.transport_provider_id
            == transport_provider_id
        )

        if for_update:
            statement = statement.with_for_update()

        try:
            model = self._session.scalar(statement)
        except SQLAlchemyError as error:
            raise TransportProviderPersistenceError(
                "Não foi possível consultar o prestador"
            ) from error

        return (
            self._to_domain(model)
            if model is not None
            else None
        )

    def get_by_tax_document(
        self,
        tax_document: str,
    ) -> TransportProvider | None:
        try:
            document = normalize_transport_provider_document(
                tax_document
            )
        except ValueError:
            return None

        try:
            model = self._session.scalar(
                select(TransportProviderModel)
                .where(
                    TransportProviderModel.tax_document
                    == document
                )
            )
        except SQLAlchemyError as error:
            raise TransportProviderPersistenceError(
                "Não foi possível consultar prestador por documento"
            ) from error

        return (
            self._to_domain(model)
            if model is not None
            else None
        )

    def search(
        self,
        query: str = "",
        status: TransportProviderStatus | None = None,
        provider_type: TransportProviderType | None = None,
        limit: int = 100,
    ) -> tuple[TransportProvider, ...]:
        statement = select(
            TransportProviderModel
        )

        query = query.strip()
        if query:
            document_query = "".join(
                character
                for character in query
                if character.isdigit()
            )
            conditions = [
                TransportProviderModel.legal_name.ilike(
                    f"%{query}%"
                ),
                TransportProviderModel.trade_name.ilike(
                    f"%{query}%"
                ),
            ]
            if document_query:
                conditions.append(
                    TransportProviderModel.tax_document.ilike(
                        f"%{document_query}%"
                    )
                )

            statement = statement.where(
                or_(*conditions)
            )

        if status is not None:
            statement = statement.where(
                TransportProviderModel.status
                == TransportProviderStatus(status).value
            )

        if provider_type is not None:
            statement = statement.where(
                TransportProviderModel.provider_type
                == TransportProviderType(provider_type).value
            )

        statement = statement.order_by(
            TransportProviderModel.legal_name,
            TransportProviderModel.transport_provider_id,
        ).limit(limit)

        try:
            models = self._session.scalars(
                statement
            ).all()
        except SQLAlchemyError as error:
            raise TransportProviderPersistenceError(
                "Não foi possível pesquisar prestadores"
            ) from error

        return tuple(
            self._to_domain(model)
            for model in models
        )

    @staticmethod
    def _to_model(
        provider: TransportProvider,
    ) -> TransportProviderModel:
        model = TransportProviderModel(
            legal_name=provider.legal_name,
            trade_name=provider.trade_name,
            tax_document=provider.tax_document,
            provider_type=provider.provider_type.value,
            status=provider.status.value,
            created_by=provider.created_by,
            updated_by=provider.updated_by,
        )

        if provider.created_at is not None:
            model.created_at = provider.created_at

        if provider.updated_at is not None:
            model.updated_at = provider.updated_at

        return model

    @staticmethod
    def _to_domain(
        model: TransportProviderModel,
    ) -> TransportProvider:
        return TransportProvider(
            transport_provider_id=model.transport_provider_id,
            legal_name=model.legal_name,
            trade_name=model.trade_name,
            tax_document=model.tax_document,
            provider_type=TransportProviderType(
                model.provider_type
            ),
            status=TransportProviderStatus(
                model.status
            ),
            created_at=model.created_at,
            created_by=model.created_by,
            updated_at=model.updated_at,
            updated_by=model.updated_by,
        )

    @staticmethod
    def _raise_integrity_error(
        error: IntegrityError,
    ) -> None:
        original_error = getattr(
            error,
            "orig",
            None,
        )
        diagnostics = getattr(
            original_error,
            "diag",
            None,
        )
        constraint_name = getattr(
            diagnostics,
            "constraint_name",
            None,
        )

        if (
            constraint_name
            == "uq_transport_providers_tax_document"
        ):
            raise TransportProviderAlreadyExistsError(
                "Documento já cadastrado para outro prestador"
            ) from error

        raise TransportProviderPersistenceError(
            "Não foi possível salvar o prestador"
        ) from error
