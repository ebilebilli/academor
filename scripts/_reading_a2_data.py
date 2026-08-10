# -*- coding: utf-8 -*-
"""A2 reading tests — stronger passages (~160–200 words) + real questions."""
from __future__ import annotations

from _reading_a1_data import p, q, pack

A2 = []

A2.append(
    pack(
        "A2",
        1,
        "Lost Keys",
        p(
            "Yesterday evening Anna left work at six o’clock and walked to the station. She was tired because she had a long day at the office. Near the entrance she put her bag on a bench for a moment to find her phone.",
            "When the train arrived, she quickly picked up her bag and got on. Ten minutes later she wanted to open her flat door, but her keys were not in the bag. She felt worried and checked every pocket twice.",
            "Anna called her brother from the station cafe. He told her to go back and look carefully. After twenty minutes she found the keys under the same bench, next to an empty coffee cup.",
            "Now Anna has a new habit. Before she leaves any place, she checks her pockets and counts her keys. She also keeps a spare key at her brother’s house.",
            "She laughed about the story later, but she does not want to lose her keys again. Small mistakes can waste a lot of time.",
        ),
        [
            q(1, "Why was Anna tired?", ["She ran a marathon", "She had a long day at the office", "She slept too much", "She missed breakfast only"], 1),
            q(2, "Where did she put her bag for a moment?", ["On a bench near the station entrance", "On the train roof", "In a taxi", "At her office desk"], 0),
            q(3, "When did she notice the keys were missing?", ["On the train immediately", "When she wanted to open her flat door", "The next morning", "At work"], 1),
            q(4, "Who did she call?", ["Her brother", "Her boss", "The police", "A stranger"], 0),
            q(5, "Where did she find the keys?", ["Under the same bench", "In the train toilet", "At the office", "In her shoe"], 0),
            q(6, "What was next to the keys?", ["An empty coffee cup", "A suitcase", "A dog", "A ticket machine"], 0),
            q(7, "What new habit does Anna have?", ["She checks her pockets and counts her keys", "She never leaves home", "She buys a new phone daily", "She sleeps at the station"], 0),
            q(8, "Where is her spare key?", ["At her brother’s house", "At the cafe", "Under the bench forever", "At school"], 0),
            q(9, "How did she feel when the keys were missing?", ["Worried", "Excited", "Bored", "Angry at football"], 0),
            q(10, "What is the best title?", ["Lost Keys", "Space News", "Bank Fraud", "Silent Movies"], 0),
        ],
    )
)

A2.append(
    pack(
        "A2",
        2,
        "New Neighbour",
        p(
            "Last month a new family moved into the flat next to ours. Their name is the Hasanovs. There are three people: Mr. Hasanov, his wife and their daughter Nilay, who is fourteen.",
            "On the first day they carried many boxes up the stairs. My father helped them with a heavy table. In the evening Mrs. Hasanov brought us homemade baklava to say thank you.",
            "Nilay goes to the same school as me, but she is in a different class. We sometimes walk home together and talk about music and homework. She likes drawing and she wants to study design later.",
            "The Hasanovs are quiet neighbours. They do not play loud music at night. On Sundays they clean the shared stairs with us.",
            "I am happy they live next door. A good neighbour can make a building feel like a friendly place.",
        ),
        [
            q(1, "When did the new family move in?", ["Last month", "Last year", "Yesterday only", "Ten years ago"], 0),
            q(2, "How many people are in the Hasanov family?", ["Two", "Three", "Four", "Five"], 1),
            q(3, "How old is Nilay?", ["Twelve", "Fourteen", "Sixteen", "Eighteen"], 1),
            q(4, "How did the writer’s father help?", ["He carried a heavy table", "He painted the flat", "He cooked dinner", "He drove a truck abroad"], 0),
            q(5, "What did Mrs. Hasanov bring?", ["Homemade baklava", "A new TV", "School books", "Loud speakers"], 0),
            q(6, "Do Nilay and the writer go to the same school?", ["Yes", "No", "Only on Fridays", "They study online only"], 0),
            q(7, "What does Nilay like?", ["Drawing", "Loud night music", "Driving trucks", "Banking"], 0),
            q(8, "What do they do on Sundays?", ["Clean the shared stairs", "Have noisy parties", "Travel to space", "Close the building"], 0),
            q(9, "How are the Hasanovs as neighbours?", ["Quiet", "Very noisy every night", "Never at home", "Always angry"], 0),
            q(10, "What is the best title?", ["New Neighbour", "Airport Delay", "Bank Fraud", "Space News"], 0),
        ],
    )
)

