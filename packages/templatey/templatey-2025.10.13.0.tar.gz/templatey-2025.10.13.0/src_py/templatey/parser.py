from __future__ import annotations

import ast
import itertools
import logging
import re
import string
from collections import defaultdict
from collections.abc import Collection
from collections.abc import Generator
from collections.abc import Iterator
from collections.abc import Mapping
from collections.abc import Sequence
from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields
from dataclasses import replace as dc_replace
from functools import singledispatch
from itertools import count
from typing import Annotated
from typing import Any
from typing import cast

from docnote import ClcNote

from templatey.exceptions import DuplicateSlotName
from templatey.exceptions import InvalidTemplateInterpolation
from templatey.interpolators import NamedInterpolator
from templatey.interpolators import transform_unicode_control
from templatey.interpolators import untransform_unicode_control
from templatey.modifiers import EnvFuncInvocationRef
from templatey.modifiers import SegmentModifier

_SLOT_MATCHER = re.compile(r'^\s*slot\.([A-z_][A-z0-9_]*)\s*$')
_CONTENT_MATCHER = re.compile(r'^\s*content\.([A-z_][A-z0-9_]*)\s*$')
_VAR_MATCHER = re.compile(r'^\s*var\.([A-z_][A-z0-9_]*)\s*$')
_FUNC_MATCHER = re.compile(r'^\s*@([A-z_][A-z0-9_]*)\(([^\)]*)\)\s*$')
_COMMENT_MATCHER = re.compile(r'^\s*#.*$')
logger = logging.getLogger(__name__)

type TemplateSegment = (
    LiteralTemplateString
    | InterpolatedSlot
    | InterpolatedContent
    | InterpolatedVariable
    | InterpolatedFunctionCall)


@dataclass(frozen=True, slots=True)
class ParsedTemplateResource:
    """In addition to storing the actual template parts, this stores
    information about which references the template had, for use later
    when validating the template (within some render context).
    """
    parts: tuple[TemplateSegment, ...]
    variable_names: frozenset[str]
    content_names: frozenset[str]
    slot_names: frozenset[str]
    function_names: frozenset[str]
    data_names: frozenset[str]
    # Separate this out from function_names so that we can put compare=False
    # while still preserving comparability between instances. It's not clear if
    # this is useful, but the memory footprint should be low
    # Note: this is included for convenience, so that the render environment
    # has easy access to all of the *args and **kwargs, so that they can be
    # tested against the signature of the actual render function during loading
    function_calls: dict[str, tuple[InterpolatedFunctionCall, ...]] = field(
        compare=False)
    slots: dict[str, InterpolatedSlot] = field(compare=False)

    # Purely here for performance reasons
    part_count: int = field(init=False, compare=False)

    def __post_init__(self):
        object.__setattr__(self, 'part_count', len(self.parts))

    @classmethod
    def from_parts(
            cls,
            parts: Sequence[TemplateSegment]
            ) -> ParsedTemplateResource:
        if not isinstance(parts, tuple):
            parts = tuple(parts)

        content_names = set()
        slot_names = set()
        variable_names = set()
        data_names = set()
        functions = defaultdict(list)
        for part in parts:
            if isinstance(part, InterpolatedContent):
                content_names.add(part.name)
            elif isinstance(part, InterpolatedVariable):
                variable_names.add(part.name)
            elif isinstance(part, InterpolatedSlot):
                # Interpolated slots must be unique; enforce that here.
                if part.name in slot_names:
                    raise DuplicateSlotName(part.name)

                for maybe_reference in part.params.values():
                    nested_content_refs, nested_var_refs, _ = \
                        _extract_nested_refs(maybe_reference)
                    content_names.update(
                        ref.name for ref in nested_content_refs)
                    variable_names.update(ref.name for ref in nested_var_refs)

                slot_names.add(part.name)

            elif isinstance(part, InterpolatedFunctionCall):
                for maybe_reference in itertools.chain(
                    part.call_args,
                    part.call_kwargs.values(),
                    (starargs for starargs in (part.call_args_exp,)),
                    (starkwargs for starkwargs in (part.call_kwargs_exp,))
                ):
                    (
                        nested_content_refs,
                        nested_var_refs,
                        nested_data_refs) = _extract_nested_refs(
                            maybe_reference)
                    content_names.update(
                        ref.name for ref in nested_content_refs)
                    variable_names.update(ref.name for ref in nested_var_refs)
                    data_names.update(ref.name for ref in nested_data_refs)

                functions[part.name].append(part)

        return cls(
            parts=parts,
            content_names=frozenset(content_names),
            variable_names=frozenset(variable_names),
            slot_names=frozenset(slot_names),
            function_names=frozenset(functions),
            function_calls={
                name: tuple(calls) for name, calls in functions.items()},
            data_names=frozenset(data_names),
            slots={
                maybe_slot.name: maybe_slot
                for maybe_slot in parts
                if isinstance(maybe_slot, InterpolatedSlot)})


