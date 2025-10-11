"""
Base classes and registry for MFA handlers.

This module provides the base handler class that all MFA methods must inherit from,
along with a registry system for managing available MFA handlers.
"""

import re
from typing import TYPE_CHECKING, Any

from django.contrib.auth.hashers import check_password
from rest_framework import serializers
from rest_framework.serializers import Serializer

from pyotp import TOTP

from auth_kit.mfa.mfa_settings import auth_kit_mfa_settings
from auth_kit.mfa.models import MFAMethod

if TYPE_CHECKING:  # pragma: no cover
    from django.utils.functional import (
        _StrPromise,  # pyright: ignore[reportPrivateUsage]
    )
else:
    _StrPromise = str


class SetupMethodSerializer(Serializer[dict[str, str]]):
    """Default serializer for MFA method initial setup responses."""

    detail = serializers.CharField(read_only=True, required=False)


class MFABaseHandler:
    """
    Base class for all MFA method handlers.

    Provides common functionality for TOTP generation/validation, backup code
    management, and code dispatch. Subclasses must implement method-specific
    behavior like sending codes via email or SMS.

    Subclasses must define a NAME (snake_case method identifier) and optionally
    customize DISPLAY_NAME (human-readable name), REQUIRES_DISPATCH flag for
    code sending, SETUP_RESPONSE_MESSAGE for user feedback, and TOTP timing
    parameters (TOTP_INTERVAL and TOTP_VALID_WINDOW). Each handler instance
    is associated with an MFAMethod instance.
    """

    NAME = ""
    DISPLAY_NAME = ""
    REQUIRES_DISPATCH = True
    SETUP_RESPONSE_MESSAGE: str | _StrPromise = ""
    TOTP_INTERVAL = auth_kit_mfa_settings.MFA_TOTP_DEFAULT_INTERVAL
    TOTP_VALID_WINDOW = auth_kit_mfa_settings.MFA_TOTP_DEFAULT_VALID_WINDOW

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """
        Validate subclass configuration.

        Args:
            **kwargs: Additional keyword arguments

        Raises:
            ValueError: If NAME is not set or invalid format
        """
        super().__init_subclass__(**kwargs)
        if not cls.NAME:
            raise ValueError(f"Class {cls.__name__} must define a non-empty NAME")

        if not re.match(r"^[a-z]+(_[a-z]+)*$", cls.NAME):
            raise ValueError(
                f"Class {cls.__name__} NAME must be in snake_case format (lowercase letters and underscores only)"
            )

        if not cls.DISPLAY_NAME:
            cls.DISPLAY_NAME = cls.NAME.replace("_", " ").upper()  # pyright: ignore

    def __init__(self, mfa_method: MFAMethod) -> None:
        """
        Initialize handler with MFA method.

        Args:
            mfa_method: MFAMethod instance to handle
        """
        self.mfa_method = mfa_method

    def _get_otp(self) -> TOTP:
        """
        Get TOTP instance for this method.

        Returns:
            Configured TOTP instance
        """
        return TOTP(self.mfa_method.secret, interval=self.TOTP_INTERVAL)

    def send_code(self) -> None:
        """Send verification code to user. Override in subclasses."""
        pass

    def initialize_method(self) -> dict[str, Any]:
        """
        Initialize method setup and return setup data.

        Returns:
            Dictionary with setup information
        """
        self.send_code()
        return {"detail": self.SETUP_RESPONSE_MESSAGE}

    @classmethod
    def get_initialize_method_serializer_class(
        cls,
    ) -> type[Serializer[Any]]:
        """
        Get serializer class for method setup responses.

        Returns:
            Serializer class for setup responses
        """
        return SetupMethodSerializer

    def get_otp_code(self) -> str:
        """
        Generate current TOTP code.

        Returns:
            Current TOTP code string
        """
        return self._get_otp().now()

    def validate_code(self, code: str) -> bool:
        """
        Validate verification code (TOTP or backup).

        Args:
            code: Code to validate

        Returns:
            True if code is valid
        """
        return self.validate_otp_code(code) or self.validate_backup_code(code)

    def validate_otp_code(self, otp_code: str) -> bool:
        """
        Validate TOTP code.

        Args:
            otp_code: TOTP code to validate

        Returns:
            True if code is valid
        """
        return self._get_otp().verify(otp=otp_code, valid_window=self.TOTP_VALID_WINDOW)

    def validate_backup_code(self, backup_code: str) -> bool:
        """
        Validate and consume backup code.

        Args:
            backup_code: Backup code to validate

        Returns:
            True if code is valid and consumed
        """
        if len(backup_code) != auth_kit_mfa_settings.BACKUP_CODE_LENGTH:
            return False

        backup_codes: set[str] = self.mfa_method.backup_codes

        if auth_kit_mfa_settings.BACKUP_CODE_SECURE_HASH:
            # Hash-based validation
            for stored_code in backup_codes:
                if check_password(backup_code, stored_code):
                    self.mfa_method.backup_codes = backup_codes - {stored_code}
                    self.mfa_method.save()
                    return True
            return False
        else:
            # Plain text validation
            if backup_code in backup_codes:
                self.mfa_method.backup_codes = backup_codes - {backup_code}
                self.mfa_method.save()
                return True
            return False


class MFAHandlerRegistry:
    """
    Registry for managing available MFA handlers.

    Provides centralized registration and retrieval of MFA handler classes.
    Handlers are automatically imported when first accessed.

    Class Attributes:
        _handlers: Dictionary mapping method names to handler classes
        imported_handler: Flag tracking whether handlers have been imported
    """

    _handlers: dict[str, type[MFABaseHandler]] = {}
    imported_handler = False

    @classmethod
    def register(cls, handler_class: type[MFABaseHandler]) -> None:
        """
        Register a handler class.

        Args:
            handler_class: Handler class to register
        """
        cls._handlers[handler_class.NAME] = handler_class

    @classmethod
    def _prefetch_handlers(cls) -> None:
        """Import all configured handlers if not already done."""
        if not cls.imported_handler:
            list(auth_kit_mfa_settings.MFA_HANDLERS)
            cls.imported_handler = True

    @classmethod
    def get_handler_class(cls, mfa_method_name: str) -> type[MFABaseHandler]:
        """
        Get handler class by method name.

        Args:
            mfa_method_name: Name of the MFA method

        Returns:
            Handler class for the method

        Raises:
            ValueError: If method name is not supported
        """
        cls._prefetch_handlers()

        handler_class = cls._handlers.get(mfa_method_name.lower())
        if not handler_class:
            raise ValueError(f"Unsupported MFA method: {mfa_method_name}")
        return handler_class

    @classmethod
    def get_handler(cls, mfa_method: MFAMethod) -> MFABaseHandler:
        """
        Get handler instance for MFA method.

        Args:
            mfa_method: MFAMethod instance

        Returns:
            Handler instance for the method
        """
        handler_class = cls.get_handler_class(mfa_method.name)
        return handler_class(mfa_method=mfa_method)

    @classmethod
    def list_handler_names(cls) -> list[str]:
        """
        Get list of all registered handler names.

        Returns:
            List of handler names
        """
        cls._prefetch_handlers()
        return list(cls._handlers.keys())

    @classmethod
    def get_handlers(cls) -> dict[str, type[MFABaseHandler]]:
        """
        Get all registered handlers.

        Returns:
            Dictionary mapping names to handler classes
        """
        cls._prefetch_handlers()
        return cls._handlers
