import logging

logging.basicConfig(
    format="%(asctime)23s | %(levelname)-8s| %(name)-30s| %(message)s",
    level=logging.INFO,
    filename="general.log",
    filemode="w",
)
logger = logging.getLogger(__name__)
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
logger.setLevel(logging.INFO)
