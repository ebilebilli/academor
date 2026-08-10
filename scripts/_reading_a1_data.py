# -*- coding: utf-8 -*-
"""Rewrite CEFR reading-test passages with stronger, level-appropriate texts + real questions."""
from __future__ import annotations

import json
import re
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "academor" / "portals" / "resources" / "quiz_questions"

# Target word counts (approx): A1 100–130 | A2 160–200 | B1 240–300


def p(*paragraphs: str) -> str:
    return "".join(f"<p>{t.strip()}</p>" for t in paragraphs if t.strip())


def q(qid: int, question: str, options: list[str], answer: int) -> dict:
    assert 0 <= answer < len(options) == 4
    return {"id": qid, "question": question, "options": options, "answer": answer}


def pack(level: str, quiz: int, title: str, passage: str, questions: list[dict]) -> dict:
    return {
        "level": level,
        "quiz": quiz,
        "title": title,
        "service": "general_english",
        "category_name": f"{level} Reading Tests",
        "has_shared_passage": True,
        "shared_passage": passage,
        "questions": questions,
    }


def word_count(html: str) -> int:
    plain = re.sub(r"<[^>]+>", " ", html)
    return len(plain.split())


# ---------------------------------------------------------------------------
# A1 — simple present, short sentences, concrete everyday topics (~100–130 w)
# ---------------------------------------------------------------------------

A1 = []

A1.append(
    pack(
        "A1",
        1,
        "My Family",
        p(
            "My name is Sara. I am ten years old and I live in Baku with my family.",
            "My mother is a nurse and my father works in a small shop. I have one brother. His name is Ali and he is seven years old.",
            "We live in a small flat near a park. My room is blue and I have many pencils there. I like drawing pictures of animals and trees.",
            "After school Ali and I play in the park. In the evening our family sits together and reads short stories. On Sundays we visit our grandmother.",
            "I love my family very much. We are happy and we help each other every day.",
        ),
        [
            q(1, "How old is Sara?", ["Ten", "Seven", "Twelve", "Five"], 0),
            q(2, "Who is Ali?", ["Sara’s friend", "Sara’s brother", "Sara’s father", "Sara’s teacher"], 1),
            q(3, "Where do they live?", ["In a hotel", "On a farm", "In a small flat in Baku", "In a big house in Ganja"], 2),
            q(4, "What does Sara like?", ["Football", "Cooking", "Driving", "Drawing"], 3),
            q(5, "What do they do in the evening?", ["Read stories together", "Go shopping", "Watch the news only", "Clean the school"], 0),
            q(6, "How many brothers does Sara have?", ["None", "One", "Two", "Three"], 1),
            q(7, "What is Sara’s mother’s job?", ["Teacher", "Nurse", "Driver", "Cook"], 1),
            q(8, "What colour is Sara’s room?", ["Red", "Green", "Blue", "Yellow"], 2),
            q(9, "When do they visit their grandmother?", ["On Mondays", "On Sundays", "Every night", "Never"], 1),
            q(10, "What is the best title?", ["Train Trip", "My Family", "Lost Keys", "City Noise"], 1),
        ],
    )
)

A1.append(
    pack(
        "A1",
        2,
        "My School",
        p(
            "My name is Leyla. I am nine years old and I go to Green School in Sumgayit.",
            "My school starts at eight o’clock in the morning. I have five lessons every day. My favourite lesson is English because we sing songs and play games.",
            "There are twenty children in my class. Our teacher is Mrs. Aysel. She is kind and she helps us with our homework.",
            "At break time I eat an apple and talk with my friends. After school I walk home with my sister. In the evening I do my homework at the table.",
            "I like my school. The classrooms are clean and the garden has many flowers.",
        ),
        [
            q(1, "How old is Leyla?", ["Seven", "Nine", "Eleven", "Thirteen"], 1),
            q(2, "Where is her school?", ["In Baku", "In Ganja", "In Sumgayit", "In Lankaran"], 2),
            q(3, "What time does school start?", ["At seven", "At eight", "At nine", "At ten"], 1),
            q(4, "How many lessons does she have every day?", ["Three", "Four", "Five", "Six"], 2),
            q(5, "What is her favourite lesson?", ["Maths", "English", "Sport", "Art"], 1),
            q(6, "Who is her teacher?", ["Mr. Ali", "Mrs. Aysel", "Miss Nigar", "Mr. Kamran"], 1),
            q(7, "What does she eat at break time?", ["An apple", "Pizza", "Soup", "Cake"], 0),
            q(8, "How many children are in her class?", ["Ten", "Fifteen", "Twenty", "Thirty"], 2),
            q(9, "Who walks home with Leyla?", ["Her brother", "Her sister", "Her teacher", "Nobody"], 1),
            q(10, "What is the best title?", ["My School", "Lost Keys", "City Noise", "Airport Delay"], 0),
        ],
    )
)

