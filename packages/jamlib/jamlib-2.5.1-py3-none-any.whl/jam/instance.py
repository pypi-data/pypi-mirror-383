# -*- coding: utf-8 -*-

import gc
from collections.abc import Callable
from typing import Any, Optional, Union

from jam.__abc_instances__ import BaseJam
from jam.__logger__ import logger
from jam.modules import JWTModule, OAuth2Module, SessionModule
from jam.utils.config_maker import __config_maker__, __module_loader__


class Jam(BaseJam):
    """Main instance."""

    _JAM_MODULES: dict[str, str] = {
        "jwt": "jam.modules.JWTModule",
        "session": "jam.modules.SessionModule",
        "oauth2": "jam.modules.OAuth2Module",
    }

    def __init__(
        self,
        config: Union[dict[str, Any], str] = "pyproject.toml",
        pointer: str = "jam",
    ) -> None:
        """Class constructor.

        Args:
            config (dict[str, Any] | str): dict or path to config file
            pointer (str): Config read point
        """
        self.jwt: Optional[JWTModule] = None
        self.session: Optional[SessionModule] = None
        self.oauth2: Optional[OAuth2Module] = None

        config = __config_maker__(config, pointer)

        # OTP
        otp_config = config.pop("otp", None)
        if otp_config:
            from jam.otp.__abc_module__ import OTPConfig

            self._otp = OTPConfig(**otp_config)
            self._otp_module = self._otp_module_setup()
            logger.debug("OTP module initialized")

        # Other modules
        if config.get("auth_type", None):
            logger.warning(
                "This configuration type is deprecated, see: https://jam.makridenko.ru/config"
            )
            name = config.pop("auth_type")
            module = __module_loader__(self._JAM_MODULES[name])
            setattr(self, name, module(**config))
        else:
            for name, cfg in config.items():
                try:
                    module = self.build_module(name, cfg)
                    setattr(self, name, module)
                    logger.debug(
                        f"Auth module '{name}' successfully initialized"
                    )
                except Exception as e:
                    logger.exception(
                        f"Failed to initialize auth module '{name}': {e}"
                    )
        gc.collect()

    # TODO: Refactor this too
    def _otp_module_setup(self) -> Callable:
        otp_type = self._otp.type
        if otp_type == "hotp":
            from jam.otp import HOTP

            return HOTP
        elif otp_type == "totp":
            from jam.otp import TOTP

            return TOTP
        else:
            raise ValueError("OTP type can only be totp or hotp.")

    def _otp_checker(self) -> None:
        if not hasattr(self, "_otp"):
            raise NotImplementedError(
                "OTP not configure. Check documentation: "
            )

    def make_payload(self, exp: Optional[int] = None, **data) -> dict[str, Any]:
        """Payload maker tool.

        Args:
            exp (int | None): If none exp = JWTModule.exp
            **data: Custom data
        """
        return self.jwt.make_payload(exp=exp, **data)

    def gen_jwt_token(self, payload: dict[str, Any]) -> str:
        """Creating a new token.

        Args:
            payload (dict[str, Any]): Payload with information

        Raises:
            EmptySecretKey: If the HMAC algorithm is selected, but the secret key is None
            EmtpyPrivateKey: If RSA algorithm is selected, but private key None
        """
        return self.jwt.gen_token(**payload)

    def verify_jwt_token(
        self, token: str, check_exp: bool = True, check_list: bool = True
    ) -> dict[str, Any]:
        """A method for verifying a token.

        Args:
            token (str): The token to check
            check_exp (bool): Check for expiration?
            check_list (bool): Check if there is a black/white list

        Raises:
            ValueError: If the token is invalid.
            EmptySecretKey: If the HMAC algorithm is selected, but the secret key is None.
            EmtpyPublicKey: If RSA algorithm is selected, but public key None.
            NotFoundSomeInPayload: If 'exp' not found in payload.
            TokenLifeTimeExpired: If token has expired.
            TokenNotInWhiteList: If the list type is white, but the token is  not there
            TokenInBlackList: If the list type is black and the token is there

        Returns:
            (dict[str, Any]): Payload from token
        """
        return self.jwt.validate_payload(
            token=token, check_exp=check_exp, check_list=check_list
        )

    def create_session(self, session_key: str, data: dict) -> str:
        """Create a new session.

        Args:
            session_key (str): Session key
            data (dict): Data to store in session

        Raises:
            NotImplementedError: If the auth type is not "session"

        Returns:
            str: The created session key
        """
        return self.session.create(session_key, data)

    def get_session(self, session_id: str) -> Optional[dict]:
        """Retrieve session data by session ID.

        Args:
            session_id (str): The ID of the session to retrieve.

        Raises:
            NotImplementedError: If the auth type is not "session".

        Returns:
            dict | None: The session data if found, otherwise None.
        """
        return self.session.get(session_id)

    def delete_session(self, session_id: str) -> None:
        """Delete a session by its ID.

        Args:
            session_id (str): The ID of the session to delete.

        Raises:
            NotImplementedError: If the auth type is not "session".

        Returns:
            None
        """
        return self.session.delete(session_id)

    def update_session(self, session_id: str, data: dict) -> None:
        """Update session data by session ID.

        Args:
            session_id (str): The ID of the session to update.
            data (dict): The new data to update the session with.

        Raises:
            NotImplementedError: If the auth type is not "session".

        Returns:
            None
        """
        return self.session.update(session_id, data)

    def clear_sessions(self, session_key: str) -> None:
        """Clear all sessions associated with a specific session key.

        Args:
            session_key (str): The session key whose sessions are to be cleared.

        Raises:
            NotImplementedError: If the auth type is not "session".

        Returns:
            None
        """
        return self.session.clear(session_key)

    def rework_session(self, old_session_key: str) -> str:
        """Rework an existing session key to a new one.

        Args:
            old_session_key (str): The old session key to be reworked.

        Raises:
            NotImplementedError: If the auth type is not "session".

        Returns:
            str: The new session key.
        """
        return self.session.rework(old_session_key)

    def get_otp_code(
        self, secret: Union[str, bytes], factor: Optional[int] = None
    ) -> str:
        """Generates an OTP.

        Args:
            secret (str | bytes): User secret key.
            factor (int | None, optional): Unixtime for TOTP(if none, use now time) / Counter for HOTP.

        Returns:
            str: OTP code (fixed-length string).
        """
        self._otp_checker()
        return self._otp_module(
            secret=secret, digits=self._otp.digits, digest=self._otp.digest
        ).at(factor)

    def get_otp_uri(
        self,
        secret: str,
        name: Optional[str] = None,
        issuer: Optional[str] = None,
        counter: Optional[int] = None,
    ) -> str:
        """Generates an otpauth:// URI for Google Authenticator.

        Args:
            secret (str): User secret key.
            name (str): Account name (e.g., email).
            issuer (str): Service name (e.g., "GitHub").
            counter (int | None, optional): Counter (for HOTP). Default is None.

        Returns:
            str: A string of the form "otpauth://..."
        """
        self._otp_checker()
        return self._otp_module(
            secret=secret, digits=self._otp.digits, digest=self._otp.digest
        ).provisioning_uri(
            name=name, issuer=issuer, type_=self._otp.type, counter=counter
        )

    def verify_otp_code(
        self,
        secret: Union[str, bytes],
        code: str,
        factor: Optional[int] = None,
        look_ahead: Optional[int] = 1,
    ) -> bool:
        """Checks the OTP code, taking into account the acceptable window.

        Args:
            secret (str | bytes): User secret key.
            code (str): The code entered.
            factor (int | None, optional): Unixtime for TOTP(if none, use now time) / Counter for HOTP.
            look_ahead (int, optional): Acceptable deviation in intervals (±window(totp) / ±look ahead(hotp)). Default is 1.

        Returns:
            bool: True if the code matches, otherwise False.
        """
        self._otp_checker()
        return self._otp_module(
            secret=secret, digits=self._otp.digits, digest=self._otp.digest
        ).verify(code=code, factor=factor, look_ahead=look_ahead)

    def oauth2_get_authorized_url(
        self, provider: str, scope: list[str], **extra_params: Any
    ) -> str:
        """Generate full OAuth2 authorization URL.

        Args:
            provider (str): Provider name
            scope (list[str]): Auth scope
            extra_params (Any): Extra ath params

        Returns:
            str: Authorization url
        """
        return self.oauth2.get_authorization_url(
            provider, scope, **extra_params
        )

    def oauth2_fetch_token(
        self,
        provider: str,
        code: str,
        grant_type: str = "authorization_code",
        **extra_params: Any,
    ) -> dict[str, Any]:
        """Exchange authorization code for access token.

        Args:
            provider (str): Provider name
            code (str): OAuth2 code
            grant_type (str): Type of oauth2 grant
            extra_params (Any): Extra auth params if needed

        Returns:
            dict: OAuth2 token
        """
        return self.oauth2.fetch_token(
            provider, code, grant_type, **extra_params
        )

    def oauth2_refresh_token(
        self,
        provider: str,
        refresh_token: str,
        grant_type: str = "refresh_token",
        **extra_params: Any,
    ) -> dict[str, Any]:
        """Use refresh token to obtain a new access token.

        Args:
            provider (str): Provider name
            refresh_token (str): Refresh token
            grant_type (str): Grant type
            extra_params (Any): Extra auth params if needed

        Returns:
            dict: Refresh token
        """
        return self.oauth2.refresh_token(
            provider, refresh_token, grant_type, **extra_params
        )

    def oauth2_client_credentials_flow(
        self,
        provider: str,
        scope: Optional[list[str]] = None,
        **extra_params: Any,
    ) -> dict[str, Any]:
        """Obtain access token using client credentials flow (no user interaction).

        Args:
            provider (str): OAuth2 provider
            scope (list[str] | None): Auth scope
            extra_params (Any): Extra auth params if needed

        Returns:
            dict: JSON with access token
        """
        return self.oauth2.client_credentials_flow(
            provider, scope, **extra_params
        )
