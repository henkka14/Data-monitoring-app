import dash
from dash.dependencies import Output, Event
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import datetime as dt
import readdata
import threading

rd = readdata.ReadData()

app = dash.Dash(__name__)
schd = rd.get_scheduler()
schd.add_job(rd.retrieve_sensor_values, 'interval', seconds=1)
thread = threading.Thread(target=schd.start)


app.layout = html.Div(children=[
  html.H1('Spin tester monitoring'),
        dcc.Graph(id='tension-graph'),
        dcc.Interval(
            id='graph-update-interval',
            interval=1*1000,
            n_intervals=0
        ),
    ]
)

def get_data():
    dates, kilograms = [], []
    
    for i in rd.get_db():
        dates.append(i['Date'])
        kilograms.append(i['Kilograms'])

    return dates, kilograms


@app.callback(Output('tension-graph', 'figure'),
              events=[Event('graph-update-interval', 'interval')])
def update_graph_scatter():
    dates, kilograms = get_data()
    data = go.Scatter(
            x=dates,
            y=kilograms,
            name='kg',
            mode= 'lines+markers'
            )
    get_data()
    return {'data': [data], 'layout': go.Layout(showlegend=True,
                                                title='Tension and compression measurements'
                                                )}

if __name__ == '__main__':
    thread.start()
    app.run_server(host='0.0.0.0')
