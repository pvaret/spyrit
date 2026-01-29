import importlib.metadata

from spyrit import constants


def get_version() -> str:
    try:
        return importlib.metadata.version(constants.PACKAGE_NAME)
    except (importlib.metadata.PackageNotFoundError, ValueError):
        return "0.0.999"
