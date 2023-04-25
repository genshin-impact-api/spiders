import json
import os
from typing import Dict
from typing import List
from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup

ENEMY_PAGE_URL_PREFIX = "https://wiki.biligame.com"
BILI_GAME_SPIRAL_ABYSS_ENEMY_LISTING_PAGE_URL = "https://wiki.biligame.com/ys/渊月螺旋"


def __get_enemy_levels_in_order(all_current_period_wikitable_rows: list) -> List[int]:
    """
    Given an ordered list of wiki table rows (coming from multiple wiki tables together), extract cell value (td) whose
    header (th) is "enemy level (怪物等级)" and returns a list of 12 ordered elements representing the enemy levels of
    each ordered chamber.

    The part

    .. code-block:: html

        <tr>
            <th>怪物等级</th>
            <td>
                <center>Lv.72</center>
            </td>
        </tr>

    is extracted and used for the enemy level info from the following example HTML structure

    .. image:: ../img/get_enemy_levels_in_order.png
        :align: center

    In this case, the returned value is `['72', '74', '76', '80', '82', '85', '88', '90', '92', '95', '98', '100']`,
    it means the enemy levels for the current period are

    - floor 9

      - chamber 1: Lv.72
      - chamber 2: Lv.74
      - chamber 3: Lv.76

    - floor 10

      - chamber 1: Lv.80
      - chamber 2: Lv.82
      - chamber 3: Lv.85

    - floor 11

      - chamber 1: Lv.88
      - chamber 2: Lv.90
      - chamber 3: Lv.92

    - floor 12

      - chamber 1: Lv.95
      - chamber 2: Lv.98
      - chamber 3: Lv.100

    Note that the values in the returned list are guaranteed to be in non-decreasing order, signifying that enemies
    become stronger as we go deeper into the spiral chambers/floors.

    :param all_current_period_wikitable_rows:  A list of wiki table rows that contain ordered enemy levels
    :return: a new list
    """
    ordered_enemy_levels = []

    for row in all_current_period_wikitable_rows:
        if row.th and "怪物等级" in row.th.get_text():
            # split so that "Lv.95" becomes "95"
            ordered_enemy_levels.append(int(row.td.center.get_text().split(".")[1]))

    return ordered_enemy_levels


def __get_halves_in_order(half: str, all_current_period_wikitable_rows: list) -> list:
    """
    Given an ordered list of wiki table rows (coming from multiple wiki tables together), extract cell (td) that
    contains enemy info of a specified half-round (上半/下半) challenge.

    For example, the <td> of the element

    .. code-block:: html

        <th style="width:80px">上半</th>
            <td>
                <b>第一波：</b><br>
                ...

    is extracted and used for the enemy info from the following example HTML structure

    .. image:: ../img/get_enemy_levels_in_order.png
        :align: center

    In this case, the returned value is a list of 12 elements, each of which is an HTML <td> element of, for example,
    the form

    .. image:: ../img/get_halves_in_order.png
        :align: center


    :param half:  The name of the half-round. Can only be either "上半" or "下半" （without double quotes）
    :param all_current_period_wikitable_rows:  A list of wiki table rows that contain all halves <td> elements in
           order (i.e. from floor 9 to 12, each of which from chamber 1 to 3)
    :return: a new list
    """
    ordered_first_halves = []

    for row in all_current_period_wikitable_rows:
        # - "row.td" below is there because "visible-md", "visible-sm", "visible-lg" versions of div tables have
        #   different rendering of row.td from "visible-xs".
        # - We are parsing based on visible-xs
        # - Duplicates will be removed later
        if row.th and half in row.th.get_text() and row.td:
            ordered_first_halves.append(row.td)

    return ordered_first_halves


def __deduplicated_enemy_info(enemy_info: List[Dict[str, str]]):
    """
    Removes duplicates from a list of enemy info.

    For example::

        [
            {
                "nameCn": "大型水史莱姆",
                "biligameUrl": "..."
            },
            {
                "nameCn": "雷箭丘丘人",
                "biligameUrl": "..."
            },
            {
                "nameCn": "大型水史莱姆",
                "biligameUrl": "..."
            }
        ]

    becomes::

        [
            {
                "nameCn": "大型水史莱姆",
                "biligameUrl": "..."
            },
            {
                "nameCn": "雷箭丘丘人",
                "biligameUrl": "..."
            }
        ]

    :param enemy_info: the list to be deduplicated
    :return: a new list without duplicates
    """
    existing_name_cn = set()

    deduplicated_enemy_info: List[Dict[str, str]] = []

    for info in enemy_info:
        if info["nameCn"] not in existing_name_cn:
            deduplicated_enemy_info.append(info)
            existing_name_cn.add(info["nameCn"])

    return deduplicated_enemy_info


