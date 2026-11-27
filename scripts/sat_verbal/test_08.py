"""Academor SAT Practice Test 8 — Reading and Writing."""

from sat_verbal.common import (
    BND, CID, COEQ, COET, CTC, FSS, INF, P_FINDING, P_FUNCTION, P_GRAPH, P_INFER, P_MAIN_IDEA,
    P_NOTES_Q, P_PURPOSE, P_SEC, P_STRUCTURE, P_TABLE, P_TRANSITION, P_WEAKEN, P_WIC, Q, RS, TRN, TSP,
    WIC, bar_chart, blank, grouped_bar_chart, line_chart, notes, p, table_image, texts, underline,
)


def module_1():
    fig_lunch = bar_chart(
        "Vegetables Eaten at Lunch Under Different Serving Approaches",
        ["Served on\nthe side", "Served\nfirst", "Named on\nthe menu", "Served first\nand named"],
        [32, 47, 41, 58],
        "Vegetables eaten (%)", 65,
        "Bar graph of the percentage of vegetables eaten: on the side 32%, served first 47%, named on the menu 41%, "
        "served first and named 58%",
        value_fmt="{:.0f}%",
    )
    fig_owls = line_chart(
        "Barn Owl Nesting Pairs in Hollin Valley",
        [2006, 2009, 2012, 2015, 2018, 2021],
        [("Nesting pairs", [14, 12, 13, 25, 37, 44])],
        "Number of nesting pairs", (0, 50),
        "Line graph of barn owl nesting pairs: about 13 from 2006 to 2012, then rising to 44 by 2021",
        note=(2012, "Nest boxes\ninstalled"),
    )
    fig_concrete = table_image(
        "Strength of Concrete Mixtures After 28 Days",
        ["Mixture", "Recycled glass", "Strength (megapascals)"],
        [["Standard", "0%", "32"], ["Mixture 1", "10%", "33"], ["Mixture 2", "20%", "31"], ["Mixture 3", "40%", "24"]],
        "Table of the strength of four concrete mixtures containing 0, 10, 20 and 40 percent recycled glass",
        col_widths=[0.3, 0.3, 0.4],
    )
    return [
        Q(WIC,
          blank("The startup's first product was ___: within a year, it was used in more than half of the city's "
                "restaurants, and competitors rushed to copy it."),
          P_WIC, "ubiquitous", ["obsolete", "unpopular", "experimental"],
          "Being used almost everywhere in the city makes the product <em>ubiquitous</em>."),
        Q(WIC,
          blank("The professor's comments on student essays were ___ but kind: she pointed out every weak argument while "
                "also suggesting how each could be improved."),
          P_WIC, "rigorous", ["lax", "hostile", "vague"],
          "Pointing out every weak argument is thorough and demanding, or <em>rigorous</em>; “but kind” adds the "
          "helpful suggestions."),
        Q(WIC,
          blank("Because the instructions were written in a technical style that few people could follow, the company "
                "hired a writer to ___ them for ordinary users."),
          P_WIC, "simplify", ["complicate", "translate", "conceal"],
          "Instructions that are too technical need to be made easier, or <em>simplified</em>."),
        Q(WIC,
          blank("The historian argues that the king's reputation for cruelty is ___, based largely on accounts written "
                "by his enemies long after his death."),
          P_WIC, "unwarranted", ["deserved", "recent", "modest"],
          "A reputation based mainly on hostile, late accounts is not justified: it is <em>unwarranted</em>."),
        Q(TSP,
          underline("Velcro was invented after a walk in the woods. ",
                    "In 1941 the Swiss engineer George de Mestral noticed that burrs from burdock plants clung stubbornly "
                    "to his clothing and to his dog's fur, and when he examined them under a microscope, he saw that "
                    "they were covered with tiny hooks.",
                    " He spent years developing a fastener that copied this design."),
          P_FUNCTION,
          "It describes the observation that led to the invention mentioned in the first sentence.",
          ["It explains why burdock plants grow in forests.",
           "It describes a problem with Velcro that de Mestral later solved.",
           "It compares Velcro with other kinds of fasteners."],
          "The burrs and their hooks are the observation that inspired the invention."),
        Q(TSP,
          p("The following text is from a short story. Priya is waiting for the results of a science competition.")
          + p("The judges had been in the other room for forty minutes. Priya had checked her watch so often that her "
              "friend Lena finally took it off her wrist and put it in her own pocket. “It doesn't make them go "
              "faster,” Lena said. Priya laughed, then went back to watching the door, counting the tiles on the floor "
              "between herself and it. There were thirty-one. There had been thirty-one the last four times, too."),
          P_PURPOSE,
          "To portray a character's nervousness as she waits for an important result",
          ["To explain how a character won a science competition",
           "To describe an argument between two friends",
           "To show that a character is bored by a long event"],
          "Checking her watch and counting the same tiles again and again show Priya's nerves."),
        Q(CTC,
          texts("Some nutrition scientists have recommended that people avoid eating late at night, arguing that food "
                "eaten in the evening is more likely to be stored as fat than the same food eaten earlier in the day.",
                "Researcher Felipe Rojas compared two groups who ate the same total amount of food each day for eight "
                "weeks. One group ate most of its food before 3:00 p.m., and the other ate most of it after 6:00 p.m. "
                "The groups' weight changed by similar amounts, though the late eaters reported sleeping less well. "
                "Rojas concludes that the timing of meals may matter more for sleep than for weight."),
          "Based on the texts, how would Rojas (Text 2) most likely respond to the scientists' argument in Text 1?",
          "By suggesting that his results do not support the claim that late eating causes weight gain",
          ["By agreeing that food eaten in the evening is more likely to be stored as fat",
           "By recommending that people eat most of their food after 6:00 p.m.",
           "By claiming that the total amount of food people eat does not affect weight"],
          "Rojas found similar weight changes regardless of timing, which does not support the scientists' claim."),
        Q(CID,
          p("When the Mars rover <em>Opportunity</em> landed in 2004, it was expected to operate for only about 90 "
            "days. Instead, it kept exploring for more than fourteen years. Engineers credit several factors: "
            "winds on Mars periodically blew dust off its solar panels, restoring power, and the team on Earth learned "
            "to park the rover on slopes facing the Sun during the Martian winter."),
          P_MAIN_IDEA,
          "The rover <em>Opportunity</em> far outlasted its expected lifespan, thanks to both lucky conditions and "
          "careful planning.",
          ["The rover <em>Opportunity</em> stopped working after about 90 days.",
           "Winds on Mars damaged the rover's solar panels.",
           "The rover was designed to operate for fourteen years."],
          "The text contrasts the expected 90 days with fourteen years and explains why."),
        Q(CID,
          p("The following text is from a short story. Old Mr. Tanaka has tended the same garden for fifty years.")
          + p("His granddaughter wanted to replace the crooked plum tree. It leaned toward the fence, she said, and its "
              "fruit was small and sour. Mr. Tanaka did not argue. Instead, he led her to the trunk and showed her the "
              "scar where her mother, at seven, had carved her initials, and the branch where her grandmother had hung "
              "a lantern every summer. The granddaughter was quiet for a while. Then she asked how to make the sour "
              "plums into jam."),
          P_MAIN_IDEA,
          "By sharing the tree's family history, Mr. Tanaka changes his granddaughter's view of it.",
          ["Mr. Tanaka agrees that the plum tree should be replaced.",
           "Mr. Tanaka's granddaughter decides to plant a new garden.",
           "Mr. Tanaka is angry with his granddaughter for criticizing the tree."],
          "After learning the tree's history, the granddaughter wants to use its fruit instead of removing it."),
        Q(COET,
          p("Psychologist Ana Costa claims that people are more likely to finish a long online course if they "
            "regularly see how much progress they have made."),
          P_FINDING,
          "Students in an online course who were shown a progress bar after each lesson completed the course more often "
          "than students in the same course who were not shown one.",
          ["Most students who signed up for online courses were working adults.",
           "Students who finished the course rated it highly.",
           "The online course included both video lessons and quizzes."],
          "Showing progress led to more completions, directly supporting Costa's claim."),
        Q(COEQ,
          p("A school tested ways of encouraging students to eat vegetables at lunch. Staff concluded that serving "
            "vegetables before the rest of the meal had a larger effect than giving them appealing names on the menu, "
            "though combining the two worked best: ___"),
          P_GRAPH,
          "students ate 47% of vegetables served first and 41% of vegetables named on the menu, compared with 58% when "
          "both approaches were used.",
          ["students ate 32% of vegetables served on the side.",
           "students ate 41% of vegetables served first and 47% of vegetables named on the menu.",
           "students ate 58% of vegetables named on the menu."],
          "Only this choice compares the two approaches correctly and shows the combination did best.",
          figure=fig_lunch),
        Q(COEQ,
          p("Conservationists installed nest boxes for barn owls in Hollin Valley in 2012. They argue that the boxes "
            "helped the owls, noting that the number of nesting pairs ___"),
          P_GRAPH,
          "stayed between about 12 and 14 before 2012 but rose to about 44 by 2021.",
          ["was about 14 in 2006.",
           "fell from about 14 to about 12 between 2006 and 2009.",
           "rose every year shown from 2006 to 2021."],
          "A flat count before the boxes and a steady rise afterward supports the conservationists' argument.",
          figure=fig_owls),
        Q(COEQ,
          p("Engineers tested whether recycled glass could replace some of the sand in concrete. They concluded that "
            "small amounts of glass had little effect on strength but that large amounts weakened the concrete: ___"),
          P_TABLE,
          "mixtures with 10% and 20% glass had strengths of 33 and 31 megapascals, close to the standard's 32, while the "
          "mixture with 40% glass had a strength of only 24.",
          ["the standard mixture contained no recycled glass.",
           "the mixture with 10% glass was the strongest of the four mixtures.",
           "every mixture containing glass was weaker than the standard mixture."],
          "Only this choice shows both parts of the conclusion; the last choice is inaccurate.",
          figure=fig_concrete),
        Q(INF,
          p("Many tree species produce huge seed crops in some years and almost none in others, a pattern called "
            "masting. Ecologist Rhys Morgan found that in a forest of oaks, mice that eat acorns became very numerous "
            "after a mast year but then declined sharply in the following lean years. In mast years, so many acorns "
            "were produced that the mice could not eat them all, and many sprouted. These findings suggest that ___"),
          P_INFER,
          "masting may help oaks reproduce by producing more seeds than seed-eating animals can consume.",
          ["oaks produce more acorns when mice are numerous.",
           "mice prefer acorns to all other foods.",
           "acorns sprout only in years when no mice are present."],
          "In mast years more acorns survive and sprout because the mice cannot eat them all."),
        Q(FSS,
          blank("Each of the paintings in the exhibit ___ accompanied by a short recording in which the artist describes "
                "how it was made."),
          P_SEC, "is", ["are", "were", "have been"],
          "The subject is the singular “each,” so the verb is <em>is</em>."),
        Q(BND,
          blank("The bakery opens at 6:00 a.m. on ___ on weekends it opens at 8:00 a.m."),
          P_SEC, "weekdays;", ["weekdays,", "weekdays", "weekdays, and, on"],
          "Two independent clauses are joined with a semicolon."),
        Q(FSS,
          blank("The city's population grew rapidly in the 1950s, and by 1960 it ___ nearly doubled."),
          P_SEC, "had", ["has", "will have", "is"],
          "The doubling was completed by a past time (1960), so the past perfect <em>had</em> doubled is needed."),
        Q(BND,
          blank("The mathematician Srinivasa Ramanujan, who had little formal training in ___ produced thousands of "
                "results, many of which are still being studied today."),
          P_SEC, "mathematics,", ["mathematics", "mathematics;", "mathematics:"],
          "The nonessential clause “who had little formal training in mathematics” must be closed with a comma."),
        Q(FSS,
          blank("The museum offers guided tours in five languages, ___ visitors from many countries to enjoy the "
                "exhibits."),
          P_SEC, "allowing", ["allows", "allowed", "it allows"],
          "The participle phrase “allowing visitors …” correctly describes the result of the first clause; the other "
          "choices create errors."),
        Q(BND,
          blank("The garden has two sections: one for vegetables and one for ___ each section is cared for by a "
                "different group of volunteers."),
          P_SEC, "flowers.", ["flowers,", "flowers", "flowers, and, each"],
          "A period ends the first sentence; a comma would create a comma splice."),
        Q(FSS,
          blank("Of all the planets in the solar system, Jupiter has the ___ number of known moons; only Saturn has "
                "more."),
          P_SEC, "second-largest", ["second-larger", "second-most large", "second-largely"],
          "Ranking among many planets calls for the superlative “largest,” here “second-largest.”"),
        Q(TRN,
          blank("Penguins cannot fly. ___ they are excellent swimmers, using their wings like flippers to move quickly "
                "through the water."),
          P_TRANSITION, "However,", ["Therefore,", "Similarly,", "For example,"],
          "Swimming well contrasts with being unable to fly."),
        Q(TRN,
          blank("The council approved the new park in March. ___ construction began in June and was finished before the "
                "end of the year."),
          P_TRANSITION, "Subsequently,", ["Nevertheless,", "In contrast,", "Likewise,"],
          "Construction followed the approval in time."),
        Q(TRN,
          blank("Some languages have no word for “blue” and use the same word for blue and green. ___ some languages "
                "have two separate words for light blue and dark blue."),
          P_TRANSITION, "Conversely,", ["Accordingly,", "For instance,", "In other words,"],
          "Having two words for blue is the opposite of having none."),
        Q(RS,
          notes(["The Sahara is the largest hot desert in the world.",
                 "Between about 11,000 and 5,000 years ago, much of it was covered by grasslands and lakes.",
                 "Rock art from that period shows giraffes, elephants, and cattle.",
                 "Changes in Earth's orbit are thought to have shifted rainfall patterns and dried the region."],
                "The student wants to emphasize how much the Sahara has changed."),
          P_NOTES_Q,
          "Although the Sahara is now the world's largest hot desert, between about 11,000 and 5,000 years ago much of it "
          "was covered by grasslands and lakes.",
          ["The Sahara is the largest hot desert in the world.",
           "Rock art in the Sahara shows giraffes, elephants, and cattle.",
           "Changes in Earth's orbit are thought to have shifted rainfall patterns."],
          "Only this choice contrasts the Sahara's past and present."),
        Q(RS,
          notes(["Hummingbirds have the highest metabolism of any bird.",
                 "Their hearts can beat more than 1,000 times per minute while they fly.",
                 "At night, many hummingbirds enter a state called torpor.",
                 "During torpor, their heart rate and body temperature drop sharply, saving energy."],
                "The student wants to explain how hummingbirds save energy."),
          P_NOTES_Q,
          "At night, many hummingbirds save energy by entering torpor, during which their heart rate and body "
          "temperature drop sharply.",
          ["Hummingbirds have the highest metabolism of any bird.",
           "A hummingbird's heart can beat more than 1,000 times per minute while it flies.",
           "Many hummingbirds enter a state called torpor."],
          "Only this choice explains how torpor saves energy."),
        Q(RS,
          notes(["Ida B. Wells was an American journalist born in 1862.",
                 "In the 1890s she investigated and reported on lynchings in the southern United States.",
                 "She gathered evidence from newspapers, eyewitnesses, and public records.",
                 "In 2020 she was awarded a posthumous Pulitzer Prize special citation."],
                "The student wants to emphasize the methods Wells used in her reporting."),
          P_NOTES_Q,
          "In reporting on lynchings in the 1890s, Ida B. Wells gathered evidence from newspapers, eyewitnesses, and "
          "public records.",
          ["Ida B. Wells was an American journalist born in 1862.",
           "In 2020 Ida B. Wells was awarded a posthumous Pulitzer Prize special citation.",
           "In the 1890s Ida B. Wells reported on lynchings in the southern United States."],
          "Only this choice describes her methods."),
    ]


