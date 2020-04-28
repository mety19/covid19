import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import requests

# Read data from https://covidtracking.com/ 
urlus = 'https://covidtracking.com/api/us/daily.csv'
urlst = 'https://covidtracking.com/api/states/daily.csv'
urlpop = 'https://github.com/mety19/covid19/raw/master/uspopulation.csv'
covus = pd.read_csv(urlus)
covus.loc[covus['states']>1,'states'] = 'US'
covst = pd.read_csv(urlst)
uspop = pd.read_csv(urlpop)

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

# Merge with population data and get state list
covall = pd.merge(covall, uspop, on='states')
statesall = covall['states'].unique()

# cumulative and incremental columns
Cumulative = ['Date', 'states', 'totalTestResults', 'positive', 'hospitalized', 'death', 'total', 'population2019']
Incremental = ['Date', 'states', 'totalTestResultsIncrease', 'positiveIncrease', 'hospitalizedIncrease', 'deathIncrease', 'total', 'population2019']


''' APP '''
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

colors = {
    'background': '#030A32', #FEFCFC for white
    'text': '#FEFCFC'  #0E0E0E for black
}


app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.Div([
            
        html.H1(children='USA SARS-COV-2 Testing and COVID-19 Tracking', style={
            'textAlign': 'center',
            'color': colors['text']
            }
            )
    ], className = "row"),
    
 
    
     html.Div([
        html.Div([
                html.Div([
                    html.P('This app plots the data referenced in covidtracking.com,  which has been put together to attempt to aggregate covid testing data for the US in the most accurate way,  and is not necessarily complete in terms of number of hospitalizations or deaths.'
                           )
                        ], style = {'color': colors['text'], 'textAlign': 'center', 'size': 16}, className = "row"),

                html.Div([
                        html.A("Data Source: https://covidtracking.com"
                                 , href='https://covidtracking.com/', target="_blank"
                            )
                        ], style = {'color': colors['text'],'textAlign': 'center'}, className = "row") 
                ],
                className='three columns',
                        style={'margin-top': '20'}
                ),
            
        html.Div([
            html.P('Choose State:', style = {'backgroundcolor': '#030A32', 'color': '#FEFCFC'}),
            dcc.Dropdown(
                    id = 'State',
                    options=[
                        {'label': k, 'value': k} for k in statesall
                        ]
                    ,
                    value=['US', 'NY'],
                    multi=True
                    )  
                ],
                className='five columns',
                        style={'margin-top': '20'}
                ),
            
        
        html.Div([
            html.P('Choose Values:', style = {'backgroundcolor': '#030A32', 'color': '#FEFCFC'}),
            dcc.RadioItems(
                    id = 'CumulIncr',
                    options=[
                        {'label': 'Cumulative', 'value': 'Cumulative'},
                        {'label': 'Incremental', 'value': 'Incremental'},
                        {'label': 'Rate Per Million', 'value': 'Rate Per Million'},
                        {'label': 'Other Rates', 'value': 'Other Rates'}
                        ],
                    style={'backgroundcolor': '#030A32', 'color': '#FEFCFC'},
                    value='Cumulative'
                    )  
            ],
            className='two columns',
                    style={'margin-top': '20'}
            ),
        html.Div([
            html.P('Scale:', style = {'backgroundcolor': '#030A32', 'color': '#FEFCFC'}),
            dcc.RadioItems(
                    id = 'Scale',
                    options=[
                        {'label': 'Raw', 'value': 'Raw'},
                        {'label': 'Log', 'value': 'Log'}
                        ],
                    style={'backgroundcolor': '#030A32', 'color': '#FEFCFC'},
                    value='Raw'
                    )  
            ],
            className='one columns',
                    style={'margin-top': '20'}
            )
        ], className="row"
    ),
   
  html.Div([
        html.Div([
            dcc.Graph(
                id='tests',
                figure={
                    'data': [],
                    'layout': {
                        'title': 'Tests Given Per Day',
                        'plot_bgcolor': '030A32',#colors['background'],
                        'paper_bgcolor': '030A32',
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
                        'plot_bgcolor': '030A32',
                        'paper_bgcolor': '030A32',
                        'font': {
                            'color': colors['text'],
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
                        'plot_bgcolor': '030A32',
                        'paper_bgcolor': '030A32',
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
                        'plot_bgcolor': '030A32',
                        'paper_bgcolor': '030A32',
                        'font': {
                            'color': colors['text']
                        }
                    }
                }
            )
        ], className = "six columns")
    ], className = "row", style={'margin-top': '20'}),

    html.Div([
            html.P('For questions or comments contact'
                           , style={
                                        'textAlign': 'center',
                                        'color': '#DFD9D9'
                                    }),
            html.P('Jeffrey S Morris - jeffrey.morris@pennmedicine.upenn.edu'
                           , style={
                                        'textAlign': 'center',
                                        'color': '#DFD9D9'
                                    }),
            html.P('Emma Zohner - emma.zohner@rice.edu'
                           , style={
                                        'textAlign': 'center',
                                        'color': '#DFD9D9'
                                    })
            ], className="row", style={'margin-top': '20'})
])

