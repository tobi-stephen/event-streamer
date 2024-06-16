# setting up consumer app as stand alone
from searchclients import Search, providers
from common import *

import logging
from confluent_kafka import Consumer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def consume(topic, config, search_client: Search):

    logger.info(f'Starting consumer for topic {topic}')
    # creates a new consumer instance
    consumer = Consumer(config)

    # subscribes to the specified topic
    consumer.subscribe([topic])

    try:
        while True:
            # consumer polls the topic and indexes it into elastic
            msg = consumer.poll(1.0)
            if msg is not None:
                if msg.error() is not None:
                    logger.info(f'Consumer error: {msg.error()}')
                    continue
                
                key: bytes = msg.key()
                value: bytes = msg.value()
                logger.info(f'Consumed message from topic {topic}: key = {key}, value = {value}')
                response = search_client.insert_document(key, value)
                logger.info(f'indexing result: {response}')
                
    except Exception as e:
        logger.error(e)
    finally:
        # closes the consumer connection
        consumer.close()


def process():
    debug = False
    import os
    prov = providers.get(os.getenv('SEARCH_PROVIDER') or 'elastic')
    search_client: Search = prov(EVENT_IDEA_INDEX, True)
    logger.info('search client is ready')

    if debug:
        search_client.create_index()

    consume(EVENT_IDEA_TOPIC, read_config(), search_client)


if __name__ == '__main__':
    process()
