import calendar
import datetime
import json
import sys
import time
from collections import defaultdict

from peitho_data.genshin_impact.character.character_info_cn import _get_character_info as get_character_info_cn
from peitho_data.genshin_impact.character.character_info_cn import _merge_by_dict_key
from peitho_data.genshin_impact.character.character_info_en import _get_character_info as get_character_info_en

RELEASE_DATE: str = "releaseDate"
__MONTH_NAME_TO_NUM: dict[str, int] = {month: index for index, month in enumerate(calendar.month_name) if month}


def __group_by_release_date_stamp(character_info_map: dict[str, dict]) -> dict[int, list[dict]]:
    """
    Regroups the return value of get_character_info_map() by character's release date.

    :param character_info_map:  The exact return value of get_character_info_map(), i.e. a mapping from character name
    to character info
    :return:  A mapping from character release date to a list of characters released on that same date
    """
    new_dict = defaultdict(list)

    for character in character_info_map.values():
        new_dict[get_character_release_date_stamp(character)].append(character)

    return new_dict


def __sort_by_character_name_cn(characters: list[dict]) -> list[dict]:
    """
    Orders a list of characters by character's Chinese name in ascending order and returns them as a new list.

    :param characters: a list of characters, each of which is represented by a dict of character info
    :return: the list with the same content but order changed to reflect character's name in ascending order
    """
    return sorted(characters, key=lambda character: character["nameCn"])


def __convert_to_local_unix_date_tamp(date_string: str) -> int:
    """
    Converts a date string of the form "month_name day_number, year" (e.g. "September 28, 2022") to a UNIX timestamp at
    local timezone.

    For example, "September 28, 2022" gets converted to 1664294400 as an integer.

    Note that this function ignores any granularity down below hours (including hours), such as minutes, and will set
    those all to 0 during conversion

    :param date_string:  A text date, such as September 28, 2022"
    :return: a number in local time as seconds since the Epoch
    """
    return int(
        time.mktime(
            datetime.datetime(
                int(date_string.split()[2]),                       # year
                int(__MONTH_NAME_TO_NUM[date_string.split()[0]]),  # month
                int(date_string.split()[1][:-1])                   # day
            ).timetuple()
        ).real
    )


def get_character_release_date_stamp(character: dict) -> int:
    """
    Given a playable character, represented by a dict of this character's info, returns a local-time UNIX timestamp of
    the release date (not date time) of this character

    For example, when character is

        {
            "nameCn": "安柏",
            "titleCn": "飞行冠军",
            "visionCn": "火",
            "biligameUrl": "https://wiki.biligame.com/ys/安柏",
            "nameEn": "Amber",
            "titleEn": "Gliding Champion",
            "releaseDate": "September 28, 2020",
            "fandomUrl": "https://genshin-impact.fandom.com/wiki/Amber"
        }

    This function returns 1664294400 which represents "Wed Sep 28 2022 00:00:00 GMT+0800 (China Standard Time)" if this
    function is called at GMT+0800 zone.

    If a character does not have a release date (because the character has been announced but not released yet), this
    function returns the max integer calculated by :py:meth:`sys.maxsize`. For example, if character is

        {
            "nameCn": "莱依拉",
            "titleCn": "绮思晚星",
            "visionCn": "冰",
            "biligameUrl": "https://wiki.biligame.com/ys/莱依拉"
        }

    then 9223372036854775807 is returned which is :py:meth:`sys.maxsize`

    :param character:  The character whose release date is to be UNIX-timestamped
    :return: a UNIX timestamp at local timezone or :py:meth:`sys.maxsize` if the character has not been released yet
    """
    return __convert_to_local_unix_date_tamp(character[RELEASE_DATE]) if RELEASE_DATE in character else sys.maxsize


def get_character_info_map() -> dict[str, dict]:
    """
    Returns a mapping of all Genshin Impact playable character Chinese names to their character info, with each
    attribute having both Chinese and English version.

    The key of the map is a character's Chinese name and the value is a JSON object that contains their info in
    key-value pairs. For example::

        {
            ...
            "八重神子": {
                "nameCn": "八重神子",
                "titleCn": "浮世笑百姿",
                "biligameUrl": "https://wiki.biligame.com/ys/八重神子",
                "nameEn": "Yae Miko",
                "titleEn": "Astute Amusement",
                "fandomUrl": "https://genshin-impact.fandom.com/wiki/Yae_Miko",
                "releaseDate": "February 16, 2022"
            },
            "申鹤": {
                "nameCn": "申鹤",
                "titleCn": "孤辰茕怀",
                "biligameUrl": "https://wiki.biligame.com/ys/申鹤",
                "nameEn": "Shenhe",
                "titleEn": "Lonesome Transcendence",
                "fandomUrl": "https://genshin-impact.fandom.com/wiki/Shenhe",
                "releaseDate": "January 05, 2022"
            },
            ...
        }

    .. attention:: This function incurs O(n) network I/O in order to fetch each of the character info from remote sites

    :return: a map where key is the Chinese name of character and value is another map of attributes of that character
    :rtype: Dict[str, Dict[str, str]]
    """
    return _merge_by_dict_key(get_character_info_cn(), get_character_info_en())


def get_character_info_json() -> str:
    """
    Returns a JSON list of all Genshin Impact playable character info.

    The JSON is in the following format::

        [
            ...
            {
                "nameCn": "申鹤",
                "titleCn": "孤辰茕怀",
                "biligameUrl": "https://wiki.biligame.com/ys/申鹤",
                "nameEn": "Shenhe",
                "titleEn": "Lonesome Transcendence",
                "fandomUrl": "https://genshin-impact.fandom.com/wiki/Shenhe",
                "releaseDate": "January 05, 2022"
            },
            {
                "nameCn": "八重神子",
                "titleCn": "浮世笑百姿",
                "biligameUrl": "https://wiki.biligame.com/ys/八重神子",
                "nameEn": "Yae Miko",
                "titleEn": "Astute Amusement",
                "fandomUrl": "https://genshin-impact.fandom.com/wiki/Yae_Miko",
                "releaseDate": "February 16, 2022"
            }
            ...
        ]

    .. attention:: This function incurs O(n) network I/O in order to fetch the character info from remote sites

    :return: a formatted (4-space-indentation) JSON string with Chinese/Korean/Japanese character properly rendered
    """
    release_date_stamp_to_characters: dict[int, list[dict]] = __group_by_release_date_stamp(get_character_info_map())

    for date_stamp, characters in release_date_stamp_to_characters.items():
        release_date_stamp_to_characters[date_stamp] = __sort_by_character_name_cn(characters)

    release_date_stamps_in_order: list = list(release_date_stamp_to_characters.keys())
    release_date_stamps_in_order.sort()

    ordered_character_list: list[dict] = []
    for idx in range(len(release_date_stamps_in_order)):
        release_timestamp = release_date_stamps_in_order[idx]
        characters_with_same_release_date = release_date_stamp_to_characters[release_timestamp]
        ordered_character_list.extend(characters_with_same_release_date)

    return json.dumps(ordered_character_list, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    pass
