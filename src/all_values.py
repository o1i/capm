import pandas as pd

from src.currencies import get_historic_currencies
from src.isin import get_historic_values
from src.utils import open_table


def get_all_historic_values(nummeraire: str = "chf"):
    """
    Returns a dataframe with the historic values of currencies and ISINs in the nummeraire currency
    :param nummeraire: currency to measure everything in
    :return: (date)[|<cur1>]+[|<ISIN1>]+
    """
    currencies = get_historic_currencies(nummeraire)
    isin_vals = get_historic_values()
    all_values = combine_all_values(isin_vals, currencies)
    return all_values


def combine_all_values(isin_vals: pd.DataFrame, currencies: pd.DataFrame) -> pd.DataFrame:
    """
    Returns currencies and ISINs valued in nummeraire (already assumed to have happened for currencies,
    and happening here to the ISIN part).

    Requires the isin to appear in data/currencies.csv

    :param isin_vals: (date)[|<isin1>]+
    :param currencies: (date)[|<cur1>]+ (measured in the nummeraire)
    :return: (date)[|<cur1>]+[|<isin1>]+
    """
    isin_currencies = open_table("data/currencies.csv").set_index("isin")
    assert all(isin_vals.columns.isin(isin_currencies.index)), "ISIN values without currency spec"
    isins = list(isin_vals.columns)
    all_values = isin_vals.merge(currencies, left_index=True, right_index=True, how="outer")
    for isin in isins:
        all_values[isin] = all_values[isin] * all_values[isin_currencies.loc[isin].iloc[0]]
    return all_values
