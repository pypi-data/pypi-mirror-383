import pytest

from binance import (
    Client,
    TickerHandlerBase,
    ReuseHandlerException,

    KlineHandlerBase,
    AccountInfoHandlerBase,
    AccountPositionHandlerBase,
    BalanceUpdateHandlerBase,
    OrderUpdateHandlerBase,
    OrderListStatusHandlerBase,
    AllMarketMiniTickersHandlerBase,
    AllMarketTickersHandlerBase
)
from binance.common.utils import create_future

from .common import ACCOUNT_INFO


@pytest.fixture
def client():
    return Client('api_key').start()


ACCOUNT_POSITION = {
    'e': 'outboundAccountPosition',
    'E': 1564034571105,
    'u': 1564034571073,
    'B': [
        {
            'a': 'ETH',
            'f': '10000.000000',
            'l': '0.000000'
        }
    ]
}


async def run_handler(
    client,
    HandlerBase,
    payload,
    expect_payload=None,
    stream='fake'
):
    future = create_future()

    if expect_payload is None:
        expect_payload = payload

    class Handler(HandlerBase):
        def receive(self, p):
            p = super().receive(p)

            if future.done():
                return
            future.set_result(p)

    client.start()
    client.handler(Handler())

    await client._receive({
        'data': ACCOUNT_POSITION,
        'stream': 'fake'
    })

    await client._receive({
        'data': payload,
        'stream': stream
    })

    await client._receive([])
    await client._receive({})

    received = await future

    if callable(expect_payload):
        expect_payload(received)
    else:
        assert received == expect_payload


@pytest.mark.asyncio
async def test_account_info(client):
    await run_handler(client, AccountInfoHandlerBase, ACCOUNT_INFO)


@pytest.mark.asyncio
async def test_account_pos(client):
    await run_handler(client, AccountPositionHandlerBase, ACCOUNT_POSITION)


@pytest.mark.asyncio
async def test_balance_update(client):
    await run_handler(client, BalanceUpdateHandlerBase, {
        'e': 'balanceUpdate',
        'E': 1573200697110,
        'a': 'BTC',
        'd': '100.00000000',
        'T': 1573200697068
    })


@pytest.mark.asyncio
async def test_order_update(client):
    await run_handler(client, OrderUpdateHandlerBase, {
        'e': 'executionReport',
        'E': 1499405658658,
        's': 'ETHBTC',
        'c': 'mUvoqJxFIILMdfAW5iGSOW',
        'S': 'BUY',
        'o': 'LIMIT'
    })


@pytest.mark.asyncio
async def test_order_list_status(client):
    await run_handler(client, OrderListStatusHandlerBase, {
        'e': 'listStatus',
        'E': 1564035303637,
        's': 'ETHBTC',
        'g': 2,
        'c': 'OCO',
        'l': 'EXEC_STARTED',
        'L': 'EXECUTING'
    })


@pytest.mark.asyncio
async def test_kline_handler(client):
    E = 123456789

    k = {
        't': 123400000,
        'T': 123460000,
        's': 'BNBBTC',
        'i': '1m',
        'f': 100,
        'L': 200,
        'o': '0.0010',
        'c': '0.0020'
    }

    payload = {
        'e': 'kline',
        'E': 123456789,
        's': 'BNBBTC',
        'k': k
    }

    def expect(received):
        row = received.iloc[0]
        assert row['symbol'] == 'BNBBTC'
        assert row['event_time'] == E

    await run_handler(client, KlineHandlerBase, payload, expect)


def expect_ticker(payload):
    row = payload.iloc[0]
    assert row['symbol'] == 'BNBBTC'
    assert row['event_time'] == 123456789


@pytest.mark.asyncio
async def test_all_market_miniticker(client):
    ticker = {
        'e': '24hrMiniTicker',
        'E': 123456789,
        's': 'BNBBTC',
        'c': '0.0025',
        'o': '0.0010',
        'h': '0.0025',
        'l': '0.0010',
        'v': '10000',
        'q': '18'
    }

    await run_handler(client, AllMarketMiniTickersHandlerBase, [
        ticker
    ], expect_ticker, '!miniTicker@arr')


@pytest.mark.asyncio
async def test_all_market_ticker(client):
    ticker = {
        'e': '24hrTicker',
        'E': 123456789,
        's': 'BNBBTC',
        'p': '0.0015',
        'P': '250.00',
        'w': '0.0018',
        'x': '0.0009',
        'c': '0.0025',
        'Q': '10',
        'b': '0.0024',
        'B': '10',
        'a': '0.0026',
        'A': '100',
        'o': '0.0010',
        'h': '0.0025',
        'l': '0.0010',
        'v': '10000',
        'q': '18',
        'O': 0,
        'C': 86400000,
        'F': 0,
        'L': 18150,
        'n': 18151
    }

    await run_handler(client, AllMarketTickersHandlerBase, [
        ticker
    ], expect_ticker, '!ticker@arr')


def test_handler_reuse():
    client = Client('api_key')
    client2 = Client('api_key')

    handler = TickerHandlerBase()

    with pytest.raises(ReuseHandlerException, match='more than one'):
        client.handler(handler)
        client2.handler(handler)
