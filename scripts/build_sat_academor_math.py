"""Build an original Academor SAT Math practice test (44 questions).

The test follows the digital SAT Math blueprint:
  * 2 modules x 22 questions, 35 minutes each (70 minutes in total)
  * per module: 8 Algebra, 8 Advanced Math, 3 Problem-Solving and Data Analysis,
    3 Geometry and Trigonometry; questions run from easier to harder
  * about a quarter of the questions are student-produced response (SPR) items
    (positions 6, 7, 13, 14, 20 and 21 in each module); the rest are 4-choice items
  * 12 figures (graphs in the xy-plane, a scatterplot, a bar graph, tables and
    geometry figures) rendered as PNGs and embedded as data URIs, the same format
    the PDF-based SAT builders use

Math is written as plain HTML (the portal has no TeX renderer): exponents use <sup>,
fractions use a small stacked inline block, variables are italic.

Output: academor/portals/resources/sat_questions/academor_sat_math_test_1.json
Load:   python academor/manage.py load_sat_quiz_resources --file academor_sat_math_test_1.json

Requires matplotlib (not a runtime dependency of the site):
    uv run --with matplotlib python scripts/build_sat_academor_math.py
"""

from __future__ import annotations

import base64
import io
import json
import math
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Arc, Circle  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "academor" / "portals" / "resources" / "sat_questions"
OUT_FILE = OUT_DIR / "academor_sat_math_test_1.json"

LETTERS = "ABCD"
SPR_POSITIONS = {6, 7, 13, 14, 20, 21}
ALG, ADV, PSDA, GEO = (
    "Algebra",
    "Advanced Math",
    "Problem-Solving and Data Analysis",
    "Geometry and Trigonometry",
)

INK = "#1f1f1f"
DARK = "#3b3b3b"
GRID = "#d4d4d4"
plt.rcParams.update({"font.size": 10, "mathtext.fontset": "dejavusans"})


# ---------------------------------------------------------------------------
# HTML math helpers
# ---------------------------------------------------------------------------

def v(name: str) -> str:
    """Italic variable."""
    return f"<i>{name}</i>"


def frac(num: str, den: str) -> str:
    """Stacked fraction that renders without a TeX engine."""
    return (
        "<span style=\"display:inline-flex;flex-direction:column;vertical-align:middle;"
        "text-align:center;font-size:0.88em;line-height:1.15;margin:0 0.12em;\">"
        f"<span style=\"border-bottom:1px solid currentColor;padding:0 0.18em;\">{num}</span>"
        f"<span style=\"padding:0 0.18em;\">{den}</span></span>"
    )


def p(text: str) -> str:
    return f"<p>{text}</p>"


X, Y = v("x"), v("y")
MINUS = "−"


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------

def _fig_to_uri(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="white", pad_inches=0.12)
    plt.close(fig)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def _img(uri: str, alt: str, width: int = 420) -> str:
    return (
        f'<p><img alt="{alt}" src="{uri}" '
        f'style="width:{width}px;max-width:100%;height:auto;display:block;"/></p>'
    )


def coord_plane(xlim, ylim, curves=(), points=(), step=1, label_every=2, size=(4.2, 4.2), alt="graph"):
    """SAT-style xy-plane: light grid, arrowed axes, labelled ticks, origin O."""
    fig, ax = plt.subplots(figsize=size)
    ax.set_xlim(xlim[0] - 0.4, xlim[1] + 0.6)
    ax.set_ylim(ylim[0] - 0.4, ylim[1] + 0.6)
    ax.set_aspect("equal" if size[0] == size[1] else "auto")
    for gx in range(xlim[0], xlim[1] + 1, step):
        ax.axvline(gx, color=GRID, lw=0.6, zorder=0)
    for gy in range(ylim[0], ylim[1] + 1, step):
        ax.axhline(gy, color=GRID, lw=0.6, zorder=0)
    arrow = dict(arrowstyle="-|>", color=INK, lw=1.1, mutation_scale=10)
    ax.annotate("", xy=(xlim[1] + 0.55, 0), xytext=(xlim[0] - 0.35, 0), arrowprops=arrow)
    ax.annotate("", xy=(0, ylim[1] + 0.55), xytext=(0, ylim[0] - 0.35), arrowprops=arrow)
    ax.text(xlim[1] + 0.5, -0.25, "$x$", ha="right", va="top", fontsize=11)
    ax.text(0.25, ylim[1] + 0.5, "$y$", ha="left", va="top", fontsize=11)
    ax.text(-0.22, -0.22, "$O$", ha="right", va="top", fontsize=10)
    for t in range(xlim[0], xlim[1] + 1):
        if t != 0 and t % label_every == 0:
            ax.text(t, -0.3, str(t).replace("-", MINUS), ha="center", va="top", fontsize=8.5, zorder=2,
                    bbox=dict(facecolor="white", edgecolor="none", pad=0.6))
    for t in range(ylim[0], ylim[1] + 1):
        if t != 0 and t % label_every == 0:
            ax.text(-0.25, t, str(t).replace("-", MINUS), ha="right", va="center", fontsize=8.5, zorder=2,
                    bbox=dict(facecolor="white", edgecolor="none", pad=0.6))
    for fn, x0, x1 in curves:
        xs = [x0 + (x1 - x0) * i / 400 for i in range(401)]
        pts = [(xx, fn(xx)) for xx in xs]
        pts = [(xx, yy) for xx, yy in pts if ylim[0] - 0.4 <= yy <= ylim[1] + 0.6]
        ax.plot([q[0] for q in pts], [q[1] for q in pts], color=INK, lw=1.9, zorder=3)
    for px, py in points:
        ax.plot(px, py, "o", color=INK, ms=4.5, zorder=4)
    ax.axis("off")
    return _img(_fig_to_uri(fig), alt)