A1.append(
    pack(
        "A1",
        3,
        "At the Shop",
        p(
            "Every Saturday morning Ramin goes to the shop with his mother. The shop is near their house and it opens at nine o’clock.",
            "Today they need milk, bread, eggs and apples. Ramin puts the bread and milk in the basket. His mother chooses six red apples and a box of eggs.",
            "There are many people in the shop. The shop assistant is friendly. She smiles and helps them find the eggs.",
            "Ramin’s mother pays at the counter. The food costs twelve manats. Then they walk home together.",
            "At home Ramin helps put the food in the kitchen. He likes shopping days because he can choose the fruit.",
        ),
        [
            q(1, "When does Ramin go to the shop?", ["Every Monday", "Every Saturday morning", "Every night", "Only in summer"], 1),
            q(2, "What time does the shop open?", ["At eight", "At nine", "At ten", "At twelve"], 1),
            q(3, "What do they need today?", ["Only water", "Milk, bread, eggs and apples", "Only meat", "Clothes"], 1),
            q(4, "How many apples do they buy?", ["Two", "Four", "Six", "Ten"], 2),
            q(5, "Who helps them find the eggs?", ["A teacher", "The shop assistant", "A policeman", "A driver"], 1),
            q(6, "How much does the food cost?", ["Five manats", "Ten manats", "Twelve manats", "Twenty manats"], 2),
            q(7, "Where is the shop?", ["Far from their house", "Near their house", "In another city", "At school"], 1),
            q(8, "What does Ramin put in the basket?", ["Apples only", "Bread and milk", "Eggs only", "Clothes"], 1),
            q(9, "Why does Ramin like shopping days?", ["He can sleep", "He can choose the fruit", "He can drive", "He can watch TV"], 1),
            q(10, "What is the best title?", ["At the Shop", "Train Trip", "Exam Stress", "City Noise"], 0),
        ],
    )
)

A1.append(
    pack(
        "A1",
        4,
        "My Morning",
        p(
            "My name is Kamran. I wake up at seven o’clock every morning. First I wash my face and brush my teeth.",
            "Then I put on my school clothes. My mother makes breakfast for me. I usually eat bread with cheese and drink a cup of tea.",
            "After breakfast I put my books in my bag. I leave the house at half past seven. I walk to school with my friend Orkhan.",
            "School is not far. It takes fifteen minutes. Sometimes we talk about football on the way.",
            "I like mornings when the sun is bright. I feel ready for my lessons.",
        ),
        [
            q(1, "What time does Kamran wake up?", ["At six", "At seven", "At eight", "At nine"], 1),
            q(2, "What does he do first?", ["Watch TV", "Wash his face and brush his teeth", "Play football", "Call his friend"], 1),
            q(3, "What does he usually eat for breakfast?", ["Pizza", "Bread with cheese", "Soup", "Cake only"], 1),
            q(4, "What does he drink?", ["Coffee", "Juice", "Tea", "Milkshake"], 2),
            q(5, "What time does he leave the house?", ["At seven", "At half past seven", "At eight", "At nine"], 1),
            q(6, "Who walks to school with him?", ["His sister", "Orkhan", "His teacher", "Nobody"], 1),
            q(7, "How long does it take to walk to school?", ["Five minutes", "Fifteen minutes", "One hour", "Two hours"], 1),
            q(8, "What do they sometimes talk about?", ["Football", "Cooking", "Trains", "Banks"], 0),
            q(9, "Who makes breakfast?", ["His father", "His mother", "Orkhan", "His teacher"], 1),
            q(10, "What is the best title?", ["My Morning", "Lost Keys", "Airport Delay", "City Noise"], 0),
        ],
    )
)

A1.append(
    pack(
        "A1",
        5,
        "Pets",
        p(
            "Nara has a white cat called Mimi. Mimi is two years old and she lives in Nara’s flat in Ganja.",
            "Every morning Nara gives Mimi a little fish and clean water. Mimi likes to sit on the sofa and sleep in the sun near the window.",
            "In the afternoon Mimi plays with a small red ball. Sometimes she runs after a toy mouse. Nara laughs when Mimi jumps.",
            "At night Mimi sleeps on Nara’s bed. Nara brushes Mimi’s fur on Saturdays. The cat is soft and quiet.",
            "Nara loves her pet very much. She says Mimi is her best friend at home.",
        ),
        [
            q(1, "What pet does Nara have?", ["A cat", "A dog", "A bird", "A fish"], 0),
            q(2, "What is the cat’s name?", ["Maya", "Mimi", "Ali", "Tom"], 1),
            q(3, "How old is Mimi?", ["One", "Two", "Three", "Five"], 1),
            q(4, "What does Mimi eat in the morning?", ["Bread", "Fish", "Rice", "Cheese"], 1),
            q(5, "Where does Mimi like to sit?", ["On the sofa", "In the garden", "At school", "In a car"], 0),
            q(6, "What colour is the ball?", ["Blue", "Green", "Red", "Yellow"], 2),
            q(7, "Where does Mimi sleep at night?", ["On the floor", "On Nara’s bed", "In the kitchen", "Outside"], 1),
            q(8, "When does Nara brush Mimi’s fur?", ["Every Monday", "On Saturdays", "Never", "Every night"], 1),
            q(9, "Where does Nara live?", ["In Baku", "In Ganja", "In London", "In Paris"], 1),
            q(10, "What is the best title?", ["Pets", "Train Trip", "City Noise", "Bank Fraud"], 0),
        ],
    )
)

