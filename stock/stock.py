import pandas as pd 


class StockInformation:
    def __init__(self):
        super().__init__()


    def __check_code_list(self):
        # check file and get code list 
        raise NotImplementedError()

    def __save_code_list(self, code_list):
        raise NotImplementedError()

    def __read_code_list(self, code_list):
        raise NotImplementedError()

    def update_code_list(self):
        code_df = pd.read_html('ttp://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0]
        code_df.종목코드 = code_df.종목코드.map('{:06d}'.format) 
        code_df = code_df[['회사명', '종목코드']]
        code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'})
        self.__save_code_list(code_df)
        raise NotImplementedError()

    def get_code_list(self):
        if not self.__check_code_list():
            self.update_code_list()
        raise NotImplementedError()