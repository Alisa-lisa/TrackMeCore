""" predefined information to spawn during alembic migration """
TOPICS = ["MENTAL", "PHYSICAL", "SOCIAL", "CONSUMABLE"]
"""
MENTAL - feelings, emotions, motivation, mood, etc.
PHYSICAL - sensations in the body, physical activity like sport
SOCIAL - connections and social events like "talked to mom", 1:1 with my boss
CONSUMPTION - meds, food, etc.
"""
ATTRITUES = {
    "MENTAL": ["mood", "stress", "motivation"],
    "SOCIAL": ["family", "friends", "work"],
    "PHYSICAL": ["sport", "sleep", "meditation"],
    "CONSUMABLE": ["alcohol", "water", "coffee", "smoking", "meds"],
}
"""
Attributes are some activities, events, states that can be associated with a data entry
and estimate as an additional information
Default values are:
    Mental: mood, stress, motivation
    Physical: family, friends, work
    Social: sport, sleep, meditation
    Consumable: alcohol, water, coffee, smoking, meds
"""


def set_topics(connection) -> None:
    raw_query = """
    insert into topics(name) values ('{}');
    """
    for value in TOPICS:
        connection.execute(raw_query.format(value))


def set_default_attributes(connection) -> None:
    """setup default attributes for each of 4 default topics"""
    raw_query = """
    insert into attributes(name, topic_id) values ('{}', {});
    """
    idx = 1
    for index, topic in enumerate(TOPICS, start=1):
        for attribute in ATTRITUES[topic]:
            connection.execute(raw_query.format(attribute, index))
            idx += 1