A1.append(
    pack(
        "A1",
        6,
        "Food",
        p(
            "My name is Aysel and I like good food. For breakfast I eat eggs and bread. I also drink warm milk.",
            "At school I have lunch at twelve o’clock. Today I have rice, chicken and salad. My friend gives me an orange.",
            "In the evening my mother cooks dinner. We often eat soup and bread. On Fridays we eat pizza together.",
            "I do not like spicy food. I like sweet things, but I eat fruit every day. Apples and bananas are my favourite.",
            "My father says healthy food helps us grow strong. I try to drink water and eat vegetables too.",
        ),
        [
            q(1, "What does Aysel eat for breakfast?", ["Pizza", "Eggs and bread", "Only fruit", "Soup"], 1),
            q(2, "What does she drink in the morning?", ["Coffee", "Warm milk", "Cola", "Tea only"], 1),
            q(3, "What time is lunch at school?", ["At ten", "At eleven", "At twelve", "At two"], 2),
            q(4, "What does she have for lunch today?", ["Rice, chicken and salad", "Only bread", "Pizza", "Soup only"], 0),
            q(5, "What do they often eat in the evening?", ["Soup and bread", "Only cake", "Ice cream", "Burgers"], 0),
            q(6, "When do they eat pizza?", ["On Mondays", "On Fridays", "Every day", "Never"], 1),
            q(7, "What food does she not like?", ["Fruit", "Spicy food", "Bread", "Milk"], 1),
            q(8, "What fruit does she like most?", ["Apples and bananas", "Only grapes", "Only melons", "No fruit"], 0),
            q(9, "Who cooks dinner?", ["Her father", "Her mother", "Her teacher", "Her friend"], 1),
            q(10, "What is the best title?", ["Food", "Lost Keys", "City Noise", "Exam Stress"], 0),
        ],
    )
)

A1.append(
    pack(
        "A1",
        7,
        "Friends",
        p(
            "My best friend is called Elvin. He is eleven years old and he lives next to my house in Mingachevir.",
            "We go to the same school and we sit together in class. Elvin is good at maths and he helps me with difficult numbers.",
            "After school we ride our bikes in the park. Sometimes we play football with other children. On rainy days we stay inside and draw pictures.",
            "Elvin has a small dog called Rocky. I like playing with Rocky because he is funny and fast.",
            "At the weekend we visit each other’s homes. I am happy because I have a kind friend.",
        ),
        [
            q(1, "What is the friend’s name?", ["Ali", "Elvin", "Kamran", "Orkhan"], 1),
            q(2, "How old is Elvin?", ["Nine", "Ten", "Eleven", "Twelve"], 2),
            q(3, "Where does Elvin live?", ["Far away", "Next to the writer’s house", "In another country", "At school"], 1),
            q(4, "What is Elvin good at?", ["Art only", "Maths", "Cooking", "Driving"], 1),
            q(5, "What do they do after school?", ["Sleep only", "Ride bikes in the park", "Go to work", "Watch the news"], 1),
            q(6, "What do they do on rainy days?", ["Swim", "Stay inside and draw", "Play outside football", "Go shopping"], 1),
            q(7, "What is the dog’s name?", ["Mimi", "Rocky", "Tom", "Max"], 1),
            q(8, "Where do they live?", ["In Mingachevir", "In London", "In Paris", "In Rome"], 0),
            q(9, "When do they visit each other’s homes?", ["Every night", "At the weekend", "Never", "Only in winter"], 1),
            q(10, "What is the best title?", ["Friends", "Airport Delay", "City Noise", "Bank Fraud"], 0),
        ],
    )
)

