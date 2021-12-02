""" 1st phase of the analysis """
from typing import List
from trackme.tracking.crud.tracking import filter_entries
import statsmodels
import statsmodels.api as sm
import numpy as np

import ruptures as rpt
import matplotlib.pyplot as plt


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
    might_be_break = []
    changes = np.gradient(input_data)
    changes = np.gradient(changes)
    for i in range(2, len(changes) - 1):
        # False = <0, True >0
        previous_sign = False if changes[i - 2] - changes[i - 1] < 0 else True
        current_sign = False if changes[i - 1] - changes[i] < 0 else True
        next_sign = False if changes[i] - changes[i + 1] < 0 else True
        # if sign has changed, it might be a breaking point
        if previous_sign is not current_sign and current_sign is next_sign:
            might_be_break.append(i)
    if len(might_be_break) >= 1:
        breaking_points.append(might_be_break[0])
        for i in range(1, len(might_be_break)):
            if might_be_break[i] > breaking_points[-1] + 21:
                breaking_points.append(might_be_break[i])

    x = [i for i in range(0, len(changes))]
    markers_on = breaking_points
    plt.plot(x, changes, "-gD", markevery=markers_on)
    plt.show()
    # TODO: bullet proof this approach. Not entirely sure about this approach =(
    return breaking_points


def detect_autocorrelation(input_data: List[int]) -> List[float]:
    """Autocorrelation is dependency of a factor on itself in time."""
    autoccorelation = statsmodels.tsa.stattools.pacf(input_data, nlags=7, alpha=0.01)
    print(autoccorelation)
    return []


def detect_breaking_points_raw(input_data: List[int]):
    # algo = rpt.Pelt(model="rbf").fit(np.array(input_data))
    # algo = rpt.Window(model="l2").fit(np.array(input_data))
    algo = rpt.Dynp(model="l1", min_size=7, jump=2).fit(np.array(input_data))
    # algo = rpt.Binseg(model="l2").fit(np.array(input_data))
    result = algo.predict(n_bkps=4)
    return result


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
    # detected = detect_breaking_points_raw(tse)[:-1]
    res["breaking_points"] = [(trend[i], tsd[i]) for i in breaking_points]
    # x = [i for i in range(0, len(trend))]
    # plt.figure(1)
    # plt.subplot(211)
    # markers_on = breaking_points
    # plt.plot(x, trend, '-gD', markevery=markers_on)
    # plt.subplot(212)
    # markers_on = detected
    # plt.plot(x, trend, '-gD', markevery=markers_on)
    # plt.show()
    return res
