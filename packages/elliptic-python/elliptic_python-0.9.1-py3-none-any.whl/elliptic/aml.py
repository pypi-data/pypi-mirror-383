from .client import Client


class AML:
    '''
    An HMAC client that defaults to the Elliptic AML API host
    '''

    def __init__(
        self,
        key: str,
        secret: str,
        base_url: str = "https://aml-api.elliptic.co",
        *args,
        **kwargs,
    ):
        '''
        Arguments
        ---------

        key      - your Elliptic API key
        secret   - your Elliptic API secret
        base_url - hostname of Elliptic API
                   (default https://aml-api.elliptic.co)
        '''

        super().__init__(*args, **kwargs)

        self.client = Client(key, secret, base_url)
