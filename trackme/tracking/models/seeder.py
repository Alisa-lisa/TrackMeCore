""" predefined information to spawn during alembic migration """
import os
import json


# Default settings for personal tracking
TOPICS = ["MENTAL", "PHYSICAL", "SOCIAL", "CONSUMABLE"]
ATTRITUES = {
    "MENTAL": ["mood", "stress", "motivation"],
    "SOCIAL": ["family", "friends", "work"],
    "PHYSICAL": ["sport", "sleep", "meditation"],
    "CONSUMABLE": ["alcohol", "water", "coffee", "smoking", "meds"],
}


def set_topics(connection) -> None:
    """
    Checks for provided configuration specifying topics
    if none is provided defaults to Mental, Social, Consumable and Physical.
    Configuration file should be provided in the root of the project with the name
    'tracking_configuration.json'
    """ 
    raw_query = """
    insert into topics(name) values ('{}');
    """
    topics = TOPICS
    file = os.getcwd() + "/tracking_configuration.json"
    if os.path.exists(file):
        with open('tracking_configuration.json', 'r') as conf:
                config = json.load(conf)
                if "topics" in config.keys():
                    topics = config["topics"]
                else:
                    topics = TOPICS
    for value in topics:
        connection.execute(raw_query.format(value))


def set_default_attributes(connection) -> None:
    """
    Checks for provided configuration specifying attributes for topics
    if none is provided defaults to pre-defined attributes
    for each of 4 default topics
    Configuration file should be provided in the root of the project with the name
    'tracking_configuration.json'
    """
    raw_query = """
    insert into attributes(name, topic_id) values ('{}', {});
    """
    idx = 1
    topics = TOPICS
    attributes = ATTRITUES
    file = os.getcwd() + "/tracking_configuration.json"
    if os.path.exists(file):
        with open('tracking_configuration.json', 'r') as conf:
            config = json.load(conf)
            if "topics" in config.keys() and "attributes" in config.keys():
                topics = config["topics"]
                attributes = config["attributes"]
            else:
                topics = TOPICS
                attributes = ATTRITUES
    for index, topic in enumerate(topics, start=1):
        for attribute in attributes[topic]:
            connection.execute(raw_query.format(attribute, index))
            idx += 1
