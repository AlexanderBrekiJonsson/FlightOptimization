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

file_dir =(r"C:\Users\Notandi\Desktop\Hote\FlightOptimization\UploadedFiles")
df = pd.DataFrame()
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
    ],
    style={"max-width": "500px"},
)

def save_file(name, content):
    """Decode and store a file uploaded with Plotly Dash."""
    data = content.encode("utf8").split(b";base64,")[1]
    with open(os.path.join(file_dir, name), "wb") as fp:
        fp.write(base64.decodebytes(data))

@app.callback(
    [Output("table", "columns"), Output("table", "data")],
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
        df = pd.DataFrame()
        columns=[{"name": i, "id": i} for i in df.columns]
        data=df.to_dict('records')

    else:
        for f in files:
            if f.endswith('.csv'):
                df = pd.read_csv(os.path.join(file_dir, f))
                df = FO.solve(df,int(nr_planes_value),int(turnaround_time_value))
                df = df[['Plane Number', 'Revenue']]
                columns=[{"name": i, "id": i} for i in df.columns]
                data=df.to_dict('records')

    return columns, data

if __name__ == '__main__':
    app.run_server(debug=True)
