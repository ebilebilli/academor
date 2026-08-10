# -*- coding: utf-8 -*-
"""Write 10 Intermediate (B1) reading quizzes: 10 questions × 5 options each."""
from __future__ import annotations

import json
import re
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "academor" / "portals" / "resources" / "quiz_questions"


def p(*paragraphs: str) -> str:
    return "".join(f"<p>{t.strip()}</p>" for t in paragraphs if t.strip())


def q(qid: int, question: str, options: list[str], answer: int) -> dict:
    assert len(options) == 5, (qid, len(options))
    assert 0 <= answer < 5
    return {"id": qid, "question": question, "options": options, "answer": answer}


def pack(quiz: int, title: str, passage: str, questions: list[dict]) -> dict:
    assert len(questions) == 10
    return {
        "level": "B1",
        "quiz": quiz,
        "title": title,
        "service": "general_english",
        "category_name": "B1 Reading Tests",
        "has_shared_passage": True,
        "shared_passage": passage,
        "questions": questions,
    }


def word_count(html: str) -> int:
    return len(re.sub(r"<[^>]+>", " ", html).split())


ITEMS: list[dict] = []

ITEMS.append(
    pack(
        1,
        "Urban Heat Islands",
        p(
            "On summer evenings in dense city centres, the air often stays warmer long after sunset. Scientists call this the urban heat island effect: concrete, asphalt and dark rooftops absorb heat during the day and release it slowly at night, while trees and open soil would normally cool the neighbourhood.",
            "A recent study in three European cities compared districts with similar income levels but different amounts of green space. Neighbourhoods with fewer street trees recorded night temperatures up to 2.5°C higher. Hospitals reported more heat-related visits among older residents during those weeks.",
            "City planners are testing practical responses rather than waiting for perfect solutions. Light-coloured roofs reflect more sunlight, and small parks with shade can lower local temperatures. However, planting projects compete with parking spaces and new apartment blocks, so progress is uneven.",
            "Critics argue that heat maps alone will not help if low-income areas receive fewer trees. Fair planning means directing investment where health risks are highest, not only where projects look attractive for tourism brochures.",
            "Residents can also help by supporting local tree programmes and reducing unnecessary car journeys on the hottest days. Individual actions cannot replace policy, yet public pressure often decides which districts receive funding first. Without both civic attention and technical planning, heat islands will keep punishing the same neighbourhoods every summer.",
        ),
        [
            q(1, "What does the urban heat island effect mainly describe?", [
                "Cities staying warmer at night because surfaces store and release heat",
                "Cities becoming colder after every rainfall",
                "Only coastal towns having cooler evenings",
                "Airports producing all city heat",
                "Museums closing earlier in summer",
            ], 0),
            q(2, "According to the study, what difference was linked to fewer street trees?", [
                "Night temperatures up to 2.5°C higher",
                "Rainfall increasing by 2.5%",
                "House prices falling overnight",
                "Schools opening two hours later",
                "Tourism rising in winter only",
            ], 0),
            q(3, "Who was especially affected during hotter weeks?", [
                "Older residents needing hospital care for heat-related problems",
                "Only tourists with cameras",
                "Airport staff exclusively",
                "Children on school buses only",
                "Museum guides working indoors",
            ], 0),
            q(4, "Why are light-coloured roofs mentioned?", [
                "They reflect more sunlight and can reduce heat",
                "They are cheaper to paint every night",
                "They stop all traffic noise",
                "They replace the need for hospitals",
                "They create more parking spaces",
            ], 0),
            q(5, "What makes planting projects difficult in practice?", [
                "They compete with parking and new apartment construction",
                "Trees grow only in museums",
                "Scientists refuse to measure temperature",
                "Green space always reduces income equally",
                "Residents dislike shade completely",
            ], 0),
            q(6, "What concern do critics raise about heat maps?", [
                "Poor areas may still receive fewer trees without fair investment",
                "Heat maps always exaggerate rainfall",
                "Maps cannot show streets at all",
                "Tourism brochures ban scientific data",
                "Hospitals ignore older patients on purpose",
            ], 0),
            q(7, "What does “fair planning” mean in this text?", [
                "Putting investment where health risks are highest",
                "Building hotels first for visitors",
                "Removing all parks from city centres",
                "Ignoring income differences between districts",
                "Painting every roof black for style",
            ], 0),
            q(8, "What role can residents play, according to the writer?", [
                "Support tree programmes and cut unnecessary hot-day car trips",
                "Replace government policy completely",
                "Close hospitals during summer",
                "Ban all scientific studies",
                "Remove shade from small parks",
            ], 0),
            q(9, "Which statement is closest to the writer’s view?", [
                "Policy matters most, but public pressure still influences funding choices",
                "Individual actions alone solve urban heat",
                "Green space is irrelevant to night temperatures",
                "Only tourism districts need cooler streets",
                "Heat islands occur only in rural villages",
            ], 0),
            q(10, "What is the most accurate title for the passage?", [
                "Urban Heat Islands",
                "Museum Ticket Rules",
                "Airport Security Checks",
                "Silent Film History",
                "Bank Loan Applications",
            ], 0),
        ],
    )
)

