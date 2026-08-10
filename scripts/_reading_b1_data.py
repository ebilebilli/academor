# -*- coding: utf-8 -*-
"""B1 reading tests — stronger passages (~240–300 words) + real questions."""
from __future__ import annotations

from _reading_a1_data import p, q, pack

B1 = []

B1.append(
    pack(
        "B1",
        1,
        "City Noise",
        p(
            "In many growing cities, night noise has become a serious quality-of-life issue. Residents often complain about late deliveries, loud cafes and motorbikes that race through narrow streets after midnight.",
            "A local survey of 200 people in one district found that 65% want quieter streets after 11 p.m. Parents said their children wake up easily, while night-shift workers argued that some noise is unavoidable.",
            "Cafe owners worry that strict rules could reduce income, especially on weekends. They suggest better soundproofing and earlier closing times for outdoor seating instead of a total ban on evening business.",
            "The city council has promised a three-month quiet-zone trial. During the trial, loud deliveries will be limited after 10:30 p.m., and fines will apply to repeated violations. Results will be published online.",
            "The discussion remains balanced: people need rest, but local businesses also need customers. A fair solution will probably combine clear rules, realistic exceptions and regular public feedback.",
        ),
        [
            q(1, "What problem does the article discuss?", ["Night noise in cities", "Airport ticket prices", "School uniforms", "Online shopping mistakes"], 0),
            q(2, "How many people took part in the survey?", ["200", "65", "10", "2,000"], 0),
            q(3, "What percentage want quieter streets after 11 p.m.?", ["65%", "11%", "30%", "100%"], 0),
            q(4, "Why are parents concerned?", ["Children wake up easily", "Cafes are too expensive", "There are no parks", "Schools close early"], 0),
            q(5, "What do cafe owners fear?", ["Lower income from strict rules", "More customers than they can serve", "Free food rules", "A ban on coffee"], 0),
            q(6, "What alternative do cafe owners suggest?", ["Soundproofing and earlier outdoor closing", "Closing forever", "Louder music", "Moving all cafes abroad"], 0),
            q(7, "How long is the quiet-zone trial?", ["Three months", "Three days", "Three years", "One weekend"], 0),
            q(8, "When will loud deliveries be limited?", ["After 10:30 p.m.", "After 11 a.m.", "All day", "Never"], 0),
            q(9, "Where will results be published?", ["Online", "Only in a locked office", "Never", "On cafe menus"], 0),
            q(10, "What is the best title?", ["City Noise", "Space News", "Bank Fraud", "Silent Movies"], 0),
        ],
    )
)

B1.append(
    pack(
        "B1",
        2,
        "Remote Work",
        p(
            "Remote work has changed how many companies organise daily life. Instead of travelling to an office every morning, employees connect through video calls, shared documents and messaging apps.",
            "Supporters say remote work saves commuting time and can improve concentration for tasks that need quiet. Parents of young children sometimes find a better balance between meetings and family responsibilities.",
            "However, critics warn that people may feel isolated. Without informal conversations in corridors, new staff can learn company culture more slowly. Some managers also worry about teamwork on creative projects.",
            "A recent company report suggested a hybrid model: three office days and two remote days. Staff liked the flexibility, but asked for clearer rules about meeting times across different time zones.",
            "Remote work is not perfect for every job. Teachers, nurses and factory workers still need to be present. The real challenge is choosing the right mix for each role rather than copying one fashion for everyone.",
        ),
        [
            q(1, "What is remote work mainly about?", ["Working from outside a traditional office", "Closing all companies", "Working only at night", "Stopping all meetings"], 0),
            q(2, "What advantage do supporters mention?", ["Saving commuting time", "Never using computers", "No need for skills", "Higher train prices"], 0),
            q(3, "What problem do critics mention?", ["Isolation and slower culture learning", "Too many free holidays", "Offices becoming larger", "No internet anywhere"], 0),
            q(4, "What hybrid model did a report suggest?", ["Three office days and two remote days", "Seven remote days", "No remote days", "One office hour a year"], 0),
            q(5, "What did staff ask for?", ["Clearer meeting-time rules across time zones", "More night shifts only", "Ban on messaging apps", "Removal of all documents"], 0),
            q(6, "Which jobs still need presence, according to the text?", ["Teachers, nurses and factory workers", "Only bank managers", "Only designers", "Nobody"], 0),
            q(7, "What is described as the real challenge?", ["Choosing the right mix for each role", "Copying one fashion for everyone", "Closing offices forever", "Stopping video calls"], 0),
            q(8, "Why can new staff struggle remotely?", ["They learn company culture more slowly", "They earn too much", "Offices are too quiet", "Trains are free"], 0),
            q(9, "What tools are mentioned for remote connection?", ["Video calls, shared documents and messaging apps", "Only paper letters", "Only radio", "Only taxis"], 0),
            q(10, "What is the best title?", ["Remote Work", "Lost Keys", "Surprise Party", "Silent Movies"], 0),
        ],
    )
)

