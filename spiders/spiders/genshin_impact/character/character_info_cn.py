from typing import Dict
from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup

CHARACTER_LISTING_PAGE_URL = "https://wiki.biligame.com/ys/%E8%A7%92%E8%89%B2%E7%AD%9B%E9%80%89"
CHARACTER_PAGE_URL_PREFIX = "https://wiki.biligame.com"


def __get_character_listing_page() -> BeautifulSoup:
    """
    Returns a programmable representation of the character listing page.

    :return: a new instance
    :rtype: BeautifulSoup
    """
    return BeautifulSoup(requests.get(CHARACTER_LISTING_PAGE_URL).content, "html.parser")


def __get_character_pages(character_listing_page: BeautifulSoup) -> Dict[str, BeautifulSoup]:
    """
    Parses the given character listing page and returns a mapping from playable character Chinese name to their
    character page

    The output is in the following format::

        {
            ...
            "安柏": BeautifulSoup(...),
            "胡桃": BeautifulSoup(...),
            ...
        }

    .. attention:: This function incurs O(n) network I/O in order to fetch the character page remote sites

    :param character_listing_page: A programmable representation of the character listing page.
    :return: a new instance
    :rtype: Dict[str, BeautifulSoup]
    """
    return {
        character_name: BeautifulSoup(requests.get(url_map["biligameUrl"]).content, "html.parser")
        for character_name, url_map in __get_character_page_urls(character_listing_page).items()
    }


def __get_character_names(character_listing_page: BeautifulSoup) -> Dict[str, Dict[str, str]]:
    """
    Parses the given character listing page and returns all the Chinese names of playable characters

    The output is in the following format::

        {
            "安柏": {
                "nameCn": "安柏"
            },
            "胡桃": {
                "nameCn": "胡桃"
            },
            ...
        }

    Note that the Chinese name is keyed by "nameCn".

    :param character_listing_page:  A programmable representation of the character listing page.
    :return: a new instance
    :rtype: Dict[str, Dict[str, str]]
    """
    return {k: {"nameCn": k} for k, v in __get_character_page_urls(character_listing_page).items()}


def __get_character_page_urls(character_listing_page: BeautifulSoup) -> Dict[str, Dict[str, str]]:
    """
    Parses the given character listing page and returns a mapping from playable character Chinese name to their
    character page URL string.

    The output is in the following format::

        {
            "安柏": {
                "biligameUrl": "https://wiki.biligame.com/ys/%E5%AE%89%E6%9F%8F"
            },
            "胡桃": {
                "biligameUrl": "https://wiki.biligame.com/ys/%E8%83%A1%E6%A1%83"
            },
            ...
        }

    Note that the URL is keyed by "biligameUrl"

    :param character_listing_page:  A programmable representation of the character listing page.

    :return: a new instance
    :rtype: Dict[str, Dict[str, str]]
    """
    characters = character_listing_page.find(id="CardSelectTr").find("tbody").find_all("tr")
    characters.pop(0)

    character_page_urls: Dict[str, Dict[str, str]] = {}

    for character in characters:
        columns = character.find_all("td")

        character_name_cn = columns[1].get_text().strip()

        if columns[1].a:
            character_biligame_url = CHARACTER_PAGE_URL_PREFIX + columns[1].a.get('href')
            character_page_urls[character_name_cn] = {
                "biligameUrl": unquote(character_biligame_url)
            }

    return character_page_urls


def __get_identity_info_by_character(character_pages_by_name: Dict[str, BeautifulSoup]) -> Dict[str, Dict[str, str]]:
    """
    Returns a mapping from all playable character names (in Chinese) to their identity info map.

    The output is in the following format::

        {
            "安柏": {
                "titleCn": "飞行冠军",
                "visionCn": "火"
            },
            "胡桃": {
                "titleCn": "雪霁梅香",
                "visionCn": "火"
            },
            ...
        }

    :param character_pages_by_name:  A mapping from character's Chinese name to its character page

    :return: a new instance
    :rtype: Dict[str, Dict[str, str]]
    """
    return {
        character_name: __get_identity_info(character_page)
        for character_name, character_page in character_pages_by_name.items()
    }