ITEMS.append(
    pack(
        2,
        "Digital Privacy Trade-offs",
        p(
            "Many free apps collect detailed information about users: location history, browsing habits and even microphone access “for better recommendations.” Companies argue that personalised adverts pay for services that people would otherwise refuse to buy.",
            "Privacy researchers warn that users rarely understand what they accept. Long permission screens use legal language, and people often tap “Agree” simply to continue. Once data is shared with partner companies, deleting an account may not remove every copy.",
            "Some governments now require clearer consent buttons and the right to download or erase personal data. Technology firms say these rules increase costs and slow innovation. Consumer groups reply that innovation should not depend on confusing customers.",
            "A practical middle path is emerging. Apps can offer a paid version with fewer trackers, while free versions show adverts but collect less sensitive details. Transparency dashboards that explain data use in plain language also help.",
            "Ultimately, privacy is not only a technical setting. It is a social choice about how much personal life should be turned into a product. Informed users and stronger rules together create healthier digital markets. Without both, convenience will continue to outrun caution.",
        ),
        [
            q(1, "How do companies mainly justify collecting user data?", [
                "Personalised adverts fund free services people would not pay for",
                "Laws require every app to record microphone audio",
                "Users always demand more tracking",
                "Data collection reduces all company costs to zero",
                "Governments ban paid applications",
            ], 0),
            q(2, "Why do researchers say consent is often weak?", [
                "Permission texts are hard to understand, so people agree just to continue",
                "Users enjoy reading legal documents carefully",
                "Apps never ask for any permission",
                "Consent buttons are illegal in every country",
                "Deleting an account always erases partner copies instantly",
            ], 0),
            q(3, "What problem remains even after account deletion?", [
                "Partner companies may still keep copies of shared data",
                "The phone battery stops charging forever",
                "All adverts disappear from the internet",
                "Governments delete every company overnight",
                "Users lose the right to buy paid apps",
            ], 0),
            q(4, "What do technology firms claim about stricter privacy rules?", [
                "They raise costs and may slow innovation",
                "They make apps completely free of adverts automatically",
                "They ban all smartphones",
                "They remove the need for consent screens",
                "They force users to share more location data",
            ], 0),
            q(5, "What counter-argument do consumer groups make?", [
                "Innovation should not rely on confusing customers",
                "Companies should collect more microphone data",
                "Legal language must become longer",
                "Paid apps should track users more closely",
                "Privacy rules should apply only to museums",
            ], 0),
            q(6, "What “middle path” does the text describe?", [
                "Paid low-tracking versions plus freer versions with limited sensitive collection",
                "Closing every free app immediately",
                "Sharing all data with every partner by default",
                "Removing consent buttons from phones",
                "Banning transparency dashboards",
            ], 0),
            q(7, "How can transparency dashboards help?", [
                "By explaining data use in plain language",
                "By hiding permission screens forever",
                "By increasing legal jargon",
                "By selling location history more quickly",
                "By disabling account deletion",
            ], 0),
            q(8, "What does the writer mean by calling privacy a “social choice”?", [
                "Society decides how much personal life becomes a commercial product",
                "Only engineers can change privacy settings",
                "Privacy is unrelated to markets",
                "Users have no responsibility at all",
                "Governments must ban all free apps",
            ], 0),
            q(9, "Which conclusion best matches the passage?", [
                "Better rules and informed users together improve digital markets",
                "Tracking is harmless if services are free",
                "Deleting an account always solves every privacy risk",
                "Companies never share data with partners",
                "Consent screens are already clear for everyone",
            ], 0),
            q(10, "What is the best title?", [
                "Digital Privacy Trade-offs",
                "School Bus Schedules",
                "Museum Cafeteria Menus",
                "Football Match Results",
                "Hotel Room Cleaning",
            ], 0),
        ],
    )
)

