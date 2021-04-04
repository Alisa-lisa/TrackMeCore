""" predefined information to spawn during alembic migration """

from alembic import op



TOPICS = ["MENTAL", "PHYSICAL", "SOCIAL", "CONSUMABLE"]
"""
MENTAL - feelings, emotions, motivation, mood, etc.
PHYSICAL - sensations in the body, physical activity like sport 
SOCIAL - connections and social events like "talked to mom", 1:1 with my boss
CONSUMPTION - meds, food, etc.
"""



def set_topics(connection: op) -> None:
    raw_query = """
    insert into topics values ({}, '{}');
    """

    for index, value in enumerate(TOPICS, start=1):
        op.execute(raw_query.format(index, value))