def __get_identity_info(character_page: BeautifulSoup) -> Dict[str, str]:
    """
    Given a programmable character web page, extracts and returns descriptive information about a character, including

    - Chinese title (e.g. 逃跑的太阳)
    - Vision (e.g. 火)

    :return: a mapping of two key-value pairs. For example ``{titleCn: "逃跑的太阳", "visionCn": "火"}``
    :rtype: Dict[str, str]
    """
    all_wikitable_rows = character_page.select('table.wikitable tr')

    meta_info: Dict[str, str] = {}

    for row in all_wikitable_rows:
        if row.th and row.th.text and "称号" in row.th.text:
            meta_info["titleCn"] = row.td.get_text().strip()
        if row.th and row.th.text and "元素属性" in row.th.text:
            meta_info["visionCn"] = row.td.get_text().strip()[0]  # "水元素" -> "水"

    return meta_info


def _merge_by_dict_key(
        first_info_map: Dict[str, Dict[str, str]],
        second_info_map: Dict[str, Dict[str, str]]
) -> Dict[str, Dict[str, str]]:
    """
    Merges two 2-level-nested maps and returns a new map so that the keys of the new map is the superset of the two and
    the values are recursively grouped and merged by the aforementioned keys

    For example, merging::

        {
            "安柏": {
                "titleCn": "飞行冠军"
            },
            "胡桃": {
                "titleCn": "雪霁梅香"
            },
            ...
        }

    and::

        {
            "安柏": {
                "biligameUrl": "https://wiki.biligame.com/ys/%E5%AE%89%E6%9F%8F"
            },
            "胡桃": {
                "biligameUrl": "https://wiki.biligame.com/ys/%E8%83%A1%E6%A1%83"
            },
            ...
        }

    results in::

        {
            "安柏": {
                "titleCn": "飞行冠军",
                "biligameUrl": "https://wiki.biligame.com/ys/%E5%AE%89%E6%9F%8F"
            },
            "胡桃": {
                "titleCn": "雪霁梅香",
                "biligameUrl": "https://wiki.biligame.com/ys/%E8%83%A1%E6%A1%83"
            },
            ...
        }

    :param first_info_map:  A to-be-merged mapping from a character's Chinese name to another map of key-value pair
    attributes of that character
    :param second_info_map:  The other to-be-merged mapping from a character's Chinese name to another map of key-value
    pair attributes of that character
    :return: a new instance
    :rtype: Dict[str, Dict[str, str]]
    """
    key_superset = set(list(first_info_map.keys()) + list(second_info_map.keys()))

    merged_map = {}
    for key in key_superset:
        value_map = {}

        if key in first_info_map:
            for k, v in first_info_map[key].items():
                value_map[k] = v
        if key in second_info_map:
            for k, v in second_info_map[key].items():
                value_map[k] = v

        merged_map[key] = value_map

    return merged_map


def _get_character_info() -> Dict[str, Dict[str, str]]:
    """
    Returns a mapping of all Genshin Impact playable character Chinese names to their character info in Chinese

    The key of the map is a character's Chinese name and the value is a JSON object that contains their info in
    key-value pairs. For example::

        {
            ...
            "八重神子": {
                "nameCn": "八重神子",
                "titleCn": "浮世笑百姿",
                "biligameUrl": "https://wiki.biligame.com/ys/%E5%85%AB%E9%87%8D%E7%A5%9E%E5%AD%90"
            },
            "申鹤": {
                "nameCn": "申鹤",
                "titleCn": "孤辰茕怀",
                "biligameUrl": "https://wiki.biligame.com/ys/%E7%94%B3%E9%B9%A4"
            },
            ...
        }

    .. attention:: This function incurs O(n) Network I/O in order to fetch the character info from remote sites

    :return: a map where key is the Chinese name of character and value is another map of attributes of that character
    """

    # fetch network I/O only once
    character_listing_page = __get_character_listing_page()
    character_pages_by_name = __get_character_pages(character_listing_page)

    # character names
    character_names = __get_character_names(character_listing_page)

    # character info URL
    character_page_urls = __get_character_page_urls(character_listing_page)

    # character title
    character_titles = __get_identity_info_by_character(character_pages_by_name)

    return _merge_by_dict_key(
        _merge_by_dict_key(character_names, character_titles),
        character_page_urls
    )


if __name__ == "__main__":
    pass