ITEMS.append(
    pack(
        3,
        "The Cost of Fast Fashion",
        p(
            "Fast fashion brands release new clothes every few weeks at prices that seem almost too low to be real. Shoppers enjoy constant novelty, and social media trends disappear within days, encouraging another purchase.",
            "Behind the low price is a long chain of pressure. Factories are asked to produce faster, often with unpaid overtime. Textile dyeing can pollute rivers near production towns, and mountains of unsold clothes are burned or dumped.",
            "Some companies now advertise “conscious collections” made with recycled fibres. Investigators note that these lines are frequently a small percentage of total production, while the main business model still depends on overproduction.",
            "Consumers are not powerless. Buying fewer items, repairing damaged clothes and choosing second-hand options reduce demand for disposable fashion. Still, individual choices work better when governments require clearer supply-chain information.",
            "The debate is not simply “fashion is bad.” Clothing is culture and identity. The harder question is whether constant newness is worth the environmental and human cost hidden in the price tag. Until that cost becomes visible to shoppers, disposable trends will keep winning by default.",
        ),
        [
            q(1, "What mainly drives repeated purchases in fast fashion culture?", [
                "Rapidly changing trends and a desire for constant novelty",
                "Clothes lasting longer than before",
                "Factories refusing to make new styles",
                "Social media banning fashion posts",
                "Higher prices stopping all shopping",
            ], 0),
            q(2, "What factory pressure is mentioned in the text?", [
                "Faster production, often with unpaid overtime",
                "Workers choosing their own deadlines freely",
                "Factories producing only one shirt a year",
                "Complete bans on overtime worldwide",
                "Automatic recycling of every garment",
            ], 0),
            q(3, "What environmental harm is linked to textile dyeing?", [
                "Pollution of rivers near production towns",
                "Cleaner drinking water in every city",
                "Less waste in landfills",
                "Cooler urban heat islands only",
                "More trees in shopping centres",
            ], 0),
            q(4, "How do investigators view many “conscious collections”?", [
                "As a small share of output while overproduction continues",
                "As proof that fast fashion has fully changed",
                "As illegal in every country",
                "As the only products companies sell",
                "As more expensive than luxury brands always",
            ], 0),
            q(5, "Which consumer action does the text support?", [
                "Buying less, repairing clothes and using second-hand options",
                "Purchasing a new outfit every week",
                "Ignoring supply-chain information",
                "Burning unused clothes at home",
                "Refusing to wear any clothing",
            ], 0),
            q(6, "Why are government requirements still important?", [
                "Clearer supply-chain information strengthens individual efforts",
                "Governments must ban all second-hand shops",
                "Rules make trends change faster",
                "Laws remove the need for recycling",
                "Officials should hide factory conditions",
            ], 0),
            q(7, "What does the writer refuse to claim?", [
                "That fashion itself is simply bad",
                "That pollution can affect rivers",
                "That overtime pressure exists",
                "That trends change quickly",
                "That recycled fibres are sometimes used",
            ], 0),
            q(8, "What “harder question” does the passage raise?", [
                "Whether endless newness justifies environmental and human costs",
                "Whether museums should sell clothes",
                "Whether social media can post photos",
                "Whether prices should always rise",
                "Whether factories can close on weekends",
            ], 0),
            q(9, "Which statement is best supported by the text?", [
                "Low prices hide pressures on workers and the environment",
                "Fast fashion has no connection to waste",
                "Conscious collections already replaced all other lines",
                "Consumers cannot influence demand at all",
                "Unsold clothes are never discarded",
            ], 0),
            q(10, "What is the best title?", [
                "The Cost of Fast Fashion",
                "Airport Delay Notices",
                "Library Opening Hours",
                "Cooking with Vegetables",
                "Silent Cinema History",
            ], 0),
        ],
    )
)

ITEMS.append(
    pack(
        4,
        "Sleep Debt and Performance",
        p(
            "Modern work culture often treats sleep as optional. People celebrate late nights finished before a deadline, then rely on coffee to survive the next morning. Sleep scientists describe the missing rest as “sleep debt,” which accumulates across the week.",
            "Research shows that even moderate sleep loss reduces attention, memory and emotional control. Drivers with several nights of poor sleep can react as slowly as someone over the legal alcohol limit, yet they may feel only “a bit tired.”",
            "Companies that extend meeting hours into the evening rarely measure the hidden cost: more mistakes, weaker creativity and higher staff turnover. A few organisations now protect “no-meeting mornings” so employees can focus when their brains are freshest.",
            "Catching up on weekends helps only partly. Sleeping until noon on Saturday can ease short-term exhaustion, but it does not fully repair the damage of five short weeknights. Regular schedules matter more than occasional long sleeps.",
            "Improving sleep is not a luxury trend. It is a performance strategy. People who defend seven to nine hours usually work more effectively than those who treat exhaustion as proof of commitment. In the long run, rested teams deliver more than tired heroes.",
        ),
        [
            q(1, "What is “sleep debt” in this passage?", [
                "Missing rest that builds up over time",
                "Money owed for buying a bed",
                "A tax on coffee sales",
                "A company bonus for night work",
                "A medical device that records dreams",
            ], 0),
            q(2, "What can several nights of poor sleep do to drivers?", [
                "Slow their reactions to levels similar to excess alcohol",
                "Improve night vision automatically",
                "Remove all feeling of tiredness",
                "Make legal alcohol limits unnecessary",
                "Increase creativity while driving",
            ], 0),
            q(3, "Why may tired people underestimate the problem?", [
                "They may feel only slightly tired despite major impairment",
                "They sleep longer than scientists recommend",
                "Coffee permanently restores memory",
                "Deadlines cancel biological needs",
                "Meetings always happen in the morning",
            ], 0),
            q(4, "What hidden costs of late meetings does the text mention?", [
                "More mistakes, weaker creativity and higher turnover",
                "Lower coffee sales in offices",
                "Longer weekend holidays for everyone",
                "Automatic salary increases",
                "Fewer emails during the day",
            ], 0),
            q(5, "Why do some organisations protect “no-meeting mornings”?", [
                "So staff can focus when mental performance is strongest",
                "Because mornings are illegal for communication",
                "To force employees to sleep at their desks",
                "To cancel all deadlines permanently",
                "To increase evening meeting numbers",
            ], 0),
            q(6, "What limitation of weekend catch-up sleep is described?", [
                "It helps partly but cannot fully repair five short weeknights",
                "It completely erases all sleep debt every time",
                "It is more effective than regular schedules",
                "It works only for drivers",
                "It replaces the need for weekday sleep",
            ], 0),
            q(7, "What does the writer value more than occasional long sleeps?", [
                "Regular sleep schedules",
                "Late-night deadlines",
                "Extra evening meetings",
                "Celebrating exhaustion",
                "Drinking more coffee",
            ], 0),
            q(8, "How does the writer reframe good sleep?", [
                "As a performance strategy, not a luxury trend",
                "As proof that someone is lazy",
                "As unrelated to attention and memory",
                "As useful only for professional drivers",
                "As less important than visible overtime",
            ], 0),
            q(9, "Which claim matches the passage most closely?", [
                "People who protect enough sleep often work more effectively",
                "Exhaustion is the best evidence of commitment",
                "Sleep loss improves emotional control",
                "Weekend sleep fully cancels weekday debt",
                "Meeting culture has no effect on mistakes",
            ], 0),
            q(10, "What is the best title?", [
                "Sleep Debt and Performance",
                "Museum Gift Shops",
                "Train Ticket Refunds",
                "Football Team Scores",
                "Hotel Breakfast Menus",
            ], 0),
        ],
    )
)

