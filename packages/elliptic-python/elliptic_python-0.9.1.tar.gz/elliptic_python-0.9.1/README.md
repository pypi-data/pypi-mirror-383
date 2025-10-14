# Elliptic SDK for Python

## Installation

The SDK is available on PyPI:

``` shell
python -m pip install elliptic-python
```

This package requires Python 3.7 or greater

## Usage

The SDK provides an instance of the popular [Requests
package](https://requests.readthedocs.io/en/latest/), adding the
necessary steps to authenticate each request using your Elliptic API key
and secret.

``` python
from elliptic import AML

aml = AML(key="YOUR_ELLIPTIC_API_KEY", secret="YOUR_ELLIPTIC_API_SECRET")

# aml.client is an instance of a requests session
response = aml.client.get("/v2/analyses")
```

## Webhook Signature Verification

Elliptic signs the webhook events it sends to your endpoint, allowing
you to validate that they were not sent by a third-party. You can use
the `WebhookRequestVerifier` class to verify the signature of a webhook
request:

``` python
from http.server import HTTPServer, BaseHTTPRequestHandler
from elliptic import WebhookRequestVerifier

verifier = WebhookRequestVerifier(
    trusted_public_key="<Trusted public key, available from the Elliptic docs>",
    expected_endpoint_id="<Your endpoint id - this will be provided when your webhook integration is set up by Elliptic>",
)

class SimpleHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))

            post_data = self.rfile.read(content_length)
            params = {
                "webhook_id_header": self.headers.get("webhook-id"),
                "webhook_timestamp_header": self.headers.get(
                    "webhook-timestamp"
                ),
                "webhook_signature_header": self.headers.get(
                    "webhook-signature"
                ),
                "req_body": post_data,
            }
            message_id = verifier.verify(params)
            print("Verification successful, message ID:", message_id)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Webhook received")
        except Exception as e:
            print("Verification failed:", e)
            self.send_response(401)
            self.end_headers()


def run(port=1337):
    server_address = ("", port)
    httpd = HTTPServer(server_address, SimpleHandler)
    print(f"Starting server on port {port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
```

## API Documentation

Documentation for Elliptic APIs can be found at the [Elliptic Developer Center](https://developers.elliptic.co)

## License
This SDK is distributed under the Apache License, Version 2.0, see LICENSE and NOTICE for more information.