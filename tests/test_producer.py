'''
PYTHONPATH=$PYTHONPATH:/home/ubuntu/data-mining-engine
export PYTHONPATH
'''
from confluent_kafka import Producer
import socket
from config import Config
import json
from datetime import datetime

configs = Config.get()

conf = {'bootstrap.servers': configs.EVENT_CONSUMER_SERVERS,
        'security.protocol': 'PLAINTEXT',
        'client.id': socket.gethostname()}
topic = configs.EVENT_TOPIC_DME_SEARCHER_QUICK
print(f'publishing to topic: {topic}')
producer = Producer(conf)

def acked(err, msg):
    if err is not None:
        print("Failed to deliver message: %s: %s" % (str(msg), str(err)))
    else:
        print("Message produced: %s" % (str(msg)))

# payload will be a json string consists of the current time in ISO format, nothing else
payload_dict = {
            'scanId': '789',
            'clientId': 'protexxa',
            'userId': '789',
            'names': ['Mary Sattler Peltola'],
            'companies': ['U.S. REPRESENTATIVE'],
            'images': ['https://peltola.house.gov/uploadedphotos/highresolution/56440a66-676c-41c0-8767-8b7bc549ac6d.jpg']
        }

payload = json.dumps(payload_dict)

producer.produce(topic, value=payload, callback=acked)
producer.flush()