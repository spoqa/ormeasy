""":mod:`ormeasy.sqlalchemy` --- SQLAlchemy related functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import contextlib
import typing

from sqlalchemy.engine import Engine
from sqlalchemy.schema import MetaData

__all__ = 'repr_entity', 'test_connection'


def repr_entity(entity: object) -> str:
    """Make a representation string for the given ``entity`` object.
    If the class specified ``__repr_columns__`` it prints
    these attributes instead of its primary keys.


    .. code-block::

       from sqlalchemy.ext.declarative import as_declarative
       from ormeasy.sqlalchemy import repr_entity

       @as_declarative()
       class Base:

          def __repr__(self):
              return repr_entity(self)


       class Song(Base):

          __tablename__ = 'song'

          __repr_columns__ = 'name', 'genre'

          id = Column(Integer, primary_key=True)

          name = Column(Unicode)

          genre = Column(Unicode)


       print(repr(Song(name='hello', genre='brit-pop'))) # it prints `<Song name=hello, genre=brit-pop>`

    .. seealso::

       ``as_declarative``
          http://docs.sqlalchemy.org/en/latest/orm/extensions/declarative/api.html#sqlalchemy.ext.declarative.as_declarative

    :param entity: an object to make a representation string
    :return: a representation string
    :rtype: :class:`str`

    """  # noqa
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
    ctx: object,
    metadata: MetaData,
    engine: Engine,
    real_transaction: bool = False,
    ctx_connection_attribute_name: str = '_test_fx_connection',
) -> typing.Generator:
    """Joining a SQLAlchemy session into an external transaction for test suit.

    :param object ctx: Context object to inject test connection into attribute
    :param MetaData metadata: SQLAlchemy schema metadata
    :param bool real_transaction: (Optional) Whether to use engine as connection directly
                                  or make separate connection. Default: `False`
    :param str ctx_connection_attribute_name: (Optional) Attribute name for injecting
                                              test connection to the context object
                                              Default: `'_test_fx_connection'`

    .. seealso::

       Documentation of the SQLAlchemy session used in test suites.
          <http://docs.sqlalchemy.org/en/latest/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites>

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
            setattr(ctx, ctx_connection_attribute_name, connection)
            try:
                yield connection
            finally:
                delattr(ctx, ctx_connection_attribute_name)
        finally:
            transaction.rollback()
    finally:
        connection.close()
    engine.dispose()
