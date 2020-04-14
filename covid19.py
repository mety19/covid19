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
            className='one columns',
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
            className='two columns',
                    style={'margin-top': '20'}
            )
        ], className="row"
    ),
   

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



if __name__ == '__main__':
    app.run_server()
