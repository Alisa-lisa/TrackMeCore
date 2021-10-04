""" predefined information to spawn during alembic migration """

from alembic import op


TOPICS = ["MENTAL", "PHYSICAL", "SOCIAL", "CONSUMABLE"]
"""
MENTAL - feelings, emotions, motivation, mood, etc.
PHYSICAL - sensations in the body, physical activity like sport
SOCIAL - connections and social events like "talked to mom", 1:1 with my boss
CONSUMPTION - meds, food, etc.
"""
ATTRITUES = {
    "MENTAL": [
        "mood",
        "pain",
        "anxiety",
        "joy",
        "happy",
        "excitement",
        "calm",
        "fear",
        "motivation",
    ],
    "SOCIAL": ["family", "pets", "friends", "online", "irl", "sport"],
    "PHYSICAL": ["sport", "sleep", "hygiene", "meditation", "pain", "walk", "chores"],
    "CONSUMABLE": ["food", "alcohol", "drinks", "water", "coffee", "nicotine", "meds"],
}
"""
Attributes are some activities, events, states that can be associated with a data entry
and estimate as an additional information
Default values are:
    Mental: mood, anxiety, happiness, love, emotions (similar to fast track - emotional mix)
    Physical: activity, sport, pain, sleep
    Social: family, friends, partner, pets
    Consumable: food, alcohol, meds, tobacco, drinks
"""


def set_topics(connection: op) -> None:
    raw_query = """
    insert into topics(name) values ('{}');
    """
    for value in TOPICS:
        connection.execute(raw_query.format(value))


def set_default_attributes(connection: op) -> None:
    """setup default attributes for each of 4 default topics"""
    raw_query = """
    insert into attributes(name, topic_id) values ('{}', {});
    """
    idx = 1
    for index, topic in enumerate(TOPICS, start=1):
        for attribute in ATTRITUES[topic]:
            connection.execute(raw_query.format(attribute, index))
            idx += 1
