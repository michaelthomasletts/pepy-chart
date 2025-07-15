__all__ = ["PepyStats"]

import os
import platform
import subprocess
from collections import defaultdict
from functools import cached_property

import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import mplcyberpunk
import requests
from pandas import DataFrame, to_datetime
from seaborn import lineplot


class PepyStats:
    def __init__(
        self,
        package: str,
        api_key: str,
        create_image: bool = True,
        *,
        output_path: str = None,
        rolling_window: int = 7,  # weekly
        automatically_open_img: bool = True,
        color: str = "#FF0000FF",  # red
        title_fontsize: int = 14,
        axis_fontsize_adj: int = 4,  # amount to subtract from title fontsize
    ):
        # required params
        self.package = package
        self.api_key = api_key

        if output_path is None and create_image is True:
            raise ValueError(
                "'output_path' must be provided if 'create_image' is True!"
            )

        self.output_path = output_path
        self.title_fontsize = title_fontsize
        self.axis_fontsize_adj = axis_fontsize_adj
        self.axis_fontsize = self.title_fontsize - self.axis_fontsize_adj
        self.color = color
        self.rolling_window = rolling_window

        if create_image:
            self.plot()
            if automatically_open_img:
                self.open_image()

    @property
    def package(self) -> str:
        return self._package

    @package.setter
    def package(self, value: str):
        self._package = value
        self.url = f"https://pepy.tech/api/v2/projects/{value}"

    def get_statistics(self) -> dict:
        headers = {"X-API-Key": self.api_key}
        response = requests.get(self.url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()

    @cached_property
    def total_downloads(self) -> int:
        return int(self.get_statistics().get("total_downloads", 0))

    def aggregate_statistics(self) -> dict:
        if not (stats := self.get_statistics().get("downloads", {})):
            raise ValueError(
                f"There are no statistics avaialble from PePy for {self.package}"
            )

        daily_downloads = defaultdict(int)

        for date, stats in stats.items():
            for version, downloads in stats.items():
                daily_downloads[date] += downloads

        self.stats = daily_downloads

    def dataframe(self, rolling_window: int = 0) -> DataFrame:
        if not hasattr(self, "stats"):
            self.aggregate_statistics()

        df = DataFrame(list(self.stats.items()), columns=["Date", "Downloads"])
        df["Date"] = to_datetime(df["Date"])
        df = df.sort_values("Date")
        if rolling_window:
            df["Downloads"] = (
                df["Downloads"].rolling(window=rolling_window).mean()
            )

        self.df = df

        return df

    def plot(self):
        # creating dataframe if it doesn't already exist
        if not hasattr(self, "df"):
            self.dataframe(rolling_window=self.rolling_window)

        # setting style
        plt.style.use("cyberpunk")
        plt.rcParams.update(
            {
                "figure.facecolor": "none",
                "axes.facecolor": "none",
                "savefig.transparent": True,
                "text.color": self.color,
                "axes.labelcolor": self.color,
                "xtick.color": self.color,
                "ytick.color": self.color,
                "axes.edgecolor": self.color,
                "grid.color": "none",
            }
        )
        plt.figure(figsize=(7.2, 4.05), dpi=100)  # → 720x405 px

        # plotting
        lineplot(
            x="Date", y="Downloads", data=self.df, marker="o", color=self.color
        )
        xlabel = plt.xlabel("Date", weight="bold", fontsize=self.axis_fontsize)
        xlabel.set_path_effects(
            [
                path_effects.Stroke(linewidth=1, foreground="red"),
                path_effects.Normal(),
            ]
        )
        y = (
            "Downloads"
            if not self.rolling_window
            else f"Downloads (Rolling Window = {self.rolling_window})"
        )
        ylabel = plt.ylabel(y, weight="bold", fontsize=self.axis_fontsize)
        ylabel.set_path_effects(
            [
                path_effects.Stroke(linewidth=1, foreground="red"),
                path_effects.Normal(),
            ]
        )
        plt.xticks(rotation=45, fontsize=self.axis_fontsize)
        plt.yticks(fontsize=self.axis_fontsize)
        plt.tight_layout()
        mplcyberpunk.add_glow_effects()
        plt.savefig(self.output_path)
        plt.close()
        print(f"Image saved at {self.output_path}")

    def open_image(self):
        system = platform.system()

        if system == "Darwin":  # macOS
            subprocess.run(["open", self.output_path])
        elif system == "Windows":
            os.startfile(self.output_path)
        elif system == "Linux":
            subprocess.run(["xdg-open", self.output_path])
        else:
            print(f"Unsupported OS: {system}")