def __extract_enemy_info(single_half) -> List[Dict[str, str]]:
    """
    Extracts enemy info from a half-cell (<td> HTML element) of the form

    .. image:: ../img/extract_enemy_info.png
        :align: center

    The function iterates through all HTML links (<a> elements), picks up the links in which the ``title`` attribute
    value equals the link text, and extracts the enemy infor from that link. For each link, an enemy info will be
    constructed in the form of::

        {
            "nameCn": a.title,
            biligameUrl": prefix + a.href
        }

    where ``prefix`` is the Biligame site URL.

    For example, this link will be picked up during the iterations, because both ``title`` and link text are
    "风丘丘萨满":

    .. code-block:: html

        <a href="/ys/风丘丘萨满" title="风丘丘萨满">
            风丘丘萨满
        </a>

    :param single_half:  An <td> HTML structure that contains information of a half-round enemies info
    :return: a new list of enemy info object extracted from the <td> element
    """
    enemy_info = []

    for link in single_half.find_all('a'):
        if link.get("title") == link.get_text():
            enemy_info.append(
                {
                    "nameCn": link.get("title"),
                    "biligameUrl": unquote(ENEMY_PAGE_URL_PREFIX + link.get("href"))
                }
            )

    deduplicated_enemy_info = __deduplicated_enemy_info(enemy_info)

    return deduplicated_enemy_info


def __get_all_wikitable_rows_by_period_id(period_page: BeautifulSoup, period_id: str):
    """
    Given the Biligame wiki Spiral Abyss page, returns all wikitable rows (<tr>) (HTML class: wikitable) of a specified
    period.

    The period to parse is determined by a
    `"period ID"
    <https://peitho-data.readthedocs.io/en/latest/genshin_impact/spiral_abyss_internal.html#period-analysis-config>`_

    :param period_page:  A programmable object modeling the Biligame wiki Spiral Abyss page
    :param period_id:  An unique identifier telling which period will have its wiki table rows returned

    :return: a list of <tr> HTML elements
    """
    floors = period_page.find("span", {"id": period_id}).find_all_next("div", class_="visible-xs", limit=4)

    nested_tables = [floor.findChildren("table", {"class": "wikitable"}) for floor in floors]
    tables = [item for sublist in nested_tables for item in sublist]

    nested_rows = [table.findChildren('tr') for table in tables]
    return [item for sublist in nested_rows for item in sublist]


