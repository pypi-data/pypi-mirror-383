"""The pysqueezebox server discovery module."""

import asyncio
import logging
import socket
from typing import Any, Awaitable, Callable

from aiohttp import ClientSession

from .server import Server

_LOGGER = logging.getLogger(__name__)

DISCOVERY_INTERVAL = 60  # default value from Logitech Media Server code
DISCOVERY_MESSAGE = b"eIPAD\x00NAME\x00JSON\x00UUID\x00VERS"
BROADCAST_ADDR = ("255.255.255.255", 3483)


def _unpack_discovery_response(
    data: bytes, addr: tuple[str | Any, int]
) -> dict[str, str] | None:
    """Return dict of unpacked responses from Logitech Media Server."""
    if data[0:1] != b"E":
        _LOGGER.debug(
            "Received non-LMS discovery response %s from %s",
            data,
            addr,
        )
        _LOGGER.debug("Prefix was %s", data[0:1])
        return None
    data = data[1::]  # drop first byte
    result = {"host": addr[0]}
    while len(data) > 0:
        tag = data[0:4].decode().lower()
        tag_len = ord(data[4:5])  # unsigned char
        val = data[5 : (5 + tag_len)].decode()
        data = data[5 + tag_len : :]  # drop this unpacked response
        result.update({tag: val})
    return result


class ServerDiscoveryProtocol(asyncio.DatagramProtocol):
    """Protocol to send discovery request and receive responses."""

    def __init__(
        self,
        callback: Awaitable[None] | Callable[[Server], None],
        session: ClientSession | None = None,
    ) -> None:
        """Initialize with callback function."""
        self.transport: asyncio.transports.BaseTransport | None = None
        self.callback = callback
        self.session = session

    def connection_made(self, transport: asyncio.transports.BaseTransport) -> None:
        """Connect to transport."""
        self.transport = transport

    def datagram_received(self, data: bytes, addr: tuple[str | Any, int]) -> None:
        """Test if responder is a Logitech Media Server."""
        _LOGGER.debug("Received LMS discovery response from %s", addr)
        response = _unpack_discovery_response(data, addr)
        _LOGGER.debug("LMS discovery response: %s", response)
        if response:
            if "host" not in response or "json" not in response:
                _LOGGER.debug(
                    "LMS discovery response %s does not contain enough information to connect",
                    response,
                )
            elif response.get("uuid") == "slimproto":
                # Discovered server is Home Assistant SlimProto
                _LOGGER.debug(
                    "Ignoring Home Assistant SlimProto server discovered at %s",
                    response.get("host"),
                )
            elif callable(self.callback):
                result = self.callback(
                    Server(
                        self.session,
                        response["host"],
                        int(response["json"]),
                        name=response.get("name"),
                        uuid=response.get("uuid"),
                    )
                )
                if asyncio.iscoroutine(result):
                    asyncio.create_task(result)


async def async_discover(
    callback: Awaitable[None] | Callable[[Server], None],
    session: ClientSession | None = None,
) -> None:
    """
    Search for Logitech Media Servers using the LMS UDP discovery protocol.

    Will search indefinitely. To stop searching, call Task.cancel().

    Parameters:
        callback: awaitable or synchronous function to call with Server object
                  containing discovered server (required)
        session:  aiohttp.ClientSession for connecting to server (recommended,
                  but can be left blank and set by callback instead)
    """
    loop = asyncio.get_running_loop()

    # for python3.7 compatability, we must create our own socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    transport, _ = await loop.create_datagram_endpoint(
        lambda: ServerDiscoveryProtocol(callback, session),
        sock=sock,
    )

    try:
        while True:
            _LOGGER.debug("Sending discovery message.")
            transport.sendto(DISCOVERY_MESSAGE, BROADCAST_ADDR)
            await asyncio.sleep(DISCOVERY_INTERVAL)

    except asyncio.CancelledError:
        _LOGGER.debug("Cancelling LMS discovery task")
        transport.close()

    finally:
        transport.close()
