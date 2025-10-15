from pyextremes import get_extremes
from pyextremes.plotting import plot_extremes
import pandas as pd
import matplotlib.pyplot as plt
from multiprocessing import freeze_support
from pyextremes import get_extremes, get_return_periods

def main():
    series = pd.read_csv(
        r'D:\OrcaflexAqC2\results_workfolder\All3mT7\long_ts.csv',
        index_col=0,
    ).squeeze()

    series.index = pd.to_datetime(series.index, unit='s')

    from pyextremes import EVA
    model = EVA(series)
    model.get_extremes(method="POT", extremes_type="high",threshold=30000, r="15s")
    model.plot_extremes()
    model.fit_model()
    model.plot_diagnostic(alpha=0.57, plotting_position='ecdf',return_period_size="3600s")
    plt.show()

    extremes = get_extremes(ts=series, method="POT", extremes_type="low", threshold=-53000, r="0.1s")
    return_periods = get_return_periods(
        ts=series,
        extremes=extremes,
        extremes_method="POT",
        extremes_type="high",
        block_size=None,
        return_period_size="3600s",
        plotting_position="weibull",
    )
    print(return_periods.sort_values("return period", ascending=False).head())


if __name__ == "__main__":
    freeze_support()
    main()
