"""Academor SAT Practice Test 3 — Reading and Writing."""

from sat_verbal.common import (
    BND, CID, COEQ, COET, CTC, FSS, INF, P_CLAIM, P_FINDING, P_FUNCTION, P_GRAPH, P_INFER, P_MAIN_IDEA,
    P_NOTES_Q, P_PURPOSE, P_SEC, P_STRUCTURE, P_TABLE, P_TRANSITION, P_WEAKEN, P_WIC, Q, RS, TRN, TSP,
    WIC, bar_chart, blank, grouped_bar_chart, line_chart, notes, p, table_image, texts, underline,
)


def module_1():
    fig_commute = bar_chart(
        "Average One-Way Commute Time in Harlow by Travel Mode",
        ["Car", "Bus", "Bicycle", "Train"],
        [27, 41, 22, 34],
        "Minutes", 50,
        "Bar graph of average commute times in Harlow: car 27, bus 41, bicycle 22 and train 34 minutes",
        value_fmt="{:.0f}",
    )
    fig_music = line_chart(
        "Physical Music Sales in Country Q, 2014–2022",
        [2014, 2016, 2018, 2020, 2022],
        [("CDs", [48, 37, 26, 17, 12]), ("Vinyl records", [4, 7, 11, 15, 19])],
        "Millions of units sold", (0, 50),
        "Line graph of CD sales falling from 48 to 12 million and vinyl sales rising from 4 to 19 million between "
        "2014 and 2022 in Country Q",
    )
    fig_drivers = table_image(
        "Average Driver Reaction Time in a Simulator",
        ["Condition", "Reaction time (seconds)"],
        [["No distraction", "0.71"], ["Talking with a passenger", "0.84"], ["Hands-free phone call", "0.98"],
         ["Reading a text message", "1.46"]],
        "Table of average driver reaction times in four conditions",
        col_widths=[0.6, 0.4],
    )
    return [
        Q(WIC,
          blank("The restorer's work on the damaged painting was ___: over two years she removed centuries of grime "
                "with brushes no wider than a few hairs, checking each section under a microscope before moving on."),
          P_WIC, "meticulous", ["hurried", "lavish", "careless"],
          "Tiny brushes and checking every section under a microscope describe extremely careful, or "
          "<em>meticulous</em>, work."),
        Q(WIC,
          blank("Tiny particles of plastic have become ___ in the environment: researchers have found them in "
                "deep-ocean sediments, in snow on remote mountains, and in drinking water."),
          P_WIC, "pervasive", ["scarce", "harmless", "temporary"],
          "Being found in places from the deep ocean to remote mountains means the particles are everywhere, or "
          "<em>pervasive</em>."),
        Q(WIC,
          blank("Although the composer's early works followed the conventions of her time, her later pieces were "
                "strikingly ___, using unusual scales and irregular rhythms that puzzled many listeners."),
          P_WIC, "innovative", ["traditional", "repetitive", "cautious"],
          "“Although” sets the later pieces against conventional early works; unusual scales and rhythms show they "
          "were <em>innovative</em>."),
        Q(WIC,
          blank("The senator was known for her ___ manner: she rarely raised her voice and preferred to win over "
                "opponents through patient, carefully reasoned argument."),
          P_WIC, "measured", ["volatile", "evasive", "indifferent"],
          "A calm, patient, reasoned style is <em>measured</em>; “volatile” is the opposite."),
        Q(TSP,
          underline("Rosalind Franklin's contribution to the discovery of the structure of DNA was long overlooked. ",
                    "Her X-ray images of DNA, including one now known as Photo 51, provided key evidence that the "
                    "molecule has a helical shape.",
                    " Yet when James Watson and Francis Crick published their model of DNA in 1953, Franklin's role "
                    "received little public recognition."),
          P_FUNCTION,
          "It explains what Franklin contributed, a contribution the text says was overlooked.",
          ["It describes an experiment that Watson and Crick carried out to test Franklin's results.",
           "It argues that Franklin's images were more important than Watson and Crick's model.",
           "It introduces a disagreement about the shape of DNA that the text goes on to resolve."],
          "The first sentence says Franklin's contribution was overlooked; the underlined sentence states what that "
          "contribution was."),
        Q(TSP,
          p("When a honeybee colony outgrows its hive, thousands of bees leave with the queen and cluster on a "
            "branch while a few hundred scouts search for a new home. A scout that finds a promising cavity returns "
            "and performs a dance that advertises it, and other scouts fly off to inspect the site. Over hours or "
            "days, more and more scouts dance for the best site, until enough of them have gathered there and the "
            "whole swarm flies to its new home."),
          P_PURPOSE,
          "To describe how a honeybee swarm chooses a new place to live",
          ["To explain why honeybee colonies sometimes outgrow their hives",
           "To compare the dances of honeybee scouts with those of other insects",
           "To argue that honeybee scouts often choose poor nest sites"],
          "The text follows the process from the swarm leaving the hive to the choice of the best site."),
        Q(CTC,
          texts("Some art historians argue that the bright colors of Impressionist painting were made possible largely "
                "by new materials. Paint sold in metal tubes allowed artists to work outdoors, and newly invented "
                "pigments gave them vivid colors that earlier painters had not been able to use.",
                "Art historian Inès Dubois points out that several leading Impressionists continued to rely on "
                "traditional pigments for much of their careers. In her view, the movement's brightness came mainly "
                "from the artists' interest in capturing changing outdoor light, an interest that would have shaped "
                "their work even without new materials."),
          "Based on the texts, how would Dubois (Text 2) most likely respond to the art historians' argument in Text 1?",
          "By suggesting that it overstates the role of new materials in shaping Impressionist painting",
          ["By agreeing that Impressionist painters could not have worked outdoors without paint tubes",
           "By claiming that Impressionist painters used only newly invented pigments",
           "By arguing that Impressionist paintings were less colorful than earlier paintings"],
          "Dubois credits the artists' interest in light rather than new materials, and notes that leading painters "
          "kept using traditional pigments."),
        Q(CID,
          p("The narwhal, a whale of the Arctic Ocean, is known for its long, spiral tusk, which is actually a tooth "
            "that grows through the animal's upper lip. For centuries, people assumed the tusk was used mainly as a "
            "weapon. Some researchers now propose a different main purpose: the tusk contains millions of nerve "
            "endings that connect the outside of the tooth to the animal's brain, and they suggest the tusk may help "
            "narwhals sense changes in the water around them."),
          P_MAIN_IDEA,
          "Some researchers think the narwhal's tusk may serve mainly as a sense organ rather than as a weapon.",
          ["The narwhal's tusk grows through the animal's lower jaw rather than its lip.",
           "Narwhals use their tusks mainly to fight other narwhals during the breeding season.",
           "Researchers have proved that narwhals use their tusks to find food."],
          "The text contrasts the old weapon idea with the newer proposal that the tusk senses the water."),
        Q(CID,
          p("The following text is from a short story. Tomas, age twelve, has just lost a chess match at his first "
            "tournament.")
          + p("He shook his opponent's hand without looking up. On the bus home, while his mother talked about dinner, "
              "Tomas replayed the game on the small magnetic board in his lap, moving the pieces back to the "
              "twenty-third move, where his bishop had wandered into danger. He tried a different square, then "
              "another. By the time the bus reached their stop, he had found the move he should have made, and he "
              "was already wondering when the next tournament would be."),
          P_MAIN_IDEA,
          "After losing, Tomas studies his mistake and becomes eager to compete again.",
          ["Tomas is so upset by his loss that he refuses to talk to his mother.",
           "Tomas blames his opponent for distracting him during the match.",
           "Tomas decides that tournament chess is too stressful for him."],
          "Tomas replays the game, finds the better move and looks forward to the next tournament."),
        Q(COET,
          p("Red foxes that live in cities often approach people more closely than foxes in the countryside do. "
            "Biologist Megan Holloway hypothesizes that city foxes have become less fearful because many of them are "
            "regularly given food by residents."),
          P_FINDING,
          "Within the same city, foxes in neighborhoods where residents often leave out food approached people more "
          "closely than foxes in neighborhoods where residents rarely do.",
          ["City foxes are, on average, slightly larger than foxes in the countryside.",
           "Foxes in the countryside are more active at night than during the day.",
           "The number of foxes living in the city has increased over the past thirty years."],
          "This finding links closeness to people directly to being fed, while keeping the city setting the same."),
        Q(COEQ,
          p("A city planner in Harlow is writing a report on travel times. The planner notes that cycling is the "
            "fastest way for many residents to get to work, with an average commute time of ___"),
          P_GRAPH,
          "22 minutes, shorter than the average for travel by car, bus, or train.",
          ["27 minutes, shorter than the average for travel by bus.",
           "41 minutes, the longest of the four travel modes.",
           "22 minutes, about the same as the average for travel by train."],
          "The claim is that cycling is fastest; only this choice gives the bicycle time and correctly says it is the "
          "shortest.",
          figure=fig_commute),
        Q(COEQ,
          p("Although sales of CDs in Country Q fell steadily between 2014 and 2022, a music journalist argues that "
            "interest in physical recordings has not disappeared, pointing out that during the same period ___"),
          P_GRAPH,
          "sales of vinyl records rose from about 4 million to about 19 million.",
          ["sales of CDs fell from about 48 million to about 12 million.",
           "sales of vinyl records were higher than sales of CDs in every year shown.",
           "sales of vinyl records fell from about 19 million to about 4 million."],
          "Rising vinyl sales show continuing interest in physical recordings despite the fall in CD sales.",
          figure=fig_music),
        Q(COEQ,
          p("Researchers measured how quickly drivers in a simulator could press the brake when an obstacle appeared. "
            "They concluded that a phone conversation slows drivers more than a conversation with a passenger, even "
            "when the driver's hands stay free: average reaction time was ___"),
          P_TABLE,
          "0.98 seconds during a hands-free phone call, compared with 0.84 seconds while talking with a passenger.",
          ["1.46 seconds while reading a text message, compared with 0.71 seconds with no distraction.",
           "0.84 seconds while talking with a passenger, compared with 0.71 seconds with no distraction.",
           "0.98 seconds while talking with a passenger, compared with 0.84 seconds during a hands-free phone call."],
          "The conclusion compares a hands-free call with talking to a passenger; only this choice reports those two "
          "values correctly.",
          figure=fig_drivers),
        Q(INF,
          p("At a village site about 3,000 years old, archaeologists found hundreds of pieces of pottery. Chemical "
            "analysis showed that most pieces were made from clay dug near the village, but about a tenth were made "
            "from a clay found only in a valley more than 200 kilometers away. The village shows no sign that its "
            "residents ever traveled that far. These findings suggest that ___"),
          P_INFER,
          "the villagers may have obtained some pottery through trade with other communities.",
          ["the villagers moved to the distant valley after they stopped making pottery.",
           "pottery made from local clay was of higher quality than pottery from the valley.",
           "the distant valley was not inhabited 3,000 years ago."],
          "Pottery from a distant clay source, without signs that villagers traveled there, points to exchange with "
          "others."),
        Q(FSS,
          blank("The results of the survey, which asked more than 2,000 residents about local parks, ___ that most "
                "people visit a park at least once a week."),
          P_SEC, "show", ["shows", "has shown", "is showing"],
          "The subject is the plural “results,” so the verb must be plural: <em>show</em>."),
        Q(BND,
          blank("The museum had planned to close the exhibit in ___ record attendance, the directors decided to keep "
                "it open through the summer."),
          P_SEC, "May; however, because of", ["May, however, because of", "May however because of", "May; however because of"],
          "“However” joins two independent clauses, so it needs a semicolon before it and a comma after it."),
        Q(FSS,
          blank("The orchestra announced that ___ would perform a free concert in the city park on the first Sunday of "
                "every month."),
          P_SEC, "it", ["they", "we", "one"],
          "“Orchestra” is a singular noun here, so the singular pronoun <em>it</em> refers to it."),
        Q(BND,
          blank("Kente cloth, a fabric woven in narrow strips by the Asante and Ewe peoples of West ___ known for its "
                "bright colors and geometric patterns."),
          P_SEC, "Africa, is", ["Africa is", "Africa; is", "Africa—is"],
          "The appositive that begins with a comma after “cloth” must close with a comma before the verb “is.”"),
        Q(FSS,
          blank("By the end of the nineteenth century, railroads ___ the time it took to cross the United States from "
                "several months to about a week."),
          P_SEC, "had reduced", ["reduce", "will reduce", "are reducing"],
          "“By the end of the nineteenth century” describes an action completed before a past time, so the past "
          "perfect <em>had reduced</em> fits."),
        Q(BND,
          blank("The recipe calls for three kinds of ___ cardamom, cinnamon, and cloves."),
          P_SEC, "spice:", ["spice;", "spice,", "spice, they are"],
          "A colon introduces the list that names the three spices."),
        Q(FSS,
          blank("Every one of the paintings in the gallery's new wing ___ been cleaned and reframed before the "
                "reopening."),
          P_SEC, "has", ["have", "are", "were"],
          "The subject is “every one,” which is singular, so the verb is <em>has</em>."),
        Q(TRN,
          blank("Sharks have no bones; their skeletons are made of cartilage. ___ their fossil record consists mostly of "
                "teeth, which are hard enough to survive for millions of years."),
          P_TRANSITION, "As a result,", ["In contrast,", "For example,", "Meanwhile,"],
          "Because cartilage rarely fossilizes, the fossil record is mostly teeth: a consequence."),
        Q(TRN,
          blank("The early versions of the app were difficult to use. ___ the newest version, which was redesigned with "
                "help from hundreds of test users, has received excellent reviews."),
          P_TRANSITION, "By contrast,", ["Similarly,", "Therefore,", "For instance,"],
          "The well-reviewed new version contrasts with the difficult early versions."),
        Q(TRN,
          blank("The novel is set in a single small town over just three days. ___ it manages to touch on almost every "
                "major event in the town's two-hundred-year history."),
          P_TRANSITION, "Nevertheless,", ["Accordingly,", "Likewise,", "In other words,"],
          "Covering two centuries despite a three-day setting is unexpected, which “Nevertheless” signals."),
        Q(RS,
          notes(["The Rosetta spacecraft was launched by the European Space Agency in 2004.",
                 "It traveled for ten years to reach a comet called 67P.",
                 "In 2014 it released a small lander called Philae.",
                 "Philae became the first spacecraft to land on the surface of a comet."],
                "The student wants to emphasize the historic achievement of the Rosetta mission."),
          P_NOTES_Q,
          "In 2014 the Rosetta mission's Philae lander became the first spacecraft ever to land on a comet.",
          ["The Rosetta spacecraft was launched by the European Space Agency in 2004.",
           "Rosetta traveled for ten years to reach a comet called 67P.",
           "The Rosetta spacecraft carried a small lander called Philae."],
          "Only this choice states the first-ever landing on a comet."),
        Q(RS,
          notes(["Bamboo is a type of grass.",
                 "Some species of bamboo can grow almost a meter in a single day.",
                 "Oak trees usually grow less than a meter per year.",
                 "Both bamboo and oak are used as building materials."],
                "The student wants to contrast the growth rates of bamboo and oak."),
          P_NOTES_Q,
          "While some bamboo species can grow almost a meter in a day, oak trees usually grow less than a meter in a "
          "whole year.",
          ["Both bamboo and oak are used as building materials.",
           "Bamboo, which is a type of grass, is used as a building material.",
           "Some species of bamboo can grow almost a meter in a single day."],
          "Only this choice compares the two growth rates."),
        Q(RS,
          notes(["Ibn Battuta was a scholar born in Tangier, Morocco, in 1304.",
                 "Over about thirty years he traveled through North Africa, the Middle East, Central Asia, India, and "
                 "China.",
                 "His travels covered roughly 120,000 kilometers.",
                 "After returning home, he dictated an account of his journeys, known as the <em>Rihla</em>."],
                "The student wants to introduce Ibn Battuta to readers who are unfamiliar with him."),
          P_NOTES_Q,
          "Ibn Battuta, a fourteenth-century scholar from Morocco, traveled for about thirty years across Africa and "
          "Asia and later described his journeys in a book known as the <em>Rihla</em>.",
          ["Ibn Battuta's travels covered roughly 120,000 kilometers.",
           "The <em>Rihla</em> was dictated after Ibn Battuta returned home.",
           "Ibn Battuta traveled through North Africa, the Middle East, Central Asia, India, and China."],
          "Only this choice says who Ibn Battuta was and what he is known for."),
    ]


