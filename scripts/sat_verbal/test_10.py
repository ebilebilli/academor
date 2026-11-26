"""Academor SAT Practice Test 10 — Reading and Writing."""

from sat_verbal.common import (
    BND, CID, COEQ, COET, CTC, FSS, INF, P_FINDING, P_FUNCTION, P_GRAPH, P_INFER, P_MAIN_IDEA,
    P_NOTES_Q, P_PURPOSE, P_SEC, P_STRUCTURE, P_TABLE, P_TRANSITION, P_WEAKEN, P_WIC, Q, RS, TRN, TSP,
    WIC, bar_chart, blank, grouped_bar_chart, line_chart, notes, p, table_image, texts, underline,
)


def module_1():
    fig_feedback = bar_chart(
        "Average Essay Score After Different Types of Feedback",
        ["Grade\nonly", "Grade and\ncomments", "Comments\nonly", "Comments and\nrevision"],
        [64, 66, 71, 79],
        "Average score on next essay", 90,
        "Bar graph of average scores on the next essay: grade only 64, grade and comments 66, comments only 71, "
        "comments and revision 79",
        value_fmt="{:.0f}",
    )
    fig_bats = line_chart(
        "Bats Recorded at Two Sites After Lights Were Changed",
        [2016, 2017, 2018, 2019, 2020, 2021],
        [("Site with dimmed lights", [44, 46, 61, 72, 80, 85]), ("Site with unchanged lights", [45, 43, 44, 41, 42, 40])],
        "Bats recorded per night", (0, 100),
        "Line graph of bats recorded per night: the site with dimmed lights rises from 44 to 85 after 2017, while the "
        "unchanged site stays near 42",
        note=(2017, "Lights dimmed\nat one site"),
    )
    fig_market = table_image(
        "Sales at a Farmers' Market by Payment Method",
        ["Year", "Cash", "Card", "Mobile payment"],
        [["2019", "71%", "24%", "5%"], ["2021", "48%", "36%", "16%"], ["2023", "29%", "41%", "30%"]],
        "Table of the share of farmers' market sales paid by cash, card and mobile payment in 2019, 2021 and 2023",
        col_widths=[0.22, 0.24, 0.24, 0.30],
    )
    return [
        Q(WIC,
          blank("The engineer's report was ___: in just two pages, it identified the cause of the failure and proposed "
                "a solution."),
          P_WIC, "succinct", ["lengthy", "confusing", "speculative"],
          "Covering the cause and a solution in two pages is <em>succinct</em>."),
        Q(WIC,
          blank("The village's isolation proved ___ for linguists: because few outsiders had ever settled there, its "
                "dialect had preserved words that had disappeared everywhere else."),
          P_WIC, "fortunate", ["harmful", "irrelevant", "temporary"],
          "The isolation preserved rare words, which was lucky, or <em>fortunate</em>, for linguists."),
        Q(WIC,
          blank("The athlete's recovery from injury was ___: doctors had expected her to need a year of rest, but she "
                "competed again within four months."),
          P_WIC, "remarkable", ["predictable", "incomplete", "routine"],
          "Returning in four months instead of a year is <em>remarkable</em>."),
        Q(WIC,
          blank("Critics found the author's second novel ___ to her first: it repeated the same setting, the same kinds "
                "of characters, and even some of the same scenes."),
          P_WIC, "derivative", ["superior", "unrelated", "opposed"],
          "A novel that repeats so much of an earlier one is <em>derivative</em> of it."),
        Q(TSP,
          underline("For centuries, the ink used to write many medieval manuscripts was made from oak galls, round growths "
                    "that form on oak trees when certain wasps lay eggs in them. ",
                    "When crushed and mixed with iron salts, the galls produce a dark ink that bonds strongly with "
                    "parchment and resists being washed away.",
                    " Over time, however, the acid in the ink can eat through the pages, posing a challenge for "
                    "conservators today."),
          P_FUNCTION,
          "It explains a quality of the ink that made it useful, before the text describes a drawback.",
          ["It describes how wasps choose which oak trees to use.",
           "It explains why conservators prefer modern inks.",
           "It argues that oak gall ink was rarely used."],
          "The ink's strong bond explains its usefulness; the next sentence introduces its harmful acid."),
        Q(TSP,
          p("The following text is from a short story. Isabel has just been elected captain of her soccer team.")
          + p("Coach Ruiz read out the result, and the team cheered. Isabel smiled and thanked everyone, but on the walk "
              "home the smile faded. She thought about Marta, who had wanted the job and had voted for her anyway, and "
              "about the games they had lost by a single goal. By the time she reached her door, she had decided two "
              "things: she would ask Marta to help her lead the warm-ups, and she would start practicing penalty kicks "
              "every morning."),
          P_PURPOSE,
          "To show a character taking her new responsibility seriously and planning how to meet it",
          ["To explain why a character did not want to be elected captain",
           "To describe a disagreement between a character and her coach",
           "To show that a character is jealous of a teammate"],
          "Isabel's thoughts turn to her teammate and the team's losses, and she makes plans to lead well."),
        Q(CTC,
          texts("Some historians argue that the spread of clocks in European towns in the 1300s and 1400s changed how "
                "people worked, encouraging them to organize labor by the hour rather than by the task.",
                "Historian Marguerite Lambert examined records from guilds and workshops in several towns and found "
                "that most workers continued to be paid by the task, or by the day, for centuries after town clocks "
                "appeared. Lambert argues that clocks may have mattered more for coordinating public events, such as "
                "markets and church services, than for organizing work."),
          "Based on the texts, how would Lambert (Text 2) most likely respond to the historians' argument in Text 1?",
          "By arguing that her evidence suggests clocks had little immediate effect on how most work was organized",
          ["By agreeing that town clocks quickly led workers to be paid by the hour",
           "By claiming that town clocks were not built until the 1600s",
           "By suggesting that markets were held less often after clocks appeared"],
          "Lambert found payment by task or day continued for centuries, which challenges the historians' argument."),
        Q(CID,
          p("Fireflies produce light through a chemical reaction in their abdomens. Each species has its own pattern of "
            "flashes, which males use to signal to females. In some species, however, females imitate the flash "
            "patterns of other species. When a male of another species approaches, expecting a mate, the female "
            "catches and eats him."),
          P_MAIN_IDEA,
          "Fireflies use flash patterns to signal mates, but some females copy other species' signals to lure prey.",
          ["Fireflies produce light only when they are hunting.",
           "Male fireflies imitate the flashes of females of other species.",
           "All firefly species share the same pattern of flashes."],
          "The text explains the signaling system and how some females exploit it."),
        Q(CID,
          p("Before the Brooklyn Bridge opened in 1883, many New Yorkers doubted that such a long suspension bridge "
            "would be safe. In 1884, to reassure the public, the showman P. T. Barnum led a parade of 21 elephants "
            "across it. The event drew large crowds and helped persuade people that the bridge was strong."),
          "According to the text, why did P. T. Barnum lead elephants across the Brooklyn Bridge?",
          "To help convince the public that the bridge was strong",
          ["To celebrate the day the bridge first opened",
           "To test whether the bridge could hold the weight of trains",
           "To protest the high cost of building the bridge"],
          "The text says the parade was meant to reassure the public about the bridge's safety."),
        Q(COET,
          p("Psychologist Helen Brandt claims that people are more likely to help a stranger when they are not in a "
            "hurry."),
          P_FINDING,
          "In a study, participants told they were late for an appointment were much less likely to stop and help a "
          "person who appeared ill than participants told they had plenty of time.",
          ["Most participants in a survey said that they consider themselves helpful.",
           "People who live in small towns report helping neighbors more often.",
           "Participants who stopped to help were often asked to describe their mood."],
          "Hurried participants helped less, directly supporting Brandt's claim."),
        Q(COEQ,
          p("A teacher tested different kinds of feedback on student essays. The teacher concluded that written comments "
            "helped more when they were not accompanied by a grade, and that having students revise their essays "
            "helped most of all: students who received comments only scored ___"),
          P_GRAPH,
          "71 on their next essay, compared with 66 for those who received a grade and comments and 79 for those who "
          "received comments and revised.",
          ["64 on their next essay, the lowest of any group.",
           "66 on their next essay, compared with 71 for those who received a grade and comments.",
           "79 on their next essay, compared with 71 for those who revised."],
          "Only this choice compares comments alone with comments plus a grade and shows revision doing best.",
          figure=fig_feedback),
        Q(COEQ,
          p("In 2017 a town dimmed the streetlights at one of two nature sites where bats are counted. Researchers "
            "argue that dimmer lights benefited the bats, noting that after 2017 the number of bats recorded per night "
            "___"),
          P_GRAPH,
          "rose from about 46 to about 85 at the site with dimmed lights but stayed near 42 at the other site.",
          ["was about 45 at both sites in 2016.",
           "rose at both sites by about the same amount.",
           "fell from about 85 to about 46 at the site with dimmed lights."],
          "Only this choice contrasts the rise at the dimmed site with no change at the other site.",
          figure=fig_bats),
        Q(COEQ,
          p("A market manager notes that customers at the farmers' market have moved away from cash, with mobile "
            "payments growing especially quickly: between 2019 and 2023, ___"),
          P_TABLE,
          "the share of sales paid in cash fell from 71% to 29%, while the share paid by mobile payment rose from 5% to "
          "30%.",
          ["the share of sales paid by card was 41% in 2023.",
           "the share of sales paid in cash was higher than the share paid by card in 2021.",
           "the share of sales paid by mobile payment fell from 30% to 5%."],
          "Only this choice shows the move away from cash and the rapid growth of mobile payments.",
          figure=fig_market),
        Q(INF,
          p("Many trees in temperate forests drop their leaves in autumn. Before they do, the trees pull nutrients such "
            "as nitrogen out of the leaves and store them in their branches and roots. Ecologist Paolo Russo found that "
            "trees growing in nitrogen-poor soil removed a larger share of the nitrogen from their leaves before "
            "dropping them than trees of the same species growing in rich soil. These findings suggest that ___"),
          P_INFER,
          "trees may recover more nutrients from their leaves when those nutrients are scarce in the soil.",
          ["trees in rich soil drop their leaves earlier than trees in poor soil.",
           "nitrogen-poor soil causes trees to grow more leaves.",
           "trees store nitrogen only in their leaves."],
          "Trees in poor soil recovered more nitrogen, suggesting they conserve it when it is scarce."),
        Q(FSS,
          blank("The museum, along with several nearby galleries, ___ free admission on the first Sunday of each month."),
          P_SEC, "offers", ["offer", "are offering", "have offered"],
          "The subject is the singular “museum”; the phrase “along with …” does not change its number."),
        Q(BND,
          blank("The novelist wrote every morning from six to ___ in the afternoons she answered letters and walked in "
                "the hills."),
          P_SEC, "noon;", ["noon,", "noon", "noon, and, in"],
          "Two independent clauses are joined with a semicolon."),
        Q(FSS,
          blank("Neither of the two candidates ___ willing to debate the other on television."),
          P_SEC, "was", ["were", "are", "have been"],
          "“Neither” is singular, so the singular verb <em>was</em> is required."),
        Q(BND,
          blank("Many of the world's most important ___ wheat, rice, and corn, are members of the grass family."),
          P_SEC, "crops, including", ["crops including,", "crops; including", "crops including"],
          "The phrase “including wheat, rice, and corn” is nonessential and set off by a pair of commas."),
        Q(FSS,
          blank("The scientists hoped that the new telescope would allow ___ to see galaxies that formed soon after the "
                "universe began."),
          P_SEC, "them", ["they", "their", "themself"],
          "The object of “allow” must be the object pronoun <em>them</em>."),
        Q(BND,
          blank("The cookbook includes recipes from every region of the ___ dumplings from the north, curries from the "
                "south, and grilled fish from the coast."),
          P_SEC, "country:", ["country;", "country", "country, and"],
          "A colon introduces the examples of regional recipes."),
        Q(FSS,
          blank("Driving through the mountains at night, ___"),
          P_SEC,
          "the travelers could see the lights of villages far below.",
          ["the lights of villages far below were visible to the travelers.",
           "villages far below could be seen by the travelers by their lights.",
           "seeing the lights of villages far below was possible for the travelers."],
          "The travelers were driving, so they must follow the opening phrase."),
        Q(TRN,
          blank("The first part of the experiment went exactly as planned. ___ the second part was delayed for weeks "
                "when a key piece of equipment broke."),
          P_TRANSITION, "However,", ["Similarly,", "Therefore,", "For example,"],
          "The delay contrasts with the smooth first part."),
        Q(TRN,
          blank("The library lends more than books. ___ patrons can borrow telescopes, sewing machines, and even "
                "fishing rods."),
          P_TRANSITION, "For example,", ["Nevertheless,", "In contrast,", "As a result,"],
          "The items listed are examples of things other than books."),
        Q(TRN,
          blank("The artist begins each sculpture by making dozens of small clay models. ___ she chooses one model and "
                "builds a full-size version in bronze."),
          P_TRANSITION, "Finally,", ["However,", "Similarly,", "In other words,"],
          "Building the full-size version is the last step in the process."),
        Q(RS,
          notes(["The Amazon River carries more water than any other river on Earth.",
                 "It discharges about 200,000 cubic meters of water per second into the Atlantic Ocean.",
                 "That is more than the next several largest rivers combined.",
                 "The Nile is generally considered the longer river."],
                "The student wants to emphasize the volume of water the Amazon carries."),
          P_NOTES_Q,
          "The Amazon carries more water than any other river, about 200,000 cubic meters per second.",
          ["The Nile is generally considered longer than the Amazon.",
           "The Amazon River flows into the Atlantic Ocean.",
           "The Amazon is one of the largest rivers on Earth."],
          "Only this choice emphasizes the volume of water."),
        Q(RS,
          notes(["Researchers placed bowls of free candy in an office.",
                 "Some bowls were placed on workers' desks.",
                 "Other bowls were placed about two meters away.",
                 "Workers ate about twice as much candy when the bowls were on their desks."],
                "The student wants to explain what the study suggests about how location affects eating."),
          P_NOTES_Q,
          "The study suggests that people eat more of a food when it is placed within easy reach.",
          ["In the study, some bowls of candy were placed on workers' desks.",
           "Researchers placed bowls of free candy in an office.",
           "In the study, some bowls of candy were placed about two meters away."],
          "Only this choice states what the study suggests."),
        Q(RS,
          notes(["Ruth Asawa was an American sculptor born in 1926.",
                 "She is best known for hanging sculptures made of looped wire.",
                 "The sculptures cast detailed shadows on the walls and floor around them.",
                 "She also worked to bring art education into public schools in San Francisco."],
                "The student wants to describe Asawa's best-known works."),
          P_NOTES_Q,
          "Ruth Asawa is best known for hanging sculptures of looped wire that cast detailed shadows around them.",
          ["Ruth Asawa was an American sculptor born in 1926.",
           "Ruth Asawa worked to bring art education into public schools.",
           "Ruth Asawa worked in San Francisco."],
          "Only this choice describes her best-known works."),
    ]


