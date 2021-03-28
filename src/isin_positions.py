import os

import pandas as pd

from src.utils import open_table


def get_isin_pos() -> pd.DataFrame:
    """
    Returns exposure by date and ISIN (holes in the index, assumes only values where something changes)

    :return: (date)[|<isin1>]+
    """
    isin_position_files = [f for f in os.listdir("data") if f.startswith("_pos")]
    isin_pos = [get_one_pos(f) for f in isin_position_files]
    if len(isin_pos) == 1:
        return (isin_pos[0])
    for i in range(1, len(isin_pos)):
        isin_pos[0] = isin_pos[0].merge(isin_pos[i], left_index=True, right_index=True, how="outer")
    return isin_pos[0]


def get_one_pos(file_path: str) -> pd.DataFrame:
    """
    Gets position changes from one file

    :param file_path: account file path
    :return: (date)|<isin1>, total number of shares at a given date
    """
    balances = open_table(os.path.join("data", file_path))
    balances["date"] = pd.to_datetime(balances["date"], dayfirst=True)
    balances.set_index("date", inplace=True)
    balances.columns = [c.lower().strip() for c in balances.columns]
    return balances.iloc[:, 0].to_frame()
