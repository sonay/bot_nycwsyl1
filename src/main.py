import logging
import sys
from collections import namedtuple, defaultdict

import requests


_logger = logging.getLogger(__name__)


NYT_MINI_GAME_URL = "https://www.nytimes.com/crosswords/game/mini"


def fetch_source():
    resp = requests.get(NYT_MINI_GAME_URL)
    resp.raise_for_status()
    return resp.text


Clue = namedtuple('Clue', ['number', 'string'])


class MiniGame:
    GROUPS = ["Across", "Down"]

    def __init__(self):
        self._groups = defaultdict(list)

    def _check_group(self, group):
        if group not in self.GROUPS:
            raise ValueError(f"Illegal group value: {group}")
        return group

    def add_clue(self, group, clue):
        self._check_group(group)
        self._groups[group].append(clue)

    def add_clues(self, group, clues):
        self._check_group(group)
        self._groups[group].extend(clues)

    def set_group(self, group, clues):
        self._check_group(group)
        # defensive copy
        self._groups[group] = clues[:]

    def clues(self, group):
        self._check_group(group)
        # defensive copy
        return list(self._groups[group])


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
