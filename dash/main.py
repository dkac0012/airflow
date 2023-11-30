import dash
from dash import html,dcc,Input,Output
import plotly.graph_objects as go
import pymysql
import pandas as pd

# MySQL에 연결하기 위한 변수 설정
host = "localhost"
port = 3306
user = ""
password = ""
database = "upbitbtc"

# MySQL에서 데이터 가져오기
connection = pymysql.connect(host=host, port=port, user=user, password=password, database=database)
cursor = connection.cursor()
cursor.execute("SELECT * FROM upbit_data")
data = cursor.fetchall()

app = dash.Dash()
# 데이터프레임으로 변환
df = pd.DataFrame(data)

# 차트 그리기
close_chart = go.Figure(data=[go.Scatter(x=df[0], y=df[4], mode="lines")])
close_chart.update_layout(title="추세선")
volume_chart = go.Figure(data=[go.Bar(x=df[0], y=df[5])])
close_chart.update_layout(title="거래량")

@app.callback(
    Output('check-value','figure'),
    Input('checklist', 'value'),
)
def golden_cross(values):
    fig = go.Figure()
    for value in values:
        cdf = df[4].rolling(value).mean()
        fig.add_trace(go.Scatter(x=df[0], y=cdf, name=f'Rolling {value}'))
    return fig
        
def candle_chart(df):
    df["Open"] = df[1].astype(float)
    df["High"] = df[2].astype(float)
    df["Low"] = df[3].astype(float)
    df["Close"] = df[4].astype(float)
    return {
        "data": [
            {"x": df[0], "open": df[1], "high": df[2], "low": df[3], "close": df[4], "type": "candlestick"}
        ],
        "layout": {
            "title": "캔들 차트"
        }
    }

# 대시보드 생성
# html.Div(children='볼륨차트'),
app.layout = html.Div([
    # dcc.Graph(figure=volume_chart),
    dcc.Graph(figure=candle_chart(df)),
    dcc.Checklist(
    options=[
        {'label': 5, 'value': 5},
        {'label': 20, 'value': 20},
        {'label': 60, 'value': 60}
    ],
    labelStyle={'display': 'inline-block'},
    value=[5],
    id='checklist'
    ),  
    dcc.Graph(id='check-value')
])


# 대시보드 실행
app.run_server(host='0.0.0.0')
