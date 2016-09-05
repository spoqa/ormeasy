""":mod:`ormeasy.sqlalchemy` --- SQLAlchemy related functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import typing
import contextlib

from sqlalchemy.engine import Engine
from sqlalchemy.schema import MetaData

__all__ = 'repr_entity', 'test_connection'


def repr_entity(entity: object) -> str:
    """Make a representation string for the given ``entity`` object.
    If the class specified ``__repr_columns__`` it prints
    these attributes instead of its primary keys.

    :param entity: an object to make a representation string
    :return: a representation string
    :rtype: :class:`str`

    """
    cls = type(entity)
    mod = cls.__module__
    name = ('' if mod == '__main__ ' else mod + '.') + cls.__qualname__
    try:
        columns = entity.__repr_columns__
    except AttributeError:
        columns = cls.__mapper__.primary_key
    names = (column if isinstance(column, str) else column.name
             for column in columns)
    pairs = ((name, getattr(entity, name))
             for name in names
             if hasattr(entity, name))
    args = ' '.join(k + '=' + repr(v) for k, v in pairs)
    return '<{0} {1}>'.format(name, args)


@contextlib.contextmanager
def test_connection(
    ctx: object, metadata: MetaData, engine: Engine,
    real_transaction: bool=False
) -> typing.Generator:
    """Joining a SQLAlchemy session into an external transaction for test suit.

    .. seealso::

       <http://docs.sqlalchemy.org/en/latest/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites>
          Documentation of the SQLAlchemy session used in test suites.

    """  # noqa
    if real_transaction:
        metadata.create_all(engine)
        try:
            yield engine
        finally:
            metadata.drop_all(engine, checkfirst=True)
        return
    connection = engine.connect()
    try:
        metadata.drop_all(connection, checkfirst=True)
        transaction = connection.begin()
        try:
            metadata.create_all(bind=connection)
            ctx._test_fx_connection = connection
            try:
                yield connection
            finally:
                del ctx._test_fx_connection
        finally:
            transaction.rollback()
    finally:
        connection.close()
    engine.dispose()
