""" analysis of interaction of multiple factors """
from typing import List, Optional
from trackme.tracking.models.tracking import TrackingActivity as TA
import scipy.stats as stats


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
    factor_one = [item.estimation for item in first_factor if item.created_at.date() in effective_dates]
    factor_two = [item.estimation for item in second_factor if item.created_at.date() in effective_dates]

    assert len(factor_one) == len(factor_two)
    # an arbitrary number for comparison of rows: a pattern can be seen after at least 2 weeks
    if len(factor_one) < 15:
        return None

    r, p = stats.pearsonr(factor_one, factor_two)
    # TODO: use p to check if correlation makes sense

    return r