A2.append(
    pack(
        "A2",
        3,
        "Market Day",
        p(
            "Every Sunday my grandmother and I go to the open market in our town. We leave home at eight o’clock because the best fruit arrives early.",
            "The market is full of colours and smells. Farmers sell tomatoes, cucumbers, grapes and fresh bread. There is also a corner with cheese and honey.",
            "Last Sunday we bought two kilos of tomatoes, a jar of honey and a round loaf of bread. My grandmother talked to a seller she has known for many years. He gave us a small bag of grapes for free.",
            "I help carry the bags and I practise asking prices in English with tourist sellers. Sometimes I feel shy, but it is good practice.",
            "After the market we drink tea at home and wash the vegetables. Market day is tiring, but it is also one of my favourite weekend activities.",
        ),
        [
            q(1, "When do they go to the market?", ["Every Sunday", "Every night", "Only in winter", "Once a year"], 0),
            q(2, "What time do they leave home?", ["At eight o’clock", "At noon", "At six in the evening", "At midnight"], 0),
            q(3, "Why do they go early?", ["The best fruit arrives early", "The market closes at 7 a.m.", "They hate mornings", "Buses stop forever"], 0),
            q(4, "What did they buy last Sunday?", ["Tomatoes, honey and bread", "Only meat", "Clothes only", "A bicycle"], 0),
            q(5, "What did the seller give for free?", ["A small bag of grapes", "A car", "A phone", "Nothing"], 0),
            q(6, "How does the writer help?", ["By carrying the bags", "By driving the bus", "By selling cheese", "By closing the market"], 0),
            q(7, "What language does the writer practise?", ["English", "Only silence", "Computer code", "Latin only"], 0),
            q(8, "What do they do after the market?", ["Drink tea and wash vegetables", "Go straight to sleep without tea", "Fly abroad", "Sell the bags again"], 0),
            q(9, "How does the writer feel about market day?", ["Tired but it is a favourite activity", "Bored and angry", "Afraid of fruit", "Uninterested"], 0),
            q(10, "What is the best title?", ["Market Day", "Space News", "Bank Fraud", "Silent Movies"], 0),
        ],
    )
)

A2.append(
    pack(
        "A2",
        4,
        "First Job",
        p(
            "This summer I started my first job at a small bookshop in the city centre. I work three days a week from ten in the morning until three in the afternoon.",
            "My main tasks are putting books on the shelves, helping customers find titles and working at the cash desk. The manager, Ms. Gunel, taught me how to use the computer for sales.",
            "On my first day I felt nervous and I made a mistake with a customer’s change. Ms. Gunel stayed calm and showed me again. After that I was more careful.",
            "I like the job because I can read new books during quiet hours. I also meet people from different countries who visit the shop.",
            "The pay is not very high, but I am learning useful skills. Next year I want to work more hours during the school holidays.",
        ),
        [
            q(1, "Where does the writer work?", ["At a small bookshop", "At a bank", "At a hospital", "At an airport"], 0),
            q(2, "How many days a week does the writer work?", ["Two", "Three", "Five", "Seven"], 1),
            q(3, "What are the working hours?", ["10 a.m. to 3 p.m.", "9 a.m. to 9 p.m.", "Only at night", "Midnight to sunrise"], 0),
            q(4, "Who is the manager?", ["Ms. Gunel", "Mr. Ali", "Mrs. Sevinc", "Dr. Rashad"], 0),
            q(5, "What mistake happened on the first day?", ["Wrong change for a customer", "The shop burned", "All books were lost", "The computer exploded"], 0),
            q(6, "How did the manager react?", ["She stayed calm and showed again", "She shouted and closed the shop", "She fired the writer immediately", "She laughed and left"], 0),
            q(7, "Why does the writer like the job?", ["Can read books and meet people", "The pay is extremely high", "There is no work to do", "The shop is always empty forever"], 0),
            q(8, "Is the pay very high?", ["No", "Yes, very high", "There is no pay", "Only food is paid"], 0),
            q(9, "What does the writer want next year?", ["To work more hours in the holidays", "To leave school forever", "To buy the airport", "To stop learning skills"], 0),
            q(10, "What is the best title?", ["First Job", "Space News", "Silent Movies", "Bank Fraud"], 0),
        ],
    )
)

A2.append(
    pack(
        "A2",
        5,
        "Train Trip",
        p(
            "Last weekend my cousin and I took a train from Baku to Gabala. We bought tickets online the night before and arrived at the station early.",
            "The train left at nine o’clock. We found seats by the window and watched the countryside change from city buildings to green hills. A ticket inspector checked our tickets after thirty minutes.",
            "We shared sandwiches and tea from a thermos. An old woman opposite us told stories about Gabala in the past. The journey lasted about four hours.",
            "When we arrived, it was raining lightly. We took a short taxi ride to our aunt’s house. She cooked a big dinner and we felt welcome.",
            "On Sunday evening we returned by train again. I slept most of the way home. It was a simple trip, but I enjoyed every part of it.",
        ),
        [
            q(1, "Where did they travel?", ["From Baku to Gabala", "From Gabala to London", "Only inside one station", "From Baku to the airport only"], 0),
            q(2, "How did they buy tickets?", ["Online the night before", "On the train without tickets", "From a friend for free", "They did not need tickets"], 0),
            q(3, "What time did the train leave?", ["At nine o’clock", "At noon", "At midnight", "At five in the evening"], 0),
            q(4, "Who checked the tickets?", ["A ticket inspector", "The aunt", "A taxi driver", "Nobody"], 0),
            q(5, "How long was the journey?", ["About four hours", "Twenty minutes", "One day", "Ten hours"], 0),
            q(6, "What was the weather like on arrival?", ["Light rain", "Heavy snow", "Very hot and dry", "A sandstorm"], 0),
            q(7, "How did they get to their aunt’s house?", ["By short taxi ride", "By plane", "By walking for five hours", "By boat"], 0),
            q(8, "What did the aunt do?", ["Cooked a big dinner", "Closed the door", "Left town", "Sold the house"], 0),
            q(9, "What did the writer do on the return trip?", ["Slept most of the way", "Drove the train", "Walked home", "Stayed in Gabala forever"], 0),
            q(10, "What is the best title?", ["Train Trip", "Bank Fraud", "Silent Movies", "Space News"], 0),
        ],
    )
)

