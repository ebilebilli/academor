"""Shared machinery for the Academor SAT Math practice tests 2–10.

Every question comes from a template that computes its own answer, so the answer key is
correct by construction. Templates return a *spec*; the assembler (build_sat_academor_math_set.py)
decides the option order (numeric choices ascend, as on the real test), balances the answer
letters and turns the spec into the JSON row the portal loader expects.

Spec kinds
  num   numeric answer; MC options are built from the template's error-based distractors
        (``plausible``), filled with nearby values when needed; can also become an SPR item
  text  non-numeric answer (expressions, interpretations, statements); MC only
  spr   student-produced response only (answers given explicitly)
"""

from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_sat_academor_math as base  # noqa: E402  (figure + HTML helpers of test 1)

v, frac, p = base.v, base.frac, base.p
MINUS = base.MINUS
X, Y = base.X, base.Y
LETTERS = "ABCD"

ALG, ADV, PSDA, GEO = base.ALG, base.ADV, base.PSDA, base.GEO

F = Fraction


# ---------------------------------------------------------------------------
# number formatting
# ---------------------------------------------------------------------------

def as_frac(value) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, float):
        return Fraction(value).limit_denominator(10000)
    return Fraction(value)


def n(value, comma=True) -> str:
    """HTML for a number: true minus sign, thousands commas, stacked fractions."""
    value = as_frac(value)
    sign = MINUS if value < 0 else ""
    value = abs(value)
    if value.denominator == 1:
        whole = int(value)
        return sign + (f"{whole:,}" if comma else str(whole))
    return sign + frac(str(value.numerator), str(value.denominator))


def np(value) -> str:
    """Number for use inside an expression: negatives in parentheses, e.g. 4 − (−7)."""
    value = as_frac(value)
    return f"({n(value)})" if value < 0 else n(value)


def coef(value, var) -> str:
    """'x', '−x', '3x', '½x' — a coefficient written the usual way."""
    value = as_frac(value)
    if value == 1:
        return var
    if value == -1:
        return MINUS + var
    return n(value) + var


def dec(value, places=2) -> str:
    """Decimal display (for money, measurements)."""
    value = as_frac(value)
    text = f"{float(abs(value)):,.{places}f}"
    return (MINUS if value < 0 else "") + text


def money(value) -> str:
    value = as_frac(value)
    if value.denominator == 1:
        return f"${int(value):,}"
    return f"${float(value):,.2f}"


def signed(coef, var="", first=False) -> str:
    """'+ 3x' / '− 3x' pieces for writing polynomials; ``first`` drops a leading '+'."""
    coef = as_frac(coef)
    if coef == 0:
        return ""
    mag = abs(coef)
    if var and mag == 1:
        body = var
    else:
        body = n(mag, comma=False) + var
    if first:
        return (MINUS if coef < 0 else "") + body
    return (f" {MINUS} " if coef < 0 else " + ") + body


def poly(*terms) -> str:
    """poly((a, 'x²'), (b, 'x'), (c, '')) -> 'ax² + bx − c' with clean signs."""
    out = ""
    for coef, var in terms:
        piece = signed(coef, var, first=(out == ""))
        out += piece
    return out or "0"


X2 = f"{X}<sup>2</sup>"


def spr_answers(value) -> list[str]:
    """Accepted SPR entries for a value: integer, fraction and terminating decimal forms."""
    value = as_frac(value)
    neg = value < 0
    mag = abs(value)
    sign = "-" if neg else ""
    if mag.denominator == 1:
        return [f"{sign}{mag.numerator}"]
    forms = [f"{sign}{mag.numerator}/{mag.denominator}"]
    den = mag.denominator
    while den % 2 == 0:
        den //= 2
    while den % 5 == 0:
        den //= 5
    if den == 1:
        text = f"{float(mag):.6f}".rstrip("0").rstrip(".")
        forms.append(f"{sign}{text}")
        if text.startswith("0."):
            forms.append(f"{sign}{text[1:]}")
    else:
        # repeating decimal: the SAT accepts the most accurate truncation / rounding that fits
        for places in (4, 3):
            text = f"{float(mag):.{places}f}"
            if len(sign + text) <= 6:
                forms.append(sign + text)
                if text.startswith("0."):
                    forms.append(sign + text[1:])
                break
    return [f for f in dict.fromkeys(forms) if len(f) <= 6]


