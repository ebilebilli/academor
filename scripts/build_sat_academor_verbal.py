"""Build an original Academor SAT Reading and Writing practice test (54 questions).

The test follows the digital SAT Reading and Writing blueprint:
  * 2 modules x 27 questions (64 minutes in total), one short passage per question
  * each module runs Craft and Structure -> Information and Ideas ->
    Standard English Conventions -> Expression of Ideas
  * 3 quantitative Command of Evidence questions per module, each with a data
    graphic (bar graph, line graph or table) rendered as a PNG and embedded in the
    question HTML as a data URI (the same format the PDF-based SAT builders use)

All passages are original. Researchers named in science passages and the data in
the graphics are fictional unless the passage is about a well-known historical fact.

Output: academor/portals/resources/sat_questions/academor_sat_verbal_test_1.json
Load:   python academor/manage.py load_sat_quiz_resources --file academor_sat_verbal_test_1.json

Requires matplotlib (not a runtime dependency of the site):
    uv run --with matplotlib python scripts/build_sat_academor_verbal.py
"""

from __future__ import annotations

import base64
import io
import json
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "academor" / "portals" / "resources" / "sat_questions"
OUT_FILE = OUT_DIR / "academor_sat_verbal_test_1.json"

BLANK = "<strong>______</strong>"
LETTERS = "ABCD"

# Prompts used on the real test, word for word.
P_WIC = "Which choice completes the text with the most logical and precise word or phrase?"
P_FUNCTION = "Which choice best describes the function of the underlined sentence in the text as a whole?"
P_PURPOSE = "Which choice best states the main purpose of the text?"
P_STRUCTURE = "Which choice best describes the overall structure of the text?"
P_MAIN_IDEA = "Which choice best states the main idea of the text?"
P_GRAPH = "Which choice most effectively uses data from the graph to complete the statement?"
P_TABLE = "Which choice most effectively uses data from the table to complete the statement?"
P_INFER = "Which choice most logically completes the text?"
P_SEC = "Which choice completes the text so that it conforms to the conventions of Standard English?"
P_TRANSITION = "Which choice completes the text with the most logical transition?"
P_NOTES = "While researching a topic, a student has taken the following notes:"
P_NOTES_Q = "Which choice most effectively uses relevant information from the notes to accomplish this goal?"


# ---------------------------------------------------------------------------
# Data graphics
# ---------------------------------------------------------------------------

INK = "#1f1f1f"
DARK = "#3b3b3b"
LIGHT = "#a9a9a9"


def _style_axes(ax):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(INK)
        ax.spines[side].set_linewidth(0.9)
    ax.tick_params(colors=INK, labelsize=10)
    ax.yaxis.grid(True, color="#d9d9d9", linewidth=0.7)
    ax.set_axisbelow(True)


def _fig_to_uri(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="white", pad_inches=0.15)
    plt.close(fig)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def _img(uri: str, alt: str) -> str:
    return (
        f'<p><img alt="{alt}" src="{uri}" '
        f'style="width:560px;max-width:100%;height:auto;display:block;"/></p>'
    )


def bar_chart(title, categories, values, ylabel, ylim, alt, value_fmt="{:.1f}"):
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    bars = ax.bar(categories, values, color=DARK, width=0.58, edgecolor=INK, linewidth=0.6)
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + ylim * 0.012,
                value_fmt.format(value), ha="center", va="bottom", fontsize=9.5, color=INK)
    ax.set_ylim(0, ylim)
    ax.set_ylabel(ylabel, fontsize=10.5, color=INK)
    ax.set_title(title, fontsize=11.5, fontweight="bold", color=INK, pad=12)
    _style_axes(ax)
    return _img(_fig_to_uri(fig), alt)


def grouped_bar_chart(title, groups, series, ylabel, ylim, alt):
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    width = 0.36
    xs = range(len(groups))
    styles = ((DARK, None), (LIGHT, "///"))
    for i, ((label, values), (color, hatch)) in enumerate(zip(series, styles)):
        offs = [x + (i - 0.5) * width for x in xs]
        bars = ax.bar(offs, values, width=width, color=color, hatch=hatch,
                      edgecolor=INK, linewidth=0.6, label=label)
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + ylim * 0.012,
                    f"{value:.1f}", ha="center", va="bottom", fontsize=9, color=INK)
    ax.set_xticks(list(xs))
    ax.set_xticklabels(groups)
    ax.set_ylim(0, ylim)
    ax.set_ylabel(ylabel, fontsize=10.5, color=INK)
    ax.set_title(title, fontsize=11.5, fontweight="bold", color=INK, pad=12)
    ax.legend(frameon=False, fontsize=9.5, loc="upper right")
    _style_axes(ax)
    return _img(_fig_to_uri(fig), alt)


def line_chart(title, xs, series, ylabel, ylim, alt, xlabel="Year", note=None):
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    markers = (("o", "-", DARK), ("s", "--", "#6e6e6e"))
    for (label, values), (marker, ls, color) in zip(series, markers):
        ax.plot(xs, values, marker=marker, linestyle=ls, color=color, linewidth=1.8,
                markersize=5.5, label=label)
    ax.set_xticks(xs)
    ax.set_ylim(*ylim)
    ax.set_xlabel(xlabel, fontsize=10.5, color=INK)
    ax.set_ylabel(ylabel, fontsize=10.5, color=INK)
    ax.set_title(title, fontsize=11.5, fontweight="bold", color=INK, pad=12)
    if len(series) > 1:
        ax.legend(frameon=False, fontsize=9.5, loc="best")
    if note:
        ax.axvline(note[0], color="#8c8c8c", linewidth=1, linestyle=":")
        ax.text(note[0] + 0.2, ylim[1] - (ylim[1] - ylim[0]) * 0.06, note[1],
                fontsize=8.5, color="#555555", va="top")
    _style_axes(ax)
    return _img(_fig_to_uri(fig), alt)


def table_image(title, header, rows, alt, col_widths=None):
    header_h, row_h = 0.5, 0.32  # inches
    table_h = header_h + row_h * len(rows)
    fig, ax = plt.subplots(figsize=(6.4, table_h))
    ax.axis("off")
    table = ax.table(cellText=rows, colLabels=header, cellLoc="center", bbox=[0, 0, 1, 1],
                     colWidths=col_widths)
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    for (r, c), cell in table.get_celld().items():
        cell.set_edgecolor(INK)
        cell.set_linewidth(0.8)
        cell.set_height((header_h if r == 0 else row_h) / table_h)
        if r == 0:
            cell.set_facecolor("#e6e6e6")
            cell.set_text_props(fontweight="bold", color=INK)
        else:
            cell.set_text_props(color=INK)
            if c == 0:
                cell.set_text_props(ha="left", color=INK)
                cell.PAD = 0.04
    ax.set_title(title, fontsize=11.5, fontweight="bold", color=INK, pad=10)
    return _img(_fig_to_uri(fig), alt)