B1.append(
    pack(
        "B1",
        3,
        "Plastic Waste",
        p(
            "Plastic waste is visible almost everywhere: on beaches, in rivers and even in city parks after public events. Single-use bottles and bags are convenient, but they stay in the environment for a very long time.",
            "Scientists warn that tiny pieces of plastic can enter the food chain. Fish may swallow microplastics, and people later eat those fish. The full health effects are still being studied, which makes the issue urgent.",
            "Some cities have banned free plastic bags in shops. Customers now bring reusable bags or pay a small fee. Supermarkets also offer refill stations for cleaning products to reduce packaging.",
            "Young activists organise weekend clean-ups and create social media campaigns. Their message is simple: refuse unnecessary plastic, reuse what you can, and recycle correctly.",
            "Governments, companies and ordinary people all share responsibility. Changing habits is not always easy, but small daily choices can reduce the mountain of waste that future generations will inherit.",
        ),
        [
            q(1, "Where is plastic waste visible, according to the text?", ["Beaches, rivers and city parks", "Only inside factories", "Only on the moon", "Nowhere"], 0),
            q(2, "Why are single-use plastics a long-term problem?", ["They stay in the environment a long time", "They disappear in one day", "They are always recycled perfectly", "They are made of metal"], 0),
            q(3, "What can enter the food chain?", ["Tiny pieces of plastic", "Only paper cups", "Reusable bags", "Refill stations"], 0),
            q(4, "What have some cities banned?", ["Free plastic bags in shops", "All fish", "Reusable bags", "Social media"], 0),
            q(5, "What do supermarkets offer to reduce packaging?", ["Refill stations for cleaning products", "More free bottles", "Plastic-only aisles", "Nothing"], 0),
            q(6, "What do young activists organise?", ["Weekend clean-ups and campaigns", "Plastic factories", "Beach parties with more waste", "Car races"], 0),
            q(7, "What is their simple message?", ["Refuse, reuse and recycle correctly", "Buy more plastic", "Ignore recycling", "Throw everything in rivers"], 0),
            q(8, "Who shares responsibility?", ["Governments, companies and ordinary people", "Only children", "Only tourists", "Nobody"], 0),
            q(9, "Are the full health effects of microplastics fully known?", ["They are still being studied", "They are completely known and harmless", "There is no research", "Doctors say plastic is food"], 0),
            q(10, "What is the best title?", ["Plastic Waste", "Surprise Party", "Lost Keys", "Silent Movies"], 0),
        ],
    )
)

B1.append(
    pack(
        "B1",
        4,
        "School Clubs",
        p(
            "After-school clubs can make school life richer than lessons alone. Drama, robotics, chess and environmental clubs give students a chance to explore interests that do not always fit into the normal timetable.",
            "Teachers say clubs improve social skills. Students learn to listen, share tasks and solve disagreements without a formal test. Shy teenagers often speak more confidently after months in a friendly club.",
            "However, not every student can stay after school. Some help at home, travel long distances, or have part-time jobs. Schools that offer lunchtime clubs or online options include more people.",
            "Funding is another challenge. Equipment for robotics or musical instruments can be expensive. Parent associations and local businesses sometimes donate materials or sponsor competitions.",
            "A good club programme does not need to be perfect. It needs regular meetings, supportive adults and clear goals so that students feel progress, not just entertainment.",
        ),
        [
            q(1, "What do school clubs offer beyond lessons?", ["A chance to explore extra interests", "Only more exams", "Longer commuting", "Less social contact"], 0),
            q(2, "What social benefit do teachers mention?", ["Listening, sharing tasks and solving disagreements", "Avoiding all classmates", "Silent rooms only", "No teamwork"], 0),
            q(3, "Who may speak more confidently after joining a club?", ["Shy teenagers", "Only teachers", "Only parents", "Nobody"], 0),
            q(4, "Why can’t every student stay after school?", ["Home duties, long travel or part-time jobs", "Clubs are illegal", "Schools ban all clubs", "There is no interest anywhere"], 0),
            q(5, "How can schools include more students?", ["Lunchtime clubs or online options", "Closing all clubs", "Making clubs more expensive", "Only weekend foreign trips"], 0),
            q(6, "What is a funding challenge?", ["Expensive equipment", "Free air", "Too many volunteers", "No students"], 0),
            q(7, "Who sometimes helps with materials?", ["Parent associations and local businesses", "Only international airlines", "Only strangers online", "Nobody"], 0),
            q(8, "What does a good club programme need?", ["Regular meetings, supportive adults and clear goals", "Only entertainment with no goals", "One meeting a year", "No adults present"], 0),
            q(9, "Which clubs are mentioned as examples?", ["Drama, robotics, chess and environmental clubs", "Only cooking for exams", "Only bank clubs", "Only silent reading forever"], 0),
            q(10, "What is the best title?", ["School Clubs", "Airport Delay", "Bank Fraud", "Lost Keys"], 0),
        ],
    )
)

B1.append(
    pack(
        "B1",
        5,
        "Travel Apps",
        p(
            "Travel apps have become everyday tools for people who move between cities or countries. With a few taps, travellers can compare ticket prices, check hotel reviews and download offline maps.",
            "Useful features include real-time transport updates and translation cameras that turn street signs into another language. Students on exchange programmes especially value apps that show safe walking routes at night.",
            "Still, technology can create new problems. If the phone battery dies, a tourist without a paper map may feel lost. Some apps also collect personal data, so privacy settings matter.",
            "Experienced travellers recommend a simple backup plan: screenshot key tickets, save the hotel address offline, and keep a small amount of local cash.",
            "Apps make travel easier, but they do not replace common sense. Looking up from the screen, asking local people politely, and noticing surroundings remain essential skills.",
        ),
        [
            q(1, "What can travellers do with travel apps?", ["Compare tickets, check hotels and download maps", "Control the weather", "Replace all languages permanently", "Build hotels"], 0),
            q(2, "What feature helps with street signs?", ["Translation cameras", "Louder music", "Battery drain only", "Cash machines"], 0),
            q(3, "Who especially values safe walking-route apps?", ["Students on exchange programmes", "Only airline pilots", "Only hotel owners", "Nobody"], 0),
            q(4, "What problem happens if the battery dies?", ["A tourist without a paper map may feel lost", "The city disappears", "Hotels close", "Apps become free forever"], 0),
            q(5, "Why do privacy settings matter?", ["Some apps collect personal data", "Apps never collect data", "Phones cannot store addresses", "Cash is digital only"], 0),
            q(6, "What backup plan is recommended?", ["Screenshot tickets, save hotel address offline, keep local cash", "Carry no phone and no cash", "Trust only memory", "Delete all apps before travel"], 0),
            q(7, "What skills remain essential?", ["Noticing surroundings and asking locals politely", "Looking only at the screen", "Ignoring people", "Never using maps"], 0),
            q(8, "Do apps replace common sense, according to the text?", ["No", "Yes completely", "Only at night", "Only for students"], 0),
            q(9, "What transport feature is mentioned?", ["Real-time transport updates", "Free private jets", "Horse riding maps only", "No transport information"], 0),
            q(10, "What is the best title?", ["Travel Apps", "Lost Keys", "Surprise Party", "Silent Movies"], 0),
        ],
    )
)