class LiteralTemplateString(str):
    __slots__ = ['part_index']
    part_index: int

    def __new__(cls, *args, part_index: int, **kwargs):
        instance = super().__new__(cls, *args, **kwargs)
        instance.part_index = part_index
        return instance


@dataclass(frozen=True, slots=True)
class InterpolatedContent:
    """
    """
    part_index: int
    # TODO: this needs a way to define any variables used by the content via
    # ComplexContent! Otherwise, strict mode in template/interface validation
    # will always fail with interpolated content.
    name: str
    config: InterpolationConfig


@dataclass(frozen=True, slots=True)
class InterpolatedSlot:
    """
    """
    part_index: int
    name: str
    params: dict[str, object]
    config: InterpolationConfig

    def __post_init__(self):
        if self.config.fmt:
            raise InvalidTemplateInterpolation(
                'Template slots cannot have format specs!')


@dataclass(frozen=True, slots=True)
class InterpolatedVariable:
    """
    """
    part_index: int
    name: str
    config: InterpolationConfig

    def __post_init__(self):
        if self.config.prefix is not None or self.config.suffix is not None:
            raise InvalidTemplateInterpolation(
                'Template variables cannot have prefixes nor suffixes. If you '
                + 'need similar behavior, you can create a dedicated '
                + 'converter function to add the affix before escaping.')


@dataclass(frozen=True, slots=True)
class InterpolatedFunctionCall:
    """
    """
    part_index: int
    name: str
    call_args: Sequence[object] = field(compare=False)
    call_args_exp: object | None = field(compare=False)
    call_kwargs: dict[str, object] = field(compare=False)
    call_kwargs_exp: object | None = field(compare=False)

    def _matches(self, other: object) -> bool:
        """Okay, so the problem is as follows:
        1.. We need to be able to check equality during testing
        2.. We need hashing in other places
        3.. We can't mess with equality, because it would break the
            dict keys we need from the hash
        4.. Therefore, we need to exempt the call args / etc from the
            normal equality check, but still need something for testing
        Therefore, we create this, which checks everything -- but just
        for testing.
        """
        if not isinstance(other, InterpolatedFunctionCall):
            return False

        return (
            self.part_index == other.part_index
            and self.name == other.name
            and self.call_args == other.call_args
            and self.call_args_exp == other.call_args_exp
            and self.call_kwargs == other.call_kwargs
            and self.call_kwargs_exp == other.call_kwargs_exp)


@dataclass(slots=True, frozen=True)
class TemplateInstanceContentRef:
    """Used to indicate that an environment function or segment
    modification needs to reference a content parameter on the current
    template instance being rendered.
    """
    name: Annotated[
        str,
        ClcNote('The name of the content parameter')]


@dataclass(slots=True, frozen=True)
class TemplateInstanceVariableRef:
    """Used to indicate that an environment function or segment
    modification needs to reference a variable parameter on the current
    template instance being rendered.
    """
    name: Annotated[
        str,
        ClcNote('The name of the variable parameter')]


@dataclass(slots=True, frozen=True)
class TemplateInstanceDataRef:
    """Used to indicate that an environment function (including one
    injected via segment modification) needs to reference a template
    data attribute on the current template instance being rendered.
    """
    name: Annotated[
        str,
        ClcNote('The name of the data attribute (the dataclass field name)')]


_VALID_NESTED_REFS = {
    'content': TemplateInstanceContentRef,
    'var': TemplateInstanceVariableRef,
    'data': TemplateInstanceDataRef,}


def parse(
        template_str: str,
        interpolator: NamedInterpolator,
        segment_modifiers: Sequence[SegmentModifier],
        ) -> ParsedTemplateResource:
    """Parses the template string with the passed interpolator and
    applies the desired segment modifiers.
    """
    if interpolator is NamedInterpolator.UNICODE_CONTROL:
        do_untransform = True
        template_str = transform_unicode_control(template_str)
    else:
        do_untransform = False

    part_index_counter = count()
    parts: list[TemplateSegment] = []
    for premodification_segment in _wrap_formatter_parse(
        template_str, do_untransform=do_untransform
    ):
        parts.extend(_apply_segment_modifiers(
            premodification_segment,
            segment_modifiers,
            part_index_counter))
    return ParsedTemplateResource.from_parts(parts)