A2.append(
    pack(
        "A2",
        6,
        "Cooking Class",
        p(
            "Every Wednesday evening I join a cooking class at the community centre. There are twelve students in the group and our teacher is Chef Nigar.",
            "In the first weeks we learned how to make simple salads and soups. Last week we cooked chicken with rice and a tomato sauce. Everyone worked in pairs.",
            "My partner was a student from Italy called Marco. He cut the vegetables while I prepared the sauce. We laughed when I added too much salt, but Chef Nigar helped us fix it.",
            "At the end of each class we sit together and taste the food. We also clean the kitchen before we leave. The class finishes at eight o’clock.",
            "I used to eat only fast food, but now I cook at home twice a week. The class has changed my habits in a good way.",
        ),
        [
            q(1, "When is the cooking class?", ["Every Wednesday evening", "Every Monday morning", "Only in summer", "Once a year"], 0),
            q(2, "How many students are in the group?", ["Eight", "Ten", "Twelve", "Twenty"], 2),
            q(3, "Who is the teacher?", ["Chef Nigar", "Chef Marco", "Ms. Gunel", "Mr. Rashad"], 0),
            q(4, "What did they cook last week?", ["Chicken with rice and tomato sauce", "Only pizza", "Only cake", "Burgers"], 0),
            q(5, "Who was the writer’s partner?", ["Marco", "Nigar", "Anna", "Elvin"], 0),
            q(6, "What mistake did the writer make?", ["Added too much salt", "Burned the kitchen", "Forgot to come", "Broke all the plates"], 0),
            q(7, "What do they do at the end of class?", ["Taste the food and clean", "Leave without cleaning", "Sell the food outside", "Sleep in the kitchen"], 0),
            q(8, "What time does the class finish?", ["At eight o’clock", "At noon", "At midnight", "At six in the morning"], 0),
            q(9, "How often does the writer cook at home now?", ["Twice a week", "Never", "Every hour", "Only once a year"], 0),
            q(10, "What is the best title?", ["Cooking Class", "Space News", "Bank Fraud", "Silent Movies"], 0),
        ],
    )
)

A2.append(
    pack(
        "A2",
        7,
        "Phone Call",
        p(
            "On Monday night my phone rang while I was doing homework. It was my uncle calling from Canada. I had not spoken to him for two months.",
            "He asked about school and my football team. Then he told me he might visit Azerbaijan in August. He wants to see our family and take a trip to the mountains.",
            "We talked for almost forty minutes. The connection was clear at first, but later there was some noise. I moved near the window and the sound became better.",
            "Before we finished, my uncle asked me to send photos of my recent school project. I promised to send them the next day.",
            "After the call I felt happy and a little homesick for family meetings. Long calls can make faraway people feel closer.",
        ),
        [
            q(1, "When did the phone ring?", ["On Monday night", "On Sunday morning", "At school lunch", "During a football match only"], 0),
            q(2, "Who called?", ["The writer’s uncle", "A teacher", "A stranger", "The police"], 0),
            q(3, "Where was the uncle calling from?", ["Canada", "Italy", "Gabala", "The next room"], 0),
            q(4, "When might the uncle visit?", ["In August", "Next week only", "In December for sure", "Never"], 0),
            q(5, "What trip does he want to take?", ["To the mountains", "To the moon", "To a bank vault", "To a silent movie set"], 0),
            q(6, "How long did they talk?", ["Almost forty minutes", "Two minutes", "Three hours", "All night without stopping"], 0),
            q(7, "How did the writer improve the sound?", ["Moved near the window", "Bought a new house", "Ended the call", "Went outside forever"], 0),
            q(8, "What did the uncle ask the writer to send?", ["Photos of a school project", "Money", "Train tickets", "A football"], 0),
            q(9, "How did the writer feel after the call?", ["Happy", "Angry", "Bored", "Afraid"], 0),
            q(10, "What is the best title?", ["Phone Call", "Bank Fraud", "Silent Movies", "Space News"], 0),
        ],
    )
)