A1.append(
    pack(
        "A1",
        8,
        "My House",
        p(
            "We live in a small house with a garden. There are four rooms: a living room, a kitchen, my parents’ bedroom and my bedroom.",
            "The living room has a big sofa and a TV. We watch films there on Saturday evenings. The kitchen is yellow and my mother cooks there every day.",
            "My bedroom is small but tidy. I have a desk near the window and a shelf for my books. There is a green plant on the desk.",
            "Outside there is a garden with two trees and many flowers. In summer we sit under the trees and drink lemonade.",
            "I like our house because it is quiet and warm. Our neighbours are friendly too.",
        ),
        [
            q(1, "How many rooms are there?", ["Two", "Three", "Four", "Six"], 2),
            q(2, "What is in the living room?", ["A big sofa and a TV", "Only a bed", "A car", "A shop"], 0),
            q(3, "What colour is the kitchen?", ["Blue", "Yellow", "Red", "Black"], 1),
            q(4, "Where is the desk?", ["In the garden", "Near the window", "In the kitchen", "Outside"], 1),
            q(5, "What is on the desk?", ["A green plant", "A TV", "A dog", "A bike"], 0),
            q(6, "How many trees are in the garden?", ["One", "Two", "Five", "Ten"], 1),
            q(7, "What do they drink in summer under the trees?", ["Coffee", "Lemonade", "Soup", "Milk only"], 1),
            q(8, "When do they watch films?", ["On Monday mornings", "On Saturday evenings", "At school", "Never"], 1),
            q(9, "Why does the writer like the house?", ["It is noisy", "It is quiet and warm", "It is very big", "It has a shop"], 1),
            q(10, "What is the best title?", ["My House", "Lost Keys", "City Noise", "Train Trip"], 0),
        ],
    )
)

A1.append(
    pack(
        "A1",
        9,
        "Weather",
        p(
            "Today the weather in Baku is sunny and warm. The sky is blue and there are no clouds. People walk in the park and children play football.",
            "Yesterday it was rainy and cold. I took my umbrella to school. The streets were wet and the buses were slow.",
            "In winter it is often windy here. I wear a coat, a hat and warm shoes. Sometimes we see a little snow.",
            "In summer it is very hot. We drink a lot of water and stay in the shade at noon. In the evening it is nicer.",
            "I like sunny days best because I can ride my bike and visit my friends outside.",
        ),
        [
            q(1, "What is the weather today?", ["Rainy", "Sunny and warm", "Snowy", "Foggy"], 1),
            q(2, "What was the weather yesterday?", ["Sunny", "Rainy and cold", "Hot", "Windy and dry"], 1),
            q(3, "What did the writer take to school yesterday?", ["A ball", "An umbrella", "A bike", "A kite"], 1),
            q(4, "What is winter often like?", ["Always hot", "Often windy", "Always dry", "Never cold"], 1),
            q(5, "What does the writer wear in winter?", ["A coat, a hat and warm shoes", "Only a T-shirt", "Swim clothes", "Nothing"], 0),
            q(6, "What is summer like?", ["Very hot", "Very cold", "Always rainy", "Always snowy"], 0),
            q(7, "What do they do at noon in summer?", ["Stay in the shade", "Play in the sun only", "Go skiing", "Make a snowman"], 0),
            q(8, "Which days does the writer like best?", ["Rainy days", "Sunny days", "Snowy nights only", "Foggy mornings"], 1),
            q(9, "Where do people walk today?", ["In the park", "In the snow", "In a museum only", "At the airport"], 0),
            q(10, "What is the best title?", ["Weather", "Bank Fraud", "Exam Stress", "Lost Keys"], 0),
        ],
    )
)

A1.append(
    pack(
        "A1",
        10,
        "Weekend",
        p(
            "At the weekend I do not go to school. On Saturday morning I help my mother clean the house. Then we go to the market to buy fruit and vegetables.",
            "On Saturday afternoon I visit my grandparents. My grandmother makes cakes and my grandfather tells funny stories.",
            "On Sunday I meet my friends in the park. We play basketball or ride our bikes. If it rains, we go to the cinema.",
            "In the evening I prepare my school bag for Monday. I also call my cousin and talk for ten minutes.",
            "Weekends are short but happy. I rest and I also help my family.",
        ),
        [
            q(1, "What does the writer do on Saturday morning?", ["Sleeps all day", "Helps clean the house", "Goes to school", "Works in a bank"], 1),
            q(2, "Where do they go after cleaning?", ["To the market", "To the airport", "To the office", "To the gym only"], 0),
            q(3, "Who does the writer visit on Saturday afternoon?", ["Teachers", "Grandparents", "Strangers", "The police"], 1),
            q(4, "What does the grandmother make?", ["Soup only", "Cakes", "Pizza every day", "Nothing"], 1),
            q(5, "Where do friends meet on Sunday?", ["In the park", "At the bank", "At the hospital", "At the station only"], 0),
            q(6, "What do they do if it rains?", ["Go to the cinema", "Play outside only", "Swim in the sea", "Go camping"], 0),
            q(7, "What does the writer prepare on Sunday evening?", ["A party", "The school bag for Monday", "A trip abroad", "A big dinner for school"], 1),
            q(8, "How long does the writer talk to the cousin?", ["One minute", "Ten minutes", "One hour", "All night"], 1),
            q(9, "How does the writer feel about weekends?", ["Bored", "Happy", "Angry", "Afraid"], 1),
            q(10, "What is the best title?", ["Weekend", "City Noise", "Lost Keys", "Exam Stress"], 0),
        ],
    )
)

