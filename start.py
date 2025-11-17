import logging
import argparse
from config import Config
import traceback
import signal

# Get arguments
parser = argparse.ArgumentParser(description="Set the environment.")
parser.add_argument('--env', type=str, default='dev', choices=['dev', 'stage', 'prod', 'prod-1445', 'test'], help='Environment: "stage" or "prod"')
parser.add_argument('--flow', type=str, default='quick', choices=['quick', 'full'], help='Run flow: "quick" or "full"')
args = parser.parse_args()

# Set up configurations according to the environment specified
# IMPORTANT: this must be called before import any other application modules so they all have the same environment applied
configs = Config.get(args.env)

# Set up logging
logger = logging.getLogger(configs.LOGGER_NAME)
logger.setLevel(configs.LOGGER_LEVEL)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logHandler = logging.StreamHandler()
logHandler.setFormatter(formatter)
logHandler.setLevel(configs.LOGGER_LEVEL)
logger.addHandler(logHandler)
logger.info(f"###### Starting DME-Searcher in env: {args.env} running flow: {args.flow} ######")

def print_ephemeral_port_range():
    with open('/proc/sys/net/ipv4/ip_local_port_range', 'r') as file:
        port_range = file.read().strip()
        print(f"Ephemeral port range: {port_range}")

print_ephemeral_port_range()

# Import the application modules after configs and logger are loaded
from clients.event_consumer import  EventConsumer

# Start the event consumer in an infinite loop
try:
    if args.flow != 'quick':
      consumer = EventConsumer(configs.EVENT_TOPIC_DME_SEARCHER_FULL, configs.EVENT_CONSUMER_GROUP_DME_SEARCHER_FULL_ID, 'full')
    else:
      consumer = EventConsumer(configs.EVENT_TOPIC_DME_SEARCHER_QUICK, configs.EVENT_CONSUMER_GROUP_DME_SEARCHER_QUICK_ID, 'quick')
except Exception as e:
  # log the exception and trace for cloudwatch to pickup
  trace = traceback.format_exc()
  logger.error(f'###### Aborting DME-Searcher in env: {args.env} due to unhandled exception: "{e}", with trace: "{trace}"')

def sigterm_handler(_signo, _stack_frame):
    logger.info('Received SIGTERM signal, exiting')
    if consumer is not None:
      consumer.close()
    exit(0)

signal.signal(signal.SIGTERM, sigterm_handler)