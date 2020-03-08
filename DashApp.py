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

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

file_dir =(r"C:\Users\Notandi\Desktop\Hote\FlightOptimization\UploadedFiles")
df = pd.DataFrame({'Revenue':[0], 'Plane Number':[0]})

if not os.path.exists(file_dir):
    os.makedirs(file_dir)

server = Flask(__name__)
app = dash.Dash(server=server)

app.layout = html.Div([
                    html.Div([html.H1("Flight Optimization Tool", style={'color': 'black', 'fontsize': 24}),]),
                    html.Div([
                        html.H2("Upload"),
                        dcc.Upload(
                            id="upload-data",
                            children=html.Div(["Drag and drop or click to select a .csv file to upload."]),
                            style={
                                "width": "50%",
                                "height": "60px",
                                "lineHeight": "60px",
                                "borderWidth": "1px",
                                "borderStyle": "dashed",
                                "borderRadius": "5px",
                                "textAlign": "center",
                                "margin": "10px",
                            },
                            multiple=True,),
                        ]),
                    html.Div([
                        html.Div(children='Select numer of planes'),
                        dcc.Slider(id='nr_plane_slider', min=1, max=10, step=1, marks={1: '1', 2: '2', 3: '3', 4: '3', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: '10'},value=1),],),

                    html.Div([
                        html.Div(children='Select plane turnaround time'),
                        dcc.Slider(id='turnaround_time_slider', min=1, max=3, step=1, marks={1: '1', 2: '2', 3: '3',}, value=1),], className='two columns'),


                    dcc.Graph(id='Total Revenue', figure=go.Figure(go.Indicator())),
                    dcc.Graph(id='Revenue_by_plane', figure=go.Figure(go.Indicator())),
                    dcc.Graph(id='Gantt', figure=go.Figure(go.Indicator())),
                ],className = 'row', style={"max-width": "1000px", 'backgroundColor':'#F5F5F5', 'font':'Garamond'},)

def save_file(name, content):
    """Decode and store a file uploaded with Plotly Dash."""
    data = content.encode("utf8").split(b";base64,")[1]
    with open(os.path.join(file_dir, name), "wb") as fp:
        fp.write(base64.decodebytes(data))

def prep_gantt(df,df_solved):
    df_gantt = pd.DataFrame()
    plane = 1

    for path in df_solved['Path'].tolist():
        df_flightpath = df[df['FlightNumber'].isin(path)]
        df_flightpath['Resource'] = 'Plane ' + str(plane)
        plane = plane +1
        df_flightpath['Task'] = df_flightpath['FlightNumber']
        df_flightpath['Start'] = df_flightpath['departureDate']
        df_flightpath['Finish'] = df_flightpath['returnDate']
        df_flightpath = df_flightpath.sort_values(by='Start', ascending=False)
        df_gantt = df_gantt.append(df_flightpath, ignore_index=True)
    return df_gantt

def prep_plane_rev(df):
    df = df.sort_values(by='Revenue', ascending=True)
    df['text'] = '$' + df['Revenue'].astype(str)
    data = go.Bar(
        x=df['Revenue'],
        y=df['Plane Number'],
        name='Household savings, percentage of household disposable income',
        orientation='h',
        text=df['text'],
        textposition='auto',)

    layout = go.Layout(title='Revenue by plane')
    return go.Figure(data=data, layout=layout)

def prep_total_rev(df):
    sum = 0
    for rev in df['Revenue'].tolist():
        sum = sum + rev

    figure = go.Figure(go.Indicator(mode = "number",value = sum,number = {'prefix': "$"},domain = {'x': [0, 1], 'y': [0, 1]}))
    return figure

@app.callback(
    [Output("Revenue_by_plane", "figure"), Output("Gantt","figure"), Output("Total Revenue","figure")],
    [Input("upload-data", "filename"), Input("upload-data", "contents"), Input("nr_plane_slider", "value"), Input("turnaround_time_slider", "value")],
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
        figure = go.Figure(go.Indicator())
        g_figure = go.Figure(go.Indicator())
        total_rev = go.Figure(go.Indicator())

    else:
        for f in files:
            if f.endswith('.csv'):
                df = pd.read_csv(os.path.join(file_dir, f))
                df_solved = FO.solve(df,int(nr_planes_value),int(turnaround_time_value))

                df_gantt = prep_gantt(df, df_solved)
                g_figure = ff.create_gantt(df_gantt, index_col='Resource', show_colorbar=True,bar_width=1.5, height=1000)

                figure = prep_plane_rev(df_solved)

                total_rev = prep_total_rev(df_solved)
    return figure, g_figure, total_rev


if __name__ == '__main__':
    app.run_server(debug=True)
