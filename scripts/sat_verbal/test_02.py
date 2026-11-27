"""Academor SAT Practice Test 2 — Reading and Writing."""

from sat_verbal.common import (
    BND, CID, COEQ, COET, CTC, FSS, INF, P_FINDING, P_FUNCTION, P_GRAPH, P_INFER, P_MAIN_IDEA,
    P_NOTES_Q, P_PURPOSE, P_SEC, P_STRUCTURE, P_TABLE, P_TRANSITION, P_WEAKEN, P_WIC, Q, RS, TRN, TSP,
    WIC, bar_chart, blank, grouped_bar_chart, line_chart, notes, p, table_image, texts, underline,
)


def module_1():
    fig_seedlings = bar_chart(
        "Seedling Survival After One Year by Planting Method",
        ["Bare\nsoil", "Shaded", "Mulched", "Mulched\nand watered"],
        [34, 49, 58, 71],
        "Seedlings surviving (%)", 80,
        "Bar graph of the percentage of seedlings surviving after one year for four planting methods",
        value_fmt="{:.0f}%",
    )
    fig_library = line_chart(
        "Library Building Visits and E-Book Loans in Riverton, 2015–2023",
        [2015, 2017, 2019, 2021, 2023],
        [("Building visits", [520, 495, 470, 390, 380]), ("E-book loans", [40, 75, 120, 185, 210])],
        "Thousands", (0, 600),
        "Line graph of library building visits falling from 520 to 380 thousand and e-book loans rising "
        "from 40 to 210 thousand between 2015 and 2023",
    )
    fig_study = table_image(
        "Average Quiz Scores by Study Strategy",
        ["Strategy", "1 day later", "1 week later"],
        [["Rereading", "78", "52"], ["Highlighting", "75", "49"], ["Practice testing", "74", "68"]],
        "Table of average quiz scores one day and one week after studying for three study strategies",
        col_widths=[0.44, 0.28, 0.28],
    )
    return [
        # ---- Craft and Structure -------------------------------------------
        Q(WIC,
          blank("The architect's design for the new library was praised for its ___: every element, from the "
                "reading tables to the light fixtures, served a clear purpose, and nothing was added merely as "
                "decoration."),
          P_WIC, "economy", ["extravagance", "obscurity", "fragility"],
          "A design in which every element has a purpose and nothing is decorative shows <em>economy</em>, "
          "careful avoidance of anything unnecessary."),
        Q(WIC,
          blank("Marine biologist Keiko Arai notes that octopuses are remarkably ___ problem solvers: in laboratory "
                "trials, an octopus that failed to open a sealed jar on its first attempt usually tried a different "
                "approach on the next."),
          P_WIC, "flexible", ["reluctant", "predictable", "solitary"],
          "Switching to a different approach after a failure shows that the animals are <em>flexible</em>."),
        Q(WIC,
          blank("Although the trade agreement was signed with great ceremony, its practical effects were ___: "
                "tariffs between the two countries stayed nearly the same, and the volume of trade barely changed."),
          P_WIC, "negligible", ["immediate", "permanent", "far-reaching"],
          "Tariffs and trade that barely changed mean that the effects were <em>negligible</em>, in contrast to "
          "the ceremony."),
        Q(WIC,
          blank("The committee's report was deliberately ___: it summarized the arguments for and against each "
                "proposal without recommending any of them, leaving the final decision to the city council."),
          P_WIC, "noncommittal", ["partisan", "inaccurate", "hasty"],
          "A report that lays out every side without recommending one is <em>noncommittal</em>."),
        Q(TSP,
          underline("The Asian giant hornet can kill thousands of European honeybees in a few hours. Japanese "
                    "honeybees, however, have a striking defense. ",
                    "When a hornet scout enters their hive, hundreds of bees surround it in a tight ball and vibrate "
                    "their flight muscles, raising the temperature inside the ball to about 46°C.",
                    " The hornet cannot survive this heat, but the bees can."),
          P_FUNCTION,
          "It describes the defense that the previous sentence introduces.",
          ["It explains why European honeybees are unable to defend themselves against hornets.",
           "It presents evidence that contradicts a claim made in the first sentence.",
           "It raises a question that the final sentence leaves unanswered."],
          "The second sentence mentions a “striking defense”; the underlined sentence explains what that defense is."),
        Q(TSP,
          p("The following text is from a short story. Marisol is about to give a speech at her high school "
            "graduation.")
          + p("Marisol had rehearsed the speech so many times that the words no longer felt like hers. Standing at "
              "the podium, she looked out at the rows of folding chairs and at faces she had known since "
              "kindergarten, and for a moment every sentence left her. Then she noticed her grandfather in the third "
              "row, nodding slowly, the way he did whenever she read aloud to him in his kitchen. She folded her "
              "notes, set them aside, and began to speak."),
          P_PURPOSE,
          "To portray a moment in which a character regains her composure by focusing on someone familiar",
          ["To explain why a character decided to give a speech she had not prepared",
           "To describe a character's frustration with an audience that is not paying attention",
           "To contrast a character's childhood memories with her plans for the future"],
          "Marisol loses her words, sees her grandfather nodding as he does at home, and then speaks without her "
          "notes: she recovers her composure through a familiar person."),
        Q(CTC,
          texts("Many economists have argued that shortening the workweek from five days to four would reduce a "
                "company's output. If employees work fewer hours, the reasoning goes, they will inevitably produce "
                "less, unless the company hires more workers.",
                "Economist Daniel Mwangi tracked 60 companies that moved to a four-day week without reducing pay. "
                "After one year, output at most of the companies was about the same as before. Mwangi found that "
                "employees took fewer sick days and spent less time in long meetings, which he suggests made up for "
                "the hours that were cut."),
          "Based on the texts, how would Mwangi (Text 2) most likely respond to the economists' reasoning in Text 1?",
          "By suggesting that it overlooks ways in which a shorter week can keep output from falling",
          ["By agreeing that companies must hire more workers if they adopt a four-day week",
           "By arguing that employees should be paid more when they work four days instead of five",
           "By claiming that the economists based their conclusion on too few companies"],
          "Mwangi found that output stayed about the same because of fewer sick days and shorter meetings, which "
          "the economists' reasoning does not consider. Text 1 does not mention any study of companies."),
        # ---- Information and Ideas -----------------------------------------
        Q(CID,
          p("Mangrove forests cover only a small part of Earth's coastlines, yet they store large amounts of "
            "carbon. Much of this carbon is held not in the trees themselves but in the waterlogged soil beneath "
            "them, where low levels of oxygen slow the decay of fallen leaves and roots. When mangroves are cleared "
            "for farms or buildings, that soil is exposed to the air, and the carbon it holds can be released into "
            "the atmosphere."),
          P_MAIN_IDEA,
          "Mangrove forests hold much of their carbon in their soil, which can release it if the forests are cleared.",
          ["Mangrove trees store more carbon in their leaves than in their roots.",
           "Most of Earth's coastlines were once covered by mangrove forests.",
           "Clearing mangroves for farms increases the amount of carbon stored in coastal soil."],
          "The text explains where mangroves store carbon (largely in the soil) and what happens to it when the "
          "forests are cleared."),
        Q(CID,
          p("In 1843 Ada Lovelace published a set of notes on the Analytical Engine, a calculating machine designed "
            "by her friend Charles Babbage. Babbage thought of the engine mainly as a tool for arithmetic. Lovelace "
            "went further: she suggested that because the machine followed rules for manipulating symbols, it might "
            "one day work with symbols that stood for things other than numbers—for example, the notes of a musical "
            "composition."),
          "According to the text, what did Lovelace suggest about the Analytical Engine?",
          "It might be able to work with symbols other than numbers, such as musical notes.",
          ["It would soon replace mathematicians in solving difficult problems.",
           "It had already been built and tested by Babbage before 1843.",
           "It could perform only calculations that people had already done by hand."],
          "Lovelace suggested the engine might handle symbols “other than numbers—for example, the notes of a "
          "musical composition.”"),
        Q(COET,
          p("Many songbirds that live in cities sing at a higher pitch than members of the same species living in "
            "the countryside. Biologist Tomás Herrera and his team hypothesize that the birds raise their pitch so "
            "that their songs are not drowned out by traffic noise, which is concentrated at low pitches."),
          P_FINDING,
          "In a city park, birds of one species sang at higher pitches on weekdays, when traffic was heavy, than on "
          "Sundays, when traffic was light.",
          ["Birds of the species living in the countryside sang more often in the morning than in the evening.",
           "City birds of the species had longer songs than birds of the species in the countryside.",
           "The species was more common in city parks than in nearby forests."],
          "If pitch rises and falls with the amount of traffic, that directly links higher songs to traffic noise."),
        Q(COEQ,
          p("Ecologist Rhea Malhotra planted tree seedlings using four methods and recorded how many survived for a "
            "year. She concluded that covering the soil with mulch improved survival compared with planting in bare "
            "soil, but that mulching combined with regular watering was the most effective method: ___"),
          P_GRAPH,
          "34% of seedlings survived in bare soil, compared with 58% of mulched seedlings and 71% of seedlings that "
          "were mulched and watered.",
          ["49% of shaded seedlings survived, which was more than the percentage that survived in bare soil.",
           "71% of seedlings that were mulched and watered survived, compared with 49% of shaded seedlings.",
           "34% of mulched seedlings survived, which was less than the percentage of shaded seedlings that survived."],
          "Only this choice compares bare soil, mulch alone and mulch with watering, the three methods in the "
          "conclusion, and it reports the graph accurately.",
          figure=fig_seedlings),
        Q(COEQ,
          p("Riverton's head librarian argues that although fewer people are visiting the library's buildings, the "
            "library is reaching readers in other ways. For example, between 2015 and 2023, ___"),
          P_GRAPH,
          "e-book loans rose from about 40 thousand to about 210 thousand while building visits fell from about "
          "520 thousand to about 380 thousand.",
          ["building visits rose from about 380 thousand to about 520 thousand while e-book loans stayed about the same.",
           "e-book loans were higher than building visits in every year shown.",
           "building visits fell by about 140 thousand, the largest drop of any year in the period."],
          "Rising e-book loans alongside falling building visits illustrates the librarian's point; the other "
          "choices misread the graph.",
          figure=fig_library),
        Q(COEQ,
          p("A student is writing about a study in which participants used one of three strategies to study the same "
            "material and then took a quiz either one day or one week later. The student claims that practice "
            "testing produced the best long-term results even though it did not produce the best short-term results. "
            "Participants who used practice testing scored ___"),
          P_TABLE,
          "lower than participants who reread the material on the quiz taken one day later (74 versus 78) but higher "
          "than them on the quiz taken one week later (68 versus 52).",
          ["higher than participants in every other group on both quizzes.",
           "68 on the quiz taken one day later and 74 on the quiz taken one week later.",
           "about the same as participants who highlighted the material on the quiz taken one week later (68 versus 49)."],
          "Only this choice shows practice testing behind rereading after one day but well ahead after one week, as "
          "the claim states.",
          figure=fig_study),
        Q(INF,
          p("Several species of seed-eating birds store food in hidden caches to eat during winter. Biologist Hana "
            "Lindqvist compared two closely related species. Birds of the first species hid seeds in thousands of "
            "separate places and later found more than 80 percent of them. Birds of the second species stored seeds "
            "in a few large caches. Lindqvist also found that the first species has a larger hippocampus, a brain "
            "region involved in spatial memory. These findings suggest that ___"),
          P_INFER,
          "the ability to remember many separate cache locations may be related to the size of the hippocampus.",
          ["birds that store seeds in a few large caches eat less during winter than other birds do.",
           "the second species could find its caches only by smell.",
           "a larger hippocampus causes birds to collect more seeds than they can eat."],
          "The species that remembers thousands of hiding places also has the larger memory region, which suggests "
          "a link between the two."),
        # ---- Standard English Conventions ----------------------------------
        Q(FSS,
          blank("The collection of letters that the explorer wrote during her travels ___ now kept at the national "
                "archive, where researchers can request to read them."),
          P_SEC, "is", ["are", "were", "have been"],
          "The subject is the singular noun “collection,” not “letters,” so the singular verb <em>is</em> is needed; "
          "“now” calls for the present tense."),
        Q(BND,
          blank("Saturn's rings are made mostly of chunks of water ___ particles are as small as grains of sand, while "
                "others are as large as houses."),
          P_SEC, "ice; some", ["ice, some", "ice some", "ice, which some"],
          "Two independent clauses must be joined properly; a semicolon does this, while a comma alone creates a "
          "comma splice."),
        Q(FSS,
          blank("When the first public museums opened in eighteenth-century Europe, many of ___ admitted visitors only "
                "on certain days and required them to request tickets in advance."),
          P_SEC, "them", ["it", "its", "their"],
          "The pronoun refers to the plural noun “museums,” and as the object of “of” it must be <em>them</em>."),
        Q(BND,
          blank("The ancient Roman fish sauce known as garum required only two main ___ fish and salt, which were left "
                "to ferment in the sun for several months."),
          P_SEC, "ingredients:", ["ingredients;", "ingredients, and", "ingredients, they were"],
          "A colon introduces the list that explains the “two main ingredients.”"),
        Q(FSS,
          blank("By the time the climbers reached the summit, they ___ through the night to set up their final camp "
                "and had slept only a few hours."),
          P_SEC, "had climbed", ["climb", "will have climbed", "are climbing"],
          "The climbing happened before another past action (reaching the summit), so the past perfect <em>had "
          "climbed</em> is needed; it also matches “had slept.”"),
        Q(BND,
          blank("Maria Sibylla ___ seventeenth-century German naturalist and artist, recorded the stages of butterfly "
                "metamorphosis in detailed illustrations."),
          P_SEC, "Merian, a", ["Merian a", "Merian; a", "Merian: a"],
          "“A seventeenth-century German naturalist and artist” is a nonessential appositive that must be set off by "
          "a pair of commas."),
        Q(FSS,
          blank("Each spring, the colony's ___ return to the same cliff and repair the mud nests they built the year "
                "before."),
          P_SEC, "swallows", ["swallow's", "swallows'", "swallow"],
          "The sentence needs a plural noun as the subject of “return”; no possession is shown."),
        # ---- Expression of Ideas -------------------------------------------
        Q(TRN,
          blank("Early telescopes produced blurry images because their glass lenses bent different colors of light by "
                "different amounts. ___ Isaac Newton designed a telescope that used a curved mirror instead of a "
                "lens to gather light."),
          P_TRANSITION, "To avoid this problem,", ["Similarly,", "For instance,", "Nevertheless,"],
          "Newton's mirror design was a way around the problem with lenses described in the first sentence."),
        Q(TRN,
          blank("Most of the world's volcanoes form along the boundaries between tectonic plates. The Hawaiian "
                "Islands, ___ formed far from any plate boundary, above a hot spot in Earth's mantle."),
          P_TRANSITION, "however,", ["for example,", "therefore,", "similarly,"],
          "Hawaii is an exception to the general pattern in the first sentence."),
        Q(TRN,
          blank("The city's new bike-share program attracted fewer riders than expected in its first month. ___ "
                "ridership tripled in the second month, after the city added stations near the main train station."),
          P_TRANSITION, "However,", ["Similarly,", "As a result,", "In other words,"],
          "The strong second month contrasts with the weak first month."),
        Q(RS,
          notes(["The Svalbard Global Seed Vault opened in 2008 on an island in the Norwegian Arctic.",
                 "It stores duplicate samples of seeds held in gene banks around the world.",
                 "If a gene bank's collection is damaged or lost, the duplicates can be used to restore it.",
                 "The vault is dug into a mountain, where the permafrost helps keep the seeds cold."],
                "The student wants to explain the purpose of the Svalbard Global Seed Vault."),
          P_NOTES_Q,
          "The Svalbard Global Seed Vault stores duplicate seed samples so that gene banks can restore their "
          "collections if they are damaged or lost.",
          ["The Svalbard Global Seed Vault, which opened in 2008, is located on an island in the Norwegian Arctic.",
           "The Svalbard Global Seed Vault is dug into a mountain, where the permafrost helps keep seeds cold.",
           "Gene banks around the world hold seeds, and the Svalbard Global Seed Vault opened in 2008."],
          "Only this choice states what the vault is for."),
        Q(RS,
          notes(["A day on a planet is the time it takes to spin once on its axis.",
                 "A year on a planet is the time it takes to orbit the Sun once.",
                 "Venus takes about 243 Earth days to spin once on its axis.",
                 "Venus takes about 225 Earth days to orbit the Sun."],
                "The student wants to emphasize an unusual fact about the length of a day on Venus."),
          P_NOTES_Q,
          "A day on Venus, about 243 Earth days, is longer than a year on Venus, about 225 Earth days.",
          ["Venus takes about 225 Earth days to orbit the Sun once.",
           "A day is the time it takes a planet to spin once, and a year is the time it takes to orbit the Sun.",
           "Venus spins on its axis and orbits the Sun, as Earth does."],
          "The unusual fact is that Venus's day is longer than its year; only this choice says so."),
        Q(RS,
          notes(["Sor Juana Inés de la Cruz was a seventeenth-century poet and scholar in New Spain (present-day Mexico).",
                 "She became a nun, which allowed her to keep studying and writing.",
                 "In 1691 she wrote a famous letter, now called the <em>Respuesta</em>, defending women's right to education.",
                 "She also wrote plays and poems that are still widely read."],
                "The student wants to introduce Sor Juana to an audience unfamiliar with her, emphasizing her defense "
                "of women's education."),
          P_NOTES_Q,
          "Sor Juana Inés de la Cruz, a seventeenth-century poet and scholar in present-day Mexico, wrote a famous "
          "1691 letter defending women's right to education.",
          ["In 1691 Sor Juana wrote a letter that is now called the <em>Respuesta</em>.",
           "Sor Juana became a nun, which allowed her to keep studying and writing.",
           "Many people still read the plays and poems of Sor Juana Inés de la Cruz."],
          "Only this choice identifies who Sor Juana was and highlights her defense of women's education."),
    ]


