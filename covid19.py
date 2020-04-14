import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd



# Read data from https://covidtracking.com/ 
urlus = 'https://covidtracking.com/api/us/daily.csv'
urlst = 'https://covidtracking.com/api/states/daily.csv'
covus = pd.read_csv(urlus)
covus.loc[covus['states']>1,'states'] = 'US'
covst = pd.read_csv(urlst)

# The US data does not have a fips column, we add fips = 0
covus['fips'] = 0

# Select columns that are relevant, same columns for US and states
# Rename state columns to match US column names
covus = pd.DataFrame(covus[['dateChecked', 'states', 'positive', 'negative', 'hospitalized', 'death', 'total'
                            , 'totalTestResults', 'fips', 'deathIncrease', 'hospitalizedIncrease'
                            , 'negativeIncrease', 'positiveIncrease', 'totalTestResultsIncrease']])
covst = pd.DataFrame(covst[['dateChecked', 'state', 'positive', 'negative', 'hospitalized', 'death', 'total'
                            , 'totalTestResults', 'fips', 'deathIncrease', 'hospitalizedIncrease'
                            , 'negativeIncrease', 'positiveIncrease', 'totalTestResultsIncrease']])
covst.columns = ['dateChecked', 'states', 'positive', 'negative', 'hospitalized', 'death', 'total'
                            , 'totalTestResults', 'fips', 'deathIncrease', 'hospitalizedIncrease'
                            , 'negativeIncrease', 'positiveIncrease', 'totalTestResultsIncrease']

# Append the two dataframes and make date a datatime type 
covall = covus.append(covst, sort=False)
covall['Date'] = pd.to_datetime(covall['dateChecked'])
statesall = covall['states'].unique()

# cumulative and incremental columns
Cumulative = ['Date', 'states', 'totalTestResults', 'positive', 'hospitalized', 'death', 'total']
Incremental = ['Date', 'states', 'totalTestResultsIncrease', 'positiveIncrease', 'hospitalizedIncrease', 'deathIncrease', 'total']



server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, server=server)

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
    ], className = "row"),
    
     html.Div([
        html.Div([
            html.P('Choose State:', style = {'backgroundcolor': '#060606', 'color': '#FEFCFC'}),
            dcc.Dropdown(
                    id = 'State',
                    options=[
                        {'label': k, 'value': k} for k in statesall
                        ]
                    ,
                    value=['US'],
                    multi=True
                    )  
                ],
                className='six columns',
                        style={'margin-top': '10'}
                ),
        html.Div([
            html.P('Choose Values:', style = {'backgroundcolor': '#060606', 'color': '#FEFCFC'}),
            dcc.RadioItems(
                    id = 'CumulIncr',
                    options=[
                        {'label': 'Cumulative', 'value': 'Cumulative'},
                        {'label': 'Incremental', 'value': 'Incremental'},
                        {'label': 'Rate', 'value': 'Rate'}
                        ],
                    style={'backgroundcolor': '#060606', 'color': '#FEFCFC'},
                    value='Cumulative'
                    )  
            ],
            className='six columns',
                    style={'margin-top': '10'}
            )
        ], className="row"
    ),    
        
#             
             
    html.Div([
        html.Div([
            dcc.Graph(
                id='tests',
                figure={
                    'data': [],
                    'layout': {
                        'title': 'Tests Given Per Day',
                        'plot_bgcolor': '2A2828',#colors['background'],
                        'paper_bgcolor': '2A2828',
                        'font': {
                            'color': colors['text']
                        }
                    }
                }
            )
        ], className = "six columns"),
        html.Div([
            dcc.Graph(
                id='positive',
                figure={
                    'data': [],
                    'layout': {
                        'title': 'Positive Tests Per Day',
                        'plot_bgcolor': '2A2828',
                        'paper_bgcolor': '2A2828',
                        'font': {
                            'color': colors['text'],
                            'size' : 12
                        }
                    }
                }
            )
        ], className = "six columns")
        
    ], className = "row"),

    html.Div([
        html.Div([
            dcc.Graph(
                id='hospitalized',
                figure={
                    'data': [],
                    'layout': {
                        'title': 'Hospitalized Patients Per Day',
                        'plot_bgcolor': '2A2828',
                        'paper_bgcolor': '2A2828',
                        'font': {
                            'color': colors['text']
                        }
                    }
                }
            )
        ], className = "six columns"),
        html.Div([
            dcc.Graph(
                id='death',
                figure={
                    'data': [],
                    'layout': {
                        'title': 'Deaths Per Day',
                        'plot_bgcolor': '2A2828',
                        'paper_bgcolor': '2A2828',
                        'font': {
                            'color': colors['text']
                        }
                    }
                }
            )
        ], className = "six columns")
    ], className = "row")

])

