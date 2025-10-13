from rq import Worker
from core.database import redis_client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info('Starting RQ worker...')
    worker = Worker(['default'], connection=redis_client)
    worker.work()
