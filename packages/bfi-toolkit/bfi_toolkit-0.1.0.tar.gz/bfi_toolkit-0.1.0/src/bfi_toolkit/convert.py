import logging
import pandas as pd
from __future__ import annotations

logger = logging.getLogger(__name__)

def convert_cfs_to_mmd(streamflow_cfs: pd.Series, area_sq_miles: float) -> pd.Series:
    """
    Convert streamflow from cubic feet per second to mm/day over a catchment.
    """
    cfs_to_cms = 0.0283168
    mi2_to_m2 = 2589988.11
    sec_per_day = 86400
    mm_per_m = 1000.0

    area_m2 = float(area_sq_miles) * mi2_to_m2
    q_m3_day = streamflow_cfs * cfs_to_cms * sec_per_day
    depth_m_day = q_m3_day / area_m2
    return depth_m_day * mm_per_m