ITEMS.append(
    pack(
        5,
        "Myths About Language Learning",
        p(
            "Many adults believe they missed their chance to learn a language because childhood is “the only time the brain can change.” Neuroscience does not support this extreme claim. Adults learn differently, not uselessly: they bring stronger learning strategies and clearer goals.",
            "Another common myth is that fluency requires living abroad for years. Immersion helps, but motivated learners who practise daily with quality input can progress significantly at home. The key is regular meaningful use, not a passport stamp.",
            "Apps that promise fluency in thirty days create unrealistic expectations. Short daily practice is valuable, yet complex grammar, pronunciation and cultural nuance need longer, varied exposure. Learners who quit after one month often blame themselves instead of the marketing.",
            "Teachers increasingly combine communicative tasks with deliberate focus on form. Conversation alone may leave fossilised errors; grammar drills alone rarely build confidence. Balanced courses treat accuracy and fluency as partners.",
            "The most useful mindset is patience with evidence. Progress feels slow week by week, but recorded speaking samples and reading logs reveal growth that mood cannot measure on a bad day. Learners who trust evidence stay longer — and staying longer is what creates fluency.",
        ),
        [
            q(1, "What extreme belief does the text reject?", [
                "That only children can change their brains enough to learn languages",
                "That adults never need learning strategies",
                "That living abroad is sometimes helpful",
                "That apps can support daily practice",
                "That grammar focus can be useful",
            ], 0),
            q(2, "What advantage do adult learners have, according to the writer?", [
                "Stronger strategies and clearer goals",
                "A permanent inability to improve",
                "No need for regular practice",
                "Automatic fluency after one week",
                "Better results without any input",
            ], 0),
            q(3, "Why is living abroad not presented as the only path?", [
                "Daily meaningful practice at home can also produce major progress",
                "Passports guarantee fluency without study",
                "Immersion never helps anyone",
                "Teachers ban study abroad programmes",
                "Apps replace all human interaction forever",
            ], 0),
            q(4, "What problem do “thirty-day fluency” promises create?", [
                "Unrealistic expectations that lead people to quit and self-blame",
                "Perfect pronunciation in one weekend",
                "Government scholarships for every learner",
                "The end of all marketing in education",
                "Immediate cultural understanding",
            ], 0),
            q(5, "What limitation of conversation-only practice is mentioned?", [
                "Errors may become fossilised without focus on form",
                "Learners never gain confidence",
                "Grammar drills become unnecessary forever",
                "Cultural nuance appears automatically",
                "Reading logs stop working",
            ], 0),
            q(6, "What limitation of grammar drills alone is mentioned?", [
                "They rarely build communicative confidence by themselves",
                "They erase all fossilised errors instantly",
                "They replace the need for input",
                "They guarantee native accents",
                "They make apps illegal",
            ], 0),
            q(7, "What teaching approach does the text favour?", [
                "Combining communicative tasks with deliberate attention to form",
                "Only silent grammar translation",
                "Only tourist phrase lists",
                "Stopping all accuracy work",
                "Promising fluency in thirty days",
            ], 0),
            q(8, "Why does the writer recommend recorded samples and reading logs?", [
                "They show progress that feelings on a bad day may hide",
                "They replace the need to practise speaking",
                "They prove adults cannot improve",
                "They are required for passport applications",
                "They make marketing claims true",
            ], 0),
            q(9, "Which statement best reflects the writer’s overall message?", [
                "Adults can learn well with realistic methods and steady evidence of progress",
                "Only childhood learners should study languages",
                "Fluency always requires emigration",
                "Short marketing courses are enough for nuance",
                "Patience is unnecessary if an app is colourful",
            ], 0),
            q(10, "What is the best title?", [
                "Myths About Language Learning",
                "Bus Route Changes",
                "Hospital Waiting Times",
                "Cooking Oil Prices",
                "Stadium Parking Rules",
            ], 0),
        ],
    )
)

