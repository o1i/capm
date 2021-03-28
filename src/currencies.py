import os
import re

import pandas as pd

from src.utils import open_table, complete_missing_days, interpolate


def get_historic_currencies(nummeraire: str) -> pd.DataFrame:
    """
    Get a dataframe of historic value pairs of currencies. Convention is the inverse of the CFA convention, i.e.
    the value is the price of the former in terms of the latter.

    Source of the data is https://www.wsj.com, closing prices are used. Missing dates are linearly interpolated.

    Assumes the files to be named data/_cur_<cur_pair>.csv.

    :param nummeraire: reference currency in which to value other currencies. Ignores pairs that do not end in the
    reference currency
    :return: (date)[|<pair1>]+
    """
    cur_files = [f for f in os.listdir("data") if f.startswith("_cur")]
    if not cur_files:
        raise ValueError("Found no currency files")
    curs = [get_one_currency(f) for f in cur_files]
    if len(curs) == 1:
        return(curs[0])
    for i in range(1, len(curs)):
        curs[0] = curs[0].merge(curs[i], on="date", how="outer")

    filled = complete_missing_days(curs[0].set_index("date"))
    interpolated = interpolate(filled)
    valued = value(interpolated, nummeraire)
    return valued


def get_one_currency(filename: str) -> pd.DataFrame:
    cur_pair = re.search("(?<=_cur_)([a-z]{6})", filename).group()
    cur = open_table(os.path.join("data", filename))[["date", "close"]]
    cur["date"] = pd.to_datetime(cur["date"], dayfirst=False)
    cur.sort_values("date", inplace=True)
    return cur.rename(columns={"close": cur_pair})


def value(df: pd.DataFrame, nummeraire: str) -> pd.DataFrame:
    """
    Returns the value of the currencies in the nummeraire currency
    :param df: date[|<pair1>]+
    :return: date[|<cur1]+
    """
    relevant = df[[c for c in df.columns if c == "date" or c.endswith(nummeraire)]]
    relevant.columns = [c if c == "date" else c.replace(nummeraire, "") for c in relevant.columns]
    relevant[nummeraire] = 1
    return relevant
