"""Utilities for managing SSH tunnels for database connections."""
from __future__ import annotations

import contextlib
import logging
import os
import select
import socketserver
import threading
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Tuple

try:  # pragma: no cover - optional dependency handled at runtime
    import paramiko
except ImportError:  # pragma: no cover - paramiko may be optional
    paramiko = None  # type: ignore[assignment]


logger = logging.getLogger(__name__)


class SSHAuthMode(str, Enum):
    """Supported SSH authentication modes."""

    PASSWORD = "password"
    PRIVATE_KEY = "private_key"
    PASSWORD_AND_KEY = "password_and_key"


_SENSITIVE_FIELDS = {
    "ssh_password",
    "ssh_private_key_passphrase",
    "password",
    "passphrase",
}


def _coerce_int(
    value: Any,
    *,
    default: Optional[int] = None,
    field_name: str,
    minimum: Optional[int] = None,
    maximum: Optional[int] = None,
) -> Optional[int]:
    """Coerce an arbitrary value to int with validation."""

    if value in (None, ""):
        return default

    try:
        coerced = int(value)
    except (TypeError, ValueError) as exc:  # pragma: no cover - defensive branch
        raise ValueError(f"Invalid integer value for {field_name!r}: {value!r}") from exc

    if minimum is not None and coerced < minimum:
        raise ValueError(
            f"Value for {field_name!r} must be >= {minimum}, received {coerced}"
        )
    if maximum is not None and coerced > maximum:
        raise ValueError(
            f"Value for {field_name!r} must be <= {maximum}, received {coerced}"
        )

    return coerced


def _mask(value: Optional[str]) -> str:
    """Return a masked representation for sensitive values."""

    if not value:
        return ""
    if len(value) <= 4:
        return "*" * len(value)
    return f"{'*' * (len(value) - 4)}{value[-4:]}"


def mask_sensitive_dict(values: Dict[str, Any]) -> Dict[str, Any]:
    """Return a copy of *values* with sensitive fields masked."""

    sanitised: Dict[str, Any] = {}
    for key, val in values.items():
        if key in _SENSITIVE_FIELDS:
            sanitised[key] = _mask(val)
        else:
            sanitised[key] = val
    return sanitised


@dataclass
class SSHConfig:
    """Runtime configuration for an SSH tunnel."""

    enabled: bool = False
    host: Optional[str] = None
    port: int = 22
    username: Optional[str] = None
    password: Optional[str] = None
    private_key_path: Optional[str] = None
    private_key_passphrase: Optional[str] = None
    auth_mode: str = SSHAuthMode.PASSWORD.value
    remote_host: Optional[str] = None
    remote_port: Optional[int] = None
    local_bind_host: str = "127.0.0.1"
    local_bind_port: Optional[int] = None
    known_hosts_path: Optional[str] = None
    strict_host_key_check: bool = True
    connect_timeout: int = 30
    keepalive_interval: int = 30
    compression: bool = False
    allow_agent: bool = False

    def __post_init__(self) -> None:
        self.port = _coerce_int(
            self.port,
            default=22,
            field_name="ssh_port",
            minimum=1,
            maximum=65535,
        ) or 22
        self.remote_port = _coerce_int(
            self.remote_port,
            field_name="remote_port",
            minimum=1,
            maximum=65535,
        )
        self.local_bind_port = _coerce_int(
            self.local_bind_port,
            field_name="ssh_local_bind_port",
            minimum=0,
            maximum=65535,
        )
        self.connect_timeout = _coerce_int(
            self.connect_timeout,
            default=30,
            field_name="ssh_connect_timeout",
            minimum=1,
        ) or 30
        self.keepalive_interval = _coerce_int(
            self.keepalive_interval,
            default=30,
            field_name="ssh_keepalive_interval",
            minimum=0,
        ) or 30

    def validate(self) -> None:
        """Validate the SSH configuration."""

        if not self.enabled:
            return

        if not self.host:
            raise ValueError("ssh_host is required when SSH tunnelling is enabled")
        if not self.username:
            raise ValueError("ssh_username is required when SSH tunnelling is enabled")
        if not self.remote_host:
            raise ValueError("Database host is required to create the SSH tunnel")
        if self.remote_port is None:
            raise ValueError("Database port is required to create the SSH tunnel")

        if self.auth_mode not in {mode.value for mode in SSHAuthMode}:
            raise ValueError(f"Unsupported SSH auth mode: {self.auth_mode!r}")

        requires_password = self.auth_mode in (
            SSHAuthMode.PASSWORD.value,
            SSHAuthMode.PASSWORD_AND_KEY.value,
        )
        requires_key = self.auth_mode in (
            SSHAuthMode.PRIVATE_KEY.value,
            SSHAuthMode.PASSWORD_AND_KEY.value,
        )

        if requires_password and not self.password:
            raise ValueError("ssh_password is required for password-based authentication")
        if requires_key and not self.private_key_path:
            raise ValueError(
                "ssh_private_key_path is required for private-key authentication"
            )

        if self.private_key_path and not os.path.isfile(self.private_key_path):
            raise ValueError(
                f"SSH private key not found at {self.private_key_path!r}. Make sure the file is readable by the backend."
            )

        if self.known_hosts_path and not os.path.exists(self.known_hosts_path):
            raise ValueError(
                f"Known hosts file not found at {self.known_hosts_path!r}. Provide a valid path or disable strict host key checking."
            )

    def to_log_dict(self) -> Dict[str, Any]:
        """Return a masked dictionary suitable for logging."""

        return mask_sensitive_dict(
            {
                "ssh_host": self.host,
                "ssh_port": self.port,
                "ssh_username": self.username,
                "ssh_auth_mode": self.auth_mode,
                "ssh_private_key_path": self.private_key_path,
                "ssh_known_hosts_path": self.known_hosts_path,
                "ssh_strict_host_key_check": self.strict_host_key_check,
                "ssh_connect_timeout": self.connect_timeout,
                "ssh_keepalive_interval": self.keepalive_interval,
                "ssh_compression": self.compression,
                "ssh_allow_agent": self.allow_agent,
                "remote_host": self.remote_host,
                "remote_port": self.remote_port,
            }
        )


