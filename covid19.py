#import os
import dash
#import dash_core_components as dcc
import dash_html_components as html
import pandas as pd


''' APP '''

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.css.append_css({'external_url': 'https://codepen.io/amyoshino/pen/jzXypZ.css'})

colors = {
    'background': '#060606', #FEFCFC for white
    'text': '#FEFCFC'  #0E0E0E for black
}


app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.Div([
            
        html.H1(children='US COVID19 CASE TRACKING', style={
            'textAlign': 'center',
            'color': colors['text']
            }
            ),
    
        html.Div(children='Data source: https://covidtracking.com/', style={
                'textAlign': 'center',
                'color': colors['text']
            })
    ], className = "row")

])



if __name__ == '__main__':
    app.run_server(debug=True)