def _apply_segment_modifiers(
        unmodified_part: TemplateSegment,
        segment_modifiers: Sequence[SegmentModifier],
        part_index_counter: count,
        ) -> Iterator[TemplateSegment]:
    """As the name suggests, this takes an unmodified part and applies
    any desired segment modifiers. Note that this can grow or contract
    the total number of segments.
    """
    # The combinatorics here are gross, but this only runs once per
    # template load, and not once per render, so at least there's
    # that.
    if isinstance(unmodified_part, str):
        for modifier in segment_modifiers:
            had_matches, after_mods = modifier.apply_and_flatten(
                unmodified_part)

            if had_matches:
                yield from (
                    _coerce_modified_segment(
                        modified_segment, part_index_counter)
                    for modified_segment in after_mods)
                break

        else:
            # We still want to create a copy here, in case the
            # template loader is doing its own caching beyond what
            # we do within the env
            yield LiteralTemplateString(
                unmodified_part,
                part_index=next(part_index_counter))

    else:
        yield dc_replace(
            unmodified_part,
            part_index=next(part_index_counter))


def _coerce_modified_segment(
        modified_segment:
            str
            | EnvFuncInvocationRef
            | TemplateInstanceContentRef
            | TemplateInstanceVariableRef,
        part_index_counter: count,
            ) -> (
                LiteralTemplateString
                | InterpolatedContent
                | InterpolatedVariable
                | InterpolatedFunctionCall):
    """Converts the result of segment modification into an actual
    parsed template resource part, including a part index.
    """
    if isinstance(modified_segment, str):
        return LiteralTemplateString(
            modified_segment, part_index=next(part_index_counter))

    elif isinstance(modified_segment, EnvFuncInvocationRef):
        return InterpolatedFunctionCall(
            part_index=next(part_index_counter),
            name=modified_segment.name,
            call_args=modified_segment.call_args,
            call_args_exp=None,
            call_kwargs=modified_segment.call_kwargs,
            call_kwargs_exp=None)

    elif isinstance(modified_segment, TemplateInstanceContentRef):
        return InterpolatedContent(
            part_index=next(part_index_counter),
            name=modified_segment.name,
            config=InterpolationConfig())

    elif isinstance(modified_segment, TemplateInstanceVariableRef):
        return InterpolatedVariable(
            part_index=next(part_index_counter),
            name=modified_segment.name,
            config=InterpolationConfig())

    else:
        raise TypeError('Unknown modified segment type!', modified_segment)


def _extract_nested_refs(
        value
        ) -> tuple[
            set[TemplateInstanceContentRef],
            set[TemplateInstanceVariableRef],
            set[TemplateInstanceDataRef]]:
    """Call this to recursively extract all of the content and variable
    references contained within an environment function call.
    """
    content_refs = set()
    var_refs = set()
    data_refs = set()

    # Note that order here is important! Mappings are always collections!
    # Strings are always collections, too!
    if isinstance(value, Mapping):
        nested_values = value.values()
    elif isinstance(value, str):
        nested_values = ()
    elif isinstance(value, Collection):
        nested_values = value
    else:
        nested_values = ()

        if isinstance(value, TemplateInstanceContentRef):
            content_refs.add(value)

        elif isinstance(value, TemplateInstanceVariableRef):
            var_refs.add(value)

        elif isinstance(value, TemplateInstanceDataRef):
            data_refs.add(value)

    for nested_val in nested_values:
        nested_content_refs, nested_var_refs, nested_data_refs = \
            _extract_nested_refs(nested_val)
        content_refs.update(nested_content_refs)
        var_refs.update(nested_var_refs)
        data_refs.update(nested_data_refs)

    return content_refs, var_refs, data_refs


