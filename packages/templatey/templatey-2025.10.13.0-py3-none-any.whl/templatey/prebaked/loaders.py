from __future__ import annotations

import typing
from importlib import import_module
from pathlib import Path
from typing import Annotated

try:
    import anyio
except ImportError:
    if typing.TYPE_CHECKING:
        import anyio

from docnote import ClcNote

from templatey._types import TemplateParamsInstance
from templatey.environments import AsyncTemplateLoader
from templatey.environments import SyncTemplateLoader


class InlineStringTemplateLoader(
        AsyncTemplateLoader[str], SyncTemplateLoader[str]):
    """This loader -- primarily intended for library use -- uses the
    resource locator as an explicit inline string version of the
    template.
    """

    def load_sync(
            self,
            template: type[TemplateParamsInstance],
            template_resource_locator: str
            ) -> str:
        return template_resource_locator

    async def load_async(
            self,
            template: type[TemplateParamsInstance],
            template_resource_locator: str
            ) -> str:
        await anyio.sleep(0)
        return template_resource_locator


class DictTemplateLoader[L: object](
        AsyncTemplateLoader[L], SyncTemplateLoader[L]):
    """A barebones template loader that simply loads templates from a
    dictionary based on whatever key you supply.
    """
    lookup: Annotated[dict[L, str],
        ClcNote('''
            Provides direct access to the template lookup. Store literal
            template text here using whatever key matches the resource locator
            used on your template definitions.
            ''')]

    def __init__(self, templates: dict[L, str] | None = None):
        if templates is None:
            templates = {}

        self.lookup = templates

    def load_sync(
            self,
            template: type[TemplateParamsInstance],
            template_resource_locator: L
            ) -> str:
        return self.lookup[template_resource_locator]

    async def load_async(
            self,
            template: type[TemplateParamsInstance],
            template_resource_locator: L
            ) -> str:
        await anyio.sleep(0)
        return self.lookup[template_resource_locator]


class CompanionFileLoader(AsyncTemplateLoader[str], SyncTemplateLoader[str]):
    """This loader uses string resource locators that correspond to
    files located in the same directory as the underlying template
    definition. For example:

    > my_templates.py
    __embed__: 'code/python'
        from templatey import template
        from templatey.prebaked.template_configs import html

        @template(html, 'custom_template.html')
        class CustomTemplate:
            ...

    That would search for a file called ``custom_template.html`` in the
    same parent directory as ``my_templates.py``.

    This supports both sync and async loading, but async loading
    requires ``anyio`` to be installed (also available via extras,
    ``pip install templatey[async_prebaked]``).
    """

    def load_sync(
            self,
            template: type[TemplateParamsInstance],
            template_resource_locator: str
            ) -> str:
        template_module_name = template.__module__
        template_module = import_module(template_module_name)
        module_file = template_module.__file__

        if module_file is None:
            raise ValueError(
                'CompanionFileLoader can only load templates defined in '
                + 'actual modules!')

        module_dir = Path(module_file).parent
        return (module_dir / template_resource_locator).read_text(
            encoding='utf-8')

    async def load_async(
            self,
            template: type[TemplateParamsInstance],
            template_resource_locator: str
            ) -> str:
        template_module_name = template.__module__
        template_module = import_module(template_module_name)
        module_file = template_module.__file__

        if module_file is None:
            raise ValueError(
                'CompanionFileLoader can only load templates defined in '
                + 'actual modules!')

        # Pyright isn't correctly applying the anyio is not None, hence the
        # ignore
        module_dir = anyio.Path(module_file).parent
        return await (module_dir / template_resource_locator).read_text(
            encoding='utf-8')
