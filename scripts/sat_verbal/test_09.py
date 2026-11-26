"""Academor SAT Practice Test 9 — Reading and Writing."""

from sat_verbal.common import (
    BND, CID, COEQ, COET, CTC, FSS, INF, P_FINDING, P_FUNCTION, P_GRAPH, P_INFER, P_MAIN_IDEA,
    P_NOTES_Q, P_PURPOSE, P_SEC, P_STRUCTURE, P_TABLE, P_TRANSITION, P_WEAKEN, P_WIC, Q, RS, TRN, TSP,
    WIC, bar_chart, blank, grouped_bar_chart, line_chart, notes, p, table_image, texts, underline,
)


def module_1():
    fig_roofs = bar_chart(
        "Average Summer Roof Surface Temperature by Roof Type",
        ["Dark\nshingles", "Light\nshingles", "White\ncoating", "Plants\n(green roof)"],
        [68, 51, 39, 33],
        "Temperature (°C)", 75,
        "Bar graph of summer roof temperatures: dark shingles 68, light shingles 51, white coating 39 and green roof 33 "
        "degrees Celsius",
        value_fmt="{:.0f}°",
    )
    fig_museum = line_chart(
        "Visitors to the Corran Science Museum by Age Group",
        [2015, 2017, 2019, 2021, 2023],
        [("Children under 12", [62, 64, 66, 70, 73]), ("Teenagers 13–18", [18, 17, 19, 34, 45])],
        "Thousands of visitors", (0, 80),
        "Line graph of museum visitors: children rising slowly from 62 to 73 thousand and teenagers rising from about "
        "18 thousand to 45 thousand after 2019",
        note=(2019, "Teen science\nnights begin"),
    )
    fig_rice = table_image(
        "Rice Yield and Water Use Under Two Irrigation Methods",
        ["Method", "Yield (tons per hectare)", "Water used (thousand cubic meters per hectare)"],
        [["Continuous flooding", "6.1", "14.0"], ["Alternate wetting and drying", "6.0", "10.5"]],
        "Table comparing rice yield and water use under continuous flooding and alternate wetting and drying",
        col_widths=[0.36, 0.28, 0.36],
    )
    return [
        Q(WIC,
          blank("The two scientists' accounts of the experiment were ___: they described the same procedure and the "
                "same results in almost exactly the same words."),
          P_WIC, "consistent", ["contradictory", "incomplete", "exaggerated"],
          "Accounts that match almost word for word are <em>consistent</em>."),
        Q(WIC,
          blank("Although the storm was expected to be ___, it weakened over the ocean and brought only light rain to "
                "the coast."),
          P_WIC, "severe", ["mild", "brief", "distant"],
          "“Although” contrasts the expectation with the weak storm that arrived, so it was expected to be "
          "<em>severe</em>."),
        Q(WIC,
          blank("The council's decision to close the library was widely ___: hundreds of residents signed petitions, "
                "and several spoke against it at a public meeting."),
          P_WIC, "opposed", ["praised", "ignored", "anticipated"],
          "Petitions and speeches against the decision show it was <em>opposed</em>."),
        Q(WIC,
          blank("The novelist is known for her ___ descriptions of ordinary objects—a chipped cup, a worn glove—which "
                "she renders in such detail that they seem to carry entire histories."),
          P_WIC, "meticulous", ["hasty", "abstract", "repetitive"],
          "Rendering small objects in great detail requires <em>meticulous</em> description."),
        Q(TSP,
          underline("The Antikythera mechanism, found in a shipwreck off a Greek island in 1901, is a bronze device more "
                    "than 2,000 years old. ",
                    "X-ray studies have revealed that its interlocking gears could predict the positions of the Sun and "
                    "Moon and the dates of eclipses.",
                    " Because of this, many researchers describe it as one of the earliest known analog computers."),
          P_FUNCTION,
          "It explains what the device could do, which supports the description in the final sentence.",
          ["It describes how the shipwreck was discovered.",
           "It argues that the device was made more recently than once thought.",
           "It compares the device with modern computers."],
          "The gears' ability to predict astronomical events is the reason the device is called an early computer."),
        Q(TSP,
          p("The following text is from a short story. Yusuf is learning to swim as an adult.")
          + p("The instructor told him to let the water hold him up. Yusuf did not believe the water would do any such "
              "thing; for forty years it had seemed to him like something that wanted to pull him down. Still, he lay "
              "back, his arms stiff, his eyes on the ceiling lights. For a few seconds nothing happened. Then he felt it—"
              "the slow, steady push from beneath—and he laughed out loud, and his ears filled with water, and he did "
              "not mind."),
          P_PURPOSE,
          "To capture the moment when a character's long-held fear gives way to delight",
          ["To explain why a character never learned to swim as a child",
           "To describe a disagreement between a character and his instructor",
           "To show that a character gives up on learning to swim"],
          "Yusuf's distrust of the water turns into laughter when he finally floats."),
        Q(CTC,
          texts("For many years, ornithologists assumed that birds' songs were mainly learned by males, since in many "
                "well-studied species from Europe and North America only the males sing.",
                "Biologist Karan Mehta and colleagues reviewed records of more than 1,000 songbird species worldwide "
                "and found that females sing in about two-thirds of them, especially in tropical species. Mehta argues "
                "that the earlier assumption reflected where researchers happened to work rather than how most "
                "songbirds actually behave."),
          "Based on the texts, how would Mehta (Text 2) most likely respond to the assumption described in Text 1?",
          "By arguing that it was based on a limited set of species that does not represent songbirds as a whole",
          ["By agreeing that female songbirds rarely sing in most parts of the world",
           "By claiming that birds in Europe and North America sing more than tropical birds",
           "By suggesting that only tropical male birds learn their songs"],
          "Mehta finds widespread female song and attributes the old assumption to the regions studied."),
        Q(CID,
          p("Many people think of glaciers as frozen and still, but glaciers move. The weight of the ice causes it to "
            "slowly deform and flow downhill, and meltwater at the base can help a glacier slide over the rock beneath "
            "it. Most glaciers move only a few centimeters to a few meters each day, but some, known as surging "
            "glaciers, can suddenly speed up and advance many times faster for months at a time."),
          P_MAIN_IDEA,
          "Glaciers move, usually slowly, through the flow of their ice and sliding at their base, and some can "
          "occasionally speed up dramatically.",
          ["Glaciers remain frozen in place unless they begin to melt completely.",
           "Surging glaciers move more slowly than other glaciers.",
           "Meltwater prevents glaciers from moving downhill."],
          "The text explains how glaciers move and notes that some surge."),
        Q(CID,
          p("In 1928 the bacteriologist Alexander Fleming returned from a vacation to find that mold had contaminated one "
            "of his dishes of bacteria. Around the mold, the bacteria had been killed. Fleming identified the substance "
            "the mold produced and named it penicillin. However, it was not until the early 1940s that other "
            "researchers, including Howard Florey and Ernst Chain, found ways to produce penicillin in large enough "
            "amounts to treat patients."),
          "According to the text, what was true about penicillin in the years immediately after Fleming's discovery?",
          "It could not yet be produced in large enough amounts to treat patients.",
          ["It was already being used to treat thousands of patients.",
           "Fleming had found that it killed mold.",
           "Florey and Chain had already discovered it."],
          "The text says large-scale production for patients came only in the early 1940s."),
        Q(COET,
          p("A team of urban planners claims that adding trees to a street reduces the speed at which drivers travel "
            "on it, because the trees make the street feel narrower."),
          P_FINDING,
          "On streets where trees were planted along the curb, average driving speeds fell, while speeds on similar "
          "streets without new trees did not change.",
          ["Residents of streets with trees reported enjoying their walks more.",
           "Trees planted along streets need regular watering during their first two years.",
           "Most drivers said that they prefer streets with trees."],
          "Speeds fell only where trees were planted, directly supporting the claim."),
        Q(COEQ,
          p("A researcher studying ways to keep buildings cool measured roof temperatures on summer afternoons. The "
            "researcher concluded that covering a roof with plants kept it even cooler than painting it with a white "
            "coating: ___"),
          P_GRAPH,
          "green roofs averaged about 33°C, compared with about 39°C for roofs with a white coating.",
          ["roofs with dark shingles averaged about 68°C.",
           "roofs with a white coating averaged about 33°C, compared with about 39°C for green roofs.",
           "roofs with light shingles averaged about 51°C, compared with about 68°C for dark shingles."],
          "Only this choice compares green roofs with white-coated roofs correctly.",
          figure=fig_roofs),
        Q(COEQ,
          p("In 2019 the Corran Science Museum began holding evening events designed for teenagers. Museum staff argue "
            "that the events attracted a new audience, noting that the number of teenage visitors ___"),
          P_GRAPH,
          "stayed near 18 thousand from 2015 to 2019 but rose to about 45 thousand by 2023.",
          ["was lower than the number of child visitors in every year shown.",
           "rose from about 62 thousand to about 73 thousand.",
           "fell slightly between 2015 and 2017."],
          "A flat count before 2019 and a sharp rise afterward supports the staff's argument.",
          figure=fig_museum),
        Q(COEQ,
          p("Rice is usually grown in fields that are kept flooded. In a method called alternate wetting and drying, "
            "farmers let fields dry out periodically. Researchers concluded that this method saves a large amount of "
            "water with almost no loss in yield: ___"),
          P_TABLE,
          "it used about 10.5 thousand cubic meters of water per hectare instead of 14.0 thousand, while yield fell "
          "only from 6.1 to 6.0 tons per hectare.",
          ["continuous flooding produced a yield of 6.1 tons per hectare.",
           "both methods produced yields of more than 6 tons per hectare.",
           "it used more water than continuous flooding but produced a higher yield."],
          "Only this choice shows both the water savings and the nearly equal yield.",
          figure=fig_rice),
        Q(INF,
          p("Some species of ants farm fungi, growing them in underground gardens and feeding them pieces of leaves. "
            "Biologist Teresa Alves found that the ants' bodies carry bacteria that produce chemicals harmful to a mold "
            "that attacks the fungus gardens. When she removed these bacteria, the mold spread through the gardens much "
            "more quickly. These findings suggest that ___"),
          P_INFER,
          "the bacteria may help the ants protect their fungus gardens from the mold.",
          ["the ants feed the bacteria to the fungus.",
           "the mold is harmless to the fungus gardens.",
           "the ants grow fungus only when bacteria are absent."],
          "Removing the bacteria let the mold spread, which suggests the bacteria protect the gardens."),
        Q(FSS,
          blank("The jury, after listening to three weeks of testimony, ___ ready to deliver its verdict."),
          P_SEC, "is", ["are", "were", "have been"],
          "“The jury” acts as one unit here (“its verdict”), so the singular <em>is</em> is required."),
        Q(BND,
          blank("Before the invention of refrigerators, people kept food cold with blocks of ice cut from frozen ___ "
                "the ice was stored in insulated buildings called icehouses."),
          P_SEC, "lakes;", ["lakes,", "lakes", "lakes, and, the"],
          "Two independent clauses are joined with a semicolon."),
        Q(FSS,
          blank("The teacher asked each student to bring ___ own calculator to the exam."),
          P_SEC, "his or her", ["their's", "there", "they're"],
          "The singular “each student” calls for a singular possessive; the other choices are not possessive "
          "pronouns at all."),
        Q(BND,
          blank("The artist Yayoi Kusama, famous for her polka dots and mirrored rooms, has said that her work ___ from "
                "hallucinations she experienced as a child."),
          P_SEC, "grew", ["grew,", "grew;", "grew:"],
          "No punctuation belongs between the verb “grew” and the phrase that completes it."),
        Q(FSS,
          blank("Neither the poet's letters nor her diary ___ ever been published."),
          P_SEC, "has", ["have", "are", "were"],
          "With “neither … nor,” the verb agrees with the nearer subject, the singular “diary.”"),
        Q(BND,
          blank("The guide offered the hikers a ___ they could take the steep trail to the summit or the gentler path "
                "around the lake."),
          P_SEC, "choice:", ["choice;", "choice,", "choice"],
          "A colon introduces the explanation of the choice."),
        Q(FSS,
          blank("Built in the twelfth century, ___"),
          P_SEC,
          "the cathedral took more than a hundred years to complete.",
          ["it took more than a hundred years to complete the cathedral.",
           "more than a hundred years were needed to complete the cathedral.",
           "completing the cathedral took more than a hundred years."],
          "The cathedral was built, so it must follow the opening phrase."),
        Q(TRN,
          blank("The first commercial airplane flights were expensive and uncomfortable. ___ only wealthy travelers "
                "could afford to fly."),
          P_TRANSITION, "Consequently,", ["However,", "Likewise,", "For example,"],
          "The high cost led to only wealthy travelers flying."),
        Q(TRN,
          blank("Many people assume that sharks must keep swimming to breathe. ___ some sharks, such as the nurse shark, "
                "can rest on the sea floor and pump water over their gills."),
          P_TRANSITION, "In fact,", ["Therefore,", "Similarly,", "In addition,"],
          "The nurse shark corrects the common assumption."),
        Q(TRN,
          blank("The museum's paintings are arranged by period, from the oldest to the most recent. ___ visitors can "
                "follow the development of the region's art from room to room."),
          P_TRANSITION, "In this way,", ["Nevertheless,", "In contrast,", "Otherwise,"],
          "The arrangement allows visitors to follow the development of the art."),
        Q(RS,
          notes(["The Okavango Delta is in Botswana.",
                 "It forms where the Okavango River spreads out into the Kalahari Desert instead of flowing to the sea.",
                 "Seasonal floods turn the dry land into a wetland each year.",
                 "The delta supports large populations of elephants, hippos, and birds."],
                "The student wants to explain what makes the Okavango Delta unusual."),
          P_NOTES_Q,
          "Instead of flowing to the sea, the Okavango River spreads into the Kalahari Desert, where seasonal floods "
          "create a wetland each year.",
          ["The Okavango Delta is in Botswana.",
           "The Okavango Delta supports large populations of elephants, hippos, and birds.",
           "The Okavango Delta is home to elephants."],
          "Only this choice explains the delta's unusual formation."),
        Q(RS,
          notes(["A study tested whether people walk faster in larger cities.",
                 "Researchers timed pedestrians walking 18 meters on a sidewalk in cities around the world.",
                 "Pedestrians in larger cities generally walked faster.",
                 "The fastest average walking speeds were recorded in some of the world's largest cities."],
                "The student wants to present the study's general finding."),
          P_NOTES_Q,
          "The study found that people in larger cities generally walk faster than people in smaller ones.",
          ["Researchers timed pedestrians walking 18 meters on a sidewalk.",
           "The study took place in cities around the world.",
           "A study tested whether people walk faster in larger cities."],
          "Only this choice states the general finding."),
        Q(RS,
          notes(["Lise Meitner was an Austrian physicist born in 1878.",
                 "In 1938 she and her nephew Otto Frisch explained how uranium nuclei split, a process they named "
                 "nuclear fission.",
                 "Her longtime colleague Otto Hahn received the 1944 Nobel Prize in Chemistry for the discovery of "
                 "fission.",
                 "Meitner did not share the prize."],
                "The student wants to emphasize that Meitner's role in the discovery was not recognized by the Nobel "
                "committee."),
          P_NOTES_Q,
          "Although Lise Meitner helped explain nuclear fission, only her colleague Otto Hahn received the Nobel Prize "
          "for its discovery.",
          ["Lise Meitner was an Austrian physicist born in 1878.",
           "In 1938 Meitner and Otto Frisch named the process nuclear fission.",
           "Otto Hahn received the 1944 Nobel Prize in Chemistry."],
          "Only this choice contrasts her role with the prize going to Hahn alone."),
    ]


