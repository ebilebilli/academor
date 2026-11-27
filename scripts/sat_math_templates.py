"""Question templates for the Academor SAT Math practice tests 2–10.

Each template takes a ``random.Random`` and returns a spec from sat_math_core. Templates are
registered with their domain, difficulty level (1 easy, 2 medium, 3 hard) and whether they
can be used as a multiple-choice item, a student-produced response (SPR) item, or both.
All contexts, names and numbers are invented for these tests.
"""

from __future__ import annotations

import math
from fractions import Fraction as F

from sat_math_core import (
    ADV, ALG, GEO, MINUS, PSDA, X, X2, Y, base, coef, dec, frac, money, n, np, num, p, poly, signed,
    spr_only, text, v,
)

TEMPLATES: list[dict] = []


def tpl(domain, level, modes=("mc", "spr")):
    def wrap(fn):
        TEMPLATES.append({"name": fn.__name__, "domain": domain, "level": level, "modes": modes, "fn": fn})
        return fn
    return wrap


def pick(rng, items):
    return items[rng.randrange(len(items))]


def nz(rng, lo, hi, exclude=(0,)):
    while True:
        x = rng.randint(lo, hi)
        if x not in exclude:
            return x


def eq(lhs, rhs):
    return f"{lhs} = {rhs}"


# ===========================================================================
# ALGEBRA
# ===========================================================================

S_LIN1 = "Linear equations in one variable"
S_LINF = "Linear functions"
S_LIN2 = "Linear equations in two variables"
S_SYS = "Systems of two linear equations in two variables"
S_INEQ = "Linear inequalities in one or two variables"


@tpl(ALG, 1)
def lin_eq_basic(rng):
    a, x = rng.randint(3, 9), rng.randint(3, 14)
    b = rng.randint(2, 20)
    c = a * x + b
    html = p(f"If {a}{X} + {b} = {c}, what is the value of {X}?")
    why = f"Subtract {b} from both sides: {a}{X} = {c - b}. Divide by {a}: {X} = {x}."
    return num(ALG, S_LIN1, html, x, [F(c + b, a), F(c, a), c - b, x + b], why, int_only=False)


@tpl(ALG, 1)
def lin_eq_grouped(rng):
    k, m, val = rng.randint(2, 6), rng.randint(2, 9), rng.randint(3, 12)
    total = k * val
    html = p(f"If {k}({X} {MINUS} {m}) = {total}, what is the value of {X} {MINUS} {m}?")
    why = f"Divide both sides by {k}: {X} {MINUS} {m} = {total} ÷ {k} = {val}. There is no need to find {X}."
    return num(ALG, S_LIN1, html, val, [val + m, total - k, total, val - m], why, lo=1)


@tpl(ALG, 1)
def lin_fixed_plus_rate(rng):
    ctx = pick(rng, [
        ("A climbing gym charges a one-time membership fee of ${fee} plus ${rate} for each visit. "
         "A member has paid ${total} in total for the membership fee and visits. How many visits has the member paid for?",
         "visits"),
        ("A plumber charges a ${fee} call-out fee plus ${rate} per hour of work. A customer's bill was ${total}. "
         "For how many hours did the plumber work?", "hours"),
        ("A school club pays ${fee} to rent a bus and ${rate} for each student who goes on the trip. "
         "The club paid ${total} in total. How many students went on the trip?", "students"),
    ])
    fee, rate, units = rng.randint(3, 12) * 5, rng.randint(6, 30), rng.randint(5, 18)
    total = fee + rate * units
    html = p(ctx[0].format(fee=fee, rate=rate, total=f"{total:,}"))
    why = f"Set up {fee} + {rate}{v('n')} = {total}. Then {rate}{v('n')} = {total - fee}, so {v('n')} = {units}."
    return num(ALG, S_LIN1, html, units, [F(total, rate), F(total + fee, rate), units + 1], why, lo=1)


@tpl(ALG, 1)
def eval_linear_function(rng):
    a, b, k = nz(rng, -6, 7, (0, 1)), rng.randint(-12, 15), rng.randint(-5, 8)
    val = a * k + b
    fx = poly((a, X), (b, ""))
    html = p(f"The function {v('f')} is defined by {v('f')}({X}) = {fx}. What is the value of {v('f')}({n(k)})?")
    why = f"Substitute {X} = {n(k)}: {v('f')}({n(k)}) = {n(a)}({n(k)}) + {n(b)} = {n(val)}."
    return num(ALG, S_LINF, html, val, [a * k - b, a + k + b, a * (k + b)], why)


@tpl(ALG, 1)
def slope_two_points(rng):
    while True:
        x1, y1 = rng.randint(-6, 4), rng.randint(-6, 8)
        dx, dy = rng.randint(1, 6), nz(rng, -9, 9)
        if F(dy, dx).denominator <= 3:
            break
    x2, y2 = x1 + dx, y1 + dy
    m = F(dy, dx)
    html = p(f"A line in the {X}{Y}-plane passes through the points ({n(x1)}, {n(y1)}) and ({n(x2)}, {n(y2)}). "
             "What is the slope of the line?")
    why = f"Slope = (change in {Y}) ÷ (change in {X}) = ({n(y2)} {MINUS} {np(y1)}) ÷ ({n(x2)} {MINUS} {np(x1)}) = {n(m)}."
    plaus = [F(dx, dy), -m, F(-dx, dy)]
    return num(ALG, S_LINF, html, m, plaus, why)


@tpl(ALG, 2)
def system_value(rng):
    while True:
        x, y = rng.randint(-4, 9), rng.randint(-4, 9)
        a, b, d, e = nz(rng, 1, 5), nz(rng, -4, 5), nz(rng, 1, 5), nz(rng, -4, 5)
        if a * e - b * d != 0 and x != y:
            break
    c, f = a * x + b * y, d * x + e * y
    ask_x = rng.random() < 0.5
    html = (p(f"{poly((a, X), (b, Y))} = {n(c)}<br>{poly((d, X), (e, Y))} = {n(f)}")
            + p(f"If ({X}, {Y}) is the solution to the system of equations above, what is the value of "
                f"{X if ask_x else Y}?"))
    ans, other = (x, y) if ask_x else (y, x)
    why = (f"Solve by elimination or substitution: the solution is {X} = {n(x)}, {Y} = {n(y)}. "
           f"So {X if ask_x else Y} = {n(ans)}.")
    return num(ALG, S_SYS, html, ans, [other, -ans, ans + other], why)


@tpl(ALG, 2, ("mc",))
def interpret_linear_model(rng):
    ctx = pick(rng, [
        ("C", "m", "the cost, in dollars, of a taxi ride of {v} miles", "dollars per mile",
         "The cost per mile of the ride, in dollars", "The fixed starting fee of the ride, in dollars",
         "The total cost, in dollars, of a 1-mile ride", "The number of miles the taxi travels for each dollar"),
        ("W", "d", "the amount of water, in liters, left in a tank {v} days after it was filled", "liters per day",
         None, None, None, None),
        ("P", "h", "the pay, in dollars, a tutor earns for {v} hours of tutoring", "dollars per hour",
         "The amount the tutor earns for each hour of tutoring, in dollars", "A fixed fee the tutor charges per session, in dollars",
         "The total amount earned for 1 hour, in dollars", "The number of hours worked for each dollar earned"),
    ])
    out, var = ctx[0], ctx[1]
    if out == "W":
        r, b = rng.randint(3, 15), rng.randint(20, 60) * 10
        model = f"{v('W')} = {b} {MINUS} {r}{v('d')}"
        html = p(f"The equation {model} gives {ctx[2].format(v=v(var))}. What is the best interpretation of {r} in this context?")
        correct = "The tank loses " + f"{r} liters of water each day."
        wrong = [f"The tank holds {r} liters when it is full.", f"The tank is empty after {r} days.",
                 f"The tank gains {r} liters of water each day."]
        why = f"{r} is the rate of change: each additional day lowers {v('W')} by {r} liters."
        return text(ALG, S_LIN2, html, correct, wrong, why)
    r, b = rng.randint(2, 9) + (F(1, 2) if rng.random() < 0.5 and out == "C" else 0), rng.randint(3, 12)
    ask_rate = rng.random() < 0.6
    model = f"{v(out)} = {dec(r, 2 if F(r).denominator != 1 else 0)}{v(var)} + {b}"
    target = dec(r, 2 if F(r).denominator != 1 else 0) if ask_rate else str(b)
    html = p(f"The equation {model} gives {ctx[2].format(v=v(var))}. What is the best interpretation of {target} in this context?")
    if ask_rate:
        correct, wrong = ctx[4], [ctx[5], ctx[6], ctx[7]]
        why = f"{target} multiplies {v(var)}, so it is the rate: {ctx[3]}."
    else:
        correct, wrong = ctx[5], [ctx[4], ctx[6], ctx[7]]
        why = f"{target} is the value of {v(out)} when {v(var)} = 0: the fixed amount charged regardless of {v(var)}."
    return text(ALG, S_LIN2, html, correct, wrong, why)


