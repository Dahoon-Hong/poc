import pandas as pd 
import os
from datetime import datetime, date


class StockInformation:
    def __init__(self):
        super().__init__()
        self.__root_path = os.path.dirname(os.path.abspath(__file__))
        self.__code_list_file_path = "%s/res/code" % (self.__root_path)
        self.__stock_info_file_path = "%s/res/stock" % (self.__root_path)

        self.__check_paths()

    def __check_paths(self):
        try:
            os.makedirs(self.__code_list_file_path)
        except FileExistsError:
            pass
        try:
            os.makedirs(self.__stock_info_file_path)
        except FileExistsError:
            pass

    def __check_code_list(self):
        # check file and get code list
        if os.path.exists("%s/code.csv" % self.__code_list_file_path):
            return True
        else:
            return False

    def __save_code_list(self, code_list):
        code_list.to_csv('%s/code.csv' % self.__code_list_file_path, index=False)

    def __read_code_list(self) -> pd.DataFrame:
        return pd.read_csv('%s/code.csv' % self.__code_list_file_path)

    def __check_stock_info(self, code):
        if os.path.exists('%s/%s.csv' % (self.__stock_info_file_path, code)):
            return True
        else:
            return False

    def __save_stock_info(self, code, info):
        info.to_csv('%s/%s.csv' % (self.__stock_info_file_path, code), index=False)

    def __read_stock_info(self, code):
        df = pd.read_csv('%s/%s.csv' % (self.__stock_info_file_path, code))
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='ignore')
        return df

    def update_code_list(self):
        code_df = pd.read_html('https://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0]
        code_df.종목코드 = code_df.종목코드.map('{:06d}'.format) 
        code_df = code_df[['회사명', '종목코드']]
        code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'})
        code_df['code'] = pd.to_numeric(code_df['code'])
        self.__save_code_list(code_df)
        return True

    def get_code_list(self):
        if not self.__check_code_list():
            self.update_code_list()
        return self.__read_code_list()

    def __get_stock_information(self, code, from_date, to_date):
        # from_date >= to_date
        df = pd.DataFrame()
        current_date = datetime.utcnow().date()
        url = 'https://finance.naver.com/item/sise_day.nhn?code=%06d' % code
        date_in_a_page = 15

        first_page = int(((current_date - from_date).days) / date_in_a_page) + 1
        last_page = int(((current_date - to_date).days) / date_in_a_page) + 1
        print(first_page, last_page)
        for page in range(first_page, last_page + 1):
            page_url = "%s&page=%d" % (url, page)
            page_df = pd.read_html(page_url, header=0)[0]
            page_df.columns = ['date', 'closing', 'comparison', 'starting', 'high', 'low', 'amount']
            print("%s [%3d/%3d]" % (page_url, len(page_df), date_in_a_page))
            page_df.dropna(inplace=True)
            page_df['date'] = pd.to_datetime(page_df['date'], format='%Y.%m.%d', errors='ignore')
            df = df.append(page_df, ignore_index=True)
        return df

    def get_stock_information(self, code, to_date):
        current_date = datetime.utcnow().date()
        if self.__check_stock_info(code):
            df = self.__read_stock_info(code)
            min_date = min(df['date']).date()
            max_date = max(df['date']).date()
            if min_date > to_date:
                df = df.append(self.__get_stock_information(code, min_date, to_date))
            if max_date < current_date:
                df = df.append(self.__get_stock_information(code, current_date, max_date))
        else:
            df = self.__get_stock_information(code, current_date, to_date)
        df = df.sort_values(by='date', ascending=True)
        df['comparison'] = df.diff()['closing']
        self.__save_stock_info(code, df)
        df['date'] = df['date'].dt.date

        return df