@app.callback(
        dash.dependencies.Output('tests', 'figure'),
        [dash.dependencies.Input('State', 'value')
        , dash.dependencies.Input('CumulIncr', 'value')
        , dash.dependencies.Input('Scale', 'value')
        ])
def update_graph_src(statesel, cumulincr, scale):
    data = []
    if cumulincr=='Cumulative':
        covsel = covall[Cumulative]
        covsel = covsel.round(2)
        plottitle = 'Cumulative Number of Tests'
    elif cumulincr=='Incremental':
        covsel = covall[Incremental]
        covsel = covsel.round(2)
        plottitle = 'Daily Number of Tests'
    elif cumulincr=='Rate Per Million':
        covsel = covall[Cumulative]
        covsel.iloc[:,2:7] = 1000000*covsel.iloc[:,2:7].div(covsel.population2019, axis=0)
        covsel = covsel.round(0)
        plottitle = 'Number of Tests per Million Residents'
    elif cumulincr=='Other Rates':
        covsel = covall[Cumulative]
        covsel.iloc[:,2:7] = covsel.iloc[:,2:7].div(covsel.population2019, axis=0)
        covsel = covsel.round(4)
        plottitle = 'Number of Tests per Resident'
        
    if scale =='Raw':
        covsel = covsel
    elif scale=='Log':
        covsel.iloc[:,2:7] = np.log10(covsel.iloc[:,2:7])
        
    for state in statesel:
        data.append({'x': covsel.loc[covsel['states'] == state]['Date'], 'y': covsel.loc[covsel['states'] == state].iloc[:,2], 'type': 'line'
                     , 'mode': 'lines+markers', 'type': 'line', 'marker': {'size': 10}, 'line': {'width' : 3}, 'name': state})
                               
    if scale == 'Raw':                         
        figure = {
                'data': data,
                'layout': {
                            'title': plottitle,
                            'plot_bgcolor': '282D46',
                            'paper_bgcolor': '282D46',
                            'font': {
                                'color': colors['text'],
                                'size' : 16
                            }
                        }
                }
        return figure
    
    elif scale == 'Log':                         
        figure = {
                'data': data,
                'layout': {
                            'title': plottitle,
                            'plot_bgcolor': '282D46',
                            'paper_bgcolor': '282D46',
                            'font': {
                                'color': colors['text'],
                                'size' : 16
                            },
                            'yaxis': {
                                    'tickvals': [0,1,2,3,4,5,6,7,8],
                                    'ticktext': ['1', '10', '100', '1K', '10K', '100K', '1M', '10M', '100M']
                                    }
                        }
                }
        return figure
      