def __get_period_info(period_id: str) -> Dict:
    """
    Returns enemy listings of a specified period of Abyssal Moon Spire (Floors 9–12)

    The data is returned in JSON format of the following pattern

    .. image:: ../img/get_period_info.png
        :align: center

    The approach is to get all table rows and take **the assumption that the order of the row indicates the natural
    ordering of the floor/chamber as well**. For example, infor of floor 10 will take the position after that of floor
    9 and chamber 3 info always appears after chamber 1

    :param period_id:  An unique identifier telling which period will have its wiki table rows returned

    :return: a new dict
    """
    period_page = BeautifulSoup(requests.get(BILI_GAME_SPIRAL_ABYSS_ENEMY_LISTING_PAGE_URL).content, "html.parser")

    all_wikitable_rows = __get_all_wikitable_rows_by_period_id(period_page, period_id)

    first_halves_in_order: list = __get_halves_in_order("上半", all_wikitable_rows)
    second_halves_in_order: list = __get_halves_in_order("下半", all_wikitable_rows)

    # 12-element lists - each element corresponds to a half
    first_halves_enemy_info_in_order: list = [
        __extract_enemy_info(single_half) for single_half in first_halves_in_order
    ]
    second_halves_enemy_info_in_order: list = [
        __extract_enemy_info(single_half) for single_half in second_halves_in_order
    ]
    enemy_levels_in_order: list = __get_enemy_levels_in_order(all_wikitable_rows)

    period_info = {}

    period_info["floor9"] = {
        "chamber1": {
            "enemyLevel": enemy_levels_in_order[0],
            "firstHalf": {
                "enemies": first_halves_enemy_info_in_order[0]
            },
            "secondHalf": {
                "enemies": second_halves_enemy_info_in_order[0]
            },
        },
        "chamber2": {
            "enemyLevel": enemy_levels_in_order[1],
            "firstHalf": {
                "enemies": first_halves_enemy_info_in_order[1]
            },
            "secondHalf": {
                "enemies": second_halves_enemy_info_in_order[1]
            },
        },
        "chamber3": {
            "enemyLevel": enemy_levels_in_order[2],
            "firstHalf": {
                "enemies": first_halves_enemy_info_in_order[2]
            },
            "secondHalf": {
                "enemies": second_halves_enemy_info_in_order[2]
            },
        }
    }

    period_info["floor10"] = {
        "chamber1": {
            "enemyLevel": enemy_levels_in_order[3],
            "firstHalf": {
                "enemies": first_halves_enemy_info_in_order[3]
            },
            "secondHalf": {
                "enemies": second_halves_enemy_info_in_order[3]
            },
        },
        "chamber2": {
            "enemyLevel": enemy_levels_in_order[4],
            "firstHalf": {
                "enemies": first_halves_enemy_info_in_order[4]
            },
            "secondHalf": {
                "enemies": second_halves_enemy_info_in_order[4]
            },
        },
        "chamber3": {
            "enemyLevel": enemy_levels_in_order[5],
            "firstHalf": {
                "enemies": first_halves_enemy_info_in_order[5]
            },
            "secondHalf": {
                "enemies": second_halves_enemy_info_in_order[5]
            },
        }
    }

    period_info["floor11"] = {
        "chamber1": {
            "enemyLevel": enemy_levels_in_order[6],
            "firstHalf": {
                "enemies": first_halves_enemy_info_in_order[6]
            },
            "secondHalf": {
                "enemies": second_halves_enemy_info_in_order[6]
            },
        },
        "chamber2": {
            "enemyLevel": enemy_levels_in_order[7],
            "firstHalf": {
                "enemies": first_halves_enemy_info_in_order[7]
            },
            "secondHalf": {
                "enemies": second_halves_enemy_info_in_order[7]
            },
        },
        "chamber3": {
            "enemyLevel": enemy_levels_in_order[8],
            "firstHalf": {
                "enemies": first_halves_enemy_info_in_order[8]
            },
            "secondHalf": {
                "enemies": second_halves_enemy_info_in_order[8]
            },
        }
    }

    period_info["floor12"] = {
        "chamber1": {
            "enemyLevel": enemy_levels_in_order[9],
            "firstHalf": {
                "enemies": first_halves_enemy_info_in_order[9]
            },
            "secondHalf": {
                "enemies": second_halves_enemy_info_in_order[9]
            },
        },
        "chamber2": {
            "enemyLevel": enemy_levels_in_order[10],
            "firstHalf": {
                "enemies": first_halves_enemy_info_in_order[10]
            },
            "secondHalf": {
                "enemies": second_halves_enemy_info_in_order[10]
            },
        },
        "chamber3": {
            "enemyLevel": enemy_levels_in_order[11],
            "firstHalf": {
                "enemies": first_halves_enemy_info_in_order[11]
            },
            "secondHalf": {
                "enemies": second_halves_enemy_info_in_order[11]
            },
        }
    }

    return period_info


def get_period_info_map(
        json_config=os.path.join(os.path.dirname(__file__), 'periods.json')
) -> Dict[str, Dict[str, str]]:
    """
    Returns enemy listings of each period of Abyssal Moon Spire (Floors 9–12) starting from the
    "July 16, 2022 - September 1, 2022" period onward.

    The data is returned in JSON format of the following pattern

    .. image:: ../img/get_period_info_map_rev_val.png
        :align: center

    .. note::
        - This function incurs only O(1) network I/O to fetch info of all periods
        - The information will be feched from `Bilibili Game Wiki <https://wiki.biligame.com/ys/渊月螺旋>`_

    :param json_config:  The path to a config file that tells Peitho Data which periods are to be analyzed and returned.
           See
           https://peitho-data.readthedocs.io/en/latest/genshin_impact/spiral_abyss_internal.html#spiral-abyss-internals
           for more details
    :return: a mapping from period (a string, e.g. period name) to a JSON object that containing information about that
             period
    """
    periods = json.load(open(json_config))
    return {period["period"]: __get_period_info(period["periodKey"]) for period in periods}


if __name__ == "__main__":
    pass
