from dataclasses import dataclass
import os


@dataclass(frozen=True)
class DatabaseSettings:
    host: str
    port: int
    database_name: str
    username: str
    password: str | None


def load_database_settings() -> DatabaseSettings:

    port_value = os.getenv(
        "DATABASE_PORT",
        "5432"
    )

    try:

        port = int(
            port_value
        )

    except ValueError as error:

        raise ValueError(
            "DATABASE_PORT inválida"
        ) from error

    return DatabaseSettings(
        host=os.getenv(
            "DATABASE_HOST",
            "localhost"
        ),
        port=port,
        database_name=os.getenv(
            "DATABASE_NAME",
            "sistemafrete"
        ),
        username=os.getenv(
            "DATABASE_USER",
            "sistemafrete_app"
        ),
        password=os.getenv(
            "DATABASE_PASSWORD"
        )
    )