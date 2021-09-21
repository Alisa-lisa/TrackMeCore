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
    "MENTAL": ["mood", "pain", "anxiety", "joy", "happiness", "excitement", "calmness", "fear", "motivation"],
    "SOCIAL": ["family", "pet", "friends", "online_communication", "events", "sport"],
    "PHYSICAL": ["sport", "sleep", "hygine", "meditation", "pain", "walk", "chores"],
    "CONSUMABLE": ["food", "alcohol", "soft drinks", "water", "coffee", "nicotine", "meds"],
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
    insert into topics values ({}, '{}');
    """

    for index, value in enumerate(TOPICS, start=1):
        connection.execute(raw_query.format(index, value))


def set_default_attributes(connection: op) -> None:
    """setup default attributes for each of 4 default topics"""
    raw_query = """
    insert into attributes values ({}, '{}', {}, Null, Null, Null);
    """
    idx = 1
    for index, topic in enumerate(TOPICS, start=1):
        for attribute in ATTRITUES[topic]:
            connection.execute(raw_query.format(idx, attribute, index))
            idx += 1
