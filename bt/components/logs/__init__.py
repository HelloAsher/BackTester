import logging

logging.basicConfig(format="%(levelname)s: %(asctime)s %(filename)s line-%(lineno)d:  %(message)s",
                    datefmt="%H:%M:%S")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
