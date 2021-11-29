""" computing base statistical information and prepare data for charts """
from typing import Tuple, List, Optional

# from trackme.tracking.types import DecompositionModels
import numpy as np

# from numpy.polynomial.polynomial import Polynomial
from scipy import stats
import statsmodels.api as sm

# from statsmodels.tsa.seasonal import seasonal_decompose
from collections import deque
from statsmodels.stats.stattools import durbin_watson
from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt

# import statsmodels


def decompose_ts(input_array: List[int]) -> List[float]:
    """Decomposes given time series into trend and cyclic component
    via Hodrick-Prescott filter
    returns (trend)"""
    hpcycles = sm.tsa.filters.hpfilter(input_array, 1600 * 3 ** 4)
    # x = [i for i in range(0, len(hpcycles[0]))]
    # plt.plot(x, hpcycles[0], 'g')
    # plt.plot(x, hpcycles[1], 'r')
    # plt.show()
    return hpcycles[1].tolist()


def autocorrelation(row: List[int], max_lag: int = 7, custom_lag: Optional[int] = None) -> dict:
    """
    Compute auto correlation for up to max_lag day difference
    Durbin-Watson test is for lag of 1 (0-4 value)
    H0 - errors are serially uncorrelated
    d = 2 indicates no autocorrelation, << 2 substantial positive, >> substantial negative
    """
    res = {}
    res["DWtest"] = durbin_watson(row)

    items = deque(row)
    for i in range(1, max_lag + 1):
        items.rotate(1)
        res[f"{i}d"] = np.corrcoef(row, items)[0, 1]
    if custom_lag is not None:
        items.rotate(custom_lag - max_lag)
        res["custom_lag"] = np.corrcoef(row, items)[0, 1]

    # auocor = statsmodels.tsa.stattools.pacf(row, nlags=14, alpha=0.08)
    # plt.plot([i for i in range(0, len(auocor[0].tolist()))], auocor[0].tolist())
    # plt.show()
    # plt.plot([i for i in range(0, len(auocor.pacf))], pacf)

    # plt.show()

    return res


def is_stationary(input_array: List[int], critical_value: Optional[int] = 1) -> bool:
    """
    Augmented Dickey-Fuller unit root test
    https://www.statsmodels.org/dev/generated/statsmodels.tsa.stattools.adfuller.html
    The null hypothesis of the Augmented Dickey-Fuller is that there is a unit root
    If the p-value is above critical statistics we can not reject H0
    has unit root -> non-stationary
    no unit root -> stationary
    Stationary process should have no time-dependent components like trend or seasonality
    """
    dftest = adfuller(input_array, autolag="AIC", regression="ctt")
    result = True if dftest[1] < dftest[4][f"{critical_value}%"] else False
    return result


def simple_trend_detection(input_array: List[int]) -> None:
    iy = input_array
    ix = [i for i in range(0, len(input_array))]
    return np.polyfit(ix, iy, 1)


# TODO: I want to choose model parameters automatically
def ts_decompistion_with_ucm(input_array: List[int]) -> dict:
    """
    UCM (unobserved components model) decomposition of a timeseries
    - the parameters for the model are kept very simple and limited
    since this is supposed to be a automatic analysis
    - the result is simple interpretation of the model coefficients
    like:
    * cycle length
    * level/trend (intercept and slope behavior)
    * accuracy - Not sure how to estimate this one
    """
    result = {}
    # manual parameters choice from the plotting
    custom_model = {
        "cycle": True,
        "autoregressive": 1,
        "trend": True,
        "level": "local linear deterministic trend",  # depends on trend
    }
    model1 = sm.tsa.UnobservedComponents(input_array, **custom_model)
    model_fitted = model1.fit(method="powell", disp=False)

    # TODO: is this a reliable approach?
    def interpretable_estimates(input_list: List[float]) -> List[float]:
        """
        Fit linear regression into estimated array to get simple interpretation in numbers
        """
        iy = input_list
        ix = [i for i in range(0, len(input_list))]
        return np.polyfit(ix, iy, 1)

    intercept_fit = interpretable_estimates(model_fitted.level["filtered"].tolist()[5:])
    print(f"Intercept fit is {intercept_fit}")
    slope_fit = interpretable_estimates(model_fitted.trend["filtered"].tolist()[5:])
    print(f"Slope fit is {slope_fit}")
    # SlowingDown, SpeedingUp, Constant -> need some proper estimate, is it individual? Can I deduce it from somewhere?
    slope_interpretation = "Unknown"
    if 0.005 >= slope_fit[0] >= 0.001:
        slope_interpretation = "Constant"
    elif slope_fit[0] < 0.001:
        slope_interpretation = "SlowingDown"
    else:
        slope_interpretation = "SpeedingUp"

    # result["cycle"] =
    result["trend"] = "Downward" if intercept_fit[0] < 0 else "Upward"
    result["speed"] = slope_interpretation
    # result["noise"] = model_fitted.resid.tolist()[5:]  # when do I want to add noise?

    return result


def prepare_main_statistics(input_array: List[int]) -> Tuple:
    """Compute mean, mode, median, std, variance of the series"""
    mean = round(np.mean(input_array), 2)
    mode = int(stats.mode(input_array)[0][0])
    median = int(np.median(input_array))
    variance = round(np.var(input_array), 2)
    std = round(np.std(input_array), 2)
    return mean, mode, median, std, variance


def prepare_rows_to_display(input_array: List[int]) -> dict:
    """Compute rows for: raw data, trend line, seasonality component
    x-axis: value
    y-axis: tick
    """
    # preparing np array for trend detection
    res = {}
    res["raw"] = input_array
    visual_debug(res, debug=True)
    return res


def visual_debug(input: dict, debug: bool = False) -> None:
    ts_data = input["raw"]
    plt.plot(ts_data)
    # sm.graphics.tsa.plot_acf(ts_data, lags=40)
    # sm.graphics.tsa.plot_pacf(ts_data, lags=40)

    # UCM
    # assumed local linear trend
    # TODO: models so far are created completely manually.
    # until I find a sane approach that gives me ok results automatically
    custom_model = {
        "cycle": True,
        # "autoregressive": 1,
        "trend": True,
        "level": "local linear deterministic trend",  # depends on trend
    }
    # custom_model = {
    #     "cycle": True,
    #     # "stohastic_cycle": True,
    #     # "damped_cycle": True,
    #     "trend": True,
    #     "level": ""
    #     # "autoregressive": 1,
    # }
    model1 = sm.tsa.UnobservedComponents(ts_data, **custom_model)
    res = model1.fit(method="powell", disp=False)
    res.plot_components(legend_loc="lower right")

    if debug:
        plt.show()
    return None


def distribution_analysis(input_data: List[int], normalized_data: List[int]) -> None:
    """currently visual analysis -> needs to be automatic later on"""
    fig, axs = plt.subplots(4)
    axs[0].plot(input_data)

    # hist_data_density = np.histogram(input_data, bins=10, density=True)
    # hist_data_samples = np.histogram(input_data, bins=10, density=False)
    # print(f"histogram density: {hist_data_density}")
    # print(f"histogram count: {hist_data_samples}")
    # x = [i for i in range(0, len(input_data))]

    bins = [i for i in range(0, 10)]
    # plt.plot(bins, hist_data_density[0])
    axs[1].hist(input_data, bins=bins, density=True)

    # old data
    axs[2].plot(normalized_data)
    axs[3].hist(normalized_data, bins=bins, density=True)

    plt.show()
