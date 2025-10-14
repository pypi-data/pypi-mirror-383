"""These are responsible for finalizing the template definition during
loading. We defer until loading so that forward refs on the templates
are resolved. Trust me, it's way, WAY easier this way (we used to try
to do it the other way and it was a massive headache.
"""
from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from dataclasses import field
from typing import cast

from templatey._fields import NormalizedFieldset
from templatey._signature import TemplateSignature
from templatey._slot_tree import build_slot_tree
from templatey._types import TemplateClass
from templatey._types import TemplateIntersectable
from templatey.parser import ParsedTemplateResource


@dataclass(slots=True)
class SignatureFinalizer:
    preload: dict[TemplateClass, ParsedTemplateResource]
    required_loads: set[TemplateClass]
    target_resource: ParsedTemplateResource = field(init=False)


@contextmanager
def finalize_signature(
        signature: TemplateSignature,
        template_cls: TemplateClass,
        *,
        force_reload: bool = False,
        preload: dict[TemplateClass, ParsedTemplateResource] | None,
        parse_cache: dict[TemplateClass, ParsedTemplateResource],
        ) -> Generator[SignatureFinalizer, None, None]:
    """This contextmanager centralizes all the logic to finalize the
    signature for a template during the loading process.
    """
    # As the name suggests, this also recursively finalizes all inclusions.
    ensure_recursive_totality(signature, template_cls)

    # Note that, because we need to potentially populate a preload, and
    # not just the cache, we have to do this every time, even if the
    # desired root template is already in the cache (because its
    # requirements might not be).
    # Three things:
    # 1. we're prioritizing the case where preload is set, because that
    #    happens during render calls, which need to be fast.
    # 2. we're assuming that the total inclusions are significantly
    #    smaller than the total template cache.
    # 3. this isn't, strictly speaking, threadsafe, so if and when we add
    #    support for finite caches, we'll need to wrap this into a lock.
    #    Or something. It's not clear how this would work if someone wants
    #    both sync and async loading at the same time.
    required_loads: set[TemplateClass] = set()

    # Note that we need a preload to construct prerender trees regardless
    # of whether or not the caller cares about it.
    if preload is None:
        preload = {}

    # Provision this in advance (with mutable args) so that we can update the
    # target resource if we fetch it from the cache
    finalizer = SignatureFinalizer(
        preload=preload,
        required_loads=required_loads)

    # This is cleaner than a difference, since we need to handle both the
    # excluded and included cases if we have a preload
    for included_template_cls in signature.total_inclusions:
        if force_reload:
            required_loads.add(included_template_cls)
        elif (
            from_cache := parse_cache.get(included_template_cls)
        ) is not None:
            preload[included_template_cls] = from_cache
            if included_template_cls is template_cls:
                finalizer.target_resource = from_cache
        else:
            required_loads.add(included_template_cls)

    yield finalizer

    # Note: the finalizers need to be done separately, because the prerender
    # tree finalizer requires all of the **resources** of all inclusions to be
    # loaded prior to constructing the tree
    for required_template_cls in required_loads:
        requirement_signature = cast(
            type[TemplateIntersectable], required_template_cls
        )._templatey_signature

        # Note that we have to do this on all of the requirements;
        # otherwise, they'll be stored in the cache with an incomplete
        # signature.
        ensure_slot_tree(requirement_signature, required_template_cls)
        ensure_prerender_tree(requirement_signature, preload)

        parsed_resource = preload[required_template_cls]
        if required_template_cls is template_cls:
            finalizer.target_resource = parsed_resource

        # Note that we only want to actually cache the resources if everything
        # succeeded without error; otherwise, we could have partially-finalized
        # signatures
        parse_cache[required_template_cls] = parsed_resource

    if not hasattr(finalizer, 'target_resource'):
        raise RuntimeError(
            'Impossible branch: target template missing from load results',
            template_cls)


