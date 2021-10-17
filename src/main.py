import logging
import sys
from collections import namedtuple, defaultdict
import json
import re

import requests
import bs4


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


class MiniGameJsonSerializer:
    def __init__(self, game):
        if not isinstance(game, MiniGame):
            raise Exception("This class can only serialize MiniGame instances")
        self.game = game

    def serialize(self, file):
        tmp = []
        for group in MiniGame.GROUPS:
            clues = self.game.clues(group)
            for clue in clues:
                tmp.append({
                    "Group": group,
                    "Number": clue.number,
                    "String": clue.string
                })
        return json.dump(tmp, file)


class MiniGameParser:
    """
    A fail-fast parser, that assumes the page source contains
    two <div> wrappers for each group "Across" and "Down".
    Inside each <div> wrapper a <h3> for the title of the group,
    i.e. "Across" or "Down", and an <ol> for the Clue List that
    contains <li> wrappers for the number and string <span>s.

    Each assumption is meticulously checked for correctness.
    A violation of an assumption causes a ParserException to be
    raised and parser stops processing further.
    """
    GROUP_WRAPPER_TAG = "div"
    GROUP_WRAPPER_CLASS_MATCHER = re.compile('^ClueList-wrapper')

    GROUP_TITLE_TAG = "h3"
    GROUP_TITLE_CLASS_MATCHER = re.compile('^ClueList-title')

    CLUE_LIST_TAG = "ol"
    CLUE_LIST_CLASS_MATCHER = re.compile("^ClueList-list")

    CLUE_TAG = "li"
    CLUE_CLASS_MATCHER = re.compile("^Clue-li")

    CLUE_NUMBER_TAG = "span"
    CLUE_NUMBER_CLASS_MATCHER = re.compile("^Clue-label")

    CLUE_STRING_TAG = "span"
    CLUE_STRING_CLASS_MATCHER = re.compile("^Clue-text")

    def __init__(self, src):
        if not src:
            raise ValueError("Page source can not be None.")
        self.src = src

    def parse(self):
        soup = bs4.BeautifulSoup(self.src, 'lxml-xml')
        game = MiniGame()
        wrapper_tags = self._group_wrapper_tags(soup)
        for wrapperTag in wrapper_tags:
            group_tag = self._group_tag(wrapperTag)
            game.set_group(str(group_tag.string), self._clues(wrapperTag))
        return game

    def _group_wrapper_tags(self, page_soup):
        wrappers = page_soup.find_all(self.GROUP_WRAPPER_TAG,
                                      class_=self.GROUP_WRAPPER_CLASS_MATCHER)
        if len(wrappers) != len(MiniGame.GROUPS):
            raise ParserException(f"Expected {len(MiniGame.GROUPS)} group wrapper tags, found: {len(wrappers)}.")
        return wrappers

    def _group_tag(self, wrapper_tag):
        groups = wrapper_tag.find_all(self.GROUP_TITLE_TAG,
                                      class_=self.GROUP_TITLE_CLASS_MATCHER,
                                      recursive=False)
        if len(groups) != 1:
            raise ParserException(f"Expected 1 group title tag, found: {len(groups)}.")

        group = groups[0]
        if group.string not in MiniGame.GROUPS:
            raise ParserException(f"Unexpected group value in group title: {group.string}.")
        return group

    def _clues(self, wrapper_tag):
        clue_list_tags = wrapper_tag.find_all(self.CLUE_LIST_TAG,
                                              class_=self.CLUE_LIST_CLASS_MATCHER,
                                              recursive=False)
        if len(clue_list_tags) != 1:
            raise ParserException(f"Expected 1 clue list tag, found: {len(clue_list_tags)}.")

        clue_tags = clue_list_tags[0].find_all(self.CLUE_TAG,
                                               class_=self.CLUE_CLASS_MATCHER,
                                               recursive=False)
        if not clue_tags:
            raise ParserException(f"Did not find any clue tags in clue list.")

        return self._parsed_clues(clue_tags)

    def _parsed_clues(self, clue_tags):
        clues = []
        for clue_tag in clue_tags:
            number_tags = clue_tag.find_all(self.CLUE_NUMBER_TAG,
                                            class_=self.CLUE_NUMBER_CLASS_MATCHER,
                                            recursive=False)
            if len(number_tags) != 1:
                raise ParserException(f"Expected 1 clue label (number) tag, found: {len(number_tags)}.")

            number = str(number_tags[0].string).strip()
            try:
                number = int(number)
            except ValueError:
                raise ParserException(f"Expected a number value for clue label, found: {number}.")

            string_tags = clue_tag.find_all(self.CLUE_STRING_TAG,
                                            class_=self.CLUE_STRING_CLASS_MATCHER,
                                            recursive=False)
            if len(string_tags) != 1:
                raise ParserException(f"Expected 1 clue text (string) tag, found: {len(string_tags)}.")
            string = str(string_tags[0].string)

            clues.append(Clue(number, string))

        return clues


class ParserException(Exception):
    def __init__(self, message):
        self.__init__(message)


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

    try:
        game = MiniGameParser(page_src).parse()
    except ParserException as e:
        _logger.critical(f"Error while parsing page source:{e}")
        return


if __name__ == "__main__":
    main()
