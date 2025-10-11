import logging
import matplotlib.pyplot as plt
import pandas as pd
from typing import Optional

logger = logging.getLogger(__name__)

def plot_baseflow(q: pd.Series, bf: pd.Series, save_path: Optional[str] = None):
    """
    Quick visualization of total streamflow vs estimated baseflow.
    """
    fig, ax = plt.subplots(figsize=(10,4))
    q.plot(ax=ax, label="Streamflow (QQ)", linewidth=1)
    bf.plot(ax=ax, label="Baseflow (Q_BF)", linewidth=1)
    ax.legend()
    ax.set_title("Baseflow Separation")
    ax.set_ylabel("Depth (e.g., mm/day)")
    ax.grid(True, alpha=0.3)
    if save_path:
        fig.savefig(save_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

