from requests import Session
from urllib.parse import urljoin
from .hmac import HMACAuth


class Client(Session):
    '''
    Generic requests client using HMAC as required by Elliptic
    '''

    def __init__(self, key: str, secret: str, base_url: str, *args, **kwargs):
        '''
        Arguments
        ---------

        key      - your Elliptic API key
        secret   - your Elliptic API secret
        base_url - hostname of Elliptic API
        '''
        super().__init__(*args, **kwargs)

        self.auth = HMACAuth(key, secret)
        self.base_url = base_url

    def request(self, method, url, *args, **kwargs):
        joined_url = urljoin(self.base_url, url)
        return super().request(method, joined_url, *args, **kwargs)
