import pandas as pd 





def get_url(item_name, code_df): 
    code = code_df[code_df['name'] == item_name]['code']
    print(code, type(code))
    url = 'http://finance.naver.com/item/sise_day.nhn?code=%06d' % code
    return url 

code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0]
code_df = code_df[['회사명', '종목코드']]
code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'})
code_df['code'] = pd.to_numeric(code_df['code'])
item_name='삼성전자' 
url = get_url(item_name, code_df)
df = pd.DataFrame() 
for page in range(1, 21): 
    # page당 10일
    pg_url = '{url}&page={page}'.format(url=url, page=page) 
    print(pg_url)
    df = df.append(pd.read_html(pg_url, header=0)[0], ignore_index=True) 
    df = df.dropna() 
    print(df)

