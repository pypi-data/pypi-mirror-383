"""Dependencies injected by fast_depends

cattle_grid uses dependencies to manage objects, one needs access to.
This works by declaring them using [fast_depends.Depends][] and then
injecting them using [fast_depends.inject][].

For example if you want to make a webrequest using the
[aiohttp.ClientSession][], you could use

```python
from cattle_grid.dependencies import ClientSession

async def web_request(session: ClientSession):
    response = await session.get("...")
```

This function can then be called via

```python
from fast_depends import inject

await inject(web_request)()
```

This package contains annotations that should be available in all code
using cattle_grid, i.e. extensions. The sub packages contain methods
for more specific use cases.
"""

import aiohttp
import logging

from typing import Annotated, Callable
from dynaconf import Dynaconf
from fast_depends import Depends
from faststream import Context
from faststream.rabbit import RabbitExchange, RabbitBroker

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from .internals import InternalExchange, CorrelationId
from .globals import get_engine, global_container


logger = logging.getLogger(__name__)


async def get_client_session():
    yield global_container.session


ClientSession = Annotated[aiohttp.ClientSession, Depends(get_client_session)]
"""The [aiohttp.ClientSession][] used by the application"""

ActivityExchange = Annotated[RabbitExchange, Depends(global_container.get_exchange)]
"""The activity exchange"""

AccountExchange = Annotated[
    RabbitExchange, Depends(global_container.get_account_exchange)
]
"""The account exchange"""

SqlAsyncEngine = Annotated[AsyncEngine, Depends(get_engine)]
"""Returns the SqlAlchemy AsyncEngine"""


SqlSessionMaker = Annotated[
    Callable[[], AsyncSession], Depends(global_container.get_session_maker)
]


async def with_sql_session(
    sql_session_maker=Depends(global_container.get_session_maker),
):
    async with sql_session_maker() as session:
        yield session


SqlSession = Annotated[AsyncSession, Depends(with_sql_session)]
"""SQL session that does not commit afterwards"""


async def with_session_commit(session: SqlSession):
    yield session
    await session.commit()


CommittingSession = Annotated[AsyncSession, Depends(with_session_commit)]
"""Session that commits the transaction"""

Config = Annotated[Dynaconf, Depends(global_container.get_config)]
"""Returns the configuration"""


def activity_exchange_publisher(
    correlation_id: CorrelationId,
    exchange: ActivityExchange,
    broker: RabbitBroker = Context(),
):
    async def publish(*args, **kwargs):
        kwargs_updated = {**kwargs}
        kwargs_updated.update(dict(exchange=exchange, correlation_id=correlation_id))
        return await broker.publish(*args, **kwargs_updated)

    return publish


def internal_exchange_publisher(
    correlation_id: CorrelationId,
    exchange: InternalExchange,
    broker: RabbitBroker = Context(),
):
    async def publish(*args, **kwargs):
        kwargs_updated = {**kwargs}
        kwargs_updated.update(dict(exchange=exchange, correlation_id=correlation_id))
        return await broker.publish(*args, **kwargs_updated)

    return publish


def account_exchange_publisher(
    correlation_id: CorrelationId,
    exchange: AccountExchange,
    broker: RabbitBroker = Context(),
):
    async def publish(*args, **kwargs):
        kwargs_updated = {**kwargs}
        kwargs_updated.update(dict(exchange=exchange, correlation_id=correlation_id))
        return await broker.publish(*args, **kwargs_updated)

    return publish


AccountExchangePublisher = Annotated[Callable, Depends(account_exchange_publisher)]
"""Publishes a message to the activity exchange"""

InternalExchangePublisher = Annotated[Callable, Depends(internal_exchange_publisher)]
"""Publishes a message to the internal exchange"""

ActivityExchangePublisher = Annotated[Callable, Depends(activity_exchange_publisher)]
"""Publishes a message to the activity exchange"""