def module_2():
    fig_birds = grouped_bar_chart(
        "Window Collisions per Building per Year",
        ["Library", "Gym", "Science hall"],
        [("Before window markers", [42, 18, 35]), ("After window markers", [9, 17, 7])],
        "Recorded bird collisions", 50,
        "Grouped bar graph of bird collisions per year before and after window markers at three campus buildings",
    )
    fig_lake = line_chart(
        "Water Clarity in Lake Senna",
        [2008, 2010, 2012, 2014, 2016, 2018, 2020],
        [("Clarity", [1.9, 1.8, 1.7, 2.6, 3.4, 3.9, 4.1])],
        "Depth at which a disk disappears (meters)", (0, 5),
        "Line graph of lake water clarity: about 1.8 meters from 2008 to 2012 and rising to 4.1 meters by 2020",
        note=(2012, "Farm runoff\nrules begin"),
    )
    fig_apps = table_image(
        "Results of a Study of Language-Learning Apps",
        ["Daily practice", "Students", "Average vocabulary gain (words)"],
        [["5 minutes", "120", "140"], ["15 minutes", "120", "310"], ["30 minutes", "120", "330"]],
        "Table of vocabulary gains for students who practiced with an app for 5, 15 and 30 minutes a day",
        col_widths=[0.32, 0.24, 0.44],
    )
    return [
        Q(WIC,
          blank("The archaeologists' interpretation of the site remains ___: some features suggest a temple, while "
                "others suggest a marketplace, and no inscription has been found to settle the question."),
          P_WIC, "tentative", ["definitive", "unanimous", "obvious"],
          "With mixed evidence and no deciding inscription, the interpretation is <em>tentative</em>."),
        Q(WIC,
          blank("The composer's notebooks reveal a ___ habit of revision: she rewrote some passages more than twenty "
                "times before she was satisfied."),
          P_WIC, "relentless", ["occasional", "careless", "reluctant"],
          "Rewriting passages more than twenty times shows a <em>relentless</em> habit."),
        Q(WIC,
          blank("The two theories are often presented as opposites, but the physicist argues that they can be ___, since "
                "each describes the same phenomenon at a different scale."),
          P_WIC, "reconciled", ["confused", "abandoned", "contrasted"],
          "Theories that describe one phenomenon at different scales can be brought together, or "
          "<em>reconciled</em>."),
        Q(WIC,
          blank("The film director is known for her ___ approach to casting: she often chooses actors with no previous "
                "experience, whom she finds by visiting schools and markets."),
          P_WIC, "unconventional", ["traditional", "cautious", "expensive"],
          "Choosing untrained actors found in schools and markets is <em>unconventional</em>."),
        Q(TSP,
          p("For much of the twentieth century, scientists believed that the stomach ulcers that affect millions of "
            "people were caused mainly by stress and spicy food. In the early 1980s, two Australian researchers, Barry "
            "Marshall and Robin Warren, proposed that a bacterium, <em>Helicobacter pylori</em>, was responsible. Many "
            "doctors were skeptical, so Marshall drank a culture of the bacteria and soon developed stomach "
            "inflammation. Their work eventually changed how ulcers are treated, and in 2005 the two received the Nobel "
            "Prize in Physiology or Medicine."),
          P_STRUCTURE,
          "It presents a long-held belief, describes a challenge to it and the evidence offered, and notes the "
          "challenge's eventual acceptance.",
          ["It describes two theories about ulcers and concludes that both were correct.",
           "It explains how ulcers are treated today and lists the medicines used.",
           "It describes Marshall's career and argues that his experiment was unnecessary."],
          "The text moves from the stress theory, to the bacterium proposal and Marshall's experiment, to the Nobel "
          "Prize."),
        Q(TSP,
          underline("The giant sequoias of California are among the largest living things on Earth. ",
                    "Their thick, spongy bark, which can be nearly a meter deep, contains little resin and protects the "
                    "trees from the low-intensity fires that once swept through their forests every few years.",
                    " In fact, these fires help the trees reproduce, because the heat opens their cones and clears the "
                    "ground for seedlings."),
          P_FUNCTION,
          "It explains how the trees survive a threat that the final sentence shows can also benefit them.",
          ["It describes how sequoias grow to such a large size.",
           "It explains why fires no longer occur in sequoia forests.",
           "It compares sequoias with other trees that grow in California."],
          "The bark protects the trees from fire; the final sentence explains how fire also helps them reproduce."),
        Q(CTC,
          texts("Some psychologists have argued that people make better decisions when they take time to think "
                "carefully about every option, listing the advantages and disadvantages of each.",
                "Psychologist Diego Varela asked participants to choose among several apartments, each described by a "
                "dozen features. Participants who were distracted with an unrelated puzzle before choosing picked the "
                "best apartment more often than those who spent the same time deliberating. Varela suggests that for "
                "complex choices, careful deliberation may sometimes lead people to focus on unimportant details."),
          "Based on the texts, how would Varela (Text 2) most likely respond to the psychologists' argument in Text 1?",
          "By suggesting that careful deliberation may not always lead to better decisions, especially for complex "
          "choices",
          ["By agreeing that people should always list the advantages and disadvantages of every option",
           "By arguing that puzzles help people make decisions about apartments",
           "By claiming that people make better decisions when they choose quickly about simple matters"],
          "Varela found distracted participants chose better on a complex task, which challenges the argument."),
        Q(CID,
          p("The following text is from a short story. Malik is helping his father paint the family's old boat.")
          + p("His father painted the hull with long, slow strokes, never letting the brush leave a drip. Malik tried "
              "to copy him and made a mess of the bow. He expected a scolding. Instead his father handed him a rag, "
              "showed him how to wipe the drip away, and said nothing more. By the end of the afternoon, Malik's "
              "strokes had grown longer and slower, and when his father stepped back to look at the boat, Malik could "
              "no longer tell which side was whose."),
          P_MAIN_IDEA,
          "Through his father's quiet guidance, Malik learns to paint as skillfully as his father.",
          ["Malik's father is angry about the mess Malik made on the bow.",
           "Malik refuses to keep painting after making a mistake.",
           "Malik's father decides to hire someone else to paint the boat."],
          "With his father's patient help, Malik's work becomes indistinguishable from his father's."),
        Q(CID,
          p("Plants cannot move away from insects that eat them, but many have chemical defenses. When a tomato plant's "
            "leaves are chewed, for example, the plant can release chemicals that make its leaves harder to digest. "
            "Some plants also release substances into the air that attract wasps and other predators of the insects "
            "doing the damage."),
          P_MAIN_IDEA,
          "Although they cannot move, plants can defend themselves against insects with chemicals, both directly and by "
          "attracting the insects' predators.",
          ["Tomato plants are eaten by more insects than other plants are.",
           "Wasps damage tomato plants by chewing their leaves.",
           "Plants defend themselves mainly by growing new leaves quickly."],
          "The text describes two kinds of chemical defense."),
        Q(COET,
          p("Some researchers claim that playing a musical instrument in childhood improves memory skills that are "
            "unrelated to music."),
          P_WEAKEN,
          "When researchers randomly assigned children to music lessons or to no lessons, the two groups showed the "
          "same improvement on memory tests a year later.",
          ["Children who play instruments are often encouraged by their parents.",
           "Many professional musicians began playing instruments in childhood.",
           "Children who take music lessons usually practice several times a week."],
          "With random assignment, equal memory gains suggest lessons do not improve memory."),
        Q(COEQ,
          p("A university added markers to windows that birds often flew into. A campus ecologist notes that the "
            "markers sharply reduced collisions at two buildings but had little effect at the gym, where collisions "
            "___"),
          P_GRAPH,
          "fell only from about 18 to about 17 per year.",
          ["fell from about 42 to about 9 per year.",
           "fell from about 35 to about 7 per year.",
           "rose from about 17 to about 18 per year."],
          "The gym shows the small change the ecologist describes.",
          figure=fig_birds),
        Q(COEQ,
          p("In 2012 new rules limited runoff from farms into Lake Senna, which had been clouded by algae. Scientists "
            "measure the lake's clarity by lowering a white disk until it disappears. They argue that the rules made "
            "the lake clearer, noting that the disk ___"),
          P_GRAPH,
          "disappeared at about 1.8 meters from 2008 to 2012 but at about 4.1 meters by 2020.",
          ["disappeared at about 1.9 meters in 2008.",
           "disappeared at shallower depths every year after 2012.",
           "disappeared at about 4.1 meters in 2012."],
          "Little change before 2012 and a large increase afterward supports the claim.",
          figure=fig_lake),
        Q(COEQ,
          p("Researchers studied students learning vocabulary with an app. They concluded that increasing daily "
            "practice from 5 to 15 minutes greatly improved results, but that practicing longer than 15 minutes added "
            "little: ___"),
          P_TABLE,
          "average gains rose from 140 words to 310 words when practice increased from 5 to 15 minutes, but only to 330 "
          "words with 30 minutes of practice.",
          ["each group had 120 students.",
           "students who practiced 30 minutes a day gained the most words, 330.",
           "average gains doubled each time practice time doubled."],
          "Only this choice shows the large gain up to 15 minutes and the small gain after.",
          figure=fig_apps),
        Q(INF,
          p("Some desert beetles collect drinking water from fog. Biologist Nadia Kader observed that on foggy mornings, "
            "the beetles climb to the tops of sand dunes and tilt their bodies into the wind. Tiny droplets collect on "
            "bumps on the beetles' backs and roll down toward their mouths. On mornings without fog, the beetles stayed "
            "lower on the dunes. These observations suggest that ___"),
          P_INFER,
          "the beetles' behavior on foggy mornings may help them gather water from the fog.",
          ["the beetles avoid the tops of dunes because of the wind.",
           "the beetles collect water only on mornings without fog.",
           "the bumps on the beetles' backs help them dig into the sand."],
          "Climbing into the wind only when there is fog, with water rolling to their mouths, points to water "
          "collection."),
        Q(BND,
          blank("The poet Rabindranath Tagore, who in 1913 became the first non-European to win the Nobel Prize in "
                "___ also composed thousands of songs."),
          P_SEC, "Literature,", ["Literature", "Literature;", "Literature:"],
          "The nonessential clause beginning after “Tagore” must close with a comma."),
        Q(FSS,
          blank("The list of volunteers who signed up to clean the park ___ longer than the organizers expected."),
          P_SEC, "was", ["were", "are", "have been"],
          "The subject is the singular “list,” so the verb is <em>was</em>."),
        Q(BND,
          blank("The trail is closed in ___ heavy snow makes the upper sections dangerous."),
          P_SEC, "winter because", ["winter, because,", "winter; because", "winter. Because"],
          "“Because heavy snow …” is a dependent clause that explains the closing; no punctuation is needed."),
        Q(FSS,
          blank("Having finished the first draft of her thesis, ___"),
          P_SEC,
          "the student sent it to her advisor for comments.",
          ["her advisor received the first draft for comments.",
           "comments on the first draft were requested from her advisor.",
           "the first draft was sent to her advisor for comments."],
          "The student finished the draft, so “the student” must follow the opening phrase."),
        Q(BND,
          blank("The violin, the cello, and the double bass all belong to the same ___ the string family."),
          P_SEC, "group:", ["group;", "group,", "group, it is"],
          "A colon introduces the name of the group."),
        Q(FSS,
          blank("The new hospital's emergency room is larger than ___, so patients wait less."),
          P_SEC, "the old hospital's", ["the old hospital", "the old hospitals'", "the old hospitals"],
          "An emergency room must be compared with an emergency room: “the old hospital's” means “the old hospital's "
          "emergency room.”"),
        Q(FSS,
          blank("Every one of the students who took the exam ___ allowed to use a calculator."),
          P_SEC, "was", ["were", "are", "have been"],
          "The subject is “every one,” which is singular, so the verb is <em>was</em>."),
        Q(TRN,
          blank("The company's profits rose for five years in a row. ___ in the sixth year, a sharp drop in sales led to "
                "its first loss."),
          P_TRANSITION, "Then,", ["Similarly,", "In addition,", "For example,"],
          "The loss came next in time, after the five years of growth."),
        Q(TRN,
          blank("Jellyfish have no brain, heart, or bones. ___ they have survived in Earth's oceans for more than 500 "
                "million years."),
          P_TRANSITION, "Even so,", ["Therefore,", "In other words,", "Similarly,"],
          "Long survival is surprising given their simple bodies."),
        Q(TRN,
          blank("To make the city safer for cyclists, planners added protected bike lanes. ___ they lowered the speed "
                "limit on several busy streets."),
          P_TRANSITION, "Additionally,", ["However,", "Instead,", "In contrast,"],
          "Lowering speed limits is a second safety measure."),
        Q(RS,
          notes(["The Arctic tern breeds in the Arctic and spends the northern winter near Antarctica.",
                 "Tracking studies show that some terns fly more than 70,000 kilometers a year.",
                 "Over a lifetime of about thirty years, a tern may fly more than two million kilometers.",
                 "That is roughly the distance to the Moon and back three times."],
                "The student wants to emphasize the lifetime distance an Arctic tern can travel."),
          P_NOTES_Q,
          "Over a lifetime, an Arctic tern may fly more than two million kilometers, roughly the distance to the Moon "
          "and back three times.",
          ["The Arctic tern breeds in the Arctic and spends the northern winter near Antarctica.",
           "Some Arctic terns fly more than 70,000 kilometers a year.",
           "Arctic terns can live for about thirty years."],
          "Only this choice emphasizes the lifetime distance."),
        Q(RS,
          notes(["A study examined how people judge the quality of wine.",
                 "Participants tasted the same wine twice.",
                 "They were told that one glass came from an expensive bottle and the other from a cheap bottle.",
                 "Most participants rated the wine from the supposedly expensive bottle as better."],
                "The student wants to present the study's conclusion about price and judgment."),
          P_NOTES_Q,
          "The study suggests that what people believe about price can affect how they judge quality.",
          ["In the study, participants tasted the same wine twice.",
           "Participants were told that one glass came from an expensive bottle.",
           "A study examined how people judge the quality of wine."],
          "Only this choice states the conclusion."),
        Q(RS,
          notes(["Tu Youyou is a Chinese pharmaceutical chemist born in 1930.",
                 "In the 1970s she studied traditional Chinese medical texts for treatments for malaria.",
                 "One text led her to extract a substance called artemisinin from sweet wormwood.",
                 "In 2015 she received the Nobel Prize in Physiology or Medicine for this work."],
                "The student wants to emphasize how traditional knowledge contributed to Tu's discovery."),
          P_NOTES_Q,
          "Studying traditional Chinese medical texts led Tu Youyou to extract artemisinin, a treatment for malaria, "
          "from sweet wormwood.",
          ["Tu Youyou is a Chinese pharmaceutical chemist born in 1930.",
           "Tu Youyou received the Nobel Prize in Physiology or Medicine in 2015.",
           "Artemisinin is extracted from sweet wormwood."],
          "Only this choice connects the traditional texts to the discovery."),
    ]