def module_2():
    fig_waste = grouped_bar_chart(
        "Household Waste Sent to Landfill per Week",
        ["Ashby", "Brill", "Corley"],
        [("Before compost pickup", [14.2, 12.8, 13.5]), ("After compost pickup", [9.1, 12.4, 8.7])],
        "Kilograms per household", 16,
        "Grouped bar graph of weekly landfill waste per household before and after compost pickup in three towns",
    )
    fig_fish = line_chart(
        "Average Length of Cod Caught in the Northern Fishery",
        [1970, 1980, 1990, 2000, 2010, 2020],
        [("Average length", [82, 78, 71, 64, 60, 58])],
        "Length (centimeters)", (40, 90),
        "Line graph of the average length of cod caught falling from 82 centimeters in 1970 to 58 centimeters in 2020",
    )
    fig_noise = table_image(
        "Average Test Scores in Classrooms with Different Noise Levels",
        ["Noise level", "Reading", "Math"],
        [["Quiet (below 40 dB)", "78", "74"], ["Moderate (40–55 dB)", "75", "73"], ["Loud (above 55 dB)", "66", "71"]],
        "Table of average reading and math scores in quiet, moderate and loud classrooms",
        col_widths=[0.44, 0.28, 0.28],
    )
    return [
        Q(WIC,
          blank("The scientist's hypothesis was initially met with ___, but within a decade, new evidence had persuaded "
                "most of her colleagues that she was right."),
          P_WIC, "skepticism", ["enthusiasm", "indifference", "envy"],
          "Colleagues who later had to be persuaded must first have doubted the idea: <em>skepticism</em>."),
        Q(WIC,
          blank("The museum's collection of ancient coins is ___: it includes examples from nearly every major empire of "
                "the ancient Mediterranean world."),
          P_WIC, "comprehensive", ["meager", "uniform", "counterfeit"],
          "Including examples from nearly every major empire makes the collection <em>comprehensive</em>."),
        Q(WIC,
          blank("The mayor's response to the flood was praised as ___: within hours, she had opened shelters and "
                "organized teams to deliver food and water."),
          P_WIC, "prompt", ["tardy", "lavish", "hesitant"],
          "Acting within hours is a <em>prompt</em> response."),
        Q(WIC,
          blank("Although the film's plot is ___, its striking images and music make it memorable."),
          P_WIC, "unremarkable", ["innovative", "intricate", "unforgettable"],
          "“Although” sets the plot against the memorable images and music, so the plot is <em>unremarkable</em>."),
        Q(TSP,
          p("When European explorers first saw the platypus in the late 1700s, many naturalists in Britain believed the "
            "specimens were fakes, with a duck's bill sewn onto the body of a mammal. Detailed examination soon showed "
            "that the animal was real. Even then, the platypus continued to puzzle scientists, because it was a mammal "
            "that laid eggs, a fact not confirmed until 1884."),
          P_STRUCTURE,
          "It describes an initial doubt about an animal, explains how that doubt was resolved, and then notes a "
          "further puzzle the animal posed.",
          ["It compares the platypus with ducks and argues that they are closely related.",
           "It describes how the platypus was first captured and then explains how it was named.",
           "It argues that early naturalists were right to believe the specimens were fakes."],
          "The text moves from doubts about fakes, to confirmation, to the lingering question of egg-laying."),
        Q(TSP,
          underline("The city of Venice is built on more than a hundred small islands in a lagoon. ",
                    "Its oldest buildings rest on millions of wooden posts driven deep into the mud, where the lack of "
                    "oxygen has kept them from rotting for centuries.",
                    " Today, however, rising sea levels and sinking ground threaten the city in ways its builders could "
                    "not have foreseen."),
          P_FUNCTION,
          "It explains how the city's oldest buildings have remained standing, before the text turns to newer threats.",
          ["It describes the tools used to build the city's bridges.",
           "It explains why the city was built on islands.",
           "It argues that the wooden posts are the main threat to the city today."],
          "The posts explain the buildings' survival; the next sentence introduces present-day threats."),
        Q(CTC,
          texts("Some economists argue that giving people cash directly is an inefficient way to reduce poverty, since "
                "recipients may spend the money on things that do not improve their lives in the long term.",
                "Economist Esi Mensah studied a program in which families received regular cash payments with no "
                "conditions attached. After two years, families had invested much of the money in livestock, tools, and "
                "small businesses, and their incomes had risen. Spending on items such as alcohol did not increase."),
          "Based on the texts, how would Mensah (Text 2) most likely respond to the economists' argument in Text 1?",
          "By arguing that her findings show recipients often spend cash in ways that improve their long-term situation",
          ["By agreeing that cash payments are an inefficient way to reduce poverty",
           "By claiming that families who received cash spent most of it on alcohol",
           "By suggesting that cash payments should be given only once"],
          "Mensah's families invested the money and raised their incomes, contradicting the economists' concern."),
        Q(CID,
          p("The following text is from a short story. Mrs. Okafor is teaching her granddaughter to bake bread.")
          + p("“You cannot rush it,” Mrs. Okafor said, covering the bowl with a cloth. Adaeze checked the clock. An hour, "
              "her grandmother had said. She swept the flour from the table, then checked again. Seven minutes. Mrs. "
              "Okafor laughed and handed her a book. When Adaeze finally lifted the cloth, the dough had doubled, soft "
              "and rounded, and she understood that the waiting had been part of the recipe all along."),
          P_MAIN_IDEA,
          "Adaeze learns that patience is an essential part of baking bread.",
          ["Adaeze decides that she does not enjoy baking.",
           "Mrs. Okafor forgets to tell Adaeze how long the dough must rise.",
           "Adaeze bakes the bread before it has finished rising."],
          "Adaeze is impatient but ends up seeing the waiting as part of the recipe."),
        Q(CID,
          p("Scientists once thought that the human appendix, a small pouch attached to the large intestine, served no "
            "purpose. Some researchers now suggest that it may store helpful gut bacteria. After an illness that clears "
            "bacteria from the intestine, these stored bacteria could help restore the gut's normal population."),
          P_MAIN_IDEA,
          "The appendix, once thought useless, may help restore helpful gut bacteria after illness.",
          ["The appendix is the main source of all bacteria in the human body.",
           "Scientists have proved that the appendix has no function.",
           "Illnesses that clear bacteria from the intestine begin in the appendix."],
          "The text contrasts the old view with the newer suggestion about storing bacteria."),
        Q(COET,
          p("Biologist Mikael Strand claims that a species of moth has become darker over the past century mainly "
            "because darker moths are better camouflaged on the soot-covered trees near factories."),
          P_WEAKEN,
          "Moths of the species have become darker at the same rate in clean rural forests as in polluted industrial "
          "areas.",
          ["Birds that eat the moths hunt mainly by sight.",
           "Trees near factories are darker than trees in rural forests.",
           "Darker moths are more common near factories than lighter moths are."],
          "If the moths darkened equally where trees are clean, soot camouflage cannot be the main cause."),
        Q(COEQ,
          p("Three towns began collecting food scraps for composting. An environmental officer notes that the program "
            "cut landfill waste sharply in two towns but made little difference in Brill, where weekly waste per "
            "household ___"),
          P_GRAPH,
          "fell only from about 12.8 to about 12.4 kilograms.",
          ["fell from about 14.2 to about 9.1 kilograms.",
           "fell from about 13.5 to about 8.7 kilograms.",
           "rose from about 12.4 to about 12.8 kilograms."],
          "Brill shows the small change the officer describes.",
          figure=fig_waste),
        Q(COEQ,
          p("A marine scientist argues that heavy fishing over several decades has reduced the size of the cod in the "
            "northern fishery, because the largest fish were caught first: the average length of cod caught ___"),
          P_GRAPH,
          "fell from about 82 centimeters in 1970 to about 58 centimeters in 2020.",
          ["was about 60 centimeters in 2010.",
           "rose from about 58 centimeters in 1970 to about 82 centimeters in 2020.",
           "stayed about the same from 1970 to 2020."],
          "The steady decline in length supports the scientist's argument.",
          figure=fig_fish),
        Q(COEQ,
          p("Researchers studied whether classroom noise affects learning. They concluded that loud classrooms were "
            "associated with much lower reading scores but had little effect on math scores: ___"),
          P_TABLE,
          "reading scores were 66 in loud classrooms compared with 78 in quiet ones, while math scores were 71 compared "
          "with 74.",
          ["math scores were 74 in quiet classrooms.",
           "reading scores were higher than math scores in quiet classrooms.",
           "math scores were 66 in loud classrooms compared with 78 in quiet ones."],
          "Only this choice shows a large reading gap and a small math gap.",
          figure=fig_noise),
        Q(INF,
          p("Many plants close their flowers at night. Botanist Lin Wei studied a species whose flowers close each "
            "evening and found that closed flowers stayed several degrees warmer than flowers that had been propped "
            "open. Pollen in the propped-open flowers was also more often damaged by dew. These findings suggest that ___"),
          P_INFER,
          "closing at night may help the flowers protect their pollen from cold and moisture.",
          ["the flowers produce pollen only at night.",
           "dew helps the flowers stay warm at night.",
           "insects pollinate the flowers mainly at night."],
          "Closed flowers stayed warmer and drier, which suggests closing protects the pollen."),
        Q(BND,
          blank("The writer Jorge Luis Borges, who worked for years as a ___ imagined a library containing every possible "
                "book."),
          P_SEC, "librarian,", ["librarian", "librarian;", "librarian:"],
          "The nonessential clause beginning with a comma after “Borges” must end with a comma."),
        Q(FSS,
          blank("The collection of essays, written over four decades, ___ the author's changing views on art."),
          P_SEC, "reveals", ["reveal", "are revealing", "have revealed"],
          "The subject is the singular “collection,” so the verb is <em>reveals</em>."),
        Q(BND,
          blank("The first known map of the world was carved into a clay tablet in ancient ___ it shows Babylon at the "
                "center, surrounded by a ring of water."),
          P_SEC, "Babylonia;", ["Babylonia,", "Babylonia", "Babylonia and,"],
          "Two independent clauses are joined with a semicolon."),
        Q(FSS,
          blank("Exhausted after the long race, ___"),
          P_SEC,
          "the runners lay on the grass and drank water.",
          ["the grass was where the runners lay and drank water.",
           "water was drunk by the runners as they lay on the grass.",
           "lying on the grass and drinking water was what the runners did."],
          "The runners were exhausted, so “the runners” must follow the opening phrase."),
        Q(BND,
          blank("The orchestra performs in three venues each year: a concert hall in the city, an outdoor stage in the "
                "___ and a small church in the countryside."),
          P_SEC, "park,", ["park;", "park", "park:"],
          "Items in a simple list are separated by commas."),
        Q(FSS,
          blank("The students' reports on the river were more detailed than ___ written by students the year before."),
          P_SEC, "those", ["that", "them", "it"],
          "Reports are compared with other reports; the plural pronoun <em>those</em> refers to them."),
        Q(FSS,
          blank("By the time the rescue team arrived, the hikers ___ shelter in a cave for two days."),
          P_SEC, "had taken", ["take", "have taken", "will take"],
          "The sheltering happened before another past event (the team's arrival), so the past perfect is needed."),
        Q(TRN,
          blank("The new phone is thinner and lighter than the previous model. ___ its battery lasts nearly twice as "
                "long."),
          P_TRANSITION, "In addition,", ["However,", "Instead,", "In contrast,"],
          "The longer battery life is another improvement added to the list."),
        Q(TRN,
          blank("Most of the city's residents supported the new bike lanes. ___ a small group of shop owners worried "
                "that losing parking spaces would hurt their businesses."),
          P_TRANSITION, "Still,", ["Therefore,", "Similarly,", "For instance,"],
          "The shop owners' concern contrasts with the general support."),
        Q(TRN,
          blank("Ancient Greek poems rarely describe the sea or the sky as blue. ___ the poet Homer described the sea as "
                "“wine-dark.”"),
          P_TRANSITION, "Indeed,", ["However,", "Nonetheless,", "Instead,"],
          "Homer's description supports and illustrates the preceding claim."),
        Q(RS,
          notes(["Komodo dragons are the largest living lizards.",
                 "They can grow up to about 3 meters long.",
                 "They live on a few islands in Indonesia.",
                 "Females can sometimes produce offspring without mating, a process called parthenogenesis."],
                "The student wants to highlight an unusual fact about Komodo dragon reproduction."),
          P_NOTES_Q,
          "Female Komodo dragons can sometimes produce offspring without mating, a process called parthenogenesis.",
          ["Komodo dragons are the largest living lizards.",
           "Komodo dragons live on a few islands in Indonesia.",
           "Komodo dragons can grow up to about 3 meters long."],
          "Only this choice is about reproduction."),
        Q(RS,
          notes(["A study compared people who used a paper map with people who used GPS directions.",
                 "Both groups walked the same route through an unfamiliar town.",
                 "Afterward, participants were asked to draw the route from memory.",
                 "The paper-map group drew the route much more accurately."],
                "The student wants to present the study's finding to readers who rely on GPS."),
          P_NOTES_Q,
          "In one study, people who used a paper map remembered a route much more accurately than people who followed "
          "GPS directions.",
          ["In one study, participants walked the same route through an unfamiliar town.",
           "In one study, participants were asked to draw a route from memory.",
           "A study compared people who used paper maps with people who used GPS."],
          "Only this choice states the finding."),
        Q(RS,
          notes(["Rumi was a thirteenth-century Persian poet.",
                 "He was born in what is now Afghanistan and later lived in Konya, in present-day Turkey.",
                 "His poetry has been translated into many languages.",
                 "In recent decades, he has been one of the best-selling poets in the United States."],
                "The student wants to emphasize Rumi's popularity today."),
          P_NOTES_Q,
          "Though Rumi lived in the thirteenth century, in recent decades he has been one of the best-selling poets in "
          "the United States.",
          ["Rumi was a thirteenth-century Persian poet.",
           "Rumi was born in what is now Afghanistan.",
           "Rumi lived in Konya, in present-day Turkey."],
          "Only this choice addresses his popularity today."),
    ]
