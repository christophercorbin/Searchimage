from confluent_kafka import Consumer, KafkaError
import json
import logging
from config import Config
from services.event_handler import EventHandler
import traceback

class EventConsumer():   
    def __init__(self, topic, group, flow='quick'):
        self._configs = Config.get()
        self._logger = logging.getLogger(self._configs.LOGGER_NAME_EVENT_CONSUMER)
        client_config = {
            'bootstrap.servers': self._configs.EVENT_CONSUMER_SERVERS,
            'security.protocol': 'PLAINTEXT',
            'group.id': group,
            'enable.auto.offset.store': self._configs.EVENT_CONSUMER_ENABLE_AUTO_OFFSET_STORE,
            'max.poll.interval.ms': self._configs.EVENT_CONSUMER_MAX_POLL_INTERVAL_MS,
            'auto.offset.reset': 'earliest'}

        self._handler = EventHandler(flow)
        self._client = Consumer(client_config)
        self._client.subscribe([topic])
        self._logger.info(f'consumer created: {self._client} for topic: {topic}')

        try:
            while True:
                msg = self._client.poll(1.0) # timeout in seconds

                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        self._logger.error(f'consumer exited with error: {msg.error()}')
                        break
                
                if self._handler is not None:
                    self._handler.process(msg.value())

                    # manually stores offsets when message is handled, see https://protexxa.atlassian.net/browse/DEF-562?focusedCommentId=10953
                    if self._configs.EVENT_CONSUMER_ENABLE_AUTO_OFFSET_STORE is False:
                        self._client.store_offsets(msg)

        except Exception as e:
            trace = traceback.format_exc()
            self._logger.error(f'uncaught consumer exception: {e} - exiting with trace: "{trace}')
        finally:
            self._logger.info('graceful shutdown')
            self._handler.close()
            self._client.close()

    def close(self):
        self._handler.close()
        self._client.close()


def test_handler(msg):
    if msg is not None:
        print(msg)
        msg_value = json.loads(msg.decode('utf-8'))

        # Extract the values
        cognito_id = msg_value.get('cognitoId')
        fullname = msg_value.get('fullname')
        image = msg_value.get('image')
        print(f'cognitoId: {cognito_id}\nfullname: {fullname}\nimage: {image}')

if __name__ == '__main__':
    client = EventConsumer(test_handler)