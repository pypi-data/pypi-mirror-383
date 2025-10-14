"""Exception definitions for KITECH Repository."""


class KitechException(Exception):
    """Base exception for KITECH Repository."""

    pass


class AuthenticationError(KitechException):
    """Authentication related errors."""

    pass


class ApiError(KitechException):
    """API request related errors."""

    pass


class DownloadError(KitechException):
    """File download related errors."""

    pass


class UploadError(KitechException):
    """File upload related errors."""

    pass


class ConfigurationError(KitechException):
    """Configuration related errors."""

    pass