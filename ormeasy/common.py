""":mod:`ormeasy.common` --- Common utility functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import importlib
import os
import pkgutil
import typing

__all__ = 'get_all_modules', 'import_all_modules',


def get_all_modules(
    module_name: str,
    path: typing.Optional[typing.Sequence[str]] = None,
) -> typing.AbstractSet[str]:
    """Find all module names from given ``module_name``.

    :param str module_name: The name of root module which want to find.
    :param list[str] or None path: The path to find the root module.
    :return: The set of module names.

    .. code-block:: python

       >>> get_all_modules('ormeasy')
       {'ormeasy.alembic', 'ormeasy.common', 'ormeasy.sqlalchemy'}
       >>> get_all_modules('ormeasy.common')
       {'ormeasy.common'}

    """
    root_mod, *_ = module_name.split('.')
    module_spec = importlib.machinery.PathFinder.find_spec(root_mod, path)
    if not module_spec:
        if path:
            raise ValueError(
                '{!s} inexists or is not a python module in {!s}'.format(
                    root_mod, path
                )
            )
        raise ValueError(
            '{!s} inexists or is not a python module'.format(root_mod)
        )
    module_name_with_dot = root_mod + '.'
    if module_spec.submodule_search_locations:
        module_names = {
            name
            for _, name, _ in pkgutil.walk_packages(
                module_spec.submodule_search_locations,
                prefix=module_name_with_dot
            )
        }
    else:
        module_names = {
            name
            for _, name, _ in pkgutil.walk_packages(
                [os.path.dirname(module_spec.origin)]
            )
            if name.startswith(module_name_with_dot) or name == module_name
        }
    return {m for m in module_names if m.startswith(module_name)}


def import_all_modules(
    module_name: str,
    path: typing.Optional[typing.Sequence[str]] = None,
) -> typing.AbstractSet[str]:
    """Import all modules. Maybe it is useful when populate revision script
    in alembic with ``--autogenerate`` option. Since alembic can only detect a
    change/creation of an object that imported in runtime, importing all
    modules helps entity to track in migration script properly.

    .. code-block:

       >>> from ormeasy.common import import_all_modules
       >>> import_all_modules('ormeasy')

    :param str module_name: The module name want to import.
    :param list[str] or None path: The path to find the root module.

    """
    modules = get_all_modules(module_name, path)
    for module_name in modules:
        importlib.import_module(module_name)
    return modules
