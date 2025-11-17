'''
PYTHONPATH=$PYTHONPATH:/home/ec2-user/defender-be-image-reverse-search
export PYTHONPATH
'''

from confluent_kafka import Producer
from config import Config
import socket
import logging

class EventProducer():
    def __init__(self):
        self._configs = Config.get()
        self._logger = logging.getLogger(self._configs.LOGGER_NAME_EVENT_PRODUCER)
        self._conf = {'bootstrap.servers': self._configs.EVENT_CONSUMER_SERVERS,
                'security.protocol': 'PLAINTEXT',
                'client.id': socket.gethostname()}
        self._producer = Producer(self._conf)

    def _acked(self, err, msg):
        if err:
            self._logger.error("Failed to deliver message: %s: %s" % (str(msg), str(err)))

    def produce(self, topic, payload, key):
        self._producer.produce(topic, value=payload, key=key, callback=self._acked)
        self._producer.flush()