def module_2():
    fig_remote = grouped_bar_chart(
        "Employees Reporting High Job Satisfaction",
        ["Engineering", "Sales", "Support"],
        [("Office only", [61, 58, 49]), ("Hybrid schedule", [74, 57, 68])],
        "Percentage of employees", 80,
        "Grouped bar graph of the share of employees reporting high job satisfaction under office-only and hybrid "
        "schedules in three departments",
    )
    fig_reef = line_chart(
        "Coral Cover on Two Reefs, 2010–2022",
        [2010, 2012, 2014, 2016, 2018, 2020, 2022],
        [("Protected reef", [42, 41, 43, 30, 34, 39, 44]), ("Unprotected reef", [40, 37, 35, 22, 21, 20, 19])],
        "Coral cover (%)", (0, 50),
        "Line graph of coral cover: both reefs drop in 2016; the protected reef recovers to 44% by 2022 while the "
        "unprotected reef stays near 20%",
        note=(2016, "Heat wave"),
    )
    fig_fruit = table_image(
        "Vitamin C in Fruit Stored for One Week",
        ["Fruit", "When picked (mg per 100 g)", "After one week (mg per 100 g)"],
        [["Strawberries", "60", "41"], ["Oranges", "53", "50"], ["Kiwis", "90", "84"]],
        "Table of vitamin C levels in strawberries, oranges and kiwis when picked and after one week",
        col_widths=[0.28, 0.36, 0.36],
    )
    return [
        Q(WIC,
          blank("Although the treaty's language was ___, its meaning was clear to both sides: neither country would "
                "build new forts along the border."),
          P_WIC, "convoluted", ["explicit", "concise", "casual"],
          "“Although” contrasts complicated language with a clear meaning, so the wording was <em>convoluted</em>."),
        Q(WIC,
          blank("The study's authors were careful to ___ their conclusions, noting that the results applied only to "
                "adults over sixty and might not hold for younger people."),
          P_WIC, "qualify", ["exaggerate", "abandon", "publicize"],
          "Limiting a conclusion to one group is to <em>qualify</em> it."),
        Q(WIC,
          blank("The village's traditions have proved remarkably ___: despite a century of rapid change, residents still "
                "celebrate the harvest with the same songs and dances their great-grandparents performed."),
          P_WIC, "durable", ["fleeting", "foreign", "costly"],
          "Traditions that survive a century of change are <em>durable</em>."),
        Q(WIC,
          blank("The chef's menu is deliberately ___, offering only five dishes, each made from ingredients grown on the "
                "restaurant's own farm."),
          P_WIC, "limited", ["extensive", "random", "expensive"],
          "Offering only five dishes makes the menu <em>limited</em>."),
        Q(TSP,
          p("The first vaccines against smallpox were made from material taken from cowpox sores. For more than a "
            "century, the method changed little. In the twentieth century, scientists learned to grow viruses in "
            "laboratory cultures, which made it possible to produce vaccines in large, consistent batches. These "
            "advances helped make possible a worldwide vaccination campaign, and in 1980 the World Health Organization "
            "declared smallpox eradicated."),
          P_STRUCTURE,
          "It traces how methods of making a vaccine developed over time and connects them to an important outcome.",
          ["It compares smallpox with cowpox and explains why one disease is more dangerous.",
           "It argues that the earliest vaccines were more effective than later ones.",
           "It describes the work of the World Health Organization and lists its other campaigns."],
          "The text moves from early cowpox material, to laboratory production, to the eradication of smallpox."),
        Q(TSP,
          underline("Nearly every culture has stories about floods. ",
                    "Some researchers have suggested that a few of these stories may preserve memories of real events, "
                    "such as rising sea levels at the end of the last ice age, when coastlines in many parts of the "
                    "world moved inland.",
                    " Others caution that floods are common enough that such stories need no single historical source."),
          P_FUNCTION,
          "It presents one possible explanation that the final sentence then qualifies.",
          ["It describes how sea levels are measured today.",
           "It gives an example of a flood story from a particular culture.",
           "It argues that all flood stories describe the same event."],
          "The underlined sentence offers an explanation; the final sentence adds a note of caution."),
        Q(CTC,
          texts("Many psychologists have argued that boredom is simply an unpleasant state that people should try to "
                "avoid, since it tends to lower mood and motivation.",
                "Psychologist Sandra Lindgren gave participants a dull task, such as copying numbers from a phone book, "
                "before asking them to think of creative uses for everyday objects. Participants who had done the dull "
                "task came up with more creative ideas than participants who had not. Lindgren suggests that boredom "
                "may encourage the mind to wander in useful ways."),
          "Based on the texts, how would Lindgren (Text 2) most likely respond to the psychologists' view in Text 1?",
          "By suggesting that boredom may have benefits that the view does not consider",
          ["By agreeing that boredom always lowers motivation and should be avoided",
           "By arguing that copying numbers is an effective way to improve mood",
           "By claiming that creative people are never bored"],
          "Lindgren's finding that boredom boosted creativity points to an overlooked benefit."),
        Q(CID,
          p("Most bird species can fly, but flight is costly: it demands large amounts of energy and strong, lightweight "
            "bodies. On islands without predators, several bird species have lost the ability to fly over many "
            "generations. Without threats to escape from, these birds could survive by walking and running, and "
            "energy that would have been spent on flight could go to other needs, such as producing eggs."),
          P_MAIN_IDEA,
          "Because flight is costly, some birds on islands without predators have lost the ability to fly over time.",
          ["Birds that live on islands are always larger than birds on the mainland.",
           "Flightless birds can no longer produce eggs.",
           "Predators on islands have caused many birds to lose the ability to fly."],
          "The text explains the cost of flight and why the absence of predators allowed some birds to lose it."),
        Q(CID,
          p("The following text is from a short story. Kwame has just moved into his first apartment.")
          + p("The apartment was smaller than it had looked in the photos, and the kitchen faucet dripped no matter how "
              "hard he turned it. Kwame unpacked his boxes anyway, lining up his books on the windowsill because he had "
              "no shelves yet. That evening he cooked rice in the one pot he owned and ate it sitting on the floor, "
              "watching the lights come on across the street. It was not much, he thought. But it was his."),
          P_MAIN_IDEA,
          "Despite the apartment's flaws, Kwame takes satisfaction in having a place of his own.",
          ["Kwame regrets moving out of his family's home.",
           "Kwame plans to fix the faucet before unpacking his boxes.",
           "Kwame dislikes his neighbors across the street."],
          "He notices the problems but ends feeling that the modest apartment is his own."),
        Q(COET,
          p("Economist Leila Farah claims that a city's new subway line raised the value of homes located near its "
            "stations."),
          P_FINDING,
          "After the line opened, home prices rose faster near the new stations than in similar neighborhoods farther "
          "away, though prices in both areas had risen at the same rate before.",
          ["Many residents said that the subway line made commuting easier.",
           "Home prices in the city as a whole rose during the decade.",
           "The subway line was completed ahead of schedule."],
          "Faster price growth only near the stations, after similar growth before, points to the subway as the cause."),
        Q(COEQ,
          p("A company let employees in three departments choose a hybrid schedule, working some days from home. A "
            "manager notes that the change seemed to raise satisfaction in two departments but not in Sales, where the "
            "percentage of employees reporting high satisfaction ___"),
          P_GRAPH,
          "was about the same under both schedules (58% and 57%).",
          ["rose from 49% to 68%.",
           "rose from 61% to 74%.",
           "was higher than in Engineering under both schedules."],
          "Sales shows almost no change, as the manager says.",
          figure=fig_remote),
        Q(COEQ,
          p("A marine biologist compared two reefs, one protected from fishing and pollution and one not. Both were "
            "damaged by a heat wave in 2016. The biologist argues that protection helped the reef recover: ___"),
          P_GRAPH,
          "coral cover on the protected reef rose from about 30% after the heat wave to about 44% by 2022, while cover "
          "on the unprotected reef stayed near 20%.",
          ["both reefs lost coral cover in 2016.",
           "coral cover on the unprotected reef was about 40% in 2010.",
           "coral cover on the unprotected reef rose to about 44% by 2022."],
          "Only this choice contrasts the protected reef's recovery with the unprotected reef's lack of recovery.",
          figure=fig_reef),
        Q(COEQ,
          p("A nutrition student claims that the vitamin C in some fruits breaks down much faster during storage than "
            "in others. For example, after one week ___"),
          P_TABLE,
          "strawberries had lost about a third of their vitamin C (60 to 41 mg), while oranges had lost very little "
          "(53 to 50 mg).",
          ["kiwis had the most vitamin C of the three fruits.",
           "oranges had 50 mg of vitamin C per 100 g.",
           "oranges had lost more vitamin C than strawberries."],
          "Only this choice compares a large loss with a small one.",
          figure=fig_fruit),
        Q(INF,
          p("Some frogs in cold regions survive winter by freezing almost solid. Biologist Erik Holm found that as "
            "temperatures drop, these frogs fill their cells with high concentrations of glucose, a kind of sugar. In "
            "laboratory tests, frog tissues treated with similar amounts of glucose suffered much less damage from "
            "freezing than untreated tissues. These findings suggest that ___"),
          P_INFER,
          "glucose may help protect the frogs' cells from being damaged by freezing.",
          ["frogs in cold regions eat more sugar in winter than in summer.",
           "freezing makes frogs' cells produce less glucose.",
           "frogs in warm regions cannot survive freezing because they lack cells."],
          "Glucose reduced freezing damage in tissues, which points to its protective role."),
        Q(BND,
          blank("Marie Curie won Nobel Prizes in two different ___ physics in 1903 and chemistry in 1911."),
          P_SEC, "sciences:", ["sciences;", "sciences, they were", "sciences"],
          "A colon introduces the two sciences that explain “two different sciences.”"),
        Q(FSS,
          blank("The flock of geese that rests on the lake each autumn ___ grown larger every year."),
          P_SEC, "has", ["have", "are", "were"],
          "The subject is the singular “flock,” so the verb is <em>has</em>."),
        Q(BND,
          blank("The old train station, which had been empty for ___ was converted into a public market in 2019."),
          P_SEC, "decades,", ["decades", "decades;", "decades—"],
          "The nonessential clause that begins with a comma after “station” must end with a comma."),
        Q(FSS,
          blank("Hoping to see the eclipse, ___"),
          P_SEC,
          "the family drove three hours to a town with clear skies.",
          ["the town with clear skies was three hours away from the family.",
           "a three-hour drive took the family to a town with clear skies.",
           "clear skies were found by the family in a town three hours away."],
          "The family did the hoping, so “the family” must follow the opening phrase."),
        Q(BND,
          blank("The museum's newest exhibit features clothing from the 1920s, including beaded dresses, wool coats, "
                "and ___ hats."),
          P_SEC, "felt", ["felt,", "felt;", "felt:"],
          "No punctuation belongs between the adjective “felt” and the noun “hats.”"),
        Q(FSS,
          blank("The researchers found that students who read for pleasure scored higher on vocabulary tests than "
                "___"),
          P_SEC, "students who did not.", ["the scores of students who did not.", "that of students who did not.",
                                           "students' who did not."],
          "Students are compared with other students; comparing students with “scores” or “that” is illogical."),
        Q(FSS,
          blank("If more people ___ public transportation, the city's air would be cleaner."),
          P_SEC, "used", ["use", "will use", "would use"],
          "A hypothetical present condition uses the past form <em>used</em> with “would” in the result."),
        Q(TRN,
          blank("The first draft of the report was nearly two hundred pages long. ___ the final version, after careful "
                "editing, was just sixty pages."),
          P_TRANSITION, "By contrast,", ["Similarly,", "Therefore,", "For example,"],
          "The short final version contrasts with the long first draft."),
        Q(TRN,
          blank("Many deep-sea fish are red. ___ red light does not reach the deep ocean, these fish appear black and "
                "are nearly invisible."),
          P_TRANSITION, "Because", ["Although", "Unless", "Whereas"],
          "The fish look black for this reason: red light does not reach them."),
        Q(TRN,
          blank("The team spent a year studying how people use public benches. ___ they found that benches facing a "
                "view were used twice as often as benches facing a wall."),
          P_TRANSITION, "Among other things,", ["Nevertheless,", "In contrast,", "Even so,"],
          "The bench finding is one of several things the study found."),
        Q(RS,
          notes(["The Dead Sea is a salt lake in the Middle East.",
                 "Its surface is about 430 meters below sea level, the lowest point on land on Earth.",
                 "Its water is about ten times saltier than ocean water.",
                 "Because the water is so salty, people float easily in it."],
                "The student wants to explain why people float easily in the Dead Sea."),
          P_NOTES_Q,
          "People float easily in the Dead Sea because its water is about ten times saltier than ocean water.",
          ["The Dead Sea is a salt lake in the Middle East.",
           "The surface of the Dead Sea is the lowest point on land on Earth.",
           "The Dead Sea is about 430 meters below sea level."],
          "Only this choice gives the reason people float."),
        Q(RS,
          notes(["A study tested whether doodling affects memory.",
                 "Participants listened to a dull phone message.",
                 "Half were asked to doodle while listening, and half were not.",
                 "The doodlers remembered about 29 percent more information from the message."],
                "The student wants to present the study's result to readers who think doodling is a distraction."),
          P_NOTES_Q,
          "Although doodling is often seen as a distraction, participants in one study who doodled while listening to a "
          "message remembered about 29 percent more of it.",
          ["In one study, participants listened to a dull phone message.",
           "Half of the participants in one study were asked to doodle.",
           "A study tested whether doodling affects memory."],
          "Only this choice presents the result and addresses the view that doodling distracts."),
        Q(RS,
          notes(["Kazimir Malevich was a Russian painter born in 1879.",
                 "In 1915 he exhibited <em>Black Square</em>, a painting of a black square on a white background.",
                 "He called his style Suprematism.",
                 "Suprematism focused on simple geometric shapes rather than recognizable objects."],
                "The student wants to describe the main idea of Suprematism."),
          P_NOTES_Q,
          "Suprematism, the style developed by Kazimir Malevich, focused on simple geometric shapes rather than "
          "recognizable objects.",
          ["Kazimir Malevich was a Russian painter born in 1879.",
           "In 1915 Malevich exhibited <em>Black Square</em>.",
           "Kazimir Malevich called his style Suprematism."],
          "Only this choice explains what Suprematism focused on."),
    ]
