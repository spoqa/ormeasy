import contextlib
import sys

try:
    from sqlalchemy.ext.asyncio import create_async_engine
except ImportError:
    create_async_engine = None


if sys.version_info < (3, 7):
    raise RuntimeError('Python >= 3.7 required.')


__all__ = 'test_connection',


@contextlib.asynccontextmanager
async def test_connection(
    ctx: object,
    metadata: MetaData,
    engine: 'sqlalchemy.ext.asyncio.AsyncEngine',
    real_transaction: bool = False,
    ctx_connection_attribute_name: str = '_test_fx_connection',
):
    """asyncio version of :func:`.sqlalchemy.test_connection`.
    Since SQLAlchemy 1.4 supports asyncio, it needs to handle async engine
    as well.

    :param object ctx: Context object to inject test connection into attribute
    :param MetaData metadata: SQLAlchemy schema metadata
    :param bool real_transaction: (Optional) Whether to use engine as connection directly
                                  or make separate connection. Default: `False`
    :param str ctx_connection_attribute_name: (Optional) Attribute name for injecting
                                              test connection to the context object
                                              Default: `'_test_fx_connection'`

    .. code-block::

       from pytest import fixture

       @fixture
       async def fx_connection(request, fx_engine: AsyncEngine):
           real_tx = request.config.getoption('--real-tx')
           async with async_test_connection(request, Base.metadata, fx_engine, real_tx) as connection:
               yield connection

    """  # noqa
    if create_async_engine is None:
        raise RuntimeError('SQLAlchemy >= 1.4 required.')
    if real_transaction:
        async with engine.begin() as connection:
            await connection.run_sync(metadata.create_all)
    async with engine.connect() as connection:
        setattr(ctx, ctx_connection_attribute_name, connection)
        if real_transaction:
            yield connection
        else:
            async with connection.begin() as transaction:
                await connection.run_sync(Base.metadata.create_all)
                yield connection
                await transaction.rollback()
    if real_transaction:
        async with engine.begin() as connection:
            await connection.run_sync(metadata.drop_all)
    await engine.dispose()
