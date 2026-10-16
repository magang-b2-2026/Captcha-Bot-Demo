import re


def solve_math_expression(text):
    if not text:
        return None

    cleaned = text.upper()

    cleaned = cleaned.replace(
        "X",
        "*"
    )

    cleaned = cleaned.replace(
        "×",
        "*"
    )

    match = re.search(
        r"(-?\d+)\s*([\+\-\*/])\s*(-?\d+)",
        cleaned
    )

    if not match:
        return None

    a = int(match.group(1))
    operator = match.group(2)
    b = int(match.group(3))

    if operator == "+":
        return a + b

    if operator == "-":
        return a - b

    if operator == "*":
        return a * b

    if operator == "/":
        if b == 0:
            return None

        return a / b

    return None