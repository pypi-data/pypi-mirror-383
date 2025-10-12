"""High-level Python bindings for the WhatsUpBraeker Go bridge."""

from __future__ import annotations

import ctypes
import json
import os
import platform
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path
from typing import Any, Dict, List, Optional

__all__ = [
    "LibraryLoadError",
    "WhatsAppClient",
    "WhatsAppMessage",
    "WhatsAppResponse",
    "load_library",
]

_LIB_EXTENSIONS = {
    "Darwin": ".dylib",
    "Linux": ".so",
    "Windows": ".dll",
}


class LibraryLoadError(RuntimeError):
    """Raised when the shared library cannot be located or loaded."""


@dataclass
class WhatsAppMessage:
    id: str
    timestamp: int
    from_jid: str
    text: str
    is_group: bool = False


@dataclass
class WhatsAppResponse:
    success: bool
    message_id: Optional[str] = None
    messages: List[WhatsAppMessage] = field(default_factory=list)
    requires_qr: bool = False
    error: Optional[str] = None


class WhatsAppClient:
    """Convenient wrapper around the Go shared library."""

    def __init__(
        self,
        phone: str,
        lib_path: Optional[Path | str] = None,
        db_uri: Optional[str] = None,
        timeout: int = 30,
        show_qr: bool = True,
    ) -> None:
        if not phone:
            raise ValueError("phone number is required")

        self.phone = str(phone)
        self.timeout = int(timeout) if timeout is not None else 30
        self.show_qr = bool(show_qr)
        self.db_uri = db_uri or "file:whatsapp.db?_foreign_keys=on"

        self._lib_path = _resolve_library_path(lib_path)
        self._lib: Optional[ctypes.CDLL] = None
        self._wa_run: Optional[ctypes._CFuncPtr] = None
        self._wa_free: Optional[ctypes._CFuncPtr] = None

        self._load_library()

    def _load_library(self) -> None:
        if not self._lib_path.exists():
            raise FileNotFoundError(f"shared library not found: {self._lib_path}")

        try:
            lib = ctypes.CDLL(str(self._lib_path))
        except OSError as exc:  # pragma: no cover - defensive
            raise LibraryLoadError(f"failed to load shared library: {exc}") from exc

        wa_run = lib.WaRun
        wa_run.argtypes = [ctypes.c_char_p]
        wa_run.restype = ctypes.c_void_p

        wa_free = lib.WaFree
        wa_free.argtypes = [ctypes.c_void_p]
        wa_free.restype = None

        self._lib = lib
        self._wa_run = wa_run
        self._wa_free = wa_free

    def _base_config(self) -> Dict[str, Any]:
        return {
            "phone": self.phone,
            "db_uri": self.db_uri,
            "timeout": max(int(self.timeout), 0),
            "show_qr": bool(self.show_qr),
        }

    def _call_library(self, extra_config: Dict[str, Any]) -> WhatsAppResponse:
        if self._wa_run is None or self._wa_free is None:
            raise RuntimeError("library functions are not initialised")

        config = self._base_config()
        config.update(extra_config)

        try:
            payload = json.dumps(config, ensure_ascii=False).encode("utf-8")
        except (TypeError, ValueError) as exc:
            raise ValueError(f"failed to serialise config: {exc}") from exc

        ptr = self._wa_run(ctypes.c_char_p(payload))
        if not ptr:
            raise RuntimeError("library returned NULL pointer")

        try:
            raw = ctypes.string_at(ptr).decode("utf-8")
        finally:
            self._wa_free(ptr)

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"failed to decode response JSON: {exc}") from exc

        messages = [
            WhatsAppMessage(
                id=str(item.get("id", "")),
                timestamp=int(item.get("timestamp", 0) or 0),
                from_jid=str(item.get("from_jid", "")),
                text=str(item.get("text", "")),
                is_group=bool(item.get("is_group", False)),
            )
            for item in data.get("messages") or []
        ]

        response = WhatsAppResponse(
            success=bool(data.get("success", False)),
            message_id=data.get("message_id"),
            messages=messages,
            requires_qr=bool(data.get("requires_qr", False)),
            error=data.get("error"),
        )
        return response

    def send_message(
        self,
        recipient: str,
        message: str,
        wait_for_response: bool = False,
    ) -> WhatsAppResponse:
        if not recipient:
            raise ValueError("recipient is required")
        if message is None or message == "":
            raise ValueError("message text is required")

        config = {
            "recipient": str(recipient),
            "message": str(message),
            "wait_for_response": bool(wait_for_response),
        }
        return self._call_library(config)

    def connect(self) -> WhatsAppResponse:
        return self._call_library({"connect_only": True})

    def receive_messages(self, duration: int = 10) -> WhatsAppResponse:
        if duration is None:
            duration = self.timeout
        config = {
            "receive_only": True,
            "timeout": max(int(duration), 0),
        }
        return self._call_library(config)

    def is_authenticated(self) -> bool:
        original_show_qr = self.show_qr
        original_timeout = self.timeout
        try:
            self.show_qr = False
            self.timeout = min(original_timeout, 5) if original_timeout else 5
            response = self.connect()
        finally:
            self.show_qr = original_show_qr
            self.timeout = original_timeout
        return response.success and not response.requires_qr

    def __enter__(self) -> "WhatsAppClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        return False


def load_library(lib_path: Optional[Path | str] = None) -> ctypes.CDLL:
    """Return the ctypes handle for the WhatsApp bridge library."""
    path = _resolve_library_path(lib_path)
    return ctypes.CDLL(str(path))


def _resolve_library_path(candidate: Optional[Path | str]) -> Path:
    if candidate is not None:
        return Path(candidate).expanduser().resolve()

    env_override = os.getenv("WA_LIB_PATH")
    if env_override:
        return Path(env_override).expanduser().resolve()

    packaged = _packaged_library_path()
    if packaged is not None:
        return packaged

    repo_fallback = _repo_dist_path()
    if repo_fallback is not None:
        return repo_fallback

    raise LibraryLoadError("Unable to locate libwa shared library")


def _packaged_library_path() -> Optional[Path]:
    name = _default_library_name()
    try:
        lib_root = resources.files(__name__).joinpath("lib")
    except AttributeError:  # pragma: no cover - defensive
        return None

    candidate = lib_root / name
    if candidate.is_file():
        return Path(candidate)
    return None


def _repo_dist_path() -> Optional[Path]:
    """Fallback to the repository's dist/ directory (useful during development)."""
    name = _default_library_name()
    repo_root = Path(__file__).resolve().parents[3]
    candidate = repo_root / "dist" / name
    if candidate.is_file():
        return candidate
    return None


def _default_library_name() -> str:
    system = platform.system()
    try:
        extension = _LIB_EXTENSIONS[system]
    except KeyError as exc:  # pragma: no cover - defensive
        raise LibraryLoadError(f"Unsupported platform: {system!r}") from exc
    return f"libwa{extension}"
