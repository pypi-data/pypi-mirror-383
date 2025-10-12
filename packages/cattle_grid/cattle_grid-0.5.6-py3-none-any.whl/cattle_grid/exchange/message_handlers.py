import logging

from cattle_grid.activity_pub.enqueuer import determine_activity_type
from cattle_grid.dependencies import InternalExchangePublisher
from cattle_grid.dependencies.internals import Transformer
from cattle_grid.model import ActivityMessage, FetchMessage


logger = logging.getLogger(__name__)


async def send_message(
    msg: ActivityMessage,
    publisher: InternalExchangePublisher,
) -> None:
    """Takes a message and ensure it is distributed appropriately"""

    content = msg.data
    activity_type = determine_activity_type(content)

    if not activity_type:
        return

    to_send = ActivityMessage(actor=msg.actor, data=content)

    await publisher(
        to_send,
        routing_key=f"outgoing.{activity_type}",
    )


async def fetch_object(msg: FetchMessage, publisher: InternalExchangePublisher) -> dict:
    """Used to fetch an object as an RPC method"""
    result = await publisher(
        msg,
        routing_key="fetch_object",
        rpc=True,
    )
    if result == b"" or result is None:
        return {}
    return result


async def fetch(
    msg: FetchMessage, publisher: InternalExchangePublisher, transformer: Transformer
) -> dict:
    """Used to fetch an object as an RPC method. In difference to `fetch_object`,
    this method applies the transformer."""
    result = await publisher(
        msg,
        routing_key="fetch_object",
        rpc=True,
    )
    if result == b"" or result is None:
        return {}

    transformed = await transformer({"raw": result})
    return transformed
