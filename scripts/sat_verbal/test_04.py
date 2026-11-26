"""Academor SAT Practice Test 4 — Reading and Writing."""

from sat_verbal.common import (
    BND, CID, COEQ, COET, CTC, FSS, INF, P_FINDING, P_FUNCTION, P_GRAPH, P_INFER, P_MAIN_IDEA,
    P_NOTES_Q, P_PURPOSE, P_SEC, P_STRUCTURE, P_TABLE, P_TRANSITION, P_WEAKEN, P_WIC, Q, RS, TRN, TSP,
    WIC, bar_chart, blank, grouped_bar_chart, line_chart, notes, p, table_image, texts, underline,
)


def module_1():
    fig_gardens = bar_chart(
        "Average Number of Bird Species Recorded per Garden",
        ["Lawn\nonly", "Lawn and\ntrees", "Native\nplants", "Native plants\nand water"],
        [6, 11, 19, 24],
        "Bird species", 30,
        "Bar graph of the average number of bird species per garden: lawn only 6, lawn and trees 11, native plants "
        "19, native plants and water 24",
        value_fmt="{:.0f}",
    )
    fig_park = line_chart(
        "Annual Visitors to Kestrel National Park, 2012–2022",
        [2012, 2014, 2016, 2018, 2020, 2022],
        [("Visitors", [210, 205, 215, 290, 180, 340])],
        "Thousands of visitors", (0, 400),
        "Line graph of park visitors: about 210 thousand from 2012 to 2016, 290 in 2018, 180 in 2020 and 340 in 2022",
        note=(2016, "Free shuttle\nbus begins"),
    )
    fig_calories = table_image(
        "Estimated Calories Burned in 30 Minutes of Activity",
        ["Activity", "Person weighing 60 kg", "Person weighing 80 kg"],
        [["Walking", "110", "145"], ["Cycling", "210", "280"], ["Swimming", "240", "320"]],
        "Table of calories burned in 30 minutes of walking, cycling and swimming by people weighing 60 and 80 kilograms",
        col_widths=[0.3, 0.35, 0.35],
    )
    return [
        Q(WIC,
          blank("The coach's instructions were ___: she told each player exactly where to stand, when to pass, and "
                "which opponent to guard."),
          P_WIC, "explicit", ["vague", "lenient", "reluctant"],
          "Telling players exactly what to do makes the instructions <em>explicit</em>."),
        Q(WIC,
          blank("The newly described species of frog is so ___ that it went unnoticed for decades: adults are smaller "
                "than a fingernail and blend almost perfectly into the leaf litter of the forest floor."),
          P_WIC, "inconspicuous", ["abundant", "aggressive", "vocal"],
          "A tiny, well-camouflaged frog that went unnoticed is <em>inconspicuous</em>."),
        Q(WIC,
          blank("Despite the ___ of the case, which involved thousands of pages of financial records, the jury reached "
                "a verdict in less than a day."),
          P_WIC, "complexity", ["simplicity", "brevity", "fairness"],
          "“Despite” sets a quick verdict against a difficult case: thousands of pages show its <em>complexity</em>."),
        Q(WIC,
          blank("Many early readers found the poet's work ___, but annotated editions have since made her references to "
                "little-known myths understandable to a wide audience."),
          P_WIC, "impenetrable", ["sentimental", "accessible", "predictable"],
          "The annotations made the poems understandable, implying that readers had found them hard to understand, "
          "or <em>impenetrable</em>."),
        Q(TSP,
          underline("Halley's Comet is named after the English astronomer Edmond Halley, even though he did not discover "
                    "it. ",
                    "Halley recognized that comets seen in 1531, 1607, and 1682 were the same object, and he predicted "
                    "that it would return in 1758.",
                    " When the comet reappeared as he had predicted, sixteen years after his death, it was named in his "
                    "honor."),
          P_FUNCTION,
          "It explains what Halley did that led to the comet being named after him.",
          ["It describes the method Halley used to discover the comet.",
           "It questions whether the sightings in 1531, 1607, and 1682 were accurate.",
           "It explains why the comet did not return as Halley predicted."],
          "The first sentence says Halley did not discover the comet; the underlined sentence explains his actual "
          "achievement, which earned him the honor."),
        Q(TSP,
          p("The following text is from a short story. Leila is helping her grandfather set up his first smartphone.")
          + p("“Tap it gently,” Leila said, “like you're waking a cat.” Her grandfather pressed the screen with his "
              "whole thumb, and the phone opened three apps at once. He stared at it, then at her, with the expression "
              "he usually saved for referees. Leila laughed so hard she had to sit down. After a moment he laughed "
              "too, and then he tried again—gently, this time, as if the phone might purr."),
          P_PURPOSE,
          "To portray a lighthearted moment in which a character learns a new skill with a relative's help",
          ["To show that a character refuses to learn how to use a new device",
           "To describe a disagreement between two characters about a gift",
           "To explain how a character first became interested in technology"],
          "The scene mixes Leila's coaching, the grandfather's mistake, shared laughter and his second, gentler try."),
        Q(CTC,
          texts("Several nutrition studies have found that adults who regularly eat breakfast weigh less, on average, "
                "than adults who skip it. On the basis of these findings, many health guides recommend eating "
                "breakfast as a way to control weight.",
                "Nutrition researcher Yuki Sato randomly assigned several hundred adults either to eat breakfast every "
                "day or to skip it for four months. At the end of the study, the two groups showed no meaningful "
                "difference in weight change. Sato notes that people who eat breakfast may differ from those who skip "
                "it in many other ways, such as their sleep and exercise habits."),
          "Based on the texts, how would Sato (Text 2) most likely respond to the recommendation described in Text 1?",
          "By cautioning that the findings it is based on show an association, not that breakfast itself affects "
          "weight",
          ["By agreeing that eating breakfast every day is an effective way to lose weight",
           "By arguing that skipping breakfast leads people to gain weight over four months",
           "By claiming that the studies in Text 1 measured weight inaccurately"],
          "Sato's randomized study found no effect, and she points to other differences between breakfast eaters and "
          "skippers that could explain the association."),
        Q(CID,
          p("Reef-building corals get much of their food from tiny algae that live inside their tissues and also give "
            "the corals much of their color. When water becomes unusually warm, the stressed corals expel these algae "
            "and turn white, an event known as bleaching. Bleached corals are not dead, and they can recover if "
            "temperatures return to normal quickly. If the heat lasts too long, however, the corals may starve."),
          P_MAIN_IDEA,
          "Unusually warm water can cause corals to lose the algae they depend on, which they may survive only if "
          "the heat does not last.",
          ["Corals turn white because the algae inside them die of old age.",
           "Bleached corals are already dead and cannot recover.",
           "Algae that live inside corals feed mainly on the corals' tissues."],
          "The text explains what bleaching is, what causes it, and when corals can recover."),
        Q(CID,
          p("In 1324 Mansa Musa, ruler of the Mali Empire, made a pilgrimage from West Africa to Mecca. He traveled "
            "with a large group of followers and a great quantity of gold. During a stay in Cairo, he and his followers "
            "spent and gave away so much gold that, according to writers of the time, the value of gold in the city "
            "fell and remained low for years afterward."),
          "According to the text, what happened in Cairo during Mansa Musa's visit?",
          "So much gold was spent and given away that its value in the city fell.",
          ["Mansa Musa traded gold for goods that he brought back to Mali.",
           "Writers of the time criticized Mansa Musa for traveling with so many followers.",
           "The price of gold rose because Mansa Musa bought large amounts of it."],
          "The text says the gold spent and given away lowered its value in Cairo for years."),
        Q(COET,
          p("Sociologist Priya Raman claims that people are more likely to recycle when recycling bins are placed "
            "right next to trash cans, so that recycling takes no extra effort."),
          P_FINDING,
          "In an office building, the amount of material recycled doubled after recycling bins were moved next to "
          "every trash can, while nothing else about the office changed.",
          ["Most people in a survey said they believe recycling is important.",
           "Recycling bins in the office building were emptied twice a week.",
           "People in the office building threw away more paper than plastic."],
          "Moving the bins beside the trash cans, with nothing else changing, directly tests Raman's claim."),
        Q(COEQ,
          p("A student is studying how garden design affects birds. The student notes that gardens with native plants "
            "attracted more bird species than lawns did and that adding a water source increased that number further: "
            "gardens with native plants had an average of ___"),
          P_GRAPH,
          "19 bird species, compared with 6 for lawn-only gardens and 24 for gardens with native plants and water.",
          ["11 bird species, compared with 6 for lawn-only gardens.",
           "24 bird species, compared with 19 for gardens with lawn and trees.",
           "6 bird species, the fewest of any type of garden."],
          "Only this choice compares native plants with lawns and shows the gain from adding water.",
          figure=fig_gardens),
        Q(COEQ,
          p("Officials at Kestrel National Park began a free shuttle bus in 2016. They claim that the shuttle helped "
            "increase the number of visitors, pointing out that ___"),
          P_GRAPH,
          "the park had about 210 thousand visitors a year before 2016 and about 290 thousand in 2018.",
          ["the park had about 180 thousand visitors in 2020.",
           "the number of visitors fell from 2012 to 2014.",
           "the park had more visitors in 2012 than in any later year shown."],
          "A jump after 2016 compared with the steady level before supports the officials' claim.",
          figure=fig_park),
        Q(COEQ,
          p("A fitness writer explains that heavier people burn more calories than lighter people do during the same "
            "activity. For example, in 30 minutes of swimming, ___"),
          P_TABLE,
          "a person weighing 80 kg burns about 320 calories, while a person weighing 60 kg burns about 240.",
          ["a person weighing 60 kg burns about 240 calories, more than while walking.",
           "a person weighing 80 kg burns about 280 calories, while a person weighing 60 kg burns about 210.",
           "a person weighing 60 kg burns about 320 calories, while a person weighing 80 kg burns about 240."],
          "Only this choice reports the swimming values correctly and compares the two weights.",
          figure=fig_calories),
        Q(INF,
          p("In a tropical forest, ecologist Daniel Ferreira found that seedlings of one tree species rarely survived "
            "when they sprouted near adult trees of the same species, but often survived near trees of other species. "
            "He also found that the soil around adult trees of the species contained fungi that attack its seedlings. "
            "These findings suggest that ___"),
          P_INFER,
          "harmful fungi near adult trees may prevent the species' seedlings from surviving close to their parents.",
          ["seedlings of the species grow better in shade than in sunlight.",
           "the fungi help adult trees of the species grow taller.",
           "trees of other species produce more seeds than this species does."],
          "Fungi that attack the seedlings are concentrated near adults, where seedlings rarely survive."),
        Q(FSS,
          blank("A series of storms that struck the coast last winter ___ damaged several historic lighthouses."),
          P_SEC, "has", ["have", "are", "were"],
          "The subject is the singular “series,” not “storms,” so the verb is <em>has</em>."),
        Q(BND,
          blank("The violinist practiced the difficult passage hundreds of ___ she could play it perfectly without "
                "looking at the music."),
          P_SEC, "times; eventually,", ["times, eventually,", "times eventually,", "times, eventually"],
          "Two independent clauses are joined with a semicolon; “eventually” then takes a comma."),
        Q(FSS,
          blank("The company recalled ___ newest model after customers reported that the battery overheated."),
          P_SEC, "its", ["their", "it's", "they're"],
          "“Company” is singular, and possession requires <em>its</em> (without an apostrophe)."),
        Q(BND,
          blank("Zora Neale Hurston trained as an anthropologist as well as a ___ she collected folktales in Florida "
                "and the Caribbean that later shaped her fiction."),
          P_SEC, "writer, and", ["writer and,", "writer,", "writer and"],
          "Two independent clauses joined by “and” need a comma before the conjunction."),
        Q(FSS,
          blank("The students' science fair ___ were displayed in the gym so that parents could see them."),
          P_SEC, "projects", ["project's", "projects'", "project"],
          "The sentence needs a plural noun for “were” and “them”; “students'” already shows possession."),
        Q(BND,
          blank("The village is reachable by only one ___ narrow gravel track that floods every spring."),
          P_SEC, "route: a", ["route, it is a", "route; a", "route a"],
          "A colon introduces the description of the one route."),
        Q(FSS,
          blank("When the volcano erupted in 1980, ash ___ as far away as cities more than 400 kilometers to the east."),
          P_SEC, "fell", ["falls", "has fallen", "will fall"],
          "The eruption is in the past (1980), so the simple past <em>fell</em> is needed."),
        Q(TRN,
          blank("Some wildflowers bloom only for a few days each year. ___ the desert lily may stay underground for "
                "years, sending up flowers only after unusually heavy rain."),
          P_TRANSITION, "In fact,", ["However,", "Consequently,", "On the other hand,"],
          "The desert lily is an even more extreme case of brief flowering, which “In fact” emphasizes."),
        Q(TRN,
          blank("The research team spent the morning collecting water samples from the river. ___ a second team "
                "measured the river's speed at several points downstream."),
          P_TRANSITION, "Meanwhile,", ["Therefore,", "In contrast,", "For example,"],
          "The second team worked at the same time as the first."),
        Q(TRN,
          blank("The library's new hours were designed to serve people who work during the day. ___ the library now "
                "stays open until 9:00 p.m. on weekdays and opens early on Saturdays."),
          P_TRANSITION, "Specifically,", ["However,", "Instead,", "Similarly,"],
          "The sentence gives the specific new hours that the first sentence mentions in general terms."),
        Q(RS,
          notes(["Machu Picchu is a fifteenth-century Inca site in the Andes Mountains of Peru.",
                 "It was built on a ridge about 2,400 meters above sea level.",
                 "Its buildings were made of stones cut to fit together without mortar.",
                 "It was named a UNESCO World Heritage Site in 1983."],
                "The student wants to emphasize the skill of Machu Picchu's builders."),
          P_NOTES_Q,
          "The builders of Machu Picchu cut its stones so precisely that they fit together without mortar.",
          ["Machu Picchu was named a UNESCO World Heritage Site in 1983.",
           "Machu Picchu is a fifteenth-century Inca site in Peru.",
           "Machu Picchu was built on a ridge about 2,400 meters above sea level."],
          "Precisely cut stones without mortar show the builders' skill."),
        Q(RS,
          notes(["Sea otters often float on their backs while eating.",
                 "They use rocks to crack open the shells of clams and sea urchins.",
                 "Sea otters eat large numbers of sea urchins.",
                 "Where sea otters are absent, sea urchins can multiply and destroy kelp forests."],
                "The student wants to explain why sea otters are important to kelp forests."),
          P_NOTES_Q,
          "By eating sea urchins, sea otters keep urchin numbers down and help protect kelp forests.",
          ["Sea otters use rocks to crack open the shells of clams and sea urchins.",
           "Sea otters often float on their backs while eating.",
           "Sea otters eat clams and sea urchins."],
          "Only this choice connects otters, urchins and kelp."),
        Q(RS,
          notes(["Katherine Johnson was a mathematician who worked for NASA.",
                 "She calculated flight paths for early American spaceflights.",
                 "In 1962 astronaut John Glenn asked that she personally check the computer's calculations before his "
                 "orbital flight.",
                 "She received the Presidential Medal of Freedom in 2015."],
                "The student wants to show how much astronauts trusted Johnson's work."),
          P_NOTES_Q,
          "Before his 1962 orbital flight, John Glenn asked that Katherine Johnson personally check the computer's "
          "calculations.",
          ["Katherine Johnson received the Presidential Medal of Freedom in 2015.",
           "Katherine Johnson was a mathematician who worked for NASA.",
           "Katherine Johnson calculated flight paths for early American spaceflights."],
          "Glenn's request shows an astronaut's trust in her work."),
    ]


