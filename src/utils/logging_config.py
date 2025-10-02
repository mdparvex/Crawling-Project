
import logging
from src.utils.mongo_logging import MongoHandler
LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

# Add MongoDB handler for persistent logging
mongo_handler = MongoHandler()
mongo_handler.setLevel(logging.INFO)
formatter = logging.Formatter(LOG_FORMAT)
mongo_handler.setFormatter(formatter)
logging.getLogger().addHandler(mongo_handler)
