import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd


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
    'background': '#060606', #FEFCFC for white
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
                className='five columns',
                        style={'margin-top': '20'}
                ),
            
        
        html.Div([
            html.P('Choose Values:', style = {'backgroundcolor': '#060606', 'color': '#FEFCFC'}),
            dcc.RadioItems(
                    id = 'CumulIncr',
                    options=[
                        {'label': 'Cumulative', 'value': 'Cumulative'},
                        {'label': 'Incremental', 'value': 'Incremental'},
                        {'label': 'Rate Per Million', 'value': 'Rate Per Million'},
                        {'label': 'Other Rates', 'value': 'Other Rates'}
                        ],
                    style={'backgroundcolor': '#060606', 'color': '#FEFCFC'},
                    value='Cumulative'
                    )  
            ],
            className='two columns',
                    style={'margin-top': '20'}
            ),
        html.Div([
            html.P('Scale:', style = {'backgroundcolor': '#060606', 'color': '#FEFCFC'}),
            dcc.RadioItems(
                    id = 'Scale',
                    options=[
                        {'label': 'Raw', 'value': 'Raw'},
                        {'label': 'Log', 'value': 'Log'}
                        ],
                    style={'backgroundcolor': '#060606', 'color': '#FEFCFC'},
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
        covsel.iloc[:,2:7] = np.log(covsel.iloc[:,2:7])
    #covsum = covsel.loc[covsel['states'] == statesel]
    #covsum = covsum.groupby([covsum['Date'].dt.date]).sum()
    #covsel.loc[covsel['states'] == 'US'].loc[:,2]=2*covsel.loc[covsel['states'] == 'US'].iloc[:,2]-covsum.iloc[:,2]
    for state in statesel:
        data.append({'x': covsel.loc[covsel['states'] == state]['Date'], 'y': covsel.loc[covsel['states'] == state].iloc[:,2], 'type': 'line'
                     , 'mode': 'lines+markers', 'type': 'line', 'marker': {'size': 10}, 'line': {'width' : 3}, 'name': state})
                     #, 'marker' : { "color" : '#095D6E', "size": 30}})                                  
    figure = {
            'data': data,
            'layout': {
                        'title': plottitle,
                        'plot_bgcolor': '2A2828',
                        'paper_bgcolor': '2A2828',
                        'font': {
                            'color': colors['text'],
                            'size' : 16
                        }
                    }
                        
            #'layout': go.Layout(title='Tests Given Per Day', )
            }
    return figure

if __name__ == '__main__':
    app.run_server()
