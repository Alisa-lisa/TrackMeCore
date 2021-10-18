""" computing base statistical information and prepare data for charts """
from typing import Tuple, List
from trackme.tracking.types import DecompositionModels
import numpy as np
from numpy.polynomial.polynomial import Polynomial
from scipy import stats
from statsmodels.tsa.seasonal import seasonal_decompose


def prepare_main_statistics(input_array: List[int]) -> Tuple:
    """Compute mean, mode, median, std, variance of the series"""
    mean = round(np.mean(input_array), 2)
    mode = int(stats.mode(input_array)[0][0])
    median = int(np.median(input_array))
    variance = round(np.var(input_array), 2)
    std = round(np.std(input_array), 2)
    return mean, mode, median, std, variance


def prepare_rows_to_display(
    input_array: List[int], seasonality: bool = False, model: DecompositionModels = DecompositionModels.ADD
) -> dict:
    """Compute rows for: raw data, trend line, seasonality component
    x-axis: value
    y-axis: tick
    """
    # preparing np array for trend detection
    x = np.array(range(0, len(input_array)))
    y = np.array(input_array)
    res = {}
    res["raw"] = input_array
    print(f"raw row is {res['raw']}")
    manual_trend = np.polyfit(x, y, 1)
    mt = Polynomial.fit(y, x, 1, domain=[], full=True)  # what is domain???
    decomposed = seasonal_decompose(input_array, model=model.value, period=1)
    print(f"computed  trend: {decomposed.trend}")
    print(f" vs manual trend {manual_trend}")
    print(f"vs polyfit {mt} \n seasonal: {decomposed.seasonal} \n noise: {decomposed.resid}")
    # res["trend"] = decomposed.trend
    # res["seasonal"] = decomposed.seasonal
    # TODO: can i switch between the models based on the size of the noise?
    return res


def detect_stationarity(input_array: List[int]) -> bool:
    """Dickey-Fuller test. H0: not stationary"""
    return False
