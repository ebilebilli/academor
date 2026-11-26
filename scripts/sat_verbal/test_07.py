"""Academor SAT Practice Test 7 — Reading and Writing."""

from sat_verbal.common import (
    BND, CID, COEQ, COET, CTC, FSS, INF, P_FINDING, P_FUNCTION, P_GRAPH, P_INFER, P_MAIN_IDEA,
    P_NOTES_Q, P_PURPOSE, P_SEC, P_STRUCTURE, P_TABLE, P_TRANSITION, P_WEAKEN, P_WIC, Q, RS, TRN, TSP,
    WIC, bar_chart, blank, grouped_bar_chart, line_chart, notes, p, table_image, texts, underline,
)


def module_1():
    fig_trees = bar_chart(
        "Average Height of Tree Saplings After Three Years",
        ["Planted\nalone", "Planted with\ngrass", "Planted with\nclover", "Planted with\nclover, fenced"],
        [1.6, 1.1, 2.0, 2.6],
        "Height (meters)", 3,
        "Bar graph of average sapling height after three years: alone 1.6, with grass 1.1, with clover 2.0, with clover "
        "and fenced 2.6 meters",
        value_fmt="{:.1f}",
    )
    fig_language = line_chart(
        "Speakers of the Revived Language of Island V",
        [1980, 1990, 2000, 2010, 2020],
        [("Fluent speakers", [140, 180, 420, 1100, 2300])],
        "Number of fluent speakers", (0, 2500),
        "Line graph of fluent speakers rising from 140 in 1980 to 180 in 1990, 420 in 2000, 1,100 in 2010 and 2,300 in "
        "2020",
        note=(1990, "Immersion\nschools open"),
    )
    fig_bees = table_image(
        "Bee Visits per Hour to Three Flower Colors",
        ["Flower color", "Bumblebees", "Honeybees"],
        [["Blue", "34", "21"], ["Yellow", "18", "29"], ["White", "12", "14"]],
        "Table of bumblebee and honeybee visits per hour to blue, yellow and white flowers",
        col_widths=[0.4, 0.3, 0.3],
    )
    return [
        Q(WIC,
          blank("The museum's new guidebook is admirably ___: it covers every gallery in fewer than forty pages, "
                "without leaving out any important work."),
          P_WIC, "concise", ["rambling", "outdated", "incomplete"],
          "Covering everything important in very few pages is <em>concise</em>."),
        Q(WIC,
          blank("The detective's theory was ___: it explained the open window, the missing key, and the muddy "
                "footprints, and no other theory could account for all three."),
          P_WIC, "compelling", ["far-fetched", "incoherent", "irrelevant"],
          "A theory that alone explains every clue is <em>compelling</em>."),
        Q(WIC,
          blank("Rather than ___ the old factory, the city converted it into apartments and studios, keeping its brick "
                "walls and tall windows."),
          P_WIC, "demolishing", ["restoring", "preserving", "inspecting"],
          "“Rather than” sets keeping the building against tearing it down, or <em>demolishing</em> it."),
        Q(WIC,
          blank("Some readers find the poet's later work ___, but others argue that its spare, plain language makes its "
                "emotions more powerful."),
          P_WIC, "austere", ["ornate", "playful", "verbose"],
          "Spare, plain language that some find too severe is <em>austere</em>."),
        Q(TSP,
          underline("Saffron, the dried stigmas of a crocus flower, is one of the most expensive spices in the world. ",
                    "Each flower produces only three stigmas, which must be picked by hand, and about 150,000 flowers "
                    "are needed to make a single kilogram of the spice.",
                    " Some growers have experimented with machines, but hand harvesting remains the norm."),
          P_FUNCTION,
          "It explains why saffron is so expensive, as stated in the first sentence.",
          ["It describes the history of saffron's use in cooking.",
           "It argues that machines should replace hand harvesting.",
           "It compares saffron with other expensive spices."],
          "The labor and the number of flowers needed explain the high price."),
        Q(TSP,
          p("The following text is from a short story. Mateo has just moved to a new country and is starting school.")
          + p("Mateo understood perhaps one word in five. The teacher wrote on the board, the students laughed at "
              "something, and he laughed a moment too late. At lunch he sat at the end of a long table and studied "
              "the others the way he studied a map, looking for landmarks. When a girl across from him pushed a bag of "
              "grapes toward him and said a word he did not know, he guessed its meaning from her smile and said it "
              "back. She laughed, and this time he laughed at exactly the right moment."),
          P_PURPOSE,
          "To show a character beginning to find his place in an unfamiliar setting through a small act of kindness",
          ["To explain why a character dislikes his new school",
           "To describe a character's difficulty reading a map of his new city",
           "To contrast two characters' opinions about their teacher"],
          "Mateo feels lost until a classmate's gesture lets him share a moment of laughter."),
        Q(CTC,
          texts("Many linguists once assumed that the languages spoken by small hunter-gatherer communities would have "
                "relatively simple grammar, since the communities themselves were small and their technology was "
                "limited.",
                "Linguist Rachel Odhiambo has documented several languages spoken by such communities and found that "
                "some of them have extremely complex grammar, including verb forms that change depending on whether "
                "the speaker saw an event, heard about it, or inferred it. Odhiambo argues that the size of a community "
                "tells us little about how complex its language will be."),
          "Based on the texts, how would Odhiambo (Text 2) most likely respond to the assumption described in Text 1?",
          "By arguing that her research contradicts it",
          ["By agreeing that small communities usually speak simple languages",
           "By claiming that the languages of large communities are always simpler",
           "By suggesting that the assumption applies only to verb forms"],
          "Odhiambo found complex grammar in small communities, which contradicts the assumption."),
        Q(CID,
          p("Wetlands are sometimes described as nature's sponges. During heavy rains, marshes and swamps soak up large "
            "amounts of water and release it slowly, which reduces flooding downstream. Wetland plants also trap "
            "sediment and absorb excess nutrients from fertilizers, so the water that flows out of a wetland is often "
            "cleaner than the water that flowed in. When wetlands are drained, communities can lose these benefits."),
          P_MAIN_IDEA,
          "Wetlands help control flooding and clean water, benefits that can be lost when they are drained.",
          ["Wetlands cause flooding by releasing water during heavy rains.",
           "Wetland plants grow best in water that contains a lot of fertilizer.",
           "Most communities have already drained the wetlands near them."],
          "The text describes the two main benefits of wetlands and the risk of losing them."),
        Q(CID,
          p("In 1953 Edmund Hillary of New Zealand and Tenzing Norgay, a Sherpa mountaineer from Nepal, became the first "
            "climbers known to reach the summit of Mount Everest. In the months that followed, reporters repeatedly "
            "asked which of the two had stepped onto the summit first. At first, both men refused to say, insisting "
            "that they had reached it as a team."),
          "According to the text, how did Hillary and Norgay at first respond to questions about who reached the summit "
          "first?",
          "They declined to answer, saying they had reached the summit together as a team.",
          ["They agreed that Hillary had reached the summit first.",
           "They said that Norgay had reached the summit first.",
           "They each claimed to have reached the summit first."],
          "Both refused to say and insisted they reached it as a team."),
        Q(COET,
          p("Ecologist Joon-ho Lee claims that the decline of a certain songbird in a forest is caused mainly by a "
            "shortage of the caterpillars that the birds feed to their chicks."),
          P_FINDING,
          "In parts of the forest where researchers added extra caterpillars to the birds' feeding areas, more chicks "
          "survived than in parts where no caterpillars were added.",
          ["The songbirds sing most often in the early morning.",
           "The forest is home to several other species of songbirds.",
           "Caterpillars are most common in the forest in late spring."],
          "Adding caterpillars improved chick survival, directly linking food supply to the birds' success."),
        Q(COEQ,
          p("Researchers tested ways to help tree saplings grow in a former pasture. They found that planting saplings "
            "with clover helped them grow taller than planting them alone, and that fencing out deer helped even more: "
            "saplings planted with clover reached an average height of ___"),
          P_GRAPH,
          "2.0 meters, compared with 1.6 meters for saplings planted alone and 2.6 meters for those planted with clover "
          "and fenced.",
          ["1.1 meters, compared with 1.6 meters for saplings planted alone.",
           "2.6 meters, compared with 2.0 meters for saplings planted with grass.",
           "1.6 meters, the same as saplings planted alone."],
          "Only this choice compares clover with planting alone and shows the further gain from fencing.",
          figure=fig_trees),
        Q(COEQ,
          p("In 1990 the community of Island V opened schools that taught all subjects in its traditional language, "
            "which few people still spoke. A linguist argues that these schools played a major role in reviving the "
            "language, noting that the number of fluent speakers ___"),
          P_GRAPH,
          "grew only from about 140 to about 180 in the decade before the schools opened but rose to about 2,300 by "
          "2020.",
          ["was about 140 in 1980.",
           "fell from about 180 to about 140 after the schools opened.",
           "reached about 1,100 in 2000."],
          "Slow growth before 1990 and rapid growth afterward supports the linguist's argument.",
          figure=fig_language),
        Q(COEQ,
          p("A biologist observed bees visiting flowers of three colors in a meadow. The biologist concluded that the "
            "two kinds of bees preferred different colors: ___"),
          P_TABLE,
          "bumblebees visited blue flowers most often (34 visits per hour), while honeybees visited yellow flowers most "
          "often (29 visits per hour).",
          ["both kinds of bees visited white flowers least often.",
           "bumblebees made 18 visits per hour to yellow flowers.",
           "honeybees visited blue flowers most often (21 visits per hour)."],
          "Only this choice shows each kind of bee favoring a different color.",
          figure=fig_bees),
        Q(INF,
          p("Ancient Roman concrete used in harbor walls has survived in seawater for about two thousand years, while "
            "much modern concrete cracks within decades in similar conditions. Geologist Laila Haddad found that the "
            "Roman concrete contains volcanic ash that reacts slowly with seawater, forming new minerals that fill "
            "small cracks as they appear. These findings suggest that ___"),
          P_INFER,
          "the durability of Roman concrete may be due partly to a chemical process that repairs it over time.",
          ["modern concrete is made without any minerals.",
           "seawater damages Roman concrete more quickly than modern concrete.",
           "the Romans built their harbor walls in places where the sea was calm."],
          "Minerals that form and fill cracks would let the concrete repair itself, helping explain its long life."),
        Q(FSS,
          blank("Neither the coach nor the players ___ surprised when the game was canceled because of the storm."),
          P_SEC, "were", ["was", "is", "has been"],
          "With “neither … nor,” the verb agrees with the nearer subject, the plural “players.”"),
        Q(BND,
          blank("The lighthouse was built in 1857 to warn ships away from the reef. Today it is a ___ visitors can "
                "climb its 200 steps to the top."),
          P_SEC, "museum, and", ["museum,", "museum and,", "museum and"],
          "Two independent clauses joined by “and” need a comma before the conjunction."),
        Q(FSS,
          blank("The scientist and her team published ___ findings in a journal so that other researchers could check "
                "them."),
          P_SEC, "their", ["its", "her", "they're"],
          "The plural subject “the scientist and her team” requires the plural possessive <em>their</em>."),
        Q(BND,
          blank("The Japanese art of kintsugi repairs broken pottery with lacquer mixed with powdered ___ instead of "
                "hiding the cracks, it highlights them as part of the object's history."),
          P_SEC, "gold;", ["gold,", "gold", "gold, and, it"],
          "Two independent clauses are joined with a semicolon."),
        Q(FSS,
          blank("The school's new schedule gives students more time for lunch and ___ classes begin a little later in "
                "the morning."),
          P_SEC, "ensures that", ["ensuring that", "to ensure that", "ensured that"],
          "“Gives … and ensures” keeps the two verbs parallel and in the present tense."),
        Q(BND,
          blank("The chef's three rules for the ___ use fresh ingredients, clean as you go, and taste everything."),
          P_SEC, "kitchen are simple:", ["kitchen are simple;", "kitchen, are simple:", "kitchen are simple"],
          "A colon introduces the list of rules; no comma belongs between the subject and the verb."),
        Q(FSS,
          blank("Looking through the telescope for the first time, ___"),
          P_SEC,
          "the students could see the rings of Saturn clearly.",
          ["the rings of Saturn were clearly visible to the students.",
           "Saturn's rings could be seen clearly by the students.",
           "it was possible for the students to see the rings of Saturn clearly."],
          "The students did the looking, so they must follow the opening phrase."),
        Q(TRN,
          blank("The library expected few people to attend its first coding workshop. ___ more than sixty people "
                "arrived, and staff had to bring in extra chairs."),
          P_TRANSITION, "Instead,", ["Similarly,", "Therefore,", "For example,"],
          "The large turnout was the opposite of what was expected."),
        Q(TRN,
          blank("Earthworms improve soil in several ways. Their tunnels allow air and water to reach plant roots. ___ "
                "their waste is rich in nutrients that plants need."),
          P_TRANSITION, "Furthermore,", ["However,", "Instead,", "In contrast,"],
          "The nutrients are a second way earthworms improve soil."),
        Q(TRN,
          blank("The two paintings look almost identical. ___ X-ray images show that the artist painted a completely "
                "different scene beneath one of them."),
          P_TRANSITION, "Yet", ["Thus,", "Likewise,", "In addition,"],
          "The hidden scene contrasts with the paintings' identical appearance."),
        Q(RS,
          notes(["The Lascaux caves are in southwestern France.",
                 "Their walls are covered with paintings of horses, deer, and bulls.",
                 "The paintings are about 17,000 years old.",
                 "The caves were closed to the public in 1963 to protect the paintings."],
                "The student wants to emphasize the age of the Lascaux paintings."),
          P_NOTES_Q,
          "The paintings of animals on the walls of the Lascaux caves are about 17,000 years old.",
          ["The Lascaux caves were closed to the public in 1963.",
           "The Lascaux caves are in southwestern France.",
           "The walls of the Lascaux caves show horses, deer, and bulls."],
          "Only this choice states the age of the paintings."),
        Q(RS,
          notes(["Some trees in a forest are connected underground by fungi that grow on their roots.",
                 "Through these networks, trees can exchange water and nutrients.",
                 "In one study, larger trees sent carbon through the network to seedlings growing in shade.",
                 "Some scientists caution that the importance of these networks is still debated."],
                "The student wants to describe the study's finding while acknowledging uncertainty."),
          P_NOTES_Q,
          "One study found that larger trees sent carbon to shaded seedlings through fungal networks, though some "
          "scientists caution that the importance of these networks is still debated.",
          ["Some trees are connected underground by fungi that grow on their roots.",
           "In one study, larger trees sent carbon through fungal networks to seedlings growing in shade.",
           "The importance of fungal networks in forests is still debated by scientists."],
          "Only this choice gives the finding and also notes the uncertainty."),
        Q(RS,
          notes(["Fanny Mendelssohn was a German composer and pianist born in 1805.",
                 "She wrote more than 450 pieces of music.",
                 "Several of her songs were first published under the name of her brother, Felix Mendelssohn.",
                 "In recent decades, her work has been performed and recorded much more often."],
                "The student wants to explain why Fanny Mendelssohn's work was long overlooked."),
          P_NOTES_Q,
          "Fanny Mendelssohn's work was long overlooked partly because several of her songs were first published under "
          "her brother's name.",
          ["Fanny Mendelssohn wrote more than 450 pieces of music.",
           "Fanny Mendelssohn was a German composer and pianist born in 1805.",
           "In recent decades, Fanny Mendelssohn's work has been performed much more often."],
          "Only this choice gives a reason her work was overlooked."),
    ]


