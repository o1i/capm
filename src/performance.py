import numpy as np
import pandas as pd

from src.all_values import get_all_historic_values
from src.all_exposure import get_all_exposure


def get_portfolio_performance(
        values: pd.DataFrame = get_all_historic_values("chf"),
        exposure: pd.DataFrame = get_all_exposure(normalise=False),
        market: str = "ie00bym11h29",  # default: acwi
) -> pd.DataFrame:
    """
    Gives CAPM performance measures for the constituents as well as the portfolio overall

    Numbers are calculated weekly but reported annually.

    :param values: valuations of the individual investments: (date)|<name>...
    :param exposure: total value by investment (date)|<name>... with the same name and same index as values
    :param market: name of the market instrument
    :return: (instrument)|return|sd|beta
    """
    assert values.shape == exposure.shape
    assert values.index.equals(exposure.index)
    values["portfolio"] = exposure.sum(axis=1, min_count=exposure.shape[1])
    days = pd.bdate_range(min(values.index), max(values.index), freq="C", weekmask="Fri")
    weekly_values = values.loc[days]
    returns = np.log10(weekly_values).diff()
    covariances = returns.cov()
    betas = covariances[market] / covariances[market][market]
    avg_returns = returns.mean() * 250/5
    sd = np.diagonal(covariances) * np.sqrt(250 / 5)
    return pd.DataFrame({"return": avg_returns, "sd": sd, "betas": betas})
