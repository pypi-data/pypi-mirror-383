from logging import getLogger, Logger

from binance.apis import (
    RestAPIGetters,
    WapiAPIGetters
)

from aioretry import RetryPolicy

from binance.subscribe.manager import SubscriptionManager
from binance.common.constants import (
    REST_API_HOST,
    STREAM_HOST,
    DEFAULT_RETRY_POLICY, DEFAULT_STREAM_TIMEOUT
)
from binance.common.types import Timeout

from .base import ClientBase


class Client(
    ClientBase,
    RestAPIGetters,
    WapiAPIGetters,
    SubscriptionManager
):
    def __init__(
        self,
        api_key=None,
        api_secret=None,
        request_params=None,
        # so that you can change api_host for CN network
        api_host: str = REST_API_HOST,
        # website_host=WEBSITE_HOST,
        stream_host: str = STREAM_HOST,
        stream_retry_policy: RetryPolicy = DEFAULT_RETRY_POLICY,
        stream_timeout: Timeout = DEFAULT_STREAM_TIMEOUT,
        logger: Logger = getLogger(__name__)
    ):
        """Binance API Client constructor

        Args:
            api_key (str): API Key
            api_secret (str): API Secret
            requests_params (:obj:`dict`, optional): Dictionary of requests params to use for all calls
        """

        self._api_key = None
        self._api_secret = None

        self.key(api_key)
        self.secret(api_secret)

        self._request_params = request_params
        self._api_host = api_host

        self._stream_host = stream_host
        self._stream_retry_policy = stream_retry_policy
        self._stream_timeout = stream_timeout

        self._receiving = True
        self._handler_ctx = None
        self._data_stream = None
        self._subscribed = set()
        self._logger = logger

    @property
    def logger(self) -> Logger:
        return self._logger

    def key(self, key):
        """Defines or changes api key. This method is unnecessary if we only request APIs of `SecurityType.NONE`

        Args:
            key (str): api key

        Returns:
            self
        """

        if key:
            self._api_key = key
        return self

    def secret(self, secret):
        """Defines or changes api secret, especially when we have not define api secret in Client constructor.

        `secret` is not always required for using binance-sdk.

        Args:
            secret (str): api secret

        Returns:
            self
        """

        if secret:
            self._api_secret = secret
        return self