B1.append(
    pack(
        "B1",
        6,
        "Healthy Habits",
        p(
            "Healthy habits are built from small actions repeated over time. Sleeping enough, drinking water, moving every day and eating regular meals sound simple, yet many students struggle to keep them.",
            "Research often links short sleep with weaker concentration in morning classes. Teenagers who scroll on phones after midnight may feel tired even if they stay in bed for eight hours.",
            "Schools can help by offering short activity breaks and healthier canteen choices. Families can support routines by eating together when possible and limiting late-night screens.",
            "Extreme diets or sudden intense exercise are rarely sustainable. A realistic plan — a 20-minute walk, fruit instead of sugary snacks, and a fixed bedtime — usually works better.",
            "Health is not only about looking fit. Mood, energy and long-term focus improve when daily habits are steady. Progress matters more than perfection.",
        ),
        [
            q(1, "How are healthy habits built?", ["From small actions repeated over time", "From one perfect day only", "From ignoring sleep", "From midnight scrolling"], 0),
            q(2, "What is linked with weaker morning concentration?", ["Short sleep", "Drinking water", "Short walks", "Eating fruit"], 0),
            q(3, "What may make teenagers tired despite long time in bed?", ["Phone scrolling after midnight", "Fixed bedtimes", "Family dinners", "Activity breaks"], 0),
            q(4, "How can schools help?", ["Activity breaks and healthier canteen choices", "Longer night exams", "More sugary snacks only", "Banning all water"], 0),
            q(5, "What family supports are mentioned?", ["Eating together and limiting late screens", "No routines", "Extreme diets only", "Removing all exercise"], 0),
            q(6, "Why are extreme diets rarely useful here?", ["They are rarely sustainable", "They always work forever", "Doctors require them daily", "They replace sleep"], 0),
            q(7, "What realistic plan is suggested?", ["A short walk, fruit instead of sugary snacks, fixed bedtime", "No sleep for a week", "Only intense exercise suddenly", "Skipping all meals"], 0),
            q(8, "What improves with steady habits?", ["Mood, energy and long-term focus", "Only phone battery", "Only exam fees", "Nothing"], 0),
            q(9, "What matters more than perfection?", ["Progress", "Looking fit only", "Midnight scrolling", "Extreme change"], 0),
            q(10, "What is the best title?", ["Healthy Habits", "Bank Fraud", "Lost Keys", "Silent Movies"], 0),
        ],
    )
)

B1.append(
    pack(
        "B1",
        7,
        "Local Market",
        p(
            "Local markets are more than places to buy food. They are social spaces where neighbours meet, farmers sell seasonal produce and traditional recipes stay alive.",
            "Compared with large supermarkets, markets often offer fresher fruit and vegetables because items travel shorter distances. Customers can also ask sellers about growing methods and taste samples before buying.",
            "In some towns, markets struggle when shopping centres open nearby. Younger people may prefer online delivery for speed. To survive, many markets add evening hours, live music or cooking demonstrations.",
            "Supporting local markets can strengthen the community economy. Money spent with small producers is more likely to stay in the area and create local jobs.",
            "A weekly market visit can also teach children where food comes from. Seeing real tomatoes on a stall is different from selecting plastic-packed options without thinking.",
        ),
        [
            q(1, "What else are local markets besides shops?", ["Social spaces for neighbours and traditions", "Only online websites", "Silent empty halls", "Airports"], 0),
            q(2, "Why may market produce be fresher?", ["Shorter travel distances", "Longer storage in factories", "More plastic packaging", "Online delivery only"], 0),
            q(3, "What can customers ask sellers?", ["About growing methods", "About airline tickets", "About bank passwords", "About school exams"], 0),
            q(4, "What threatens some markets?", ["Nearby shopping centres and online delivery", "Too many farmers", "Free music forever", "Too much freshness"], 0),
            q(5, "How do markets try to survive?", ["Evening hours, music or cooking demonstrations", "Closing permanently", "Selling only plastic", "Banning young people"], 0),
            q(6, "How can markets help the local economy?", ["Money is more likely to stay in the area", "All money leaves immediately", "Jobs disappear", "Only tourists benefit abroad"], 0),
            q(7, "What can children learn from market visits?", ["Where food comes from", "How to fly planes", "How to ignore farmers", "How to shop only online"], 0),
            q(8, "What can customers do before buying?", ["Taste samples", "Take food without paying", "Close the stall", "Remove all sellers"], 0),
            q(9, "What preference of younger people is mentioned?", ["Online delivery for speed", "Only traditional recipes", "Never shopping", "Only evening concerts"], 0),
            q(10, "What is the best title?", ["Local Market", "Airport Delay", "Bank Fraud", "Silent Movies"], 0),
        ],
    )
)

