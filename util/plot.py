import matplotlib.dates as mdates
import seaborn as sns
from matplotlib import ticker
from pandas import DataFrame

palette = iter(sns.color_palette())
sns.set_theme()


def get_color():
    return next(palette)


def add_plot(plot: sns.FacetGrid | None, data: DataFrame, x_column: str, y_column: str,
             label: str, color: str = get_color()):
    if plot is not None:
        return plot.map_dataframe(sns.lineplot, x_column, y_column, color=(color, 0.75), label=label)
    return sns.relplot(kind="line", data=data, x=x_column, y=y_column,
                       color=(color, 0.75), height=6, aspect=1.4, legend="full", label=label)


def complete_plot(plot: sns.FacetGrid, title: str):
    plot.set(ylabel="Intensity", title=title)
    plot.set(ylim=(0, 10))
    ax = plot.ax
    ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
    plot.figure.legend()
    return plot


def save_figure(plot: sns.FacetGrid, file_path: str):
    plot.savefig(file_path)