# ---------------------------------------------------------------------------
# specs
# ---------------------------------------------------------------------------

def num(domain, skill, html, correct, plausible, why, *, fmt=n, lo=None, hi=None, step=None,
        spr_ok=True, spr_value=None, int_only=None):
    """Numeric-answer spec. ``plausible`` are error-based distractor values (most likely first).

    When the answer is a whole number, the wrong choices are whole numbers too (``int_only``),
    unless a template asks for fractional distractors on purpose.
    """
    correct_f = as_frac(correct)
    if int_only is None:
        int_only = correct_f.denominator == 1
    return {
        "int_only": int_only,
        "kind": "num", "domain": domain, "skill": skill, "html": html, "why": why,
        "correct": as_frac(correct), "plausible": [as_frac(x) for x in plausible],
        "fmt": fmt, "lo": None if lo is None else as_frac(lo), "hi": None if hi is None else as_frac(hi),
        "step": None if step is None else as_frac(step), "spr_ok": spr_ok,
        "spr_value": None if spr_value is None else as_frac(spr_value),
    }


def text(domain, skill, html, correct, distractors, why):
    assert len(distractors) == 3, (skill, distractors)
    assert correct not in distractors and len(set(distractors)) == 3, (skill, correct, distractors)
    return {"kind": "text", "domain": domain, "skill": skill, "html": html, "why": why,
            "correct": correct, "distractors": list(distractors)}


def spr_only(domain, skill, html, value, why):
    return {"kind": "spr", "domain": domain, "skill": skill, "html": html, "why": why,
            "answers": spr_answers(value), "value": as_frac(value)}


# ---------------------------------------------------------------------------
# option placement
# ---------------------------------------------------------------------------

def _default_step(correct: Fraction) -> Fraction:
    mag = abs(correct)
    if correct.denominator != 1:
        return Fraction(1, correct.denominator)
    if mag >= 1000:
        return Fraction(max(1, int(mag) // 10 // 10 * 10))
    if mag >= 100:
        return Fraction(max(1, int(mag) // 10))
    if mag >= 20:
        return Fraction(max(1, int(mag) // 5))
    return Fraction(1)


def numeric_options(spec, target: int):
    """Choices in ascending order with the correct one at index ``target``; None if impossible."""
    c = spec["correct"]
    lo, hi = spec["lo"], spec["hi"]

    int_only = spec.get("int_only")

    def ok(x):
        return (x != c and (lo is None or x >= lo) and (hi is None or x <= hi)
                and (not int_only or x.denominator == 1))

    cands = []
    for x in spec["plausible"]:
        if ok(x) and x not in cands:
            cands.append(x)
    below = [x for x in cands if x < c][: target]
    above = [x for x in cands if x > c][: 3 - target]
    step = spec["step"] or _default_step(c)
    k = 1
    while len(below) < target and k < 40:
        x = c - step * k
        if ok(x) and x not in below:
            below.append(x)
        k += 1
    k = 1
    while len(above) < 3 - target and k < 40:
        x = c + step * k
        if ok(x) and x not in above:
            above.append(x)
        k += 1
    if len(below) != target or len(above) != 3 - target:
        return None
    spec.setdefault("_fill", {})[target] = sum(1 for x in below + above if x not in cands)
    values = sorted(below) + [c] + sorted(above)
    texts = [spec["fmt"](x) for x in values]
    if len(set(texts)) != 4:
        return None
    return texts


def text_options(spec, target: int):
    others = list(spec["distractors"])
    return others[:target] + [spec["correct"]] + others[target:]