def scatter_figure():
    data = [(1, 56), (1.5, 62), (2, 60), (2.5, 66), (3, 69), (3.5, 68), (4, 70), (4.5, 76),
            (5, 79), (5.5, 77), (6, 80), (6.5, 86), (7, 88), (7.5, 87), (8, 93)]
    fig, ax = plt.subplots(figsize=(5.2, 3.8))
    ax.scatter([d[0] for d in data], [d[1] for d in data], color=INK, s=18, zorder=3)
    ax.plot([0, 9], [52, 97], color=DARK, lw=1.4, zorder=2)
    ax.set_xlim(0, 9)
    ax.set_ylim(40, 100)
    ax.set_xticks(range(0, 10))
    ax.set_yticks(range(40, 101, 10))
    ax.grid(color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.set_xlabel("Hours spent studying", fontsize=10)
    ax.set_ylabel("Test score", fontsize=10)
    ax.set_title("Study Time and Test Scores", fontsize=11, fontweight="bold", pad=8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    return _img(_fig_to_uri(fig), "Scatterplot of test score versus hours spent studying with a line of best fit", 460)


def bar_figure():
    fig, ax = plt.subplots(figsize=(5.0, 3.5))
    xs, ys = [0, 1, 2, 3, 4], [2, 5, 6, 4, 3]
    ax.bar(xs, ys, color=DARK, width=0.62, edgecolor=INK, zorder=3)
    ax.set_xticks(xs)
    ax.set_yticks(range(0, 8))
    ax.set_ylim(0, 7)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.set_xlabel("Number of books read", fontsize=10)
    ax.set_ylabel("Number of students", fontsize=10)
    ax.set_title("Books Read Last Month", fontsize=11, fontweight="bold", pad=8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    return _img(_fig_to_uri(fig), "Bar graph of the number of books read last month by 20 students", 440)


def table_figure(header, rows, alt, col_widths=None, width=380, title=None):
    header_h = 0.58 if any("\n" in h for h in header) else 0.42
    row_h = 0.34
    h = header_h + row_h * len(rows)
    fig, ax = plt.subplots(figsize=(4.6, h))
    ax.axis("off")
    t = ax.table(cellText=rows, colLabels=header, cellLoc="center", bbox=[0, 0, 1, 1], colWidths=col_widths)
    t.auto_set_font_size(False)
    t.set_fontsize(10)
    for (r, c), cell in t.get_celld().items():
        cell.set_edgecolor(INK)
        cell.set_linewidth(0.8)
        cell.set_height((header_h if r == 0 else row_h) / h)
        if r == 0:
            cell.set_facecolor("#e6e6e6")
            cell.set_text_props(fontweight="bold")
    if title:
        ax.set_title(title, fontsize=10.5, fontweight="bold", pad=6)
    return _img(_fig_to_uri(fig), alt, width)


def parallel_lines_figure():
    fig, ax = plt.subplots(figsize=(4.4, 3.0))
    th = math.radians(65)
    ax.plot([-3, 3.6], [1.5, 1.5], color=INK, lw=1.4)
    ax.plot([-3, 3.6], [-1.0, -1.0], color=INK, lw=1.4)
    def tx(y):  # transversal t passes through (-0.4, -1) at 65 degrees
        return -0.4 + (y + 1.0) / math.tan(th)

    ax.plot([tx(-2.0), tx(2.6)], [-2.0, 2.6], color=INK, lw=1.4)
    # intersections of the transversal x = -0.4 + (y + 1)/tan(th)
    top = (tx(1.5), 1.5)
    bot = (-0.4, -1.0)
    ax.add_patch(Arc(top, 0.9, 0.9, theta1=65, theta2=180, color=INK, lw=1))
    ax.text(top[0] + 0.62 * math.cos(math.radians(122)), top[1] + 0.62 * math.sin(math.radians(122)),
            "115°", ha="center", va="center", fontsize=10)
    ax.add_patch(Arc(bot, 0.9, 0.9, theta1=0, theta2=65, color=INK, lw=1))
    ax.text(bot[0] + 0.78 * math.cos(math.radians(30)), bot[1] + 0.78 * math.sin(math.radians(30)),
            "$x°$", ha="center", va="center", fontsize=10.5)
    ax.text(3.7, 1.5, r"$\ell$", va="center", fontsize=12)
    ax.text(3.7, -1.0, "$m$", va="center", fontsize=11)
    ax.text(tx(2.55) + 0.12, 2.5, "$t$", fontsize=11)
    ax.set_xlim(-3.1, 4.1)
    ax.set_ylim(-2.1, 2.8)
    ax.set_aspect("equal")
    ax.axis("off")
    return _img(_fig_to_uri(fig), "Parallel lines l and m cut by transversal t with angles 115 degrees and x degrees", 380)


def circle_figure():
    fig, ax = plt.subplots(figsize=(3.4, 3.4))
    ax.add_patch(Circle((0, 0), 1, fill=False, color=INK, lw=1.4))
    a1, a2 = math.radians(20), math.radians(92)
    A = (math.cos(a1), math.sin(a1))
    B = (math.cos(a2), math.sin(a2))
    ax.plot([0, A[0]], [0, A[1]], color=INK, lw=1.2)
    ax.plot([0, B[0]], [0, B[1]], color=INK, lw=1.2)
    for pt in ((0, 0), A, B):
        ax.plot(*pt, "o", color=INK, ms=3.5)
    ax.add_patch(Arc((0, 0), 0.42, 0.42, theta1=20, theta2=92, color=INK, lw=1))
    ax.text(0.31 * math.cos(math.radians(56)), 0.31 * math.sin(math.radians(56)), "72°", fontsize=9,
            ha="center", va="center")
    ax.text(-0.08, -0.12, "$O$", fontsize=11, ha="right")
    ax.text(A[0] + 0.07, A[1], "$A$", fontsize=11, va="center")
    ax.text(B[0], B[1] + 0.08, "$B$", fontsize=11, ha="center", va="bottom")
    ax.text(0.5 * A[0] + 0.04, 0.5 * A[1] - 0.12, "10", fontsize=9.5)
    ax.set_xlim(-1.2, 1.25)
    ax.set_ylim(-1.2, 1.25)
    ax.set_aspect("equal")
    ax.axis("off")
    return _img(_fig_to_uri(fig), "Circle with center O, radius 10 and central angle AOB of 72 degrees", 300)


def right_triangle_figure():
    fig, ax = plt.subplots(figsize=(4.2, 2.8))
    C, A, B = (0, 0), (4.8, 0), (0, 2.0)
    ax.plot([C[0], A[0], B[0], C[0]], [C[1], A[1], B[1], C[1]], color=INK, lw=1.4)
    s = 0.22
    ax.plot([s, s, 0], [0, s, s], color=INK, lw=1)
    ax.text(-0.15, -0.15, "$C$", ha="right", va="top", fontsize=11)
    ax.text(A[0] + 0.12, -0.12, "$A$", ha="left", va="top", fontsize=11)
    ax.text(-0.12, B[1] + 0.1, "$B$", ha="right", va="bottom", fontsize=11)
    ax.text(A[0] / 2, -0.18, "24", ha="center", va="top", fontsize=10.5)
    ax.text(A[0] / 2 + 0.2, B[1] / 2 + 0.22, "26", ha="center", va="bottom", fontsize=10.5)
    ax.set_xlim(-0.6, 5.4)
    ax.set_ylim(-0.7, 2.6)
    ax.set_aspect("equal")
    ax.axis("off")
    return _img(_fig_to_uri(fig), "Right triangle ABC with right angle C, AC = 24 and AB = 26", 360)


def similar_triangles_figure():
    fig, ax = plt.subplots(figsize=(4.2, 3.0))
    A, B, C = (1.6, 3.0), (0, 0), (4.6, 0)
    k = 0.6
    D = (A[0] + k * (B[0] - A[0]), A[1] + k * (B[1] - A[1]))
    E = (A[0] + k * (C[0] - A[0]), A[1] + k * (C[1] - A[1]))
    ax.plot([A[0], B[0], C[0], A[0]], [A[1], B[1], C[1], A[1]], color=INK, lw=1.4)
    ax.plot([D[0], E[0]], [D[1], E[1]], color=INK, lw=1.4)
    ax.text(A[0], A[1] + 0.12, "$A$", ha="center", va="bottom", fontsize=11)
    ax.text(B[0] - 0.12, B[1] - 0.05, "$B$", ha="right", va="top", fontsize=11)
    ax.text(C[0] + 0.12, C[1] - 0.05, "$C$", ha="left", va="top", fontsize=11)
    ax.text(D[0] - 0.14, D[1], "$D$", ha="right", va="center", fontsize=11)
    ax.text(E[0] + 0.14, E[1], "$E$", ha="left", va="center", fontsize=11)
    ax.text((A[0] + D[0]) / 2 - 0.16, (A[1] + D[1]) / 2 + 0.05, "6", ha="right", fontsize=10.5)
    ax.text((D[0] + B[0]) / 2 - 0.16, (D[1] + B[1]) / 2, "4", ha="right", fontsize=10.5)
    ax.text((D[0] + E[0]) / 2, D[1] + 0.08, "9", ha="center", va="bottom", fontsize=10.5)
    ax.set_xlim(-0.6, 5.2)
    ax.set_ylim(-0.5, 3.5)
    ax.set_aspect("equal")
    ax.axis("off")
    return _img(_fig_to_uri(fig), "Triangle ABC with segment DE parallel to BC, AD = 6, DB = 4, DE = 9", 340)


# ---------------------------------------------------------------------------
# Question builders
# ---------------------------------------------------------------------------

def mcq(domain, skill, html, options, answer):
    assert len(options) == 4 and len(set(options)) == 4, (skill, options)
    return {"domain": domain, "skill": skill, "question": html, "options": options,
            "correct": options[LETTERS.index(answer)], "letter": answer}


def spr(domain, skill, html, answers):
    return {"domain": domain, "skill": skill, "question": html, "question_type": "spr",
            "spr_correct_answers": answers, "spr_max_length": 6, "letter": None}


def module_1():
    fig_line = coord_plane((-2, 8), (-2, 6), curves=[(lambda x: -0.5 * x + 3, -2, 8)],
                           points=[(0, 3), (6, 0)], label_every=2, size=(4.4, 3.4),
                           alt="Graph of a line through (0, 3) and (6, 0)")
    fig_parab = coord_plane((-2, 6), (-5, 5), curves=[(lambda x: (x - 2) ** 2 - 4, -1.2, 5.2)],
                            label_every=2, size=(3.6, 4.4), alt="Graph of an upward parabola with vertex (2, -4)")
    return [
        mcq(ALG, "Linear equations in one variable",
            p(f"If 4{X} + 7 = 31, what is the value of {X}?"),
            ["6", "7.75", "9.5", "24"], "A"),
        mcq(ALG, "Linear equations in one variable",
            p(f"If 3({X} {MINUS} 2) = 15, what is the value of {X} {MINUS} 2?"),
            ["3", "5", "7", "13"], "B"),
        mcq(ALG, "Linear functions",
            p(f"The graph of the linear function {v('f')} is shown.") + fig_line
            + p(f"Which equation defines {v('f')}?"),
            [f"{v('f')}({X}) = {frac('1', '2')}{X} + 3",
             f"{v('f')}({X}) = {MINUS}2{X} + 3",
             f"{v('f')}({X}) = {MINUS}{frac('1', '2')}{X} + 3",
             f"{v('f')}({X}) = {MINUS}{frac('1', '2')}{X} + 6"], "C"),
        mcq(ADV, "Equivalent expressions",
            p(f"Which expression is equivalent to (3{X}<sup>2</sup> + 5{X} {MINUS} 2) {MINUS} "
              f"({X}<sup>2</sup> {MINUS} 4{X} + 6)?"),
            [f"2{X}<sup>2</sup> + {X} + 4", f"2{X}<sup>2</sup> + {X} {MINUS} 8",
             f"4{X}<sup>2</sup> + 9{X} + 4", f"2{X}<sup>2</sup> + 9{X} {MINUS} 8"], "D"),
        mcq(GEO, "Lines, angles, and triangles",
            p(f"In the figure, line {v('&#8467;')} is parallel to line {v('m')}, and both lines are "
              f"intersected by line {v('t')}.") + parallel_lines_figure()
            + p(f"What is the value of {X}?"),
            ["25", "55", "65", "115"], "C"),
        spr(ALG, "Linear equations in one variable",
            p("A gym charges a one-time sign-up fee of $40 plus $25 per month. A member has paid a total "
              "of $315 for the sign-up fee and monthly charges. For how many months has the member paid?"),
            ["11"]),
        spr(ADV, "Nonlinear equations in one variable and systems of equations in two variables",
            p(f"If {X}<sup>2</sup> {MINUS} 10{X} + 21 = 0 and {X} &gt; 5, what is the value of {X}?"),
            ["7"]),
        mcq(PSDA, "Two-variable data: models and scatterplots",
            p("The scatterplot shows the number of hours 15 students spent studying for a test and their "
              "test scores. A line of best fit is also shown.") + scatter_figure()
            + p("The line of best fit has the equation " + f"{Y} = 5{X} + 52, where {Y} is the predicted test score "
                f"and {X} is the number of hours spent studying. Based on the line of best fit, what is the "
                "predicted test score for a student who studied for 6 hours?"),
            ["67", "72", "77", "82"], "D"),
        mcq(ALG, "Systems of two linear equations in two variables",
            p(f"2{X} + {Y} = 11<br>{X} {MINUS} {Y} = 1")
            + p(f"If ({X}, {Y}) is the solution to the system of equations above, what is the value of {Y}?"),
            ["2", "3", "4", "5"], "B"),
        mcq(ADV, "Nonlinear functions",
            p(f"The function {v('f')} is defined by {v('f')}({X}) = 3{X}<sup>2</sup> {MINUS} 2. "
              f"What is the value of {v('f')}({MINUS}2)?"),
            [f"{MINUS}14", f"{MINUS}10", "10", "34"], "C"),
        mcq(ADV, "Equivalent expressions",
            p(f"Which expression is equivalent to {X}<sup>2</sup> {MINUS} 49?"),
            [f"({X} + 7)({X} {MINUS} 7)", f"({X} {MINUS} 7)<sup>2</sup>", f"({X} + 7)<sup>2</sup>",
             f"({X} {MINUS} 49)({X} + 1)"], "A"),
        mcq(ALG, "Linear inequalities in one or two variables",
            p("A delivery van can carry a load of at most 1,200 kilograms. The driver weighs 80 kilograms, "
              f"and each box weighs 35 kilograms. Which inequality represents the possible numbers of boxes, "
              f"{v('b')}, that the van can carry along with the driver?"),
            [f"80 + 35{v('b')} &ge; 1,200", f"80 + 35{v('b')} &le; 1,200", f"35 + 80{v('b')} &le; 1,200",
             f"80{v('b')} + 35{v('b')} &le; 1,200"], "B"),
        spr(PSDA, "Ratios, rates, proportional relationships, and units",
            p("A printer prints 18 pages every 45 seconds. At this rate, how many pages does the printer "
              "print in 6 minutes?"),
            ["144"]),
        spr(GEO, "Right triangles and trigonometry",
            p(f"Triangle {v('ABC')} is a right triangle with its right angle at {v('C')}. The length of "
              f"{v('AC')} is 9, and the area of triangle {v('ABC')} is 54. What is the length of {v('AB')}?"),
            ["15"]),
        mcq(ADV, "Nonlinear functions",
            p(f"The graph of {Y} = {v('f')}({X}) is shown.") + fig_parab
            + p(f"Which equation could define {v('f')}?"),
            [f"{v('f')}({X}) = ({X} + 2)<sup>2</sup> {MINUS} 4", f"{v('f')}({X}) = ({X} {MINUS} 2)<sup>2</sup> + 4",
             f"{v('f')}({X}) = {MINUS}({X} {MINUS} 2)<sup>2</sup> {MINUS} 4",
             f"{v('f')}({X}) = ({X} {MINUS} 2)<sup>2</sup> {MINUS} 4"], "D"),
        mcq(PSDA, "One-variable data: distributions and measures of center and spread",
            p("The bar graph shows the number of books each of 20 students read last month.") + bar_figure()
            + p("Which of the following statements about the data is true?"),
            ["The median is greater than the mean.", "The mean is equal to the mode.",
             "The mean is greater than the median.", "The range of the data is 3."], "C"),
        mcq(ALG, "Linear equations in two variables",
            p(f"The equation {v('C')} = 1.5{v('m')} + 4 gives the cost {v('C')}, in dollars, of a taxi ride "
              f"of {v('m')} miles. What is the best interpretation of 1.5 in this context?"),
            ["The cost per mile of the ride, in dollars", "The total cost, in dollars, of a 1-mile ride",
             "The fixed starting fee, in dollars", "The number of miles the taxi travels per dollar"], "A"),
        mcq(ADV, "Nonlinear functions",
            p("A population of bacteria doubles every 3 hours. The initial population is 500. Which function "
              f"gives the population {v('P')} after {v('t')} hours?"),
            [f"{v('P')}({v('t')}) = 500(2)<sup>{v('t')}/3</sup>", f"{v('P')}({v('t')}) = 500(2)<sup>3{v('t')}</sup>",
             f"{v('P')}({v('t')}) = 500(3)<sup>{v('t')}/2</sup>", f"{v('P')}({v('t')}) = 2(500)<sup>{v('t')}/3</sup>"],
            "A"),
        mcq(GEO, "Circles",
            p(f"A circle in the {X}{Y}-plane has the equation ({X} {MINUS} 3)<sup>2</sup> + ({Y} + 1)<sup>2</sup> = 49. "
              "Which of the following gives the center and the radius of the circle?"),
            [f"Center ({MINUS}3, 1), radius 7", f"Center (3, {MINUS}1), radius 7",
             f"Center (3, {MINUS}1), radius 49", f"Center ({MINUS}3, 1), radius 49"], "B"),
        spr(ADV, "Equivalent expressions",
            p(f"If 3<sup>{X} + 2</sup> = 243, what is the value of {X}?"),
            ["3"]),
        spr(ALG, "Linear functions",
            p(f"In the {X}{Y}-plane, the line with equation {Y} = {v('m')}{X} + {v('b')} passes through the "
              f"points (2, 5) and (6, 17), where {v('m')} and {v('b')} are constants. What is the value of {v('b')}?"),
            ["-1"]),
        mcq(ADV, "Nonlinear equations in one variable and systems of equations in two variables",
            p(f"In the equation {X}<sup>2</sup> + 6{X} + {v('k')} = 0, {v('k')} is a constant. For what value of "
              f"{v('k')} does the equation have exactly one real solution?"),
            [f"{MINUS}9", "3", "6", "9"], "D"),
    ]


def module_2():
    fig_exp = coord_plane((-2, 4), (-1, 9), curves=[(lambda x: 8 * 0.5 ** x, -1.5, 4)],
                          points=[(0, 8), (1, 4), (2, 2)], label_every=2, size=(3.4, 4.4),
                          alt="Graph of a decreasing exponential curve through (0, 8), (1, 4) and (2, 2)")
    fig_down = coord_plane((-6, 4), (-4, 10), curves=[(lambda x: -(x + 4) * (x - 2), -5.3, 3.3)],
                           points=[(-4, 0), (2, 0), (-1, 9)], label_every=2, size=(3.8, 4.6),
                           alt="Graph of a downward parabola with x-intercepts -4 and 2 and vertex (-1, 9)")
    fig_table = table_figure(["$x$", "$f(x)$"], [["1", "7"], ["3", "13"], ["5", "19"], ["7", "25"]],
                             "Table of values: f(1) = 7, f(3) = 13, f(5) = 19, f(7) = 25",
                             width=220)
    fig_two_way = table_figure(
        ["", "Plays an\ninstrument", "Does not play\nan instrument", "Total"],
        [["10th grade", "36", "64", "100"], ["11th grade", "54", "46", "100"], ["Total", "90", "110", "200"]],
        "Two-way table of 200 students by grade and whether they play an instrument",
        col_widths=[0.26, 0.26, 0.3, 0.18], width=440)
    return [
        mcq(ALG, "Linear equations in one variable",
            p(f"If 2(3{X} {MINUS} 5) = 4{X} + 8, what is the value of {X}?"),
            [f"{MINUS}1", "4.5", "9", "18"], "C"),
        mcq(ALG, "Linear functions",
            p(f"The function {v('f')}({X}) = 250 {MINUS} 12{X} models the amount of fuel {v('f')}({X}), in liters, "
              f"remaining in a generator's tank after {X} hours of use. What is the value of {v('f')}(10)?"),
            ["120", "130", "238", "370"], "B"),
        mcq(ALG, "Linear functions",
            p(f"The table shows four values of {X} and their corresponding values of {v('f')}({X}) for the "
              f"linear function {v('f')}.") + fig_table + p(f"Which equation defines {v('f')}?"),
            [f"{v('f')}({X}) = 3{X} + 4", f"{v('f')}({X}) = 6{X} + 1", f"{v('f')}({X}) = 3{X} + 7",
             f"{v('f')}({X}) = 4{X} + 3"], "A"),
        mcq(ADV, "Nonlinear functions",
            p(f"The graph of {Y} = {v('f')}({X}) is shown, where {v('f')}({X}) = {v('a')}({v('b')})<sup>{X}</sup> "
              f"and {v('a')} and {v('b')} are positive constants.") + fig_exp
            + p(f"Which equation could define {v('f')}?"),
            [f"{v('f')}({X}) = 8(2)<sup>{X}</sup>", f"{v('f')}({X}) = 4(0.5)<sup>{X}</sup>",
             f"{v('f')}({X}) = 8(0.5)<sup>{X}</sup>", f"{v('f')}({X}) = 0.5(8)<sup>{X}</sup>"], "C"),
        mcq(GEO, "Circles",
            p(f"In the figure, points {v('A')} and {v('B')} lie on the circle with center {v('O')}. The radius "
              f"of the circle is 10, and the measure of angle {v('AOB')} is 72&deg;.") + circle_figure()
            + p(f"What is the length of the shorter arc {v('AB')}?"),
            ["2&pi;", "4&pi;", "20&pi;", "72&pi;"], "B"),
        spr(ALG, "Systems of two linear equations in two variables",
            p("At a theater, adult tickets cost $12 each and child tickets cost $7 each. A group bought "
              "15 tickets for a total of $145. How many adult tickets did the group buy?"),
            ["8"]),
        spr(ADV, "Nonlinear functions",
            p(f"The function {v('g')} is defined by {v('g')}({X}) = {X}<sup>2</sup> {MINUS} 6{X} + {v('c')}, "
              f"where {v('c')} is a constant. If the minimum value of {v('g')}({X}) is 11, what is the value "
              f"of {v('c')}?"),
            ["20"]),
        mcq(PSDA, "Probability and conditional probability",
            p("The table shows the results of a survey of 200 students about whether they play a musical "
              "instrument.") + fig_two_way
            + p("If one of the students who play an instrument is selected at random, what is the probability "
                "that the student is in 11th grade?"),
            [frac("27", "100"), frac("9", "20"), frac("27", "50"), frac("3", "5")], "D"),
        mcq(ALG, "Linear inequalities in one or two variables",
            p(f"{Y} &gt; 2{X} {MINUS} 3<br>{X} + {Y} &lt; 6")
            + p(f"Which point ({X}, {Y}) is a solution to the system of inequalities above?"),
            ["(1, 2)", "(3, 4)", "(4, 1)", f"(0, {MINUS}4)"], "A"),
        mcq(ADV, "Equivalent expressions",
            p("Which expression is equivalent to "
              + frac(f"{X}<sup>2</sup> {MINUS} 9", f"{X}<sup>2</sup> + {X} {MINUS} 6")
              + f", for {X} &gt; 2?"),
            [frac(f"{X} {MINUS} 3", f"{X} {MINUS} 2"), frac(f"{X} + 3", f"{X} {MINUS} 2"),
             frac(f"{X} {MINUS} 3", f"{X} + 2"), frac(f"{MINUS}3", f"{X} {MINUS} 2")], "A"),
        mcq(GEO, "Right triangles and trigonometry",
            p(f"In right triangle {v('ABC')}, angle {v('C')} is a right angle, {v('AC')} = 24, and {v('AB')} = 26.")
            + right_triangle_figure() + p(f"What is the value of sin {v('A')}?"),
            [frac("5", "12"), frac("5", "13"), frac("12", "13"), frac("12", "5")], "B"),
        mcq(ALG, "Linear functions",
            p("A water tank contains 900 liters of water. Water drains from the tank at a constant rate, and "
              f"after 15 minutes the tank contains 660 liters. Which function gives the volume {v('V')}, in "
              f"liters, of water in the tank {v('t')} minutes after it starts draining?"),
            [f"{v('V')}({v('t')}) = 900 {MINUS} 16{v('t')}", f"{v('V')}({v('t')}) = 660 {MINUS} 16{v('t')}",
             f"{v('V')}({v('t')}) = 900 {MINUS} 15{v('t')}", f"{v('V')}({v('t')}) = 900 {MINUS} 240{v('t')}"], "A"),
        spr(PSDA, "One-variable data: distributions and measures of center and spread",
            p("The mean of a list of 5 numbers is 18. When a sixth number is added to the list, the mean of "
              "the 6 numbers is 20. What is the sixth number?"),
            ["30"]),
        spr(ADV, "Nonlinear equations in one variable and systems of equations in two variables",
            p(f"The function {v('f')} is defined by {v('f')}({X}) = " + frac(f"{X} + 4", f"{X} {MINUS} 2")
              + f". If {v('f')}({v('a')}) = 3, what is the value of {v('a')}?"),
            ["5"]),
        mcq(ADV, "Nonlinear equations in one variable and systems of equations in two variables",
            p(f"{Y} = {X}<sup>2</sup> {MINUS} 4{X} + 7<br>{Y} = 2{X} {MINUS} 2")
            + p(f"The system of equations above has exactly one solution, ({X}, {Y}). What is the value of {X} + {Y}?"),
            ["3", "4", "7", "12"], "C"),
        mcq(PSDA, "Inference from sample statistics and margin of error",
            p("A random sample of 400 residents of a city was surveyed, and 62% of those surveyed said they "
              "support building a new park. The margin of error for this estimate is 4 percentage points. "
              "Which of the following is the most appropriate conclusion?"),
            ["Exactly 62% of all residents of the city support building the park.",
             "Between 58% and 66% of the 400 residents surveyed support building the park.",
             "It is plausible that between 58% and 66% of all residents of the city support building the park.",
             "At least 66% of all residents of the city support building the park."], "C"),
        mcq(ALG, "Linear equations in one variable",
            p(f"4({v('a')}{X} {MINUS} 3) = 12{X} + {v('b')}")
            + p(f"In the equation above, {v('a')} and {v('b')} are constants. If the equation has infinitely many "
                f"solutions, what is the value of {v('a')} + {v('b')}?"),
            [f"{MINUS}15", f"{MINUS}9", "9", "15"], "B"),
        mcq(ADV, "Nonlinear functions",
            p(f"The graph of {Y} = {v('f')}({X}) is shown.") + fig_down + p(f"Which equation could define {v('f')}?"),
            [f"{v('f')}({X}) = ({X} + 4)({X} {MINUS} 2)", f"{v('f')}({X}) = {MINUS}({X} {MINUS} 4)({X} + 2)",
             f"{v('f')}({X}) = {MINUS}({X} + 1)<sup>2</sup> {MINUS} 9", f"{v('f')}({X}) = {MINUS}({X} + 4)({X} {MINUS} 2)"],
            "D"),
        mcq(GEO, "Lines, angles, and triangles",
            p(f"In the figure, {v('D')} lies on {v('AB')}, {v('E')} lies on {v('AC')}, and {v('DE')} is parallel "
              f"to {v('BC')}. The lengths of {v('AD')}, {v('DB')}, and {v('DE')} are 6, 4, and 9, respectively.")
            + similar_triangles_figure() + p(f"What is the length of {v('BC')}?"),
            ["6", "13", "13.5", "15"], "D"),
        spr(ADV, "Equivalent expressions",
            p(f"If {X}<sup>3/2</sup> = 64 and {X} &gt; 0, what is the value of {X}?"),
            ["16"]),
        spr(ALG, "Systems of two linear equations in two variables",
            p(f"3{X} + {v('k')}{Y} = 8<br>6{X} + 12{Y} = 5")
            + p(f"In the system of equations above, {v('k')} is a constant. If the system has no solution, what "
                f"is the value of {v('k')}?"),
            ["6"]),
        mcq(ADV, "Equivalent expressions",
            p(f"({v('a')}{X} + 3)(2{X} {MINUS} {v('b')}) = 6{X}<sup>2</sup> {MINUS} 6{X} {MINUS} 12")
            + p(f"The equation above is true for all values of {X}, where {v('a')} and {v('b')} are constants. "
                f"What is the value of {v('a')} + {v('b')}?"),
            [f"{MINUS}1", "1", "4", "7"], "D"),
    ]


def build() -> dict:
    m1, m2 = module_1(), module_2()
    for name, module in (("Module 1", m1), ("Module 2", m2)):
        assert len(module) == 22, (name, len(module))
        spr_pos = {i + 1 for i, item in enumerate(module) if item.get("question_type") == "spr"}
        assert spr_pos == SPR_POSITIONS, (name, spr_pos)
        letters = Counter(item["letter"] for item in module if item["letter"])
        assert letters == {"A": 4, "B": 4, "C": 4, "D": 4}, (name, letters)
        domains = Counter(item["domain"] for item in module)
        assert domains == {ALG: 8, ADV: 8, PSDA: 3, GEO: 3}, (name, domains)

    questions = []
    for number, item in enumerate(m1 + m2, start=1):
        row = {
            "id": number,
            "module": 1 if number <= 22 else 2,
            "domain": item["domain"],
            "skill": item["skill"],
            "question": item["question"],
        }
        if item.get("question_type") == "spr":
            row.update({
                "question_type": "spr",
                "spr_correct_answers": item["spr_correct_answers"],
                "spr_max_length": item["spr_max_length"],
                "answer_key": f"<p><strong>Correct Answer: {item['spr_correct_answers'][0]}</strong></p>",
            })
        else:
            row.update({
                "options": item["options"],
                "correct": item["correct"],
                "answer_key": f"<p><strong>Correct Answer: {item['letter']}</strong></p>",
            })
        questions.append(row)

    return {
        "title": "Academor SAT Practice Test 1 Math",
        "category_name": "SAT Math",
        "service": "sat-math",
        "is_sat": True,
        "sat_section": "algebra",
        "time_limit_minutes": 70,
        "questions": questions,
    }


def main():
    data = build()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    with_img = sum(1 for item in data["questions"] if "<img" in item["question"])
    n_spr = sum(1 for item in data["questions"] if item.get("question_type") == "spr")
    print(f"OK {OUT_FILE.relative_to(REPO)}: {len(data['questions'])} questions ({n_spr} SPR), "
          f"{with_img} with figures, {OUT_FILE.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