ITEMS.append(
    pack(
        6,
        "Food Waste in the Supply Chain",
        p(
            "When people discuss food waste, they often imagine leftovers on a dinner plate. In reality, a large share of loss happens earlier: crops left unharvested because prices fell, fruit rejected for unusual shape, and supermarket shelves cleared before the printed date even when products remain safe.",
            "Farmers may destroy surplus rather than sell at a loss, especially when transport and storage cost more than the expected income. Retailers fear empty shelves less than they fear customers seeing imperfect stock, so appearance standards remain strict.",
            "Several cities now connect surplus food to charities through refrigerated logistics apps. The challenge is speed and trust: donations must stay cold, arrive on time and meet hygiene rules. Without reliable systems, good intentions fail.",
            "Households still matter. Planning meals, understanding date labels and storing food correctly can cut waste dramatically. Education campaigns work best when combined with smaller package sizes and discounts on near-date items.",
            "Reducing waste is both an ethical and an economic issue. Food that never reaches a plate wastes land, water and labour. Smarter systems turn potential rubbish into meals — and reduce pressure on the climate.",
        ),
        [
            q(1, "What misconception about food waste does the text correct?", [
                "That waste occurs only as leftovers on plates",
                "That farms never lose any crops",
                "That date labels are always meaningless",
                "That charities refuse all donations",
                "That packaging size never affects waste",
            ], 0),
            q(2, "Why might farmers destroy surplus produce?", [
                "Selling it could cost more in transport and storage than it earns",
                "Laws ban selling any fruit with normal shapes",
                "Customers demand empty supermarket shelves",
                "Apps require every crop to be burned",
                "Charities pay higher prices than markets",
            ], 0),
            q(3, "Why do retailers keep strict appearance standards?", [
                "They worry customers dislike imperfect-looking stock",
                "Unusual shapes are illegal to sell everywhere",
                "Perfect appearance increases harvest rainfall",
                "Date labels disappear on irregular fruit",
                "Charities only accept damaged food",
            ], 0),
            q(4, "What do refrigerated logistics apps try to do?", [
                "Move surplus food to charities quickly and safely",
                "Increase the number of empty shelves",
                "Remove hygiene rules for donations",
                "Force farmers to destroy more crops",
                "Stop discounts on near-date products",
            ], 0),
            q(5, "Why can good donation intentions fail?", [
                "Without reliable cold transport, timing and hygiene, systems break down",
                "Charities never need food",
                "Customers prefer wasted meals",
                "Education campaigns ban apps",
                "Package sizes cannot change",
            ], 0),
            q(6, "Which household practices does the writer recommend?", [
                "Meal planning, understanding labels and correct storage",
                "Ignoring date labels completely",
                "Buying only the largest packages always",
                "Leaving surplus crops in fields",
                "Avoiding discounts on near-date items",
            ], 0),
            q(7, "How can retailers support lower household waste?", [
                "Smaller packages and discounts on near-date items",
                "Removing all date information",
                "Banning charity partnerships",
                "Keeping shelves empty on purpose",
                "Rejecting every imperfect fruit forever",
            ], 0),
            q(8, "Why is food waste described as more than an ethical problem?", [
                "It also wastes land, water and labour and increases climate pressure",
                "It only affects restaurant menus",
                "It reduces supermarket advertising costs",
                "It improves soil quality automatically",
                "It has no economic effects",
            ], 0),
            q(9, "Which conclusion fits the passage?", [
                "Waste reduction needs better systems plus smarter everyday habits",
                "Only plate leftovers matter in the supply chain",
                "Appearance standards have no commercial reason",
                "Apps alone remove the need for hygiene rules",
                "Farmers always profit from surplus sales",
            ], 0),
            q(10, "What is the best title?", [
                "Food Waste in the Supply Chain",
                "Cinema Ticket Discounts",
                "Mountain Climbing Tips",
                "Library Late Fees",
                "Phone Screen Repair",
            ], 0),
        ],
    )
)

