""" collect data from the DB for further analysis """
from trackme.tracking.analysis import (
    prepare_main_statistics,
    # prepare_rows_to_display,
    # distribution_analysis,
    autocorrelation,
    # is_stationary,
    # ts_decompistion_with_ucm,
    # simple_trend_detection,
    decompose_ts,
)
from trackme.tracking.crud import filter_entries


async def collect_simple_statistics(user_id: int, attribute_id: int) -> dict:
    # get rows per given info
    ts_raw = await filter_entries(
        user_id=user_id, topics=None, start=None, end=None, attribute=attribute_id, comments=None, ts=True
    )
    # length = len(ts_raw)
    # ts = [t.estimation for t in ts_raw][length-120:length-60]
    ts = [t.estimation for t in ts_raw]
    # apply transformations and analysis to the row
    mean, mode, median, var, std = prepare_main_statistics(ts)  # type: ignore
    # TODO: build in a check for sanity of the numbers
    res = {"statistics": {"mean": mean, "mode": mode, "median": median, "variance": var, "std": std}}
    res["autocorrelation"] = autocorrelation(ts, 7, 30)  # type: ignore

    # if the row is not stationary, we can't really work with it directly
    # stationary_process = is_stationary(ts)
    # res["stationarity"] = stationary_process
    res["trend"] = decompose_ts(ts)  # type: ignore
    # def deterministic_detrending():
    #     trend = simple_trend_detection(ts)
    #     print(f"detected trend {trend}")
    #     def trend_value(value: float) -> float:
    #         return value * trend[0] + trend[1]
    #
    #     # extract trend
    #     stationaty_ts = [ts[i] - trend_value(i) for i in range(0, len(ts))]
    #     print(f"is adjusted series stationary? {is_stationary(stationaty_ts)}")
    #     distribution_analysis(ts, stationaty_ts)
    #     # prepare_rows_to_display(stationaty_ts)
    #
    # if not stationary_process:
    #     trend, cycle = decompose_ts(ts)
    #     is_stationary_now = is_stationary(cycle)
    # let's take the trend out
    # res["decomposition"] = ts_decompistion_with_ucm(ts)
    # print(f"this is dict {res}")
    # TODO: seasonality makes sense only after 2 weeks of data
    # TODO: distribution makes sense after 30 entry points
    # TODO: raw and trend can be done after a week
    # decomposed_ts = prepare_rows_to_display(ts)

    return res
