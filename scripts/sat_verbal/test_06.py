"""Academor SAT Practice Test 6 — Reading and Writing."""

from sat_verbal.common import (
    BND, CID, COEQ, COET, CTC, FSS, INF, P_FINDING, P_FUNCTION, P_GRAPH, P_INFER, P_MAIN_IDEA,
    P_NOTES_Q, P_PURPOSE, P_SEC, P_STRUCTURE, P_TABLE, P_TRANSITION, P_WEAKEN, P_WIC, Q, RS, TRN, TSP,
    WIC, bar_chart, blank, grouped_bar_chart, line_chart, notes, p, table_image, texts, underline,
)


def module_1():
    fig_pests = bar_chart(
        "Tomatoes Damaged by Insects Under Four Treatments",
        ["No\ntreatment", "Marigolds\nplanted nearby", "Insect\nnetting", "Marigolds\nand netting"],
        [38, 27, 14, 9],
        "Damaged tomatoes (%)", 45,
        "Bar graph of the percentage of damaged tomatoes: no treatment 38%, marigolds 27%, netting 14%, marigolds and "
        "netting 9%",
        value_fmt="{:.0f}%",
    )
    fig_temps = line_chart(
        "Average Monthly High Temperature in Two Cities",
        [1, 3, 5, 7, 9, 11],
        [("Port Alder (coastal)", [9, 11, 15, 19, 17, 11]), ("Fenwick (inland)", [1, 8, 19, 29, 21, 6])],
        "Temperature (°C)", (0, 32),
        "Line graph of monthly high temperatures: the coastal city ranges from 9 to 19 degrees and the inland city "
        "from 1 to 29 degrees",
        xlabel="Month (1 = January)",
    )
    fig_votes = table_image(
        "Ballots Cast by Method in Dunmore County Elections",
        ["Election", "In person", "By mail"],
        [["2014", "41,200", "6,300"], ["2018", "38,900", "12,800"], ["2022", "35,400", "24,100"]],
        "Table of ballots cast in person and by mail in three elections",
        col_widths=[0.3, 0.35, 0.35],
    )
    return [
        Q(WIC,
          blank("The town's water supply is ___: during dry summers, the reservoir falls so low that residents are "
                "required to limit how much water they use."),
          P_WIC, "precarious", ["abundant", "inexpensive", "historic"],
          "A supply that runs dangerously low in dry summers is <em>precarious</em>."),
        Q(WIC,
          blank("His apology seemed ___: he repeated it word for word to each person and never mentioned what he had "
                "actually done wrong."),
          P_WIC, "perfunctory", ["heartfelt", "elaborate", "spontaneous"],
          "A mechanical, word-for-word apology that avoids the actual wrong is <em>perfunctory</em>."),
        Q(WIC,
          blank("By examining the design of its anchor and the coins found in its hold, researchers were able to ___ "
                "when the ship had sunk."),
          P_WIC, "ascertain", ["conceal", "exaggerate", "dispute"],
          "Using evidence to find out when the ship sank is to <em>ascertain</em> it."),
        Q(WIC,
          blank("The documentary takes a ___ view of the inventor, celebrating his achievements while also examining "
                "the harsh conditions in the factories he owned."),
          P_WIC, "nuanced", ["flattering", "dismissive", "superficial"],
          "Showing both achievements and faults is a <em>nuanced</em> view; “flattering” and “dismissive” are "
          "one-sided."),
        Q(TSP,
          underline("A dandelion seed is carried through the air by a tuft of about 100 thin bristles. Scientists long "
                    "assumed that the tuft worked like a small parachute, simply catching the wind. ",
                    "In 2018, however, researchers showed that air flowing through the gaps between the bristles forms "
                    "a stable ring of swirling air just above the tuft, which helps keep the seed aloft.",
                    " The finding has since inspired engineers who design very small flying devices."),
          P_FUNCTION,
          "It presents a finding that revises the assumption described in the previous sentence.",
          ["It explains why dandelions produce so many seeds.",
           "It describes an experiment that confirmed the parachute assumption.",
           "It introduces a problem that engineers have not yet solved."],
          "The 2018 discovery of the swirling air ring changes the simple parachute view."),
        Q(TSP,
          p("The following text is from a short story. Noor, a violinist, is listening to a recording of her first "
            "concert.")
          + p("She had remembered the concert as a disaster. Her bow had trembled in the slow movement; she had rushed "
              "the final page. But the recording told a different story. The trembling was barely audible, and the "
              "rushing sounded like excitement rather than fear. Noor played the last minute twice, then a third "
              "time, and found herself wondering what else she had been too frightened to hear correctly."),
          P_PURPOSE,
          "To show a character discovering that her memory of a performance was harsher than the performance itself",
          ["To explain why a character stopped playing the violin after her first concert",
           "To describe how a character learned to make recordings of her concerts",
           "To contrast a character's skill with that of the other musicians in her concert"],
          "Noor remembered a disaster, but the recording reveals a much better performance."),
        Q(CTC,
          texts("Most scientists agree that an asteroid struck Earth about 66 million years ago, near what is now the "
                "Yucatán Peninsula. Many describe this impact as the single cause of the mass extinction that ended "
                "the age of dinosaurs.",
                "Geologist Amelia Ward argues that the asteroid was only part of the story. Huge volcanic eruptions in "
                "what is now India, known as the Deccan Traps, released large amounts of gas over hundreds of thousands "
                "of years before and after the impact. Ward suggests that these eruptions may have already weakened "
                "many ecosystems by the time the asteroid struck."),
          "Based on the texts, how would Ward (Text 2) most likely respond to the view described in Text 1?",
          "By arguing that it is incomplete because volcanic eruptions may also have contributed to the extinction",
          ["By rejecting the idea that an asteroid struck Earth 66 million years ago",
           "By agreeing that the asteroid impact was the only cause of the extinction",
           "By claiming that the Deccan Traps eruptions began after the dinosaurs had died out"],
          "Ward accepts the impact but adds the eruptions as an earlier, contributing cause."),
        Q(CID,
          p("For centuries, Polynesian navigators crossed thousands of kilometers of open ocean without compasses or "
            "maps. They steered by the rising and setting points of stars, read the direction of ocean swells, and "
            "watched for birds that fly out to sea and return to land at night. In 1976 the voyaging canoe "
            "<em>Hōkūleʻa</em> sailed from Hawaii to Tahiti using only these traditional methods, showing that such "
            "long voyages were possible."),
          P_MAIN_IDEA,
          "Polynesian navigators used natural signs to cross vast stretches of ocean, and a modern voyage confirmed "
          "that their methods worked.",
          ["Polynesian navigators relied mainly on maps drawn by earlier sailors.",
           "The <em>Hōkūleʻa</em> used modern instruments to sail from Hawaii to Tahiti.",
           "Birds that fly out to sea were the only sign Polynesian navigators used."],
          "The text describes the traditional methods and the 1976 voyage that proved them."),
        Q(CID,
          p("The following text is from a short story. Daniel, who grew up in a city, is spending the summer at his "
            "aunt's farm.")
          + p("His aunt handed him the bucket and pointed at the goat. Daniel had seen it done in videos; how hard "
              "could it be? Ten minutes later, the bucket was empty, his shoes were wet, and the goat was chewing his "
              "sleeve with great interest. His aunt, leaning on the gate, did not offer to help. “Tomorrow,” she said, "
              "“you'll do better.” To his surprise, Daniel found he was looking forward to it."),
          P_MAIN_IDEA,
          "Despite failing at a new task, Daniel becomes eager to try it again.",
          ["Daniel decides that farm work is too difficult for him.",
           "Daniel's aunt is angry that he wasted the milk.",
           "Daniel has milked goats many times before coming to the farm."],
          "After an amusing failure, Daniel finds himself looking forward to trying again."),
        Q(COET,
          p("Marine biologist Sung-min Park claims that noise from passing ships makes some reef fish less able to "
            "notice approaching predators."),
          P_FINDING,
          "When recordings of ship engines were played, the fish took much longer to flee from a model predator than "
          "they did when recordings of natural reef sounds were played.",
          ["Reef fish were more common near islands with fewer ships.",
           "Ship engines produce sounds at many different pitches.",
           "Some reef fish make sounds to communicate with one another."],
          "Slower escape responses during ship noise directly support the claim."),
        Q(COEQ,
          p("A gardener tested ways to protect tomatoes from insects. She concluded that netting was more effective "
            "than planting marigolds, though combining the two worked best: ___"),
          P_GRAPH,
          "14% of tomatoes protected by netting were damaged, compared with 27% of those near marigolds and 9% of "
          "those with both.",
          ["38% of tomatoes with no treatment were damaged.",
           "27% of tomatoes near marigolds were damaged, compared with 38% of tomatoes with no treatment.",
           "9% of tomatoes protected by netting were damaged, compared with 14% of those with both."],
          "Only this choice compares netting with marigolds and shows the combination doing best.",
          figure=fig_pests),
        Q(COEQ,
          p("Coastal cities often have milder seasons than inland cities, because the ocean warms and cools more slowly "
            "than land does. For example, the average monthly high temperature in ___"),
          P_GRAPH,
          "Port Alder ranges from about 9°C to about 19°C, while in Fenwick it ranges from about 1°C to about 29°C.",
          ["Fenwick is about 29°C in July.",
           "Port Alder is higher than in Fenwick in every month shown.",
           "Port Alder and Fenwick is about the same in May."],
          "Only this choice compares the ranges, showing the coastal city's milder seasons.",
          figure=fig_temps),
        Q(COEQ,
          p("A county official notes that voting by mail became much more common in Dunmore County between 2014 and "
            "2022, even as the number of people voting in person declined: ___"),
          P_TABLE,
          "mail ballots rose from 6,300 to 24,100, while in-person ballots fell from 41,200 to 35,400.",
          ["in-person ballots rose from 35,400 to 41,200.",
           "mail ballots were higher than in-person ballots in 2022.",
           "in 2018, 38,900 ballots were cast in person."],
          "Only this choice shows both trends described by the official.",
          figure=fig_votes),
        Q(INF,
          p("After two strong hurricanes struck a group of Caribbean islands, biologist Clara Méndez compared lizards "
            "measured just before the storms with lizards that survived them. On average, the survivors had larger toe "
            "pads, which help lizards grip surfaces, than the lizards measured before the storms. These findings "
            "suggest that ___"),
          P_INFER,
          "lizards that could cling more tightly to branches may have been more likely to survive the hurricanes.",
          ["the hurricanes caused the lizards' toe pads to grow larger.",
           "lizards with small toe pads left the islands before the storms.",
           "larger toe pads make lizards faster runners on the ground."],
          "Survivors having larger gripping pads suggests that better grip improved survival."),
        Q(FSS,
          blank("There ___ several reasons why the bridge was closed, including cracks in its supports and a damaged "
                "railing."),
          P_SEC, "were", ["was", "is", "has been"],
          "The subject “several reasons” is plural and the closing happened in the past, so <em>were</em> fits."),
        Q(BND,
          blank("The comet—visible from Earth only once every 76 ___ appear again in 2061."),
          P_SEC, "years—will", ["years, will", "years will", "years; will"],
          "An interruption that begins with a dash must end with a dash."),
        Q(FSS,
          blank("The author, ___ first novel was rejected by eleven publishers, later won several major prizes."),
          P_SEC, "whose", ["who's", "who", "whom"],
          "The possessive relative pronoun <em>whose</em> shows that the novel belonged to the author."),
        Q(BND,
          blank("The garden's most popular feature is a maze made of ___ hedges that are trimmed by hand twice a year."),
          P_SEC, "yew", ["yew,", "yew;", "yew:"],
          "No punctuation belongs between the noun “yew” and the noun it describes, “hedges.”"),
        Q(FSS,
          blank("Last spring the students planted a garden behind the school, and by June they ___ enough vegetables to "
                "donate to a local food bank."),
          P_SEC, "had grown", ["grow", "will grow", "are growing"],
          "The growing was completed by a past time (June), so <em>had grown</em> is needed."),
        Q(BND,
          blank("Ella Fitzgerald recorded more than 200 albums during her ___ she became known as the “First Lady of "
                "Song.”"),
          P_SEC, "career, and", ["career,", "career and,", "career and"],
          "Two independent clauses joined by “and” need a comma before the conjunction."),
        Q(FSS,
          blank("Unlike the city's older buildings, ___"),
          P_SEC,
          "the new library uses solar panels to produce most of its electricity.",
          ["solar panels produce most of the new library's electricity.",
           "most of the electricity for the new library comes from solar panels.",
           "the electricity of the new library comes mostly from solar panels."],
          "Buildings must be compared with a building: “the new library” must follow the opening phrase."),
        Q(TRN,
          blank("Many people believe that goldfish have a memory span of only a few seconds. ___ experiments have shown "
                "that goldfish can remember how to find food in a maze for months."),
          P_TRANSITION, "In reality,", ["Similarly,", "For example,", "As a result,"],
          "The experiments correct the popular belief."),
        Q(TRN,
          blank("The architect wanted the building to use as little energy as possible. ___ she oriented its windows to "
                "capture winter sunlight and added thick insulation to its walls."),
          P_TRANSITION, "To that end,", ["However,", "In contrast,", "Even so,"],
          "The windows and insulation serve the goal of using little energy."),
        Q(TRN,
          blank("The first part of the hike follows a wide, flat path along the river. ___ the trail becomes narrow and "
                "steep as it climbs toward the waterfall."),
          P_TRANSITION, "Later,", ["Therefore,", "For instance,", "Similarly,"],
          "The sentence describes the next part of the hike in time order."),
        Q(RS,
          notes(["The Burj Khalifa in Dubai is about 828 meters tall.",
                 "It was completed in 2010.",
                 "The Eiffel Tower in Paris is about 330 meters tall.",
                 "The Eiffel Tower was completed in 1889."],
                "The student wants to compare the heights of the two structures."),
          P_NOTES_Q,
          "At about 828 meters, the Burj Khalifa is more than twice as tall as the Eiffel Tower, which is about 330 "
          "meters tall.",
          ["The Burj Khalifa was completed in 2010, and the Eiffel Tower was completed in 1889.",
           "The Burj Khalifa in Dubai is about 828 meters tall.",
           "The Eiffel Tower, completed in 1889, is in Paris."],
          "Only this choice compares the two heights."),
        Q(RS,
          notes(["Mushrooms are the fruiting bodies of fungi.",
                 "Most of a fungus grows underground as a network of thin threads called mycelium.",
                 "One honey fungus in Oregon covers an area of nearly 10 square kilometers.",
                 "Scientists estimate that this fungus is thousands of years old."],
                "The student wants to emphasize that the visible part of a fungus is only a small part of it."),
          P_NOTES_Q,
          "A mushroom is only the fruiting body of a fungus; most of the fungus grows underground as a network of "
          "threads.",
          ["One honey fungus in Oregon covers nearly 10 square kilometers.",
           "Scientists estimate that a honey fungus in Oregon is thousands of years old.",
           "Mushrooms are the fruiting bodies of fungi."],
          "Only this choice contrasts the visible mushroom with the hidden network."),
        Q(RS,
          notes(["Jesse Owens was an American track and field athlete.",
                 "At the 1936 Olympic Games in Berlin, he won four gold medals.",
                 "He won the 100 meters, the 200 meters, the long jump, and the 4 × 100 meter relay.",
                 "His achievement challenged the Nazi government's claims of racial superiority."],
                "The student wants to emphasize the significance of Owens's victories beyond sports."),
          P_NOTES_Q,
          "By winning four gold medals at the 1936 Berlin Olympics, Jesse Owens challenged the Nazi government's "
          "claims of racial superiority.",
          ["Jesse Owens won the 100 meters, the 200 meters, the long jump, and the relay.",
           "Jesse Owens was an American track and field athlete.",
           "At the 1936 Olympic Games, Jesse Owens won four gold medals."],
          "Only this choice explains the significance beyond sports."),
    ]


