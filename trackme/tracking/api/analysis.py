""" Analysis of the data: with DB and supplying all the data """
from fastapi import APIRouter, HTTPException, Header
from trackme import conf
from trackme.tracking.crud import check_user, collect_simple_statistics


router = APIRouter()

"""
Explanation of the return dict

1. Autocorrelation: the situation in which successive values of a variable
measured over time are correlated with other values of the same series separated
from them by a specific interval

Meaning: your previous behavior withing given attribute is influenced
(positively or negatively) by previous X days

2. Trend: general direction where your behavior is heading

3. Seasonality or cyclic behavior - strongly repeated pattern in behavior.
This is not a bad thing, should be rather used as fact and maybe the goal
of tracking would be to icnrease or decrease the phase duration

4. Distribution: abstract thing on it's own

4. Stationarity: how stable is your behavior, or did you experience
fundamental changes in the way you behave. Should have an impact on most decisions about other factors.

5. Modeled behavior: very abstract thing. But basically it is a simplified
representation of all components together.
"""


@router.get("/analyze", response_model=dict)
async def simple_statistics(attribute: int, token: str = Header(...), access_token: str = Header(...)):
    """
    # Collect initial analysis to display. Shown information:
    - Basic parameters: mean, mode, median, standard deviation and variance
    - Raw data points
    - Seasonality row
    - Trend line
    - Autocorrelation - not yet implemented, null
    - Stationarity - bool (this week to previous week) -  not yet implemented, use Dickey-Fuller test
    ---
    ## Parameters:
    * attribute (optional): int Attribute id to collect information for
    * start (optional): str beginning of the time period of the analysis (default: from the first entry)
    * end (optional): str end of the time period of the analysis (default: till the last entry)
    * charts (optional): List[str] types of chart to show

    ## Returns:
    JSON object with simple statistics and a data array to show for each type of chart
    """
    if access_token is not None and access_token == conf.ACCESS_TOKEN:
        user_id = await check_user(token)
        if user_id is None:
            raise HTTPException(status_code=404, detail="Unknown user")
        return await collect_simple_statistics(user_id, attribute)
    raise HTTPException(status_code=401, detail="You are not authorized to access this API")
