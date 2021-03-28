import pandas as pd

from src.accounts import get_account_balances
from src.isin_positions import get_isin_pos
from src.all_values import get_all_historic_values


def get_all_exposure(values: pd.DataFrame = get_all_historic_values()):
    """
    Gets the exposure of every date where the valuations are available and of every observed instrument in nummeraire
    currency

    :param values: (date)[|<cur1>]+[|<isin1>] valuations, must contain all instruments in possession
    :return: (date)[|<cur1>]+[|<isin1>]
    """
    cash = get_account_balances()
    investments = get_isin_pos()
    portfolio = cash.merge(investments, left_index=True, right_index=True, how="outer")
    assert all(c in values.columns for c in portfolio.columns)