ITEMS.append(
    pack(
        7,
        "Who Should Pay for Public Transport?",
        p(
            "Public transport debates often start with ticket prices, but the deeper question is who should fund the network. If fares cover the full cost, low-income workers may be priced out of reliable commuting. If taxes cover almost everything, people who never use buses may protest.",
            "Economists note that cars also receive hidden support through road space, parking rules and pollution that others breathe. When these costs are ignored, private driving looks cheaper than it truly is, and buses seem expensive by comparison.",
            "Some cities keep fares low and invest in frequency: a bus every six minutes attracts riders who would otherwise drive. Higher ridership can justify the subsidy because fewer cars mean less congestion for everyone, including drivers.",
            "Other cities experiment with peak pricing — higher tickets at rush hour — to spread demand. Critics say this punishes workers with fixed schedules. Supporters reply that free travel for students and shift workers can protect fairness.",
            "There is no single correct formula. A healthy system usually mixes fares, local taxes and targeted discounts, guided by clear goals: access to jobs, cleaner air and predictable journey times.",
        ),
        [
            q(1, "What deeper issue sits behind ticket-price arguments?", [
                "How the transport network should be funded",
                "Which bus colour passengers prefer",
                "Whether trains should serve museums only",
                "How to ban all local taxes",
                "Whether drivers need free parking everywhere",
            ], 0),
            q(2, "What risk appears if fares must cover the full cost?", [
                "Low-income workers may be unable to afford reliable commuting",
                "Buses will arrive every six minutes automatically",
                "Air pollution will disappear",
                "Students will receive unlimited free travel",
                "Congestion will end without subsidies",
            ], 0),
            q(3, "Why can private driving look artificially cheap?", [
                "Hidden costs like road space and pollution are often ignored",
                "Buses never receive any public money",
                "Ticket machines always overcharge cars",
                "Economists ban parking rules",
                "Rush-hour pricing removes all taxes",
            ], 0),
            q(4, "How can frequent service justify subsidies?", [
                "It attracts riders, cuts car use and reduces congestion for everyone",
                "It forces non-users to ride buses daily",
                "It raises pollution in city centres",
                "It eliminates the need for journey-time goals",
                "It removes discounts for shift workers",
            ], 0),
            q(5, "What is peak pricing designed to do?", [
                "Spread demand away from the busiest hours",
                "Make weekends more crowded than weekdays",
                "Ban students from public transport",
                "Increase traffic for private cars only",
                "Replace all local tax funding",
            ], 0),
            q(6, "Why do critics dislike peak pricing?", [
                "Workers with fixed schedules may be unfairly punished",
                "It always lowers fares at rush hour",
                "It guarantees free travel for every passenger",
                "It removes buses from the timetable",
                "It hides the cost of road space",
            ], 0),
            q(7, "How do supporters of peak pricing suggest protecting fairness?", [
                "By offering free or protected travel for students and shift workers",
                "By ending all discounts permanently",
                "By charging children the highest fares",
                "By closing routes to job centres",
                "By ignoring air-quality goals",
            ], 0),
            q(8, "What funding mix does the writer generally favour?", [
                "Fares, local taxes and targeted discounts together",
                "Fares only, with no public contribution",
                "Taxes only, with no tickets at all",
                "Tourism fees paid by museums exclusively",
                "Parking fines as the only income source",
            ], 0),
            q(9, "Which goals should guide the system, according to the text?", [
                "Job access, cleaner air and predictable journey times",
                "Maximum profit from every single ride",
                "Empty buses for advertising photos",
                "Longer car queues in every district",
                "Removing services from low-income areas",
            ], 0),
            q(10, "What is the best title?", [
                "Who Should Pay for Public Transport?",
                "Baking Bread at Home",
                "Football Transfer Rumours",
                "Beach Holiday Photos",
                "Laptop Battery Care",
            ], 0),
        ],
    )
)

ITEMS.append(
    pack(
        8,
        "AI Tools in Classrooms",
        p(
            "Artificial intelligence tools can draft essays, explain maths steps and translate reading texts within seconds. Enthusiastic teachers see a chance to give every student a patient tutor. Sceptical teachers fear that students will submit machine-written work and learn less.",
            "The strongest classroom uses are often supportive rather than replacement-based. AI can generate practice questions at different levels, summarise a difficult article for preparation, or help learners check grammar before a teacher reviews ideas and arguments.",
            "Assessment design must change with the technology. If homework only asks for a polished final text, cheating becomes easy. Tasks that require process notes, oral defence of ideas or personal data from local projects are harder to outsource to a chatbot.",
            "Equity is another concern. Students with fast devices and quiet study space gain more from AI practice than classmates sharing a phone. Schools that ignore this gap may widen existing inequalities while celebrating “innovation.”",
            "Used carefully, AI is a powerful assistant. Used blindly, it becomes a shortcut that weakens thinking. The difference depends less on the software itself than on the learning goals teachers set around it.",
        ),
        [
            q(1, "What opportunity do enthusiastic teachers see in AI?", [
                "A patient tutor available to every student",
                "A way to close all schools",
                "A replacement for every oral exam",
                "A ban on homework forever",
                "A tool that removes teacher planning",
            ], 0),
            q(2, "What do sceptical teachers mainly fear?", [
                "Students submitting machine-written work and learning less",
                "AI refusing to translate any text",
                "Practice questions becoming too difficult",
                "Devices becoming slower than books",
                "Grammar checks disappearing completely",
            ], 0),
            q(3, "Which classroom uses does the text call strongest?", [
                "Supportive uses such as practice, summaries and grammar checks before review",
                "Replacing teachers in every lesson",
                "Letting chatbots grade oral defence alone",
                "Stopping all personal projects",
                "Removing process notes from assessment",
            ], 0),
            q(4, "Why must assessment design change?", [
                "Polished final-text homework is easy to outsource to chatbots",
                "Students no longer need ideas or arguments",
                "Oral defence has become impossible",
                "Local projects cannot include personal data",
                "Grammar practice is now illegal",
            ], 0),
            q(5, "Which task features make AI outsourcing harder?", [
                "Process notes, oral defence and local personal project data",
                "Only asking for a perfect final essay",
                "Allowing unlimited anonymous chatbot submission",
                "Removing all teacher review",
                "Translating texts without discussion",
            ], 0),
            q(6, "What equity problem does the passage highlight?", [
                "Students with better devices and space benefit more from AI practice",
                "All students share identical study conditions",
                "Innovation always reduces inequality automatically",
                "Phones cannot run any AI tool",
                "Quiet space is irrelevant to learning gaps",
            ], 0),
            q(7, "What risk do schools face if they ignore the access gap?", [
                "Celebrating innovation while widening inequality",
                "Making every student equally advanced overnight",
                "Eliminating the need for learning goals",
                "Banning supportive AI uses forever",
                "Removing maths explanations from class",
            ], 0),
            q(8, "According to the writer, what mainly decides AI’s educational value?", [
                "The learning goals teachers set around the tools",
                "The brand name of the software alone",
                "Whether essays can be drafted in seconds",
                "How colourful the chatbot interface is",
                "Whether translation features exist",
            ], 0),
            q(9, "Which statement best matches the writer’s balanced view?", [
                "AI helps when it supports thinking and harms when it replaces thinking",
                "AI should write every assessed essay",
                "Teachers should never allow grammar checking",
                "Device access differences do not matter",
                "Assessment can stay unchanged forever",
            ], 0),
            q(10, "What is the best title?", [
                "AI Tools in Classrooms",
                "Zoo Animal Feeding Times",
                "Winter Coat Sales",
                "Train Platform Closures",
                "Guitar Lesson Prices",
            ], 0),
        ],
    )
)

