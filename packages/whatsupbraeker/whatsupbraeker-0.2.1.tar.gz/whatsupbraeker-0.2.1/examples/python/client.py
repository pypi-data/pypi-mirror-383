#!/usr/bin/env python3
"""
Minimal example showing how to call the Go shared library directly via ctypes.
"""

from __future__ import annotations

import argparse
import ctypes
import json
import sys
from pathlib import Path
from typing import Any, Dict


def load_library(path: Path) -> ctypes.CDLL:
    lib = ctypes.CDLL(str(path))
    lib.WaRun.argtypes = [ctypes.c_char_p]
    lib.WaRun.restype = ctypes.c_void_p
    lib.WaFree.argtypes = [ctypes.c_void_p]
    lib.WaFree.restype = None
    return lib


def call_run(lib: ctypes.CDLL, config: Dict[str, Any]) -> Dict[str, Any]:
    payload = json.dumps(config, ensure_ascii=False).encode("utf-8")
    ptr = lib.WaRun(ctypes.c_char_p(payload))
    if not ptr:
        raise RuntimeError("library returned NULL pointer")

    try:
        raw = ctypes.string_at(ptr).decode("utf-8")
    finally:
        lib.WaFree(ptr)

    return json.loads(raw)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Direct ctypes example for libwa.so")
    parser.add_argument("--phone", required=True, help="Account phone number without '+'.")
    parser.add_argument("--recipient", help="Recipient phone number.")
    parser.add_argument("--message", help="Message text to send.")
    parser.add_argument("--connect", action="store_true", help="Only connect (useful for QR login).")
    parser.add_argument("--receive", type=int, metavar="SECONDS", help="Listen for messages for N seconds.")
    parser.add_argument("--timeout", type=int, default=30, help="Generic timeout in seconds (default: 30).")
    parser.add_argument("--db-uri", default="file:whatsapp.db?_foreign_keys=on", help="SQLite connection string.")
    parser.add_argument("--lib", default="../../dist/libwa.so", help="Path to libwa.so (default: ../../dist/libwa.so).")
    parser.add_argument("--no-qr", action="store_true", help="Do not print QR codes in the console.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    lib_path = Path(args.lib)
    if not lib_path.is_absolute():
        lib_path = (Path(__file__).resolve().parent / lib_path).resolve()
    if not lib_path.exists():
        print(f"Shared library not found: {lib_path}", file=sys.stderr)
        return 1

    if not args.connect and not args.receive and not (args.recipient and args.message):
        print("Specify --connect, --receive, or both --recipient and --message.", file=sys.stderr)
        return 1

    config: Dict[str, Any] = {
        "phone": args.phone,
        "db_uri": args.db_uri,
        "timeout": args.timeout,
        "show_qr": not args.no_qr,
    }

    if args.connect:
        config["connect_only"] = True
    if args.receive is not None:
        config["receive_only"] = True
        config["timeout"] = args.receive
    if args.recipient and args.message:
        config["recipient"] = args.recipient
        config["message"] = args.message

    try:
        lib = load_library(lib_path)
        response = call_run(lib, config)
    except Exception as exc:  # pragma: no cover - defensive
        print(f"Error calling library: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(response, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