@dataclass(slots=True)
class _TotalityRecursionGuard:
    root_template_cls: TemplateClass
    root_total_inclusions: set[TemplateClass]


def ensure_recursive_totality(
        signature: TemplateSignature,
        template_cls: TemplateClass,
        *,
        _recursion_guard: _TotalityRecursionGuard | None = None
        ) -> None:
    """This function constructs and populates the
    ``signature.fieldset`` and ``signature.total_inclusions``
    attributes if (and only if) either one of them is missing, and
    then recursively does the same for all non-dynamic nested slot
    classes.

    This is helpful for several reasons:
    ++  it makes sure that we have a full fieldset and descendant
        classes for the entire descendancy tree, so that we can
        construct a slot tree (and thereafter a prerender tree) for
        the class
    ++  if the attributes already exist, it does nothing, so we
        don't waste work on nested template classes
    ++  it allows parsed template resources to fall out of cache
        without discarding the work we did processing the signature
        itself

    This is meant to be called during loading (instead of, for example,
    during ``@template`` decoration time) because it maximizes the
    chances that all of the type hints are available (ie, no longer
    forward refs).

    Note that our approach here, though not computationally ideal, is
    much simpler than a more sophisticated/efficient approach. Instead
    of trying to construct all of the totalities at the same time, we
    simply construct them for the root class, and then proceed on to
    each one of its inclusions iteratively. Again, there's a lot of
    duplicate work here, but it makes it **much** easier to resolve
    recursion loops.

    This returns the total inclusions for the passed class, whether or
    not it was the root template class.
    """
    if not hasattr(signature, 'fieldset'):
        signature.fieldset = NormalizedFieldset.from_template_cls(
            template_cls)

    # If we've already calculated total inclusions, AND this is a recursive
    # call, we still need to update the caller with the total inclusions!
    # This is critical; the point of recursive calls is not to populate the
    # value on the downstream child, but rather to extract inclusions on
    # behalf of the upstream parent.
    if hasattr(signature, 'total_inclusions'):
        if _recursion_guard is not None:
            _recursion_guard.root_total_inclusions.update(
                signature.total_inclusions)

    # But if we haven't calculated total inclusions yet, obviously we still
    # need to do that, regardless of whether or not this is a recursive call.
    else:
        total_inclusions: set[TemplateClass]
        if _recursion_guard is None:
            total_inclusions = {template_cls}
            recursion_guard = _TotalityRecursionGuard(
                root_template_cls=template_cls,
                root_total_inclusions=total_inclusions)
        else:
            total_inclusions = _recursion_guard.root_total_inclusions
            # Note: this MUST be before the recursive call, or it won't protect
            # against recursion!
            total_inclusions.add(template_cls)
            recursion_guard = _recursion_guard

        # Note that in addition to saving us work (both by deduping
        # and by reusing the results from creating the fieldset),
        # this also flattens unions, aliases, etc.
        direct_inclusions: set[TemplateClass] = set()
        for _, nested_slot_cls in signature.fieldset.slotpaths:
            # Note that these do NOT include dynamic slot classes!
            direct_inclusions.add(nested_slot_cls)

        # Don't forget that templates can include themselves as a slot!
        # (Also, the total_classes already includes it).
        # This is another protection against infinite recursion.
        direct_inclusions.discard(template_cls)
        for nested_slot_cls in direct_inclusions:
            if nested_slot_cls not in total_inclusions:
                nested_signature = cast(
                    type[TemplateIntersectable], nested_slot_cls
                )._templatey_signature
                ensure_recursive_totality(
                    nested_signature,
                    nested_slot_cls,
                    _recursion_guard=recursion_guard)

        # We only want to set the value if we're being called on the root;
        # nothing else is definitely correct!
        if _recursion_guard is None:
            # Note that this needs to be before the recursive call to
            # prevent infinite recursion
            signature.total_inclusions = frozenset(total_inclusions)

            # But we do actually need to ensure recursive totality, so then
            # we need to follow up with each and every one of the inclusions.
            for nested_inclusion in total_inclusions:
                nested_signature = cast(
                    type[TemplateIntersectable], nested_inclusion
                )._templatey_signature
                # Note the difference: no _root_template_cls!
                ensure_recursive_totality(nested_signature, nested_inclusion)