@app.callback(
        dash.dependencies.Output('positive', 'figure'),
        [dash.dependencies.Input('State', 'value')
        , dash.dependencies.Input('CumulIncr', 'value')
        , dash.dependencies.Input('Scale', 'value')
        ])
def update_graph_src(statesel, cumulincr, scale):
    data = []
    if cumulincr=='Cumulative':
        covsel = covall[Cumulative]
        plottitle = 'Cumulative Number of Positive Tests'
    elif cumulincr=='Incremental':
        covsel = covall[Incremental]
        plottitle = 'Daily Number of Positive Tests'
    elif cumulincr=='Rate Per Million':
        covsel = covall[Cumulative]
        covsel.iloc[:,2:7] = 1000000*(covsel.iloc[:,2:7].div(covsel.population2019, axis=0))
        covsel = covsel.round(0)
        plottitle = 'Number of Positive Tests per Million Residents'
    elif cumulincr=='Other Rates':
        covsel = covall[Cumulative]
        covsel.iloc[:,2:7] = (covsel.iloc[:,2:7].div(covsel.total, axis=0))
        covsel = covsel.round(4)
        plottitle = 'Number of Positive Tests per Test'
        
    if scale =='Raw':
        covsel = covsel
    elif scale=='Log':
        covsel.iloc[:,2:7] = np.log10(covsel.iloc[:,2:7])
        
    for state in statesel:
        data.append({'x': covsel.loc[covall['states'] == state]['Date'], 'y': covsel.loc[covsel['states'] == state].iloc[:,3], 'type': 'line'
                     , 'mode': 'lines+markers', 'type': 'line', 'marker': {'size': 10}, 'line': {'width' : 3}, 'name': state})
                                
    if scale == 'Raw':                         
        figure = {
                'data': data,
                'layout': {
                            'title': plottitle,
                            'plot_bgcolor': '282D46',
                            'paper_bgcolor': '282D46',
                            'font': {
                                'color': colors['text'],
                                'size' : 16
                            }
                        }
                }
        return figure
    
    elif scale == 'Log':                         
        figure = {
                'data': data,
                'layout': {
                            'title': plottitle,
                            'plot_bgcolor': '282D46',
                            'paper_bgcolor': '282D46',
                            'font': {
                                'color': colors['text'],
                                'size' : 16
                            },
                            'yaxis': {
                                    'tickvals': [0,1,2,3,4,5,6,7,8],
                                    'ticktext': ['1', '10', '100', '1K', '10K', '100K', '1M', '10M', '100M']
                                    }
                        }
                }
        return figure
  
@app.callback(
        dash.dependencies.Output('hospitalized', 'figure'),
        [dash.dependencies.Input('State', 'value')
        , dash.dependencies.Input('CumulIncr', 'value')
        , dash.dependencies.Input('Scale', 'value')
        ])
