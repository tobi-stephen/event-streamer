from confluent_kafka import Producer

import json
import logging
from common import *


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class KafkaService:

    def __init__(self):
        pass

    def produce_idea_event(self, event_key: str, event_data: dict):
        # get config properties
        config = read_config()

        # creates a new producer instance
        producer = Producer(config)

        # get key and value from event_data
        producer.produce(EVENT_IDEA_TOPIC, key=event_key, value=json.dumps(event_data))
        logger.info(f'produced message to {EVENT_IDEA_TOPIC}: key={event_key}, value={event_data}')
        
        # send any outstanding or buffered messages to the Kafka broker
        producer.flush()
