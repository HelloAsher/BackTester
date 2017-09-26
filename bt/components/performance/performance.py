import pandas as pd
import numpy as np


def create_sharp_ratio(returns: pd.Series, periods=250 * 4 * 15):
    """
    为这个投资组合计算夏普比率，假设无风险收益率为0
    :param returns: 投资组合的 每一期的收益率，是一个pandas series
    :param periods: 投资组合的投资期数
    :return:    夏普比率
    """

    """
    第一个肯定为nan，因为在portfolio的create_equity_curve_dataframe函数中调用了pct_change函数，所以要去掉第一项，不然计算出来的夏普比率为nan
    """
    return_temp = returns[1:-1]
    return (np.sqrt(periods) * np.mean(return_temp.values)) / np.std(return_temp.values)


def create_drawdowns(equity_curve: pd.Series):
    """
    计算股票或者投资组合的最大回撤
    :param equity_curve:    每期的收益率百分比，是一个pandas series
    :return:    最大回撤和连续发生最大回的期数
    """
    hwm = [0]
    equity_index = equity_curve.index
    drawdown = pd.Series(index=equity_index)  # 存放每个期的回撤
    duration = pd.Series(index=equity_index)  # 存放连续发生回撤

    for i in range(1, len(equity_index)):
        curr_hwm = max(hwm[i - 1], equity_curve.values[i])
        hwm.append(curr_hwm)
        drawdown[i] = hwm[i] - equity_curve.values[i]  # drawdown 中存放的总是直到当前位置的最大值，是一个百分比的小数形式
        duration[i] = 0 if drawdown[i] == 0 else duration[i - 1] + 1  # drawdown[i] 永远都是大于等于0的，不可能小于0
    return drawdown.max(), duration.max()