B1.append(
    pack(
        "B1",
        8,
        "Public Transport",
        p(
            "Reliable public transport can reduce traffic, air pollution and the stress of daily commuting. Buses, metro lines and trains allow many people to travel without owning a car.",
            "When services run on time and stations feel safe, more citizens choose public options. Clear information boards, mobile ticket apps and night routes make the system more attractive.",
            "Problems appear when vehicles are overcrowded or delayed. Passengers may return to private cars, which then increases congestion. Cities that invest only in new roads often discover the traffic returns quickly.",
            "Fair pricing is also important. Student discounts and monthly passes help families plan costs. For older people, low-floor buses and priority seating improve access.",
            "Public transport works best as part of a wider plan that includes walking paths and bike lanes. The goal is not to punish drivers, but to give everyone practical choices.",
        ),
        [
            q(1, "What can reliable public transport reduce?", ["Traffic, pollution and commuting stress", "All walking", "All jobs", "Only ticket prices to zero forever"], 0),
            q(2, "What makes public options more attractive?", ["On-time service, safety, info boards and apps", "No night routes", "Hidden prices", "Overcrowding"], 0),
            q(3, "What happens if services are delayed and crowded?", ["People may return to private cars", "Traffic disappears", "Everyone walks only", "Stations close happily"], 0),
            q(4, "What do cities learn from building only new roads?", ["Traffic often returns quickly", "Cars vanish forever", "Buses become unnecessary forever", "Pollution ends automatically"], 0),
            q(5, "What pricing ideas help families?", ["Student discounts and monthly passes", "Random daily fines only", "No tickets for anyone ever", "Hidden fees"], 0),
            q(6, "What helps older passengers?", ["Low-floor buses and priority seating", "Higher steps only", "No seating", "Night racing"], 0),
            q(7, "What should accompany public transport in a wider plan?", ["Walking paths and bike lanes", "Only more private parking", "Closing all stations", "Banning all buses"], 0),
            q(8, "What is the goal described?", ["Give everyone practical choices", "Punish all drivers", "Remove all transport", "Stop student travel"], 0),
            q(9, "Which transport types are mentioned?", ["Buses, metro lines and trains", "Only helicopters", "Only taxis", "Only private jets"], 0),
            q(10, "What is the best title?", ["Public Transport", "Lost Keys", "Surprise Party", "Silent Movies"], 0),
        ],
    )
)

B1.append(
    pack(
        "B1",
        9,
        "Social Media",
        p(
            "Social media platforms connect friends, share news and open creative opportunities. Young people can learn skills from short videos, follow educational channels and join study groups across cities.",
            "At the same time, constant notifications can break concentration. Comparing perfect online images with real life may increase anxiety. Not every post is true, so media literacy is essential.",
            "Experts suggest practical limits: turn off non-essential alerts during homework, avoid screens one hour before sleep, and ask whether a post is helpful before sharing it.",
            "Schools that teach students how to check sources and recognise advertising see better critical thinking. Parents who discuss online experiences calmly often guide more effectively than strict bans alone.",
            "Social media is a tool. Like any tool, it can help or harm depending on how carefully people use it.",
        ),
        [
            q(1, "What positive uses of social media are mentioned?", ["Learning skills, education channels and study groups", "Only spreading false news", "Only breaking concentration", "Only increasing anxiety"], 0),
            q(2, "What can constant notifications do?", ["Break concentration", "Improve deep sleep automatically", "Remove all anxiety", "Make every post true"], 0),
            q(3, "Why may anxiety increase?", ["Comparing perfect images with real life", "Turning off alerts", "Checking sources", "Calm family talks"], 0),
            q(4, "What limit is suggested before sleep?", ["Avoid screens one hour before sleep", "Use screens all night", "Share every post", "Ignore homework alerts only by posting more"], 0),
            q(5, "What should people ask before sharing?", ["Whether a post is helpful", "Whether it will get maximum anger", "Whether nobody checks it", "Whether it is the longest"], 0),
            q(6, "What do schools teach for better thinking?", ["How to check sources and recognise advertising", "How to ban all books", "How to avoid all friends", "How to believe every post"], 0),
            q(7, "What parental approach is described as effective?", ["Discussing experiences calmly", "Only strict bans with no talk", "Ignoring online life", "Deleting schools"], 0),
            q(8, "How does the text describe social media?", ["As a tool that can help or harm", "As always safe", "As always harmful", "As unnecessary for learning"], 0),
            q(9, "What should students turn off during homework?", ["Non-essential alerts", "All education channels", "All study groups", "All clocks"], 0),
            q(10, "What is the best title?", ["Social Media", "Lost Keys", "Bike Repair", "Silent Movies"], 0),
        ],
    )
)

B1.append(
    pack(
        "B1",
        10,
        "Second Languages",
        p(
            "Learning a second language opens doors to study, travel and work. It also trains the brain to notice patterns and switch between different ways of expressing ideas.",
            "Many learners focus only on grammar rules and forget real communication. Short daily conversations, even five minutes with a partner, often build fluency faster than long silent textbook weeks.",
            "Mistakes are part of progress. Students who fear errors may stay quiet and practise less. Supportive classrooms treat mistakes as information, not as failure.",
            "Technology offers podcasts, language apps and online tutors. Still, human interaction remains powerful because people adapt speed, explain meaning and encourage speakers.",
            "A second language is a long journey. Consistency matters more than talent. Learners who practise a little every day usually go further than those who study intensively once a month.",
        ),
        [
            q(1, "What opportunities can a second language open?", ["Study, travel and work", "Only silent reading forever", "Only grammar tests without speaking", "No real-world use"], 0),
            q(2, "What do many learners forget when focusing only on grammar?", ["Real communication", "All vocabulary forever", "How to write numbers", "School timetables"], 0),
            q(3, "What often builds fluency faster?", ["Short daily conversations", "Long silent textbook weeks only", "Avoiding partners", "Studying once a month only"], 0),
            q(4, "How should supportive classrooms treat mistakes?", ["As information, not failure", "As a reason to stay quiet forever", "As proof of no talent", "As unimportant"], 0),
            q(5, "What technology tools are mentioned?", ["Podcasts, apps and online tutors", "Only paper dictionaries from 1800", "Only classroom chalk", "No technology"], 0),
            q(6, "Why is human interaction powerful?", ["People adapt speed, explain and encourage", "Humans never make mistakes", "Apps cannot exist", "Textbooks talk back"], 0),
            q(7, "What matters more than talent?", ["Consistency", "Studying once a month", "Fear of errors", "Avoiding practice"], 0),
            q(8, "Who usually progresses further?", ["Learners who practise a little every day", "Those who study intensively once a month only", "Those who never speak", "Those who fear all mistakes and stop"], 0),
            q(9, "What brain benefit is mentioned?", ["Noticing patterns and switching expression styles", "Forgetting the first language automatically", "Sleeping less", "Avoiding travel"], 0),
            q(10, "What is the best title?", ["Second Languages", "Lost Keys", "Airport Delay", "Silent Movies"], 0),
        ],
    )
)

