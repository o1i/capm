import os

import pandas as pd

from src.utils import open_table


def get_account_balances() -> pd.DataFrame:
    """
    Get a dataframe of historic account balances grouped by currency

    No interpolation happens, there will be holes in the index.

    Assumes the files to be named data/_acc_[...].csv and have the following content:
    date,<cur>
    dd.mm.yyyy,<value>
    Only the dates with a value change need to be filled (rest is ffilled later on)

    Multiple accounts may have the same currencies, but they will be aggregated

    :return: (date)[|<cur1>]+
    """
    acc_files = [f for f in os.listdir("data") if f.startswith("_acc")]
    if not acc_files:
        raise ValueError("Found no account files")
    accounts = [get_one_account(f) for f in acc_files]
    if len(accounts) == 1:
        return accounts[0]
    for i in range(1, len(accounts)):
        accounts[0] = accounts[0].merge(accounts[i], left_index=True, right_index=True, how="outer")

    curs = list(accounts[0].columns.str[:3].unique())
    for cur in curs:
        accounts[0][cur] = accounts[0][[c for c in accounts[0].columns if c.startswith(cur)]].sum(axis=1, min_count=1)
    return accounts[0][curs]


def get_one_account(file_path: str) -> pd.DataFrame:
    """
    Gets account changes from one file

    :param file_path: account file path
    :return: (date)|<cur1>, column name is still the original currency measured in that currency
    """
    balances = open_table(os.path.join("data", file_path))
    balances["date"] = pd.to_datetime(balances["date"], dayfirst=True)
    balances.set_index("date", inplace=True)
    return balances.iloc[:, 0].to_frame()