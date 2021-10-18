""" collect data from the DB for further analysis """
from trackme.tracking.analysis import (
    prepare_main_statistics,
    # prepare_rows_to_display,
)
from trackme.tracking.crud import filter_entries


async def collect_simple_statistics(user_id: int, attribute_id: int) -> dict:
    # get rows per given info
    ts_raw = await filter_entries(
        user_id=user_id, topics=None, start=None, end=None, attribute=attribute_id, comments=None
    )
    ts = [t.estimation for t in ts_raw]
    # apply transformations and analysis to the row
    mean, mode, median, var, std = prepare_main_statistics(ts)
    # TODO: build in a check for sanity of the numbers
    res = {"statistics": {"mean": mean, "mode": mode, "median": median, "variance": var, "std": std}}
    # TODO: seasonality makes sense only after 2 weeks of data
    # TODO: distribution makes sense after 30 entry points
    # TODO: raw and trend can be done after a week
    # decomposed_ts = prepare_rows_to_display(ts)

    print(f"this is dict {res}")
    return res