B1.append(
    pack(
        "B1",
        11,
        "Food Delivery",
        p(
            "Food delivery apps have grown quickly in cities. With a few clicks, customers can order meals from many restaurants and track the rider on a map.",
            "For busy students and office workers, delivery saves time after long days. Restaurants can reach customers who rarely eat out. During bad weather, demand often rises.",
            "There are downsides. Packaging waste increases, and frequent orders can become expensive. Some riders face pressure to deliver quickly in heavy traffic, which raises safety concerns.",
            "A balanced approach is possible: use delivery occasionally, choose restaurants with less packaging, and tip fairly when service is good. Cooking at home a few nights a week still matters for health and budget.",
            "Delivery is convenient, but it should not replace all shared meals. Sitting at a table with family or friends remains a valuable social habit.",
        ),
        [
            q(1, "What can customers do with delivery apps?", ["Order meals and track riders", "Drive the restaurant kitchen", "Remove all packaging forever", "Stop all traffic"], 0),
            q(2, "Who finds delivery especially useful?", ["Busy students and office workers", "Only professional chefs", "Only people who never eat", "Only airport staff abroad"], 0),
            q(3, "When does demand often rise?", ["During bad weather", "Only on sunny holidays abroad", "When restaurants close forever", "When apps disappear"], 0),
            q(4, "What downside is mentioned about packaging?", ["Waste increases", "Waste disappears", "Packaging is always reusable glass", "There is no packaging"], 0),
            q(5, "Why are riders’ conditions a concern?", ["Pressure to deliver quickly in traffic", "They never work", "They earn unlimited free time", "Roads are empty always"], 0),
            q(6, "What balanced advice is given?", ["Use delivery occasionally and cook at home some nights", "Order every meal forever", "Never tip", "Avoid all restaurants online and offline"], 0),
            q(7, "What social habit remains valuable?", ["Shared meals at a table", "Eating alone while walking in traffic", "Never eating with others", "Only ordering at midnight"], 0),
            q(8, "How can restaurants benefit?", ["They reach customers who rarely eat out", "They must close kitchens", "They lose all orders", "They stop cooking"], 0),
            q(9, "What can frequent orders do to budgets?", ["Become expensive", "Always save money automatically", "Remove all costs", "Pay the customer"], 0),
            q(10, "What is the best title?", ["Food Delivery", "Lost Keys", "Museum Visit", "Silent Movies"], 0),
        ],
    )
)

B1.append(
    pack(
        "B1",
        12,
        "Community Garden",
        p(
            "Community gardens turn empty city spaces into green shared projects. Neighbours grow vegetables, herbs and flowers together and learn from one another’s experience.",
            "These gardens improve local air quality and offer quiet places to relax. Children who help plant seeds often understand food production better than classmates who only see supermarket shelves.",
            "Organisation is important. Clear schedules for watering, shared tool storage and simple rules about harvesting prevent arguments. Some gardens also hold monthly meetings to plan seasonal work.",
            "Challenges include theft, dry summers and unequal participation. Successful groups solve problems early and welcome new volunteers without making the work feel exclusive.",
            "A community garden is small compared with a farm, yet its social value can be large. People who dig soil side by side often build trust that spreads beyond the garden fence.",
        ),
        [
            q(1, "What do community gardens use?", ["Empty city spaces", "Only private farms far away", "Airport runways", "School exam halls"], 0),
            q(2, "What do neighbours grow together?", ["Vegetables, herbs and flowers", "Only plastic plants", "Cars", "Nothing"], 0),
            q(3, "What benefit for children is mentioned?", ["Better understanding of food production", "Less interest in nature", "Only supermarket knowledge", "Avoiding all planting"], 0),
            q(4, "What organisation details prevent arguments?", ["Watering schedules, tool storage and harvesting rules", "No meetings ever", "Secret tool hiding", "No schedules"], 0),
            q(5, "What challenges are listed?", ["Theft, dry summers and unequal participation", "Too much rain every day forever", "No volunteers needed", "Unlimited free workers"], 0),
            q(6, "How do successful groups act?", ["Solve problems early and welcome volunteers", "Make work exclusive", "Ignore new people", "Close after one week"], 0),
            q(7, "What social value can gardens create?", ["Trust beyond the garden fence", "Only competition and anger", "Less neighbour contact", "Closed communities with no talk"], 0),
            q(8, "What environmental benefit is mentioned?", ["Improved local air quality", "More traffic pollution", "Less green space", "No quiet places"], 0),
            q(9, "How often may some gardens meet to plan?", ["Monthly", "Once in ten years", "Every hour", "Never"], 0),
            q(10, "What is the best title?", ["Community Garden", "Bank Fraud", "Airport Delay", "Silent Movies"], 0),
        ],
    )
)

