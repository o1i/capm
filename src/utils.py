import pandas as pd


def open_table(path: str) -> pd.DataFrame:
    """Open a dataframe and normalise column names"""
    df = pd.read_csv(path)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df


def complete_missing_days(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensures every date occurs, input has to have a date index
    :param df: (date)|...
    :return: (date)|..., fills missing dates
    """
    all_dates = pd.date_range(min(df.index), max(df.index))
    return df.reindex(all_dates)


def interpolate(df: pd.DataFrame, limit_area="inside") -> pd.DataFrame:
    """
    Interpolate all non-index coulmns linearly.
    """
    return df.interpolate(method="index", limit_area=limit_area)
