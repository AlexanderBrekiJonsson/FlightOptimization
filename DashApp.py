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

UPLOAD_DIRECTORY =(r"C:\Users\Notandi\Desktop\Hote\FlightOptimization\UploadedFiles")
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

df = pd.DataFrame()

server = Flask(__name__)
app = dash.Dash(server=server)

@server.route("/download/<path:path>")
def download(path):
    """Serve a file from the upload directory."""
    return send_from_directory(UPLOAD_DIRECTORY, path, as_attachment=True)


app.layout = html.Div(
    [
        html.H1("Flight Optimization Tool"),
        
        html.H2("Upload"),
        #html.Div([dcc.Input(id='dash_input', value='TEST', type='text')]),
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
    with open(os.path.join(UPLOAD_DIRECTORY, name), "wb") as fp:
        
        fp.write(base64.decodebytes(data))


def uploaded_files():
    """List the files in the upload directory."""
    files = []
    for filename in os.listdir(UPLOAD_DIRECTORY):
        path = os.path.join(UPLOAD_DIRECTORY, filename)
        if os.path.isfile(path):
            files.append(filename)
    return files


def file_download_link(filename):
    """Create a Plotly Dash 'A' element that downloads a file from the app."""
    location = "/download/{}".format(urlquote(filename))
    return html.A(filename, href=location)


@app.callback(
    [Output("table", "columns"), Output("table", "data")],
    [Input("upload-data", "filename"), Input("upload-data", "contents")],


)

def update_output(uploaded_filenames, uploaded_file_contents):
    """Save uploaded files and regenerate the file list."""
    mydir = r"C:\Users\Notandi\Desktop\Hote\FlightOptimization\UploadedFiles"

    if uploaded_filenames is not None and uploaded_file_contents is not None:
        for name, data in zip(uploaded_filenames, uploaded_file_contents):
            if name.endswith('.csv'):
                print('CSV file uploaded')
                save_file(name, data)                
            else:
                print('Not a CSV file!')
    files = os.listdir(mydir)
    if len(files) == 0:
        df = pd.DataFrame()
        columns=[{"name": i, "id": i} for i in df.columns]
        data=df.to_dict('records')

    else: 
        for f in files:
            if f.endswith('.csv'):
                df = pd.read_csv(os.path.join(mydir, f))
                columns=[{"name": i, "id": i} for i in df.columns]
                data=df.to_dict('records')
        
        for f in files:
            print(f)
            os.remove(os.path.join(mydir, f))


    
    return columns, data    

if __name__ == '__main__':
    app.run_server(debug=True)
