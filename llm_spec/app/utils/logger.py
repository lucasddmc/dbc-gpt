import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("dbc_gpt.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("dbc_gpt")