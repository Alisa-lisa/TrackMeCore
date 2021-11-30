""" 1st phase of the analysis """
from typing import List
from trackme.tracking.crud.tracking import filter_entries
import statsmodels.api as sm
import numpy as np

# import matplotlib.pyplot as plt


def detect_trend(input_data: List[int]) -> List[float]:
    """
    Why using this filter: trend should be as smooth as it gets, thus rather simple model:
    https://www.statsmodels.org/dev/generated/statsmodels.tsa.filters.hp_filter.hpfilter.html
    Decomposes given time series into trend and cyclic component
    via Hodrick-Prescott filter
    returns (trend)"""
    hpcycles = sm.tsa.filters.hpfilter(input_data, 1600 * 3 ** 4)
    return hpcycles[1].tolist()


def detect_breaking_points(input_data: List[float]) -> List[int]:
    """based on first derivative collect obvious (hardcoded threshold) changes
    return indexes of the changes in the row
    """
    breaking_points = []
    changes = np.gradient(input_data)
    for i in range(2, len(changes) - 1):
        # False = <0, True >0
        previous_sign = False if changes[i - 2] - changes[i - 1] < 0 else True
        current_sign = False if changes[i - 1] - changes[i] < 0 else True
        next_sign = False if changes[i] - changes[i + 1] < 0 else True
        # if sign has changed, it must be breaking point
        if previous_sign is not current_sign and current_sign is next_sign:
            breaking_points.append(i)
    # TODO: bullet proof this approach. Not entirely sure about this approach =(
    return breaking_points


async def collect_report(user_id: int, attribute_id: int) -> dict:
    """detect trend, breaking points"""
    res = {}  # type: ignore
    # collect time series to get trend
    ts_raw = await filter_entries(
        user_id=user_id, topics=None, start=None, end=None, attribute=attribute_id, comments=None, ts=True
    )
    # arbitrary number 2weeks worth of data can show you some dependencies
    if len(ts_raw) < 2 * 7:
        return res

    tse = [t.estimation for t in ts_raw if t.estimation is not None]
    tsd = [t.created_at for t in ts_raw if t.created_at is not None]
    trend = detect_trend(tse)
    res["trend"] = [(trend[i], tsd[i]) for i in range(0, len(trend))]

    # detect breaking points with hard-coded value
    breaking_points = detect_breaking_points(trend)
    res["breaking_points"] = [(trend[i], tsd[i]) for i in breaking_points]
    return res
