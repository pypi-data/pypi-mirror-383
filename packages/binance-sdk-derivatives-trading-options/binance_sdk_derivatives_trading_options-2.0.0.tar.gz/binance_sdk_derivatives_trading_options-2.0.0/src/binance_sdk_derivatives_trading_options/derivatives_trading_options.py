import platform
from importlib.metadata import version

from binance_common.configuration import (
    ConfigurationRestAPI,
    ConfigurationWebSocketStreams,
)
from binance_common.constants import (
    DERIVATIVES_TRADING_OPTIONS_REST_API_PROD_URL,
    DERIVATIVES_TRADING_OPTIONS_WS_STREAMS_PROD_URL,
)
from . import metadata
from .rest_api import DerivativesTradingOptionsRestAPI
from .websocket_streams import DerivativesTradingOptionsWebSocketStreams

LIB_NAME = metadata.NAME
LIB_VERSION = version(LIB_NAME)


class DerivativesTradingOptions:
    """DerivativesTradingOptions API that exposes REST, and Stream APIs in a single interface."""

    def __init__(
        self,
        config_rest_api: ConfigurationRestAPI = None,
        config_ws_streams: ConfigurationWebSocketStreams = None,
    ) -> None:
        self._rest_api = None
        self._rest_api_config = (
            ConfigurationRestAPI() if config_rest_api is None else config_rest_api
        )
        self._websocket_streams = None
        self._websocket_streams_config = (
            ConfigurationWebSocketStreams()
            if config_ws_streams is None
            else config_ws_streams
        )

    @property
    def rest_api(self) -> DerivativesTradingOptionsRestAPI:
        if self._rest_api is None and self._rest_api_config:
            self._rest_api_config.base_headers["User-Agent"] = (
                f"{LIB_NAME}/{LIB_VERSION} (Python/{platform.python_version()}; {platform.system()}; {platform.machine()})"
            )
            self._rest_api_config.base_path = (
                DERIVATIVES_TRADING_OPTIONS_REST_API_PROD_URL
                if self._rest_api_config.base_path is None
                else self._rest_api_config.base_path
            )
            self._rest_api = DerivativesTradingOptionsRestAPI(self._rest_api_config)
        return self._rest_api

    @property
    def websocket_streams(self) -> DerivativesTradingOptionsWebSocketStreams:
        if self._websocket_streams is None and self._websocket_streams_config:
            self._websocket_streams_config.user_agent = f"{LIB_NAME}/{LIB_VERSION} (Python/{platform.python_version()}; {platform.system()}; {platform.machine()})"
            self._websocket_streams_config.stream_url = (
                DERIVATIVES_TRADING_OPTIONS_WS_STREAMS_PROD_URL
                if self._websocket_streams_config.stream_url is None
                else self._websocket_streams_config.stream_url
            )
            self._websocket_streams = DerivativesTradingOptionsWebSocketStreams(
                self._websocket_streams_config
            )

        return self._websocket_streams