A1.append(
    pack(
        "A1",
        11,
        "Sports",
        p(
            "My name is Farid and I love sports. Three times a week I go swimming at the sports centre near my school.",
            "On Tuesdays and Thursdays I play football with my class. I am a goalkeeper. Our team wears blue shirts.",
            "At the weekend I sometimes play table tennis with my father. He is very good and he usually wins, but I am learning fast.",
            "My sister prefers running. She runs in the park every morning before school. She wants to join a running club.",
            "Sport helps me feel strong and happy. After exercise I drink water and rest for a short time.",
        ),
        [
            q(1, "How often does Farid go swimming?", ["Every day", "Three times a week", "Once a month", "Never"], 1),
            q(2, "Where does he swim?", ["In the sea only", "At the sports centre", "At home", "At the airport"], 1),
            q(3, "When does he play football?", ["On Mondays only", "On Tuesdays and Thursdays", "Every night", "Only in winter"], 1),
            q(4, "What position does he play?", ["Striker", "Goalkeeper", "Referee", "Coach"], 1),
            q(5, "What colour are the team shirts?", ["Red", "Blue", "Yellow", "Black"], 1),
            q(6, "Who does he play table tennis with?", ["His sister", "His father", "His teacher", "Nobody"], 1),
            q(7, "What sport does his sister prefer?", ["Swimming", "Football", "Running", "Tennis"], 2),
            q(8, "When does his sister run?", ["Every morning before school", "Only at night", "Only on Sundays", "Never"], 0),
            q(9, "What does he drink after exercise?", ["Cola", "Water", "Coffee", "Soup"], 1),
            q(10, "What is the best title?", ["Sports", "Lost Keys", "City Noise", "Bank Fraud"], 0),
        ],
    )
)

A1.append(
    pack(
        "A1",
        12,
        "Clothes",
        p(
            "Today is a school day, so I wear my school uniform. It is a white shirt, dark trousers and black shoes.",
            "When it is cold, I also wear a grey jumper and a warm coat. In my bag I keep a scarf and gloves.",
            "At the weekend I like colourful clothes. I wear blue jeans, a red T-shirt and white trainers. My sister wears a long green dress.",
            "Yesterday we went shopping for new clothes. I bought a brown jacket because my old one was small.",
            "My mother says clean clothes are important. Every Sunday evening I prepare my clothes for the next week.",
        ),
        [
            q(1, "What does the writer wear on a school day?", ["A uniform", "Only pyjamas", "A green dress", "Swim clothes"], 0),
            q(2, "What colour is the school shirt?", ["Blue", "White", "Red", "Green"], 1),
            q(3, "What does he wear when it is cold?", ["A grey jumper and a warm coat", "Only a T-shirt", "Shorts", "Nothing"], 0),
            q(4, "What is in the bag?", ["A scarf and gloves", "A ball only", "Food only", "Books only"], 0),
            q(5, "What colour are the weekend jeans?", ["Black", "Blue", "Yellow", "Pink"], 1),
            q(6, "What does the sister wear?", ["A long green dress", "A school uniform only", "A brown jacket", "Black shoes only"], 0),
            q(7, "What did the writer buy yesterday?", ["A brown jacket", "A red car", "A bike", "A phone"], 0),
            q(8, "Why did he buy a new jacket?", ["It was free", "The old one was small", "He lost his bag", "The teacher asked"], 1),
            q(9, "When does he prepare clothes for the week?", ["On Sunday evening", "On Monday morning at school", "Never", "Every night at midnight"], 0),
            q(10, "What is the best title?", ["Clothes", "Airport Delay", "City Noise", "Exam Stress"], 0),
        ],
    )
)