class _ForwardServer(socketserver.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True


class _ForwardHandler(socketserver.BaseRequestHandler):
    remote_host: str = "localhost"
    remote_port: int = 0
    ssh_transport: Optional[Any] = None
    stop_event: Optional[threading.Event] = None
    select_timeout: float = 1.0

    def handle(self) -> None:  # pragma: no cover - network interaction
        if not self.ssh_transport:
            logger.error("SSH transport missing; cannot proxy request")
            return

        try:
            chan = self.ssh_transport.open_channel(
                "direct-tcpip",
                (self.remote_host, self.remote_port),
                self.request.getpeername(),
            )
        except Exception as exc:  # pragma: no cover - defensive branch
            logger.error("Failed to open channel through SSH tunnel: %s", exc)
            return

        if chan is None:
            logger.error("SSH transport returned no channel for tunnel")
            return

        try:
            while True:
                if self.stop_event and self.stop_event.is_set():
                    break

                rlist, _, _ = select.select(
                    [self.request, chan], [], [], self.select_timeout
                )
                if self.request in rlist:
                    data = self.request.recv(65536)
                    if not data:
                        break
                    chan.sendall(data)
                if chan in rlist:
                    data = chan.recv(65536)
                    if not data:
                        break
                    self.request.sendall(data)
        finally:
            try:
                chan.close()
            except Exception:  # pragma: no cover - cleanup best effort
                pass
            try:
                self.request.close()
            except Exception:  # pragma: no cover - cleanup best effort
                pass


class SSHTunnel:
    """Manage the lifecycle of an SSH tunnel using Paramiko."""

    def __init__(self, config: SSHConfig):
        self.config = config
        self._client: Optional[Any] = None
        self._transport: Optional[Any] = None
        self._server: Optional[_ForwardServer] = None
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self.local_bind_host: str = config.local_bind_host
        self.local_bind_port: Optional[int] = config.local_bind_port

    def open(self) -> Tuple[str, int]:  # pragma: no cover - network interaction
        """Open the SSH tunnel and return the local bind address."""

        if paramiko is None:
            raise RuntimeError(
                "Paramiko is required for SSH tunnelling. Install it via 'pip install paramiko'."
            )

        self.config.validate()
        logger.debug("Opening SSH tunnel with config: %s", self.config.to_log_dict())

        self._client = paramiko.SSHClient()
        self._configure_host_key_policy(self._client)

        password = (
            self.config.password
            if self.config.auth_mode
            in (SSHAuthMode.PASSWORD.value, SSHAuthMode.PASSWORD_AND_KEY.value)
            else None
        )
        key_filename = (
            self.config.private_key_path
            if self.config.auth_mode
            in (SSHAuthMode.PRIVATE_KEY.value, SSHAuthMode.PASSWORD_AND_KEY.value)
            else None
        )

        try:
            self._client.connect(
                hostname=self.config.host,
                port=self.config.port,
                username=self.config.username,
                password=password,
                key_filename=key_filename,
                passphrase=self.config.private_key_passphrase,
                timeout=self.config.connect_timeout,
                banner_timeout=self.config.connect_timeout,
                allow_agent=self.config.allow_agent,
                look_for_keys=False,
                compress=self.config.compression,
            )
        except Exception as exc:  # pragma: no cover - connection failure path
            raise RuntimeError(f"Failed to establish SSH connection: {exc}") from exc

        self._transport = self._client.get_transport()
        if self._transport is None:  # pragma: no cover - defensive branch
            self.close()
            raise RuntimeError("SSH transport is not available after authentication")

        if self.config.keepalive_interval:
            self._transport.set_keepalive(self.config.keepalive_interval)

        handler = self._build_handler(self._transport)
        bind_host = self.config.local_bind_host or "127.0.0.1"
        bind_port = self.config.local_bind_port or 0
        self._server = _ForwardServer((bind_host, bind_port), handler)
        self._server.stop_event = self._stop_event  # type: ignore[attr-defined]

        self.local_bind_host, self.local_bind_port = self._server.server_address

        self._thread = threading.Thread(
            target=self._serve,
            name="ThothSSHForwardServer",
            daemon=True,
        )
        self._thread.start()

        logger.info(
            "SSH tunnel active %s:%s -> %s:%s",
            self.local_bind_host,
            self.local_bind_port,
            self.config.remote_host,
            self.config.remote_port,
        )

        return self.local_bind_host, int(self.local_bind_port)

    def _serve(self) -> None:  # pragma: no cover - network interaction
        if not self._server:
            return
        try:
            self._server.serve_forever(poll_interval=0.5)
        except Exception as exc:
            if not self._stop_event.is_set():
                logger.error("SSH tunnel server terminated unexpectedly: %s", exc)

    def _configure_host_key_policy(self, client: Any) -> None:
        if self.config.strict_host_key_check:
            if self.config.known_hosts_path:
                try:
                    client.load_host_keys(self.config.known_hosts_path)
                except Exception as exc:  # pragma: no cover - defensive branch
                    raise ValueError(
                        f"Unable to load known hosts from {self.config.known_hosts_path!r}: {exc}"
                    ) from exc
            else:
                client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.RejectPolicy())
        else:
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def _build_handler(self, transport: Any) -> type[_ForwardHandler]:
        config = self.config
        stop_evt = self._stop_event  # Renamed to avoid Python 3.13 PEP 709 scoping issue

        class Handler(_ForwardHandler):  # type: ignore[misc]
            remote_host = config.remote_host or "localhost"
            remote_port = int(config.remote_port or 0)
            ssh_transport = transport
            stop_event = stop_evt  # Use renamed variable to avoid name collision
            select_timeout = 1.0

        return Handler

    def is_active(self) -> bool:
        return bool(self._transport and self._transport.is_active())

    def close(self) -> None:  # pragma: no cover - cleanup interaction
        self._stop_event.set()

        if self._server is not None:
            with contextlib.suppress(Exception):
                self._server.shutdown()
            with contextlib.suppress(Exception):
                self._server.server_close()
            self._server = None

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
        self._thread = None

        if self._transport is not None:
            with contextlib.suppress(Exception):
                self._transport.close()
            self._transport = None

        if self._client is not None:
            with contextlib.suppress(Exception):
                self._client.close()
            self._client = None

    def __enter__(self) -> "SSHTunnel":
        self.open()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self) -> None:  # pragma: no cover - best effort cleanup
        self.close()