def update_graph_src(statesel, cumulincr, scale):
    data = []
    if cumulincr=='Cumulative':
        covsel = covall[Cumulative]
        plottitle = 'Cumulative Number of Hospitalized Patients'
    elif cumulincr=='Incremental':
        covsel = covall[Incremental]
        plottitle = 'Daily Number of Hospitalized Patients'
    elif cumulincr=='Rate Per Million':
        covsel = covall[Cumulative]
        covsel.iloc[:,2:7] = 1000000*covsel.iloc[:,2:7].div(covsel.population2019, axis=0)
        covsel = covsel.round(0)
        plottitle = 'Number of Hospitalized Patients per Million Residents'
    elif cumulincr=='Other Rates':
        covsel = covall[Cumulative]
        covsel.iloc[:,2:7] = covsel.iloc[:,2:7].div(covsel.iloc[:,3], axis=0)
        covsel = covsel.round(4)
        plottitle = 'Number of Hospitalized Patients per Positive Test'
        
    if scale =='Raw':
        covsel = covsel
    elif scale=='Log':
        covsel.iloc[:,2:7] = np.log10(covsel.iloc[:,2:7])
        
    for state in statesel:
        data.append({'x': covsel.loc[covall['states'] == state]['Date'], 'y': covsel.loc[covsel['states'] == state].iloc[:,4]
                     , 'mode': 'lines+markers', 'type': 'line', 'marker': {'size': 10}, 'line': {'width' : 3}, 'name': state})
                                  
    if scale == 'Raw':                         
        figure = {
                'data': data,
                'layout': {
                            'title': plottitle,
                            'plot_bgcolor': '282D46',
                            'paper_bgcolor': '282D46',
                            'font': {
                                'color': colors['text'],
                                'size' : 16
                            }
                        }
                }
        return figure
    
    elif scale == 'Log':                         
        figure = {
                'data': data,
                'layout': {
                            'title': plottitle,
                            'plot_bgcolor': '282D46',
                            'paper_bgcolor': '282D46',
                            'font': {
                                'color': colors['text'],
                                'size' : 16
                            },
                            'yaxis': {
                                    'tickvals': [0,1,2,3,4,5,6,7,8],
                                    'ticktext': ['1', '10', '100', '1K', '10K', '100K', '1M', '10M', '100M']
                                    }
                        }
                }
        return figure

@app.callback(
        dash.dependencies.Output('death', 'figure'),
        [dash.dependencies.Input('State', 'value')
        , dash.dependencies.Input('CumulIncr', 'value')
        , dash.dependencies.Input('Scale', 'value')
        ])
def update_graph_src(statesel, cumulincr, scale):
    data = []
    if cumulincr=='Cumulative':
        covsel = covall[Cumulative]
        plottitle = 'Cumulative Number of Deaths'
    elif cumulincr=='Incremental':
        covsel = covall[Incremental]
        plottitle = 'Daily Number Deaths'
    elif cumulincr=='Rate Per Million':
        covsel = covall[Cumulative]
        covsel.iloc[:,2:7] = 1000000*covsel.iloc[:,2:7].div(covsel.population2019, axis=0)
        covsel = covsel.round(0)
        plottitle = 'Number of Deaths per Million Residents'
    elif cumulincr=='Other Rates':
        covsel = covall[Cumulative]
        covsel.iloc[:,2:7] = covsel.iloc[:,2:7].div(covsel.iloc[:,3], axis=0)
        covsel = covsel.round(4)
        plottitle = 'Number of Deaths per Positive Test'
    
    if scale =='Raw':
        covsel = covsel
    elif scale=='Log':
        covsel.iloc[:,2:7] = np.log10(covsel.iloc[:,2:7])
        
    for state in statesel:
        data.append({'x': covsel.loc[covall['states'] == state]['Date'], 'y': covsel.loc[covsel['states'] == state].iloc[:,5]
        , 'mode': 'lines+markers', 'type': 'line', 'marker': {'size': 10}, 'line': {'width' : 3}, 'name': state})
                               
    if scale == 'Raw':                         
        figure = {
                'data': data,
                'layout': {
                            'title': plottitle,
                            'plot_bgcolor': '282D46',
                            'paper_bgcolor': '282D46',
                            'font': {
                                'color': colors['text'],
                                'size' : 16
                            }
                        }
                }
        return figure
    
    elif scale == 'Log':                         
        figure = {
                'data': data,
                'layout': {
                            'title': plottitle,
                            'plot_bgcolor': '282D46',
                            'paper_bgcolor': '282D46',
                            'font': {
                                'color': colors['text'],
                                'size' : 16
                            },
                            'yaxis': {
                                    'tickvals': [0,1,2,3,4,5,6,7,8],
                                    'ticktext': ['1', '10', '100', '1K', '10K', '100K', '1M', '10M', '100M']
                                    }
                        }
                }
        return figure

if __name__ == '__main__':
    app.run_server()