A1.append(
    pack(
        "A1",
        13,
        "City Park",
        p(
            "Near my home there is a big city park. It has tall trees, a small lake and a playground for children.",
            "In the morning many people walk or run there. Old people sit on benches and talk. Children play on the swings and the slide.",
            "There is a little cafe next to the lake. You can buy ice cream and juice. In spring the flowers are beautiful and colourful.",
            "On Sundays my family goes to the park after lunch. We take a ball and play for one hour. Then we feed the ducks near the water.",
            "The park is clean and quiet. I feel happy when I go there.",
        ),
        [
            q(1, "What is near the writer’s home?", ["A big city park", "An airport", "A factory", "A hospital only"], 0),
            q(2, "What is in the park?", ["Tall trees, a lake and a playground", "Only cars", "Only shops", "Only houses"], 0),
            q(3, "What do old people do there?", ["Play football", "Sit on benches and talk", "Drive cars", "Sell tickets"], 1),
            q(4, "What can you buy at the cafe?", ["Ice cream and juice", "Cars", "Books only", "Clothes"], 0),
            q(5, "When are the flowers beautiful?", ["In spring", "Only in winter", "Never", "Only at night"], 0),
            q(6, "When does the family go to the park?", ["On Sundays after lunch", "Every midnight", "Only on Mondays before school", "Never"], 0),
            q(7, "How long do they play?", ["Ten minutes", "One hour", "All day", "One minute"], 1),
            q(8, "What do they feed?", ["The ducks", "The cats at school", "The dogs at the bank", "Nothing"], 0),
            q(9, "How is the park?", ["Dirty and noisy", "Clean and quiet", "Closed always", "Very dark"], 1),
            q(10, "What is the best title?", ["City Park", "Lost Keys", "Bank Fraud", "Exam Stress"], 0),
        ],
    )
)

A1.append(
    pack(
        "A1",
        14,
        "Bus Ride",
        p(
            "Every day I take the bus to school. The bus stop is in front of our building. The number 12 bus comes at twenty past seven.",
            "The bus is often full in the morning. I usually find a seat near the window. I look at the shops and trees on the way.",
            "The ride takes about twenty-five minutes. Sometimes the bus is late when there is a lot of traffic.",
            "Yesterday a kind old man gave me his seat because the bus was crowded. I said thank you and smiled.",
            "I like the bus ride because I can meet friends and talk before lessons start.",
        ),
        [
            q(1, "How does the writer go to school?", ["By bus", "By plane", "By boat", "By taxi every day"], 0),
            q(2, "Where is the bus stop?", ["In front of the building", "Far in another city", "Inside the school", "At the airport"], 0),
            q(3, "Which bus does the writer take?", ["Number 5", "Number 12", "Number 20", "Number 100"], 1),
            q(4, "What time does the bus come?", ["At seven", "At twenty past seven", "At eight", "At nine"], 1),
            q(5, "How long is the ride?", ["Five minutes", "About twenty-five minutes", "Two hours", "All day"], 1),
            q(6, "When is the bus sometimes late?", ["When there is a lot of traffic", "When it is Sunday", "When school is closed", "Never"], 0),
            q(7, "What happened yesterday?", ["A kind old man gave the writer a seat", "The bus did not come", "The writer drove a car", "School was cancelled"], 0),
            q(8, "Where does the writer usually sit?", ["Near the window", "On the floor", "Outside", "In the driver’s seat"], 0),
            q(9, "Why does the writer like the bus ride?", ["To sleep only", "To meet friends and talk", "To cook food", "To buy a car"], 1),
            q(10, "What is the best title?", ["Bus Ride", "City Noise", "Bank Fraud", "Exam Stress"], 0),
        ],
    )
)

A1.append(
    pack(
        "A1",
        15,
        "Birthday",
        p(
            "Last Saturday was my birthday. I turned twelve years old. In the morning my parents gave me a new blue bike.",
            "In the afternoon my friends came to our flat. There were eight children at the party. We played games and listened to music.",
            "My mother made a big chocolate cake with twelve candles. Everyone sang “Happy Birthday” and I blew out the candles.",
            "I got books, a football and a red cap as presents. My grandmother gave me a warm jumper.",
            "In the evening we ate pizza and cake. I was tired but very happy. It was a wonderful day.",
        ),
        [
            q(1, "When was the birthday?", ["Last Saturday", "Last Monday", "Next week", "Yesterday morning only"], 0),
            q(2, "How old did the writer turn?", ["Ten", "Eleven", "Twelve", "Thirteen"], 2),
            q(3, "What did the parents give in the morning?", ["A new blue bike", "A phone", "A car", "A dog"], 0),
            q(4, "How many children were at the party?", ["Four", "Six", "Eight", "Twelve"], 2),
            q(5, "What kind of cake was it?", ["Chocolate", "Lemon only", "No cake", "Cheese"], 0),
            q(6, "How many candles were on the cake?", ["Ten", "Eleven", "Twelve", "Twenty"], 2),
            q(7, "What presents did the writer get?", ["Books, a football and a red cap", "Only money", "A plane ticket", "Nothing"], 0),
            q(8, "What did the grandmother give?", ["A warm jumper", "A bike", "A football", "A cake"], 0),
            q(9, "What did they eat in the evening?", ["Pizza and cake", "Only salad", "Soup only", "Nothing"], 0),
            q(10, "What is the best title?", ["Birthday", "Lost Keys", "City Noise", "Exam Stress"], 0),
        ],
    )
)

