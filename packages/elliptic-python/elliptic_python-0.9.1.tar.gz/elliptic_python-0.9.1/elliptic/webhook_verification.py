import base64
import re
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature
from datetime import datetime, timezone
import uuid

# Constants
ASYMMETRIC_SIGNATURE_PREFIX = "v1a,"
PUBLIC_KEY_PREFIX = "whpk_"

UUID_REGEX = "[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}"
WEBHOOK_ID_REGEX = re.compile(
    f"^messageId_({UUID_REGEX})_endpointId_({UUID_REGEX})$"
)
TIMESTAMP_TOLERANCE_SECONDS = 5 * 60


def parse_webhook_id_header(webhook_id):
    if webhook_id is None:
        raise ValueError("expected webhook_id_header to be a string")
    match = WEBHOOK_ID_REGEX.match(webhook_id)
    if match is None:
        raise ValueError("Invalid format for webhook_id_header")
    message_id, endpoint_id = match.groups()
    return message_id, endpoint_id


def verify_endpoint_id(endpoint_id, expected_endpoint_id):
    if isinstance(expected_endpoint_id, uuid.UUID):
        expected_endpoint_id = str(expected_endpoint_id)

    if not isinstance(endpoint_id, str):
        raise TypeError("endpoint_id must be a string.")

    if endpoint_id != expected_endpoint_id:
        raise ValueError("Invalid endpoint id")


def verify_timestamp(webhook_timestamp_header):
    if webhook_timestamp_header is None:
        raise ValueError("expected webhook_timestamp_header to be a string")

    try:
        timestamp_seconds = int(webhook_timestamp_header)
    except ValueError:
        raise ValueError("Invalid timestamp")

    now_seconds = int(datetime.now(tz=timezone.utc).timestamp())
    difference = abs(timestamp_seconds - now_seconds)
    if difference >= TIMESTAMP_TOLERANCE_SECONDS:
        raise ValueError("Invalid timestamp")


class WebhookRequestVerifier:
    def __init__(self, trusted_public_key: str, expected_endpoint_id: str):
        if not isinstance(trusted_public_key, str):
            raise ValueError("Invalid public key - expected string.")
        if not trusted_public_key.startswith(PUBLIC_KEY_PREFIX):
            raise ValueError(
                "Invalid public key format - "
                + f"expected public key to start with {PUBLIC_KEY_PREFIX}"
            )
        if not isinstance(expected_endpoint_id, str):
            raise ValueError("Invalid endpoint id - expected string.")
        try:
            uuid.UUID(expected_endpoint_id)
        except ValueError:
            raise ValueError("Invalid endpoint id - expected UUID.")

        # Extract the raw bytes from the public key
        trusted_public_key = base64.b64decode(
            trusted_public_key[len(PUBLIC_KEY_PREFIX):]
        )

        # Load the public key from raw bytes
        self.trusted_public_key = Ed25519PublicKey.from_public_bytes(
            trusted_public_key
        )
        self.expected_endpoint_id = expected_endpoint_id

    def verify_signature(
        self,
        req_body: bytes,
        webhook_id_header: str,
        webhook_timestamp_header: str,
        webhook_signature_header: str,
    ):
        dot = b"."  # Equivalent to Buffer.from(".", "ascii")

        # Concatenate the parts of the data buffer as bytes
        data_buffer = (
            webhook_id_header.encode("ascii")
            + dot
            + webhook_timestamp_header.encode("ascii")
            + dot
            + req_body
        )

        if webhook_signature_header is None:
            raise ValueError(
                "expected webhook_signature_header to be a string"
            )

        if not webhook_signature_header.startswith(
            ASYMMETRIC_SIGNATURE_PREFIX
        ):
            raise ValueError(
                "Invalid signature identifier - should start with "
                f"{ASYMMETRIC_SIGNATURE_PREFIX}"
            )

        sig_values_str = webhook_signature_header[
            len(ASYMMETRIC_SIGNATURE_PREFIX):
        ]
        sig_values = sig_values_str.split(" ")
        sig_buffers = [base64.b64decode(sig_value) for sig_value in sig_values]

        # Attempt to verify each signature
        for sig in sig_buffers:
            try:
                # Directly use the Ed25519 public key's verify method
                self.trusted_public_key.verify(signature=sig, data=data_buffer)
                return  # Successful verification exits the function
            except InvalidSignature:
                continue  # Try next signature if current fails

        raise ValueError("No valid signatures found")

    def verify(self, options: dict) -> str:
        req_body = options.get("req_body")
        webhook_id_header = options.get("webhook_id_header")
        webhook_timestamp_header = options.get("webhook_timestamp_header")
        webhook_signature_header = options.get("webhook_signature_header")
        message_id, endpoint_id = parse_webhook_id_header(webhook_id_header)
        verify_endpoint_id(endpoint_id, self.expected_endpoint_id)
        verify_timestamp(webhook_timestamp_header)
        self.verify_signature(
            req_body,
            webhook_id_header,
            webhook_timestamp_header,
            webhook_signature_header,
        )
        return message_id
