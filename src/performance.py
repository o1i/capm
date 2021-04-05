from dateutil.relativedelta import relativedelta

import numpy as np
import pandas as pd

from src.all_values import get_all_historic_values
from src.all_exposure import get_all_exposure


def get_portfolio_performance(
        values: pd.DataFrame = get_all_historic_values("chf"),
        exposure: pd.DataFrame = get_all_exposure(normalise=False),
        market: str = "ie00bym11h29",  # default: acwi,
        max_dur: relativedelta = relativedelta(years=2),
) -> tuple:
    """
    Gives CAPM performance measures for the constituents as well as the portfolio overall

    Numbers are calculated weekly but reported annually.

    :param values: valuations of the individual investments: (date)|<name>...
    :param exposure: total value by investment (date)|<name>... with the same name and same index as values
    :param market: name of the market instrument
    :param max_dur: maximum time horizon of analysis
    :return: (instrument)|return|sd|beta, covariance-array, last fully observed exposure weights
    """
    assert values.shape == exposure.shape
    assert values.index.equals(exposure.index)
    assert set(values.columns) == set(exposure.columns)
    exposure = exposure[values.columns]  # align column order
    # values["portfolio"] = exposure.sum(axis=1, min_count=exposure.shape[1])
    days = pd.bdate_range(min(values.index), max(values.index), freq="C", weekmask="Fri")
    days = days[days >= max(days) - max_dur]
    weekly_values = values.loc[days]
    returns = np.log10(weekly_values).diff()
    weekly_exp = exposure.loc[days]
    returns.loc[returns.index[1:], "portfolio"] = np.nansum(weekly_exp.iloc[:-1, :].values /  # exposure
                                                            np.tile(np.nansum(weekly_exp.iloc[:-1, :].values,
                                                                              axis=1).reshape([-1, 1]),
                                                                    [1, weekly_exp.shape[1]]) *  # normalisation
                                                            returns.iloc[1:, :].values, axis=1)  # returns
    covariances = returns.cov()
    betas = covariances[market] / covariances[market][market]
    avg_returns = returns.apply(lambda x: 10 ** (np.nanmean(x) * 250/5) - 1)
    sd = np.diagonal(covariances) * np.sqrt(250 / 5)
    last_weights = exposure.dropna().iloc[-1, :]
    return pd.DataFrame({"return": avg_returns, "sd": sd, "beta": betas}), covariances, last_weights
