""" 1st phase of the analysis """
from trackme.tracking.analytics.multifactor_analysis import pearson_correlation, pointbiserial_correlation
from typing import List, Tuple, Optional
from trackme.tracking.crud.tracking import filter_entries, get_time_horizon, collect_attributes_ids
from trackme.tracking.crud.tracking_validation import is_attribute_binary
from trackme.tracking.models.tracking import TrackingActivity as TA
import statsmodels
import statsmodels.api as sm
from statsmodels.stats.stattools import durbin_watson
import numpy as np
from fastapi.logger import logger


def detect_autocorrelation(input_data: List[int]) -> Tuple[bool, Optional[List[float]]]:
    """
    Compute auto correlation for up to max_lag day difference
    Durbin-Watson test is for lag of 1 (0-4 value)
    H0 - errors are serially uncorrelated
    d = 2 indicates no autocorrelation, << 2 substantial positive, >> substantial negative
    """
    try:
        is_autocor = True if durbin_watson(input_data) != 2 else False
        autocor = statsmodels.tsa.stattools.pacf(input_data, nlags=7, alpha=0.01)[0].tolist()
    except Exception as ex:
        logger.error(f"Couldn't compute autocorrelation due to {ex}")
        autocor = None
        is_autocor = False
    return is_autocor, autocor


def detect_trend(input_data: List[int]) -> List[float]:
    """
    Why using this filter: trend should be as smooth as it gets, thus rather simple model:
    https://www.statsmodels.org/dev/generated/statsmodels.tsa.filters.hp_filter.hpfilter.html
    Decomposes given time series into trend and cyclic component
    via Hodrick-Prescott filter
    returns (trend)"""
    hpcycles = sm.tsa.filters.hpfilter(input_data, 1600 * 3 ** 4)
    return hpcycles[1].tolist()


# TODO: breaking points are a complex topic -> will be implemented in a later feature
# def detect_breaking_points(input_data: List[float]) -> List[int]:
#     """based on first derivative collect obvious (hardcoded threshold) changes
#     return indexes of the changes in the row
#     """
#     breaking_points = []
#     might_be_break = []
#     changes = np.gradient(input_data)
#     changes = np.gradient(changes)
#     for i in range(2, len(changes) - 1):
#         # False = <0, True >0
#         previous_sign = False if changes[i - 2] - changes[i - 1] < 0 else True
#         current_sign = False if changes[i - 1] - changes[i] < 0 else True
#         next_sign = False if changes[i] - changes[i + 1] < 0 else True
#         # if sign has changed, it might be a breaking point
#         if previous_sign is not current_sign and current_sign is next_sign:
#             might_be_break.append(i)
#     if len(might_be_break) >= 1:
#         breaking_points.append(might_be_break[0])
#         for i in range(1, len(might_be_break)):
#             if might_be_break[i] > breaking_points[-1] + 21:
#                 breaking_points.append(might_be_break[i])
#
#     x = [i for i in range(0, len(changes))]
#     markers_on = breaking_points
#     plt.plot(x, changes, "-gD", markevery=markers_on)
#     plt.show()
#     # TODO: bullet proof this approach. Not entirely sure about this approach =(
#     return breaking_points
#
#
# def detect_breaking_points_raw(input_data: List[int]):
#     # algo = rpt.Pelt(model="rbf").fit(np.array(input_data))
#     # algo = rpt.Window(model="l2").fit(np.array(input_data))
#     algo = rpt.Dynp(model="l1", min_size=7, jump=2).fit(np.array(input_data))
#     # algo = rpt.Binseg(model="l2").fit(np.array(input_data))
#     result = algo.predict(n_bkps=4)
#     return result
DAYS = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}


