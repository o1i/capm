import numpy as np
import pandas as pd

from src.accounts import get_account_balances
from src.isin_positions import get_isin_pos
from src.all_values import get_all_historic_values


def get_all_exposure(values: pd.DataFrame = get_all_historic_values(), normalise: bool = False):
    """
    Gets the exposure of every date where the valuations are available and of every observed instrument in nummeraire
    currency

    :param values: (date)[|<cur1>]+[|<isin1>] valuations, must contain all instruments in possession
    :param normalise: if True, values are normalised to sum to 1
    :return: (date)[|<cur1>]+[|<isin1>]
    """
    cash = get_account_balances()
    investments = get_isin_pos()
    portfolio = cash.merge(investments, left_index=True, right_index=True, how="outer")
    assert all(c in values.columns for c in portfolio.columns)
    relevant_values = values[portfolio.columns].merge(
        portfolio, left_index=True, right_index=True, how="left", suffixes=["_val", "_pos"])
    for c in [c for c in relevant_values.columns if c.endswith("_pos")]:
        relevant_values[c].fillna(method="ffill", inplace=True)
    for c in portfolio.columns:
        relevant_values[c + "_tot"] = np.where(relevant_values[c + "_pos"] == 0, 0,
                                               relevant_values[c + "_val"] * relevant_values[c + "_pos"])
    exposure = relevant_values[[c for c in relevant_values if c.endswith("_tot")]]
    exposure.columns = [c.replace("_tot", "") for c in exposure.columns]
    return exposure if not normalise else exposure.div(exposure.sum(axis=1, min_count=1), axis=0)
