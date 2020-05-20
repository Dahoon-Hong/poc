from urllib import request, parse

"""
어제 날씨
현재 날씨 (온도, 기상)
어제 동시간대 대비 +-
내일 날씨 (오늘 동시간대 날씨 +-)
"""


import json
# Python 샘플 코드 #
API_KEY = 'sVxRb9xnn5lKF9nHWILoNtwrNqKmP2gnEQiLIWFwjP%2FCDj%2FusdgXowaSL%2F8k1ulL4e1KxndObMYTbX6L9ipDiA%3D%3D'
API_ENDPOINT = 'http://apis.data.go.kr/1360000/VilageFcstInfoService'
#단기실황 
API_NCAT_PATH = '/getUltraSrtNcst'
#단기조회 
API_FCST_PATH = '/getUltraSrtFcst'
#예보조회 
API_FCST_VILAGE_PATH = '/getVilageFcst'


def dfs(data, key_chain=[]):
    if not isinstance(data, dict):
        return
    
    for key in data:
        _key_chain = key_chain.copy()
        _key_chain.append(key)
        if isinstance(data[key], dict):
            dfs(data[key], _key_chain)
        elif isinstance(data[key], list):
            for idx, item in enumerate(data[key]):
                print('%s : [%s]' % (''.join(['[%s]' % k for k in _key_chain + [idx]]), item))    
        else:
            print('%s : [%s]' % (''.join(['[%s]' % k for k in _key_chain]), data[key]))


queryParams = '?' + "ServiceKey=" + API_KEY +'&'+ parse.urlencode({
    'ServiceKey': API_KEY,
    'pageNo': '1',
    'numOfRows': '60',
    'dataType': 'JSON',
    'base_date': '20200520',
    'base_time': '0900',
    'nx': '55',
    'ny': '127'})
print('REQUEST TO ', API_ENDPOINT + API_FCST_VILAGE_PATH + queryParams)
response = request.urlopen(API_ENDPOINT + API_FCST_VILAGE_PATH + queryParams).read()
print(response)
#response = b'{"response":{"header":{"resultCode":"00","resultMsg":"NORMAL_SERVICE"},"body":{"dataType":"JSON","items":{"item":[{"baseDate":"20200520","baseTime":"0630","category":"LGT","fcstDate":"20200520","fcstTime":"0700","fcstValue":"0","nx":18,"ny":1},{"baseDate":"20200520","baseTime":"0630","category":"LGT","fcstDate":"20200520","fcstTime":"0800","fcstValue":"0","nx":18,"ny":1},{"baseDate":"20200520","baseTime":"0630","category":"LGT","fcstDate":"20200520","fcstTime":"0900","fcstValue":"0","nx":18,"ny":1},{"baseDate":"20200520","baseTime":"0630","category":"LGT","fcstDate":"20200520","fcstTime":"1000","fcstValue":"0","nx":18,"ny":1},{"baseDate":"20200520","baseTime":"0630","category":"LGT","fcstDate":"20200520","fcstTime":"1100","fcstValue":"0","nx":18,"ny":1},{"baseDate":"20200520","baseTime":"0630","category":"LGT","fcstDate":"20200520","fcstTime":"1200","fcstValue":"0","nx":18,"ny":1},{"baseDate":"20200520","baseTime":"0630","category":"PTY","fcstDate":"20200520","fcstTime":"0700","fcstValue":"0","nx":18,"ny":1},{"baseDate":"20200520","baseTime":"0630","category":"PTY","fcstDate":"20200520","fcstTime":"0800","fcstValue":"0","nx":18,"ny":1},{"baseDate":"20200520","baseTime":"0630","category":"PTY","fcstDate":"20200520","fcstTime":"0900","fcstValue":"0","nx":18,"ny":1},{"baseDate":"20200520","baseTime":"0630","category":"PTY","fcstDate":"20200520","fcstTime":"1000","fcstValue":"0","nx":18,"ny":1}]},"pageNo":1,"numOfRows":10,"totalCount":60}}}'
result = json.loads(response.decode("UTF-8"))

print('---------------------------')
dfs(result)