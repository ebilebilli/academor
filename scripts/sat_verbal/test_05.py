"""Academor SAT Practice Test 5 — Reading and Writing."""

from sat_verbal.common import (
    BND, CID, COEQ, COET, CTC, FSS, INF, P_FINDING, P_FUNCTION, P_GRAPH, P_INFER, P_MAIN_IDEA,
    P_NOTES_Q, P_PURPOSE, P_SEC, P_STRUCTURE, P_TABLE, P_TRANSITION, P_WEAKEN, P_WIC, Q, RS, TRN, TSP,
    WIC, bar_chart, blank, grouped_bar_chart, line_chart, notes, p, table_image, texts, underline,
)


def module_1():
    fig_volunteer = bar_chart(
        "Adults in Linton Who Volunteered in the Past Year, by Age",
        ["18–29", "30–44", "45–64", "65 and\nolder"],
        [24, 31, 36, 28],
        "Percentage of adults", 40,
        "Bar graph of the percentage of adults who volunteered: 24% aged 18 to 29, 31% aged 30 to 44, 36% aged 45 to "
        "64 and 28% aged 65 and older",
        value_fmt="{:.0f}%",
    )
    fig_cars = line_chart(
        "Electric Cars Registered in Country P, 2016–2022",
        [2016, 2018, 2020, 2022],
        [("Electric cars", [12, 30, 75, 190])],
        "Thousands of cars", (0, 200),
        "Line graph of electric cars registered in Country P rising from 12 thousand in 2016 to 30 in 2018, 75 in 2020 "
        "and 190 in 2022",
    )
    fig_coral = table_image(
        "Survival of Transplanted Coral Fragments After One Year",
        ["Depth", "Fragments planted", "Fragments surviving"],
        [["3 meters", "100", "42%"], ["6 meters", "100", "68%"], ["9 meters", "100", "71%"], ["12 meters", "100", "39%"]],
        "Table of the survival of transplanted coral fragments at depths of 3, 6, 9 and 12 meters",
        col_widths=[0.3, 0.35, 0.35],
    )
    return [
        Q(WIC,
          blank("The tour guide's directions were frustratingly ___: “Walk until you see the old tree,” he said, “then "
                "turn somewhere near the river.”"),
          P_WIC, "imprecise", ["detailed", "concise", "accurate"],
          "“Somewhere near the river” is vague, so the directions were <em>imprecise</em>."),
        Q(WIC,
          blank("Engineers designed the stadium's roof to be ___: it can withstand winds of more than 200 kilometers per "
                "hour and the weight of heavy snow."),
          P_WIC, "resilient", ["fragile", "ornamental", "temporary"],
          "A roof that withstands strong winds and heavy snow is <em>resilient</em>."),
        Q(WIC,
          blank("The diplomat's ___ reply—“My government will consider all options”—revealed nothing about what her "
                "country actually planned to do."),
          P_WIC, "guarded", ["candid", "furious", "detailed"],
          "An answer designed to reveal nothing is <em>guarded</em>."),
        Q(WIC,
          blank("Early reviews of the film were ___: some critics called it a masterpiece, while others dismissed it as "
                "confusing and slow."),
          P_WIC, "polarized", ["unanimous", "brief", "delayed"],
          "Opinions split into two opposite camps are <em>polarized</em>."),
        Q(TSP,
          underline("It is often claimed that the Great Wall of China is the only human-made structure visible from "
                    "space. ",
                    "Astronauts who have orbited Earth, however, report that the wall is very difficult to see with the "
                    "naked eye, because it is narrow and similar in color to the land around it.",
                    " Large cities, highways, and airports, by contrast, are often easy to spot, especially at night."),
          P_FUNCTION,
          "It presents evidence that challenges the claim in the first sentence.",
          ["It explains why the Great Wall of China was built from local materials.",
           "It offers an example that supports the claim in the first sentence.",
           "It describes the equipment that astronauts use to photograph Earth."],
          "Astronauts' reports that the wall is hard to see undercut the common claim."),
        Q(TSP,
          p("Louis Braille lost his sight as a young child. As a student at a school for blind children in Paris, he "
            "learned about “night writing,” a system of raised dots designed for soldiers to read in the dark. The "
            "system used cells of up to twelve dots, which were too large to feel with a single fingertip. By the age "
            "of fifteen, Braille had developed a simpler system based on cells of only six dots, which readers could "
            "recognize with one touch. A version of his system is still used around the world."),
          P_PURPOSE,
          "To explain how Louis Braille created his reading system by improving an existing one",
          ["To argue that night writing was more useful to soldiers than Braille's system",
           "To describe the school in Paris where Louis Braille later taught",
           "To compare the reading speeds of people who use different dot systems"],
          "The text traces how Braille simplified the twelve-dot night writing into his six-dot system."),
        Q(CTC,
          texts("Some educators argue that students learn more when they take notes by hand than when they type them on "
                "a laptop. Because writing is slower than typing, they explain, students who write by hand must "
                "summarize what they hear instead of copying it word for word.",
                "Education researcher Marco Bianchi compared students who took notes by hand with students who typed "
                "notes after being told to summarize rather than to record every word. Both groups remembered the "
                "material equally well. Bianchi concludes that what matters is how students take notes, not what they "
                "use to take them."),
          "Based on the texts, how would Bianchi (Text 2) most likely respond to the educators' argument in Text 1?",
          "By suggesting that the benefit they attribute to handwriting comes from summarizing, which students can "
          "also do while typing",
          ["By agreeing that students who type notes always remember less than students who write by hand",
           "By arguing that summarizing is less useful than recording every word",
           "By claiming that writing by hand is faster than typing for most students"],
          "Bianchi found that typists who summarized did as well, so the key factor is summarizing, not handwriting."),
        Q(CID,
          p("Ocean tides are caused mainly by the gravitational pull of the Moon, which draws the water on the side of "
            "Earth facing it into a bulge. The Sun's gravity also affects the tides, though less strongly because the "
            "Sun is much farther away. When the Sun and Moon line up, as they do at new and full moon, their pulls "
            "combine to produce especially large tides, called spring tides."),
          P_MAIN_IDEA,
          "Tides are produced mostly by the Moon's gravity, with the Sun's gravity adding to the effect, especially "
          "when the two are aligned.",
          ["The Sun's gravity has a stronger effect on tides than the Moon's gravity does.",
           "Spring tides occur only during the spring months of the year.",
           "Tides are caused by winds that push ocean water toward the shore."],
          "The text explains the Moon's main role, the Sun's smaller one, and their combined effect."),
        Q(CID,
          p("The following text is from a short story. Ana's father, a fisherman, has injured his hand.")
          + p("For years Ana had watched him mend the nets on the dock, his fingers moving faster than she could "
              "follow. Now he sat beside her with his bandaged hand in his lap and talked her through it: over, under, "
              "pull the knot tight. Her first knots slipped. By evening they held, and her father, who was not a man "
              "who gave compliments, tested one with his good hand and simply nodded."),
          P_MAIN_IDEA,
          "Ana learns a skill from her injured father and earns his quiet approval.",
          ["Ana refuses to help her father mend the nets.",
           "Ana's father is unable to explain how to mend the nets.",
           "Ana's father criticizes the knots that Ana ties at the end of the day."],
          "Ana learns to mend the nets with her father's guidance, and his nod shows approval."),
        Q(COET,
          p("Agronomist Lucia Ferraro and her team claim that a new organic fertilizer substantially increases the "
            "amount of wheat that a field produces."),
          P_WEAKEN,
          "In the same region and season, fields treated with the new fertilizer produced about the same amount of "
          "wheat as similar fields that received no fertilizer.",
          ["Farmers who tried the new fertilizer said it was easy to apply.",
           "The new fertilizer costs slightly more than older fertilizers.",
           "Wheat grown with the new fertilizer was slightly taller on average."],
          "If treated fields produced no more than untreated ones, the claim of increased yield is weakened."),
        Q(COEQ,
          p("A report on volunteering in Linton notes that adults in the middle of their working lives were the most "
            "likely to volunteer: ___"),
          P_GRAPH,
          "36% of adults aged 45 to 64 volunteered, a higher percentage than in any other age group.",
          ["24% of adults aged 18 to 29 volunteered, the lowest percentage of any age group.",
           "28% of adults aged 65 and older volunteered.",
           "31% of adults aged 30 to 44 volunteered, a higher percentage than in any other age group."],
          "The 45–64 group had the highest share, which supports the report's statement.",
          figure=fig_volunteer),
        Q(COEQ,
          p("An energy analyst notes that the number of electric cars registered in Country P grew rapidly, more than "
            "doubling every two years between 2016 and 2022: the number rose from ___"),
          P_GRAPH,
          "about 12 thousand in 2016 to about 30 thousand in 2018 and about 75 thousand in 2020.",
          ["about 190 thousand in 2022 to about 75 thousand in 2020.",
           "about 12 thousand in 2016 to about 15 thousand in 2018.",
           "about 75 thousand in 2018 to about 190 thousand in 2020."],
          "12 to 30 and 30 to 75 are each more than a doubling, and the years match the graph.",
          figure=fig_cars),
        Q(COEQ,
          p("Marine biologists transplanted fragments of coral at four depths to help restore a damaged reef. They "
            "concluded that fragments survived best at intermediate depths: ___"),
          P_TABLE,
          "68% and 71% of fragments survived at 6 and 9 meters, compared with 42% at 3 meters and 39% at 12 meters.",
          ["42% of fragments survived at 3 meters.",
           "the same number of fragments was planted at each depth.",
           "fewer fragments survived at 12 meters than at any other depth."],
          "Only this choice compares the middle depths with both the shallowest and the deepest.",
          figure=fig_coral),
        Q(INF,
          p("Wild wheat plants scatter their seeds when the seeds are ripe, but cultivated wheat keeps its seeds "
            "attached until they are harvested. At an archaeological site about 10,000 years old, researchers found "
            "that the oldest layers contained mostly wheat with the wild, scattering trait, while later layers "
            "contained more and more wheat that kept its seeds. These findings suggest that ___"),
          P_INFER,
          "people at the site may have gradually begun to cultivate wheat over time.",
          ["wild wheat stopped growing near the site 10,000 years ago.",
           "the people at the site ate less wheat as time went on.",
           "cultivated wheat was brought to the site from elsewhere all at once."],
          "A gradual rise in the cultivated trait across layers points to cultivation developing over time."),
        Q(FSS,
          blank("The number of students taking the advanced chemistry course ___ increased every year since the school "
                "built its new laboratory."),
          P_SEC, "has", ["have", "are", "were"],
          "“The number” is singular, so the verb is <em>has</em>; “since” calls for the present perfect."),
        Q(BND,
          blank("The tour visited three cities: Lyon, ___ Turin, Italy; and Geneva, Switzerland."),
          P_SEC, "France;", ["France,", "France", "France:"],
          "When items in a list contain commas, semicolons separate the items."),
        Q(FSS,
          blank("Each of the cities that applied to host the conference had to describe how ___ would provide housing "
                "for visitors."),
          P_SEC, "it", ["they", "them", "we"],
          "The pronoun refers to “each,” which is singular, so <em>it</em> is required."),
        Q(BND,
          blank("Mae Jemison was the first African American woman to travel into ___ in 1992 she flew aboard the space "
                "shuttle <em>Endeavour</em>."),
          P_SEC, "space;", ["space,", "space", "space and,"],
          "Two independent clauses are joined with a semicolon."),
        Q(FSS,
          blank("The paintings in the new exhibit are brighter than ___ in the museum's permanent collection."),
          P_SEC, "those", ["that", "the one", "it"],
          "Paintings must be compared with other paintings; the plural pronoun <em>those</em> does this."),
        Q(BND,
          blank("The scientists faced an unexpected ___ the samples they had collected in the Arctic had thawed during "
                "shipping."),
          P_SEC, "problem:", ["problem,", "problem", "problem, and"],
          "A colon introduces the explanation of the problem; a comma alone would create a comma splice."),
        Q(FSS,
          blank("Whoever finishes the puzzle first ___ the prize, a book of even harder puzzles."),
          P_SEC, "wins", ["win", "are winning", "have won"],
          "“Whoever finishes the puzzle first” is a singular subject, so the verb is <em>wins</em>."),
        Q(TRN,
          blank("Honeybees communicate the location of food through dances. ___ a bee that has found flowers far from "
                "the hive performs a “waggle dance” whose angle points other bees toward the food."),
          P_TRANSITION, "For example,", ["However,", "Instead,", "Nonetheless,"],
          "The waggle dance is an example of communication through dance."),
        Q(TRN,
          blank("Many early cars ran on electricity. ___ by the 1920s, cars powered by gasoline had become far more "
                "common, partly because gasoline was cheap and the cars could travel long distances."),
          P_TRANSITION, "However,", ["Similarly,", "Thus,", "For instance,"],
          "The rise of gasoline cars contrasts with the early popularity of electric cars."),
        Q(TRN,
          blank("The team's first prototype was too heavy to fly. ___ the engineers replaced its metal frame with one "
                "made of carbon fiber, cutting its weight by more than half."),
          P_TRANSITION, "To solve this problem,", ["In contrast,", "Likewise,", "For example,"],
          "Replacing the frame responds to the weight problem."),
        Q(RS,
          notes(["The Panama Canal opened in 1914.",
                 "It connects the Atlantic and Pacific Oceans across the Isthmus of Panama.",
                 "Before it opened, ships traveling between New York and San Francisco had to sail around the southern "
                 "tip of South America.",
                 "The canal shortened that trip by about 13,000 kilometers."],
                "The student wants to emphasize how the Panama Canal changed shipping."),
          P_NOTES_Q,
          "By connecting the Atlantic and Pacific Oceans, the Panama Canal shortened the voyage between New York and "
          "San Francisco by about 13,000 kilometers.",
          ["The Panama Canal opened in 1914.",
           "The Panama Canal crosses the Isthmus of Panama.",
           "Before 1914, ships sailed around the southern tip of South America."],
          "Only this choice shows the canal's effect on shipping."),
        Q(RS,
          notes(["Cheetahs can run at about 100 kilometers per hour.",
                 "They can keep up that speed for only about 20 to 30 seconds.",
                 "Pronghorn antelope can run at about 90 kilometers per hour.",
                 "Pronghorn can keep up high speeds for several minutes."],
                "The student wants to contrast the running abilities of cheetahs and pronghorn."),
          P_NOTES_Q,
          "Although cheetahs are slightly faster than pronghorn, pronghorn can keep up high speeds for much longer.",
          ["Cheetahs can run at about 100 kilometers per hour.",
           "Pronghorn can run at about 90 kilometers per hour and keep up high speeds for several minutes.",
           "Both cheetahs and pronghorn are fast runners."],
          "Only this choice contrasts speed and endurance across the two animals."),
        Q(RS,
          notes(["Frida Kahlo was a Mexican painter born in 1907.",
                 "Many of her best-known works are self-portraits.",
                 "Her paintings often combine images from Mexican folk art with personal symbols.",
                 "In 1938 she held her first solo exhibition, in New York City."],
                "The student wants to describe the style of Kahlo's paintings."),
          P_NOTES_Q,
          "Frida Kahlo's paintings, many of them self-portraits, often combine images from Mexican folk art with "
          "personal symbols.",
          ["Frida Kahlo was a Mexican painter born in 1907.",
           "In 1938 Frida Kahlo held her first solo exhibition, in New York City.",
           "Frida Kahlo held an exhibition in New York City."],
          "Only this choice describes her style."),
    ]


