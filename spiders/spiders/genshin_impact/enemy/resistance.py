from typing import Dict

import requests
from bs4 import BeautifulSoup


def __get_all_tbodies_element(enemy_page: BeautifulSoup) -> list:
    """
    Given a programmable web page, this function finds all tables classed "wikitable gw-table-kd" and returns all of
    their tbody elements wrapped in a list, with each element being a tbody element.

    :param enemy_page:  The provided web page
    :return: a new list
    """
    all_tables = enemy_page.find_all("table", {"class": "wikitable gw-table-kd"})

    nested_tbodies = [table.findChildren('tbody') for table in all_tables]
    return [item for sublist in nested_tbodies for item in sublist]


def __parse_base_resistance_info(tbody) -> Dict[str, str]:
    """
    Given a Biligame enemy page tbody that contains all of the enemy base resistance info, this function parses the
    tbody and outputs as a map whose key is the resistance type name and the value is its corresponding base resistance
    value.

    An example output would be

    .. code-block:: json

        {
            "物理": "10%",
            "火": "10%",
            "水": "∞",
            "冰": "10%",
            "雷": "10%",
            "风": "10%",
            "岩": "10%",
            "草": "10%"
        }

    .. note::
        The tbody structure must satisfy the following properties:

        1. The 2nd row contains all resistance types
        2. The 3rd row contains all base resistance value with the column order that corresponds to the 3nd row

        For instance, the following tbody tells that the electro resistance of this enemy is 50%:

        .. code-block:: html

            <tbody>
                <tr>
                    <th colspan="9">抗性<sup id="cite_ref-2" class="reference"><a href="#cite_note-2">[2]</a></sup></th>
                </tr>
                <tr>
                    <th style="width:10%"><img alt="物理.png" src="...png"> 物理</th>
                    <th style="width:10%"><img alt="火.png" src="...png"> <span style="color:red">火</span></th>
                    <th style="width:10%"><img alt="水.png" src="...png"> <span style="color:#6eaae8">水</span></th>
                    <th style="width:10%"><img alt="冰.png" src="...png"> <span style="color:#82d7ff">冰</span></th>
                    <th style="width:10%"><img alt="雷.png" src="...png"> <span style="color:#9245e6">雷</span></th>
                    <th style="width:10%"><img alt="风.png" src="...png"> <span style="color:#41c77d">风</span></th>
                    <th style="width:10%"><img alt="岩.png" src="...png"> <span style="color:#a99847">岩</span></th>
                    <th style="width:10%"><img alt="草.png" src="...png"> <span style="color:#619e7f">草</span></th>
                </tr>
                <tr>
                    <td>10%</td>
                    <td>10%</td>
                    <td><span style="color:#FF2323">∞</span></td>
                    <td>10%</td>
                    <td>10%</td>
                    <td>50%</td>
                    <td>10%</td>
                    <td>10%</td>
                </tr>
                <tr style="display:none">
                    <td colspan="9"></td>
                </tr>
            </tbody>

    :param tbody:  An html table body element that satisfies the structure described above
    :return:  a new map
    """
    resistance_types = []
    base_resistance_values = []

    for idx, row in enumerate(tbody.find_all("tr")):
        if idx == 1:
            resistance_types = [column.get_text().strip() for column in row.find_all("th")]
        if idx == 2:
            base_resistance_values = [column.get_text().strip() for column in row.find_all("td")]
    return dict(zip(resistance_types, base_resistance_values))


def get_base_resistance_info(enemy_page_url: str) -> Dict[str, str]:
    """
    Returns the base resistance info of a specified enemy.

    The returned value is a map from element name to the degree of base resistance to that element on this enemy. For
    example

    .. code-block:: json

        {
            "物理": "10%",
            "火": "10%",
            "水": "∞",
            "冰": "10%",
            "雷": "10%",
            "风": "10%",
            "岩": "10%",
            "草": "10%"
        }

    .. note::
        The example above describes the base resistance of
        `Large Anemo Slime <https://genshin-impact.fandom.com/wiki/Large_Anemo_Slime>`_

    :param enemy_page_url:  A Biligame URL pointing to the page of the specified enemy. For example
                            https://wiki.biligame.com/ys/大型水史莱姆
    :rtype: Dict[str, str] a new dict
    """
    enemy_page = BeautifulSoup(requests.get(enemy_page_url).content, "html.parser")
    all_tbody_elements = __get_all_tbodies_element(enemy_page)

    for tbody in all_tbody_elements:
        if "抗性" in tbody.find("tr").th:
            return __parse_base_resistance_info(tbody)


if __name__ == "__main__":
    pass
