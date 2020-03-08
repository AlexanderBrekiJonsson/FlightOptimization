import datetime
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from flask import Flask, send_from_directory
import base64
import os
from urllib.parse import quote as urlquote
import numpy as np
import pandas as pd
import dash_table
import FlightOptimization as FO
import plotly.graph_objects as go
import plotly.figure_factory as ff

file_dir =(r"C:\Users\Notandi\Desktop\Hote\FlightOptimization\UploadedFiles")
df = pd.DataFrame({'Revenue':[0], 'Plane Number':[0]})

df_gantt = pd.read_csv('test.csv')
df_gantt['Task'] = df_gantt['FlightNumber']
df_gantt['Start'] = df_gantt['departureDate']
df_gantt['Finish'] = df_gantt['returnDate']
df_gantt['Resource'] = 'Plane 1'
df_gantt = df_gantt.sort_values(by='Start', ascending=False)

if not os.path.exists(file_dir):
    os.makedirs(file_dir)

server = Flask(__name__)
app = dash.Dash(server=server)

app.layout = html.Div(
    [
        html.H1("Flight Optimization Tool"),
        html.H2("Upload"),
        dcc.Upload(
            id="upload-data",
            children=html.Div(
                ["Drag and drop or click to select a .csv file to upload."]
            ),
            style={
                "width": "100%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
            },
            multiple=True,
        ),
        html.Div(children='Select numer of planes'),
        html.Div([dcc.Input(id='nr_planes', value='1', type='number')]),
        html.Div(children='Select plane turnaround time'),
        html.Div([dcc.Input(id='turnaround_time', value='1', type='number')]),

        html.H2("Flight List"),
        dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        ),
        dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'y': df['Revenue'].tolist(), 'x': df['Plane Number'].tolist(), 'type': 'bar', 'name': 'SF'},
            ],
            'layout': {
                'title': 'Dash Data Visualization'
            }
        }
        ),
        dcc.Graph(id='Gantt', figure= ff.create_gantt(df_gantt, index_col='Resource', show_colorbar=True,bar_width=1.5)),

    ],
    style={"max-width": "1000px"},
)

def save_file(name, content):
    """Decode and store a file uploaded with Plotly Dash."""
    data = content.encode("utf8").split(b";base64,")[1]
    with open(os.path.join(file_dir, name), "wb") as fp:
        fp.write(base64.decodebytes(data))


@app.callback(
    [Output("table", "columns"), Output("table", "data"), Output("example-graph", "figure"), Output("Gantt","figure")],
    [Input("upload-data", "filename"), Input("upload-data", "contents"), Input("nr_planes", "value"), Input("turnaround_time", "value")],
)

def update_output(uploaded_filenames, uploaded_file_contents, nr_planes_value, turnaround_time_value):
    """Save uploaded files and regenerate the file list."""

    if uploaded_filenames is not None and uploaded_file_contents is not None:
        for name, data in zip(uploaded_filenames, uploaded_file_contents):
            if name.endswith('.csv'):
                for f in os.listdir(file_dir):
                    print(f)
                    os.remove(os.path.join(file_dir, f))
                print('CSV file uploaded')
                save_file(name, data)
            else:
                print('Not a CSV file!')

    files = os.listdir(file_dir)

    if len(files) == 0:
        df = pd.DataFrame({'Revenue':[0], 'Plane Number':[0]})
        columns=[{"name": i, "id": i} for i in df.columns]
        data=df.to_dict('records')
        figure={
            'data': [
                {'y': df['Revenue'].tolist(), 'x': df['Plane Number'].tolist(), 'type': 'bar', 'name': 'SF'},
            ],
            'layout': {
                'title': 'Dash Data Visualization'
            }
        }
        df_gantt = pd.read_csv('test.csv')
        df_gantt['Task'] = df_gantt['FlightNumber']
        df_gantt['Start'] = df_gantt['departureDate']
        df_gantt['Finish'] = df_gantt['returnDate']
        df_gantt['Resource'] = 'Plane 1'
        df_gantt = df_gantt.sort_values(by='Start', ascending=False)
        g_figure = ff.create_gantt(df_gantt, index_col='Resource', show_colorbar=True,bar_width=1.5)

    else:
        for f in files:
            if f.endswith('.csv'):
                df = pd.read_csv(os.path.join(file_dir, f))
                df_solved = FO.solve(df,int(nr_planes_value),int(turnaround_time_value))
                columns=[{"name": i, "id": i} for i in df_solved.columns]

                df_gantt = pd.DataFrame()
                plane = 1
                for path in df_solved['Path'].head().tolist():
                    df_flightpath = df[df['FlightNumber'].isin(path)]
                    df_flightpath['Resource'] = 'Plane ' + str(plane)
                    plane = plane +1

                    df_flightpath['Task'] = df_flightpath['FlightNumber']
                    df_flightpath['Start'] = df_flightpath['departureDate']
                    df_flightpath['Finish'] = df_flightpath['returnDate']
                    df_flightpath = df_flightpath.sort_values(by='Start', ascending=False)
                    df_gantt = df_gantt.append(df_flightpath, ignore_index=True)
                g_figure = ff.create_gantt(df_gantt, index_col='Resource', show_colorbar=True,bar_width=1.5)
                data=df_solved[['Plane Number', 'Revenue']].to_dict('records')
                figure={
                    'data': [
                        {'y': df_solved['Revenue'].tolist(), 'x': df_solved['Plane Number'].tolist(), 'type': 'bar', 'name': 'SF'},
                    ],
                    'layout': {
                        'title': 'Dash Data Visualization'
                    }
                }

    return columns, data, figure, g_figure


if __name__ == '__main__':
    app.run_server(debug=True)