# ---------------------------------------------------------------------------
# Question helpers
# ---------------------------------------------------------------------------

def p(text: str) -> str:
    return f"<p>{text}</p>"


def q(domain, skill, body_html, prompt, options, answer, why, figure=""):
    assert len(options) == 4 and len(set(options)) == 4, (skill, options)
    assert answer in LETTERS
    return {
        "domain": domain,
        "skill": skill,
        "question": f"{figure}{body_html}{p(prompt)}",
        "options": options,
        "correct": options[LETTERS.index(answer)],
        "letter": answer,
        "answer_key": f"<p><strong>Correct Answer: {answer}</strong></p><p>{why}</p>",
    }


def notes(items, goal):
    lis = "".join(f"<li>{item}</li>" for item in items)
    return f"{p(P_NOTES)}<ul>{lis}</ul>{p(goal)}"


CS, II, SEC, EOI = (
    "Craft and Structure",
    "Information and Ideas",
    "Standard English Conventions",
    "Expression of Ideas",
)


# ---------------------------------------------------------------------------
# Module 1
# ---------------------------------------------------------------------------

def module_1():
    fig_pollinators = bar_chart(
        "Pollinator Visits to Sunflowers by Field Type",
        ["No special\nmargins", "Flower\nstrips", "Hedgerows", "Flower strips\nand hedgerows"],
        [4.2, 9.8, 7.1, 13.5],
        "Average visits per hour",
        16,
        "Bar graph of average pollinator visits per hour to sunflowers in four field types",
    )
    fig_seeds = table_image(
        "Germination Rates of Three Prairie Species at Three Soil Temperatures",
        ["Species", "10°C", "20°C", "30°C"],
        [
            ["Common yarrow", "22%", "78%", "64%"],
            ["Purple coneflower", "8%", "55%", "81%"],
            ["Blue grama", "3%", "41%", "88%"],
        ],
        "Table of germination rates for three prairie species at 10, 20 and 30 degrees Celsius",
        col_widths=[0.4, 0.2, 0.2, 0.2],
    )
    fig_turtles = line_chart(
        "Loggerhead Sea Turtle Nests Counted on Two Beaches, 2010–2022",
        [2010, 2012, 2014, 2016, 2018, 2020, 2022],
        [
            ("Beach A", [120, 115, 118, 160, 205, 240, 270]),
            ("Beach B", [130, 125, 121, 118, 112, 109, 104]),
        ],
        "Number of nests",
        (0, 300),
        "Line graph of loggerhead sea turtle nests on Beach A and Beach B from 2010 to 2022",
        note=(2014, "Restrictions begin\non Beach A"),
    )

    return [
        # ---- Craft and Structure -------------------------------------------
        q(CS, "Words in Context",
          p("Although the Atacama Desert receives almost no rainfall, its coastal hills are not "
            "entirely barren: fog drifting in from the Pacific Ocean provides enough moisture to "
            f"{BLANK} small communities of lichens and cacti that could not otherwise survive there."),
          P_WIC, ["sustain", "obscure", "relocate", "imitate"], "A",
          "The fog supplies the moisture that keeps the lichens and cacti alive, so it "
          "<em>sustains</em> them."),
        q(CS, "Words in Context",
          p("Critics who expected choreographer Lin Bao's new work to repeat the elaborate spectacle "
            f"of her earlier productions were surprised by its {BLANK}: the piece features a single "
            "dancer, a bare stage, and no music other than the sound of the performer's breathing."),
          P_WIC, ["extravagance", "familiarity", "austerity", "ambiguity"], "C",
          "One dancer, a bare stage and no music describe severe simplicity, or <em>austerity</em>, "
          "the opposite of the expected spectacle."),
        q(CS, "Words in Context",
          p("Historians long assumed that medieval European farmers rarely traveled beyond their own "
            f"villages, but recent analyses of market records have {BLANK} that view, showing that "
            "many farmers regularly journeyed dozens of kilometers to sell produce at regional fairs."),
          P_WIC, ["reinforced", "complicated", "anticipated", "popularized"], "B",
          "Evidence of regular long journeys runs against the old assumption, so the records have "
          "<em>complicated</em> it."),
        q(CS, "Words in Context",
          p(f"The novelist had grown accustomed to {BLANK} reviews: critics typically acknowledged "
            "her technical skill but rarely expressed real enthusiasm for her books. She was therefore "
            "surprised when her third novel, which she considered her least ambitious, was praised "
            "effusively."),
          P_WIC, ["scathing", "rapturous", "anonymous", "lukewarm"], "D",
          "Reviews that admit skill but lack enthusiasm are <em>lukewarm</em>; "
          "“scathing” is too harsh and “rapturous” contradicts the text."),
        q(CS, "Text Structure and Purpose",
          p("Many people assume that bees locate flowers primarily by sight. <u>Yet when researchers "
            "scented artificial flowers but painted them the same dull gray as the surrounding "
            "background, bumblebees still visited the scented flowers far more often than unscented "
            "ones.</u> Such findings suggest that, for bumblebees at least, odor can be as important "
            "a cue as color."),
          P_FUNCTION,
          [
            "It introduces a common assumption that the text goes on to defend.",
            "It describes a method that the researchers later rejected as unreliable.",
            "It summarizes a conclusion that the final sentence of the text calls into question.",
            "It presents an observation that challenges the assumption described in the previous sentence.",
          ], "D",
          "The experiment shows bees finding flowers without visual cues, which challenges the "
          "assumption that they rely mainly on sight."),
        q(CS, "Text Structure and Purpose",
          p("The following text is adapted from a short story. Teodora has just arrived at her "
            "grandmother's apartment for the first time in many years.")
          + p("The hallway smelled exactly as Teodora remembered: of floor wax, of oranges, of "
              "something sweet baking just out of sight. She had expected the place to seem smaller, "
              "the way childhood places are supposed to, but instead it seemed to have grown, as if "
              "the years she had been away had been quietly added to its rooms. On the wall hung the "
              "same faded photograph of the harbor, crooked by the same few degrees."),
          P_PURPOSE,
          [
            "To describe a character's impression that a familiar place is unchanged in some respects but seems different in others",
            "To explain why a character has avoided visiting a relative for many years",
            "To contrast a character's memories of a place with her grandmother's memories of it",
            "To show that a character is disappointed by the condition of an apartment she once admired",
          ], "A",
          "The smells and the crooked photograph are unchanged, while the apartment unexpectedly "
          "seems larger."),
        q(CS, "Cross-Text Connections",
          p("<strong>Text 1</strong>")
          + p("For decades, many linguists held that infants learn the sounds of their native language "
              "mainly by hearing speech directed at them. On this view, the slow, exaggerated "
              "“baby talk” that caregivers use is the primary source of the input infants need.")
          + p("<strong>Text 2</strong>")
          + p("Psycholinguist Amara Okafor and colleagues recorded the full daily sound environments of "
              "40 infants and found that speech directed at the infants made up less than a fifth of "
              "the language they heard. Yet infants in households with more overheard conversation "
              "—speech between adults—developed sound discrimination abilities faster than other "
              "infants did, even when the amount of speech directed at them was similar."),
          "Based on the texts, how would Okafor and colleagues (Text 2) most likely respond to the view "
          "described in Text 1?",
          [
            "By agreeing that infants need slow, exaggerated speech in order to learn any language sounds at all",
            "By arguing that the view overlooks the contribution that speech not directed at infants may make to their learning",
            "By suggesting that the view is correct for most infants but not for those who hear little adult conversation",
            "By claiming that caregivers rarely use slow, exaggerated speech when talking to infants",
          ], "B",
          "Text 2 finds that overheard adult conversation speeds learning, which the infant-directed "
          "view in Text 1 ignores."),
        # ---- Information and Ideas -----------------------------------------
        q(II, "Central Ideas and Details",
          p("Foresters have traditionally treated dead trees in managed forests as a fire hazard to be "
            "cleared away. But a growing body of research shows that standing dead trees, or snags, "
            "provide nesting cavities for woodpeckers and owls, while fallen logs retain moisture during "
            "droughts and gradually return nutrients to the soil as they decay. As a result, some forest "
            "agencies now require that a minimum number of snags and logs be left in place after a harvest."),
          P_MAIN_IDEA,
          [
            "Dead trees pose a greater fire risk in managed forests than foresters once believed.",
            "Woodpeckers and owls depend more heavily on dead trees than other forest animals do.",
            "Research on the ecological benefits of dead trees has led some forest managers to change their practices.",
            "Fallen logs are more beneficial to forests than standing dead trees are.",
          ], "C",
          "The text moves from the old view, to research on the benefits of dead trees, to the "
          "resulting change in policy."),
        q(II, "Central Ideas and Details",
          p("The following text is adapted from a short story.")
          + p("Mr. Halloran ran the town's only bookshop as if it were a lending library he resented. He "
              "would sell you a book, certainly, but only after asking what you intended to do with it, "
              "and if your answer displeased him, he might steer you toward something “more "
              "suitable” from a shelf near the back. Regular customers learned to name a book they "
              "did not want and then accept whatever he recommended instead—which, more often than "
              "not, turned out to be exactly what they had been looking for."),
          "According to the text, what is true about Mr. Halloran's regular customers?",
          [
            "They avoid the bookshop whenever possible because they dislike Mr. Halloran's questions.",
            "They prefer borrowing books from a library to buying them from Mr. Halloran.",
            "They frequently ask Mr. Halloran to order books that are not available in his shop.",
            "They have developed a strategy for dealing with Mr. Halloran that usually leads them to books they want.",
          ], "D",
          "They name a book they do not want, accept his recommendation, and usually get what they "
          "were looking for."),
        q(II, "Command of Evidence: Textual",
          p("Marine biologist Henrik Vaal hypothesizes that juvenile reef fish use the sounds produced "
            "by healthy coral reefs—such as the clicks of snapping shrimp and the grunts of adult "
            "fish—to locate suitable places to settle."),
          "Which finding, if true, would most directly support Vaal's hypothesis?",
          [
            "Juvenile reef fish settled near underwater speakers playing recordings of healthy reefs more often than near speakers playing no sound.",
            "Snapping shrimp produce louder clicks at night than they do during the day.",
            "Adult reef fish produce grunts primarily when defending their territories from rivals.",
            "Healthy coral reefs contain a greater variety of fish species than degraded reefs do.",
          ], "A",
          "Only choice A links reef sounds directly to where juvenile fish choose to settle."),
        q(II, "Command of Evidence: Quantitative",
          p("Agricultural scientist Priya Raman and colleagues studied how features at the edges of "
            "fields affect pollinators visiting sunflower crops. They counted visits by bees and other "
            "pollinators to sunflowers in fields with no special margins, fields bordered by strips of "
            "wildflowers, fields bordered by hedgerows, and fields with both features. Raman's team "
            f"concluded that combining the features was more effective than using either one alone: {BLANK}"),
          P_GRAPH,
          [
            "fields with flower strips averaged 9.8 visits per hour, compared with 4.2 visits per hour in fields with no special margins.",
            "fields with both features averaged 13.5 visits per hour, more than fields with only flower strips (9.8) or only hedgerows (7.1).",
            "fields with hedgerows averaged 7.1 visits per hour, fewer than fields with flower strips.",
            "fields with no special margins averaged the fewest visits per hour, at 4.2.",
          ], "B",
          "The claim compares the combination with each single feature; only B makes that comparison.",
          figure=fig_pollinators),
        q(II, "Command of Evidence: Quantitative",
          p("A student studying native plants for a prairie-restoration project grew seeds of three "
            "species at three soil temperatures and recorded the percentage of seeds that germinated. "
            "The student concluded that purple coneflower and blue grama are better suited to warm soil "
            f"than common yarrow is, since {BLANK}"),
          P_TABLE,
          [
            "at 20°C, common yarrow had a higher germination rate (78%) than either purple coneflower or blue grama did.",
            "blue grama had the lowest germination rate of the three species at 10°C (3%).",
            "at 30°C, both purple coneflower (81%) and blue grama (88%) had higher germination rates than common yarrow did (64%).",
            "purple coneflower's germination rate increased from 8% at 10°C to 55% at 20°C.",
          ], "C",
          "“Warm soil” points to the 30°C column, where both species beat yarrow.",
          figure=fig_seeds),
        q(II, "Command of Evidence: Quantitative",
          p("In 2014, authorities began restricting nighttime lighting and foot traffic on Beach A, a "
            "nesting site for loggerhead sea turtles, while nearby Beach B remained unregulated. A "
            "researcher claims that the restrictions contributed to an increase in nesting on Beach A."),
          "Which choice best describes data from the graph that support the researcher's claim?",
          [
            "In 2010, the number of nests on Beach B was higher than the number on Beach A.",
            "The number of nests on both beaches decreased between 2010 and 2014.",
            "The number of nests on Beach A in 2022 was more than twice the number on Beach B in 2010.",
            "After 2014, the number of nests on Beach A increased substantially, while the number on Beach B continued to decline slightly.",
          ], "D",
          "Nesting rose on the regulated beach after 2014 but not on the comparison beach, which "
          "supports a link to the restrictions.",
          figure=fig_turtles),
        q(II, "Inferences",
          p("In laboratory experiments, the freshwater crustacean <em>Daphnia</em> grows protective "
            "spines and helmet-like head extensions when it detects chemicals released by predatory "
            "fish. Producing these structures requires energy that would otherwise go toward "
            "reproduction, and <em>Daphnia</em> raised in water without predator chemicals do not "
            f"develop them. This suggests that {BLANK}"),
          P_INFER,
          [
            "the ability to develop protective structures only when predators are present allows <em>Daphnia</em> to avoid the costs of defense when it is unnecessary.",
            "<em>Daphnia</em> that develop protective structures reproduce more quickly than those that do not.",
            "predatory fish are unable to detect <em>Daphnia</em> that lack spines and head extensions.",
            "<em>Daphnia</em> raised in water containing predator chemicals eventually lose the ability to reproduce.",
          ], "A",
          "Defenses are costly and appear only when predators are detected, so the switch saves "
          "energy when no threat is present."),
        # ---- Standard English Conventions ----------------------------------
        q(SEC, "Form, Structure, and Sense",
          p("The collection of letters exchanged between the two astronomers, which were donated to the "
            f"university archive in 2019, {BLANK} new insight into how nineteenth-century scientists "
            "shared observations across great distances."),
          P_SEC, ["offer", "have offered", "offers", "are offering"], "C",
          "The subject is the singular noun “collection,” so the verb is “offers.”"),
        q(SEC, "Boundaries",
          p("The Andean condor is one of the heaviest flying birds in the "
            f"{BLANK} it rarely flaps its wings, relying instead on rising columns of warm air to stay "
            "aloft for hours."),
          P_SEC, ["world,", "world;", "world", "world, which"], "B",
          "Two independent clauses are joined, so a semicolon is needed."),
        q(SEC, "Boundaries",
          p(f"Architect {BLANK} designed the community center to stay cool without air conditioning by "
            "using thick earthen walls and a roof that channels breezes through the building."),
          P_SEC, ["Leila Haddad", "Leila, Haddad", "Leila Haddad,", ", Leila Haddad,"], "A",
          "A title directly before a name is not separated from it by commas, and no comma belongs "
          "between the subject and its verb."),
        q(SEC, "Form, Structure, and Sense",
          p("When the first transcontinental telegraph line in the United States was completed in "
            f"1861, it {BLANK} the time needed to send a message from one coast to the other from "
            "about ten days to a matter of minutes."),
          P_SEC, ["reduces", "will reduce", "has been reducing", "reduced"], "D",
          "The event is completed and placed in 1861, so the simple past “reduced” is needed."),
        q(SEC, "Form, Structure, and Sense",
          p("Sociologists studying neighborhood gardens have found that the gardens do more than supply "
            f"fresh produce: by giving residents a shared project, {BLANK} also strengthen social ties "
            "among people who might otherwise never interact."),
          P_SEC, ["it", "they", "this", "one"], "B",
          "The pronoun refers to the plural “gardens,” so “they” is correct."),
        q(SEC, "Boundaries",
          p("The museum's new exhibit focuses on three overlooked figures in the history of "
            f"{BLANK} a weaver who designed punched-card patterns, a mathematician who wrote early "
            "programs, and an engineer who built one of the first electronic memory systems."),
          P_SEC, ["computing:", "computing,", "computing;", "computing so"], "A",
          "A colon introduces the list that explains “three overlooked figures.”"),
        q(SEC, "Form, Structure, and Sense",
          p(f"Having spent nearly a decade observing chimpanzees in the wild, {BLANK}"),
          P_SEC,
          [
            "the primatologist's book describes tool use in remarkable detail.",
            "tool use is described in remarkable detail in the primatologist's book.",
            "the primatologist describes tool use in remarkable detail in a new book.",
            "remarkable detail about tool use is provided in the primatologist's book.",
          ], "C",
          "The person who spent a decade observing must come right after the modifying phrase."),
        # ---- Expression of Ideas -------------------------------------------
        q(EOI, "Transitions",
          p("Many comets follow vast, elongated orbits that take thousands of years to complete. "
            f"{BLANK} short-period comets complete an orbit in less than 200 years; Comet Encke, for "
            "instance, returns to the inner solar system about every 3.3 years."),
          P_TRANSITION, ["Similarly,", "By contrast,", "Therefore,", "For example,"], "B",
          "Short orbits are the opposite of thousand-year orbits, so a contrast is needed."),
        q(EOI, "Transitions",
          p("The Roman architect Vitruvius argued that buildings should possess three qualities: "
            "strength, usefulness, and beauty. Centuries later, his writings were rediscovered and "
            f"eagerly studied by Renaissance architects. {BLANK} his treatise became one of the most "
            "influential texts in the history of Western architecture."),
          P_TRANSITION, ["Instead,", "Nevertheless,", "As a result,", "Meanwhile,"], "C",
          "The treatise's influence follows from its rediscovery and study, a cause-and-effect relationship."),
        q(EOI, "Transitions",
          p("Some bioluminescent fungi glow continuously, a puzzling trait because producing light "
            "consumes energy. One hypothesis holds that the glow attracts insects that then spread the "
            f"fungi's spores. {BLANK} in one experiment, artificial mushrooms fitted with green lights "
            "attracted significantly more insects than unlit ones did."),
          P_TRANSITION, ["In support of this idea,", "Despite this,", "In other words,", "Even so,"], "A",
          "The experiment provides evidence for the hypothesis just stated."),
        q(EOI, "Rhetorical Synthesis",
          notes([
            "The Great Green Wall is an initiative launched by the African Union in 2007.",
            "Its goal is to restore degraded land across the Sahel region of Africa.",
            "The initiative originally aimed to plant a continuous line of trees across the continent.",
            "Over time, its focus shifted to a mosaic of land-management practices, such as restoring "
            "grasslands and supporting farmers' water-harvesting techniques.",
          ], "The student wants to explain how the Great Green Wall's approach has changed."),
          P_NOTES_Q,
          [
            "The Great Green Wall, launched in 2007, aims to restore degraded land in Africa's Sahel region.",
            "Initially focused on planting a continuous line of trees, the Great Green Wall now emphasizes a mosaic of land-management practices.",
            "Water-harvesting techniques are one of the land-management practices supported by the Great Green Wall.",
            "The African Union launched the Great Green Wall initiative in 2007.",
          ], "B",
          "Only B describes both the original approach and the current one."),
        q(EOI, "Rhetorical Synthesis",
          notes([
            "Mae Jemison earned a medical degree from Cornell University.",
            "She served as a Peace Corps medical officer in Sierra Leone and Liberia.",
            "In 1987, she was selected for NASA's astronaut program.",
            "In 1992, she flew aboard the space shuttle <em>Endeavour</em>, becoming the first African "
            "American woman to travel to space.",
          ], "The student wants to emphasize the historic significance of Jemison's 1992 mission."),
          P_NOTES_Q,
          [
            "Mae Jemison, who earned a medical degree from Cornell University, was selected for NASA's astronaut program in 1987.",
            "Before joining NASA, Mae Jemison served as a Peace Corps medical officer in Sierra Leone and Liberia.",
            "When Mae Jemison flew aboard the space shuttle <em>Endeavour</em> in 1992, she became the first African American woman to travel to space.",
            "Mae Jemison flew aboard the space shuttle <em>Endeavour</em>.",
          ], "C",
          "Only C states what made the 1992 flight historic."),
        q(EOI, "Rhetorical Synthesis",
          notes([
            "Reflecting telescopes use mirrors to gather and focus light.",
            "Refracting telescopes use lenses.",
            "A large lens can be supported only at its edges, so it can sag under its own weight and "
            "distort images.",
            "A mirror can be supported across its entire back surface.",
            "The largest refracting telescope built for regular research, at Yerkes Observatory, has a "
            "lens 102 centimeters (40 inches) in diameter.",
          ], "The student wants to explain why the largest telescopes are reflecting telescopes."),
          P_NOTES_Q,
          [
            "Reflecting telescopes use mirrors, whereas refracting telescopes use lenses.",
            "The refracting telescope at Yerkes Observatory has a lens 102 centimeters in diameter.",
            "Large lenses can sag under their own weight because they can be supported only at their edges.",
            "Because a mirror can be supported across its entire back surface while a large lens sags when held only at its edges, the largest telescopes use mirrors rather than lenses.",
          ], "D",
          "Only D gives the reason (support and sagging) and connects it to the conclusion."),
    ]