A2.append(
    pack(
        "A2",
        8,
        "Rainy Picnic",
        p(
            "We planned a picnic in the park for Saturday. My friends and I prepared sandwiches, fruit and a football. The morning was cloudy, but we still hoped for sun.",
            "At eleven o’clock we arrived and put a blanket under a large tree. After twenty minutes the rain started suddenly. At first it was light, then it became heavy.",
            "We quickly packed our food and ran to a nearby cafe. We were wet but we laughed a lot. Inside the cafe we ate our sandwiches and drank hot chocolate.",
            "When the rain stopped, we returned to the park for a short football game. The grass was wet, so we played carefully.",
            "The day was not perfect, but it was still fun. We learned to keep a plan flexible when the weather changes.",
        ),
        [
            q(1, "What did they plan for Saturday?", ["A picnic in the park", "A flight abroad", "An exam", "A bank visit"], 0),
            q(2, "What food did they prepare?", ["Sandwiches and fruit", "Only soup", "Only pizza from a restaurant", "Nothing"], 0),
            q(3, "What time did they arrive?", ["At eleven o’clock", "At six in the morning", "At midnight", "At three only"], 0),
            q(4, "Where did they put the blanket?", ["Under a large tree", "On a bus", "In a cafe first", "On the football roof"], 0),
            q(5, "Where did they go when it rained heavily?", ["To a nearby cafe", "Home immediately forever", "To the cinema only", "To school"], 0),
            q(6, "What did they drink in the cafe?", ["Hot chocolate", "Cold water only", "Coffee with salt", "Nothing"], 0),
            q(7, "What did they do after the rain stopped?", ["Played football carefully", "Slept under the tree", "Left the country", "Cancelled all friendships"], 0),
            q(8, "Why did they play carefully?", ["The grass was wet", "They had no ball", "It was night", "The cafe was closed"], 0),
            q(9, "What lesson did they learn?", ["Keep plans flexible when weather changes", "Never go outside", "Rain means failure", "Picnics are impossible"], 0),
            q(10, "What is the best title?", ["Rainy Picnic", "Bank Fraud", "Space News", "Silent Movies"], 0),
        ],
    )
)

A2.append(
    pack(
        "A2",
        9,
        "Football Match",
        p(
            "Last Friday our school team played against Green Hill School. The match started at four o’clock on our sports field. Many students came to watch and cheer.",
            "In the first half the score was 1–1. Our captain scored first, but Green Hill scored a few minutes later. At half-time our coach told us to pass the ball more and stay calm.",
            "In the second half I assisted a goal with a long pass. Five minutes before the end, our striker scored again. We won 3–1.",
            "After the match both teams shook hands. The Green Hill players were disappointed, but they congratulated us. Our coach said teamwork was the reason for our success.",
            "That evening I felt proud and tired. Winning is nice, but playing fairly is more important.",
        ),
        [
            q(1, "Who did they play against?", ["Green Hill School", "A professional club", "Teachers only", "A university team from abroad"], 0),
            q(2, "What time did the match start?", ["At four o’clock", "At noon", "At nine in the morning", "At night"], 0),
            q(3, "What was the score at half-time?", ["1–1", "3–1", "0–0", "2–0"], 0),
            q(4, "What did the coach say at half-time?", ["Pass more and stay calm", "Stop playing", "Argue with the referee", "Go home"], 0),
            q(5, "How did the writer help in the second half?", ["Assisted a goal with a long pass", "Scored three goals alone", "Became the referee", "Left the field early"], 0),
            q(6, "What was the final score?", ["3–1", "1–1", "0–5", "2–2"], 0),
            q(7, "What happened after the match?", ["Both teams shook hands", "A big fight started", "Nobody spoke", "The field closed forever"], 0),
            q(8, "What did the coach say was the reason for success?", ["Teamwork", "Luck only", "Expensive boots", "The weather"], 0),
            q(9, "How did the writer feel that evening?", ["Proud and tired", "Angry and bored", "Afraid", "Indifferent"], 0),
            q(10, "What is the best title?", ["Football Match", "Bank Fraud", "Space News", "Silent Movies"], 0),
        ],
    )
)

A2.append(
    pack(
        "A2",
        10,
        "Museum Visit",
        p(
            "On a school trip last month we visited the National History Museum. We left school by bus at nine and arrived forty minutes later.",
            "A guide met us at the entrance and explained the rules. We could take photos without flash, but we could not touch the objects. Our class stayed together in small groups.",
            "I liked the room with ancient tools and maps. There was also a short film about life in the past. My friend preferred the jewellery exhibition.",
            "At one o’clock we had lunch in the museum cafe. Then we had free time in the gift shop. I bought a small notebook with old city pictures on the cover.",
            "Before we left, we wrote three new facts in our worksheets. The trip helped me understand history better than a normal lesson.",
        ),
        [
            q(1, "Where did they go?", ["The National History Museum", "A cinema", "A football stadium", "An airport"], 0),
            q(2, "How long did the bus ride take?", ["Forty minutes", "Five minutes", "Three hours", "All day"], 0),
            q(3, "What photo rule was there?", ["Photos without flash", "No photos at all", "Only flash photos", "Video with loud music"], 0),
            q(4, "What room did the writer like?", ["Ancient tools and maps", "Only the cafe", "The car park", "The gift shop only"], 0),
            q(5, "What did the friend prefer?", ["The jewellery exhibition", "The bus ride", "Homework", "The rules talk only"], 0),
            q(6, "Where did they have lunch?", ["In the museum cafe", "At school", "At home", "On the bus floor"], 0),
            q(7, "What did the writer buy?", ["A small notebook", "A real ancient tool", "A ticket to Canada", "Nothing"], 0),
            q(8, "What did they write before leaving?", ["Three new facts in worksheets", "A long novel", "A complaint letter only", "Nothing"], 0),
            q(9, "What time did they leave school?", ["At nine", "At noon", "At four", "At midnight"], 0),
            q(10, "What is the best title?", ["Museum Visit", "Bank Fraud", "Space News", "Silent Movies"], 0),
        ],
    )
)

