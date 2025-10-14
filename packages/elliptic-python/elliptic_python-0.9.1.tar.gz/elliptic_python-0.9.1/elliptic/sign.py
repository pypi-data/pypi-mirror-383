import base64
import hmac as crypto
import hashlib


def sign(secret, time_of_request, http_method, http_path, payload):
    '''
    Generates a SHA256 signature of a request for HMAC authentication
    '''
    hmac = crypto.new(base64.b64decode(secret), digestmod=hashlib.sha256)
    request_text = time_of_request + http_method + http_path.lower() + payload
    hmac.update(request_text.encode('UTF-8'))
    return base64.b64encode(hmac.digest()).decode('utf-8')
