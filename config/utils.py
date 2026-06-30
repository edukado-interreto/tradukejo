import os
import socket
import sys
from enum import StrEnum, auto
from typing import Self


class Environment(StrEnum):
    PRODUCTION = auto()
    STAGING = auto()
    DEV = auto()
    BUILD = auto()
    TESTING = auto()

    def display_name(self):
        if self == self.PRODUCTION:
            return ""
        if self == self.STAGING:
            return "TEST"
        return str(self).upper()

    @property
    def deployed(self) -> bool:
        return self in {self.PRODUCTION, self.STAGING}

    @classmethod
    def init(cls, config, debug: bool) -> Self:
        if is_testing():
            return cls.TESTING
        if debug:
            return cls.DEV
        return cls(config("ENVIRONMENT", "production"))

    def __getattr__(self, attr) -> bool:
        """Check the enum’s value by attribute

        >>> ENVIRONMENT = Environment.DEV
        >>> ENVIRONMENT.is_dev
        True
        >>> ENVIRONMENT.is_production
        False
        """
        name = attr.replace("is_", "")
        if name in (e.value for e in type(self)):
            return self.value == name
        return super().__getattribute__(name)

    def __dir__(self):
        return (*super().__dir__(), *(f"is_{v}" for v in type(self)))


def is_testing():
    return "test" in sys.argv or "PYTEST_VERSION" in os.environ


def django_vite_dev_mode(environment: Environment) -> bool:
    """Checks if `vite` is running the Docker service.

    Always return False in production
    """
    SERVICE_NAME = "vue"

    if environment.deployed:
        return False

    try:
        return bool(socket.gethostbyname(SERVICE_NAME))
    except socket.gaierror:
        return False


def get_beercss_dir(static_dir) -> str:
    """
    Get the BeerCSS directory name in the form `beercss-x.y.z`
    """
    try:
        return list(static_dir.glob("beercss-*"))[-1].name
    except IndexError:
        raise IndexError(f"BeerCSS is not install properly in {static_dir}")