B1.append(
    pack(
        "B1",
        13,
        "Exam Stress",
        p(
            "Exam periods can create heavy pressure for students. Long study hours, fear of disappointing family and comparison with classmates often combine into stress that affects sleep and appetite.",
            "Some stress can motivate careful preparation. Too much stress, however, reduces memory and makes simple mistakes more likely. Students may reread pages without understanding them.",
            "Helpful strategies include breaking revision into short sessions, practising past papers under timed conditions and asking teachers early about unclear topics. Exercise and short breaks protect concentration.",
            "Parents help most when they offer calm support instead of constant reminders about rankings. Friends can form study groups that share notes without turning into silent competition.",
            "Exams measure performance on a day, not a person’s whole value. Remembering that perspective can make the process more manageable.",
        ),
        [
            q(1, "What can create heavy pressure in exam periods?", ["Long study, fear of disappointing family and comparison", "Only short breaks", "Only exercise", "Calm support"], 0),
            q(2, "What can too much stress reduce?", ["Memory", "All mistakes forever", "The need for sleep", "Teacher questions"], 0),
            q(3, "What unhelpful study behaviour is described?", ["Rereading without understanding", "Practising past papers", "Asking teachers early", "Taking short breaks"], 0),
            q(4, "Which revision strategy is recommended?", ["Short sessions and timed past papers", "Studying only the night before with no breaks", "Avoiding teachers", "Comparing rankings all day"], 0),
            q(5, "How do parents help most?", ["Calm support instead of constant ranking reminders", "More pressure about rankings", "Ignoring students completely", "Cancelling all exams"], 0),
            q(6, "How can friends help?", ["Study groups that share notes without silent competition", "Only competing silently", "Hiding all notes", "Increasing fear"], 0),
            q(7, "What do exams measure, according to the text?", ["Performance on a day, not a person’s whole value", "A person’s whole value forever", "Only family income", "Only sports ability"], 0),
            q(8, "What protects concentration?", ["Exercise and short breaks", "No sleep", "Nonstop comparison", "Skipping meals always"], 0),
            q(9, "When should students ask about unclear topics?", ["Early", "Only after the exam", "Never", "Only if friends forbid it"], 0),
            q(10, "What is the best title?", ["Exam Stress", "Lost Keys", "Surprise Party", "Silent Movies"], 0),
        ],
    )
)

B1.append(
    pack(
        "B1",
        14,
        "Recycling Drive",
        p(
            "Last autumn our neighbourhood organised a recycling drive in the central square. Volunteers set up coloured containers for paper, plastic, glass and metal, and explained what could not be recycled.",
            "In one afternoon, residents brought old magazines, bottles and tin cans. A local company provided a truck and weighed each category. Paper was the largest amount by weight.",
            "Children designed posters with slogans about reducing waste. A short talk explained how contaminated items — for example, dirty pizza boxes — can spoil a whole recycling load.",
            "Some people admitted they had thrown recyclable materials into general rubbish before because rules felt confusing. Clear signs and friendly volunteers helped change that habit.",
            "The drive collected useful materials, but its bigger success was education. When people understand why sorting matters, everyday behaviour starts to change.",
        ),
        [
            q(1, "Where was the recycling drive?", ["In the central square", "At the airport", "In a closed factory only", "Online only"], 0),
            q(2, "Which materials had separate containers?", ["Paper, plastic, glass and metal", "Only food waste", "Only clothes", "Only electronics"], 0),
            q(3, "What was the largest amount by weight?", ["Paper", "Glass", "Metal only", "Plastic only"], 0),
            q(4, "Who provided a truck?", ["A local company", "The children alone", "An airline", "Nobody"], 0),
            q(5, "What example of contamination is given?", ["Dirty pizza boxes", "Clean glass bottles", "Dry newspapers", "Empty metal cans"], 0),
            q(6, "Why had some people used general rubbish before?", ["Rules felt confusing", "They hated paper", "There were no materials", "Volunteers banned recycling"], 0),
            q(7, "What helped change habits?", ["Clear signs and friendly volunteers", "Hidden containers", "No explanations", "Confusing rules only"], 0),
            q(8, "What was the bigger success than collection?", ["Education", "Weighing the truck only", "Designing one poster", "Closing the square"], 0),
            q(9, "What did children design?", ["Posters with slogans", "The truck engine", "New laws alone", "Pizza boxes"], 0),
            q(10, "What is the best title?", ["Recycling Drive", "Lost Keys", "Surprise Party", "Silent Movies"], 0),
        ],
    )
)

B1.append(
    pack(
        "B1",
        15,
        "Weekend Markets",
        p(
            "Weekend markets bring energy to quiet streets. Early in the morning, sellers arrange fruit, handmade crafts and second-hand books while musicians prepare small performances.",
            "Visitors enjoy the atmosphere as much as the products. Walking between stalls, people meet neighbours they rarely see during busy weekdays. Tourists also discover local specialities that shops may not display.",
            "Organisers must manage space carefully. Crowded aisles can be unsafe for children and older visitors. Waste bins and toilets need to be easy to find.",
            "Weather always affects attendance. Sudden rain can empty outdoor markets within minutes, so temporary covers and flexible stall plans help.",
            "When weekend markets are well organised, they support small makers and create a sense of place. A city feels more human when people gather face to face.",
        ),
        [
            q(1, "What do weekend markets bring to quiet streets?", ["Energy", "Silence only", "Closed shops forever", "No visitors"], 0),
            q(2, "What products are mentioned?", ["Fruit, handmade crafts and second-hand books", "Only airline tickets", "Only cars", "Only computers"], 0),
            q(3, "What do visitors enjoy besides products?", ["The atmosphere and meeting neighbours", "Only online chats", "Empty aisles", "No music"], 0),
            q(4, "What must organisers manage carefully?", ["Space, safety, bins and toilets", "Only music volume to maximum", "Removing all stalls", "Hiding tourists"], 0),
            q(5, "What can sudden rain do?", ["Empty outdoor markets quickly", "Increase sales forever", "Stop all weather forever", "Close indoor shops only"], 0),
            q(6, "What helps with bad weather?", ["Temporary covers and flexible plans", "No covers", "Ignoring rain", "Removing bins"], 0),
            q(7, "Who do well-organised markets support?", ["Small makers", "Only giant factories abroad", "Nobody", "Only online sellers far away"], 0),
            q(8, "What sense can markets create?", ["A sense of place", "A sense of isolation only", "Fear of neighbours", "No human contact"], 0),
            q(9, "When do sellers arrive to arrange goods?", ["Early in the morning", "After midnight only", "Late at night after closing", "Never"], 0),
            q(10, "What is the best title?", ["Weekend Markets", "Exam Stress", "Bank Fraud", "Silent Movies"], 0),
        ],
    )
)