ITEMS.append(
    pack(
        9,
        "The Problem with Volunteer Tourism",
        p(
            "Volunteer tourism promises meaningful holidays: travellers paint schools, play with children or help at animal shelters for a week, then post smiling photographs online. The industry sells purpose as part of the package price.",
            "Researchers have documented serious downsides. Short visits disrupt children’s need for stable caregivers. Unskilled volunteers may do construction work that local workers could be paid to complete. In worst cases, orphanages have been created mainly to attract donations and visitors.",
            "Not every project is exploitative. Longer placements with professional training, local leadership and transparent finances can contribute real skills. The difference is whether the programme serves the community’s stated needs or the visitor’s desire to feel useful quickly.",
            "Ethical travellers ask hard questions before booking: Who designed the project? Are local staff paid fairly? What happens after volunteers leave? If answers are vague, the “help” may be branding rather than impact.",
            "Wanting to do good is not the problem. The problem is confusing a short emotional experience with sustainable development. Better alternatives often include supporting local organisations financially or volunteering where one’s professional skills are genuinely required.",
        ),
        [
            q(1, "What does volunteer tourism package together?", [
                "Holiday travel and a sense of purpose sold as part of the price",
                "Only professional medical training courses",
                "Permanent jobs for every visitor",
                "Government scholarships for local workers",
                "Free housing for all community leaders",
            ], 0),
            q(2, "How can short visits harm children, according to researchers?", [
                "They disrupt children’s need for stable caregivers",
                "They always improve exam results immediately",
                "They replace the need for schools",
                "They guarantee long-term friendships",
                "They remove all online photographs",
            ], 0),
            q(3, "Why can unskilled construction volunteering be problematic?", [
                "Local workers could be paid to do the same work",
                "Paint is illegal in every country",
                "Shelters refuse all adult visitors",
                "Projects never need any building repairs",
                "Tourists cannot post photographs afterwards",
            ], 0),
            q(4, "What extreme abuse is mentioned in the text?", [
                "Orphanages created mainly to attract donations and visitors",
                "Schools banning all international contact",
                "Animal shelters refusing volunteers with training",
                "Communities rejecting transparent finances",
                "Travellers refusing to feel useful",
            ], 0),
            q(5, "When can volunteer programmes still be valuable?", [
                "When they involve longer stays, training, local leadership and clear finances",
                "When visits last only one afternoon",
                "When no local staff are paid",
                "When project goals remain secret",
                "When emotional photos matter more than needs",
            ], 0),
            q(6, "What key difference does the writer emphasise?", [
                "Serving community needs versus satisfying a visitor’s quick wish to feel useful",
                "Choosing beaches instead of cities",
                "Posting more photographs online",
                "Avoiding all professional skills",
                "Paying higher package prices always",
            ], 0),
            q(7, "Which pre-booking question matches the text’s advice?", [
                "Who designed the project and are local staff paid fairly?",
                "Which filter looks best on social media?",
                "How quickly can I finish and leave?",
                "Can the orphanage increase visitor numbers this month?",
                "Will the hotel include free breakfast?",
            ], 0),
            q(8, "What do vague answers to ethical questions suggest?", [
                "The “help” may be branding more than real impact",
                "The project is definitely sustainable",
                "Local leadership is unusually strong",
                "Finances must already be transparent",
                "Professional skills are not required anywhere",
            ], 0),
            q(9, "What alternatives does the writer recommend?", [
                "Funding local organisations or volunteering where real skills are needed",
                "Taking more one-week painting trips",
                "Creating more orphanages for tourism",
                "Avoiding all questions before booking",
                "Replacing local workers with unskilled visitors",
            ], 0),
            q(10, "What is the best title?", [
                "The Problem with Volunteer Tourism",
                "Recipe for Chocolate Cake",
                "City Marathon Results",
                "New Smartphone Models",
                "Office Chair Design",
            ], 0),
        ],
    )
)