A2.append(
    pack(
        "A2",
        11,
        "Flat Share",
        p(
            "When I started university, I moved into a shared flat with two other students, Lala and Orkhan. The flat has three bedrooms, a kitchen and a small balcony.",
            "We made simple house rules in the first week. Everyone cleans the kitchen after cooking. We take turns buying shared food like rice, oil and tea. Quiet hours start at eleven at night.",
            "At first it was difficult because Orkhan liked loud music. After a calm conversation he agreed to use headphones in the evening.",
            "On Sundays we often cook dinner together and talk about our week. Sometimes we invite classmates for a film night.",
            "Sharing a flat teaches responsibility. I have learned to plan money better and to respect other people’s space.",
        ),
        [
            q(1, "How many students share the flat?", ["Three", "Two", "Four", "Five"], 0),
            q(2, "What rooms does the flat have?", ["Three bedrooms, a kitchen and a balcony", "Only one room", "Five bathrooms only", "A shop and an office"], 0),
            q(3, "When do quiet hours start?", ["At eleven at night", "At six in the morning", "Never", "At noon"], 0),
            q(4, "What problem happened at first?", ["Orkhan liked loud music", "There was no kitchen", "Lala left forever", "The balcony fell"], 0),
            q(5, "How was the problem solved?", ["He agreed to use headphones", "They called the police", "They moved out immediately", "They broke the speakers"], 0),
            q(6, "What do they often do on Sundays?", ["Cook dinner together", "Have exams all day", "Travel abroad", "Clean another building"], 0),
            q(7, "What shared food do they buy?", ["Rice, oil and tea", "Only pizza daily", "Cars", "Tickets"], 0),
            q(8, "What has the writer learned?", ["To plan money and respect space", "To ignore all rules", "To sleep all day", "To avoid classmates"], 0),
            q(9, "Who are the flatmates?", ["Lala and Orkhan", "Only teachers", "Anna and Marco only", "Strangers from the market"], 0),
            q(10, "What is the best title?", ["Flat Share", "Bank Fraud", "Space News", "Silent Movies"], 0),
        ],
    )
)

A2.append(
    pack(
        "A2",
        12,
        "Online Shop",
        p(
            "Last month I ordered a pair of running shoes from an online shop. The website showed good reviews and free delivery in three days.",
            "I chose size 42 and paid by card. The next day I received an email with a tracking number. I checked the map every evening.",
            "On the third day the parcel arrived, but the shoes were size 40. I felt disappointed and opened the shop’s help page.",
            "I wrote a short message explaining the mistake and attached a photo of the box label. The next morning the shop replied and offered a free exchange.",
            "One week later I received the correct size. Now I always double-check product details before I click “buy”. Online shopping is easy, but careful reading is important.",
        ),
        [
            q(1, "What did the writer order?", ["Running shoes", "A laptop", "Books", "Food"], 0),
            q(2, "What size did the writer choose?", ["42", "40", "38", "44"], 0),
            q(3, "How long was free delivery promised?", ["Three days", "One day", "One month", "Same hour"], 0),
            q(4, "What size arrived first?", ["40", "42", "38", "44"], 0),
            q(5, "How did the writer contact the shop?", ["Wrote a message with a photo", "Visited a bank", "Called the police", "Did nothing"], 0),
            q(6, "What did the shop offer?", ["A free exchange", "No help", "Extra wrong shoes", "A holiday"], 0),
            q(7, "When did the correct size arrive?", ["One week later", "The same night", "Never", "After one year"], 0),
            q(8, "What does the writer do now before buying?", ["Double-checks product details", "Buys without reading", "Orders five pairs always", "Avoids all websites forever"], 0),
            q(9, "How did the writer pay?", ["By card", "With cash on the street", "With fruit", "The shoes were free"], 0),
            q(10, "What is the best title?", ["Online Shop", "Bank Fraud", "Space News", "Silent Movies"], 0),
        ],
    )
)

