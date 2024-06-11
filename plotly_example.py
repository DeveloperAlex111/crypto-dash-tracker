import pandas as pd
import datetime as dt
import pandas_datareader as dr
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from binance_funcs import get_historical_ohlc_data, get_symbols, TIME_UNITS, AMOUNT_OF_DAYS

app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
app.title = "Candlestick chart"
symbol_dropdown = html.Div([
    html.P('Symbol:'),
    dcc.Dropdown(
        id='symbol-dropdown',
        options=[{'label': symbol, 'value': symbol} for symbol in get_symbols()],
        value='BTCUSDT'
    )
])

timeunit_dropdown = html.Div([
    html.P('Time units:'),
    dcc.Dropdown(
        id='timeunit-dropdown',
        options=[{'label': unit, 'value': unit} for unit in TIME_UNITS],
        value='1h'
    )
])

amount_days_dropdown = html.Div([
    html.P('Amount of days:'),
    dcc.Dropdown(
        id='amount_of_days-dropdown',
        options=[{'label': amount_of_days, 'value': amount_of_days} for amount_of_days in AMOUNT_OF_DAYS],
        value='3'
    )
])


app.layout = html.Div([
    html.H1('Real Time Charts from Binance.com'),
    dbc.Row([
        dbc.Col(symbol_dropdown),
        dbc.Col(timeunit_dropdown),
        dbc.Col(amount_days_dropdown)
    ]),
    html.Hr(),

    dcc.Interval(id='update', interval=5000),


    html.Div(id='page-content')

], style={'margin-left': '5%', 'margin-right': '5%', 'margin-top': '20px'})


@app.callback(
    Output('page-content', 'children'),
    [Input('update', 'n_intervals')],
    State('symbol-dropdown', 'value'), State('timeunit-dropdown', 'value'), State('amount_of_days-dropdown', 'value')
)

def update_ohlc_chart(interval, symbol, unit, amount_of_days):
    
    timeframe_str = unit
    amount_of_days = int(amount_of_days)
    data_candles = get_historical_ohlc_data(symbol, amount_of_days, unit)
   
    fig_chart = make_subplots(rows=2, #making a plotly subplots (two charts in one graph)
                              cols=1,  
                              shared_xaxes=True,
                              row_heights=[0.7, 0.3],
                              vertical_spacing=0.05,
                              )
    
    fig_chart.add_trace(go.Candlestick(x=data_candles.open_date_time, 
                                        low = data_candles['low'],
                                        high = data_candles['high'],
                                        close = data_candles['close'],
                                        open = data_candles['open'],
                                        increasing_line_color = 'green',
                                        decreasing_line_color = 'red', 
                                        name=symbol),
                                        row=1, col=1)
    
    fig_chart.add_trace(go.Scatter(x=data_candles["open_date_time"],
                                   y=data_candles["hma"], 
                                   name="HMA", 
                                   mode="lines", 
                                   line_color="#000fff",),
                                   row=1, col=1)
    
    fig_chart.add_trace(go.Scatter(x=data_candles["open_date_time"], 
                                y=data_candles["rsi"],
                                name='RSI',),
                                row=2, col=1)
    
    fig_chart.add_hline(y=70, line_width=1, line_dash="dash", line_color="red", row=2, col=1, annotation_text="Overbought > 70%")
    fig_chart.add_hline(y=50, line_width=1, line_dash="dash", line_color="yellow", row=2, col=1)  
    fig_chart.add_hline(y=30, line_width=1, line_dash="dash", line_color="red", row=2, col=1, annotation_text="Oversold < 30%")   

    fig_chart.update_layout(height=700,
                    title_text="Candlestick chart "+symbol+" with the Hull Moving Average (HMA) and Relative Strength Index (RSI) Indicators",
                    template="plotly_dark",
                    yaxis={'side': 'right'},
                    yaxis_title="Value"
    )

    fig_chart.update(layout_xaxis_rangeslider_visible=False)
        
    fig_chart.layout.xaxis.fixedrange = True
    fig_chart.layout.yaxis.fixedrange = True



    return [
        html.H2(id='chart-details', children=f'{symbol} - {timeframe_str}'),
        dcc.Graph(figure=fig_chart, config={'displayModeBar': False})
        ]


if __name__ == '__main__':
    # starts the server
    app.run_server()

