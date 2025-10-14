from typing import List, Tuple, Any

Token = Tuple[str, Any]  # (type, value)

KEYWORDS = {"and", "or", "not", "in", "true", "false", "null", "none"}
SYMS = {
    "(": "LPAREN",
    ")": "RPAREN",
    ".": "DOT",
    ",": "COMMA",
    "==": "EQ",
    "!=": "NE",
    ">=": "GE",
    "<=": "LE",
    ">": "GT",
    "<": "LT",
}


def tokenize(s: str) -> List[Token]:
    import re

    tokens: List[Token] = []
    i = 0
    n = len(s)
    ws = re.compile(r"\s+")
    ident = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
    number = re.compile(r"(?:\d+\.\d*|\d*\.\d+|\d+)")
    string = re.compile(r"""('([^'\\]|\\.)*'|"([^"\\]|\\.)*")""")

    while i < n:
        m = ws.match(s, i)
        if m:
            i = m.end()
        if i >= n:
            break

        if i + 1 < n and s[i : i + 2] in SYMS:
            tokens.append((SYMS[s[i : i + 2]], s[i : i + 2]))
            i += 2
            continue

        if s[i] in SYMS:
            tokens.append((SYMS[s[i]], s[i]))
            i += 1
            continue

        m = string.match(s, i)
        if m:
            raw = m.group(0)
            string_val = bytes(raw[1:-1], "utf-8").decode("unicode_escape")
            tokens.append(("STRING", string_val))
            i = m.end()
            continue

        m = number.match(s, i)
        if m:
            numtxt = m.group(0)
            number_val = float(numtxt) if "." in numtxt else int(numtxt)
            tokens.append(("NUMBER", number_val))
            i = m.end()
            continue

        m = ident.match(s, i)
        if m:
            name = m.group(0)
            low = name.lower()
            if low in KEYWORDS:
                if low == "true":
                    tokens.append(("BOOL", True))
                elif low == "false":
                    tokens.append(("BOOL", False))
                elif low in ("null", "none"):
                    tokens.append(("NULL", None))
                else:
                    tokens.append((low.upper(), low))  # AND, OR, NOT, IN
            else:
                tokens.append(("IDENT", name))
            i = m.end()
            continue

        raise SyntaxError(f"Unexpected character at {i}: {s[i]!r}")

    tokens.append(("EOF", None))
    return tokens