# ---------------------------------------------------------------------------
# Module 2 (harder)
# ---------------------------------------------------------------------------

def module_2():
    fig_wheat = grouped_bar_chart(
        "Average Yield of Three Wheat Varieties",
        ["Kestrel", "Marlow", "Sable"],
        [("Normal rainfall", [6.8, 6.1, 5.4]), ("Drought", [3.1, 4.2, 4.9])],
        "Yield (tonnes per hectare)",
        8,
        "Grouped bar graph of wheat yields for Kestrel, Marlow and Sable under normal rainfall and drought",
    )
    fig_song = line_chart(
        "Average Minimum Song Frequency of Great Tits, 1990–2020",
        [1990, 1995, 2000, 2005, 2010, 2015, 2020],
        [
            ("Urban sites", [3.90, 3.98, 4.07, 4.15, 4.22, 4.31, 4.38]),
            ("Forest sites", [3.88, 3.87, 3.90, 3.89, 3.88, 3.91, 3.90]),
        ],
        "Frequency (kilohertz)",
        (3.7, 4.5),
        "Line graph of average minimum song frequency of great tits at urban and forest sites from 1990 to 2020",
    )
    fig_noise = table_image(
        "Average Task Scores under Four Background Conditions",
        ["Background condition", "Reading\nscore (%)", "Arithmetic\nscore (%)"],
        [
            ["Silence", "82", "79"],
            ["Instrumental music", "80", "81"],
            ["Music with lyrics", "68", "78"],
            ["Background conversation", "64", "72"],
        ],
        "Table of average reading and arithmetic scores under four background conditions",
        col_widths=[0.5, 0.25, 0.25],
    )

    return [
        # ---- Craft and Structure -------------------------------------------
        q(CS, "Words in Context",
          p("Though the poet's later work is often described as radically experimental, a careful "
            f"reading reveals that it is {BLANK} the formal traditions she claimed to reject: her "
            "fragmented lines frequently conceal the meter and rhyme schemes of classical sonnets."),
          P_WIC, ["incompatible with", "suffused with", "unconcerned with", "contemporaneous with"], "B",
          "Hidden sonnet meter and rhyme mean the work is thoroughly permeated by tradition, or "
          "<em>suffused with</em> it."),
        q(CS, "Words in Context",
          p("Economist Tomás Ibarra argues that the popular image of the lone inventor is "
            f"{BLANK}: most major innovations, he contends, emerged from networks of collaborators whose "
            "contributions were later attributed to a single, celebrated individual."),
          P_WIC, ["inevitable", "ambitious", "apt", "misleading"], "D",
          "If the credit really belongs to networks, the lone-inventor image gives a false impression."),
        q(CS, "Words in Context",
          p(f"The archaeological team's initial conclusions about the settlement were necessarily {BLANK}: "
            "having excavated only a small fraction of the site, the researchers acknowledged that "
            "further digging could substantially revise their account of how its inhabitants lived."),
          P_WIC, ["provisional", "unanimous", "exhaustive", "derivative"], "A",
          "Conclusions that further digging could revise are temporary, or <em>provisional</em>."),
        q(CS, "Words in Context",
          p("Although the treaty was hailed at the time as a decisive diplomatic achievement, historians "
            f"have since noted that its provisions were so {BLANK} that each signatory could interpret "
            "them as supporting its own, often contradictory, territorial claims."),
          P_WIC, ["punitive", "stringent", "equivocal", "belated"], "C",
          "Language that supports contradictory readings is open to more than one interpretation: "
          "<em>equivocal</em>."),
        q(CS, "Text Structure and Purpose",
          p("Bird migration has often been described as a feat of instinct, with each species following "
            "a fixed, inherited route. Studies of the Eurasian blackcap complicate this picture. Since the "
            "1960s, a growing number of blackcaps breeding in central Europe have begun wintering in "
            "Britain rather than in Spain, a shift that became viable as backyard bird feeders grew "
            "common. <u>Remarkably, the offspring of these birds inherit the new direction: when raised "
            "in captivity, they orient toward Britain even without ever having made the journey.</u>"),
          P_FUNCTION,
          [
            "It provides evidence that a recently developed migratory behavior has become heritable.",
            "It explains why blackcaps were originally unable to survive winters in Britain.",
            "It suggests that captive-raised birds are unreliable subjects for migration research.",
            "It challenges the claim that blackcaps have changed their wintering grounds.",
          ], "A",
          "Captive-raised young that orient toward Britain show the new route is passed on genetically."),
        q(CS, "Text Structure and Purpose",
          p("The following text is adapted from a short story. Ines, a violinist, is preparing for an "
            "audition.")
          + p("For weeks Ines had practiced the concerto's opening until she could play it in her sleep, "
              "and some nights, she suspected, she did. Her teacher praised the precision of her "
              "fingering, the evenness of her bow. Then, at their last lesson, he asked her to play it "
              "once more, “but this time as if you had never heard it before.” Ines lifted the "
              "violin and found, to her dismay, that she did not know how."),
          P_STRUCTURE,
          [
            "It presents a teacher's criticism of a student and then shows the student rejecting that criticism.",
            "It recounts a character's early failures and then describes how she eventually overcame them.",
            "It contrasts a character's confidence before an audition with her nervousness during it.",
            "It describes a character's thorough preparation and then reveals a limitation that this preparation has created.",
          ], "D",
          "Endless repetition has made the piece so familiar that Ines can no longer play it as if "
          "it were new."),
        q(CS, "Cross-Text Connections",
          p("<strong>Text 1</strong>")
          + p("Many economists argue that minimum wage increases inevitably reduce employment, since "
              "employers faced with higher labor costs will hire fewer workers. Studies that find no job "
              "losses after modest increases, these economists contend, simply fail to capture effects "
              "that emerge over longer periods.")
          + p("<strong>Text 2</strong>")
          + p("Labor economist Ruth Adeyemi notes that in markets where a few large employers dominate "
              "hiring, those employers can hold wages below the value of what workers produce. In such "
              "markets, Adeyemi argues, a moderate minimum wage increase can actually raise employment "
              "by drawing more people into jobs that now pay enough to make working worthwhile."),
          "Based on the texts, how would Adeyemi (Text 2) most likely respond to the economists' argument "
          "in Text 1?",
          [
            "She would agree that minimum wage increases reduce employment but argue that the reductions are smaller than the economists claim.",
            "She would contend that their reasoning assumes market conditions that do not hold in every labor market.",
            "She would argue that the studies they criticize examined periods too long to detect employment effects.",
            "She would claim that large employers typically pay wages above the value of what workers produce.",
          ], "B",
          "Adeyemi identifies markets dominated by a few employers, where the “inevitable” "
          "job losses in Text 1 need not occur."),
        # ---- Information and Ideas -----------------------------------------
        q(II, "Central Ideas and Details",
          p("Chemist Saeko Mori and colleagues have developed a coating that allows glass to repair "
            "small scratches on its own. The coating contains microscopic capsules filled with a liquid "
            "polymer; when a scratch ruptures the capsules, the polymer flows into the gap and hardens "
            "on exposure to air. Although the coating restored the transparency of scratched samples in "
            "laboratory tests, the team notes that each region of the coating can heal only once, since "
            "the capsules there are emptied in the process, and that the coating has not yet been "
            "tested under the temperature swings that windows and screens routinely experience."),
          P_MAIN_IDEA,
          [
            "Mori's team has developed a self-healing coating for glass that shows promise, though it has limitations that may affect its practical use.",
            "Self-healing coatings for glass are unlikely to be used commercially because they cannot withstand changes in temperature.",
            "Liquid polymers are more effective than other materials at restoring the transparency of scratched glass.",
            "Mori's team has determined that the coating can repair the same scratch repeatedly as long as it is exposed to air.",
          ], "A",
          "The text presents a successful test and two acknowledged limitations; B overstates an "
          "untested concern and D contradicts the text."),
        q(II, "Central Ideas and Details",
          p("The following text is adapted from a novel. Arthur has worked as a clockmaker for decades.")
          + p("Arthur no longer looked at the clocks when he repaired them; he listened. A healthy "
              "movement had a rhythm as distinctive as a voice, and he could tell from the faintest "
              "hesitation in its beat that a pivot had worn or a spring had weakened. Customers "
              "sometimes found this unsettling, watching him sit with his eyes half closed and a pocket "
              "watch held to his ear, as though the thing were confiding in him."),
          "Based on the text, what is true about Arthur?",
          [
            "He can no longer see well enough to repair clocks by sight.",
            "He prefers repairing pocket watches to repairing other kinds of clocks.",
            "His long experience has given him the ability to diagnose problems in clocks by sound.",
            "His customers distrust his skills and often take their clocks elsewhere.",
          ], "C",
          "He identifies worn pivots and weak springs from the rhythm of the beat."),
        q(II, "Command of Evidence: Textual",
          p("Some languages require speakers to mark grammatically how they know what they are reporting "
            "—for example, whether they witnessed an event themselves or heard about it from "
            "someone else. Linguist Esra Demir hypothesizes that speakers of such languages pay closer "
            "attention to the sources of their information than speakers of languages without this "
            "requirement do."),
          "Which finding, if true, would most directly support Demir's hypothesis?",
          [
            "Speakers of languages with required source marking recalled whether they had seen or been told about events more accurately than other speakers did, though both groups recalled the events themselves equally well.",
            "Speakers of languages with required source marking produced longer descriptions of events than speakers of other languages did.",
            "Children learning languages with required source marking begin using the markers later than they begin using other grammatical forms.",
            "Some languages without required source marking have optional words, such as “apparently,” that indicate where information came from.",
          ], "A",
          "A isolates memory for information sources (not memory in general) as the difference between groups."),
        q(II, "Command of Evidence: Quantitative",
          p("Plant breeder Amina Diallo tested three wheat varieties in fields that received normal "
            "rainfall and in fields subjected to drought. Diallo argues that farmers in regions where "
            "droughts are becoming more frequent should consider planting Sable, even though it is not "
            f"the highest-yielding variety under normal conditions, because {BLANK}"),
          P_GRAPH,
          [
            "Kestrel produced the highest yield of the three varieties under normal rainfall, at 6.8 tonnes per hectare.",
            "Sable produced the lowest yield of the three varieties under normal rainfall.",
            "Marlow's yield under drought was 4.2 tonnes per hectare, higher than Kestrel's.",
            "under drought, Sable's yield fell only to 4.9 tonnes per hectare, the highest of the three varieties in those conditions.",
          ], "D",
          "The argument concerns drought performance; D shows Sable has the smallest drop and the "
          "highest drought yield.",
          figure=fig_wheat),
        q(II, "Command of Evidence: Quantitative",
          p("Researchers have proposed that birds in cities sing at higher pitches so that their songs "
            "are not masked by low-frequency traffic noise. A team led by ornithologist Jonas Pettersson "
            "tracked the average minimum frequency of great tit songs at urban and forest sites over "
            "three decades, during which traffic at the urban sites increased steadily. The team claims "
            "that its data are consistent with the proposal."),
          "Which choice best describes data from the graph that support the team's claim?",
          [
            "In 1990, the average minimum song frequency was nearly the same at urban and forest sites.",
            "From 1990 to 2020, the average minimum song frequency rose steadily at urban sites, while at forest sites it stayed close to 3.9 kilohertz.",
            "The average minimum song frequency at forest sites was lower in 1995 than in 1990.",
            "The average minimum song frequency at urban sites in 2020 was higher than the frequency at forest sites in 1990.",
          ], "B",
          "Pitch rose only where traffic grew, while the quieter forest sites stayed flat.",
          figure=fig_song),
        q(II, "Command of Evidence: Quantitative",
          p("Psychologist Nadia Kovac hypothesized that background sounds containing understandable words "
            "interfere more with reading than with arithmetic, because reading and processing speech draw "
            "on the same verbal resources. She measured participants' performance on reading and "
            f"arithmetic tasks under four background conditions. The data support her hypothesis, since {BLANK}"),
          P_TABLE,
          [
            "arithmetic scores were higher with instrumental music (81%) than in silence (79%).",
            "arithmetic scores were lower with background conversation (72%) than in any other condition.",
            "compared with silence, reading scores fell by 14 or more percentage points in the two conditions that included words, whereas arithmetic scores fell by no more than 7 points.",
            "in silence, reading scores (82%) were higher than arithmetic scores (79%).",
          ], "C",
          "The hypothesis compares the effect of words on reading with their effect on arithmetic; "
          "only C makes that comparison.",
          figure=fig_noise),
        q(II, "Inferences",
          p("Fig trees and the wasps that pollinate them are known for an exclusive relationship: each "
            "fig species is typically pollinated by a single wasp species, and each wasp species can "
            "reproduce only inside the figs of its partner tree. However, genetic studies have revealed "
            "that in some regions two or more wasp species share a single fig species, and that some "
            "wasps occasionally pollinate figs of a species other than their usual partner. Because "
            f"hybrid fig trees can result from such cross-pollination, these findings suggest that {BLANK}"),
          P_INFER,
          [
            "fig trees would be unable to reproduce without the help of more than one wasp species.",
            "wasps that pollinate multiple fig species produce more offspring than wasps that pollinate a single species.",
            "hybrid fig trees are unable to attract any wasp pollinators.",
            "the strict pairing of single fig and wasp species may be less universal than previously thought and could contribute to the emergence of new fig lineages.",
          ], "D",
          "Shared and cross-species pollination contradict a strict one-to-one rule, and hybrids could "
          "give rise to new lineages."),
        # ---- Standard English Conventions ----------------------------------
        q(SEC, "Form, Structure, and Sense",
          p(f"In the late 1870s, {BLANK} observations of Mars led some astronomers to believe that the "
            "planet's surface was crisscrossed by artificial canals."),
          P_SEC,
          [
            "astronomer Giovanni Schiaparellis'",
            "astronomer Giovanni Schiaparelli's",
            "astronomer, Giovanni Schiaparelli's,",
            "astronomer Giovanni Schiaparellis",
          ], "B",
          "The singular possessive of “Schiaparelli” is “Schiaparelli's,” with no "
          "commas after the title."),
        q(SEC, "Boundaries",
          p("The Svalbard Global Seed Vault—a facility built deep inside a mountain on a remote "
            f"Norwegian {BLANK} holds more than one million seed samples from around the world."),
          P_SEC, ["island,", "island;", "island—", "island"], "C",
          "The supplementary phrase opened with a dash must be closed with a dash."),
        q(SEC, "Form, Structure, and Sense",
          p(f"Among the most surprising discoveries at the cave {BLANK} a set of bone flutes that "
            "researchers estimate to be more than 35,000 years old."),
          P_SEC, ["was", "were", "have been", "are"], "A",
          "In this inverted sentence the subject is the singular “a set,” so the verb is "
          "“was.”"),
        q(SEC, "Boundaries",
          p("The novelist drafted each of her books by hand, often filling dozens of "
            f"{BLANK} only after completing a full draft did she type the manuscript and begin revising."),
          P_SEC, ["notebooks,", "notebooks", "notebooks;", "notebooks and"], "C",
          "Two independent clauses need a semicolon; a comma alone creates a comma splice."),
        q(SEC, "Form, Structure, and Sense",
          p("In 1928, while sorting through culture plates in his London laboratory, Alexander Fleming "
            f"{BLANK} that a mold growing on one plate had killed the bacteria surrounding it."),
          P_SEC, ["noticing", "to notice", "having noticed", "noticed"], "D",
          "The sentence needs a main verb in the past tense: “noticed.”"),
        q(SEC, "Boundaries",
          p("Early photographers needed their subjects to remain still for several minutes during "
            f"exposures. By the 1850s, {BLANK} improved chemical processes had reduced exposure times "
            "to a few seconds."),
          P_SEC, ["however", "however,", "however;", "however:"], "B",
          "“However” interrupts the clause here, so it is set off by commas on both sides."),
        q(SEC, "Form, Structure, and Sense",
          p("The wingspan of the wandering albatross can exceed three meters, which is greater than "
            f"{BLANK}"),
          P_SEC,
          [
            "that of any other living bird.",
            "any other living bird.",
            "any other living bird's wingspans.",
            "those of any other living bird.",
          ], "A",
          "A wingspan must be compared with a wingspan; the singular “that of” does this."),
        # ---- Expression of Ideas -------------------------------------------
        q(EOI, "Transitions",
          p("For much of the twentieth century, scientists assumed that the adult human brain could not "
            f"generate new neurons. {BLANK} studies beginning in the 1990s found evidence that new neurons "
            "form in the hippocampus, a region involved in memory."),
          P_TRANSITION, ["Consequently,", "Similarly,", "However,", "For instance,"], "C",
          "The new findings contradict the earlier assumption."),
        q(EOI, "Transitions",
          p("Researchers have long hoped to produce spider silk, which is remarkably strong and elastic, "
            "on an industrial scale. Farming spiders the way silkworms are farmed has proven impractical, "
            "however: many species are territorial and will attack one another when housed together. "
            f"{BLANK} researchers have turned to genetically modified organisms, such as bacteria and "
            "silkworms, that can produce spider silk proteins."),
          P_TRANSITION, ["Instead,", "Likewise,", "Nonetheless,", "In comparison,"], "A",
          "Modified organisms replace the impractical option of farming spiders."),
        q(EOI, "Transitions",
          p("The Voyager 1 spacecraft, launched in 1977, was designed primarily to study Jupiter and "
            f"Saturn during a mission expected to last about five years. {BLANK} it far outlived that "
            "mission: in 2012, it became the first human-made object to enter interstellar space."),
          P_TRANSITION, ["Therefore,", "However,", "For example,", "Similarly,"], "B",
          "Outliving a five-year plan by decades runs against what was expected."),
        q(EOI, "Rhetorical Synthesis",
          notes([
            "The Rosetta Stone was discovered in 1799 near the town of Rashid (Rosetta), Egypt.",
            "It contains the same decree written in three scripts: Egyptian hieroglyphs, Demotic, and "
            "ancient Greek.",
            "Scholars at the time could already read ancient Greek.",
            "By comparing the Greek text with the hieroglyphs, Jean-François Champollion announced "
            "a breakthrough in deciphering hieroglyphs in 1822.",
          ], "The student wants to explain why the Rosetta Stone was useful for deciphering hieroglyphs."),
          P_NOTES_Q,
          [
            "Discovered in 1799, the Rosetta Stone contains a decree written in three scripts.",
            "Because the Rosetta Stone presents the same decree in hieroglyphs and in ancient Greek, which scholars could already read, it allowed them to use the Greek text to decipher the hieroglyphs.",
            "Jean-François Champollion announced a breakthrough in deciphering hieroglyphs in 1822.",
            "The Rosetta Stone was found near Rashid, Egypt, and contains text in Egyptian hieroglyphs, Demotic, and ancient Greek.",
          ], "B",
          "Only B explains the reason: a known script beside an unknown one with the same content."),
        q(EOI, "Rhetorical Synthesis",
          notes([
            "Tardigrades are microscopic animals known for surviving extreme conditions.",
            "When their surroundings dry out, tardigrades lose most of their body water and enter a "
            "dormant state called cryptobiosis.",
            "In cryptobiosis, a tardigrade's metabolism drops to less than 0.01% of its normal rate.",
            "Wood frogs survive the winter by allowing up to about two-thirds of their body water to freeze.",
          ], "The student wants to emphasize a difference between how tardigrades and wood frogs survive "
             "harsh conditions."),
          P_NOTES_Q,
          [
            "Tardigrades and wood frogs can both survive conditions that would kill many other animals.",
            "Tardigrades are microscopic animals, and wood frogs survive the winter by allowing some of their body water to freeze.",
            "Whereas tardigrades survive drying out by losing most of their body water, wood frogs survive winter by allowing much of their body water to freeze.",
            "In cryptobiosis, a tardigrade's metabolism drops to less than 0.01% of its normal rate.",
          ], "C",
          "Only C uses a contrast (“whereas”) between the two survival strategies."),
        q(EOI, "Rhetorical Synthesis",
          notes([
            "Retrieval practice means trying to recall material from memory rather than simply rereading it.",
            "In one well-known study, students read a passage and then either reread it or took a recall "
            "test on it.",
            "When tested five minutes later, the students who reread the passage remembered slightly more.",
            "When tested one week later, the students who took the recall test remembered substantially more.",
          ], "The student wants to present the study's findings to an audience unfamiliar with retrieval "
             "practice, emphasizing its long-term benefit."),
          P_NOTES_Q,
          [
            "Retrieval practice has been examined by researchers in a well-known study.",
            "Students who reread a passage remembered slightly more when they were tested five minutes later.",
            "In one study, students who reread a passage and students who took a recall test on it were tested at two different times.",
            "Retrieval practice—trying to recall material rather than simply rereading it—may not help much in the short term, but in one study it helped students remember substantially more a week later.",
          ], "D",
          "Only D defines the term for a new audience and highlights the one-week result."),
    ]


