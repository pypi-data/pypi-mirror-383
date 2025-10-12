"""Command-line interface for the WhatsUpBraeker client."""

from __future__ import annotations

import argparse
import os
import sys
from typing import List, Optional

from . import WhatsAppClient, WhatsAppMessage


def _format_messages(messages: List[WhatsAppMessage]) -> str:
    if not messages:
        return "No messages received."

    lines = []
    for item in messages:
        suffix = " (group)" if item.is_group else ""
        lines.append(f"- [{item.timestamp}] {item.from_jid}{suffix}: {item.text}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Interact with WhatsApp through the Go bridge.")
    parser.add_argument("--phone", required=True, help="Account phone number without '+'.")
    parser.add_argument("--lib", help="Path to libwa shared library.")
    parser.add_argument(
        "--db-uri",
        help="SQLite connection string (default: file:whatsapp.db?_foreign_keys=on).",
    )
    parser.add_argument("--timeout", type=int, default=30, help="Operation timeout in seconds (default: 30).")
    parser.add_argument("--no-qr", action="store_true", help="Do not print QR codes to the console.")
    parser.add_argument("--recipient", help="Recipient phone number.")
    parser.add_argument("--message", help="Text message to send.")
    parser.add_argument("--wait-for-response", action="store_true", help="Wait for replies after sending a message.")
    parser.add_argument("--connect", action="store_true", help="Only connect to WhatsApp (show QR if needed).")
    parser.add_argument(
        "--receive",
        type=int,
        metavar="SECONDS",
        help="Listen for incoming messages for the specified amount of seconds.",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    action_selected = any(
        [
            args.connect,
            args.receive is not None,
            args.recipient and args.message,
        ]
    )

    if not action_selected:
        parser.error("Specify --connect, --receive, or both --recipient and --message.")

    lib_path = args.lib or os.getenv("WA_LIB_PATH")

    try:
        with WhatsAppClient(
            phone=args.phone,
            lib_path=lib_path,
            db_uri=args.db_uri,
            timeout=args.timeout,
            show_qr=not args.no_qr,
        ) as client:
            if args.connect:
                response = client.connect()
                if response.success:
                    print("Connected to WhatsApp.")
                elif response.requires_qr:
                    print("Authentication required. Scan the QR code displayed in the console.")
                else:
                    print(f"Failed to connect: {response.error or 'unknown error'}", file=sys.stderr)
                    return 1

            if args.recipient and args.message:
                response = client.send_message(
                    recipient=args.recipient,
                    message=args.message,
                    wait_for_response=args.wait_for_response,
                )
                if response.success:
                    print(f"Message sent. ID: {response.message_id or '<unknown>'}")
                    if response.messages:
                        print("Incoming messages:")
                        print(_format_messages(response.messages))
                else:
                    print(f"Failed to send message: {response.error or 'unknown error'}", file=sys.stderr)
                    return 1

            if args.receive is not None:
                response = client.receive_messages(duration=args.receive)
                if response.success:
                    print("Incoming messages:")
                    print(_format_messages(response.messages))
                else:
                    print(f"Failed to receive messages: {response.error or 'unknown error'}", file=sys.stderr)
                    return 1

    except Exception as exc:  # pragma: no cover - defensive
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0
