from datetime import datetime
import os
import pandas as pd


class Transaction:
    def __init__(self, df, name, code):
        self.df = df
        
        self.code = code
        self.name = name

        self.df['buy_stack'] = 0
        self.df['amount_stack'] = 0
        self.df['current_budget'] = 0
        self.df['realized_profit'] = 0

        self.__root_path = os.path.dirname(os.path.abspath(__file__))
        self.__transaction_output_file_path = "%s/transaction/code" % (self.__root_path)
        self.__transaction_input_file_path = "%s/transaction/input" % (self.__root_path)

        self.__check_paths()

    def __check_paths(self):
        try:
            os.makedirs(self.__transaction_output_file_path)
        except FileExistsError:
            pass

    def __update_transaction(self, t_type, date, amount, amount_krw):
        if amount < 0:
            raise ValueError("INVALID AMOUNT")

        if t_type == 'sell':
            amount *= -1
            amount_krw *= -1

        condition = self.df['date'] >= date
        self.df.loc[condition, 'buy_stack'] += amount_krw
        self.df.loc[condition, 'amount_stack'] += amount
        self.df.loc[condition, 'realized_profit'] -= amount_krw

    def update_buy(self, date, amount, amount_krw):
        return self.__update_transaction(date, 'buy', amount, amount_krw)

    def update_sell(self, date, amount, amount_krw):
        return self.__update_transaction(date, 'sell', amount, amount_krw)

    def update_budget(self):
        self.df['current_budget'] = self.df['closing'] * self.df['amount_stack'] - self.df['buy_stack']

    def get_history(self):
        self.update_budget()
        return self.df

    def get_name(self):
        return self.name

    def save_history(self):
        return self.df.to_csv('%s/%s.csv' % (self.__code_list_file_path, self.code), index=False)

    def read_history(self):
        t_df = pd.read_csv('./res/input/total.csv', encoding='CP949')
        t_df.columns = ['name', 'date', 'category', 'amount', 'amount_krw']
        t_df = t_df[t_df['name'] == self.name]
        t_df.dropna(inplace=True)
        t_df['date'] = t_df['date'].apply(lambda x: datetime.strptime(str(x)[:6], "%y%m%d").date())
        t_df['amount_krw'] = t_df['amount_krw'].apply(lambda x: x if x > 0 else x * -1)
        t_df['category'] = t_df['category'].apply(lambda x: 'buy' if x == '매수' else 'sell')

        self.__update_history(t_df)
            
    def __update_history(self):
        self.t_df.apply(
            lambda x: self.__update_transaction(x['category'], x['date'], x['amount'], x['amount_krw']),
            axis=1
        )