B1.append(
    pack(
        "B1",
        16,
        "Bike Lanes",
        p(
            "Cities that build protected bike lanes often see more people cycling to work and school. Separation from fast cars makes riders feel safer, especially beginners and parents with children.",
            "Bike lanes can also free road space if some short car trips are replaced by cycling. Cleaner air and less noise benefit residents who live near busy avenues.",
            "Opponents argue that lanes reduce parking and may slow cars during peak hours. Shop owners sometimes fear fewer customers arriving by vehicle.",
            "Evidence from several cities shows that careful design matters. Continuous lanes, clear signals and bike parking near shops encourage use. Incomplete lanes that suddenly end can create danger.",
            "Transport planning works best when drivers, cyclists and pedestrians are considered together. The aim is safer streets for everyone, not victory for one group.",
        ),
        [
            q(1, "What often increases when protected bike lanes are built?", ["People cycling to work and school", "Only car racing", "Parking only", "Noise always"], 0),
            q(2, "Who especially feels safer with separation from cars?", ["Beginners and parents with children", "Only professional racers", "Only truck drivers", "Nobody"], 0),
            q(3, "What environmental benefits are mentioned?", ["Cleaner air and less noise", "More pollution", "Louder avenues", "No change"], 0),
            q(4, "What do opponents argue?", ["Less parking and slower cars in peak hours", "More parking automatically", "No effect on traffic", "Bikes become illegal"], 0),
            q(5, "What do some shop owners fear?", ["Fewer customers by vehicle", "Too many bike customers", "Free parking forever", "No streets left"], 0),
            q(6, "What design features encourage cycling?", ["Continuous lanes, clear signals and bike parking", "Lanes that suddenly end", "No signals", "Hidden parking far away"], 0),
            q(7, "Why are incomplete lanes a problem?", ["They can create danger", "They are always safer", "They increase parking", "They remove all cars kindly"], 0),
            q(8, "What is the planning aim?", ["Safer streets for everyone", "Victory for one group only", "Removing all pedestrians", "Banning all bikes"], 0),
            q(9, "Who should be considered together?", ["Drivers, cyclists and pedestrians", "Only drivers", "Only cyclists", "Only shop owners abroad"], 0),
            q(10, "What is the best title?", ["Bike Lanes", "Lost Keys", "Surprise Party", "Silent Movies"], 0),
        ],
    )
)

B1.append(
    pack(
        "B1",
        17,
        "Library Changes",
        p(
            "Modern libraries are changing from silent book warehouses into active learning centres. Visitors still borrow novels and study guides, but they also use free Wi-Fi, join workshops and reserve study rooms.",
            "Digital catalogues help readers find titles quickly. E-book loans are useful for people who travel or prefer reading on a tablet. Librarians now teach information skills as well as recommending books.",
            "Not everyone welcomes the change. Some readers miss complete silence and worry that group events create noise. Libraries try to solve this by creating quiet zones and separate activity areas.",
            "Budget cuts remain a threat. When opening hours are reduced, students who need evening study space suffer most. Community campaigns sometimes protect libraries by showing how many people rely on them.",
            "A strong library is both a collection and a public service. Keeping that balance is the key challenge of the next decade.",
        ),
        [
            q(1, "How are modern libraries described?", ["As active learning centres", "As closed warehouses only", "As private clubs", "As online shops only"], 0),
            q(2, "What extra services are mentioned?", ["Wi-Fi, workshops and study rooms", "Only selling cars", "Only loud concerts all day", "No books at all"], 0),
            q(3, "Who benefits from e-book loans?", ["People who travel or prefer tablets", "Only people without devices", "Only children under five", "Nobody"], 0),
            q(4, "What new role do librarians have?", ["Teaching information skills", "Ignoring readers", "Closing catalogues", "Banning Wi-Fi"], 0),
            q(5, "What do some readers miss?", ["Complete silence", "More group noise", "Fewer books", "No study rooms"], 0),
            q(6, "How do libraries reduce noise conflict?", ["Quiet zones and separate activity areas", "Removing all events and Wi-Fi forever", "One shared loud room only", "Closing evenings"], 0),
            q(7, "Who suffers most when evening hours are cut?", ["Students needing evening study space", "People who never visit", "Online shoppers only", "Tourists at airports"], 0),
            q(8, "How can communities protect libraries?", ["Campaigns showing how many people rely on them", "Ignoring budget cuts", "Reducing visitors", "Hiding opening hours"], 0),
            q(9, "What balance is the key challenge?", ["Collection and public service", "Only digital with no books", "Only silence with no people", "Only events with no reading"], 0),
            q(10, "What is the best title?", ["Library Changes", "Lost Keys", "Surprise Party", "Silent Movies"], 0),
        ],
    )
)

B1.append(
    pack(
        "B1",
        18,
        "Tourist Boom",
        p(
            "A sudden tourist boom can bring money and jobs to a historic town. Hotels fill up, restaurants hire staff and craft sellers find more customers for handmade goods.",
            "Yet rapid growth also creates pressure. Narrow streets become crowded, housing rents rise, and local people may feel pushed out of their own centre. Waste and water systems struggle when visitor numbers jump too quickly.",
            "City planners recommend limits on short-term apartment rentals and better public transport to popular sites. Guided visits at different times of day can reduce peak overcrowding.",
            "Tourists also have responsibility: respect local rules, support small businesses and avoid damaging monuments for photos. Sustainable tourism protects the place that visitors come to enjoy.",
            "The goal is balance. A town should welcome guests without losing the daily life that makes it authentic.",
        ),
        [
            q(1, "What positive effects can a tourist boom bring?", ["Money, jobs and more customers for crafts", "Only empty hotels", "Lower rents always", "Less restaurant work"], 0),
            q(2, "What housing problem can appear?", ["Rents rise", "Rents disappear", "Free homes for all tourists", "No housing pressure"], 0),
            q(3, "What systems may struggle?", ["Waste and water systems", "Only airline systems abroad", "Only school exams", "Nothing"], 0),
            q(4, "What do planners recommend for rentals?", ["Limits on short-term apartment rentals", "Unlimited rentals with no rules", "Closing all hotels", "Banning all guests"], 0),
            q(5, "How can overcrowding at sites be reduced?", ["Guided visits at different times", "Sending all tourists at noon only", "Closing transport", "Damaging monuments"], 0),
            q(6, "What responsibility do tourists have?", ["Respect rules and support small businesses", "Ignore local life", "Damage monuments for photos", "Avoid all small shops"], 0),
            q(7, "What does sustainable tourism protect?", ["The place visitors come to enjoy", "Only airline profits", "Only photo opportunities", "Nothing local"], 0),
            q(8, "What is the goal?", ["Welcome guests without losing authentic daily life", "Replace residents completely", "Stop all tourism forever", "Maximise crowds only"], 0),
            q(9, "What happens to narrow streets?", ["They become crowded", "They become wider automatically", "They close to residents only forever", "They empty completely"], 0),
            q(10, "What is the best title?", ["Tourist Boom", "Lost Keys", "Bike Repair", "Silent Movies"], 0),
        ],
    )
)

