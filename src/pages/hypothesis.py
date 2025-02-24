import dash
from dash import html, dcc, callback, Output, Input

dash.register_page(__name__, path='/hypothesis', name="Hypothesis", order=2)

# Define the hypothesis description with bold text.
description = html.Div(
    html.P([
        "We believe that TikTok is ",
        html.B("a music trend setter"),
        " rather than a mirror of existing musical trends."
    ], style={'fontSize': '20px', 'textAlign': 'center', 'margin': '10px 0'}),
    style={'margin': '10px 0'}
)

# Create bullet points with inline LaTeX expressions for additional metrics.
measurements = html.Div([
    html.P("We can figure this out by measuring:", style={'fontSize': '20px', 'textAlign': 'center'}),
    html.Div(
        html.Ul([
            html.Li([
                "The popularity spike magnitudes of TikTok and Spotify ",
                dcc.Markdown(
                    "$\\rightarrow\\ \\text{ correlation coefficient, C}$", 
                    mathjax=True, 
                    style={'textAlign': 'center', 'display': 'inline-block'}
                )
            ]),
            html.Li([
                "When popularity spikes happen relative to each other ",
                dcc.Markdown(
                    "$\\rightarrow\\ \\text{ time delay, }\\;t_d$", 
                    mathjax=True, 
                    style={'textAlign': 'center', 'display': 'inline-block'}
                )
            ])
        ], style={
            'fontSize': '20px',
            'display': 'inline-block',
            'textAlign': 'left',
            'listStylePosition': 'inside',
            'padding': '0'
        }),
        style={'textAlign': 'center'}
    )
], style={'margin': '10px 0'})

layout = html.Div([
    html.H1("Hypothesis", style={'textAlign': 'center', 'marginTop': '80px', 'marginBottom': '20px'}),
    description,
    measurements
], style={'margin': '20px'})

@callback(
    Output('url', 'pathname'),
    Input('back-btn', 'n_clicks'),
    prevent_initial_call=True
)
def navigate_back(n_clicks):
    if n_clicks:
        return '/'