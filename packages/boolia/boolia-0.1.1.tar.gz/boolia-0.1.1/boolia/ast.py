from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, List, Set

Resolver = Callable[[List[str]], Any]


class Node:
    def eval(self, resolve: Resolver, tags: Set[str], functions) -> Any:
        raise NotImplementedError()


@dataclass
class Literal(Node):
    value: Any

    def eval(self, resolve, tags, functions):
        return self.value


@dataclass
class Name(Node):
    parts: List[str]  # e.g., ["house","light","on"] or ["car"]

    def eval(self, resolve, tags, functions):
        if len(self.parts) == 1:
            name = self.parts[0]
            val = resolve(self.parts)
            # If missing policy returns None and tag is present, treat as True
            if val is None and name in tags:
                return True
            return val
        else:
            return resolve(self.parts)


@dataclass
class Unary(Node):
    op: str
    right: Node

    def eval(self, resolve, tags, functions):
        v = self.right.eval(resolve, tags, functions)
        if self.op == "NOT":
            return not bool(v)
        raise ValueError(f"Unknown unary op {self.op}")


@dataclass
class Binary(Node):
    left: Node
    op: str
    right: Node

    def eval(self, resolve, tags, functions):
        if self.op == "AND":
            return bool(self.left.eval(resolve, tags, functions)) and bool(self.right.eval(resolve, tags, functions))
        if self.op == "OR":
            return bool(self.left.eval(resolve, tags, functions)) or bool(self.right.eval(resolve, tags, functions))
        le = self.left.eval(resolve, tags, functions)
        r = self.right.eval(resolve, tags, functions)
        if self.op == "EQ":
            return le == r
        if self.op == "NE":
            return le != r
        if self.op == "GT":
            return le > r
        if self.op == "LT":
            return le < r
        if self.op == "GE":
            return le >= r
        if self.op == "LE":
            return le <= r
        if self.op == "IN":
            try:
                return le in r
            except TypeError:
                return False
        raise ValueError(f"Unknown binary op {self.op}")


@dataclass
class Call(Node):
    name: str
    args: List[Node]

    def eval(self, resolve, tags, functions):
        fn = functions.get(self.name)
        vals = [a.eval(resolve, tags, functions) for a in self.args]
        return fn(*vals)
