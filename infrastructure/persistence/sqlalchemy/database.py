from sqlalchemy import (
    Engine,
    URL,
    create_engine
)
from sqlalchemy.orm import (
    Session,
    sessionmaker
)

from config.database import (
    DatabaseSettings
)


def create_database_url(
    settings: DatabaseSettings
) -> URL:

    if not settings.password:

        raise ValueError(
            "DATABASE_PASSWORD não configurada"
        )

    return URL.create(
        drivername="postgresql+psycopg",
        username=settings.username,
        password=settings.password,
        host=settings.host,
        port=settings.port,
        database=settings.database_name
    )


def create_database_engine(
    settings: DatabaseSettings
) -> Engine:

    return create_engine(
        create_database_url(
            settings
        ),
        pool_pre_ping=True
    )


def create_session_factory(
    engine: Engine
) -> sessionmaker[Session]:

    return sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False
    )