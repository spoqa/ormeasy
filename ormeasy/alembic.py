""":mod:`ormeasy.alembic` --- alembic related functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import typing

from alembic.config import Config
from alembic.environment import EnvironmentContext
from alembic.script import ScriptDirectory
from sqlalchemy.engine import Engine
from sqlalchemy.schema import MetaData
from sqlalchemy.sql.expression import literal_column

from .common import import_all_modules

__all__ = 'upgrade_database',


def upgrade_database(
    config: Config,
    engine: Engine,
    metadata: MetaData,
    *,
    revision: str = 'head',
    module_name: typing.Optional[str] = None,
) -> None:
    """Upgrades the database schema to the chosen ``revision`` (default is
    head).

    """
    script = ScriptDirectory.from_config(config)

    def upgrade(rev, context):
        def update_current_rev(old, new):
            if old == new:
                return
            if new is None:
                context.impl._exec(context._version.delete())
            elif old is None:
                context.impl._exec(
                    context._version.insert().values(
                        version_num=literal_column("'%s'" % new)
                    )
                )
            else:
                context.impl._exec(
                    context._version.update().values(
                        version_num=literal_column("'%s'" % new)
                    )
                )

        if not rev and revision == 'head':
            if module_name:
                import_all_modules(module_name)
            metadata.create_all(engine)
            dest = script.get_revision(revision)
            update_current_rev(None, dest and dest.revision)
            return []
        return script._upgrade_revs(revision, rev)
    with EnvironmentContext(config, script, fn=upgrade, as_sql=False,
                            destination_rev=revision, tag=None):
        script.run_env()
