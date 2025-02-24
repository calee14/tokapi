from dash import Dash, html, dcc, Output, Input
import dash
import plotly.express as px

external_css = []
external_scripts = []

app = Dash(__name__,
           pages_folder='pages',
           use_pages=True,
           external_stylesheets=external_css,
           external_scripts=external_scripts,
           suppress_callback_exceptions=True)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Br(),
    html.P(id='page-title'),
    dash.page_container
], className="bg-dark-blue", style={
    'width': '100%',
    'height': '100vh',  # covers the full viewport height
    'margin': '0',
    'padding': '0'
})

if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=8080)