A2.append(
    pack(
        "A2",
        13,
        "Camping",
        p(
            "In May our youth club went camping near a lake for two nights. We travelled by minibus and arrived in the afternoon.",
            "First we put up the tents. It took longer than we expected because the wind was strong. Then we collected wood for a small fire with the leader’s help.",
            "In the evening we cooked pasta and sat under the stars. Someone played a guitar and we sang quiet songs. At night the forest sounded different from the city.",
            "The next day we hiked for three hours and saw many birds. One student fell in soft mud, but nobody was hurt and we all laughed.",
            "On the last morning we cleaned the campsite carefully. Camping taught us teamwork and respect for nature.",
        ),
        [
            q(1, "How long was the camping trip?", ["Two nights", "One hour", "Two weeks", "One month"], 0),
            q(2, "Where did they camp?", ["Near a lake", "In the city centre", "At school", "At an airport"], 0),
            q(3, "Why was putting up tents difficult?", ["The wind was strong", "There were no tents", "It was snowing heavily", "Nobody helped"], 0),
            q(4, "What did they cook in the evening?", ["Pasta", "Pizza only", "Soup from a restaurant", "Nothing"], 0),
            q(5, "How long was the hike?", ["Three hours", "Ten minutes", "One day without stop", "Thirty seconds"], 0),
            q(6, "What happened to one student?", ["Fell in soft mud", "Got lost forever", "Broke a leg", "Left by plane"], 0),
            q(7, "What did they do on the last morning?", ["Cleaned the campsite", "Built a house", "Started a fire without rules", "Left rubbish everywhere"], 0),
            q(8, "What did camping teach them?", ["Teamwork and respect for nature", "How to drive", "How to ignore rules", "How to hate forests"], 0),
            q(9, "How did they travel there?", ["By minibus", "By plane", "By boat only", "On foot for two days"], 0),
            q(10, "What is the best title?", ["Camping", "Bank Fraud", "Space News", "Silent Movies"], 0),
        ],
    )
)

A2.append(
    pack(
        "A2",
        14,
        "Bike Repair",
        p(
            "My bike chain broke on the way to school last Tuesday. I had to walk the last kilometre and I arrived late for the first lesson.",
            "After school I took the bike to a small repair shop near the bus station. The mechanic looked at it and said the chain and one brake pad needed changing.",
            "The repair cost eighteen manats and took one hour. While I waited, I read a sports magazine in the shop.",
            "The mechanic also showed me how to check tyre pressure every week. He said many problems start from small forgotten details.",
            "Now my bike feels safe again. I leave home ten minutes earlier so I am not late if something goes wrong.",
        ),
        [
            q(1, "What broke on the bike?", ["The chain", "The wheel forever", "The seat only", "The bell"], 0),
            q(2, "How far did the writer walk?", ["The last kilometre", "Ten kilometres", "One metre", "All the way to another city"], 0),
            q(3, "Where was the repair shop?", ["Near the bus station", "Inside the school", "At home", "At the airport"], 0),
            q(4, "What needed changing?", ["The chain and one brake pad", "Only the colour", "The whole bike frame", "Nothing"], 0),
            q(5, "How much did the repair cost?", ["Eighteen manats", "Eighty manats", "Free", "Two manats"], 0),
            q(6, "How long did the repair take?", ["One hour", "One day", "Ten minutes", "One week"], 0),
            q(7, "What tip did the mechanic give?", ["Check tyre pressure every week", "Never ride again", "Sell the bike immediately", "Ignore all problems"], 0),
            q(8, "What does the writer do now?", ["Leaves home ten minutes earlier", "Stops using the bike", "Takes a plane to school", "Sleeps in the shop"], 0),
            q(9, "Why was the writer late?", ["Had to walk after the chain broke", "Forgot school exists", "The teacher cancelled class", "Slept until noon"], 0),
            q(10, "What is the best title?", ["Bike Repair", "Bank Fraud", "Space News", "Silent Movies"], 0),
        ],
    )
)

A2.append(
    pack(
        "A2",
        15,
        "Language Club",
        p(
            "Our school has an English language club that meets every Thursday after lessons. About fifteen students come each week. The club leader is a volunteer teacher called Mr. Samir.",
            "We practise speaking through short role-plays, such as ordering food or asking for directions. Sometimes we watch a short video and discuss it in simple English.",
            "Last month we prepared a mini drama about a family trip. I played the father and I had to learn twenty lines. It was difficult, but my friends helped me practise.",
            "After the drama night, some shy students started speaking more. The club feels friendly and nobody laughs when someone makes a mistake.",
            "I join because I want to feel confident in real conversations. Grades are important, but speaking practice helps me outside the classroom too.",
        ),
        [
            q(1, "When does the club meet?", ["Every Thursday after lessons", "Every Monday morning", "Only in exams week", "Once a year"], 0),
            q(2, "About how many students come?", ["Fifteen", "Fifty", "Two", "One hundred"], 0),
            q(3, "Who is the club leader?", ["Mr. Samir", "Ms. Gunel", "Chef Nigar", "Mrs. Sevinc"], 0),
            q(4, "What speaking activities do they do?", ["Role-plays like ordering food", "Only grammar tests", "Silent reading only", "Maths problems"], 0),
            q(5, "What did they prepare last month?", ["A mini drama about a family trip", "A sports day only", "A cooking exam", "A bank project"], 0),
            q(6, "What role did the writer play?", ["The father", "A tree", "The teacher", "A bus driver"], 0),
            q(7, "How many lines did the writer learn?", ["Twenty", "Two", "Two hundred", "None"], 0),
            q(8, "What changed after drama night?", ["Shy students spoke more", "The club closed", "Everyone left school", "Mistakes were punished"], 0),
            q(9, "Why does the writer join?", ["To feel confident in real conversations", "Only to get free food", "To avoid all English", "To sleep after school"], 0),
            q(10, "What is the best title?", ["Language Club", "Bank Fraud", "Space News", "Silent Movies"], 0),
        ],
    )
)

