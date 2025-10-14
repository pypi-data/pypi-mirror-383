"""
This module provides an SDK to assist in making requests to the Elliptic APIs

FUNCTIONS:
    AML:
        The AML function provides a configured Session from the requests
        package (https://pypi.org/project/requests/). It must be provided
        with your Elliptic API key and secret, and the client attribute
        on the returned instance holds the configured session, which
        can be called using the regular requests methods.

        Example:

        from elliptic import AML

        aml = AML(
            key="YOUR_ELLIPTIC_API_KEY",
            secret="YOUR_ELLIPTIC_API_SECRET",
        )

        # aml.client is a requests session
        response = aml.client.get("/v2/analyses")

    WebhookRequestVerifier:
        The WebhookRequestVerifier class provides functionality to verify
        the signatures of incoming webhook requests. This is necessary
        to ensure that webhook events are securely sent from Elliptic.

        Example:

        from elliptic import WebhookRequestVerifier

        verifier = WebhookRequestVerifier(
            trusted_public_key="YOUR_TRUSTED_PUBLIC_KEY",
            expected_endpoint_id="YOUR_ENDPOINT_ID"
        )

     # Example payload
        payload = {
            'webhook_id_header': 'messageId_1234_endpointId_YOUR_ENDPOINT_ID',
            'webhook_timestamp_header': str(int(time.time())),
            'webhook_signature_header': 'v1a,valid_signature_here',
            'req_body': b'webhook_request_body'
        }

        try:
            # Verify the webhook request
            message_id = verifier.verify(payload)
            print('Verification successful, message ID:', message_id)
        except ValueError as e:
            print('Verification failed:', e)
"""
from .aml import AML
from .webhook_verification import WebhookRequestVerifier

__all__ = ['AML', 'WebhookRequestVerifier']
