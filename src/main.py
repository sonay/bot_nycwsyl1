import logging
import sys

import requests


_logger = logging.getLogger(__name__)


NYT_MINI_GAME_URL = "https://www.nytimes.com/crosswords/game/mini"


def fetch_source():
    resp = requests.get(NYT_MINI_GAME_URL)
    resp.raise_for_status()
    return resp.text


def main():
    logging.basicConfig(filename='bot_nycwsyl1.log', format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
    if sys.version_info[0:3] != (3,8,7):
        _logger.warning("This app has only been tested for Python 3.9.7")

    try:
        page_src = fetch_source()
    except requests.HTTPError as e:
        _logger.critical(f"Could not get page source: {e}")
        return
    else:
        _logger.info("Success fetching page source.")


if __name__ == "__main__":
    main()