A2.append(
    pack(
        "A2",
        16,
        "Airport Delay",
        p(
            "In July my parents and I flew to Turkey for a short holiday. We arrived at the airport three hours before the flight, but the departure board soon showed a delay.",
            "At first the delay was one hour. Later it became three hours because of strong winds. Many families sat on the floor near the gate and waited.",
            "The airline gave us water and small sandwiches. My father downloaded offline games for me, and my mother read a book. I walked around the terminal to stay awake.",
            "Finally we boarded at night. The flight was calm and we landed safely. We reached the hotel after midnight, tired but relieved.",
            "Now I always pack a light jumper and a power bank for airport waits. Delays are annoying, but good preparation makes them easier.",
        ),
        [
            q(1, "Where were they flying?", ["To Turkey", "To Canada", "To Gabala by plane", "Nowhere"], 0),
            q(2, "How early did they arrive at the airport?", ["Three hours before the flight", "Ten minutes before", "One day before", "After the flight left"], 0),
            q(3, "Why was the flight delayed later?", ["Strong winds", "No tickets", "A lost passport only for them", "The hotel was full"], 0),
            q(4, "How long was the final delay?", ["Three hours", "One hour only", "Ten hours", "One minute"], 0),
            q(5, "What did the airline give?", ["Water and small sandwiches", "Free hotel rooms for all", "New phones", "Nothing"], 0),
            q(6, "What did the father do?", ["Downloaded offline games", "Slept outside", "Cancelled the holiday", "Drove the plane"], 0),
            q(7, "When did they board?", ["At night", "In the early morning only", "Never", "At lunch the next week"], 0),
            q(8, "When did they reach the hotel?", ["After midnight", "At noon the same day", "Before the delay", "One week later"], 0),
            q(9, "What does the writer pack now for waits?", ["A light jumper and a power bank", "Only heavy furniture", "Nothing", "Extra tickets only"], 0),
            q(10, "What is the best title?", ["Airport Delay", "Bank Fraud", "Space News", "Silent Movies"], 0),
        ],
    )
)

A2.append(
    pack(
        "A2",
        17,
        "Garden Project",
        p(
            "Our class started a garden project behind the school in March. Each group is responsible for one vegetable bed. My group grows tomatoes and herbs.",
            "Twice a week we water the plants and remove weeds. We keep a simple notebook with dates, weather notes and plant growth.",
            "In May some plants looked weak because there was little rain. Our teacher suggested natural compost, and after two weeks the plants looked stronger.",
            "Parents visited on Open Day and tasted a small herb salad we made. They asked many questions and took photos.",
            "The project taught us patience. Plants do not grow in one day, and careful work brings better results than rushing.",
        ),
        [
            q(1, "When did the garden project start?", ["In March", "In December", "In July only", "Last week suddenly"], 0),
            q(2, "What does the writer’s group grow?", ["Tomatoes and herbs", "Only flowers", "Trees for wood", "Nothing"], 0),
            q(3, "How often do they water the plants?", ["Twice a week", "Every hour", "Once a year", "Never"], 0),
            q(4, "What do they write in the notebook?", ["Dates, weather and growth", "Only jokes", "Exam answers", "Shopping lists"], 0),
            q(5, "Why did some plants look weak in May?", ["Little rain", "Too much snow", "Students ate them all", "No soil"], 0),
            q(6, "What did the teacher suggest?", ["Natural compost", "Cutting all plants", "Closing the garden", "Using less water forever"], 0),
            q(7, "What happened on Open Day?", ["Parents tasted a herb salad", "The garden was destroyed", "Nobody came", "It snowed inside"], 0),
            q(8, "What did the project teach?", ["Patience", "How to rush everything", "How to avoid work", "How to hate plants"], 0),
            q(9, "Where is the garden?", ["Behind the school", "On the roof of a bank", "At the airport", "In another city"], 0),
            q(10, "What is the best title?", ["Garden Project", "Bank Fraud", "Space News", "Silent Movies"], 0),
        ],
    )
)