def module_2():
    fig_sleep = grouped_bar_chart(
        "Average Nightly Sleep of Students Before and After a Later School Start",
        ["Grade 9", "Grade 10", "Grade 11", "Grade 12"],
        [("Start at 7:30", [7.1, 6.9, 6.6, 6.4]), ("Start at 8:30", [7.8, 7.6, 7.3, 6.6])],
        "Hours of sleep", 9,
        "Grouped bar graph of average nightly sleep by grade before and after the school start time moved from 7:30 "
        "to 8:30",
    )
    fig_glacier = line_chart(
        "Length of Tarn Glacier, 1960–2020",
        [1960, 1970, 1980, 1990, 2000, 2010, 2020],
        [("Length", [8.4, 8.3, 8.2, 7.9, 7.3, 6.6, 5.8])],
        "Length (kilometers)", (5, 9),
        "Line graph of the length of Tarn Glacier decreasing slowly from 8.4 kilometers in 1960 to 8.2 in 1980 and "
        "then quickly to 5.8 in 2020",
    )
    fig_reading = table_image(
        "Reading Program Results at Three Schools",
        ["School", "Program?", "Average reading gain (points)"],
        [["Ashford", "Yes", "14"], ["Brookside", "No", "6"], ["Cedar Hill", "Yes", "13"]],
        "Table of average reading gains at three schools, two of which used a reading program",
        col_widths=[0.3, 0.25, 0.45],
    )
    return [
        Q(WIC,
          blank("The historian's account of the strike is admirably ___: she quotes workers, factory owners, and "
                "government officials at length and allows readers to weigh their claims for themselves."),
          P_WIC, "evenhanded", ["sensational", "one-sided", "fragmentary"],
          "Giving every group a full hearing and letting readers decide is <em>evenhanded</em>."),
        Q(WIC,
          blank("Although the scientist's early results seemed to ___ her hypothesis, later experiments with larger "
                "samples failed to reproduce them."),
          P_WIC, "vindicate", ["undermine", "obscure", "complicate"],
          "“Although” contrasts the early results with later failures; the early results seemed to support, or "
          "<em>vindicate</em>, the hypothesis."),
        Q(WIC,
          blank("The ___ of the documents surprised the researchers: a single box in the archive contained letters, "
                "receipts, maps, recipes, and even children's drawings."),
          P_WIC, "heterogeneity", ["uniformity", "scarcity", "authenticity"],
          "A box with many different kinds of documents shows <em>heterogeneity</em>, or variety."),
        Q(WIC,
          blank("Critics praised the actor's ___ performance: rather than shouting or weeping, he conveyed the "
                "character's grief through small gestures and long silences."),
          P_WIC, "restrained", ["flamboyant", "careless", "unrehearsed"],
          "Small gestures and silences instead of shouting show a <em>restrained</em> performance."),
        Q(TSP,
          p("For centuries, sailors told stories of “rogue waves,” single waves far taller than those around them that "
            "appeared without warning. Many scientists dismissed the stories as exaggerations, since standard models "
            "of the ocean predicted that such waves would be extremely rare. Then, on January 1, 1995, a sensor on the "
            "Draupner oil platform in the North Sea recorded a wave about 26 meters high in seas where most waves were "
            "about 12 meters. The measurement prompted researchers to develop new models that could explain how such "
            "waves form."),
          P_STRUCTURE,
          "It describes a phenomenon that was long doubted, presents a measurement that confirmed it, and notes the "
          "research that followed.",
          ["It explains how rogue waves form and then describes how sailors can avoid them.",
           "It compares sailors' stories with scientific models and concludes that both were mistaken.",
           "It describes a measurement and then argues that the sensor that recorded it was faulty."],
          "The text moves from doubted stories, to the 1995 measurement, to the new models it prompted."),
        Q(TSP,
          underline("Many people assume that a desert is defined by heat. ",
                    "Yet Antarctica, the coldest place on Earth, is also the largest desert in the world.",
                    " Scientists define a desert by how little precipitation it receives, and most of Antarctica's "
                    "interior gets less than 5 centimeters of precipitation a year."),
          P_FUNCTION,
          "It presents a fact that seems to contradict the assumption in the first sentence.",
          ["It gives an example that supports the assumption in the first sentence.",
           "It explains why scientists measure precipitation in centimeters.",
           "It introduces a claim that the final sentence shows to be false."],
          "A cold desert challenges the assumption that deserts are defined by heat; the final sentence then "
          "explains why Antarctica counts as a desert."),
        Q(CTC,
          texts("Many urban planners argue that building more roads is the best way to reduce traffic congestion. "
                "More lanes, they say, give the same number of cars more space, so traffic should move faster.",
                "Transportation researcher Kofi Asante studied highways in thirty cities over two decades. He found that "
                "when cities added lanes, the amount of driving increased almost in proportion to the new space, and "
                "within a few years congestion returned to its earlier level. Asante calls this effect “induced "
                "demand”: new roads encourage people to make trips they would not otherwise have made."),
          "Based on the texts, how would Asante (Text 2) most likely respond to the urban planners' argument in Text 1?",
          "By pointing out that it assumes the number of cars stays the same after new lanes are built",
          ["By agreeing that building more roads is the most effective way to reduce congestion",
           "By arguing that congestion is caused mainly by poorly designed traffic lights",
           "By suggesting that the planners studied too few cities to reach a conclusion"],
          "The planners assume “the same number of cars,” but Asante found that new lanes bring more driving."),
        Q(CID,
          p("For a long time, scientists assumed that plants could not respond to sound. Recent studies have begun to "
            "challenge that assumption. In one experiment, researchers played recordings of buzzing bees to "
            "evening primrose flowers. Within minutes, the flowers produced nectar with a higher sugar content than "
            "flowers that heard silence or higher-pitched sounds. The researchers suggest that this response may help "
            "the plants attract pollinators that are nearby."),
          P_MAIN_IDEA,
          "An experiment suggests that some flowers may respond to the sound of bees by making their nectar sweeter.",
          ["Evening primroses produce nectar only when bees are nearby.",
           "Scientists have long known that plants respond to many kinds of sound.",
           "Bees prefer flowers that produce high-pitched sounds."],
          "The text centers on the experiment in which bee sounds led flowers to make sweeter nectar."),
        Q(CID,
          p("The following text is from a short story. Imani has moved from a large city to a small farming town.")
          + p("In the city, Imani had never noticed the sky; buildings had cut it into narrow strips. Here it was "
              "everywhere, and it was never the same twice. In her first weeks she kept a notebook of it—pale green "
              "at the edge of a storm, a flat white like paper in winter, a red so deep at sunset that she stopped her "
              "bicycle on the road to look. She had expected to be bored in the town. Instead she found she had "
              "something new to watch every evening."),
          P_MAIN_IDEA,
          "Imani finds unexpected interest in her new surroundings by observing the changing sky.",
          ["Imani misses the tall buildings of the city where she used to live.",
           "Imani is frightened by the storms in the farming town.",
           "Imani wants to become a painter after she moves to the town."],
          "She expected boredom but discovers the ever-changing sky, which she records and watches each evening."),
        Q(COET,
          p("The following text is from a speech delivered at the opening of a public library. The speaker argues "
            "that libraries serve people of every age and background.")
          + p("“This building will belong to the student preparing for an exam and to the grandmother learning to use "
              "a computer. It will belong to the new arrival practicing a new language and to the child hearing a "
              "story for the first time. Its doors will be open to all of them.”"),
          "Which quotation from the text most effectively illustrates the speaker's claim?",
          "“the student preparing for an exam and … the grandmother learning to use a computer”",
          ["“This building will belong”",
           "“Its doors will be open”",
           "“hearing a story for the first time”"],
          "The student and the grandmother show people of very different ages using the library."),
        Q(COEQ,
          p("A school district moved its start time from 7:30 to 8:30 and surveyed students about their sleep. A "
            "district report notes that students in most grades slept more after the change, though the effect was "
            "much smaller for students in grade 12, whose average sleep rose only from ___"),
          P_GRAPH,
          "6.4 hours to 6.6 hours.",
          ["7.1 hours to 7.8 hours.",
           "6.6 hours to 7.3 hours.",
           "6.6 hours to 6.4 hours."],
          "Grade 12 went from 6.4 to 6.6 hours, a gain of only 0.2 hours.",
          figure=fig_sleep),
        Q(COEQ,
          p("Glaciologist Ingrid Solberg has measured Tarn Glacier for decades. She reports that the glacier did not "
            "just shrink between 1960 and 2020; it shrank faster over time, losing ___"),
          P_GRAPH,
          "only about 0.2 kilometers of length from 1960 to 1980 but about 2.4 kilometers from 1980 to 2020.",
          ["about 0.2 kilometers of length from 1980 to 2020.",
           "about 8.4 kilometers of length from 1960 to 2020.",
           "the same amount of length in each decade from 1960 to 2020."],
          "A small loss in the first twenty years and a much larger loss afterward shows the shrinking sped up.",
          figure=fig_glacier),
        Q(COEQ,
          p("A school board is considering adopting a new reading program in every school. A board member argues that "
            "the program appears to be effective, citing results from three schools: ___"),
          P_TABLE,
          "the two schools that used the program had average reading gains of 14 and 13 points, while the school "
          "that did not use it had a gain of 6 points.",
          ["Ashford had an average reading gain of 14 points.",
           "Brookside did not use the program and had an average reading gain of 6 points.",
           "Cedar Hill had a smaller average reading gain than Ashford did."],
          "Only this choice compares schools with and without the program.",
          figure=fig_reading),
        Q(INF,
          p("Lake Varn is home to two species of small fish that eat insects. Ecologist Rosa Lind noticed that where "
            "only one of the species lives, it feeds both near the surface and near the bottom of the lake. Where both "
            "species live together, however, one feeds almost entirely near the surface and the other almost "
            "entirely near the bottom. These observations suggest that ___"),
          P_INFER,
          "when the two species share a habitat, they may divide the available food sources to avoid competing.",
          ["each species prefers insects found near the bottom of the lake.",
           "one species will eventually replace the other in all parts of the lake.",
           "insects near the surface of the lake are more nutritious than insects near the bottom."],
          "Each species uses both zones when alone but splits them when together, which points to reduced "
          "competition."),
        Q(FSS,
          blank("Among the most popular exhibits at the science center ___ a pendulum that shows the rotation of Earth "
                "and a room where visitors can experience simulated earthquakes."),
          P_SEC, "are", ["is", "was", "has been"],
          "The subject comes after the verb: “a pendulum … and a room,” a compound subject, so the verb is plural."),
        Q(BND,
          blank("Some of the most detailed early maps of the night sky were made by astronomers at the observatory in "
                "Samarkand, which was built in the ___ by the ruler and astronomer Ulugh Beg."),
          P_SEC, "1420s", ["1420s,", "1420s;", "1420s:"],
          "No punctuation belongs between “the 1420s” and the phrase “by the ruler …,” which completes the clause."),
        Q(FSS,
          blank("Having studied the migration routes of whales for decades, ___"),
          P_SEC,
          "the biologist was able to predict where the pod would surface next.",
          ["the pod's next surfacing was predicted by the biologist.",
           "predicting where the pod would surface next was possible for the biologist.",
           "it was possible for the biologist to predict where the pod would surface next."],
          "The opening phrase describes the biologist, who must be the subject placed right after the comma."),
        Q(BND,
          blank("Many plants that grow in poor soil have formed partnerships with ___ fungi wrap around or enter the "
                "plants' roots and supply them with minerals in exchange for sugars."),
          P_SEC, "fungi: the", ["fungi, the", "fungi the", "fungi, and, the"],
          "A colon introduces the explanation of the partnership; a comma alone would create a comma splice."),
        Q(FSS,
          blank("The two scientists disagreed about how to interpret the data, but neither of ___ doubted that the "
                "measurements themselves were accurate."),
          P_SEC, "them", ["they", "their", "themselves"],
          "The object of the preposition “of” must be the object pronoun <em>them</em>."),
        Q(BND,
          blank("The ship's log, which recorded the weather every four ___ now one of the most valuable sources of "
                "information about the climate of the eighteenth century."),
          P_SEC, "hours, is", ["hours is", "hours; is", "hours, and is"],
          "The nonessential clause “which recorded …” must be closed with a comma before the main verb “is.”"),
        Q(FSS,
          blank("Of all the routes up the mountain, the northern ridge is considered the ___ because of its loose rock "
                "and sudden storms."),
          P_SEC, "most dangerous", ["more dangerous", "dangerousest", "most dangerously"],
          "Comparing more than two routes requires the superlative adjective <em>most dangerous</em>."),
        Q(TRN,
          blank("The Wright brothers' first powered flight, in 1903, lasted just twelve seconds and covered about 37 "
                "meters. ___ within six years they were making flights that lasted more than an hour."),
          P_TRANSITION, "Yet", ["Thus,", "Similarly,", "In short,"],
          "Hour-long flights six years later contrast with the very short first flight."),
        Q(TRN,
          blank("The researchers expected that students who studied with music would remember less. ___ the students "
                "who studied with quiet instrumental music remembered slightly more than those who studied in silence."),
          P_TRANSITION, "Surprisingly,", ["Consequently,", "Likewise,", "For example,"],
          "The result was the opposite of what the researchers expected."),
        Q(TRN,
          blank("Spiders spin silk for many purposes. They use it to build webs for catching prey, to wrap their eggs, "
                "and to make lines for climbing. ___ some young spiders use long strands of silk to float through the "
                "air and travel to new areas."),
          P_TRANSITION, "In addition,", ["However,", "Therefore,", "In contrast,"],
          "Floating through the air is one more use of silk, added to the list."),
        Q(RS,
          notes(["The Atacama Desert in Chile is one of the driest places on Earth.",
                 "Some weather stations there have recorded almost no rain for years at a time.",
                 "Because the air is so dry and clear, many large telescopes have been built there.",
                 "Scientists have also tested equipment for Mars missions in the Atacama."],
                "The student wants to explain why the Atacama Desert is a good place for telescopes."),
          P_NOTES_Q,
          "The Atacama Desert's very dry, clear air makes it a good place for large telescopes.",
          ["The Atacama Desert in Chile is one of the driest places on Earth.",
           "Scientists have tested equipment for Mars missions in the Atacama Desert.",
           "Some weather stations in the Atacama have recorded almost no rain for years."],
          "Only this choice gives the reason—dry, clear air—for building telescopes there."),
        Q(RS,
          notes(["A study compared two groups of adults learning to juggle.",
                 "One group practiced for one hour once a week.",
                 "The other group practiced for ten minutes six days a week.",
                 "After six weeks, the group that practiced in short daily sessions could juggle longer without dropping "
                 "a ball."],
                "The student wants to present the study's finding to readers interested in learning new skills."),
          P_NOTES_Q,
          "In one study of adults learning to juggle, short daily practice sessions led to better results than one "
          "long weekly session.",
          ["In one study, one group of adults practiced juggling for one hour once a week.",
           "A study of adults learning to juggle lasted six weeks.",
           "In one study, adults learning to juggle were divided into two groups."],
          "Only this choice states the result that matters to people learning a skill."),
        Q(RS,
          notes(["Wangari Maathai was a Kenyan environmental activist.",
                 "In 1977 she founded the Green Belt Movement.",
                 "The movement has planted tens of millions of trees in Kenya.",
                 "In 2004 Maathai became the first African woman to receive the Nobel Peace Prize."],
                "The student wants to emphasize Maathai's international recognition."),
          P_NOTES_Q,
          "In 2004 Wangari Maathai, founder of Kenya's Green Belt Movement, became the first African woman to receive "
          "the Nobel Peace Prize.",
          ["Wangari Maathai founded the Green Belt Movement in 1977.",
           "The Green Belt Movement has planted tens of millions of trees in Kenya.",
           "Wangari Maathai was a Kenyan environmental activist."],
          "Only this choice mentions the Nobel Peace Prize, her international recognition."),
    ]
