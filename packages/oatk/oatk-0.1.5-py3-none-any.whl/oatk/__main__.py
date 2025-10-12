import logging

import os

from fire import Fire
from oatk import OAuthToolkit

# load the environment variables for this setup
from dotenv import load_dotenv, find_dotenv

logger = logging.getLogger(__name__)
load_dotenv(find_dotenv(usecwd=True))

LOG_LEVEL = os.environ.get("LOG_LEVEL") or "INFO"

# setup logging infrastructure

logging.getLogger("urllib3").setLevel(logging.WARN)

FORMAT  = "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"
DATEFMT = "%Y-%m-%d %H:%M:%S %z"

logging.basicConfig(level=LOG_LEVEL, format=FORMAT, datefmt=DATEFMT)
formatter = logging.Formatter(FORMAT, DATEFMT)
logging.getLogger().handlers[0].setFormatter(formatter)

def cli():
  Fire(OAuthToolkit, name="oatk")

if __name__ == '__main__':
  cli()