def _wrap_formatter_parse(
        formattable_template_str: str,
        do_untransform=False
        ) -> Generator[TemplateSegment, None, None]:
    """A generator. Wraps the very weird API provided by
    string.Formatter.parse, instead yielding either:
    ++  literal text, in string format
    ++  ``InterpolatedContent`` instances
    ++  ``InterpolatedSlot`` instances
    ++  ``InterpolatedVariable`` instances
    ++  ``InterpolatedFunctionCall`` instances
    """
    part_counter = itertools.count()
    formatter = string.Formatter()

    for format_tuple in formatter.parse(formattable_template_str):
        # Arg order here is: literal_text, field_name, format_spec, conversion
        # Note that this can contain BOTH a literal text and a field name.
        # It's a really weird API; that's why we're wrapping it in
        # _extract_formatting_kwargs. It still reads things left-to-right, but
        # it bundles them together really strangely
        if do_untransform:
            literal_text, field_name, format_spec, conversion = (
                untransform_unicode_control(format_tuple_part)
                if format_tuple_part is not None else None
                for format_tuple_part in format_tuple)
        else:
            literal_text, field_name, format_spec, conversion = format_tuple

        if literal_text is not None:
            if do_untransform:
                yield LiteralTemplateString(
                    untransform_unicode_control(literal_text),
                    part_index=next(part_counter))
            else:
                yield LiteralTemplateString(
                    literal_text,
                    part_index=next(part_counter))

        # field_name can be None, an empty string, or a kwargname.
        # None means there's no formatting field left in the string -- in which
        # case, the literal_text would contain the rest of the string.
        if field_name is None:
            continue
        else:
            coerced_interpolation = _coerce_interpolation(
                field_name, format_spec, conversion, part_counter)
            if coerced_interpolation is not None:
                yield coerced_interpolation


@dataclass(frozen=True, slots=True)
class InterpolationConfig:
    """
    """
    fmt: str | None = None
    prefix: str | None = None
    suffix: str | None = None

    def apply_prefix_iter(self) -> Iterator[str]:
        """If a prefix is defined, yields it. Otherwise, does nothing.
        """
        prefix = self.prefix
        if prefix is not None:
            yield prefix

    def apply_suffix_iter(self) -> Iterator[str]:
        """If a suffix is defined, yields it. Otherwise, does nothing.
        """
        suffix = self.suffix
        if suffix is not None:
            yield suffix

    def apply_affix(self, val: str | None) -> tuple[str, ...]:
        """For the given val, inserts any defined prefix and/or suffix.
        If val is None, returns an empty tuple.

        Note that tuples are faster for list.extend than both iterators
        and lists, at least for these small sizes.
        """
        if val is None:
            return ()

        suffix = self.suffix
        prefix = self.prefix
        # Explicitly typing out the logic square here as a microoptimization
        if prefix is None:
            if suffix is None:
                return (val,)
            else:
                return (val, suffix)
        elif suffix is None:
            return (prefix, val)
        else:
            return (prefix, val, suffix)

    @classmethod
    def from_format_spec(
            cls,
            format_spec: str | None
            ) -> tuple[InterpolationConfig, dict[str, object]]:
        if format_spec is None or not format_spec:
            return (cls(), {})

        # If you shift away from using AST-based parsing, then this trick is
        # useful for converting raw strings to normal ones:
        # codecs.decode(r'\n', 'unicode_escape') == '\n'
        try:
            tree = ast.parse(f'print({format_spec})')
        except (ValueError, SyntaxError) as exc:
            raise InvalidTemplateInterpolation(
                'Invalid interpolation parameters!'
            ) from exc

        injected_print = cast(ast.Call, cast(ast.Expr, tree.body[0]).value)

        kwargs = {}
        dunders = {}

        if injected_print.args:
            raise InvalidTemplateInterpolation(
                'Everything after the : in a templatey interpolation must be '
                + 'a keyword-only argument dict!')

        for ast_kwarg in injected_print.keywords:
            argname = ast_kwarg.arg
            if argname is None:
                raise InvalidTemplateInterpolation(
                    'Additional arguments in templatey interpolations (ex '
                    + 'explicit slot parameters) do not currently support '
                    + 'star expansion (**kwargs)')

            elif argname.startswith('__') and argname.endswith('__'):
                dunder_name = argname[2:-2]

                if dunder_name not in _interp_cfg_fields:
                    logger.warning('Skipping unknown dunder field %s', argname)
                    continue

                # I think the following bit is reporting as unreachable because
                # it doesn't think the singledispatch will match on anything,
                # and therefore raise valueerror
                dunder_value = _extract_reference_or_literal(ast_kwarg.value)

                if not isinstance(dunder_value, str):
                    raise InvalidTemplateInterpolation(
                        'Non-string values for interpolation dunders are not '
                        + 'currently supported!')

                dunders[dunder_name] = dunder_value

            else:
                kwargs[ast_kwarg.arg] = _extract_reference_or_literal(
                    ast_kwarg.value)

        return (cls(**dunders), kwargs)


