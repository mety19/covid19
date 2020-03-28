# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

#import pandas as pd
#import numpy as np
#import seaborn as sns
#import matplotlib.pyplot as plt
#
#amd = pd.read_csv('C:/Users/Emma/Downloads/genelevel_rsem_expectedcounts_byrid.matrix.tsv',delimiter='\t',encoding='utf-8', header=1)
#amd = np.transpose(amd)
#print(amd.head())

#from flask import Flask
#server = Flask('covidapp')


import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go

#app = dash.react.Dash('dash app name', server=server)

app = dash.Dash()

urlus = 'https://covidtracking.com/api/us/daily.csv'
urlst = 'https://covidtracking.com/api/states/daily.csv'
covus = pd.read_csv(urlus)
covst = pd.read_csv(urlst)
covnony = pd.DataFrame(covst[~covst['state'].isin(['NY'])])
covny = pd.DataFrame(covst[covst['state'].isin(['NY'])])

covus['Date'] = pd.to_datetime(covus['dateChecked'])
covus["posrate"] = covus["positive"]/covus["totalTestResults"]

covny['Date'] = pd.to_datetime(covny['dateChecked'])
covny["posrate"] = covny["positive"]/covny["totalTestResults"]

NYrates = pd.DataFrame(covny.groupby("dateChecked")["positive"].sum()/covny.groupby("dateChecked")
                       ["totalTestResults"].sum())
NYrates.columns = ["posrate"]

covnyr = covny[['dateChecked', 'totalTestResults']]
NYnewtests = pd.DataFrame(-covnyr.set_index('dateChecked').diff()["totalTestResults"])

sansNYrates = pd.DataFrame(covnony.groupby("dateChecked")["positive"].sum()/covnony.groupby("dateChecked")
                           ["totalTestResults"].sum())
sansNYrates.columns = ["posrate"]

covusr = covus[['dateChecked', 'totalTestResults']]
sansNYnewtests = pd.DataFrame(-covusr.set_index('dateChecked').diff()["totalTestResults"])

indexNamesArr = NYrates.index.values
datesr = pd.to_datetime(list(indexNamesArr))
indexNamesArr = NYnewtests.index.values
datest = pd.to_datetime(list(indexNamesArr))


#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']



app.layout = html.Div(children=[
    html.H1(children='COVID-19 CASE TRACKING'),

    html.Div(children='''
        US and NY Positive Test Rates and New Cases
    '''),

    dcc.Graph(
        id='rates',
        figure={
            'data': [
                {'x': datesr, 'y': sansNYrates["posrate"], 'type': 'line', 'name': 'US without NY'},
                {'x': datesr, 'y': NYrates["posrate"], 'type': 'line', 'name': 'NY'},
            ],
            'layout': {
                'title': 'Positive Test Rate'
            }
        }
    ),
    dcc.Graph(
        id='tests',
        figure={
            'data': [
                {'x': datest, 'y': sansNYnewtests['totalTestResults'], 'type': 'line', 'name': 'US without NY'},
                {'x': datest, 'y': NYnewtests['totalTestResults'], 'type': 'line', 'name': 'NY'},
            ],
            'layout': {
                'title': 'Incremental Positive Tests'
            }
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
    #app.server.run()