B1.append(
    pack(
        "B1",
        19,
        "Online Learning",
        p(
            "Online learning expanded rapidly when schools needed flexible options. Students can watch recorded lessons, submit homework digitally and join live discussions from home.",
            "Advantages include saving travel time and reviewing difficult explanations more than once. Learners in remote areas can access courses that local schools do not offer.",
            "Disadvantages are real. Screen fatigue, weak internet and limited face-to-face support can reduce motivation. Practical subjects such as laboratory science or music performance are harder online.",
            "Effective online courses use clear weekly goals, short videos and regular feedback. Teachers who check progress early prevent small problems from becoming failure.",
            "The future is likely hybrid: online tools for flexibility and classroom time for discussion, experiments and social learning. Technology should support teachers, not replace them.",
        ),
        [
            q(1, "What can students do in online learning?", ["Watch lessons, submit homework and join discussions", "Only travel longer to school", "Avoid all feedback", "Delete courses"], 0),
            q(2, "What advantage is mentioned for difficult explanations?", ["Reviewing them more than once", "Never reviewing", "Only one live chance ever", "No recordings"], 0),
            q(3, "Who can access extra courses online?", ["Learners in remote areas", "Only city centre students with no internet", "Only teachers abroad", "Nobody"], 0),
            q(4, "What disadvantages are listed?", ["Screen fatigue, weak internet and less face-to-face support", "Too much laboratory time", "Too many social activities", "No screens at all"], 0),
            q(5, "Which subjects are harder online?", ["Laboratory science or music performance", "Only history reading", "Only recorded grammar", "All subjects equally easy"], 0),
            q(6, "What makes online courses effective?", ["Clear goals, short videos and regular feedback", "Long unclear videos with no goals", "No teacher checks", "Late feedback only after failure"], 0),
            q(7, "What future model is likely?", ["Hybrid online and classroom learning", "Only online forever", "Only classroom with no tools", "No teachers"], 0),
            q(8, "What should technology do?", ["Support teachers, not replace them", "Replace all teachers", "Remove classroom discussion", "Stop experiments"], 0),
            q(9, "What travel-related advantage is mentioned?", ["Saving travel time", "Longer commuting", "More bus delays", "No home study"], 0),
            q(10, "What is the best title?", ["Online Learning", "Lost Keys", "Surprise Party", "Silent Movies"], 0),
        ],
    )
)

B1.append(
    pack(
        "B1",
        20,
        "Neighbour Disputes",
        p(
            "Living close to other people can create small conflicts that grow if nobody talks calmly. Common disputes include loud music at night, parking in shared spaces and rubbish left in corridors.",
            "Many problems start from misunderstanding rather than bad intentions. A neighbour who works night shifts may sleep during the day and feel disturbed by afternoon renovations.",
            "Useful first steps are polite conversation and clear examples instead of angry messages. Written building rules help when emotions are high. In serious cases, a building manager or local mediation service can assist.",
            "Good neighbour relationships are built daily: greeting people, sharing information about repairs and respecting quiet hours. Prevention is easier than formal complaints.",
            "A peaceful building does not require friendship with everyone. It requires basic respect, communication and a willingness to find practical compromises.",
        ),
        [
            q(1, "What common disputes are mentioned?", ["Loud music, parking and corridor rubbish", "Only garden flowers", "Only school grades", "Airline delays"], 0),
            q(2, "How do many problems start?", ["From misunderstanding rather than bad intentions", "Always from planned harm", "From friendship only", "From no neighbours existing"], 0),
            q(3, "Why might afternoon renovations cause conflict?", ["A night-shift neighbour may be sleeping", "Nobody sleeps by day ever", "Renovations are silent", "Rules ban all talk"], 0),
            q(4, "What first steps are useful?", ["Polite conversation and clear examples", "Only angry messages", "Immediate formal war", "Ignoring everyone forever"], 0),
            q(5, "What helps when emotions are high?", ["Written building rules", "Louder music", "More corridor rubbish", "No manager contact"], 0),
            q(6, "Who can assist in serious cases?", ["A building manager or mediation service", "Only social media strangers", "Nobody", "Only tourists"], 0),
            q(7, "How are good neighbour relationships built?", ["Daily respect, greetings and quiet hours", "Formal complaints first always", "Never speaking", "Avoiding all rules"], 0),
            q(8, "What is easier than formal complaints?", ["Prevention", "Escalation", "Night parties", "Corridor waste"], 0),
            q(9, "What does a peaceful building require?", ["Respect, communication and compromise", "Friendship with everyone mandatory", "No communication", "Victory in every argument"], 0),
            q(10, "What is the best title?", ["Neighbour Disputes", "Lost Keys", "Surprise Party", "Silent Movies"], 0),
        ],
    )
)

assert len(B1) == 20