A1.append(
    pack(
        "A1",
        16,
        "Library",
        p(
            "There is a public library near my school. It is open from nine in the morning until six in the evening.",
            "I go there twice a week after lessons. I like the quiet rooms and the big shelves full of books.",
            "Last week I borrowed two story books and one book about animals. I can keep them for two weeks.",
            "The librarian is called Mrs. Sevinc. She helps children find easy books. She also reads stories on Fridays at four o’clock.",
            "At home I read for thirty minutes every night. Books help me learn new words and they make me happy.",
        ),
        [
            q(1, "Where is the library?", ["Near the school", "Far in another country", "At the airport", "Inside a hospital"], 0),
            q(2, "When is the library open?", ["From 9 to 6", "Only at night", "Never", "Only on Sundays"], 0),
            q(3, "How often does the writer go?", ["Twice a week", "Once a year", "Every hour", "Never"], 0),
            q(4, "What did the writer borrow last week?", ["Two story books and one animal book", "Only magazines", "A laptop", "Clothes"], 0),
            q(5, "How long can the books be kept?", ["Two days", "Two weeks", "Two years", "One hour"], 1),
            q(6, "Who is the librarian?", ["Mrs. Sevinc", "Mr. Ali", "Miss Nara", "Mr. Farid"], 0),
            q(7, "When does she read stories?", ["On Fridays at four", "Every Monday at eight", "Never", "Only in summer"], 0),
            q(8, "How long does the writer read at home?", ["Five minutes", "Thirty minutes", "Three hours", "All night"], 1),
            q(9, "Why does the writer like books?", ["They help learn new words", "They are heavy", "They are expensive", "They are noisy"], 0),
            q(10, "What is the best title?", ["Library", "Lost Keys", "City Noise", "Airport Delay"], 0),
        ],
    )
)

A1.append(
    pack(
        "A1",
        17,
        "Doctor Visit",
        p(
            "Yesterday I felt ill. I had a headache and a sore throat. My mother took me to the doctor in the afternoon.",
            "We waited fifteen minutes in the waiting room. Then the doctor called my name. She asked me questions and looked at my throat.",
            "The doctor said I had a cold. She told me to rest at home and drink warm tea. She also gave me some medicine.",
            "I did not go to school today. I stayed in bed and slept a lot. My mother made soup for me.",
            "I feel a little better now. Tomorrow I hope I can go back to school and see my friends.",
        ),
        [
            q(1, "How did the writer feel yesterday?", ["Ill", "Very happy", "Hungry only", "Angry"], 0),
            q(2, "What symptoms did the writer have?", ["A headache and a sore throat", "A broken leg", "Only a toothache", "Nothing"], 0),
            q(3, "Who took the writer to the doctor?", ["The teacher", "The mother", "A friend", "Nobody"], 1),
            q(4, "How long did they wait?", ["Five minutes", "Fifteen minutes", "One hour", "All day"], 1),
            q(5, "What did the doctor say?", ["It was a cold", "It was nothing", "Go to sport now", "Travel today"], 0),
            q(6, "What should the writer drink?", ["Warm tea", "Cold cola", "Coffee", "Nothing"], 0),
            q(7, "Did the writer go to school today?", ["No", "Yes", "Only in the morning", "Only for sport"], 0),
            q(8, "What did the mother make?", ["Soup", "Pizza", "Cake", "Ice cream"], 0),
            q(9, "How does the writer feel now?", ["A little better", "Much worse", "The same and angry", "Afraid of school"], 0),
            q(10, "What is the best title?", ["Doctor Visit", "Lost Keys", "City Noise", "Train Trip"], 0),
        ],
    )
)

