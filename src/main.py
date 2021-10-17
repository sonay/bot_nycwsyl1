import logging
import sys

_logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(filename='bot_nycwsyl1.log', format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
    if sys.version_info[0:3] != (3,8,7):
        _logger.warning("This app has only been tested for Python 3.9.7")


if __name__ == "__main__":
    main()
