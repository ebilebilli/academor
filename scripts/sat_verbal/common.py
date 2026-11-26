"""Helpers shared by the Reading and Writing test files (scripts/sat_verbal/test_NN.py).

Re-exports the HTML, prompt and chart helpers of practice test 1 so every test looks the same.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build_sat_academor_verbal as base  # noqa: E402

p, notes, BLANK, LETTERS = base.p, base.notes, base.BLANK, base.LETTERS
CS, II, SEC, EOI = base.CS, base.II, base.SEC, base.EOI
P_WIC, P_FUNCTION, P_PURPOSE, P_STRUCTURE = base.P_WIC, base.P_FUNCTION, base.P_PURPOSE, base.P_STRUCTURE
P_MAIN_IDEA, P_GRAPH, P_TABLE, P_INFER = base.P_MAIN_IDEA, base.P_GRAPH, base.P_TABLE, base.P_INFER
P_SEC, P_TRANSITION, P_NOTES_Q = base.P_SEC, base.P_TRANSITION, base.P_NOTES_Q
bar_chart, grouped_bar_chart, line_chart, table_image = (
    base.bar_chart, base.grouped_bar_chart, base.line_chart, base.table_image,
)

WIC, TSP, CTC = "Words in Context", "Text Structure and Purpose", "Cross-Text Connections"
CID, COET, COEQ, INF = (
    "Central Ideas and Details", "Command of Evidence: Textual", "Command of Evidence: Quantitative", "Inferences",
)
FSS, BND = "Form, Structure, and Sense", "Boundaries"
TRN, RS = "Transitions", "Rhetorical Synthesis"

DOMAIN_OF = {WIC: CS, TSP: CS, CTC: CS, CID: II, COET: II, COEQ: II, INF: II, FSS: SEC, BND: SEC, TRN: EOI, RS: EOI}

P_CLAIM = "Which quotation from the text most effectively illustrates the claim?"
P_FINDING = "Which finding, if true, would most directly support the researchers' claim?"
P_WEAKEN = "Which finding, if true, would most directly weaken the researchers' claim?"
P_DETAIL = "According to the text, what is true about {x}?"
P_CTC = "Based on the texts, how would {a} (Text 2) most likely respond to {b} (Text 1)?"


def Q(skill, body_html, prompt, correct, wrong, why, figure=""):
    """One question: the correct choice first, then the three wrong choices."""
    assert len(wrong) == 3, (skill, wrong)
    return {
        "domain": DOMAIN_OF[skill],
        "skill": skill,
        # every "___" in a passage becomes the standard blank used on the test
        "question": f"{figure}{body_html.replace('___', BLANK)}{p(prompt)}",
        "correct": correct,
        "wrong": list(wrong),
        "why": why,
    }


def texts(t1, t2):
    """Paired passages for Cross-Text Connections."""
    return p("<strong>Text 1</strong>") + p(t1) + p("<strong>Text 2</strong>") + p(t2)


def blank(text):
    return p(text.replace("___", BLANK))


def underline(before, under, after=""):
    return p(f"{before}<u>{under}</u>{after}")