def module_2():
    fig_bikes = grouped_bar_chart(
        "Weekday Bicycle Trips on Three Streets Before and After Protected Lanes",
        ["Elm Street", "Mill Road", "Park Avenue"],
        [("Before", [420, 310, 520]), ("After", [880, 330, 1040])],
        "Bicycle trips per day", 1200,
        "Grouped bar graph of daily bicycle trips before and after protected lanes on three streets",
    )
    fig_ice = line_chart(
        "Days per Year That Lake Ostra Was Covered by Ice",
        [1900, 1920, 1940, 1960, 1980, 2000, 2020],
        [("Days of ice cover", [118, 116, 112, 109, 101, 92, 84])],
        "Days", (60, 130),
        "Line graph of the number of days Lake Ostra was frozen, falling from 118 in 1900 to 84 in 2020",
    )
    fig_trial = table_image(
        "Results of a Trial of Two Pain Relievers",
        ["Group", "Patients", "Reported less pain after 1 hour"],
        [["Drug A", "200", "62%"], ["Drug B", "200", "64%"], ["Placebo", "200", "31%"]],
        "Table of the share of patients reporting less pain after one hour for two drugs and a placebo",
        col_widths=[0.3, 0.25, 0.45],
    )
    return [
        Q(WIC,
          blank("The biography is ___ in its detail: the author consulted thousands of letters and diaries and seems to "
                "record nearly every dinner her subject ever attended."),
          P_WIC, "exhaustive", ["cursory", "fictional", "ambiguous"],
          "Recording nearly every detail from thousands of sources makes the biography <em>exhaustive</em>."),
        Q(WIC,
          blank("The mayor's speech was intended to ___ residents' fears about the new factory, so she emphasized the "
                "strict safety standards it would have to meet."),
          P_WIC, "allay", ["provoke", "document", "ignore"],
          "Stressing safety standards is meant to calm, or <em>allay</em>, fears."),
        Q(WIC,
          blank("Although the two theories are often presented as rivals, they are in fact ___: one explains how "
                "the behavior develops in an individual, and the other explains why it evolved in the species."),
          P_WIC, "complementary", ["contradictory", "identical", "outdated"],
          "Theories that explain different parts of the same behavior fit together: they are <em>complementary</em>."),
        Q(WIC,
          blank("The dancer's movements appeared ___, but she later explained that each seemingly spontaneous gesture "
                "had been rehearsed for months."),
          P_WIC, "improvised", ["mechanical", "clumsy", "borrowed"],
          "“Seemingly spontaneous” and “but … rehearsed” show the movements looked <em>improvised</em>."),
        Q(TSP,
          p("Many people picture a scientific discovery as a single moment of insight. The development of the "
            "lithium-ion battery tells a different story. In the 1970s, chemist M. Stanley Whittingham built a battery "
            "that worked but was prone to catching fire. In 1980 John Goodenough found a better material for one end "
            "of the battery, and in 1985 Akira Yoshino built the first version that could be made safely in large "
            "numbers. The three shared the 2019 Nobel Prize in Chemistry."),
          P_STRUCTURE,
          "It challenges a common view of discovery and then uses the history of an invention to illustrate the "
          "challenge.",
          ["It describes a battery that failed and then explains why the problem was never solved.",
           "It argues that Whittingham deserved most of the credit for the lithium-ion battery.",
           "It compares the lithium-ion battery with other batteries and concludes that it is the most useful."],
          "The text questions the single-moment view and then traces a discovery built up by three scientists over "
          "years."),
        Q(TSP,
          underline("Many large bridges of the early twentieth century were designed almost entirely by engineers. ",
                    "The Golden Gate Bridge was different: its color, a reddish orange called “International Orange,” "
                    "was chosen by consulting architect Irving Morrow, who thought it would blend with the surrounding "
                    "hills and stand out in fog.",
                    " The bridge, completed in 1937, is now one of the most photographed structures in the world."),
          P_FUNCTION,
          "It gives an example of an architect's influence on a bridge's design, in contrast to the practice described "
          "in the first sentence.",
          ["It explains why most bridges of the early twentieth century were painted gray.",
           "It describes how the Golden Gate Bridge was built more quickly than other bridges.",
           "It questions whether the color of the Golden Gate Bridge was a good choice."],
          "The underlined sentence shows an architect choosing the color, unlike bridges designed almost entirely by "
          "engineers."),
        Q(CTC,
          texts("Some biologists have argued that animals play mainly to practice skills they will need as adults. "
                "Young cats that pounce on one another, for example, may be rehearsing how to catch prey.",
                "Animal behaviorist Nora Ekberg observed young rats and found that they played most when they had "
                "recently been separated from their companions, regardless of whether the play involved adult skills. "
                "Ekberg proposes that play may serve partly to build and repair social bonds."),
          "Based on the texts, how would Ekberg (Text 2) most likely respond to the biologists' view in Text 1?",
          "By suggesting that play may have a social purpose in addition to helping animals practice skills",
          ["By agreeing that play is mainly a way for young animals to rehearse catching prey",
           "By arguing that young rats rarely play when they have companions nearby",
           "By claiming that cats play more than rats because they hunt more"],
          "Ekberg's findings point to bonding as another reason for play, without denying skill practice."),
        Q(CID,
          p("The following text is from a short story. Esperanza has been asked to judge a pie contest at the county "
            "fair.")
          + p("She had expected the task to be easy. But each pie came with a baker standing nearby, pretending not to "
              "watch her face. Mrs. Lund's crust was too pale, and Esperanza saw Mrs. Lund see her notice it. The "
              "Harper twins had made a cherry pie so tart that her eyes watered, and they looked so hopeful that she "
              "took a second bite to be polite. By the ninth pie she understood that she was judging not only pies "
              "but people she would see at the grocery store every week for the rest of her life."),
          P_MAIN_IDEA,
          "Esperanza realizes that judging the contest is harder than she expected because of her connection to the "
          "bakers.",
          ["Esperanza decides that Mrs. Lund's pie is the best in the contest.",
           "Esperanza dislikes cherry pie and refuses to finish the Harper twins' entry.",
           "Esperanza is new to the county and does not know any of the bakers."],
          "The watchful bakers, whom she will keep seeing in town, make the judging difficult."),
        Q(CID,
          p("Earth's magnetic field has reversed its direction many times, so that a compass that points north today "
            "would have pointed south during some periods in the past. Geologists know this because when lava cools, "
            "magnetic minerals in it line up with the field at that time and are then locked in place. By measuring the "
            "direction of these minerals in rock layers of different ages, researchers have built a record of "
            "reversals going back millions of years."),
          P_MAIN_IDEA,
          "Cooled lava preserves the direction of Earth's magnetic field, allowing geologists to trace past reversals "
          "of the field.",
          ["Compasses were invented to help geologists measure magnetic reversals.",
           "Earth's magnetic field has always pointed in the same direction.",
           "Lava cools more quickly during magnetic reversals than at other times."],
          "The text explains that the field has reversed and how rocks record those reversals."),
        Q(COET,
          p("Psychologist Anders Lund claims that people tend to remember the end of an experience more than its "
            "middle when they judge how pleasant the experience was as a whole."),
          P_FINDING,
          "Participants rated a long concert that ended with their favorite song as more enjoyable than a shorter "
          "concert with the same songs that ended with a song they disliked.",
          ["Participants who attended concerts regularly said that they enjoyed live music more than recordings.",
           "Participants could name more songs from the beginning of a concert than from the middle.",
           "Participants rated outdoor concerts as more enjoyable than indoor concerts."],
          "The longer concert with the better ending was rated higher, showing that the ending shaped the overall "
          "judgment."),
        Q(COEQ,
          p("A city added protected bicycle lanes to three streets. A transportation analyst notes that the lanes were "
            "followed by large increases in cycling on two streets but had almost no effect on the third: on Mill "
            "Road, ___"),
          P_GRAPH,
          "daily bicycle trips rose only from about 310 to about 330.",
          ["daily bicycle trips rose from about 420 to about 880.",
           "daily bicycle trips rose from about 520 to about 1,040.",
           "daily bicycle trips fell from about 330 to about 310."],
          "Mill Road shows the small change the analyst describes.",
          figure=fig_bikes),
        Q(COEQ,
          p("Records of when Lake Ostra froze and thawed have been kept since 1900. A climate researcher notes that the "
            "lake has been losing ice cover faster in recent decades than it did early in the twentieth century: the "
            "number of days of ice cover ___"),
          P_GRAPH,
          "fell by only about 6 days from 1900 to 1940 but by about 25 days from 1960 to 2020.",
          ["fell from about 118 in 1900 to about 84 in 2020.",
           "stayed about the same from 1960 to 2020.",
           "rose by about 6 days from 1900 to 1940."],
          "Comparing a small early decline with a large later decline supports the claim of faster loss.",
          figure=fig_ice),
        Q(COEQ,
          p("Researchers tested two pain relievers against a placebo, a pill with no medicine in it. They concluded "
            "that both drugs were effective but that neither was clearly better than the other: ___"),
          P_TABLE,
          "62% of patients taking Drug A and 64% of patients taking Drug B reported less pain, compared with 31% of "
          "patients taking the placebo.",
          ["64% of patients taking Drug B reported less pain after one hour.",
           "31% of patients taking the placebo reported less pain after one hour.",
           "Drug B helped twice as many patients as Drug A did."],
          "Both drugs were well above the placebo and close to each other, which matches both parts of the conclusion.",
          figure=fig_trial),
        Q(INF,
          p("Some species of birds lay their eggs in the nests of other birds, which then raise the chicks as their own. "
            "Biologist Ruth Okafor found that a host species living in areas where such birds are common was much more "
            "likely to reject eggs that looked different from its own than was the same species living in areas where "
            "such birds are absent. This finding suggests that ___"),
          P_INFER,
          "the host species may become better at recognizing foreign eggs where the threat of having to raise another "
          "bird's chicks is greater.",
          ["birds that lay eggs in other nests prefer areas where the host species is rare.",
           "the host species lays fewer eggs in areas where such birds are common.",
           "foreign eggs are always larger than the eggs of the host species."],
          "Rejection is stronger where egg-laying intruders are common, suggesting the hosts' defense matches the "
          "threat."),
        Q(BND,
          blank("Toni Morrison's novel <em>Beloved</em>, published in ___ won the Pulitzer Prize for Fiction the "
                "following year."),
          P_SEC, "1987,", ["1987", "1987;", "1987:"],
          "The phrase “published in 1987” is set off by commas: one before it and one after it."),
        Q(FSS,
          blank("The measurements from the two satellites, which orbit Earth at different heights, ___ to be combined "
                "before the map can be completed."),
          P_SEC, "need", ["needs", "is needing", "has needed"],
          "The subject is the plural “measurements,” not “satellites” or “heights,” so the verb is <em>need</em>."),
        Q(BND,
          blank("The trail climbs steeply for the first two ___ then it levels off and follows a ridge to the summit."),
          P_SEC, "kilometers;", ["kilometers,", "kilometers", "kilometers, and, then"],
          "Two independent clauses are joined with a semicolon; a comma alone would be a comma splice."),
        Q(FSS,
          blank("Raised in a family of musicians, ___"),
          P_SEC,
          "the pianist began performing in public at the age of six.",
          ["public performances began for the pianist at the age of six.",
           "the age of six was when the pianist began performing in public.",
           "performing in public was something the pianist began at the age of six."],
          "The pianist, not the performances or the age, was raised in a family of musicians."),
        Q(BND,
          blank("The coastal town is famous for two ___ the lighthouse built in 1871 and the annual kite festival."),
          P_SEC, "things:", ["things;", "things, they are", "things"],
          "A colon introduces the two things the town is famous for."),
        Q(FSS,
          blank("The museum's two newest galleries are larger and better lit than ___"),
          P_SEC, "the older ones.", ["the older one's.", "the older ones'.", "the older ones' galleries."],
          "The galleries are compared with other galleries; no possessive is needed."),
        Q(FSS,
          blank("If the committee had received the proposal earlier, it ___ more time to consider the budget."),
          P_SEC, "would have had", ["will have", "has had", "would of had"],
          "A past condition contrary to fact (“had received”) pairs with <em>would have had</em>."),
        Q(TRN,
          blank("For years, scientists assumed that the deep ocean floor was nearly lifeless. ___ the discovery of "
                "hydrothermal vents in 1977 revealed entire communities of animals living in complete darkness."),
          P_TRANSITION, "However,", ["Similarly,", "Therefore,", "For example,"],
          "The discovery overturned the earlier assumption."),
        Q(TRN,
          blank("The two cities are about the same size. ___ one has three times as many public parks as the other."),
          P_TRANSITION, "Even so,", ["As a result,", "Likewise,", "In other words,"],
          "Despite their similar size, the cities differ greatly in parks."),
        Q(TRN,
          blank("The researchers first measured the height of each plant. ___ they dried the plants and weighed them to "
                "find their total mass."),
          P_TRANSITION, "Next,", ["However,", "In contrast,", "For instance,"],
          "The sentence describes the following step in a sequence."),
        Q(RS,
          notes(["Glass frogs live in the rainforests of Central and South America.",
                 "Their skin is so transparent on the underside that their organs can be seen.",
                 "When they sleep, glass frogs store most of their red blood cells in their liver.",
                 "This makes their bodies even more transparent and may help hide them from predators."],
                "The student wants to explain how glass frogs may avoid predators while sleeping."),
          P_NOTES_Q,
          "While sleeping, glass frogs store most of their red blood cells in their liver, making their bodies more "
          "transparent and possibly harder for predators to see.",
          ["Glass frogs live in the rainforests of Central and South America.",
           "The skin on the underside of glass frogs is so transparent that their organs can be seen.",
           "Glass frogs store red blood cells in their liver."],
          "Only this choice links the blood-storage behavior to hiding from predators."),
        Q(RS,
          notes(["The first modern Olympic Games were held in Athens in 1896.",
                 "About 240 athletes from 14 countries took part.",
                 "The 2020 Summer Olympics, held in 2021 in Tokyo, included more than 11,000 athletes.",
                 "Athletes from about 200 national teams competed in Tokyo."],
                "The student wants to show how much the Olympic Games have grown."),
          P_NOTES_Q,
          "About 240 athletes competed in the first modern Olympic Games in 1896, while more than 11,000 competed in "
          "the Tokyo Games.",
          ["The first modern Olympic Games were held in Athens in 1896.",
           "The 2020 Summer Olympics were held in 2021 in Tokyo.",
           "Athletes from about 200 national teams competed in Tokyo."],
          "Comparing the numbers of athletes shows the growth."),
        Q(RS,
          notes(["Murasaki Shikibu was a writer at the Japanese imperial court around the year 1000.",
                 "She wrote <em>The Tale of Genji</em>.",
                 "<em>The Tale of Genji</em> follows the life and relationships of a fictional prince.",
                 "Many scholars consider it one of the world's earliest novels."],
                "The student wants to emphasize the historical importance of <em>The Tale of Genji</em>."),
          P_NOTES_Q,
          "<em>The Tale of Genji</em>, written by Murasaki Shikibu around the year 1000, is considered by many "
          "scholars to be one of the world's earliest novels.",
          ["<em>The Tale of Genji</em> follows the life and relationships of a fictional prince.",
           "Murasaki Shikibu was a writer at the Japanese imperial court.",
           "Murasaki Shikibu wrote <em>The Tale of Genji</em>, which is about a prince."],
          "Only this choice states why the work is historically important."),
    ]
