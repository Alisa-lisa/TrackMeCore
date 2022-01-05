""" analysis of interaction of multiple factors """
from typing import List, Optional
from trackme.tracking.types.tracking import TrackingActivity as TA
import scipy.stats as stats
import numpy as np


def _avg_estimation(date, array: List[TA]) -> Optional[int]:
    estimations = [
        item.estimation for item in array if (item.created_at.date() == date and item.estimation is not None)
    ]
    if len(estimations) < 1:
        return None
    return int(np.mean(estimations))


def pearson_correlation(first_factor: List[TA], second_factor: List[TA]) -> Optional[float]:
    """Pearson coefficient can be seen as global syncrony
    with three big hypothesis about the series:
    1. data is normally distributed
    2. there are no extremes
    3. data is homoscedastic - variance is stable over time
    Since I know that it's not going to be the case for most factors this is
    an unreliable estimate and later on will be done for different stable time frames
    """
    # TODO: do I want to use SQL for this?
    # we only check for rows with estimation, no binary features yet
    # 1. get same size vector -> for now drop na, use same days,
    # later extrapolate if nothing is given based on autocorrelation of the factor
    first_series_dates = [item.created_at.date() for item in first_factor if item is not None]
    second_series_dates = [item.created_at.date() for item in second_factor if item is not None]
    effective_dates = list(set(first_series_dates).intersection(second_series_dates))
    # take average if there are multiple entries for the same day
    # should be done via sql ideally

    factor_one = []
    factor_two = []
    for date in effective_dates:
        daily_estimate = _avg_estimation(date, second_factor)
        if daily_estimate is not None:
            factor_two.append(daily_estimate)
            factor_one.append(_avg_estimation(date, first_factor))

    assert len(factor_one) == len(factor_two)
    # an arbitrary number for comparison of rows: a pattern can be seen after at least 2 weeks
    if len(factor_one) < 15:
        return None
    r, p = stats.pearsonr(factor_one, factor_two)
    # TODO: use p to check if correlation makes sense
    return r


def pointbiserial_correlation(first_factor: List[TA], second_factor: List[TA]) -> Optional[float]:
    """Point-biserial correlation
    https://en.wikipedia.org/wiki/Point-biserial_correlation_coefficient
    """
    # arbitrary number of entries to meet some realistic estimation
    if len(second_factor) < 15:
        return None
    first_series_dates = list(set([item.created_at.date() for item in first_factor if item is not None]))
    factor_one = [_avg_estimation(date, first_factor) for date in first_series_dates]
    factor_two_dates = list(set([item.created_at.date() for item in second_factor]))
    factor_two = [1 if d in factor_two_dates else 0 for d in first_series_dates]
    # TODO: start thinking about parsing comments to distinguish between consumables?
    # do not compute correlation for everyday thing for now -> 
    # need different approach (example meds dosage, or different meds)
    if 1 not in factor_two:
        return None
    assert len(factor_one) == len(factor_two)
    r, p = stats.pointbiserialr(np.array(factor_one), np.array(factor_two))
    return r
