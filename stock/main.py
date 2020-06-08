from datetime import date

from stock import StockInformation
import config

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


if __name__ == "__main__":
    stock = StockInformation()
    code_list = stock.get_code_list()

    for name in config.noi:
        try:
            code = code_list[code_list['name'] == name]['code'].item()
        except ValueError:
            print("CANNOT FOUND CODE FOR NAME [%s]" % name)
            continue

        print(code)
        df = stock.get_stock_information(code, date(2020, 6, 1))
        print(df)

        # transaction init
        dfs = df.copy()
        dfs['buy_stack'] = 0
        dfs['amount_stack'] = 0
        dfs['profit'] = 0

        # buy 2020-05-27, 5930, 50000, 10
        condition = dfs['date'] >= date(2020, 5, 27)
        dfs.loc[condition, 'buy_stack'] += 50000 * 10
        dfs.loc[condition, 'amount_stack'] += 10
        print(dfs)

        # buy 2020-05-27, 5930, 49000, 5
        condition = dfs['date'] >= date(2020, 5, 27)
        dfs.loc[condition, 'buy_stack'] += 49000 * 5
        dfs.loc[condition, 'amount_stack'] += 5
        print(dfs)

        # buy 2020-05-28, 5930, 50700, 30
        condition = dfs['date'] >= date(2020, 5, 31)
        dfs.loc[condition, 'buy_stack'] += 50700 * 30
        dfs.loc[condition, 'amount_stack'] += 30
        print(dfs)
        
        dfs['profit'] = dfs['closing'] * dfs['amount_stack'] - dfs['buy_stack']
        print(dfs)

        '''
        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
        '''
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Scatter(x=dfs['date'], y=dfs['profit'], mode='lines', name='profit'),
            secondary_y=False
        )
        fig.add_trace(
            go.Scatter(x=dfs['date'], y=dfs['closing'], mode='lines', name='closing'),
            secondary_y=True
        )
        fig.update_layout(
            title_text="[%s] profit" % code,
            yaxis=dict(tickformat=",000"),
            yaxis2=dict(tickformat=",000"),
        )
        fig.update_xaxes(title_text="date")
        fig.show()