def module_2():
    fig_phones = grouped_bar_chart(
        "Students Reporting Good Concentration in Class",
        ["School A", "School B", "School C"],
        [("Before phone ban", [48, 52, 45]), ("After phone ban", [63, 54, 61])],
        "Percentage of students", 70,
        "Grouped bar graph of the share of students reporting good concentration before and after a phone ban at three "
        "schools",
    )
    fig_salmon = line_chart(
        "Salmon Returning to Spawn in the Ely River",
        [2008, 2010, 2012, 2014, 2016, 2018, 2020],
        [("Salmon counted", [900, 850, 820, 1500, 2600, 3400, 3900])],
        "Number of salmon", (0, 4500),
        "Line graph of salmon counted in the Ely River: about 850 from 2008 to 2012, then rising to 3,900 by 2020",
        note=(2012, "Dam\nremoved"),
    )
    fig_bread = table_image(
        "Shelf Life of Bread Stored Three Ways",
        ["Storage method", "Days until mold appeared"],
        [["Paper bag at room temperature", "4"], ["Plastic bag at room temperature", "3"],
         ["Plastic bag in refrigerator", "9"], ["Freezer", "more than 60"]],
        "Table of days until mold appeared on bread stored in four ways",
        col_widths=[0.62, 0.38],
    )
    return [
        Q(WIC,
          blank("Although the artist's paintings appear ___, each one is the product of dozens of carefully planned "
                "sketches."),
          P_WIC, "spontaneous", ["deliberate", "methodical", "laborious"],
          "“Although” contrasts appearance with careful planning, so the paintings look <em>spontaneous</em>."),
        Q(WIC,
          blank("The two leaders' meeting ended without agreement, but both described it as ___, saying that the open "
                "exchange of views had been useful."),
          P_WIC, "productive", ["hostile", "pointless", "secretive"],
          "Calling an open, useful exchange <em>productive</em> fits even though no agreement was reached."),
        Q(WIC,
          blank("The scientist's critics argued that her conclusions were ___, since they were based on a single "
                "experiment that had not been repeated."),
          P_WIC, "premature", ["unanimous", "conclusive", "overdue"],
          "Conclusions drawn from one unrepeated experiment were reached too early: they were <em>premature</em>."),
        Q(WIC,
          blank("The essayist's style is famously ___: she rarely uses one word where three will do, and her sentences "
                "often run for half a page."),
          P_WIC, "verbose", ["terse", "plain", "hesitant"],
          "Using many words and very long sentences is <em>verbose</em>; “terse” means the opposite."),
        Q(TSP,
          p("For much of the nineteenth century, doctors did not wash their hands between patients. In 1847, physician "
            "Ignaz Semmelweis noticed that women in one ward of a Vienna hospital, where doctors came directly from "
            "performing autopsies, died of fever far more often than women in a ward staffed by midwives. He required "
            "doctors to wash their hands in a chlorine solution, and deaths in the first ward fell sharply. Yet many "
            "of his colleagues rejected his findings, and handwashing did not become standard practice until decades "
            "later."),
          P_STRUCTURE,
          "It describes a common practice, presents an observation and experiment that challenged it, and notes the "
          "resistance the findings met.",
          ["It explains how midwives were trained and then compares their work with that of doctors.",
           "It describes Semmelweis's career and then argues that he was wrong about handwashing.",
           "It presents two theories about fever and explains why both were later abandoned."],
          "The text moves from the lack of handwashing, to Semmelweis's observation and intervention, to its rejection."),
        Q(TSP,
          underline("The Atacama Desert receives so little rain that some of its weather stations have never recorded "
                    "any. ",
                    "Yet in years when unusual rains do fall, the desert can burst into bloom, with hundreds of species "
                    "of flowers appearing from seeds that have waited in the soil for years.",
                    " Local people call this event the <em>desierto florido</em>, or “flowering desert.”"),
          P_FUNCTION,
          "It describes an exception to the extreme dryness described in the first sentence.",
          ["It explains why some weather stations in the desert have never recorded rain.",
           "It argues that the desert will soon receive more rain than it does today.",
           "It gives an example of a plant that does not need water to grow."],
          "The rare blooming after unusual rains contrasts with the usual dryness."),
        Q(CTC,
          texts("Some researchers have argued that the ability to recognize oneself in a mirror is a sign of advanced "
                "intelligence found only in a few animals, such as great apes, dolphins, and elephants.",
                "Biologist Kenji Ito tested cleaner wrasse, a small reef fish, by placing a colored mark on its throat "
                "where it could be seen only in a mirror. Many of the fish, after looking in the mirror, tried to "
                "scrape off the mark. Ito suggests that the mirror test may be measuring something other than the kind "
                "of intelligence researchers have assumed, or that such intelligence is more widespread than thought."),
          "Based on the texts, how would Ito (Text 2) most likely respond to the researchers' argument in Text 1?",
          "By questioning whether passing the mirror test reliably shows the rare intelligence they describe",
          ["By agreeing that only great apes, dolphins, and elephants can pass the mirror test",
           "By arguing that cleaner wrasse are more intelligent than great apes",
           "By claiming that the mirror test cannot be used with any animal"],
          "A small fish passing the test leads Ito to doubt what the test shows or how rare the ability is."),
        Q(CID,
          p("Many cities are planting “urban forests,” dense groups of trees along streets and in parks. Studies show "
            "that shaded streets can be several degrees cooler on summer days than unshaded streets nearby, because "
            "trees block sunlight and release water vapor from their leaves. Urban planners hope that more trees will "
            "reduce the health risks of heat waves, which are becoming more frequent in many places."),
          P_MAIN_IDEA,
          "Cities are planting trees partly because trees can cool streets and may reduce the dangers of heat waves.",
          ["Trees release more water vapor in cities than in forests.",
           "Heat waves have become less frequent in cities that plant trees.",
           "Urban forests are planted mainly to provide homes for birds."],
          "The text explains how trees cool streets and why planners want them for heat waves."),
        Q(CID,
          p("The following text is from a short story. Grace, a lighthouse keeper's daughter, is watching a storm.")
          + p("Her father had gone down to check the boats, and Grace was alone with the lamp. Every few seconds its "
              "beam swept past the window, white across the black water, and she counted the seconds between flashes "
              "as he had taught her: one, two, three, four. The wind threw rain against the glass like handfuls of "
              "gravel. Grace kept counting. As long as the light turned, she told herself, the ships would know where "
              "the rocks were."),
          P_MAIN_IDEA,
          "During a frightening storm, Grace steadies herself by focusing on the lighthouse's purpose.",
          ["Grace is angry that her father left her alone during the storm.",
           "Grace tries to repair the lamp after it stops turning.",
           "Grace sees a ship crash into the rocks below the lighthouse."],
          "Grace counts the flashes and reminds herself that the light guides ships, which keeps her calm."),
        Q(COET,
          p("Historian Rafael Duarte claims that a series of letters long attributed to a famous general were actually "
            "written by his secretary."),
          P_FINDING,
          "The handwriting in the letters matches the handwriting in the secretary's personal diary but not the "
          "handwriting in documents the general is known to have written himself.",
          ["The letters discuss events that the general took part in.",
           "The general wrote many letters during his military career.",
           "The secretary worked for the general for more than ten years."],
          "Matching handwriting to the secretary, and not to the general, directly supports Duarte's claim."),
        Q(COEQ,
          p("Three schools banned students' phones during class. A researcher notes that the ban was followed by a "
            "large increase in students reporting good concentration at two schools, but only a small change at the "
            "third: at School B, the percentage ___"),
          P_GRAPH,
          "rose only from 52% to 54%.",
          ["rose from 48% to 63%.",
           "rose from 45% to 61%.",
           "fell from 54% to 52%."],
          "School B shows the small change the researcher describes.",
          figure=fig_phones),
        Q(COEQ,
          p("A dam on the Ely River was removed in 2012 so that salmon could reach their spawning grounds upstream. "
            "Biologists say the removal has been a success, pointing out that the number of salmon counted ___"),
          P_GRAPH,
          "stayed below 1,000 from 2008 to 2012 but rose to about 3,900 by 2020.",
          ["fell slightly from 2008 to 2012.",
           "was about 900 in 2008.",
           "rose every year from 2008 to 2020."],
          "A low, flat count before 2012 and a sharp rise afterward supports the claim.",
          figure=fig_salmon),
        Q(COEQ,
          p("A student is investigating how to keep bread fresh. The student concludes that cold temperatures slow the "
            "growth of mold more than the type of bag does: bread in a plastic bag lasted ___"),
          P_TABLE,
          "9 days in a refrigerator but only 3 days at room temperature, while bread in a paper bag at room "
          "temperature lasted 4 days.",
          ["more than 60 days in a freezer.",
           "3 days at room temperature, 1 day less than bread in a paper bag.",
           "9 days at room temperature but only 3 days in a refrigerator."],
          "Only this choice shows the large effect of cold compared with the small effect of the bag type.",
          figure=fig_bread),
        Q(INF,
          p("Many migrating birds fly at night. Ornithologist Helena Varga found that birds released in a planetarium "
            "oriented themselves correctly when shown the normal night sky, but became confused when the stars were "
            "rearranged so that the pattern no longer matched the real sky. Birds tested on overcast nights without the "
            "planetarium also oriented poorly. These findings suggest that ___"),
          P_INFER,
          "the birds may use the pattern of the stars to find their direction.",
          ["the birds navigate mainly by the position of the Sun.",
           "the birds cannot migrate on clear nights.",
           "planetariums cause birds to lose their sense of direction permanently."],
          "Confusion when the star pattern changes or is hidden points to the stars as a guide."),
        Q(FSS,
          blank("The success of the new vaccines, which were developed in record time, ___ researchers around the "
                "world."),
          P_SEC, "has encouraged", ["have encouraged", "encourage", "are encouraging"],
          "The subject is the singular “success,” so the singular verb <em>has encouraged</em> is required."),
        Q(BND,
          blank("Amrita Sher-Gil, one of India's most celebrated modern ___ combined techniques she learned in Paris with "
                "subjects drawn from everyday Indian life."),
          P_SEC, "painters,", ["painters", "painters;", "painters—"],
          "The appositive that begins with a comma after “Sher-Gil” must also close with a comma."),
        Q(FSS,
          blank("Of the two routes to the summit, the eastern one is the ___ because it has fewer steep sections."),
          P_SEC, "easier", ["easiest", "most easy", "more easier"],
          "Comparing exactly two routes calls for the comparative <em>easier</em>."),
        Q(BND,
          blank("The recipe calls for an unusual ___ a pinch of black pepper in the strawberry jam."),
          P_SEC, "ingredient:", ["ingredient;", "ingredient", "ingredient, it is"],
          "A colon introduces the explanation of the unusual ingredient."),
        Q(FSS,
          blank("The volunteers who cleaned the beach last weekend collected more than 300 kilograms of trash, most of "
                "___ was plastic."),
          P_SEC, "which", ["it", "that", "them"],
          "“Most of which” correctly introduces a dependent clause about the trash; “it” would create a comma "
          "splice."),
        Q(BND,
          blank("Scientists have found evidence of liquid water beneath the icy surface of Europa, one of Jupiter's "
                "___ this makes it one of the most promising places to search for life beyond Earth."),
          P_SEC, "moons;", ["moons,", "moons", "moons, and, this"],
          "Two independent clauses are joined with a semicolon."),
        Q(FSS,
          blank("To reduce traffic, the city council has proposed charging drivers a fee to enter the city center, "
                "a plan that ___ already been tried successfully in several other cities."),
          P_SEC, "has", ["have", "are", "were"],
          "The verb agrees with “a plan,” which is singular: <em>has</em>."),
        Q(TRN,
          blank("The first telephones required an operator to connect every call by hand. ___ automatic switching "
                "systems, introduced in the late 1800s and early 1900s, allowed callers to dial numbers themselves."),
          P_TRANSITION, "Later,", ["Similarly,", "In other words,", "For example,"],
          "Automatic switching came after the operator system."),
        Q(TRN,
          blank("The study found that people who slept less than six hours a night made more errors on memory tests. "
                "___ the researchers recommend that students avoid staying up late before exams."),
          P_TRANSITION, "Accordingly,", ["Nevertheless,", "In contrast,", "Meanwhile,"],
          "The recommendation follows from the finding."),
        Q(TRN,
          blank("Some plants defend themselves against grazing animals with sharp thorns. Other plants, ___ rely on "
                "chemicals that make their leaves taste bitter."),
          P_TRANSITION, "by contrast,", ["for example,", "as a result,", "in other words,"],
          "Chemical defenses are a different strategy from thorns, so the sentence contrasts the two groups."),
        Q(RS,
          notes(["The Great Pyramid of Giza was built around 2560 BCE.",
                 "It was originally about 146 meters tall.",
                 "For about 3,800 years, it was the tallest human-made structure in the world.",
                 "It was built as a tomb for the pharaoh Khufu."],
                "The student wants to emphasize how long the Great Pyramid held a record."),
          P_NOTES_Q,
          "Built around 2560 BCE, the Great Pyramid of Giza remained the tallest human-made structure in the world for "
          "about 3,800 years.",
          ["The Great Pyramid of Giza was built as a tomb for the pharaoh Khufu.",
           "The Great Pyramid of Giza was originally about 146 meters tall.",
           "The Great Pyramid of Giza was built around 2560 BCE."],
          "Only this choice mentions the record held for 3,800 years."),
        Q(RS,
          notes(["Researchers taught a group of crows to recognize a person wearing a particular mask.",
                 "The person wearing the mask had captured some crows.",
                 "Years later, crows scolded and mobbed anyone wearing that mask.",
                 "Even crows that had never been captured joined in."],
                "The student wants to emphasize that crows may learn from one another."),
          P_NOTES_Q,
          "Crows that had never been captured also mobbed people wearing the mask, suggesting that crows may learn "
          "from one another.",
          ["Researchers taught crows to recognize a person wearing a particular mask.",
           "Years later, crows scolded people wearing the mask.",
           "The person wearing the mask had captured some crows."],
          "Only this choice points to uncaptured crows joining in, which suggests learning from others."),
        Q(RS,
          notes(["Gabriel García Márquez was a Colombian writer.",
                 "His novel <em>One Hundred Years of Solitude</em> was published in 1967.",
                 "The novel mixes realistic events with magical ones, a style often called magical realism.",
                 "He received the Nobel Prize in Literature in 1982."],
                "The student wants to explain what magical realism is, using García Márquez's novel as an example."),
          P_NOTES_Q,
          "Magical realism mixes realistic events with magical ones, as Gabriel García Márquez does in <em>One Hundred "
          "Years of Solitude</em>.",
          ["Gabriel García Márquez received the Nobel Prize in Literature in 1982.",
           "<em>One Hundred Years of Solitude</em> was published in 1967.",
           "Gabriel García Márquez was a Colombian writer who received the Nobel Prize."],
          "Only this choice defines the style and gives the novel as an example."),
    ]