async def simple_statistics(input_data: List[TA], user_id: int, attribute_id: int) -> dict:
    """When not there is not enough data to run analysis show:
    1. structure of estimates - count of entries per day of the week
    5. time frame for this attribute - earliest date and latest date of the entry
    """

    def base_stats(key: int) -> Tuple[float, float, float]:
        """get min, max and avg for weekday"""
        array = []
        for item in input_data:
            if item.created_at.weekday() == key:
                array.append(item.estimation)
        if bool(array):
            return (min(array), max(array), np.mean(array))
        return (0, 0, 0)

    res = {}
    res["total"] = len(input_data)
    estimations = [i.estimation for i in input_data if i.estimation is not None]
    binary = False if len(estimations) > 0 else True
    tmp = {int(i): 0 for i in DAYS.keys()}
    for i in input_data:
        weekday = int(i.created_at.weekday())
        new_value = tmp[weekday]
        tmp[weekday] = new_value + 1
    stats = []
    for key in tmp.keys():
        if not binary:
            base = base_stats(key)
            stats.append({"count": tmp[key], "min": base[0], "max": base[1], "avg": base[2], "day": DAYS[key]})
        else:
            stats.append({"count": tmp[key], "day": DAYS[key]})
    res["time_structure"] = stats  # type: ignore
    dates = await get_time_horizon(user_id=user_id, attribute_id=attribute_id)
    res["start"] = dates[0]
    res["end"] = dates[1]
    return res


async def collect_report(user_id: int, attribute_id: int) -> dict:
    """detect trend, breaking points"""
    res = {}
    res["enough_data"] = True
    ts_raw = await filter_entries(
        user_id=user_id, topics=None, start=None, end=None, attribute=attribute_id, comments=None, ts=True
    )
    tse = [t.estimation for t in ts_raw if t.estimation is not None]
    tsd = [t.created_at for t in ts_raw if t.created_at is not None]
    # (arbitrary number) 2 weeks worth of data can show you some dependencies
    res["recap"] = await simple_statistics(ts_raw, user_id, attribute_id)  # type: ignore
    if len(tse) < 2 * 7 + 1:
        res["enough_data"] = False
        return res
    trend = detect_trend(tse)
    res["trend"] = [(trend[i], tsd[i]) for i in range(0, len(trend))]  # type: ignore
    autocor = detect_autocorrelation(tse)
    if autocor[0] and autocor[1] is not None:
        res["autocorrelation"] = {
            "is_autocorrelated": autocor[0],
            "autocorrelaton_estimates": autocor[1][1:8],
        }  # type: ignore

    # multiple correlations
    res["multifactor"] = {}  # type: ignore
    is_main_factor_binary = await is_attribute_binary(attribute_id, user_id)
    if not is_main_factor_binary:
        res["multifactor"]["pearson"] = []  # type: ignore
        # continuous_factor vs continuous_factors correlation
        continuous_factors = await collect_attributes_ids(user_id, binary=False)
        if None in continuous_factors:
            continuous_factors.remove(None)  # type: ignore
        for a in continuous_factors:
            is_binary = await is_attribute_binary(a, user_id)
            if is_binary:
                continuous_factors.remove(a)
        continuous_factors.remove(attribute_id)
        for factor in continuous_factors:
            raw_second = await filter_entries(
                user_id=user_id, topics=None, start=None, end=None, attribute=factor, comments=None, ts=True
            )
            res["multifactor"]["pearson"].append({factor: pearson_correlation(ts_raw, raw_second)})  # type: ignore

        # continuous_factor vs binary_factors correlation
        res["multifactor"]["pbsr"] = []  # type: ignore
        binary_factors = await collect_attributes_ids(user_id, binary=True)
        if None in binary_factors:
            binary_factors.remove(None)  # type:ignore
        for factor in binary_factors:
            raw_second = await filter_entries(
                user_id=user_id, topics=None, start=None, end=None, attribute=factor, comments=None, ts=True
            )
            res["multifactor"]["pbsr"].append({factor: pointbiserial_correlation(ts_raw, raw_second)})  # type: ignore

    # binary_factors vs binary_factors correlation: TBI
    else:
        return res
    return res
