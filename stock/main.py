from datetime import datetime, date
import pandas as pd
from stock import StockInformation
import config

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def buy_stock(df, t_date, amount, total_price):
    condition = df['date'] >= t_date
    df.loc[condition, 'buy_stack'] += total_price
    df.loc[condition, 'amount_stack'] += amount




if __name__ == "__main__":
    stock = StockInformation()
    code_list = stock.get_code_list()

#    for name in config.noi:
    name = '현대자동차'
    try:
        code = code_list[code_list['name'] == name]['code'].item()
    except ValueError:
        print("CANNOT FOUND CODE FOR NAME [%s]" % name)
        #continue

    print(code)
    df = stock.get_stock_information(code, date(2019, 8, 1))
    #df = stock.get_stock_information(code, date(2020, 6, 1))
    print(df)

    # transaction init
    dfs = df.copy()
    dfs['buy_stack'] = 0
    dfs['amount_stack'] = 0
    dfs['profit'] = 0
    '''
    t_df = pd.read_csv('./res/input/%s.csv'%code, encoding='CP949')
    print(t_df)
    t_df.columns = ['name', 'date', 'category', 'amount' ,'amount_krw']
    t_df.dropna(inplace=True)
    t_df['date'] = t_df['date'].apply(lambda x : datetime.strptime(str(x)[:-2], "%y%m%d").date())
    t_df['amount_krw'] = t_df['amount_krw'].apply(lambda x : x if x > 0 else x*-1)
    t_df['category'] = t_df['category'].apply(lambda x : 'buy' if x == '매수' else 'sell')
    print(t_df)

    # buy 2020-05-27, 5930, 50000, 10
    t_df[t_df['category'] == 'buy'].apply(lambda x : buy_stock(dfs, x['date'], x['amount'], x['amount_krw']), axis=1)
    '''


    dfs['profit'] = dfs['closing'] * dfs['amount_stack'] - dfs['buy_stack']
    print(dfs)

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