@dataclass(slots=True)
class _TotalityFrame:
    """When calculating totality, we need to resolve recursion loops
    (again). ``_TotalityFrame`` objects maintain the state we need to
    use a stack-based approach for that instead of the naive recursion
    option, which ends up in infinite recursion when you get to
    nontrivial recursion loops.

    TODO: this needs a better description, that's less sloppy and
    confusing. Point is, we use this to calculate recursive totality.
    """
    slot_cls: TemplateClass
    # Note: this gets mutated during processing
    remaining_direct_inclusions: set[TemplateClass]
    signature: TemplateSignature
    total_classes: set[TemplateClass] = field(init=False)
    recursion_sources: list[tuple[_TotalityFrame, ...]] = field(
        default_factory=list)

    def __post_init__(self):
        self.total_classes = {self.slot_cls}

    @classmethod
    def from_slot_cls(cls, slot_cls: TemplateClass) -> _TotalityFrame:
        signature = cast(
            type[TemplateIntersectable], slot_cls)._templatey_signature
        # Note that in addition to saving us work (both by deduping
        # and by reusing the results from creating the fieldset),
        # this also flattens unions, aliases, etc.
        direct_inclusions: set[TemplateClass] = set()
        for _, nested_slot_cls in signature.fieldset.slotpaths:
            # Note that these do NOT include dynamic slot classes!
            direct_inclusions.add(nested_slot_cls)

        # Don't forget that templates can include themselves as a slot!
        # (Also, the total_classes already includes it).
        # This prevents infinite recursion.
        direct_inclusions.discard(slot_cls)

        return cls(
            slot_cls=slot_cls,
            remaining_direct_inclusions=direct_inclusions,
            signature=signature)

    @property
    def exhausted(self) -> bool:
        return not bool(self.remaining_direct_inclusions)

    def extract_recursion_loop(
            self,
            stack: list[_TotalityFrame],
            recursion_target: _TotalityFrame
            ) -> tuple[_TotalityFrame, ...]:
        """Given the current stack, and an up-stack recursion target,
        extracts out just the frames that are part of the recursion
        loop.
        """
        target_frames: list[_TotalityFrame] = []
        target_encountered = False
        for frame in stack:
            if frame is recursion_target:
                target_encountered = True
            elif target_encountered:
                target_frames.append(frame)

        if not target_encountered:
            raise ValueError(
                'Recursion target not found in stack!',
                stack, recursion_target)

        return tuple(target_frames)


def ensure_slot_tree(
        signature: TemplateSignature,
        template_cls: TemplateClass,):
    """After ensuring recursive totality, call this to make sure
    that the slot tree is defined on the signature.

    This is meant to be called during loading (instead of, for example,
    during ``@template`` decoration time) because it maximizes the
    chances that all of the type hints are available (ie, no longer
    forward refs).
    """
    if not hasattr(signature, 'slot_tree'):
        signature.slot_tree = build_slot_tree(template_cls)


def ensure_prerender_tree(
        signature: TemplateSignature,
        preload: dict[TemplateClass, ParsedTemplateResource]):
    """After fully loading the underlying template and all of its
    inclusions, call this to make sure that the prerender tree is
    defined on the signature.

    This is meant to be called during loading (instead of, for example,
    during ``@template`` decoration time) because it maximizes the
    chances that all of the type hints are available (ie, no longer
    forward refs).
    """
    if not hasattr(signature, 'prerender_tree'):
        signature.prerender_tree = signature.slot_tree.distill_prerender_tree(
            preload)
