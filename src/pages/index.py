import dash
from dash import html

dash.register_page(__name__, path='/', name="About")

layout = html.Div([
    html.Div("lol"),
], style={'margin': '20px'})