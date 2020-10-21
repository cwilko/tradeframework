import pandas as pd
from tradeframework.api import Model


class PreOpenMomentum(Model):

    def __init__(self, name, env):
        Model.__init__(self, name, env)
        return

    # Generate Signals and use them with asset values to calculate allocations
    def getSignals(self, idx=0):

        # Extract window from the data
        # TODO : Handle list of assetInfos
        # TODO: ADD WINDOW SUPPORT
        window = self.assets[0].values[idx:]

        context = {}
        context['temp'] = {'data': pd.DataFrame(), 'currentSignal': Model.CASH}

        # Extract the relevant asset information
        context['temp']['data'] = pd.concat([context['temp']['data'], window[(window.index.hour == 16) & (
            window.index.minute == 00)].resample('B').agg({'Open': 'first'}).fillna(method='ffill').shift(1).dropna()])

        # Generate the signals for the next n steps
        signals = window.groupby(window.index).apply(lambda x: gap_close_predict(x, context['temp']))
        #self.signals = pd.concat([self.signals, newSignals], join="outer", axis=0)

        return signals

# Whichever direction the market has moved by morning EST, trade in the same direction until the close.


def gap_close_predict(ohlc, context):
    signal = pd.Series({'bar': Model.CASH, 'gap': Model.CASH})

    if ohlc.index.date in context['data'].index.date:

        if (ohlc.index.hour == 7) & (ohlc.index.minute == 0):
            # print(ohlc.Open[0])
            # print(context["data"].loc[ohlc.index.date[0]].Open)

            if (ohlc.Open[0] > context['data'].loc[ohlc.index.date[0]].Open):
                context['currentSignal'] = Model.BUY
            else:
                context['currentSignal'] = Model.SELL

        if (ohlc.index.hour >= 7) & (ohlc.index.hour <= 15):
            signal = pd.Series({'bar': context['currentSignal'], 'gap': context['currentSignal']})

    return signal