def module_2():
    fig_steps = grouped_bar_chart(
        "Average Daily Steps of Office Workers",
        ["Team A", "Team B", "Team C"],
        [("Before standing desks", [5200, 4800, 5600]), ("After standing desks", [5300, 6900, 5500])],
        "Steps per day", 8000,
        "Grouped bar graph of average daily steps for three teams before and after standing desks were installed",
    )
    fig_rents = line_chart(
        "Average Monthly Rent for a One-Bedroom Apartment",
        [2014, 2016, 2018, 2020, 2022],
        [("Calder City", [900, 1050, 1250, 1300, 1550]), ("Brenton", [850, 880, 920, 950, 990])],
        "Dollars", (600, 1700),
        "Line graph of average rents: Calder City rising from 900 to 1,550 dollars and Brenton from 850 to 990 dollars "
        "between 2014 and 2022",
    )
    fig_sleep = table_image(
        "Memory Test Scores After Different Amounts of Sleep",
        ["Hours of sleep", "Average score (out of 50)"],
        [["4", "28"], ["6", "36"], ["8", "44"], ["10", "45"]],
        "Table of average memory test scores after 4, 6, 8 and 10 hours of sleep",
        col_widths=[0.45, 0.55],
    )
    return [
        Q(WIC,
          blank("The negotiators reached an agreement only after weeks of ___ discussions in which each side insisted "
                "on terms the other found unacceptable."),
          P_WIC, "contentious", ["cordial", "brief", "casual"],
          "Discussions in which both sides make unacceptable demands are <em>contentious</em>."),
        Q(WIC,
          blank("The archaeologist warned that the site was ___: a single heavy rain could wash away layers that had "
                "survived for thousands of years."),
          P_WIC, "vulnerable", ["impervious", "abandoned", "renowned"],
          "A site that one rain could damage is <em>vulnerable</em>."),
        Q(WIC,
          blank("The writer's memoir is notable for its ___: she describes her own mistakes as plainly as she describes "
                "her successes."),
          P_WIC, "candor", ["vanity", "secrecy", "humor"],
          "Plainly admitting mistakes shows honesty, or <em>candor</em>."),
        Q(WIC,
          blank("Early critics ___ the architect's design, calling it ugly and impractical; today the building is "
                "considered one of the city's treasures."),
          P_WIC, "disparaged", ["commended", "commissioned", "replicated"],
          "Calling the design ugly and impractical is to <em>disparage</em> it."),
        Q(TSP,
          p("Scientists once thought that the inner solar system had been bombarded by asteroids and comets in a single, "
            "intense burst about 3.9 billion years ago. This idea was based largely on rock samples brought back from "
            "the Moon, many of which seemed to date from that period. More recent analyses, however, suggest that the "
            "samples may have come mostly from a single large impact, whose debris spread across the Moon's surface. "
            "Many researchers now favor the view that bombardment declined gradually over a longer period."),
          P_STRUCTURE,
          "It presents an earlier view, explains the evidence for it, and then describes a reinterpretation of that "
          "evidence.",
          ["It describes two impacts on the Moon and compares their sizes.",
           "It explains how rock samples were collected and then lists their ages.",
           "It argues that asteroids never struck the inner solar system."],
          "The text moves from the single-burst view, to the Moon samples behind it, to a new reading of those samples."),
        Q(TSP,
          underline("The violin maker Antonio Stradivari built instruments in Italy in the late 1600s and early 1700s. ",
                    "In several blind tests, however, professional violinists who could not see the instruments were "
                    "unable to reliably tell Stradivari violins from high-quality modern ones, and many preferred the "
                    "modern violins.",
                    " These results have led some experts to question whether the old instruments' famous sound is "
                    "partly a matter of reputation."),
          P_FUNCTION,
          "It presents findings that the final sentence suggests may challenge the instruments' reputation.",
          ["It explains the methods Stradivari used to build his violins.",
           "It describes the history of violin making in Italy.",
           "It argues that modern violins should be sold for higher prices."],
          "The blind-test results are the basis for questioning whether the famous sound is partly reputation."),
        Q(CTC,
          texts("Many historians have described the medieval period in Europe as a time when scientific thinking largely "
                "stopped, with scholars simply repeating the ideas of ancient authors.",
                "Historian Tobias Weber points to scholars at universities in Paris and Oxford in the 1300s who "
                "criticized ancient ideas about motion and developed new ways of describing speed and acceleration. "
                "Weber argues that their work, though often overlooked, laid groundwork for later scientists."),
          "Based on the texts, how would Weber (Text 2) most likely respond to the historians' description in Text 1?",
          "By arguing that it overlooks medieval scholars who developed new scientific ideas",
          ["By agreeing that medieval scholars only repeated ancient ideas",
           "By claiming that ancient ideas about motion were correct",
           "By suggesting that universities did not exist in medieval Europe"],
          "Weber's examples of original work contradict the claim that scientific thinking stopped."),
        Q(CID,
          p("The following text is from a short story. Mrs. Adeyemi runs a small bookshop that is about to close.")
          + p("On the last day, the regulars came. Mr. Haas, who had bought a mystery novel every Saturday for twenty "
              "years, bought three. The Kim sisters, who had learned to read in the children's corner, brought their "
              "own children. By evening the shelves were half empty, and Mrs. Adeyemi realized that the shop had not "
              "really been a store at all. It had been a room where people met, and the room, she thought, would "
              "remain in them after the door was locked."),
          P_MAIN_IDEA,
          "As her bookshop closes, Mrs. Adeyemi realizes it mattered most as a place that connected people.",
          ["Mrs. Adeyemi is relieved that she no longer has to sell books.",
           "Mrs. Adeyemi decides to keep the bookshop open after all.",
           "Mrs. Adeyemi is upset that the regular customers did not visit on the last day."],
          "The regulars' visits lead her to see the shop as a meeting place that will live on in them."),
        Q(CID,
          p("Lichens look like single organisms, but each is actually a partnership between a fungus and an alga or "
            "bacterium that can make food from sunlight. The fungus provides structure and protection, while its "
            "partner provides sugars. This partnership allows lichens to grow in places where neither partner could "
            "survive alone, from bare rock to the frozen soil of the Arctic."),
          P_MAIN_IDEA,
          "Lichens are partnerships in which each partner provides something the other needs, allowing them to live in "
          "harsh places.",
          ["Lichens are a type of fungus that can make food from sunlight.",
           "Lichens grow only in the Arctic.",
           "The fungus in a lichen gets nothing from its partner."],
          "The text explains the partnership and how it lets lichens survive in harsh environments."),
        Q(COET,
          p("Some researchers claim that a recent decline in a city's crime rate was caused mainly by a new program that "
            "added streetlights to dark streets."),
          P_WEAKEN,
          "Crime declined by the same amount on streets that did not receive new lights as on streets that did.",
          ["Residents said they felt safer walking on streets with new lights.",
           "The new streetlights use less electricity than the old ones.",
           "Most of the new streetlights were installed in the first year of the program."],
          "If crime fell equally with or without new lights, the lights cannot be the main cause."),
        Q(COEQ,
          p("A company installed standing desks for three teams. A manager notes that the desks seemed to change the "
            "habits of only one team: Team B's average daily steps ___"),
          P_GRAPH,
          "rose from about 4,800 to about 6,900, while the other teams' averages changed by only about 100 steps.",
          ["rose from about 5,200 to about 5,300.",
           "fell from about 5,600 to about 5,500.",
           "were lower than Team A's both before and after the desks were installed."],
          "Only this choice shows one team changing sharply while the others barely changed.",
          figure=fig_steps),
        Q(COEQ,
          p("A housing analyst argues that rents rose much faster in Calder City than in nearby Brenton between 2014 and "
            "2022: in Calder City the average rent rose ___"),
          P_GRAPH,
          "by about $650, while in Brenton it rose by about $140.",
          ["from about $850 to about $990.",
           "by about $140, while in Brenton it rose by about $650.",
           "every year shown, as it did in Brenton."],
          "Comparing the two increases supports the claim; the third choice reverses the cities.",
          figure=fig_rents),
        Q(COEQ,
          p("Researchers measured memory after different amounts of sleep. They concluded that more sleep improved "
            "memory, but that the benefit leveled off beyond eight hours: ___"),
          P_TABLE,
          "average scores rose from 28 after 4 hours to 44 after 8 hours, but only to 45 after 10 hours.",
          ["participants who slept 6 hours scored an average of 36.",
           "average scores rose by the same amount for each additional two hours of sleep.",
           "participants who slept 10 hours scored the highest average, 45."],
          "Only this choice shows large gains up to eight hours and almost none after.",
          figure=fig_sleep),
        Q(INF,
          p("Elephants communicate partly through low rumbles that travel through the ground as well as the air. "
            "Biologist Zanele Dube played recordings of warning rumbles through the ground near elephants that could not "
            "hear them through the air. The elephants froze and turned toward the source, and some lifted a foot, as "
            "if sensing vibrations. These findings suggest that ___"),
          P_INFER,
          "elephants may be able to detect messages from other elephants through vibrations in the ground.",
          ["elephants cannot hear rumbles that travel through the air.",
           "elephants make rumbles only when they are in danger.",
           "lifting a foot helps elephants make louder rumbles."],
          "Reacting to rumbles they could only sense through the ground points to vibration-based communication."),
        Q(FSS,
          blank("The list of ingredients printed on the side of the box ___ several items that many shoppers would not "
                "recognize."),
          P_SEC, "includes", ["include", "are including", "have included"],
          "The subject is the singular “list,” so the verb is <em>includes</em>."),
        Q(BND,
          blank("The geologist explained that the canyon was formed over millions of years by a single ___ which slowly "
                "cut through layers of rock."),
          P_SEC, "river,", ["river", "river;", "river:"],
          "A comma introduces the nonessential clause “which slowly cut …”"),
        Q(FSS,
          blank("The novel was so popular that within a year ___ had been translated into twenty languages."),
          P_SEC, "it", ["they", "them", "one"],
          "The pronoun refers to “the novel,” which is singular."),
        Q(BND,
          blank("Some of the earliest known musical instruments are flutes made from bird bone and mammoth ___ which "
                "were found in caves in Germany and are about 40,000 years old."),
          P_SEC, "ivory,", ["ivory", "ivory;", "ivory—"],
          "A comma introduces the nonessential clause that adds information about the flutes."),
        Q(FSS,
          blank("Whether the bridge will be repaired or replaced ___ on the results of next month's inspection."),
          P_SEC, "depends", ["depend", "are depending", "have depended"],
          "A clause used as a subject (“Whether … replaced”) is singular, so the verb is <em>depends</em>."),
        Q(BND,
          blank("The team had prepared for every ___ the one thing they had not planned for was a power failure."),
          P_SEC, "problem except one:", ["problem except one;", "problem, except one,", "problem except one"],
          "A colon introduces the explanation of the one problem; the other choices create errors."),
        Q(FSS,
          blank("The painter Hokusai, ___ created his famous print of a great wave in his seventies, continued working "
                "until his death at the age of eighty-eight."),
          P_SEC, "who", ["whom", "which", "whose"],
          "The subject of “created” is a person, so the subject pronoun <em>who</em> is needed."),
        Q(TRN,
          blank("Most stars appear white to the naked eye. ___ when viewed through a telescope, many show distinct "
                "colors, from deep red to bright blue."),
          P_TRANSITION, "However,", ["Therefore,", "For example,", "Similarly,"],
          "Colors seen through a telescope contrast with the white appearance to the naked eye."),
        Q(TRN,
          blank("The school wanted to encourage students to read more over the summer. ___ it gave every student a free "
                "book and a reading log with prizes for each book finished."),
          P_TRANSITION, "To this end,", ["In contrast,", "Even so,", "Otherwise,"],
          "The free books and prizes were meant to achieve the goal of more reading."),
        Q(TRN,
          blank("The first test of the new engine failed after only ten seconds. ___ the engineers redesigned the fuel "
                "system, and the second test ran for a full minute."),
          P_TRANSITION, "Undeterred,", ["Similarly,", "In other words,", "For instance,"],
          "The engineers kept working despite the failure."),
        Q(RS,
          notes(["The International Space Station orbits Earth about once every 90 minutes.",
                 "That means astronauts aboard it see about 16 sunrises and sunsets each day.",
                 "The station has been continuously occupied since November 2000.",
                 "It is about the size of a football field."],
                "The student wants to describe an unusual aspect of daily life aboard the space station."),
          P_NOTES_Q,
          "Because the International Space Station orbits Earth about every 90 minutes, astronauts aboard it see about "
          "16 sunrises and sunsets each day.",
          ["The International Space Station is about the size of a football field.",
           "The International Space Station has been occupied since November 2000.",
           "The International Space Station orbits Earth."],
          "Only this choice describes an unusual aspect of daily life aboard the station."),
        Q(RS,
          notes(["Researchers studied two groups of children learning to play the piano.",
                 "The first group practiced the same piece repeatedly.",
                 "The second group practiced several different pieces in a mixed order.",
                 "A week later, the second group played a new piece more accurately."],
                "The student wants to present the study's conclusion."),
          P_NOTES_Q,
          "The study suggests that practicing several pieces in a mixed order may help children learn to play new "
          "pieces more accurately.",
          ["In the study, one group of children practiced the same piece repeatedly.",
           "Researchers studied two groups of children learning to play the piano.",
           "The second group of children practiced several different pieces."],
          "Only this choice states the conclusion of the study."),
        Q(RS,
          notes(["Alexander von Humboldt was a German naturalist and explorer.",
                 "From 1799 to 1804 he explored parts of South America, Central America, and Mexico.",
                 "He recorded how plant life changes with altitude on mountains such as Chimborazo.",
                 "His ideas influenced later scientists, including Charles Darwin."],
                "The student wants to emphasize Humboldt's influence on other scientists."),
          P_NOTES_Q,
          "Alexander von Humboldt's ideas influenced later scientists, including Charles Darwin.",
          ["From 1799 to 1804 Humboldt explored parts of the Americas.",
           "Humboldt recorded how plant life changes with altitude on mountains.",
           "Alexander von Humboldt was a German naturalist and explorer."],
          "Only this choice mentions his influence on other scientists."),
    ]
