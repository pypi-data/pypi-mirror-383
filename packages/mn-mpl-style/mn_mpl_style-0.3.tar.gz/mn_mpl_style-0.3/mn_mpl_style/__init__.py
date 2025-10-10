import matplotlib.pyplot as plt

import os

def use_style(style_name="mn_adi"):
    """Apply a custom Matplotlib style."""
    style_path = os.path.join(os.path.dirname(__file__), "styles", f"{style_name}.mplstyle")
    plt.style.use(style_path)

# As a default, apply the mn_thesis style
use_style(style_name="mn_adi")