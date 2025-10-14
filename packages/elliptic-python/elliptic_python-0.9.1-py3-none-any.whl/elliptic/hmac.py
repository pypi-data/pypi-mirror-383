import json
import time
from requests.auth import AuthBase
from requests import PreparedRequest
from .sign import sign

JSON_SEPERATORS = (',', ':')


class HMACAuth(AuthBase):
    '''
    An authenticator to add HMAC signature to requests
    '''

    def __init__(self, key, secret):
        self.api_key = key
        self.secret_key = secret

    def format_payload(self, body: bytes) -> str:
        '''
        Takes an optional request body and returns a JSON encoded string
        with unnecessary whitespace removed, and compatiable with Elliptic's
        request signing process
        '''
        original_string = body.decode('utf-8')
        json_decoded = json.loads(original_string)
        return json.dumps(json_decoded, separators=JSON_SEPERATORS)

    def __call__(self, request: PreparedRequest) -> PreparedRequest:
        version = "0.9.1"
        timestamp = str(int(round(time.time() * 1000)))
        payload = self.format_payload(request.body or b"{}")
        signature = sign(
            self.secret_key,
            timestamp,
            request.method,
            request.path_url,
            payload,
        )

        request.headers.update(
            {
                "x-access-key": self.api_key,
                "x-access-timestamp": timestamp,
                "x-access-sign": signature,
                "x-client-name": "elliptic-sdk-python",
                "x-client-version": version,
            }
        )

        return request
