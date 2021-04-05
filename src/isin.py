import os
import re

import pandas as pd

from src.utils import open_table, complete_missing_days, interpolate


def get_historic_values() -> pd.DataFrame:
    """
    Get a dataframe of historic valuations (in their respective currencies) stored in data

    Source of the data is UBS quotes. Where available (ETFs), total return prices are used, closing otherwise

    Assumes the files to be named data/_val_<isin>_[...].csv.

    :return: (date)[|<isin>]+
    """
    val_files = [f for f in os.listdir("data") if f.startswith("_val")]
    if not val_files:
        raise ValueError("Found no valuation files")
    vals = [get_one_val(f) for f in val_files]
    if len(vals) == 1:
        return(vals)
    for i in range(1, len(vals)):
        vals[0] = vals[0].merge(vals[i], on="date", how="outer")
    filled = complete_missing_days(vals[0].set_index("date"))
    interpolated = interpolate(filled)
    return interpolated


def get_one_val(filename: str) -> pd.DataFrame:
    isin = re.search("(?<=_val_)([^_]+)(?=_)", filename).group().lower().strip()
    values = open_table(os.path.join("data", filename))
    values["date"] = pd.to_datetime(values["date"], dayfirst=True)
    values[isin] = values["total_return"] if "total_return" in values.columns else values["close"]
    values.sort_values("date", inplace=True)
    return values[["date", isin]]
