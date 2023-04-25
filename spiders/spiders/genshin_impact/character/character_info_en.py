from typing import Dict

import requests
from bs4 import BeautifulSoup

from peitho_data.genshin_impact.character.character_info_cn import _merge_by_dict_key

WIKI_CHARACTER_LIST_PAGE_URL = "https://genshin-impact.fandom.com/wiki/Characters"
WIKI_CHARACTER_PAGE_URL_PREFIX = "https://genshin-impact.fandom.com"


def __get_character_listing_page() -> BeautifulSoup:
    """
    Returns a programmable representation of a English page listing all playable Genshin Impact characters with links
    to each character's page.

    :return: a
    """
    url = WIKI_CHARACTER_LIST_PAGE_URL
    return BeautifulSoup(requests.get(url).content, "html.parser")


def __get_character_pages(character_listing_page: BeautifulSoup) -> Dict[str, BeautifulSoup]:
    """
    Parses the given character listing page and returns a mapping from playable character English name to their
    character page

    The output is in the following format::

        {
            ...
            "Amber": BeautifulSoup(...),
            "Hu Tao": BeautifulSoup(...),
            ...
        }

    .. attention:: This function incurs O(n) network I/O in order to fetch the character page remote sites

    :param character_listing_page: A programmable representation of the character listing page.
    :return: a new instance
    :rtype: Dict[str, BeautifulSoup]
    """
    return {
        character_name: BeautifulSoup(requests.get(url_map["fandomUrl"]).content, "html.parser")
        for character_name, url_map in __get_character_page_urls(character_listing_page).items()
    }


def __get_character_names(character_listing_page: BeautifulSoup) -> Dict[str, Dict[str, str]]:
    """
    Parses the given character listing page and returns all the English names of playable characters

    The output is in the following format::

        {
            "Amber": {
                "nameEn": "Amber"
            },
            "Hu Tao": {
                "nameEn": "Hu Tao"
            },
            ...
        }

    Note that the English name is keyed by "nameEn".

    :param character_listing_page:  A programmable representation of the character listing page.
    :return: a new instance
    :rtype: Dict[str, Dict[str, str]]
    """
    return {name: {"nameEn": name} for name in __get_character_page_urls(character_listing_page).keys()}


def __get_character_page_urls(character_listing_page: BeautifulSoup) -> Dict[str, Dict[str, str]]:
    """
    Parses the given character listing page and returns a mapping from playable character English name to their
    character page URL string.

    The output is in the following format::

        {
            "Amber": {
                "fandomUrl": "https://genshin-impact.fandom.com/wiki/Amber"
            },
            "Hu Tao": {
                "fandomUrl": "https://genshin-impact.fandom.com/wiki/Hu_Tao"
            },
            ...
        }

    Note that the URL is keyed by "fandomUrl"

    :param character_listing_page:  A programmable representation of the character listing page.

    :return: a new instance
    :rtype: Dict[str, Dict[str, str]]
    """
    tables = character_listing_page.find_all("table", {"class": "article-table sortable alternating-colors-table"})

    character_page_urls = {}

    for table in tables:
        characters = table.find("tbody").find_all("tr")
        characters.pop(0)

        for character in characters:
            columns = character.find_all("td")

            character_name_en = columns[1].get_text().strip()

            if columns[1].a:
                character_fandom_url = "https://genshin-impact.fandom.com" + columns[1].a.get('href')

                character_page_urls[character_name_en] = {
                    "fandomUrl": character_fandom_url
                }

        break  # only the first table contains the character finalized character page structure so we could safely parse

    return character_page_urls


def __get_character_metadata(character_pages_by_name: Dict[str, BeautifulSoup]) -> Dict[str, Dict[str, str]]:
    """
    Returns a mapping from all playable character names (in English) to their metadata, usch as English title and
    release date.

    The output is in the following format::

        {
            "Amber": {
                "titleCn": "Gliding Champion"
            },
            "Hu Tao": {
                "titleCn": "Fragrance in Thaw"
            },
            ...
        }

    :param character_pages_by_name:  A mapping from character's English name to its character page, from which the title
    can be parsed and fetched

    :return: a new instance
    :rtype: Dict[str, Dict[str, str]]
    """
    return {
        character_name: {
            "titleEn": __get_character_title(character_page),
            "releaseDate": __get_character_release_date(character_page)
        }
        for character_name, character_page in character_pages_by_name.items()
    }


def __get_character_title(character_page: BeautifulSoup) -> str:
    """
    Given a programmable character page, extracts and returns the English title of that character.

    :return: an English phrase
    :rtype: str
    """
    return character_page.find('h2', attrs={'data-item-name': "secondary_title"}).get_text()


def __get_character_release_date(character_page: BeautifulSoup) -> str:
    """
    Given a programmable character page, extracts and returns the release date of that character.

    :return: an English phrase
    :rtype: str
    """
    return character_page.find(
        "div",
        attrs={"data-source": "releaseDate"}
    ).div.get_text(strip=True, separator="\n").splitlines()[0]


def __get_character_names_cn(character_pages_by_name: Dict[str, BeautifulSoup]) -> Dict[str, str]:
    """
     Returns a mapping from all playable characters to their Chinese name.

     The output is in the following format::

         {
            ...
             "Amber": "安柏",
             "Hu Tao": "胡桃",
             ...
         }

     :param character_pages_by_name:  A mapping from character's English name to its character page, from which the
     title can be parsed and fetched

     :return: a new instance
     :rtype: Dict[str, Dict[str, str]]
     """
    return {
        character_name: __get_character_name_cn(character_page)
        for character_name, character_page in character_pages_by_name.items()
    }


def __get_character_name_cn(character_page: BeautifulSoup) -> str:
    """
    Given a programmable character page, extracts and returns the Chinese name of that character.

    :return: a Chinese phrase
    :rtype: str
    """
    return character_page.find('span', attrs={'lang': "zh-Hans"}).get_text()


def _get_character_info() -> Dict[str, Dict[str, str]]:
    """
    Returns a mapping of all Genshin Impact playable character Chinese names to their character info in English

    The key of the map is a character's Chinese name and the value is a JSON object that contains their info in
    key-value pairs. For example::

        {
            ...
            "八重神子": {
                "nameEn": "Yae Miko",
                "titleEn": "Astute Amusement",
                "fandomUrl": "https://genshin-impact.fandom.com/wiki/Yae_Miko"
            },
            "申鹤": {
                "nameEn": "Shenhe",
                "titleEn": "Lonesome Transcendence",
                "fandomUrl": "https://genshin-impact.fandom.com/wiki/Shenhe"
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

    # character title, release dates, etc
    character_metadata = __get_character_metadata(character_pages_by_name)

    # character Chinese name: en -> cn
    character_names_cn = __get_character_names_cn(character_pages_by_name)

    character_info_with_en_name_key = _merge_by_dict_key(
        _merge_by_dict_key(character_names, character_metadata),
        character_page_urls
    )

    character_info_with_cn_name_key = {}

    for name_en, character_info in character_info_with_en_name_key.items():
        name_cn = character_names_cn[name_en]

        character_info_with_cn_name_key[name_cn] = character_info

    return character_info_with_cn_name_key


if __name__ == "__main__":
    pass
