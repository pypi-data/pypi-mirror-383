from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, Literal, Optional, Set, Union

from .parser import parse
from .ast import Node
from .resolver import default_resolver_factory, MissingPolicy
from .functions import FunctionRegistry, DEFAULT_FUNCTIONS


RuleEntry = Union["Rule", "RuleGroup"]
RuleMember = Union[str, RuleEntry]


def compile_expr(source: str) -> Node:
    return parse(source)


def evaluate(
    source_or_ast: Union[str, Node],
    *,
    context: Optional[Dict[str, Any]] = None,
    tags: Optional[Set[str]] = None,
    resolver=None,
    on_missing: MissingPolicy = "false",
    default_value: Any = None,
    functions: Optional[FunctionRegistry] = None,
) -> bool:
    node = compile_expr(source_or_ast) if isinstance(source_or_ast, str) else source_or_ast
    ctx = context or {}
    tg = tags or set()
    res = resolver or default_resolver_factory(ctx, on_missing=on_missing, default_value=default_value)
    fns = functions or DEFAULT_FUNCTIONS
    out = node.eval(res, tg, fns)
    return bool(out)


@dataclass
class Rule:
    ast: Node

    def evaluate(self, **kwargs) -> bool:
        return evaluate(self.ast, **kwargs)


def compile_rule(source: str) -> Rule:
    return Rule(compile_expr(source))


class RuleGroup:
    def __init__(
        self,
        *,
        mode: Literal["all", "any"] = "all",
        members: Iterable[RuleMember] = (),
    ) -> None:
        if mode not in {"all", "any"}:
            raise ValueError("RuleGroup mode must be 'all' or 'any'")
        self.mode = mode
        self._members = list(members)
        self._rule_lookup: Optional[Callable[[str], RuleEntry]] = None

    @property
    def members(self):
        return tuple(self._members)

    def add(self, member: RuleMember) -> "RuleGroup":
        self._members.append(member)
        if isinstance(member, RuleGroup) and self._rule_lookup is not None:
            member.bind_lookup(self._rule_lookup)
        return self

    def extend(self, members: Iterable[RuleMember]) -> "RuleGroup":
        for member in members:
            self.add(member)
        return self

    def bind_lookup(self, lookup: Callable[[str], RuleEntry]) -> None:
        self._rule_lookup = lookup
        for member in self._members:
            if isinstance(member, RuleGroup):
                member.bind_lookup(lookup)

    def evaluate(self, **kwargs) -> bool:
        return self._evaluate(kwargs, set())

    def _evaluate(self, kwargs: Dict[str, Any], stack: Set[int]) -> bool:
        ident = id(self)
        if ident in stack:
            raise ValueError("Cycle detected while evaluating RuleGroup")
        stack.add(ident)
        try:
            if self.mode == "all":
                for member in self._members:
                    if not self._eval_member(member, kwargs, stack):
                        return False
                return True
            for member in self._members:
                if self._eval_member(member, kwargs, stack):
                    return True
            return False
        finally:
            stack.remove(ident)

    def _eval_member(self, member: RuleMember, kwargs: Dict[str, Any], stack: Set[int]) -> bool:
        if isinstance(member, RuleGroup):
            return member._evaluate(kwargs, stack)
        if isinstance(member, Rule):
            return member.evaluate(**kwargs)
        if isinstance(member, str):
            if self._rule_lookup is None:
                raise ValueError("RuleGroup with named members requires binding to a RuleBook")
            target = self._rule_lookup(member)
            if isinstance(target, RuleGroup):
                return target._evaluate(kwargs, stack)
            return target.evaluate(**kwargs)
        raise TypeError(f"Unsupported RuleGroup member type: {type(member)!r}")


class RuleBook:
    def __init__(self):
        self._rules: Dict[str, RuleEntry] = {}

    def add(self, name: str, source: str) -> Rule:
        r = compile_rule(source)
        self._store(name, r)
        return r

    def add_group(
        self,
        name: str,
        *,
        mode: Literal["all", "any"] = "all",
        members: Iterable[RuleMember] = (),
    ) -> RuleGroup:
        group = RuleGroup(mode=mode, members=members)
        self._store(name, group)
        return group

    def register(self, name: str, rule: RuleEntry) -> RuleEntry:
        self._store(name, rule)
        return rule

    def replace(self, name: str, source: str) -> Rule:
        return self.add(name, source)

    def get(self, name: str) -> RuleEntry:
        if name not in self._rules:
            raise KeyError(f"Unknown rule: {name}")
        return self._rules[name]

    def evaluate(self, name: str, **kwargs) -> bool:
        return self.get(name).evaluate(**kwargs)

    def names(self):
        return list(self._rules.keys())

    def _store(self, name: str, rule: RuleEntry) -> None:
        self._rules[name] = rule
        if isinstance(rule, RuleGroup):
            rule.bind_lookup(self.get)
