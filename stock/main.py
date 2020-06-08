from datetime import date

from stock import StockInformation
import config

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