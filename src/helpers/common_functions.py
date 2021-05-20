from typing import List
import os

def result_code_mappers(val) -> str:
    """Map result codes 0/1/2 to string explanations"""
    m = {0: "passed", 1: "failed", 2: "human moderation required"}

    return m[val]

def format_output_text(stringval) -> str:
    """Removes the unwanted characters in output text  and provides clean readable output ."""

    stringval=stringval.replace("},","<br>")
    for ch in ['{','}','[',']',]:
        if ch in stringval:
            stringval=stringval.replace(ch,"")
    return stringval



def colouring(html_table) -> str:
    """The function highlights detected tags with individual colours in the html code.

    Args:
        html_table (str) : original html code

    Returns:
        html_table (str): modified html in which all detected tags are highlighted with individual colour
    """

    pos = {
        'Title matched': 'green',
        'Token in names list': 'aqua',
        'PERSON': 'yellow',
        'NORP': 'fuchsia',
        'Email': 'wood',
        'Personal Description': 'cyan',
        'Telephone number':'blue',
        'UK Postcode': 'white',
        'Social Media': 'orange'
    }

    for key, value in pos.items():
        html_table = html_table.replace(key , "<span class='{}'>{}</span>".format(value, key))

    return html_table


def read_csv_list(path: str) -> List[str]:
    """read from a csv list to a python list

    Args
      path (str): path to find csv list

    Returns
      Python list from csv
    """
    with open(path, "r", encoding="latin-1") as fh:
      result = [line.rstrip() for line in fh]

    return result