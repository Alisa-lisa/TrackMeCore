""" analysis of interaction of multiple factors """
from typing import List, Optional
from trackme.tracking.types.tracking import TrackingActivity as TA
import scipy.stats as stats
import numpy as np


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

    def _avg_estimation(date, array: List[TA]) -> int:
        return int(np.mean([item.estimation for item in array if item.created_at.date() == date]))  # type: ignore

    factor_one = []
    factor_two = []
    for date in effective_dates:
        factor_one.append(_avg_estimation(date, first_factor))
        factor_two.append(_avg_estimation(date, second_factor))

    assert len(factor_one) == len(factor_two)
    # an arbitrary number for comparison of rows: a pattern can be seen after at least 2 weeks
    if len(factor_one) < 15:
        return None

    r, p = stats.pearsonr(factor_one, factor_two)
    # TODO: use p to check if correlation makes sense

    return r