# We use this for faster checks when parsing templates in from_format_spec
_interp_cfg_fields = {field.name for field in fields(InterpolationConfig)}


def _coerce_interpolation(field_name, format_spec, conversion, part_counter):
    try:
        if conversion:
            raise InvalidTemplateInterpolation(
                'Conversion specs are not supported in templatey; pass a '
                + 'stringifier to the field definition instead.')

        # The format spec is determined by the first : in the interpolation.
        # Any following :s are included as part of it. However, for function
        # calls, we want to interpret the format spec : as literally part of
        # the field_name, so we join them back up.
        if format_spec:
            full_interpolation_def = f'{field_name}:{format_spec}'
        else:
            full_interpolation_def = field_name

        if _COMMENT_MATCHER.match(full_interpolation_def) is not None:
            return None

        if (match := _FUNC_MATCHER.match(full_interpolation_def)) is not None:
            args, starargs, kwargs, starkwargs = _extract_call_signature(
                match.group(2))
            return InterpolatedFunctionCall(
                part_index=next(part_counter),
                name=match.group(1),
                call_args=args,
                call_args_exp=starargs,
                call_kwargs=kwargs,
                call_kwargs_exp=starkwargs,)

        interp_cfg, kwargs = InterpolationConfig.from_format_spec(format_spec)
        if (match := _SLOT_MATCHER.match(field_name)) is not None:
            slot_params_str = format_spec.strip()
            args, starargs, kwargs, starkwargs = _extract_call_signature(
                slot_params_str)

            return InterpolatedSlot(
                part_index=next(part_counter),
                name=match.group(1),
                params=kwargs,
                config=interp_cfg)

        else:
            if kwargs:
                raise InvalidTemplateInterpolation(
                    'Interpolated variables and content cannot have arbitrary '
                    + 'kwargs, only dunders!')

            if (match := _VAR_MATCHER.match(field_name)) is not None:
                return InterpolatedVariable(
                    part_index=next(part_counter),
                    name=match.group(1),
                    config=interp_cfg)

            elif (match := _CONTENT_MATCHER.match(field_name)) is not None:
                return InterpolatedContent(
                    part_index=next(part_counter),
                    name=match.group(1),
                    config=interp_cfg)

        raise InvalidTemplateInterpolation(
            'Unknown target for templatey interpolation (must be var, slot, '
            + 'env function, content, or comment)')

    except InvalidTemplateInterpolation as exc:
        exc.add_note(f'{field_name=}, {format_spec=}, {conversion=}')
        raise exc


def _extract_call_signature(str_signature):
    """Returns *args and **kwargs for the desired asset function."""
    try:
        tree = ast.parse(f'print({str_signature})')
        injected_print = cast(ast.Call, cast(ast.Expr, tree.body[0]).value)

        args = []
        starargs = None
        kwargs = {}
        starkwargs = None

        for ast_arg in injected_print.args:
            if isinstance(ast_arg, ast.Starred):
                starargs = _extract_reference_or_literal(ast_arg.value)
            else:
                args.append(_extract_reference_or_literal(ast_arg))

        for ast_kwarg in injected_print.keywords:
            if ast_kwarg.arg is None:
                starkwargs = _extract_reference_or_literal(ast_kwarg.value)
            else:
                kwargs[ast_kwarg.arg] = _extract_reference_or_literal(
                    ast_kwarg.value)

        return args, starargs, kwargs, starkwargs

    except (ValueError, SyntaxError) as exc:
        raise InvalidTemplateInterpolation(
            'Invalid environment function call signature') from exc


@singledispatch
def _extract_reference_or_literal(ast_node) -> Any:
    """Gets the actual reference out of an AST node used in the call
    signature, either as an arg or the value of a kwarg.
    """
    raise ValueError('No matching node type', ast_node)


@_extract_reference_or_literal.register
def _(ast_node: ast.Attribute):
    should_be_name = ast_node.value
    if not isinstance(should_be_name, ast.Name):
        raise ValueError('Non-literals must be attributes', ast_node)

    target_cls = _VALID_NESTED_REFS.get(should_be_name.id)
    if target_cls is None:
        raise ValueError(
            'Invalid asset reference value for asset function',
            should_be_name.id)

    return target_cls(name=ast_node.attr)


@_extract_reference_or_literal.register
def _(ast_node: ast.Constant):
    return ast_node.value