@app.callback(
        dash.dependencies.Output('tests', 'figure'),
        [dash.dependencies.Input('State', 'value')
        , dash.dependencies.Input('CumulIncr', 'value')])
def update_graph_src(statesel, cumulincr):
    data = []
    if cumulincr=='Cumulative':
        covsel = covall[Cumulative]
    elif cumulincr=='Incremental':
        covsel = covall[Incremental]
    elif cumulincr=='Rate':
        covsel = covall[Cumulative]
        covsel.iloc[:,2:6] = covsel.iloc[:,2:6].div(covsel.total, axis=0)
    for state in statesel:
        data.append({'x': covsel.loc[covall['states'] == state]['Date'], 'y': covsel.loc[covsel['states'] == state].iloc[:,2], 'type': 'line', 'name': state})
                     #, 'marker' : { "color" : '#095D6E', "size": 30}})                                  
    figure = {
            'data': data,
            'layout': {
                        'title': 'Tests Given Per Day',
                        'plot_bgcolor': '2A2828',
                        'paper_bgcolor': '2A2828',
                        'font': {
                            'color': colors['text'],
                            'size' : 12
                        }
                    }
            }
    return figure

@app.callback(
        dash.dependencies.Output('positive', 'figure'),
        [dash.dependencies.Input('State', 'value')
        , dash.dependencies.Input('CumulIncr', 'value')])
def update_graph_src(statesel, cumulincr):
    data = []
    if cumulincr=='Cumulative':
        covsel = covall[Cumulative]
    elif cumulincr=='Incremental':
        covsel = covall[Incremental]
    elif cumulincr=='Rate':
        covsel = covall[Cumulative]
        covsel.iloc[:,2:6] = covsel.iloc[:,2:6].div(covsel.total, axis=0)
    for state in statesel:
        data.append({'x': covsel.loc[covall['states'] == state]['Date'], 'y': covsel.loc[covsel['states'] == state].iloc[:,3], 'type': 'line', 'name': state})
                     #, 'marker' : { "color" : '#095D6E', "size": 30}})                                  
    figure = {
            'data': data,
            'layout': {
                        'title': 'Positive Tests Per Day',
                        'plot_bgcolor': '2A2828',
                        'paper_bgcolor': '2A2828',
                        'font': {
                            'color': colors['text'],
                            'size' : 12
                        }
                    }
            }
    return figure

@app.callback(
        dash.dependencies.Output('hospitalized', 'figure'),
        [dash.dependencies.Input('State', 'value')
        , dash.dependencies.Input('CumulIncr', 'value')])
def update_graph_src(statesel, cumulincr):
    data = []
    if cumulincr=='Cumulative':
        covsel = covall[Cumulative]
    elif cumulincr=='Incremental':
        covsel = covall[Incremental]
    elif cumulincr=='Rate':
        covsel = covall[Cumulative]
        covsel.iloc[:,2:6] = covsel.iloc[:,2:6].div(covsel.total, axis=0)
    for state in statesel:
        data.append({'x': covsel.loc[covall['states'] == state]['Date'], 'y': covsel.loc[covsel['states'] == state].iloc[:,4], 'type': 'line', 'name': state})
                     #, 'marker' : { "color" : '#095D6E', "size": 30}})                                  
    figure = {
            'data': data,
            'layout': {
                        'title': 'Hospitalized Patients Per Day',
                        'plot_bgcolor': '2A2828',
                        'paper_bgcolor': '2A2828',
                        'font': {
                            'color': colors['text'],
                            'size' : 12
                        }
                    }
            }
    return figure

@app.callback(
        dash.dependencies.Output('death', 'figure'),
        [dash.dependencies.Input('State', 'value')
        , dash.dependencies.Input('CumulIncr', 'value')])
def update_graph_src(statesel, cumulincr):
    data = []
    if cumulincr=='Cumulative':
        covsel = covall[Cumulative]
    elif cumulincr=='Incremental':
        covsel = covall[Incremental]
    elif cumulincr=='Rate':
        covsel = covall[Cumulative]
        covsel.iloc[:,2:6] = covsel.iloc[:,2:6].div(covsel.total, axis=0)
    for state in statesel:
        data.append({'x': covsel.loc[covall['states'] == state]['Date'], 'y': covsel.loc[covsel['states'] == state].iloc[:,5], 'type': 'line', 'name': state})
                     #, 'marker' : { "color" : '#095D6E', "size": 30}})                                  
    figure = {
            'data': data,
            'layout': {
                        'title': 'Deaths Per Day',
                        'plot_bgcolor': '2A2828',
                        'paper_bgcolor': '2A2828',
                        'font': {
                            'color': colors['text'],
                            'size' : 12
                        }
                    }
            }
    return figure



if __name__ == '__main__':
    app.run_server()
    #app.server.run(debug=True, threaded=True)
