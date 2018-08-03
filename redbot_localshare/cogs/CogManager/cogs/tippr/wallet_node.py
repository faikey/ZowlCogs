import aiohttp
import asyncio
from jsonrpcclient.aiohttp_client import aiohttpClient
from jsonrpcclient import config

__all__ = ['initialize', 'get_new_address', 'get_received_by_account',
           'json_to_amount', 'amount_to_json']

_session = None  # type: aiohttp.ClientSession
_node_client = None  # type: aiohttpClient

config.validate = False


async def initialize(loop: asyncio.BaseEventLoop, *,
                     host: str=None, port: int=None,
                     username: str=None, password: str=None):
    """
    Initializes the wallet node client.

    Parameters
    ----------
    loop
        Event loop to use to connect to wallet node.
    host : str
        IP address of the wallet node (probably 127.0.0.1)
    port : int
        Port of the JSON-RPC server on the wallet (probably 8332)
    username : str
        Username to connect to the JSON-RPC server.
    password : str
        Password to connect to the JSON-RPC server.

    Raises
    ------
    RuntimeError
        If any of host, port, user, password are not supplied.

    LookupError
        If the host could not be found.

    Returns
    -------
    dict
        Status info of the wallet node.
    """
    if None in (host, port, username, password):
        raise RuntimeError

    global _session
    global _node_client

    _session = aiohttp.ClientSession(loop=loop)

    addr = "http://{}:{}@{}:{}".format(
        username, password, host, port
    )

    _node_client = aiohttpClient(_session, addr)

    try:
        return await _node_client.request("getinfo")
    except aiohttp.client_exceptions.ClientConnectorError as e:
        raise LookupError from e


def _ensure_initialized(func):
    async def pred(*args, **kwargs):
        if _node_client is None:
            raise RuntimeError("Wallet client has not been initialized.")
        return await func(*args, **kwargs)
    return pred


def json_to_amount(value: float) -> int:
    """
    Converts the BTC value returned from the JSON-RPC API
    into "Satoshis". 1 BTC == 1e8 Satoshi

    Internally this is an integer and is necessary to prevent
    floating point rounding issues.

    Parameters
    ----------
    value : float
        Floating point value returned by the JSON-RPC API.

    Returns
    -------
    int
        Amount in Satoshis
    """
    return int(round(1e8 * value))


def amount_to_json(value: int) -> float:
    """
    Does the opposite conversion of ``json_to_amount``.

    Parameters
    ----------
    value : int
        BTC value in Satoshis

    Returns
    -------
    float
        BTC value suitable for the JSON-RPC API.
    """
    return float(value / 1e8)


@_ensure_initialized
async def get_new_address(uuid: str) -> str:
    """
    Get's a new BTC address from the wallet node.

    Parameters
    ----------
    uuid : str
        This is used to create or add to a give account within
        the bitcoin wallet. This is necessary because "move"
        only works with different accounts. This should be the
        discord user ID 99% of the time.

    Returns
    -------
    str
        New BTC address.
    """
    return await _node_client.request("getnewaddress", uuid)


@_ensure_initialized
async def get_received_by_account(account: str) -> int:
    """
    Gets the amount of BTC available in a wallet account.

    Parameters
    ----------
    account : str
        Local bitcoin address.

    Returns
    -------
    int
        Available satoshis in wallet.
    """
    raw_value = await _node_client.request(
        "getreceivedbyaccount", account)

    return json_to_amount(raw_value)


@_ensure_initialized
async def move(from_uuid: str, to_uuid: str, amount: int):
    """
    Moves ``amount`` from one account to another. This does
    *NOT* do amount validation.

    Parameters
    ----------
    from_uuid : str
        UUID of the account to move BTC from.
    to_uuid : str
        UUID of the account to move BTC to.
    amount : int
        Amount, in satoshis, to move.
    """
    await _node_client.request(
        "move",
        from_uuid, to_uuid, amount_to_json(amount)
    )