@tpl(ALG, 2, ("mc",))
def inequality_model(rng):
    cap = rng.randint(8, 20) * 100
    w0, each = rng.randint(6, 12) * 10, rng.randint(15, 45)
    who = pick(rng, [("elevator", "an operator", "crate"), ("delivery van", "the driver", "box"),
                     ("cargo lift", "a worker", "package")])
    var = v("b")
    art = "An" if who[0][0] in "aeiou" else "A"
    html = p(f"{art} {who[0]} can carry a load of at most {cap:,} kilograms. {who[1].capitalize()} weighs {w0} kilograms, "
             f"and each {who[2]} weighs {each} kilograms. Which inequality represents the possible numbers of {who[2]}s, "
             f"{var}, that the {who[0]} can carry along with {who[1]}?")
    correct = f"{w0} + {each}{var} &le; {cap:,}"
    wrong = [f"{w0} + {each}{var} &ge; {cap:,}", f"{each} + {w0}{var} &le; {cap:,}", f"{w0}{var} + {each}{var} &le; {cap:,}"]
    why = f"The total weight {w0} + {each}{var} can be at most (&le;) {cap:,} kilograms."
    return text(ALG, S_INEQ, html, correct, wrong, why)


@tpl(ALG, 2, ("mc",))
def line_from_graph(rng):
    while True:
        b = rng.randint(-3, 4)
        run, rise = pick(rng, [(1, 2), (2, 1), (3, 1), (1, 3), (2, 3), (3, 2), (1, 1)]), None
        sign = pick(rng, [1, -1])
        rise, run = run[1] * sign, run[0]
        x2 = run * (2 if run < 3 else 1)
        y2 = b + rise * x2 // run
        if -5 <= y2 <= 6 and x2 <= 7:
            break
    m = F(rise, run)
    fig = base.coord_plane((-3, 7), (-5, 6), curves=[(lambda xx, m=m, b=b: float(m) * xx + b, -3, 7)],
                           points=[(0, b), (x2, y2)], label_every=2, size=(4.2, 4.0),
                           alt=f"Graph of a line through (0, {b}) and ({x2}, {y2})")

    def expr(slope, icpt):
        s = "" if slope == 1 else (MINUS if slope == -1 else n(slope))
        if slope.denominator != 1:
            s = (MINUS if slope < 0 else "") + frac(str(abs(slope.numerator)), str(slope.denominator))
        return f"{v('f')}({X}) = {s}{X}" + signed(icpt, "") if icpt else f"{v('f')}({X}) = {s}{X}"

    correct = expr(m, b)
    cands = [expr(-m, b), expr(1 / m if m else F(1), b), expr(m, -b if b else b + 2), expr(-1 / m, b), expr(m, b + 1)]
    wrong = []
    for c in cands:
        if c != correct and c not in wrong:
            wrong.append(c)
    html = p(f"The graph of the linear function {v('f')} is shown.") + fig + p(f"Which equation defines {v('f')}?")
    why = (f"The line crosses the {Y}-axis at (0, {n(b)}), so the {Y}-intercept is {n(b)}. "
           f"From (0, {n(b)}) to ({x2}, {n(y2)}) the slope is {n(y2 - b)} ÷ {x2} = {n(m)}.")
    return text(ALG, S_LINF, html, correct, wrong[:3], why)


@tpl(ALG, 2)
def parallel_line_intercept(rng):
    m = F(nz(rng, -5, 5), pick(rng, [1, 1, 2, 3]))
    b0 = rng.randint(-6, 6)
    x0 = rng.randint(-4, 6) * (m.denominator)
    y0 = rng.randint(-6, 10)
    b = y0 - m * x0
    html = p(f"Line {v('k')} is defined by {Y} = {coef(m, X)}{signed(b0, '')}. Line {v('j')} is parallel to "
             f"line {v('k')} and passes through the point ({n(x0)}, {n(y0)}). What is the {Y}-intercept of line {v('j')}?")
    why = (f"Parallel lines have equal slopes, so line {v('j')} is {Y} = {coef(m, X)} + {v('b')}. Substituting "
           f"({n(x0)}, {n(y0)}): {n(y0)} = {n(m)}({n(x0)}) + {v('b')}, so {v('b')} = {n(b)}.")
    return num(ALG, S_LINF, html, b, [y0 + m * x0, b0, y0], why)


@tpl(ALG, 2)
def linear_table(rng):
    a, b = nz(rng, -5, 6, (0,)), rng.randint(-8, 12)
    xs = sorted(rng.sample(range(-2, 7), 3))
    k = rng.randint(8, 15)
    rows = [[str(x).replace("-", MINUS), str(a * x + b).replace("-", MINUS)] for x in xs]
    fig = base.table_figure([f"x", f"f(x)"], rows, "Table of values of a linear function f", width=220)
    html = (p(f"The table shows three values of {X} and their corresponding values of {v('f')}({X}), "
              f"where {v('f')} is a linear function.") + fig + p(f"What is the value of {v('f')}({k})?"))
    val = a * k + b
    why = (f"The slope is ({n(a * xs[1] + b)} {MINUS} {np(a * xs[0] + b)}) ÷ ({n(xs[1])} {MINUS} {np(xs[0])}) = {n(a)}, and "
           f"{v('f')}(0) = {n(b)}. So {v('f')}({X}) = {poly((a, X), (b, ''))} and {v('f')}({k}) = {n(val)}.")
    return num(ALG, S_LINF, html, val, [a * k, a * k - b, val + a], why)


@tpl(ALG, 2)
def two_var_context(rng):
    pa, pb = rng.randint(3, 9), rng.randint(10, 18)
    na, nb = rng.randint(4, 15), rng.randint(2, 9)
    total = pa * na + pb * nb
    item = pick(rng, [("small notebooks", "large notebooks", "A school store sells"),
                      ("adult tickets", "student tickets", "A theater sold")])
    if item[0] == "adult tickets":
        pa, pb = pb, pa
        total = pa * na + pb * nb
    html = p(f"{item[2]} {item[0]} for ${pa} each and {item[1]} for ${pb} each. The equation "
             f"{pa}{v('a')} + {pb}{v('b')} = {total:,} represents a day on which ${total:,} was collected from "
             f"{v('a')} {item[0]} and {v('b')} {item[1]}. If {nb} {item[1]} were sold that day, how many {item[0]} were sold?")
    why = f"Substitute {v('b')} = {nb}: {pa}{v('a')} + {pb * nb} = {total}, so {pa}{v('a')} = {total - pb * nb} and {v('a')} = {na}."
    return num(ALG, S_LIN2, html, na, [F(total, pa), F(total - nb, pa), na + nb], why, lo=1)


@tpl(ALG, 2)
def fraction_equation(rng):
    a, b = pick(rng, [(2, 3), (3, 4), (2, 5), (4, 6), (3, 6), (2, 4)])
    lcm = a * b // math.gcd(a, b)
    x = lcm * rng.randint(1, 4)
    c = F(x, a) + F(x, b)
    html = p(f"If {frac(X, str(a))} + {frac(X, str(b))} = {n(c)}, what is the value of {X}?")
    why = (f"Multiply both sides by {lcm}: {lcm // a}{X} + {lcm // b}{X} = {n(c * lcm)}, so "
           f"{lcm // a + lcm // b}{X} = {n(c * lcm)} and {X} = {x}.")
    return num(ALG, S_LIN1, html, x, [c * (a + b), F(c * lcm), c * a * b / (a + b) * 2], why, lo=1, int_only=False)


@tpl(ALG, 3)
def system_no_solution(rng):
    a, b = nz(rng, 2, 7), nz(rng, 2, 7)
    while math.gcd(a, b) != 1:
        b = nz(rng, 2, 7)
    k = rng.randint(2, 4)
    c = rng.randint(3, 15)
    d = c * k + rng.randint(1, 9)
    html = (p(f"{a}{X} + {b}{Y} = {c}<br>{v('r')}{X} + {b * k}{Y} = {d}")
            + p(f"In the system of equations above, {v('r')} is a constant. If the system has no solution, "
                f"what is the value of {v('r')}?"))
    why = (f"A system of two linear equations has no solution when the lines are parallel: the coefficients of "
           f"{X} and {Y} are proportional but the constants are not. The {Y}-coefficient is multiplied by {k}, so "
           f"{v('r')} = {a} × {k} = {a * k} (and {c} × {k} = {c * k} &ne; {d}).")
    return num(ALG, S_SYS, html, a * k, [b * k, a + k, F(b * k * a, b) + a, a], why, lo=1)