def extract_ssh_parameters(params: Dict[str, Any]) -> Tuple[Optional[SSHConfig], Dict[str, Any]]:
    """Extract SSH configuration from adapter parameters."""

    adapter_params = {k: v for k, v in params.items() if not k.startswith("ssh_")}
    enabled = bool(params.get("ssh_enabled"))

    if not enabled:
        return None, adapter_params

    config = SSHConfig(
        enabled=True,
        host=params.get("ssh_host"),
        port=params.get("ssh_port", 22),
        username=params.get("ssh_username"),
        password=params.get("ssh_password"),
        private_key_path=params.get("ssh_private_key_path"),
        private_key_passphrase=params.get("ssh_private_key_passphrase"),
        auth_mode=params.get("ssh_auth_method", SSHAuthMode.PASSWORD.value),
        remote_host=adapter_params.get("host"),
        remote_port=adapter_params.get("port"),
        local_bind_host=params.get("ssh_local_bind_host", "127.0.0.1"),
        local_bind_port=params.get("ssh_local_bind_port"),
        known_hosts_path=params.get("ssh_known_hosts_path"),
        strict_host_key_check=params.get("ssh_strict_host_key_check", True),
        connect_timeout=params.get("ssh_connect_timeout", 30),
        keepalive_interval=params.get("ssh_keepalive_interval", 30),
        compression=bool(params.get("ssh_compression", False)),
        allow_agent=bool(params.get("ssh_allow_agent", False)),
    )

    config.validate()
    return config, adapter_params
