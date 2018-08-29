"""The module is responsible for graphical plotting with Dash."""

import threading
import datetime as dt
import re
import sqlite3
import time

import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import peakutils

import readdata

data_reader = readdata.ReadData()
app = dash.Dash(__name__)

def data_timer(*args, interval=0.00001):
    """Gather data at the given interval."""
    data_reader.retrieve_sensor_values()
    next_int=int(args[0])+1
    threading.Timer(interval, data_timer,[str(next_int)]).start()

app.layout = html.Div(children=[
        html.H1('Spin tester monitoring'),
        html.Div(id='graphs'),
        dcc.Interval(
            id='graph-update-interval',
            interval=1*1000,
            n_intervals=0,
        ),
    ]
)

def get_data():
    """
    Get the data from SQLite database
    that is created in readdata module.
    """
    conn = sqlite3.connect(
        data_reader.dbname,
        detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES
        )
    c = conn.cursor()
    c.execute('SELECT * FROM monitoring_table')
    our_data = c.fetchall()
    conn.close()

    return our_data

@app.callback(Output('graphs', 'children'),
        [Input('graph-update-interval', 'n_intervals')])
def _(n):
    graphs = []
    our_data = list(zip(*get_data()))

    if len(our_data[0]) > 300:
        indices = len(peakutils.indexes(our_data[2][-100:], thres=0.5))
        seco = (our_data[0][-1] - our_data[0][-100]).total_seconds()
        rpm.append(indices/seco*60)
        count_up.append(len(rpm))

    data_kg = go.Scatter(
            x=list(our_data[0]),
            y=list(our_data[1]),
            name='kg',
            mode= 'lines+markers',
            )

    data_rounds = go.Scatter(
            x=count_up,
            y=rpm,
            name='rpm',
            mode= 'lines+markers',
            )


    graphs.append(dcc.Graph(id="kg", figure={'data': [data_kg], 'layout': go.Layout(showlegend=True,
                                                title='Tension and compression measurements'
                                                )}))

    graphs.append(dcc.Graph(id="rounds", figure={'data': [data_rounds], 'layout': go.Layout(showlegend=True,
                                                title='Round measurements'
                                                )}))
    return graphs

if __name__ == '__main__':
    rpm = []
    count_up = []
    data_timer("1")
    app.run_server(host='0.0.0.0')