def module_2():
    fig_power = grouped_bar_chart(
        "Share of Electricity from Wind and Solar Power in Four Countries",
        ["Country W", "Country X", "Country Y", "Country Z"],
        [("2012", [6, 11, 4, 9]), ("2022", [14, 15, 22, 12])],
        "Share of electricity (%)", 25,
        "Grouped bar graph of the share of electricity from wind and solar power in four countries in 2012 and 2022",
    )
    fig_cranes = line_chart(
        "Cranes Counted at Marsh Lake Each Autumn, 2012–2022",
        [2012, 2014, 2016, 2018, 2020, 2022],
        [("Cranes counted", [310, 295, 300, 420, 560, 640])],
        "Number of cranes", (0, 700),
        "Line graph of cranes counted at Marsh Lake, steady at about 300 until 2016 and rising to 640 by 2022",
        note=(2016, "Wetland\nrestoration\nbegins"),
    )
    fig_islands = table_image(
        "Seabird Nesting Success on Four Islands",
        ["Island", "Rats present?", "Nests that fledged a chick"],
        [["North Isle", "Yes", "21%"], ["Gull Rock", "No", "64%"], ["Pine Island", "Yes", "28%"],
         ["Far Skerry", "No", "59%"]],
        "Table of the percentage of seabird nests that fledged a chick on two islands with rats and two islands without rats",
        col_widths=[0.32, 0.28, 0.40],
    )
    return [
        # ---- Craft and Structure -------------------------------------------
        Q(WIC,
          blank("Some critics dismissed the novelist's early stories as ___, but later readers recognized that their "
                "apparent simplicity concealed carefully constructed patterns of imagery."),
          P_WIC, "artless", ["intricate", "sentimental", "lengthy"],
          "The critics mistook the stories' simplicity for a lack of skill: they called them <em>artless</em>, which "
          "later readers found to be wrong."),
        Q(WIC,
          blank("The physicist's explanation of how semiconductors work was so ___ that even listeners with no "
                "background in science could follow every step."),
          P_WIC, "lucid", ["tentative", "esoteric", "laborious"],
          "An explanation that anyone can follow is clear, or <em>lucid</em>; “esoteric” means the opposite."),
        Q(WIC,
          blank("Although the governor's transportation plan was popular when it was announced, support for it began "
                "to ___ once voters learned how much it would cost."),
          P_WIC, "wane", ["intensify", "stabilize", "originate"],
          "“Although … popular” signals a change for the worse: support began to <em>wane</em>."),
        Q(WIC,
          blank("Rather than ___ the findings of earlier researchers, the new study builds on them, using more precise "
                "instruments to confirm and extend their measurements."),
          P_WIC, "repudiating", ["corroborating", "summarizing", "publicizing"],
          "The study confirms and extends the earlier work instead of rejecting it, or <em>repudiating</em> it."),
        Q(TSP,
          p("For decades, astronomers counted Pluto as the ninth planet in the solar system. In 2005, however, "
            "astronomers announced the discovery of Eris, a distant icy body with more mass than Pluto, which raised "
            "the question of whether Eris should also be called a planet. In 2006 the International Astronomical "
            "Union adopted a definition requiring a planet to have cleared the area around its orbit of other "
            "objects. Pluto, which shares its region of space with many icy bodies, was reclassified as a dwarf "
            "planet."),
          P_STRUCTURE,
          "It describes a long-standing classification, presents a discovery that raised questions about it, and "
          "then explains how the classification changed.",
          ["It presents two competing definitions of a planet and argues that the older one is more useful.",
           "It explains how Eris was discovered and then describes the methods astronomers use to measure mass.",
           "It describes why Pluto was first classified as a planet and then argues that it should be classified "
           "as one again."],
          "The text moves from Pluto's status as a planet, to the discovery of Eris, to the new definition that "
          "changed Pluto's classification. It takes no side."),
        Q(TSP,
          underline("Researchers have long debated whether learning two languages in childhood affects mental skills "
                    "that are not related to language. Psychologist Lena Varga gave children a task that required them "
                    "to sort cards first by color and then, without warning, by shape. ",
                    "Children who spoke two languages switched to the new sorting rule more quickly than children who "
                    "spoke only one.",
                    " Varga suggests that regularly switching between two languages may give children practice in "
                    "shifting their attention."),
          P_FUNCTION,
          "It presents a result that Varga uses as the basis for the suggestion in the final sentence.",
          ["It describes a limitation of the card-sorting task that Varga used.",
           "It introduces the debate that Varga's study was designed to settle.",
           "It offers an explanation that the final sentence rejects."],
          "The faster switching by bilingual children is the finding on which Varga bases her suggestion about "
          "practice in shifting attention."),
        Q(CTC,
          texts("Historians have often described the printing press as the main reason that new religious ideas spread "
                "so quickly across Europe in the sixteenth century. Printed pamphlets, they argue, allowed a single "
                "writer's arguments to reach thousands of readers within weeks.",
                "Historian Clara Ruiz agrees that printing mattered, but she notes that most Europeans at the time "
                "could not read. In the towns she studied, Ruiz found that new ideas spread largely through sermons, "
                "public debates, and songs that people learned by ear and repeated to one another."),
          "Based on the texts, how would Ruiz (Text 2) most likely respond to the historians' view in Text 1?",
          "By arguing that it gives too little weight to ways of spreading ideas that did not depend on reading",
          ["By agreeing that printed pamphlets were the only way most Europeans learned about new ideas",
           "By claiming that the printing press had no effect on the spread of new religious ideas",
           "By suggesting that more Europeans could read in the sixteenth century than historians have assumed"],
          "Ruiz grants that printing mattered but stresses sermons, debates and songs for people who could not read."),
        # ---- Information and Ideas -----------------------------------------
        Q(CID,
          p("An octopus has about 500 million neurons, and roughly two-thirds of them are located not in its brain but "
            "in its eight arms. This arrangement allows each arm to respond to touch and taste and even to carry out "
            "some movements, such as grasping food, without detailed instructions from the brain. Researchers think "
            "this may help an octopus control a body that has no rigid skeleton and an almost limitless range of "
            "possible positions."),
          P_MAIN_IDEA,
          "Because many of an octopus's neurons are in its arms, the arms can handle some tasks on their own, which "
          "may help the animal control its flexible body.",
          ["An octopus has more neurons than any other animal without a skeleton.",
           "The brain of an octopus is too small to control the animal's movements.",
           "Researchers have not yet found out how octopuses use their arms to grasp food."],
          "The text explains where an octopus's neurons are, what this lets the arms do, and why it may be useful."),
        Q(CID,
          p("The following text is from a short story. Mr. Okonjo has repaired clocks in the same small shop for "
            "forty years.")
          + p("His daughter had brought the brochures again—bright pictures of retirement villages beside the sea. Mr. "
              "Okonjo set them on the counter beside a mantel clock whose spring he had been coaxing back to life all "
              "morning. He did not dislike the sea. But when the clock finally began to tick, steady and sure, he "
              "listened to it the way some people listen to music, and he knew he would not be leaving the shop "
              "this year."),
          P_MAIN_IDEA,
          "Mr. Okonjo's satisfaction in his work leads him to decide against retiring for now.",
          ["Mr. Okonjo is unhappy that his daughter wants him to move away from the sea.",
           "Mr. Okonjo has grown tired of repairing clocks and wants a quieter life.",
           "Mr. Okonjo cannot repair the mantel clock and decides to close his shop."],
          "Hearing the repaired clock tick, he takes pleasure in his work and decides not to leave the shop this year."),
        Q(COET,
          p("A mountain frog species has declined sharply over the past twenty years. Biologist Aiko Tanaka and her "
            "team claim that the main cause of the decline is a fungal disease that attacks the frogs' skin, rather "
            "than the loss of the frogs' habitat."),
          P_WEAKEN,
          "Frog populations declined just as sharply in areas where the fungus was absent as in areas where it was "
          "present.",
          ["Frogs infected with the fungus were less active than frogs that were not infected.",
           "The fungus was found in more than half of the ponds where the frogs live.",
           "Areas where the frogs' habitat was protected also had the fungus."],
          "If frogs declined equally with or without the fungus, the fungus cannot be the main cause."),
        Q(COEQ,
          p("A student is writing about the growth of wind and solar power. The student notes that while each of the "
            "four countries shown increased the share of its electricity that came from wind and solar between 2012 "
            "and 2022, the size of the increase varied a great deal. For example, ___"),
          "Which choice most effectively uses data from the graph to complete the example?",
          "Country Y's share rose from 4% to 22%, while Country X's share rose only from 11% to 15%.",
          ["Country W's share was 6% in 2012 and 14% in 2022.",
           "Country Z had a higher share than Country Y in 2022.",
           "Country X had the highest share of the four countries in both 2012 and 2022."],
          "Only this choice contrasts a large increase (18 points) with a small one (4 points); the other choices "
          "describe a single country or misread the graph.",
          figure=fig_power),
        Q(COEQ,
          p("Marsh Lake was drained for farmland decades ago, and in 2016 a conservation group began restoring part "
            "of the wetland. Volunteers count the cranes that stop at the lake during their autumn migration. The "
            "group argues that the restoration has made the lake more attractive to cranes, noting that ___"),
          P_GRAPH,
          "the number of cranes stayed close to 300 from 2012 to 2016 but rose to about 640 by 2022.",
          ["the number of cranes was higher in 2012 than in 2014.",
           "about 300 cranes were counted in 2016, the year the restoration began.",
           "the number of cranes fell every year after the restoration began."],
          "A flat count before 2016 and a steady rise afterward supports the claim; the other choices either ignore "
          "the change or misread the graph.",
          figure=fig_cranes),
        Q(COEQ,
          p("Rats that reach islands often eat the eggs and chicks of ground-nesting seabirds. A biologist surveyed "
            "four islands and concluded that rats were associated with much lower nesting success. In support of "
            "this conclusion, the biologist points out that ___"),
          P_TABLE,
          "on both islands with rats, fewer than 30% of nests fledged a chick, while on both islands without rats, "
          "more than 55% did.",
          ["Gull Rock had a higher percentage of successful nests than Far Skerry did.",
           "North Isle and Pine Island both have rats.",
           "28% of nests on Pine Island fledged a chick."],
          "Only this choice compares the islands with and without rats.",
          figure=fig_islands),
        Q(INF,
          p("In many orchards, farmers rent honeybee hives to pollinate their trees. Ecologist Samuel Ortiz studied "
            "apple orchards and found that orchards surrounded by patches of natural woodland were visited by many "
            "species of wild bees, while orchards surrounded only by other farms were visited by few. Orchards near "
            "woodland produced more apples than other orchards, even when both kinds of orchards had the same number "
            "of rented hives. These findings suggest that ___"),
          P_INFER,
          "wild bees from nearby woodland may add to the pollination that rented honeybees provide.",
          ["rented honeybees are unable to pollinate apple trees on their own.",
           "farmers near woodland rent more hives than other farmers do.",
           "apple trees in woodland produce more fruit than apple trees on farms do."],
          "With the same number of rented hives, orchards with more wild bee visitors produced more apples, "
          "which points to an added contribution from wild bees."),
        # ---- Standard English Conventions ----------------------------------
        Q(BND,
          blank("The first successful vaccine was developed in the 1790s by Edward Jenner, who observed that milkmaids "
                "who had caught cowpox, a mild ___ seemed to be protected from smallpox."),
          P_SEC, "disease,", ["disease", "disease;", "disease:"],
          "“A mild disease” is a nonessential appositive that begins with a comma, so it must also end with one."),
        Q(FSS,
          blank("Neither the museum's director nor its curators ___ expected the small exhibit of embroidered maps to "
                "draw such large crowds."),
          P_SEC, "had", ["has", "was", "is"],
          "With “neither … nor,” the verb agrees with the nearer subject, the plural “curators,” and the past "
          "context calls for <em>had</em>."),
        Q(BND,
          blank("Composer Florence Price became the first Black woman to have a symphony performed by a major American "
                "orchestra in ___ Chicago Symphony Orchestra played her Symphony in E Minor."),
          P_SEC, "1933, when the", ["1933, the", "1933 the", "1933; when the"],
          "“When the … played” is a dependent clause that can follow the main clause after a comma; the other "
          "choices create a comma splice, a run-on, or a fragment."),
        Q(FSS,
          blank("Walking along the riverbank at dawn, ___"),
          P_SEC,
          "the photographer noticed a heron standing perfectly still in the reeds.",
          ["a heron standing perfectly still in the reeds caught the photographer's eye.",
           "the reeds hid a heron that the photographer noticed standing perfectly still.",
           "the photographer's attention was caught by a heron standing perfectly still."],
          "The opening phrase describes the photographer, so “the photographer” must come right after the comma."),
        Q(BND,
          blank("The Great Barrier Reef is the largest coral reef system in the ___ it stretches for more than 2,000 "
                "kilometers along the coast of northeastern Australia."),
          P_SEC, "world;", ["world,", "world", "world, and it,"],
          "Two independent clauses are joined correctly with a semicolon."),
        Q(FSS,
          blank("The bridge that opened last year replaced one built in 1950. The new bridge's main span is nearly "
                "twice as long as ___ and was finished in half the time."),
          P_SEC, "the old bridge's", ["the old bridge", "the old bridges'", "the old bridges"],
          "A span must be compared with a span: the possessive “the old bridge's” stands for “the old bridge's main "
          "span.” There is only one old bridge, so the plural forms do not fit."),
        Q(FSS,
          blank("Each of the students in the photography course ___ required to submit a portfolio of twenty images "
                "at the end of the term."),
          P_SEC, "is", ["are", "were being", "have been"],
          "The subject is the singular pronoun “each,” so the singular verb <em>is</em> is required."),
        # ---- Expression of Ideas -------------------------------------------
        Q(TRN,
          blank("Many desert plants store water in thick, fleshy stems. ___ the saguaro cactus can swell to hold "
                "hundreds of liters of water after a heavy rain."),
          P_TRANSITION, "For example,", ["However,", "Instead,", "Even so,"],
          "The saguaro is an example of a desert plant that stores water in its stem."),
        Q(TRN,
          blank("The novelist wrote her first three books in English, the language she used at school. ___ she wrote "
                "her fourth book in Swahili, the language she had spoken at home as a child."),
          P_TRANSITION, "By contrast,", ["Likewise,", "Therefore,", "In addition,"],
          "Writing in Swahili contrasts with writing the first three books in English."),
        Q(TRN,
          blank("To reduce food waste, the school cafeteria began letting students choose their own portion sizes. "
                "___ the amount of food thrown away each week fell by almost half."),
          P_TRANSITION, "As a result,", ["In contrast,", "For example,", "Nevertheless,"],
          "The drop in waste followed from the change in policy."),
        Q(RS,
          notes(["Hedy Lamarr was a famous film actress in the 1930s and 1940s.",
                 "During World War II she co-invented a method for switching radio signals among many frequencies.",
                 "The method, called frequency hopping, made signals harder to jam.",
                 "Ideas related to frequency hopping were later used in wireless technologies such as Wi-Fi and "
                 "Bluetooth."],
                "The student wants to highlight a surprising contrast in Lamarr's career."),
          P_NOTES_Q,
          "Although she was best known as a film actress, Hedy Lamarr also co-invented a method of switching radio "
          "frequencies that made signals harder to jam.",
          ["Hedy Lamarr was a famous film actress in the 1930s and 1940s.",
           "Frequency hopping makes signals harder to jam by switching them among many frequencies.",
           "Wireless technologies such as Wi-Fi and Bluetooth use ideas related to frequency hopping."],
          "Only this choice sets her fame as an actress against her work as an inventor."),
        Q(RS,
          notes(["Researchers trained one group of honeybees to link the color blue with sugar water.",
                 "A second group was trained to link the color yellow with sugar water.",
                 "Both groups were then shown blue and yellow flowers that contained no sugar water.",
                 "Each group mostly visited the flowers of the color it had been trained on."],
                "The student wants to present the conclusion of the study."),
          P_NOTES_Q,
          "The study suggests that honeybees can learn to associate a particular color with food.",
          ["One group of honeybees was trained to link the color blue with sugar water.",
           "The researchers showed honeybees blue and yellow flowers that contained no sugar water.",
           "Two groups of honeybees were trained in a study about color."],
          "The other choices describe steps of the study; only this one states what the results show."),
        Q(RS,
          notes(["The Silk Road was a network of trade routes linking China with the Mediterranean region.",
                 "It was used for more than 1,500 years.",
                 "Merchants traded goods such as silk, spices, and glass along the routes.",
                 "Religions, technologies, and artistic styles also spread along the routes."],
                "The student wants to emphasize that the Silk Road spread more than goods."),
          P_NOTES_Q,
          "Besides goods such as silk and spices, religions, technologies, and artistic styles also traveled along "
          "the Silk Road.",
          ["The Silk Road, a network of trade routes, was used for more than 1,500 years.",
           "Merchants on the Silk Road traded silk, spices, and glass.",
           "The Silk Road linked China with the Mediterranean region."],
          "Only this choice points out that ideas and culture, not just goods, moved along the routes."),
    ]
