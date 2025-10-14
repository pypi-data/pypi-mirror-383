from typing import List, Optional
from .lexer import tokenize, Token
from .ast import Node, Literal, Name, Unary, Binary, Call


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def take(self, *types: str) -> Optional[Token]:
        t = self.peek()
        if t[0] in types:
            self.pos += 1
            return t
        return None

    def expect(self, typ: str) -> Token:
        t = self.peek()
        if t[0] != typ:
            raise SyntaxError(f"Expected {typ}, got {t}")
        self.pos += 1
        return t

    BP = {
        "OR": 10,
        "AND": 20,
        "NOT": 30,  # unary
        "EQ": 40,
        "NE": 40,
        "GT": 40,
        "LT": 40,
        "GE": 40,
        "LE": 40,
        "IN": 40,
    }

    def parse(self) -> Node:
        node = self.expression(0)
        if self.peek()[0] != "EOF":
            raise SyntaxError("Unexpected trailing input")
        return node

    def expression(self, rbp: int) -> Node:
        t = self.expect(self.peek()[0])
        left = self.nud(t)
        while True:
            t = self.peek()
            lbp = self.lbp(t)
            if lbp <= rbp:
                break
            self.expect(t[0])
            left = self.led(t, left)
        return left

    def lbp(self, t: Token) -> int:
        typ = t[0]
        if typ in ("AND", "OR", "EQ", "NE", "GT", "LT", "GE", "LE", "IN"):
            return self.BP[typ]
        return 0

    def nud(self, t: Token) -> Node:
        typ, val = t
        if typ == "LPAREN":
            expr = self.expression(0)
            self.expect("RPAREN")
            return expr
        if typ == "NUMBER":
            return Literal(val)
        if typ == "STRING":
            return Literal(val)
        if typ == "BOOL":
            return Literal(val)
        if typ == "NULL":
            return Literal(None)
        if typ == "IDENT":
            # function call or dotted name
            if self.take("LPAREN"):
                args: List[Node] = []
                if not self.take("RPAREN"):
                    while True:
                        args.append(self.expression(0))
                        if self.take("COMMA"):
                            continue
                        self.expect("RPAREN")
                        break
                return Call(val, args)
            parts = [val]
            while self.take("DOT"):
                nxt = self.expect("IDENT")
                parts.append(nxt[1])
            return Name(parts)
        if typ == "NOT":
            right = self.expression(self.BP["NOT"])
            return Unary("NOT", right)
        raise SyntaxError(f"Unexpected token: {t}")

    def led(self, t: Token, left: Node) -> Node:
        typ, _ = t
        if typ in ("AND", "OR", "EQ", "NE", "GT", "LT", "GE", "LE", "IN"):
            right = self.expression(self.BP[typ])
            return Binary(left, typ, right)
        raise SyntaxError(f"Unexpected infix token: {t}")


def parse(source: str) -> Node:
    return Parser(tokenize(source)).parse()