def module_2():
    fig_trust = grouped_bar_chart(
        "Respondents Who Trust Each News Source “a Great Deal”",
        ["Local\nnewspapers", "National\nnewspapers", "Television\nnews", "Social\nmedia"],
        [("Ages 18–34", [38, 30, 26, 18]), ("Ages 55 and older", [52, 37, 44, 9])],
        "Percentage of respondents", 60,
        "Grouped bar graph of the share of younger and older respondents who trust four news sources a great deal",
    )
    fig_ozone = line_chart(
        "Pesticide Level in Fish from Lake Mira, 1980–2020",
        [1980, 1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020],
        [("Pesticide level", [1.5, 12.5, 20.5, 22.8, 24.5, 24.0, 22.2, 21.5, 20.5])],
        "Micrograms per kilogram", (0, 28),
        "Line graph of the pesticide level in fish rising from 1.5 in 1980 to about 24.5 in 2000 and then falling "
        "slowly to about 20.5 in 2020",
        note=(1990, "Pesticide\nbanned"),
    )
    fig_typing = table_image(
        "Average Typing Speed After Six Weeks of Practice",
        ["Practice schedule", "Minutes per week", "Words per minute"],
        [["One 60-minute session", "60", "38"], ["Three 20-minute sessions", "60", "45"],
         ["Six 10-minute sessions", "60", "51"]],
        "Table of typing speeds after six weeks for three practice schedules with the same total time",
        col_widths=[0.42, 0.28, 0.30],
    )
    return [
        Q(WIC,
          blank("The biologist was ___ about her results, cautioning reporters that her sample was small and that the "
                "findings would need to be confirmed by other studies."),
          P_WIC, "circumspect", ["boastful", "indifferent", "careless"],
          "Warning that the findings are limited shows caution: she was <em>circumspect</em>."),
        Q(WIC,
          blank("The novel's ___ plot, which jumps back and forth across three centuries and a dozen narrators, rewards "
                "careful readers but frustrates casual ones."),
          P_WIC, "convoluted", ["straightforward", "predictable", "brief"],
          "A plot that jumps across centuries and narrators is complicated, or <em>convoluted</em>."),
        Q(WIC,
          blank("Little remains of the medieval castle, which was gradually ___ by later residents of the town, who "
                "took its stones to build their own houses and walls."),
          P_WIC, "dismantled", ["fortified", "admired", "excavated"],
          "Taking the castle's stones away piece by piece <em>dismantled</em> it."),
        Q(WIC,
          blank("The new evidence did not ___ the theory; it simply showed that the theory applies to fewer cases than "
                "its supporters had claimed."),
          P_WIC, "invalidate", ["inspire", "describe", "explain"],
          "The evidence limited the theory without disproving it, so it did not <em>invalidate</em> it."),
        Q(TSP,
          p("In 1977 a severe drought struck Daphne Major, a small island in the Galápagos. Most of the plants that "
            "produce small, soft seeds died, leaving mainly large, hard seeds. Biologists Peter and Rosemary Grant, "
            "who had been measuring the island's finches for years, found that many birds died during the drought. "
            "The survivors had, on average, larger beaks, which allowed them to crack the hard seeds. The next "
            "generation of finches also had larger beaks than the generation before the drought."),
          P_STRUCTURE,
          "It describes an environmental change and then explains how that change affected the physical traits of a "
          "bird population.",
          ["It compares two species of finches and argues that one is better suited to drought.",
           "It explains how the Grants chose Daphne Major and then describes their measuring methods.",
           "It describes a drought and then argues that the finches will eventually leave the island."],
          "The text moves from the drought, to its effect on seeds, to the survival of larger-beaked finches and "
          "their offspring."),
        Q(TSP,
          underline("Bioluminescence, the production of light by living things, is rare on land but common in the deep "
                    "sea. ",
                    "In one large survey of the open ocean, about three-quarters of the animals observed between the "
                    "surface and a depth of nearly 4,000 meters could produce their own light.",
                    " They use it to attract prey, to find mates, and to confuse predators."),
          P_FUNCTION,
          "It provides support for the statement that bioluminescence is common in the deep sea.",
          ["It explains how animals produce light.",
           "It describes the uses of bioluminescence on land.",
           "It questions estimates of how many animals live in the deep sea."],
          "The survey finding of about three-quarters supports the claim that the trait is common in the sea."),
        Q(CTC,
          texts("Some economists argue that raising a city's minimum wage will lead businesses to cut jobs, because "
                "employers will hire fewer workers when each worker costs more.",
                "Economist Hana Kim studied restaurants in neighboring towns, one of which raised its minimum wage. "
                "Over three years, employment at restaurants in that town did not fall compared with the other town. "
                "Kim notes that higher wages also reduced how often workers quit, which saved employers the cost of "
                "hiring and training new staff."),
          "Based on the texts, how would Kim (Text 2) most likely respond to the economists' argument in Text 1?",
          "By noting that it leaves out savings that can offset the cost of higher wages",
          ["By agreeing that raising the minimum wage always leads businesses to cut jobs",
           "By claiming that restaurants in both towns hired more workers than they needed",
           "By arguing that the minimum wage should be the same in every town"],
          "Kim found no job losses and points to savings from lower turnover, which the economists do not consider."),
        Q(CID,
          p("For most of the twentieth century, scientists believed that adult birds could not grow new brain cells. "
            "In the 1980s, however, neuroscientist Fernando Nottebohm found that canaries grow large numbers of new "
            "neurons in the brain regions that control song, especially in the season when they learn new songs. His "
            "work helped convince researchers to look for new neuron growth in other animals, including mammals."),
          P_MAIN_IDEA,
          "A study of canaries challenged a long-held belief about adult brains and encouraged further research on "
          "the topic.",
          ["Canaries learn new songs only when they are young.",
           "Scientists have proven that adult mammals cannot grow new neurons.",
           "Birds grow new brain cells in every region of the brain at the same rate."],
          "The discovery overturned an assumption and led researchers to look for similar growth elsewhere."),
        Q(CID,
          p("The following text is from a short story. Mr. Petrov, a retired teacher, is visiting his old school.")
          + p("The classroom had new desks, and the chalkboard had been replaced by a white screen that glowed when "
              "the teacher touched it. Mr. Petrov felt like a guest in a house he used to own. Then a boy in the front "
              "row raised his hand and asked the same question Mr. Petrov had been asked every year for thirty-five "
              "years—why do we have to learn this?—and the old teacher smiled, because the answer had not changed."),
          P_MAIN_IDEA,
          "Although the classroom has changed, Mr. Petrov recognizes something familiar in the students.",
          ["Mr. Petrov is upset that the school has removed the chalkboard.",
           "Mr. Petrov cannot answer the student's question about learning.",
           "Mr. Petrov decides to return to teaching at his old school."],
          "The new equipment makes him feel like a guest, but a familiar question reconnects him to the classroom."),
        Q(COET,
          p("Linguist Amaru Quispe claims that children who grow up hearing two languages learn to tell apart the "
            "sounds of each language very early, before they can speak either language."),
          P_FINDING,
          "Eight-month-old infants raised with two languages noticed when a speaker switched from one language to the "
          "other, while infants raised with one language did not.",
          ["Children raised with two languages usually speak their first words at the same age as other children.",
           "Adults who learned a second language as children have larger vocabularies than other adults.",
           "Many parents who speak two languages use only one language with their children."],
          "Infants who cannot yet speak noticing a switch between languages directly supports the claim."),
        Q(COEQ,
          p("A media researcher surveyed adults about how much they trust different sources of news. The researcher "
            "notes that the gap between younger and older respondents was largest for television news: ___"),
          P_GRAPH,
          "44% of respondents aged 55 and older trusted television news a great deal, compared with 26% of those aged "
          "18 to 34.",
          ["52% of respondents aged 55 and older trusted local newspapers a great deal, compared with 38% of those "
           "aged 18 to 34.",
           "18% of respondents aged 18 to 34 trusted social media a great deal.",
           "26% of respondents aged 55 and older trusted television news a great deal, compared with 44% of those aged "
           "18 to 34."],
          "The television gap (18 points) is the largest; the last choice reverses the groups.",
          figure=fig_trust),
        Q(COEQ,
          p("A pesticide that builds up in fish was banned in the region around Lake Mira in 1990. Scientists say that "
            "the ban has worked, but slowly, because the pesticide that had already entered the lake breaks down over "
            "decades. The graph supports this view: the pesticide level in fish ___"),
          P_GRAPH,
          "kept rising until about 2000 and has fallen only gradually since then.",
          ["dropped to its lowest level in 1990, the year the ban took effect.",
           "has risen steadily every year since 1980.",
           "fell to zero by 2020."],
          "A rise until about 2000 and a slow decline afterward match a delayed, gradual effect of the ban.",
          figure=fig_ozone),
        Q(COEQ,
          p("In a study, adults spent 60 minutes a week for six weeks practicing typing, divided in different ways. "
            "The researchers concluded that spreading the same amount of practice over more, shorter sessions "
            "produced better results: ___"),
          P_TABLE,
          "participants who practiced in six 10-minute sessions typed 51 words per minute, compared with 38 for those "
          "who practiced in one 60-minute session.",
          ["every group practiced for a total of 60 minutes per week.",
           "participants who practiced in one 60-minute session typed 38 words per minute.",
           "participants who practiced in three 20-minute sessions typed faster than those who practiced in six "
           "10-minute sessions."],
          "Only this choice compares more, shorter sessions with one long session.",
          figure=fig_typing),
        Q(INF,
          p("Sound travels about four times faster in water than in air, and low-pitched sounds can travel thousands "
            "of kilometers through the ocean. Marine biologist Ines Kowalczyk recorded the calls of fin whales, which "
            "are among the lowest-pitched sounds made by any animal, and found that whales separated by hundreds of "
            "kilometers appeared to change direction in response to one another's calls. Her findings suggest that ___"),
          P_INFER,
          "fin whales may be able to communicate with one another across very long distances.",
          ["fin whales cannot hear high-pitched sounds.",
           "sound travels more slowly in cold water than in warm water.",
           "fin whales call most often when they are close together."],
          "Whales far apart reacting to each other's low calls suggests long-distance communication."),
        Q(BND,
          blank("The longest river in Africa, the ___ flows north through eleven countries before reaching the "
                "Mediterranean Sea."),
          P_SEC, "Nile,", ["Nile", "Nile;", "Nile:"],
          "“The Nile” is an appositive renaming “the longest river,” so it is set off by commas on both sides."),
        Q(FSS,
          blank("The committee members, along with their chair, ___ expected to vote on the budget tomorrow."),
          P_SEC, "are", ["is", "was", "has been"],
          "The subject is “members”; “along with their chair” does not change the number, so the verb is <em>are</em>."),
        Q(BND,
          blank("Many people know that Benjamin Franklin experimented with ___ fewer know that he also invented a "
                "musical instrument called the glass armonica."),
          P_SEC, "electricity;", ["electricity,", "electricity", "electricity, and, also"],
          "Two independent clauses are joined with a semicolon."),
        Q(FSS,
          blank("Neither of the two proposals ___ enough support to pass when the council voted last week."),
          P_SEC, "had", ["have", "has", "are having"],
          "“Neither” is singular, and the vote was last week, so the past tense <em>had</em> is correct."),
        Q(BND,
          blank("The recipe was handed down from my great-grandmother, a baker who ran a small shop in ___ and it has "
                "been made in our family for more than a century."),
          P_SEC, "Naples,", ["Naples", "Naples;", "Naples:"],
          "The appositive “a baker who ran a small shop in Naples” must end with a comma before “and it has been …”"),
        Q(FSS,
          blank("After hiking for six hours, ___"),
          P_SEC,
          "the group finally reached the lake at the top of the valley.",
          ["the lake at the top of the valley finally came into view of the group.",
           "the top of the valley was where the group finally found the lake.",
           "reaching the lake at the top of the valley finally happened for the group."],
          "The group did the hiking, so “the group” must follow the opening phrase."),
        Q(FSS,
          blank("The coach told the players that ___ would need to practice twice a day before the championship."),
          P_SEC, "they", ["them", "their", "it"],
          "The players are the subject of “would need,” so the subject pronoun <em>they</em> is needed."),
        Q(TRN,
          blank("Octopuses can change the color of their skin in a fraction of a second. ___ they can change its "
                "texture, raising small bumps to look like rock or coral."),
          P_TRANSITION, "Moreover,", ["However,", "Instead,", "In contrast,"],
          "Changing texture adds a second ability to the first."),
        Q(TRN,
          blank("The museum's attendance fell sharply during the renovation. ___ it rose to record levels in the year "
                "after the new galleries opened."),
          P_TRANSITION, "Afterward, though,", ["Therefore,", "Similarly,", "In other words,"],
          "The record attendance after reopening contrasts with the earlier fall."),
        Q(TRN,
          blank("The experiment's results were clear: plants given more light grew faster. ___ plants given the most "
                "light grew about twice as tall as those given the least."),
          P_TRANSITION, "In particular,", ["Nevertheless,", "On the other hand,", "Instead,"],
          "The second sentence gives a specific detail of the general result."),
        Q(RS,
          notes(["The axolotl is a salamander native to lakes near Mexico City.",
                 "Unlike most salamanders, it usually keeps its gills and lives in water its whole life.",
                 "Axolotls can regrow lost limbs, parts of their spinal cord, and even parts of their heart.",
                 "Scientists study axolotls to learn more about how tissues regenerate."],
                "The student wants to explain why scientists study axolotls."),
          P_NOTES_Q,
          "Because axolotls can regrow limbs and even parts of their heart, scientists study them to learn how tissues "
          "regenerate.",
          ["The axolotl is a salamander native to lakes near Mexico City.",
           "Axolotls usually keep their gills and live in water their whole lives.",
           "Unlike most salamanders, axolotls live in lakes near Mexico City."],
          "Only this choice gives the reason scientists study axolotls."),
        Q(RS,
          notes(["A study compared two groups of hospital patients after surgery.",
                 "Patients in the first group had rooms with windows facing trees.",
                 "Patients in the second group had rooms with windows facing a brick wall.",
                 "Patients with a view of trees left the hospital about one day sooner on average."],
                "The student wants to present the study's main finding."),
          P_NOTES_Q,
          "In the study, patients whose rooms looked out on trees left the hospital about a day sooner than patients "
          "whose rooms faced a brick wall.",
          ["The study compared two groups of hospital patients after surgery.",
           "Some patients in the study had rooms with windows facing a brick wall.",
           "Some patients in the study had rooms with windows facing trees."],
          "Only this choice states the result of the comparison."),
        Q(RS,
          notes(["Chinua Achebe was a Nigerian writer born in 1930.",
                 "His first novel, <em>Things Fall Apart</em>, was published in 1958.",
                 "The novel describes life in an Igbo village before and during the arrival of European colonizers.",
                 "It has been translated into more than fifty languages."],
                "The student wants to emphasize how widely <em>Things Fall Apart</em> has been read."),
          P_NOTES_Q,
          "Chinua Achebe's 1958 novel <em>Things Fall Apart</em> has been translated into more than fifty languages.",
          ["Chinua Achebe was a Nigerian writer born in 1930.",
           "<em>Things Fall Apart</em> describes life in an Igbo village.",
           "<em>Things Fall Apart</em> was Achebe's first novel."],
          "Translation into more than fifty languages shows how widely the novel has been read."),
    ]