A1.append(
    pack(
        "A1",
        18,
        "At the Cafe",
        p(
            "On Friday afternoon my aunt took me to a small cafe near the river. The cafe is called Sunny Cup and it is always busy.",
            "We sat at a table by the window. I ordered a cheese sandwich and a glass of orange juice. My aunt ordered coffee and a piece of cake.",
            "The waiter was friendly and fast. The food came after ten minutes. My sandwich was fresh and tasty.",
            "While we ate, we talked about my school and her work. She gave me some good advice about reading more books.",
            "After we paid the bill, we walked along the river for twenty minutes. It was a nice and quiet afternoon.",
        ),
        [
            q(1, "When did they go to the cafe?", ["On Friday afternoon", "On Monday morning", "At midnight", "On Sunday night only"], 0),
            q(2, "What is the cafe called?", ["Sunny Cup", "Big Burger", "Night Star", "Green Bus"], 0),
            q(3, "Where did they sit?", ["By the window", "Outside in the rain", "In the kitchen", "On the bus"], 0),
            q(4, "What did the writer order?", ["A cheese sandwich and orange juice", "Only coffee", "Pizza and cola", "Soup only"], 0),
            q(5, "What did the aunt order?", ["Coffee and cake", "A sandwich", "Tea only", "Nothing"], 0),
            q(6, "How long did the food take?", ["Two minutes", "Ten minutes", "One hour", "All afternoon"], 1),
            q(7, "What did they talk about?", ["School and her work", "Only football scores", "Buying a car", "Flying to space"], 0),
            q(8, "What advice did the aunt give?", ["Read more books", "Stop school", "Sleep all day", "Never read"], 0),
            q(9, "What did they do after paying?", ["Walked along the river", "Went to work", "Played football", "Went home immediately only"], 0),
            q(10, "What is the best title?", ["At the Cafe", "City Noise", "Exam Stress", "Bank Fraud"], 0),
        ],
    )
)

A1.append(
    pack(
        "A1",
        19,
        "Holidays",
        p(
            "In summer my family goes on holiday for one week. Last year we went to the seaside in Lankaran.",
            "We stayed in a small hotel near the beach. Every morning we swam in the sea. The water was warm and clean.",
            "In the afternoon we walked in the town and bought ice cream. My father took many photos. My mother read a book under an umbrella.",
            "One day we visited a fruit market. We bought peaches and cherries. They were sweet and fresh.",
            "I want to go there again next summer. Holidays help us rest and spend happy time together.",
        ),
        [
            q(1, "How long is the family holiday?", ["One day", "One week", "One month", "One year"], 1),
            q(2, "Where did they go last year?", ["To the seaside in Lankaran", "To the mountains only", "To another country by plane", "Nowhere"], 0),
            q(3, "Where did they stay?", ["In a small hotel near the beach", "At school", "In a tent in Baku", "At the airport"], 0),
            q(4, "What did they do every morning?", ["Swam in the sea", "Went to work", "Studied maths", "Cleaned the school"], 0),
            q(5, "What did the father do?", ["Took many photos", "Cooked all day", "Slept only", "Drove a bus"], 0),
            q(6, "What did the mother do?", ["Read a book under an umbrella", "Played football", "Sold ice cream", "Built a hotel"], 0),
            q(7, "What fruit did they buy?", ["Peaches and cherries", "Only bananas", "Only apples from home", "Nothing"], 0),
            q(8, "How was the fruit?", ["Sweet and fresh", "Old and bad", "Frozen", "Very spicy"], 0),
            q(9, "What does the writer want next summer?", ["To go there again", "To stay home forever", "To work in a bank", "To skip holiday"], 0),
            q(10, "What is the best title?", ["Holidays", "Lost Keys", "City Noise", "Exam Stress"], 0),
        ],
    )
)

A1.append(
    pack(
        "A1",
        20,
        "My Teacher",
        p(
            "My favourite teacher is Mr. Rashad. He teaches history at our school. He is tall and he always smiles.",
            "His lessons are interesting. He tells stories about old cities and famous people. Sometimes he shows pictures on the board.",
            "Mr. Rashad is strict but fair. He wants us to listen carefully and do our homework on time. He helps students who do not understand.",
            "Last month our class visited a museum with him. We learned about ancient coins and maps. It was my best school trip.",
            "I like Mr. Rashad because he believes in us. He says hard work can open many doors.",
        ),
        [
            q(1, "What does Mr. Rashad teach?", ["History", "Sport", "Music", "Cooking"], 0),
            q(2, "How does he look?", ["Tall and always smiling", "Short and angry", "Old and quiet only", "Never at school"], 0),
            q(3, "What makes his lessons interesting?", ["Stories about old cities and people", "Only tests", "Long silence", "No talking"], 0),
            q(4, "How is he as a teacher?", ["Strict but fair", "Never in class", "Always angry", "Always late"], 0),
            q(5, "What does he want students to do?", ["Listen and do homework on time", "Sleep in class", "Ignore homework", "Leave school"], 0),
            q(6, "Where did the class go last month?", ["To a museum", "To the airport", "To a bank", "To a factory"], 0),
            q(7, "What did they learn about?", ["Ancient coins and maps", "Only football", "Cooking recipes", "Car engines"], 0),
            q(8, "What does he say about hard work?", ["It can open many doors", "It is useless", "It is boring only", "It is for robots"], 0),
            q(9, "Why does the writer like him?", ["He believes in students", "He gives no homework", "He cancels all lessons", "He is never there"], 0),
            q(10, "What is the best title?", ["My Teacher", "Lost Keys", "City Noise", "Airport Delay"], 0),
        ],
    )
)

assert len(A1) == 20