@tpl(ALG, 3)
def infinitely_many(rng):
    k, m, c = rng.randint(2, 6), rng.randint(1, 8), rng.randint(1, 12)
    a = k
    b = k * m + c
    html = p(f"In the equation {a}{X} + {v('b')} = {k}({X} + {m}) + {c}, {v('b')} is a constant. If the equation has "
             f"infinitely many solutions, what is the value of {v('b')}?")
    why = (f"Expand the right side: {k}{X} + {k * m} + {c} = {k}{X} + {k * m + c}. The equation is true for every "
           f"{X} only when {v('b')} = {b}.")
    return num(ALG, S_LIN1, html, b, [k * m, m + c, k * (m + c)], why, lo=1)


@tpl(ALG, 3)
def system_word(rng):
    pa, pb = rng.randint(4, 9), rng.randint(10, 16)
    na, nb = rng.randint(10, 40), rng.randint(10, 40)
    count, total = na + nb, pa * na + pb * nb
    item = pick(rng, [("bags of rice", "bags of beans", "A food bank received"),
                      ("paperback books", "hardcover books", "A library bought"),
                      ("small plants", "large plants", "A garden center sold")])
    html = p(f"{item[2]} a total of {count} {item[0].split()[-1] if 'books' in item[0] else 'items'}: {item[0]} costing "
             f"${pa} each and {item[1]} costing ${pb} each. The total cost was ${total:,}. How many {item[1]} were there?")
    why = (f"Let {v('s')} and {v('l')} be the numbers of {item[0]} and {item[1]}. Then {v('s')} + {v('l')} = {count} and "
           f"{pa}{v('s')} + {pb}{v('l')} = {total}. Multiply the first equation by {pa} and subtract: "
           f"{pb - pa}{v('l')} = {total - pa * count}, so {v('l')} = {nb}.")
    return num(ALG, S_SYS, html, nb, [na, count // 2, nb + (pb - pa)], why, lo=1, hi=count - 1)


@tpl(ALG, 3)
def inequality_largest_integer(rng):
    a, b = rng.randint(3, 8), rng.randint(5, 30)
    c = rng.randint(30, 90)
    # a x - b < c  ->  x < (c + b)/a
    bound = F(c + b, a)
    largest = math.ceil(bound) - 1
    html = p(f"What is the greatest integer value of {X} that satisfies the inequality {a}{X} {MINUS} {b} &lt; {c}?")
    why = (f"Add {b}: {a}{X} &lt; {c + b}. Divide by {a}: {X} &lt; {n(bound)}. "
           f"The greatest integer less than {n(bound)} is {largest}.")
    return num(ALG, S_INEQ, html, largest, [largest + 1, math.floor(F(c - b, a)), math.floor(F(c, a))], why)


@tpl(ALG, 3)
def perpendicular_slope(rng):
    a, b = nz(rng, -6, 6), nz(rng, 2, 7)
    c = rng.randint(-10, 12)
    m = F(-a, b)
    perp = -1 / m
    html = p(f"Line {v('p')} is defined by {poly((a, X), (b, Y))} = {n(c)}. Line {v('q')} is perpendicular to line {v('p')} in "
             f"the {X}{Y}-plane. What is the slope of line {v('q')}?")
    why = (f"Write line {v('p')} in slope-intercept form: {Y} = {coef(m, X)}{signed(F(c, b), '')}, so its slope is {n(m)}. "
           f"Perpendicular slopes are negative reciprocals: {n(perp)}.")
    return num(ALG, S_LINF, html, perp, [m, -m, 1 / m], why)


@tpl(ALG, 3)
def linear_decrease_time(rng):
    v0 = rng.randint(18, 40) * 1000
    d = rng.randint(12, 30) * 100
    years = rng.randint(4, 9)
    w = v0 - d * years
    thing = pick(rng, ["a delivery truck", "a printing machine", "a tractor"])
    html = p(f"The value of {thing} was ${v0:,} when it was new and decreases by ${d:,} each year. After how many years "
             f"will the value of the {thing.split(' ', 1)[1]} be ${w:,}?")
    why = f"Solve {v0} {MINUS} {d}{v('t')} = {w}: {d}{v('t')} = {v0 - w}, so {v('t')} = {years}."
    return num(ALG, S_LINF, html, years, [F(w, d), F(v0, d) - years, years + 1], why, lo=1)


@tpl(ALG, 3)
def coefficient_from_solution(rng):
    x0 = rng.randint(2, 9)
    a, c, d = rng.randint(2, 9), rng.randint(2, 7), rng.randint(-10, 20)
    if a == c:
        a += 1
    b = (c * x0 + d) - a * x0
    html = p(f"In the equation {a}{X} + {v('k')} = {c}{X}{signed(d, '')}, {v('k')} is a constant. If {X} = {x0} is the solution "
             f"to the equation, what is the value of {v('k')}?")
    why = f"Substitute {X} = {x0}: {a * x0} + {v('k')} = {c * x0 + d}, so {v('k')} = {n(b)}."
    return num(ALG, S_LIN1, html, b, [-b, c * x0 + d, b + a], why)


@tpl(ALG, 3)
def intersection_sum(rng):
    while True:
        m1, m2 = nz(rng, -4, 5), nz(rng, -4, 5)
        if m1 != m2:
            break
    x0, y0 = rng.randint(-5, 6), rng.randint(-6, 8)
    b1, b2 = y0 - m1 * x0, y0 - m2 * x0
    html = p(f"The graphs of {Y} = {poly((m1, X), (b1, ''))} and {Y} = {poly((m2, X), (b2, ''))} intersect at the point "
             f"({v('a')}, {v('b')}) in the {X}{Y}-plane. What is the value of {v('a')} + {v('b')}?")
    why = (f"Set the expressions equal: {poly((m1, X), (b1, ''))} = {poly((m2, X), (b2, ''))}, so {X} = {n(x0)}. "
           f"Then {Y} = {n(y0)}, and {v('a')} + {v('b')} = {n(x0 + y0)}.")
    return num(ALG, S_SYS, html, x0 + y0, [x0, y0, x0 - y0], why)


# ===========================================================================
# ADVANCED MATH
# ===========================================================================

S_EQV = "Equivalent expressions"
S_NLF = "Nonlinear functions"
S_NLE = "Nonlinear equations in one variable and systems of equations in two variables"


def q2(a, b, c):
    return poly((a, X2), (b, X), (c, ""))


@tpl(ADV, 1, ("mc",))
def poly_subtract(rng):
    a, b, c = rng.randint(3, 8), nz(rng, -8, 8), nz(rng, -9, 9)
    d = rng.randint(1, a - 1)
    e = nz(rng, -8, 8, (0, b, -b))
    f = nz(rng, -9, 9, (0, c, -c))
    html = p(f"Which expression is equivalent to ({q2(a, b, c)}) {MINUS} ({q2(d, e, f)})?")
    correct = q2(a - d, b - e, c - f)
    cands = [q2(a - d, b + e, c + f), q2(a + d, b + e, c + f), q2(a - d, b - e, c + f), q2(a - d, b + e, c - f)]
    wrong = []
    for x in cands:
        if x != correct and x not in wrong:
            wrong.append(x)
    why = f"Distribute the minus sign to every term of the second expression, then combine like terms: {correct}."
    return text(ADV, S_EQV, html, correct, wrong[:3], why)


@tpl(ADV, 1)
def eval_quadratic(rng):
    a, b, k = rng.randint(2, 6), rng.randint(-12, 12), rng.randint(-5, -2)
    val = a * k * k + b
    html = p(f"The function {v('f')} is defined by {v('f')}({X}) = {poly((a, X2), (b, ''))}. What is the value of "
             f"{v('f')}({n(k)})?")
    why = f"{v('f')}({n(k)}) = {a}({n(k)})<sup>2</sup>{signed(b, '')} = {a}({k * k}){signed(b, '')} = {n(val)}."
    return num(ADV, S_NLF, html, val, [-a * k * k + b, (a * k) ** 2 + b, 2 * a * k + b], why)


@tpl(ADV, 1, ("mc",))
def factor_difference_squares(rng):
    a, k = pick(rng, [1, 1, 2, 3]), rng.randint(2, 9)
    ax = X if a == 1 else f"{a}{X}"
    lead = X2 if a == 1 else f"{a * a}{X2}"
    html = p(f"Which expression is equivalent to {lead} {MINUS} {k * k}?")
    correct = f"({ax} + {k})({ax} {MINUS} {k})"
    wrong = [f"({ax} {MINUS} {k})<sup>2</sup>", f"({ax} + {k})<sup>2</sup>", f"({ax} {MINUS} {k * k})({ax} + 1)"]
    why = f"This is a difference of squares: ({ax})<sup>2</sup> {MINUS} {k}<sup>2</sup> = ({ax} + {k})({ax} {MINUS} {k})."
    return text(ADV, S_EQV, html, correct, wrong, why)


@tpl(ADV, 1)
def exponent_rule(rng):
    a, b = rng.randint(3, 9), rng.randint(2, 8)
    c = rng.randint(1, a + b - 2)
    html = p(f"For {X} &gt; 0, the expression {frac(f'{X}<sup>{a}</sup> · {X}<sup>{b}</sup>', f'{X}<sup>{c}</sup>')} "
             f"is equivalent to {X}<sup>{v('k')}</sup>. What is the value of {v('k')}?")
    why = f"Add exponents when multiplying and subtract when dividing: {a} + {b} {MINUS} {c} = {a + b - c}."
    return num(ADV, S_EQV, html, a + b - c, [a * b - c, a + b + c, a * b], why, lo=1)


@tpl(ADV, 1)
def solve_square(rng):
    a, b = rng.randint(1, 9), rng.randint(2, 9)
    html = p(f"If ({X} {MINUS} {a})<sup>2</sup> = {b * b} and {X} &gt; {a}, what is the value of {X}?")
    why = f"Take square roots: {X} {MINUS} {a} = {b} (positive because {X} &gt; {a}), so {X} = {a + b}."
    return num(ADV, S_NLE, html, a + b, [a - b, b, a + b * b, b * b], why)


@tpl(ADV, 2)
def quadratic_root(rng):
    r1, r2 = sorted(rng.sample([v_ for v_ in range(-7, 10) if v_ != 0], 2))
    B, C = -(r1 + r2), r1 * r2
    ask_sum = rng.random() < 0.4
    html = p(f"What is the {'sum of the solutions' if ask_sum else 'greater solution'} of the equation "
             f"{poly((1, X2), (B, X), (C, ''))} = 0?")
    if ask_sum:
        ans = r1 + r2
        why = f"The equation factors as ({X}{signed(-r1, '')})({X}{signed(-r2, '')}) = 0, so the solutions are {n(r1)} and {n(r2)}; their sum is {n(ans)}."
        plaus = [-(r1 + r2), r1 * r2, r2]
    else:
        ans = r2
        why = f"The equation factors as ({X}{signed(-r1, '')})({X}{signed(-r2, '')}) = 0, so {X} = {n(r1)} or {X} = {n(r2)}. The greater solution is {n(r2)}."
        plaus = [-r1, -r2, r1, r1 * r2]
    return num(ADV, S_NLE, html, ans, plaus, why)


@tpl(ADV, 2, ("mc",))
def expand_binomials(rng):
    a, b, c, d = rng.randint(2, 5), nz(rng, -7, 7), rng.randint(1, 4), nz(rng, -7, 7)
    mid = a * d + b * c
    if mid == 0:
        d += 1 if d != -1 else 2
        mid = a * d + b * c
    html = p(f"Which expression is equivalent to ({poly((a, X), (b, ''))})({poly((c, X), (d, ''))})?")
    correct = q2(a * c, mid, b * d)
    cands = [q2(a * c, 0, b * d), q2(a * c, a * d - b * c, b * d) if a * d - b * c != mid else q2(a * c, mid + 2, b * d),
             q2(a * c, mid, -b * d), q2(a + c, mid, b * d)]
    wrong = []
    for x in cands:
        if x != correct and x not in wrong:
            wrong.append(x)
    why = (f"Multiply each term: {a}{X} · {c}{X} = {a * c}{X2}, the middle terms give {a * d}{X} + ({n(b * c)}{X}) = {n(mid)}{X}, "
           f"and {n(b)} · {n(d)} = {n(b * d)}.")
    return text(ADV, S_EQV, html, correct, wrong[:3], why)


@tpl(ADV, 2, ("mc",))
def exponential_model(rng):
    p0 = rng.randint(2, 9) * 100
    g, k = pick(rng, [(2, 3), (2, 4), (3, 5), (2, 6), (3, 2)])
    thing = pick(rng, [("A population of bacteria", "population", "hours", "t"),
                       ("The number of users of a new app", "number of users", "weeks", "w"),
                       ("The area covered by a mold colony, in square millimeters,", "area", "days", "d")])
    word = {2: "doubles", 3: "triples"}[g]
    t = v(thing[3])
    html = p(f"{thing[0]} {word} every {k} {thing[2]}. The initial {thing[1]} is {p0:,}. Which function gives the "
             f"{thing[1]} {v('P')} after {t} {thing[2]}?")
    correct = f"{v('P')}({t}) = {p0:,}({g})<sup>{t}/{k}</sup>"
    wrong = [f"{v('P')}({t}) = {p0:,}({g})<sup>{k}{t}</sup>", f"{v('P')}({t}) = {p0:,}({k})<sup>{t}/{g}</sup>",
             f"{v('P')}({t}) = {g}({p0:,})<sup>{t}/{k}</sup>"]
    why = (f"The starting value {p0:,} is multiplied by {g} once every {k} {thing[2]}, so after {t} {thing[2]} it has been "
           f"multiplied {t}/{k} times.")
    return text(ADV, S_NLF, html, correct, wrong, why)


@tpl(ADV, 2)
def percent_growth_value(rng):
    r = pick(rng, [10, 20, 50])
    a = rng.randint(5, 40) * 100
    val = a * F(100 + r, 100) ** 2
    thing = pick(rng, [("An investment", "dollars", "year"), ("The number of members of a club", "members", "year"),
                       ("A town's population", "people", "year")])
    factor = {10: "1.1", 20: "1.2", 50: "1.5"}[r]
    html = p(f"{thing[0]} is modeled by the function {v('f')}({v('t')}) = {a:,}({factor})<sup>{v('t')}</sup>, where "
             f"{v('f')}({v('t')}) is the number of {thing[1]} {v('t')} {thing[2]}s after the start. What is the value of "
             f"{v('f')}(2)?")
    why = f"{v('f')}(2) = {a:,}({factor})<sup>2</sup> = {a:,} × {float(F(100 + r, 100) ** 2):g} = {n(val)}."
    return num(ADV, S_NLF, html, val, [a * F(100 + 2 * r, 100), a * F(100 + r, 100), a * F(100 + r, 100) ** 3], why, lo=1)


@tpl(ADV, 2, ("mc",))
def vertex_from_graph(rng):
    h, k = nz(rng, -3, 4), nz(rng, -4, 4)
    up = rng.random() < 0.6
    s = 1 if up else -1
    lim = (-5, 5)
    fig = base.coord_plane((-5, 6), lim, curves=[(lambda xx, h=h, k=k, s=s: s * (xx - h) ** 2 + k, h - 3.2, h + 3.2)],
                           label_every=2, size=(3.8, 3.8),
                           alt=f"Graph of a parabola that opens {'upward' if up else 'downward'} with vertex ({h}, {k})")

    def form(sign, hh, kk):
        lead = "" if sign > 0 else MINUS
        inner = f"{X}{signed(-hh, '')}"
        return f"{v('f')}({X}) = {lead}({inner})<sup>2</sup>{signed(kk, '')}"

    correct = form(s, h, k)
    wrong = [form(s, -h, k), form(s, h, -k), form(-s, h, k)]
    html = p(f"The graph of {Y} = {v('f')}({X}) is shown.") + fig + p(f"Which equation could define {v('f')}?")
    why = (f"The vertex is ({n(h)}, {n(k)}) and the parabola opens {'upward' if up else 'downward'}, so "
           f"{v('f')}({X}) = {'' if up else MINUS}({X}{signed(-h, '')})<sup>2</sup>{signed(k, '')}.")
    return text(ADV, S_NLF, html, correct, wrong, why)


@tpl(ADV, 2)
def rational_equation(rng):
    x, c, t = rng.randint(2, 9), rng.randint(1, 8), rng.randint(2, 5)
    a, b = x * t, (x + c) * t
    html = p(f"What is the solution to the equation {frac(str(a), X)} = {frac(str(b), f'{X} + {c}')}?")
    why = f"Cross-multiply: {a}({X} + {c}) = {b}{X}, so {a * c} = {b - a}{X} and {X} = {x}."
    return num(ADV, S_NLE, html, x, [c, x + c, F(a * c, b + a), t], why, lo=1, int_only=False)


@tpl(ADV, 2)
def radical_equation(rng):
    b, a = rng.randint(3, 9), rng.randint(-8, 15)
    x = b * b - a
    html = p(f"What value of {X} satisfies the equation &radic;<span style=\"text-decoration:overline\">{poly((1, X), (a, ''))}</span> = {b}?")
    why = f"Square both sides: {poly((1, X), (a, ''))} = {b * b}, so {X} = {n(x)}. Check: &radic;{b * b} = {b}."
    return num(ADV, S_NLE, html, x, [b - a, b * b + a, 2 * b - a], why)


@tpl(ADV, 2)
def composition(rng):
    a, b, c, k = nz(rng, -4, 5, (0, 1)), rng.randint(-6, 8), rng.randint(-5, 6), rng.randint(-3, 4)
    g = k * k + c
    val = a * g + b
    html = p(f"The functions {v('f')} and {v('g')} are defined by {v('f')}({X}) = {poly((a, X), (b, ''))} and "
             f"{v('g')}({X}) = {poly((1, X2), (c, ''))}. What is the value of {v('f')}({v('g')}({n(k)}))?")
    why = f"First {v('g')}({n(k)}) = {n(k)}<sup>2</sup>{signed(c, '')} = {n(g)}. Then {v('f')}({n(g)}) = {n(a)}({n(g)}){signed(b, '')} = {n(val)}."
    return num(ADV, S_NLF, html, val, [(a * k + b) ** 2 + c, a * k * k + c + b, a * g - b], why)


@tpl(ADV, 3)
def discriminant_one_solution(rng):
    s = rng.randint(2, 9)
    c = s * s
    html = p(f"In the equation {X2} + {v('k')}{X} + {c} = 0, {v('k')} is a positive constant. If the equation has exactly "
             f"one real solution, what is the value of {v('k')}?")
    why = (f"A quadratic has exactly one real solution when its discriminant is 0: {v('k')}<sup>2</sup> {MINUS} 4(1)({c}) = 0, "
           f"so {v('k')}<sup>2</sup> = {4 * c} and {v('k')} = {2 * s}.")
    return num(ADV, S_NLE, html, 2 * s, [s, c, 4 * s, 4 * c], why, lo=1)


@tpl(ADV, 3)
def sum_of_roots(rng):
    while True:
        a, b, c = rng.randint(2, 6), nz(rng, -15, 15), nz(rng, -12, 12)
        if b * b - 4 * a * c > 0 and F(-b, a).denominator in (1, 2, 3) and abs(F(-b, a)) != abs(F(c, a)):
            break
    html = p(f"What is the sum of the solutions to {q2(a, b, c)} = 0?")
    why = f"For {v('a')}{X2} + {v('b')}{X} + {v('c')} = 0, the sum of the solutions is {MINUS}{v('b')}/{v('a')} = {n(F(-b, a))}."
    return num(ADV, S_NLE, html, F(-b, a), [F(b, a), F(-c, a), F(c, a)], why)


@tpl(ADV, 3)
def line_parabola_sum(rng):
    x1, x2 = rng.sample([t for t in range(-5, 8) if t != 0], 2)
    q = x1 + x2
    if q == 0:
        x2 += 1
        q = x1 + x2
    pc = rng.randint(-6, 8)
    r = pc - x1 * x2  # x² + pc = qx + r  <=>  x² − qx + x1·x2 = 0, whose solutions are x1 and x2
    assert q * q - 4 * x1 * x2 > 0
    html = (p(f"{Y} = {poly((1, X2), (pc, ''))}<br>{Y} = {poly((q, X), (r, ''))}")
            + p(f"The graphs of the equations in the system intersect at two points. What is the sum of the "
                f"{X}-coordinates of the two points?"))
    why = (f"Set the equations equal: {poly((1, X2), (-q, X), (pc - r, ''))} = 0. The sum of the solutions of "
           f"{X2} + {v('b')}{X} + {v('c')} = 0 is {MINUS}{v('b')}, which is {n(q)}.")
    return num(ADV, S_NLE, html, q, [-q, x1 * x2, pc - r], why)


@tpl(ADV, 3)
def vertex_minimum(rng):
    h, c = nz(rng, -6, 7), rng.randint(-10, 20)
    m = c - h * h
    html = p(f"The function {v('f')} is defined by {v('f')}({X}) = {poly((1, X2), (-2 * h, X), (c, ''))}. What is the "
             f"minimum value of {v('f')}({X})?")
    why = (f"Complete the square: {v('f')}({X}) = ({X}{signed(-h, '')})<sup>2</sup>{signed(m, '')}. The minimum value "
           f"occurs at {X} = {n(h)} and equals {n(m)}.")
    return num(ADV, S_NLF, html, m, [c, h, c + h * h, -h * h], why)


@tpl(ADV, 3)
def exponent_equation(rng):
    combos = [(3, 2, 2), (2, 1, 2), (3, 1, 3), (4, 3, 2), (5, 2, 2), (4, 1, 4), (6, 4, 2)]
    while True:
        pw, qw, base_ = pick(rng, combos)
        x, s = rng.randint(1, 8), rng.randint(0, 4)
        num_ = pw * (x + s) - qw * x
        if num_ % qw == 0:
            t = num_ // qw
            if t != s and t >= 0:
                break
    bp, bq = base_ ** pw, base_ ** qw
    lhs = f"{bp}<sup>{X}{signed(s, '') if s else ''}</sup>"
    rhs = f"{bq}<sup>{X}{signed(t, '') if t else ''}</sup>" if bq != base_ else f"{base_}<sup>{X}{signed(t, '') if t else ''}</sup>"
    html = p(f"If {lhs} = {rhs}, what is the value of {X}?")
    sx = f"({X}{signed(s, '')})" if s else X
    tx = (f"({X}{signed(t, '')})" if qw != 1 else f"{X}{signed(t, '')}") if t else X
    why = (f"Write both sides as powers of {base_}: {base_}<sup>{pw}{sx}</sup> = {base_}<sup>{coef(qw, tx)}</sup>. "
           f"So {pw}{sx} = {coef(qw, tx)}, which gives {X} = {x}.")
    return num(ADV, S_EQV, html, x, [t - s, x + s, F(t, pw) if F(t, pw).denominator == 1 else x + 2], why, lo=0)


@tpl(ADV, 3, ("mc",))
def factor_from_table(rng):
    r = nz(rng, -6, 6, (0, 1))
    ox, oy = pick(rng, [(0, rng.randint(2, 9)), (1, rng.randint(-8, -2))])
    tx, ty = rng.randint(2, 5), rng.randint(3, 12)
    if tx == r:
        tx += 1
    rows = sorted([(r, 0), (ox, oy), (tx, ty)])
    fig = base.table_figure(["x", "p(x)"], [[str(a).replace("-", MINUS), str(b).replace("-", MINUS)] for a, b in rows],
                            "Table of values of a polynomial function p", width=220)
    html = (p(f"For the polynomial function {v('p')}, the table shows some values of {X} and their corresponding values "
              f"of {v('p')}({X}).") + fig + p(f"Which of the following must be a factor of {v('p')}({X})?"))
    correct = f"{X}{signed(-r, '')}"
    wrong = [f"{X}{signed(r, '')}", f"{X}{signed(-oy, '')}", f"{X}{signed(-ty, '')}"]
    why = (f"Because {v('p')}({n(r)}) = 0, {n(r)} is a zero of {v('p')}, so by the factor theorem "
           f"{X}{signed(-r, '')} is a factor of {v('p')}({X}).")
    return text(ADV, S_NLF, html, correct, wrong, why)


@tpl(ADV, 3)
def square_expansion_coefficient(rng):
    a, b = rng.randint(2, 7), nz(rng, -9, 9)
    k = 2 * a * b
    html = p(f"The expression ({poly((a, X), (b, ''))})<sup>2</sup> is equivalent to {a * a}{X2} + {v('k')}{X} + {b * b}, "
             f"where {v('k')} is a constant. What is the value of {v('k')}?")
    why = f"({v('a')} + {v('b')})<sup>2</sup> = {v('a')}<sup>2</sup> + 2{v('a')}{v('b')} + {v('b')}<sup>2</sup>, so {v('k')} = 2({a})({n(b)}) = {n(k)}."
    return num(ADV, S_EQV, html, k, [a * b, a * a + b * b, -k, 2 * a + 2 * b], why)


@tpl(ADV, 3)
def rational_simplify_value(rng):
    a, k = rng.randint(2, 9), rng.randint(10, 30)
    html = p(f"For {X} &ne; {a}, the expression {frac(f'{X2} {MINUS} {a * a}', f'{X} {MINUS} {a}')} is equivalent to "
             f"{v('g')}({X}). What is the value of {v('g')}({k})?")
    why = f"{X2} {MINUS} {a * a} = ({X} + {a})({X} {MINUS} {a}), so {v('g')}({X}) = {X} + {a} and {v('g')}({k}) = {k + a}."
    return num(ADV, S_EQV, html, k + a, [k - a, k * k - a * a, k], why, lo=1)


# ===========================================================================
# PROBLEM-SOLVING AND DATA ANALYSIS
# ===========================================================================

S_RATE = "Ratios, rates, proportional relationships, and units"
S_PCT = "Percentages"
S_ONE = "One-variable data: distributions and measures of center and spread"
S_TWO = "Two-variable data: models and scatterplots"
S_PROB = "Probability and conditional probability"
S_INF = "Inference from sample statistics and margin of error"
S_EXP = "Evaluating statistical claims: observational studies and experiments"


@tpl(PSDA, 1)
def rate_units(rng):
    ctx = pick(rng, [("A printer prints {a} pages every {b} seconds. At this rate, how many pages does the printer print in {m} minutes?", "pages"),
                     ("A machine fills {a} bottles every {b} seconds. At this rate, how many bottles does the machine fill in {m} minutes?", "bottles"),
                     ("A pump moves {a} liters of water every {b} seconds. At this rate, how many liters does the pump move in {m} minutes?", "liters")])
    b = pick(rng, [15, 20, 30, 40, 45])
    a = rng.randint(2, 9) * (b // math.gcd(b, 60) if False else 1) + rng.randint(1, 5)
    m = rng.randint(3, 12)
    while (m * 60) % b:
        m += 1
    total = F(a * m * 60, b)
    while total.denominator != 1:
        a += 1
        total = F(a * m * 60, b)
    html = p(ctx[0].format(a=a, b=b, m=m))
    why = f"{m} minutes = {m * 60} seconds, which is {n(F(m * 60, b))} groups of {b} seconds. {n(F(m * 60, b))} × {a} = {n(total)} {ctx[1]}."
    return num(PSDA, S_RATE, html, total, [a * m, F(a * m * b, 60), total + a], why, lo=1)


@tpl(PSDA, 1)
def percent_of(rng):
    pct, base_ = pick(rng, [5, 15, 20, 25, 30, 35, 40, 60, 75, 120]), rng.randint(2, 30) * 20
    val = F(pct * base_, 100)
    html = p(f"What is {pct}% of {base_:,}?")
    why = f"{pct}% of {base_:,} = {pct}/100 × {base_:,} = {n(val)}."
    return num(PSDA, S_PCT, html, val, [F(base_, pct) if F(base_, pct).denominator == 1 else val * 10, val * 10, base_ - val], why, lo=1)


@tpl(PSDA, 1)
def mean_of_values(rng):
    while True:
        vals = [rng.randint(4, 30) for _ in range(rng.randint(5, 7))]
        if sum(vals) % len(vals) == 0:
            break
    mean = F(sum(vals), len(vals))
    srt = sorted(vals)
    med = F(srt[len(srt) // 2]) if len(srt) % 2 else F(srt[len(srt) // 2 - 1] + srt[len(srt) // 2], 2)
    thing = pick(rng, ["the numbers of minutes", "the numbers of points", "the numbers of pages"])
    who = {"the numbers of minutes": "students spent on a quiz", "the numbers of points": "a player scored in games",
           "the numbers of pages": "students read in one evening"}[thing]
    html = p(f"The list shows {thing} {who}: {', '.join(map(str, vals))}. What is the mean of the list?")
    why = f"Sum = {sum(vals)}; there are {len(vals)} values; mean = {sum(vals)} ÷ {len(vals)} = {n(mean)}."
    return num(PSDA, S_ONE, html, mean, [med, F(max(vals) + min(vals), 2), F(sum(vals), len(vals) - 1)], why, lo=1)


@tpl(PSDA, 2)
def original_from_percent(rng):
    pct = pick(rng, [10, 15, 20, 25, 30, 40])
    original = rng.randint(3, 30) * 20
    new = original * F(100 + pct, 100)
    while new.denominator != 1:
        original += 20
        new = original * F(100 + pct, 100)
    thing = pick(rng, [("The number of visitors to a museum", "this year", "last year"),
                       ("The enrollment at a language school", "this term", "last term"),
                       ("The number of books in a school library", "this year", "last year")])
    html = p(f"{thing[0]} {thing[1]} is {n(new)}, which is {pct}% greater than it was {thing[2]}. What was the number "
             f"{thing[2]}?")
    why = f"{thing[1].capitalize()}'s value is {100 + pct}% of {thing[2]}'s: {n(new)} ÷ {n(F(100 + pct, 100))} = {n(original)}."
    return num(PSDA, S_PCT, html, original, [new * F(100 - pct, 100), new - pct, original - 20], why, lo=1)


@tpl(PSDA, 2)
def proportion_scaling(rng):
    a, b = rng.randint(2, 6), rng.randint(3, 9)
    k = rng.randint(3, 8)
    ctx = pick(rng, [("A recipe uses {a} cups of flour for every {b} cups of milk. How many cups of flour are needed for {m} cups of milk?", "cups of flour"),
                     ("On a map, {a} centimeters represent {b} kilometers. How many centimeters on the map represent {m} kilometers?", "centimeters"),
                     ("A paint mixture uses {a} liters of blue paint for every {b} liters of white paint. How many liters of blue paint are needed for {m} liters of white paint?", "liters")])
    m = b * k
    html = p(ctx[0].format(a=a, b=b, m=m))
    why = f"The ratio is {a} : {b}. {m} is {k} times {b}, so the answer is {k} × {a} = {a * k} {ctx[1]}."
    return num(PSDA, S_RATE, html, a * k, [b * k, m - b + a, a + m - b, a * m], why, lo=1)


@tpl(PSDA, 2, ("mc",))
def percent_change_twice(rng):
    p0 = rng.randint(4, 20) * 20
    up, down = pick(rng, [(20, 20), (25, 20), (10, 10), (50, 20), (20, 25), (40, 25)])
    final = p0 * F(100 + up, 100) * F(100 - down, 100)
    html = p(f"The price of a jacket was ${p0}. The price was increased by {up}%, and then the new price was decreased "
             f"by {down}%. What was the final price of the jacket?")
    why = f"${p0} × {n(F(100 + up, 100))} = {money(p0 * F(100 + up, 100))}; then × {n(F(100 - down, 100))} gives {money(final)}."
    return num(PSDA, S_PCT, html, final, [p0 * F(100 + up - down, 100), p0, p0 * F(100 + up, 100)], why, fmt=money, lo=1,
               spr_ok=False)


@tpl(PSDA, 2, ("mc",))
def two_way_probability(rng):
    groups = pick(rng, [("Grade 10", "Grade 11"), ("Morning class", "Evening class")])
    cats = pick(rng, [("Plays a sport", "Does not play a sport", "do not play a sport"),
                      ("Has a library card", "Does not have a library card", "do not have a library card")])
    a, b, c, d = (rng.randint(8, 30) for _ in range(4))
    tot = a + b + c + d
    rows = [[groups[0], str(a), str(b), str(a + b)], [groups[1], str(c), str(d), str(c + d)],
            ["Total", str(a + c), str(b + d), str(tot)]]
    fig = base.table_figure(["", cats[0].replace(" a ", "\na "), cats[1].replace("not ", "not\n"), "Total"], rows,
                            "Two-way table of students by group and category", width=440,
                            col_widths=[0.28, 0.27, 0.27, 0.18])
    html = (p(f"The table summarizes {tot} students by group and by whether each student {cats[0].lower()[0:]}.") + fig
            + p(f"If one of these students is selected at random, what is the probability that the student is in "
                f"{groups[1]} and {cats[1].lower()}?"))
    correct = F(d, tot)
    why = f"{d} of the {tot} students are in {groups[1]} and {cats[2]}, so the probability is {n(correct)}."
    return num(PSDA, S_PROB, html, correct, [F(d, c + d), F(d, b + d), F(c + d, tot)], why,
               fmt=lambda x: frac(str(x.numerator), str(x.denominator)) if x.denominator != 1 else str(x), lo=0, hi=1,
               spr_ok=False)


@tpl(PSDA, 2)
def unit_conversion(rng):
    kind = pick(rng, ["speed", "flow"])
    if kind == "speed":
        mps = pick(rng, [5, 10, 15, 20, 25, 30])
        kmh = F(mps * 3600, 1000)
        html = p(f"A cyclist travels at a constant speed of {mps} meters per second. What is this speed in kilometers per "
                 f"hour? (1 kilometer = 1,000 meters)")
        why = f"{mps} m/s × 3,600 s/h = {mps * 3600:,} m/h = {n(kmh)} km/h."
        return num(PSDA, S_RATE, html, kmh, [F(mps * 60, 1000), F(mps * 1000, 3600), mps * 60], why, lo=1)
    lpm = rng.randint(3, 12) * 5
    hours = rng.randint(2, 6)
    total = lpm * 60 * hours
    html = p(f"Water flows into a pool at a rate of {lpm} liters per minute. How many liters of water flow into the pool "
             f"in {hours} hours?")
    why = f"{hours} hours = {hours * 60} minutes; {hours * 60} × {lpm} = {total:,} liters."
    return num(PSDA, S_RATE, html, total, [lpm * hours, lpm * 60, total // 10], why, lo=1)


def _scatter(rng, slope, icpt, xlabel, ylabel, title, xs):
    pts = [(x, round(slope * x + icpt + rng.uniform(-1.0, 1.0) * max(2, abs(slope) * 1.2), 1)) for x in xs]
    fig, ax = base.plt.subplots(figsize=(5.2, 3.8))
    ax.scatter([q[0] for q in pts], [q[1] for q in pts], color=base.INK, s=18, zorder=3)
    x0, x1 = 0, max(xs) + 1
    ax.plot([x0, x1], [slope * x0 + icpt, slope * x1 + icpt], color=base.DARK, lw=1.4, zorder=2)
    ax.set_xlim(x0, x1)
    ys = [q[1] for q in pts] + [icpt, slope * x1 + icpt]
    ax.set_ylim(math.floor(min(ys) / 10) * 10, math.ceil(max(ys) / 10) * 10 + 5)
    ax.grid(color=base.GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.set_title(title, fontsize=11, fontweight="bold", pad=8)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
    return base._img(base._fig_to_uri(fig), f"Scatterplot of {ylabel.lower()} versus {xlabel.lower()} with a line of best fit", 460)


@tpl(PSDA, 2, ("mc",))
def scatter_prediction(rng):
    ctx = pick(rng, [("Hours of practice", "Score", "Practice Time and Scores", (3, 50)),
                     ("Temperature (°C)", "Drinks sold", "Temperature and Cold Drink Sales", (4, 20)),
                     ("Distance (km)", "Delivery time (min)", "Delivery Distance and Time", (2, 10))])
    slope, icpt = ctx[3][0] + rng.randint(0, 3), ctx[3][1] + rng.randint(0, 10)
    xs = [i * 0.5 + 1 for i in range(14)]
    fig = _scatter(rng, slope, icpt, ctx[0], ctx[1], ctx[2], xs)
    xq = rng.randint(3, 8)
    pred = slope * xq + icpt
    html = (p(f"The scatterplot shows data for 14 observations and a line of best fit.") + fig
            + p(f"The line of best fit has the equation {Y} = {slope}{X} + {icpt}. Based on the line of best fit, what is "
                f"the predicted value of {Y} when {X} = {xq}?"))
    why = f"Substitute {X} = {xq}: {Y} = {slope}({xq}) + {icpt} = {pred}."
    return num(PSDA, S_TWO, html, pred, [slope * xq, pred + slope, icpt + xq], why, lo=1, spr_ok=False)


@tpl(PSDA, 3, ("mc",))
def median_after_removal(rng):
    vals = sorted(rng.sample(range(10, 40), 6))
    outlier = vals[-1] + rng.randint(40, 80)
    data = vals + [outlier]
    html = p(f"A data set consists of the values {', '.join(map(str, data))}. If the value {outlier} is removed from the "
             f"data set, which of the following statements is true?")
    correct = "The mean decreases, and the median decreases."
    if vals[2] == vals[3]:
        correct = "The mean decreases, and the median stays the same."
    wrong = [w for w in ["The mean decreases, and the median stays the same.", "The mean stays the same, and the median decreases.",
                         "The mean increases, and the median increases.", "The mean decreases, and the median decreases."]
             if w != correct][:3]
    why = (f"Removing the much larger value {outlier} lowers the mean a lot. The median changes from {vals[3]} (the 4th of 7 values) "
           f"to the average of {vals[2]} and {vals[3]}, which is {n(F(vals[2] + vals[3], 2))}, so it also decreases.")
    return text(PSDA, S_ONE, html, correct, wrong, why)


@tpl(PSDA, 3, ("mc",))
def margin_of_error(rng):
    est, moe = rng.randint(30, 70), pick(rng, [2, 3, 4, 5])
    pop = pick(rng, ["the students at a large high school", "the residents of a city", "the employees of a large company"])
    html = p(f"A random sample of {pop} was surveyed, and {est}% of those surveyed said they support a new park. The margin of "
             f"error for the estimate is {moe} percentage points at a 95% confidence level. Which of the following is the "
             f"most appropriate conclusion?")
    correct = f"It is plausible that between {est - moe}% and {est + moe}% of all {pop.replace('the ', '', 1)} support the new park."
    wrong = [f"Exactly {est}% of all {pop.replace('the ', '', 1)} support the new park.",
             f"Between {est - moe}% and {est + moe}% of the people in the sample support the new park.",
             f"It is plausible that between {est - 2 * moe}% and {est}% of all {pop.replace('the ', '', 1)} support the new park."]
    why = "A margin of error gives a plausible range for the population value: the estimate plus or minus the margin."
    return text(PSDA, S_INF, html, correct, wrong, why)


@tpl(PSDA, 3, ("mc",))
def experiment_conclusion(rng):
    t = pick(rng, [("a new study app", "test scores", "students"), ("a new fertilizer", "plant growth", "tomato plants"),
                   ("a daily stretching routine", "reported back pain", "office workers")])
    n_ = rng.randint(6, 20) * 10
    html = p(f"Researchers selected {n_} {t[2]} at random from a large population and randomly assigned half of them to use "
             f"{t[0]} and the other half not to. The group that used {t[0]} showed a significant improvement in {t[1]}. "
             f"Which conclusion is best supported?")
    correct = f"Using {t[0]} likely causes an improvement in {t[1]} for {t[2]} in the population."
    wrong = [f"Using {t[0]} causes an improvement in {t[1]} for anyone, including people outside the population.",
             f"There is a relationship between {t[0]} and {t[1]}, but no conclusion about cause can be drawn.",
             f"The results apply only to the {n_} {t[2]} in the study."]
    why = ("Random assignment supports a cause-and-effect conclusion, and random selection allows the result to be "
           "generalized to the population the sample came from, but not beyond it.")
    return text(PSDA, S_EXP, html, correct, wrong, why)


@tpl(PSDA, 3, ("mc",))
def conditional_probability(rng):
    a, b, c, d = (rng.randint(10, 40) for _ in range(4))
    rows = [["Chose the train", str(a), str(b), str(a + b)], ["Chose the bus", str(c), str(d), str(c + d)],
            ["Total", str(a + c), str(b + d), str(a + b + c + d)]]
    fig = base.table_figure(["", "Weekday", "Weekend", "Total"], rows, "Two-way table of trips by transport and day",
                            width=420, col_widths=[0.34, 0.22, 0.22, 0.22])
    html = (p("The table shows how a group of commuters traveled on a set of trips, by day type.") + fig
            + p("If one of the weekend trips is selected at random, what is the probability that the train was chosen?"))
    correct = F(b, b + d)
    why = f"There are {b + d} weekend trips, and the train was chosen on {b} of them: {n(correct)}."
    return num(PSDA, S_PROB, html, correct, [F(b, a + b), F(b, a + b + c + d), F(d, b + d)], why,
               fmt=lambda x: frac(str(x.numerator), str(x.denominator)) if x.denominator != 1 else str(x), lo=0, hi=1,
               spr_ok=False)


# ===========================================================================
# GEOMETRY AND TRIGONOMETRY
# ===========================================================================

S_AREA = "Area and volume"
S_LAT = "Lines, angles, and triangles"
S_RTT = "Right triangles and trigonometry"
S_CIRC = "Circles"


@tpl(GEO, 1)
def rectangle_perimeter(rng):
    w, l = rng.randint(3, 12), rng.randint(13, 30)
    html = p(f"A rectangle has an area of {w * l} square centimeters and a width of {w} centimeters. What is the perimeter of "
             f"the rectangle, in centimeters?")
    why = f"Length = {w * l} ÷ {w} = {l}. Perimeter = 2({l} + {w}) = {2 * (l + w)}."
    return num(GEO, S_AREA, html, 2 * (l + w), [l + w, l, w * l // 2], why, lo=1)


@tpl(GEO, 1)
def triangle_third_angle(rng):
    a, b = rng.randint(30, 80), rng.randint(25, 70)
    c = 180 - a - b
    html = p(f"In triangle {v('ABC')}, the measure of angle {v('A')} is {a}° and the measure of angle {v('B')} is {b}°. "
             f"What is the measure, in degrees, of angle {v('C')}?")
    why = f"The angles of a triangle add up to 180°: 180 {MINUS} {a} {MINUS} {b} = {c}."
    return num(GEO, S_LAT, html, c, [a + b, 360 - a - b, 90 - b + a if 90 - b + a > 0 else c + 10], why, lo=1)


@tpl(GEO, 1)
def box_volume(rng):
    l, w, h = rng.randint(3, 12), rng.randint(2, 9), rng.randint(2, 8)
    html = p(f"A rectangular storage box has a length of {l} inches, a width of {w} inches, and a height of {h} inches. "
             f"What is the volume of the box, in cubic inches?")
    why = f"Volume = length × width × height = {l} × {w} × {h} = {l * w * h}."
    return num(GEO, S_AREA, html, l * w * h, [l + w + h, 2 * (l * w + w * h + l * h), l * w], why, lo=1)


@tpl(GEO, 2)
def pythagorean(rng):
    a, b, c = pick(rng, [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25), (9, 12, 15), (6, 8, 10), (12, 16, 20)])
    k = pick(rng, [1, 1, 2]) if c <= 13 else 1
    a, b, c = a * k, b * k, c * k
    ask_leg = rng.random() < 0.5
    if ask_leg:
        html = p(f"A right triangle has a hypotenuse of length {c} and one leg of length {a}. What is the length of the other leg?")
        why = f"{a}<sup>2</sup> + {v('b')}<sup>2</sup> = {c}<sup>2</sup>, so {v('b')}<sup>2</sup> = {c * c - a * a} and {v('b')} = {b}."
        return num(GEO, S_RTT, html, b, [c - a, c + a, c * c - a * a], why, lo=1)
    html = p(f"The legs of a right triangle have lengths {a} and {b}. What is the length of the hypotenuse?")
    why = f"{a}<sup>2</sup> + {b}<sup>2</sup> = {a * a + b * b} = {c}<sup>2</sup>, so the hypotenuse is {c}."
    return num(GEO, S_RTT, html, c, [a + b, a * a + b * b, b + 1 if b + 1 != c else b + 2], why, lo=1)


@tpl(GEO, 2, ("mc",))
def circle_center_radius(rng):
    h, k, r = nz(rng, -6, 6), nz(rng, -6, 6), rng.randint(2, 9)
    html = p(f"A circle in the {X}{Y}-plane has the equation ({X}{signed(-h, '')})<sup>2</sup> + ({Y}{signed(-k, '')})<sup>2</sup> = "
             f"{r * r}. Which of the following gives the center and the radius of the circle?")
    correct = f"Center ({n(h)}, {n(k)}), radius {r}"
    wrong = [f"Center ({n(-h)}, {n(-k)}), radius {r}", f"Center ({n(h)}, {n(k)}), radius {r * r}",
             f"Center ({n(-h)}, {n(-k)}), radius {r * r}"]
    why = (f"The form ({X} {MINUS} {v('h')})<sup>2</sup> + ({Y} {MINUS} {v('k')})<sup>2</sup> = {v('r')}<sup>2</sup> has center "
           f"({v('h')}, {v('k')}) and radius {v('r')}; here the center is ({n(h)}, {n(k)}) and the radius is &radic;{r * r} = {r}.")
    return text(GEO, S_CIRC, html, correct, wrong, why)


@tpl(GEO, 2)
def similar_triangles(rng):
    ad, db = rng.randint(2, 9), rng.randint(2, 9)
    g = math.gcd(ad, ad + db)
    de = ad // g * rng.randint(1, 4)
    if de < 3:
        de *= 3
    bc = F(de * (ad + db), ad)
    html = p(f"In triangle {v('ABC')}, point {v('D')} lies on {v('AB')} and point {v('E')} lies on {v('AC')} so that "
             f"{v('DE')} is parallel to {v('BC')}. If {v('AD')} = {ad}, {v('DB')} = {db}, and {v('DE')} = {de}, what is the "
             f"length of {v('BC')}?")
    why = (f"Triangles {v('ADE')} and {v('ABC')} are similar, so {v('BC')}/{v('DE')} = {v('AB')}/{v('AD')} = {ad + db}/{ad}. "
           f"{v('BC')} = {de} × {ad + db}/{ad} = {n(bc)}.")
    return num(GEO, S_LAT, html, bc, [F(de * db, ad), de + db, F(de * ad, db)], why, lo=1)


@tpl(GEO, 2, ("mc",))
def arc_length(rng):
    r = rng.randint(3, 12)
    ang = pick(rng, [30, 45, 60, 90, 120, 135, 150])
    arc = F(ang, 360) * 2 * r
    html = p(f"A circle has a radius of {r} centimeters. What is the length, in centimeters, of an arc of the circle that is "
             f"intercepted by a central angle of {ang}°?")

    def pi(x):
        x = F(x)
        if x.denominator == 1:
            return f"{x.numerator}&pi;" if x.numerator != 1 else "&pi;"
        return frac(f"{x.numerator}&pi;" if x.numerator != 1 else "&pi;", str(x.denominator))

    correct = pi(arc)
    cands = [pi(F(ang, 360) * r * r), pi(arc * 2), pi(F(ang, 180) * r), pi(F(ang, 360) * r)]
    wrong = []
    for c in cands:
        if c != correct and c not in wrong:
            wrong.append(c)
    why = f"Arc length = ({ang}/360)(2&pi;{v('r')}) = ({n(F(ang, 360))})(2&pi; · {r}) = {correct}."
    return text(GEO, S_CIRC, html, correct, wrong[:3], why)


@tpl(GEO, 2)
def triangle_area_from_base(rng):
    b, h = rng.randint(4, 20), rng.randint(3, 16)
    if (b * h) % 2:
        b += 1
    html = p(f"A triangle has a base of {b} meters and an area of {b * h // 2} square meters. What is the height of the "
             f"triangle, in meters?")
    why = f"Area = ½ × base × height, so {b * h // 2} = ½({b})({v('h')}) and {v('h')} = {h}."
    return num(GEO, S_AREA, html, h, [F(h, 2), 2 * h, b * h // 2 - b], why, lo=1)


@tpl(GEO, 3, ("mc",))
def trig_ratio(rng):
    a, b, c = pick(rng, [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25), (20, 21, 29), (9, 40, 41), (12, 35, 37)])
    if rng.random() < 0.5:
        a, b = b, a
    # BC = a (opposite A), AC = b (opposite B), AB = c
    func, ang = pick(rng, [("cos", "B"), ("sin", "A"), ("tan", "A"), ("tan", "B"), ("sin", "B"), ("cos", "A")])
    ratios = {("sin", "A"): F(a, c), ("cos", "A"): F(b, c), ("tan", "A"): F(a, b),
              ("sin", "B"): F(b, c), ("cos", "B"): F(a, c), ("tan", "B"): F(b, a)}
    names = {("sin", "A"): "BC/AB", ("cos", "A"): "AC/AB", ("tan", "A"): "BC/AC",
             ("sin", "B"): "AC/AB", ("cos", "B"): "BC/AB", ("tan", "B"): "AC/BC"}
    correct_v = ratios[(func, ang)]
    html = p(f"In right triangle {v('ABC')}, angle {v('C')} is a right angle, {v('BC')} = {a}, {v('AC')} = {b}, and "
             f"{v('AB')} = {c}. What is the value of {func} {v(ang)}?")
    why = f"{func} {v(ang)} = {names[(func, ang)]} = {n(correct_v)} (SOH-CAH-TOA, measured from angle {v(ang)})."
    plaus = [F(a, c), F(b, c), F(a, b), F(b, a)]
    return num(GEO, S_RTT, html, correct_v, plaus, why,
               fmt=lambda x: frac(str(x.numerator), str(x.denominator)) if x.denominator != 1 else str(x), lo=0,
               spr_ok=False)


@tpl(GEO, 3)
def circle_complete_square(rng):
    h, k, r = nz(rng, -6, 6), nz(rng, -6, 6), rng.randint(2, 9)
    c = h * h + k * k - r * r
    html = p(f"The equation {poly((1, X2), (-2 * h, X), (1, f'{Y}<sup>2</sup>'), (-2 * k, Y), (c, ''))} = 0 defines a circle in "
             f"the {X}{Y}-plane. What is the radius of the circle?")
    why = (f"Complete the square: ({X}{signed(-h, '')})<sup>2</sup> + ({Y}{signed(-k, '')})<sup>2</sup> = {h * h} + {k * k}"
           f"{signed(-c, '')} = {r * r}. The radius is {r}.")
    return num(GEO, S_CIRC, html, r, [r * r, abs(c) if abs(c) not in (r, r * r) else r + 2, h * h + k * k], why, lo=1)


@tpl(GEO, 3)
def cylinder_volume_ratio(rng):
    r, h = rng.randint(2, 6), rng.randint(3, 10)
    kr = pick(rng, [2, 3])
    ratio = kr * kr
    html = p(f"Cylinder A has radius {r} and height {h}. Cylinder B has radius {kr * r} and height {h}. The volume of cylinder B "
             f"is how many times the volume of cylinder A?")
    why = f"Volume = &pi;{v('r')}<sup>2</sup>{v('h')}. Multiplying the radius by {kr} multiplies the volume by {kr}<sup>2</sup> = {ratio}."
    return num(GEO, S_AREA, html, ratio, [kr, kr ** 3, 2 * kr], why, lo=1)


@tpl(GEO, 3)
def isosceles_exterior(rng):
    apex = rng.randint(20, 100)
    if apex % 2:
        apex += 1
    base_ang = (180 - apex) // 2
    ext = 180 - base_ang
    html = p(f"In isosceles triangle {v('PQR')}, {v('PQ')} = {v('PR')}, and the measure of angle {v('P')} is {apex}°. Side "
             f"{v('QR')} is extended past {v('R')} to point {v('S')}. What is the measure, in degrees, of angle {v('PRS')}?")
    why = (f"The base angles are equal: (180 {MINUS} {apex}) ÷ 2 = {base_ang}°. Angle {v('PRS')} is supplementary to angle "
           f"{v('PRQ')}: 180 {MINUS} {base_ang} = {ext}°.")
    return num(GEO, S_LAT, html, ext, [base_ang, 180 - apex, apex + base_ang if apex + base_ang != ext else ext + 10], why, lo=1)