ITEMS.append(
    pack(
        10,
        "Water Scarcity Is Not Only About Rain",
        p(
            "When reservoirs look low, people blame the weather. Rainfall matters, but water scarcity is often created by how societies manage demand: leaking pipes, thirsty crops in dry regions, and cities that expand faster than their water systems.",
            "Agriculture uses a large share of freshwater in many countries. Exporting water-intensive crops from dry areas is sometimes called “virtual water” trade — shipping the water footprint abroad inside food. This can support farmers’ incomes while deepening local shortages.",
            "Cities lose astonishing volumes through old infrastructure. Fixing leaks is less glamorous than building a new dam, yet it can deliver more water per dollar. Political leaders still prefer visible megaprojects that photograph well at opening ceremonies.",
            "Households can adapt by repairing taps, choosing efficient appliances and questioning decorative lawns in arid climates. Still, personal savings cannot compensate for industrial waste or misdirected agricultural policy.",
            "Treating scarcity as only a natural disaster hides responsibility. Droughts are natural events; crises become disasters when planning ignores limits. Resilient communities invest early in efficiency, fair pricing and crops suited to the climate they actually have.",
        ),
        [
            q(1, "What main point does the opening make about scarcity?", [
                "Management of demand often matters as much as rainfall",
                "Rain never affects reservoirs",
                "Leaking pipes are imaginary",
                "Cities never expand",
                "Agriculture uses no freshwater",
            ], 0),
            q(2, "What is “virtual water” trade in this text?", [
                "Exporting water-intensive crops and thus shipping a water footprint abroad",
                "Selling bottled rain online as a digital product",
                "Building dams only for tourism photos",
                "Repairing taps in private homes",
                "Pricing water fairly in cities",
            ], 0),
            q(3, "What tension does virtual water trade create?", [
                "Farmer income may rise while local shortages deepen",
                "Crops stop needing any water",
                "Export bans appear in every dry region automatically",
                "Cities gain unlimited reservoirs",
                "Leaks disappear without repairs",
            ], 0),
            q(4, "Why can fixing leaks outperform a new dam?", [
                "It can provide more water per dollar spent",
                "It creates better opening ceremony photos",
                "It increases decorative lawns",
                "It removes the need for fair pricing",
                "It makes agriculture unnecessary",
            ], 0),
            q(5, "Why do leaders still favour megaprojects, according to the writer?", [
                "They are more visible and photograph well politically",
                "They always cost less than leak repairs",
                "Scientists ban efficiency investments",
                "Households refuse to save any water",
                "Dams hide all responsibility for planning",
            ], 0),
            q(6, "Which household actions are suggested?", [
                "Repairing taps, using efficient appliances and questioning lawns in dry climates",
                "Watering decorative lawns more often",
                "Ignoring industrial water waste",
                "Expanding cities without new systems",
                "Exporting more thirsty crops",
            ], 0),
            q(7, "What limitation of personal savings does the text stress?", [
                "They cannot offset industrial waste or poor agricultural policy alone",
                "They solve scarcity without any government role",
                "They replace the need for climate-suited crops",
                "They make megaprojects unnecessary forever",
                "They remove droughts as natural events",
            ], 0),
            q(8, "How does the writer distinguish droughts from disasters?", [
                "Droughts are natural; disasters grow when planning ignores limits",
                "Disasters are natural and droughts are political only",
                "Both are caused only by household taps",
                "Neither relates to water management",
                "Dams prevent all natural droughts permanently",
            ], 0),
            q(9, "What early investments mark resilient communities?", [
                "Efficiency, fair pricing and climate-suited crops",
                "Only glamorous megaprojects",
                "Unlimited lawns in arid cities",
                "Ignoring leaky infrastructure",
                "Exporting more water-intensive food without review",
            ], 0),
            q(10, "What is the best title?", [
                "Water Scarcity Is Not Only About Rain",
                "Birthday Party Games",
                "Online Game Rankings",
                "Shoe Shop Discounts",
                "Airport Duty-Free Lists",
            ], 0),
        ],
    )
)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for item in ITEMS:
        wc = word_count(item["shared_passage"])
        assert 160 <= wc <= 400, (item["title"], wc)
        for row in item["questions"]:
            assert len(row["options"]) == 5
            assert 0 <= row["answer"] < 5
        path = OUT / f"b1_reading_test_{item['quiz']:02d}.json"
        path.write_text(json.dumps(item, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {path.name} ({wc} words)")


if __name__ == "__main__":
    main()