def build() -> dict:
    m1, m2 = module_1(), module_2()
    assert len(m1) == 27 and len(m2) == 27
    for name, module in (("Module 1", m1), ("Module 2", m2)):
        letters = Counter(item["letter"] for item in module)
        assert max(letters.values()) - min(letters.values()) <= 1, (name, letters)
        domains = Counter(item["domain"] for item in module)
        assert domains == {CS: 7, II: 7, SEC: 7, EOI: 6}, (name, domains)

    questions = []
    for number, item in enumerate(m1 + m2, start=1):
        questions.append({
            "id": number,
            "module": 1 if number <= 27 else 2,
            "domain": item["domain"],
            "skill": item["skill"],
            "question": item["question"],
            "options": item["options"],
            "correct": item["correct"],
            "answer_key": item["answer_key"],
        })

    return {
        "title": "Academor SAT Practice Test 1 Reading and Writing",
        "category_name": "SAT Reading and Writing",
        "service": "sat-verbal",
        "is_sat": True,
        "sat_section": "reading",
        "time_limit_minutes": 64,
        "questions": questions,
    }


def main():
    data = build()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    with_img = sum(1 for item in data["questions"] if "<img" in item["question"])
    print(f"OK {OUT_FILE.relative_to(REPO)}: {len(data['questions'])} questions, {with_img} with data graphics, "
          f"{OUT_FILE.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
