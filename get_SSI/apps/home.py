import pandas as pd
from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from app import app
from app import server

layout = html.Div([
    dbc.Row(dbc.Col(html.H3('Please select a link'),
                    width={'size': 6, 'offset': 0}
                    ), )
])
