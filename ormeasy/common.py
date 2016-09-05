""":mod:`ormeasy.common` --- Common utility functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import importlib
import os
import pkgutil
import typing

__all__ = 'get_all_modules', 'import_all_modules',


def get_all_modules(module_name: str) -> typing.AbstractSet[str]:
    """Find all module names from given ``module_name``.

    :param str module_name: The name of root module which want to find.
    :return: The set of module names.

    """
    module_spec = importlib.machinery.PathFinder.find_spec(module_name)
    if not module_spec:
        raise ValueError(
            '{!s} inexists or is not a python module'.format(module_name)
        )
    module_name_with_dot = module_name + '.'
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
    return module_names


def import_all_modules(module_name: str) -> typing.AbstractSet[str]:
    """Import all modules. Maybe it is useful when populate revision script
    in alembic with ``--autogenerate`` option. Since alembic can only detect a
    change/creation of an object that imported in runtime, importing all
    modules helps entity to track in migration script properly.

    .. code-block:

       >>> from ormeasy.common import import_all_modules
       >>> import_all_modules('ormeasy')

    :param str module_name: The module name want to import.

    """
    modules = get_all_modules(module_name)
    for module_name in modules:
        importlib.import_module(module_name)
    return modules
