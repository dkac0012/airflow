import dash
from dash import html,dcc
import pandas as pd
import pymysql

# MySQL에 연결하기 위한 변수 설정
host = "localhost"
port = 3306
user = "afirst"
password = "airf"
database = "upbitbtc"

# MySQL에서 데이터 가져오기
connection = pymysql.connect(host=host, port=port, user=user, password=password, database=database)
cursor = connection.cursor()
cursor.execute("SELECT * FROM upbit_data")
data = cursor.fetchall()

# 데이터프레임으로 변환
df = pd.DataFrame(data)
# 이동 평균을 계산합니다.
MA20 = df[4].rolling(20).mean()

# 볼린저 밴드를 계산합니다.
upper_band = MA20 + 2 * df[4].rolling(20).std()
lower_band = MA20 - 2 * df[4].rolling(20).std()

# MFI  = 100-(100/(1+긍정적 현금 흐름/부정적 현금흐름))
# 긍정적 현금 흐름 : 중심 가격이 전일보다 상승한 날들의 현금 흐름의 합
# 부정적 현금 흐름 : 중심 가격이 전일 보다 하락한 날들의 현금 흐름의 합
df['TP']= (df[2]+df[3]+[4])/3
df['PMF'] = 0
df['NMF'] = 0 
for i in range(len(df[4])-1):
    if(df.TP.values[i] < df.TP.values[i+1]):
        df.PMF.values[i+1] = df.TP.values[i+1] * df[5].values[i+1]
        df.NMF.values[i+1] = 0
    else:
        df.NMF.values[i+1] = df.TP.values[i+1] * df[5].values[i+1]
        df.PMF.values[i+1] = 0
df['MFR'] = df.PMF.rolling(10).sum()/df.NMF.rolling(10).sum()
df['MFI10'] = 100 - 100/(1+df['MFR'])



# 볼린저 밴드를 대시보드에 표시합니다.
figure = dcc.Graph(
    figure={
        "data": [
            {"x": df[0], "y": MA20, "type": "line","color":"black"},
            {"x": df[0], "y": upper_band, "type": "line", "linestyle": "dashed","fillcolor":"blue"},
            {"x": df[0], "y": lower_band, "type": "line", "linestyle": "dashed","fillcolor":"blue"},
        ],
        "layout": {
            "title": "볼린저 밴드"
        }
    }
)

# Dash 앱을 생성합니다.
app = dash.Dash()
app.layout = html.Div(children=[figure])

# Dash 앱을 실행합니다.
app.run_server(debug=True,host='0.0.0.0')
