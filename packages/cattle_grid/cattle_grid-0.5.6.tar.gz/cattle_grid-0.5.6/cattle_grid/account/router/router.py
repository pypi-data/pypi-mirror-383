import asyncio
import logging
from faststream.rabbit import RabbitRouter, RabbitQueue

from cattle_grid.activity_pub.actor import (
    create_actor,
    actor_to_object,
)

from cattle_grid.model.account import (
    FetchMessage,
    FetchResponse,
    InformationResponse,
    CreateActorRequest,
)
from cattle_grid.account.permissions import can_create_actor_at_base_url
from cattle_grid.database.account import ActorForAccount
from cattle_grid.dependencies import (
    AccountExchangePublisher,
    InternalExchangePublisher,
    SqlSession,
)
from cattle_grid.dependencies.internals import MethodInformation
from cattle_grid.dependencies.globals import global_container

from .info import create_information_response
from .annotations import (
    AccountName,
    AccountFromRoutingKey,
    ActorFromMessage,
)
from .exception import exception_middleware
from .trigger import handle_trigger

logger = logging.getLogger(__name__)


async def handle_fetch(
    msg: FetchMessage,
    name: AccountName,
    actor: ActorFromMessage,
    publisher: AccountExchangePublisher,
    internal_publisher: InternalExchangePublisher,
):
    """Used to retrieve an object"""
    try:
        async with asyncio.timeout(0.5):
            result = await internal_publisher(
                {"actor": actor.actor_id, "uri": msg.uri},
                routing_key="fetch_object",
                rpc=True,
            )
        if result == b"":
            result = None
        logger.info("GOT result %s", result)
    except TimeoutError as e:
        logger.error("Request ran into timeout %s", e)
        result = None

    if result:
        await publisher(
            FetchResponse(
                uri=msg.uri,
                actor=actor.actor_id,
                data=result,
            ),
            routing_key=f"receive.{name}.response.fetch",
        )
    else:
        await publisher(
            {
                "message": f"Could not fetch object: {msg.uri}",
            },
            routing_key=f"error.{name}",
        )


async def create_actor_handler(
    create_message: CreateActorRequest,
    account: AccountFromRoutingKey,
    session: SqlSession,
    publisher: AccountExchangePublisher,
) -> None:
    """Creates an actor associated with the account.

    Updating and deleting actors is done through trigger events."""

    if not await can_create_actor_at_base_url(
        session, account, create_message.base_url
    ):
        raise ValueError(f"Base URL {create_message.base_url} not in allowed base urls")

    actor = await create_actor(
        session,
        create_message.base_url,
        preferred_username=create_message.preferred_username,
        profile=create_message.profile,
    )

    session.add(
        ActorForAccount(
            account=account,
            actor=actor.actor_id,
            name=create_message.name or "from drive",
        )
    )

    if create_message.automatically_accept_followers:
        actor.automatically_accept_followers = True

    result = actor_to_object(actor)

    await session.refresh(account)

    logger.info("Created actor %s for %s", actor.actor_id, account.name)

    await publisher(
        result,
        routing_key=f"receive.{account.name}.response.create_actor",
    )
    await session.commit()


def create_router() -> RabbitRouter:
    router = RabbitRouter(middlewares=[exception_middleware])

    router.publisher(
        "receive.name.response.fetch",
        schema=FetchResponse,
        title="receive.NAME.response.fetch",
    )

    router.subscriber(
        RabbitQueue(
            "send_request_fetch", routing_key="send.*.request.fetch", durable=True
        ),
        exchange=global_container.account_exchange,
        title="send.*.request.fetch",
    )(handle_fetch)

    router.publisher(
        "receive.name.response.info",
        schema=InformationResponse,
        title="receive.NAME.response.info",
    )

    @router.subscriber(
        RabbitQueue(
            "send_request_info", routing_key="send.*.request.info", durable=True
        ),
        exchange=global_container.account_exchange,
        title="send.*.request.info",
    )
    async def information_request_handler(
        account: AccountFromRoutingKey,
        method_information: MethodInformation,
        session: SqlSession,
        publisher: AccountExchangePublisher,
    ) -> None:
        """Provides information about the underlying service"""
        await publisher(
            await create_information_response(session, account, method_information),
            routing_key=f"receive.{account.name}.response.info",
        )

    router.publisher(
        "receive.name.response.create_actor",
        schema=dict,
        title="receive.NAME.response.create_actor",
        description="""The response to a create_actor request
    is the actor profile (as formatted towards the Fediverse)
    This might change in the future""",
    )

    router.subscriber(
        RabbitQueue(
            "send_request_create_actor",
            routing_key="send.*.request.create_actor",
            durable=True,
        ),
        exchange=global_container.account_exchange,
        title="send.*.request.create_actor",
    )(create_actor_handler)

    router.subscriber(
        RabbitQueue("send_trigger", routing_key="send.*.trigger.#", durable=True),
        exchange=global_container.account_exchange,
        title="send.*.trigger.#",
    )(handle_trigger)

    return router
