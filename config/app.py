import os


def _read_bool_environment(
    name: str,
    default: bool = False
) -> bool:

    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "on"
    }


QUALP_EMAIL = os.getenv(
    "QUALP_EMAIL"
)

QUALP_PASSWORD = os.getenv(
    "QUALP_PASSWORD"
)

QUALP_HEADLESS = _read_bool_environment(
    "QUALP_HEADLESS",
    default=False
)