A2.append(
    pack(
        "A2",
        18,
        "Cinema Night",
        p(
            "Last Saturday my friends and I went to the cinema to watch a comedy film. We bought tickets for the 7:30 showing and arrived twenty minutes early.",
            "The cinema was crowded, so we sat near the side. Before the film, there were many adverts. We bought popcorn and shared it.",
            "The film was funny and not too long. My favourite part was when the main character got lost in a supermarket. We laughed so much that a person in front turned around and smiled.",
            "After the film we walked to a nearby cafe and talked about the story. We all agreed the ending was surprising but happy.",
            "Cinema night has become our monthly tradition. It is a cheap way to relax and spend time together after a busy week.",
        ),
        [
            q(1, "What kind of film did they watch?", ["A comedy", "A horror film", "A documentary only", "A silent news report"], 0),
            q(2, "What time was the showing?", ["7:30", "5:00", "Midnight", "9:00 only"], 0),
            q(3, "How early did they arrive?", ["Twenty minutes early", "Two hours early", "Exactly on time with no wait", "After the film ended"], 0),
            q(4, "Where did they sit?", ["Near the side", "In the front middle always", "Outside", "On the stage"], 0),
            q(5, "What was the writer’s favourite part?", ["The character got lost in a supermarket", "The adverts only", "Leaving early", "The tickets queue"], 0),
            q(6, "Where did they go after the film?", ["To a nearby cafe", "Straight home in silence", "To school", "To the airport"], 0),
            q(7, "How did they describe the ending?", ["Surprising but happy", "Sad and confusing only", "Missing", "Boring"], 0),
            q(8, "How often is cinema night?", ["Monthly", "Every day", "Once in a lifetime", "Never again"], 0),
            q(9, "What did they buy to eat?", ["Popcorn", "A full dinner in the cinema seats", "Only water", "Nothing"], 0),
            q(10, "What is the best title?", ["Cinema Night", "Bank Fraud", "Space News", "Silent Movies"], 0),
        ],
    )
)

A2.append(
    pack(
        "A2",
        19,
        "Volunteer Day",
        p(
            "Our town organised a Volunteer Day in April. Students and adults cleaned parks, painted old benches and collected plastic bottles.",
            "I joined a group that cleaned the riverside path. We wore gloves and carried big bags. In three hours we filled twelve bags with rubbish.",
            "A local cafe gave free tea to volunteers at midday. People took photos and shared them online to encourage others.",
            "In the afternoon we planted ten small trees near the playground. A gardener showed us how to water them correctly.",
            "At the end of the day I felt useful and tired. Volunteer Day showed me that small actions can improve a place for everyone.",
        ),
        [
            q(1, "When was Volunteer Day?", ["In April", "In December", "Every Monday forever", "Last night only"], 0),
            q(2, "What did the writer’s group clean?", ["The riverside path", "A bank office", "The airport runway", "School exams"], 0),
            q(3, "How many bags did they fill?", ["Twelve", "Two", "One hundred", "None"], 0),
            q(4, "How long did the cleaning take?", ["Three hours", "Ten minutes", "One week", "All month"], 0),
            q(5, "What did the cafe give volunteers?", ["Free tea", "Free phones", "Free tickets abroad", "Nothing"], 0),
            q(6, "How many trees did they plant?", ["Ten", "One", "Fifty", "Zero"], 0),
            q(7, "Who showed them how to water the trees?", ["A gardener", "A pilot", "A banker", "Nobody"], 0),
            q(8, "How did the writer feel at the end?", ["Useful and tired", "Angry and bored", "Afraid", "Indifferent"], 0),
            q(9, "What else did volunteers do in town?", ["Painted benches and collected bottles", "Closed all parks", "Built a stadium in one hour", "Cancelled school"], 0),
            q(10, "What is the best title?", ["Volunteer Day", "Bank Fraud", "Space News", "Silent Movies"], 0),
        ],
    )
)

A2.append(
    pack(
        "A2",
        20,
        "Surprise Party",
        p(
            "Last Friday we organised a surprise party for our classmate Nigar because she was moving to another city. We planned everything in secret for one week.",
            "After the last lesson we asked her to come to the classroom for a “group photo”. When she opened the door, we shouted and showed a banner with her name.",
            "There was a cake, soft drinks and a box for handwritten notes. Each student wrote one wish for her new school life.",
            "Nigar cried happy tears and hugged everyone. She said she would video-call us every month. We took many photos together.",
            "Surprise parties need careful planning, but the smile on a friend’s face makes the work worthwhile.",
        ),
        [
            q(1, "Why was the party for Nigar?", ["She was moving to another city", "It was a national holiday only", "She won a lottery", "She became a teacher"], 0),
            q(2, "How long did they plan in secret?", ["One week", "One hour", "One year", "One day only without plans"], 0),
            q(3, "How did they get her to the classroom?", ["Asked her to come for a group photo", "Told her about the party early", "Sent a taxi", "Locked her outside"], 0),
            q(4, "What was on the banner?", ["Her name", "A football score", "A map of Canada", "Nothing"], 0),
            q(5, "What did students write?", ["One wish for her new school life", "Homework answers", "Complaints only", "Shopping lists"], 0),
            q(6, "How did Nigar react?", ["Cried happy tears and hugged everyone", "Got angry and left", "Ignored everyone", "Cancelled the move immediately"], 0),
            q(7, "What did she promise?", ["To video-call every month", "Never to call again", "To return the next day forever", "To delete all contacts"], 0),
            q(8, "When was the party?", ["Last Friday after the last lesson", "On Sunday morning", "During an exam", "At midnight in the park"], 0),
            q(9, "What food and drink were there?", ["Cake and soft drinks", "Only water", "A full restaurant menu", "Nothing to eat"], 0),
            q(10, "What is the best title?", ["Surprise Party", "Bank Fraud", "Space News", "Silent Movies"], 0),
        ],
    )
)

assert len(A2) == 20
