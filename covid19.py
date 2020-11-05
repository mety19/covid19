import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import datetime as dt

''' PREPARE WORLD DATA '''
# Read data from https://covidtracking.com/ 
urlworld = 'https://covid.ourworldindata.org/data/owid-covid-data.csv'
world = pd.read_csv(urlworld)

# Remove US terriories from world data
usterritories = ['American Samoa', 'Guam', 'Northern Mariana Islands', 'Puerto Rico', 'United States Virgin Islands']
world = world[~world['location'].isin(usterritories)]

# Select World Fields and Rename columns and sort data
worldfields = ['iso_code', 'location',	'date',	'total_cases', 'new_cases',	'total_deaths',	'new_deaths'
               , 'total_cases_per_million',	'new_cases_per_million',	'total_deaths_per_million'
               ,	'new_deaths_per_million', 'total_tests',	'new_tests',	'total_tests_per_thousand'
               ,	'new_tests_per_thousand', 'tests_units']
world = world[worldfields]
world.columns = ['iso_code', 'states', 'dateChecked', 'positive', 'positiveIncrease', 'death', 'deathIncrease', 'positiveMil'
                 , 'positiveIncreaseMil', 'deathMil', 'deathIncreaseMil', 'total', 'totalTestResultsIncrease', 'totalK'
                 , 'totalTestResultsIncreaseK', 'testunits']

world = world.sort_values(by=['states', 'dateChecked'])

# Get country list and fill in blanks with previous values
countryall = world['states'].unique()
for w in countryall:
    country = world.loc[world['states']==w]
    country = country.fillna(method='ffill')
    world.loc[world['states']==w] = country

# Create missing columns that will be in US data
world['area'] = 'World'
world['fips'] = 0
world['negative'] = 0
world['hospitalized'] = 0
world['totalTestResults'] = world['total']
world['hospitalizedIncrease'] = 0
world['negativeIncrease'] = 0

world = pd.DataFrame(world[['dateChecked', 'area', 'states', 'positive', 'negative', 'hospitalized', 'death', 'total', 'totalTestResults', 'fips', 'deathIncrease'
                 , 'hospitalizedIncrease', 'negativeIncrease', 'positiveIncrease', 'totalTestResultsIncrease']])
                

''' PREPARE US DATA '''
# Read data from https://covidtracking.com/ 
urlus = 'https://covidtracking.com/api/v1/us/daily.csv'
urlst = 'https://covidtracking.com/api/v1/states/daily.csv'
covus = pd.read_csv(urlus)
covus.loc[covus['states']>1,'states'] = 'USA'
covst = pd.read_csv(urlst)
covst = covst[covst.dateChecked.notnull()]
covst.state = 'USA'+', '+covst.state

# Read us and world population data
urluspop = 'https://github.com/mety19/covid19/raw/master/uspopulation.csv'
uspop = pd.read_csv(urluspop)
uspop = uspop.iloc[:, 0:2]
uspop.columns =['states', 'population']
uspop.states = 'USA'+', '+uspop.states

urlworldpop = 'https://github.com/mety19/covid19/raw/master/worldpopulation.csv'
worldpop = pd.read_csv(urlworldpop)
worldpop.columns = ['states', 'population']

pop = uspop.append(worldpop, sort=False)

# The US data does not have a fips column, we add fips = 0
covus['fips'] = 0
covus['area'] = 'USA'
covst['area'] = 'USA'

# Select columns that are relevant, same columns for US and states
# Rename state columns to match US column names
covus = pd.DataFrame(covus[['dateChecked', 'area', 'states', 'positive', 'negative', 'hospitalized', 'death', 'total'
                            , 'totalTestResults', 'fips', 'deathIncrease', 'hospitalizedIncrease'
                            , 'negativeIncrease', 'positiveIncrease', 'totalTestResultsIncrease']])
covst = pd.DataFrame(covst[['dateChecked', 'area', 'state', 'positive', 'negative', 'hospitalized', 'death', 'total'
                            , 'totalTestResults', 'fips', 'deathIncrease', 'hospitalizedIncrease'
                            , 'negativeIncrease', 'positiveIncrease', 'totalTestResultsIncrease']])
covst.columns = ['dateChecked', 'area', 'states', 'positive', 'negative', 'hospitalized', 'death', 'total'
                            , 'totalTestResults', 'fips', 'deathIncrease', 'hospitalizedIncrease'
                            , 'negativeIncrease', 'positiveIncrease', 'totalTestResultsIncrease']

# Get US state list and combined jurisdictions
statesall = covst['states'].unique()
statescountryall = np.concatenate([statesall, countryall])

''' COMBINE WORLD AND US DATA'''
# Append the two dataframes and make date, and dateindex datatime types 
world = world.fillna(1)
worldusa = world.append([covus, covst], sort=False)
worldusa['dateChecked'] = worldusa.dateChecked.str.split('T').str[0]
worldusa['Date'] = worldusa['Dateindex'] = pd.to_datetime(worldusa['dateChecked'])

# Merge with population data and get state list
worldusa = pd.merge(worldusa, pop, on='states')

# Get US state list
statesall = worldusa[worldusa.area == 'USA']['states'].unique()

# Create dictionary of US states and world country lists
all_options = {'USA': statesall
               , 'World': countryall
               , 'All': statescountryall}
covall = worldusa

# cumulative and incremental columns
Cumulative = ['Date', 'states', 'totalTestResults', 'positive', 'hospitalized', 'death', 'total', 'population', 'Dateindex', 'dateChecked']
Incremental = ['Date', 'states', 'totalTestResultsIncrease', 'positiveIncrease', 'hospitalizedIncrease', 'deathIncrease', 'total', 'population', 'Dateindex', 'dateChecked']


''' APP '''
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.css.append_css({'external_url': 'https://codepen.io/amyoshino/pen/jzXypZ.css'})

colors = {
    'background': '#030A32', #FEFCFC for white
    'text': '#FEFCFC'  #0E0E0E for black
}


app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.Div([
            
        html.H1(children='World and USA SARS-COV-2 Testing and COVID-19 Tracking', style={
            'textAlign': 'center',
            'color': colors['text']
            })    
    ], className = "row"),
    
 
    
     html.Div([
        html.Div([
                html.Div([
                    html.P('''This app plots data referenced in covidtracking.com and covid.ourworldindata.org. 
                           These datasets have been put together to attempt to aggregate COVID-19 data in the most accurate way
                           ,  and are not necessarily complete in terms of number of tests, cases, hospitalizations or deaths.'''
                           )
                        ], style = {'color': colors['text'], 'textAlign': 'center', 'size': 14}, className = 'row'),

                html.Div([
                        html.A('Data Source: https://covidtracking.com'
                                 , href='https://covidtracking.com/', target='_blank'
                            )
                        ], style = {'textAlign': 'center'}, className = 'row'),
                html.Div([
                        html.A('Data Source: https://covid.ourworldindata.org'
                                 , href='https://covid.ourworldindata.org/', target='_blank'
                            )
                        ], style = {'textAlign': 'center'}, className = 'row'),
                
                html.Div([html.P('')], style = {'textAlign': 'center'}, className = 'row'),
                
                html.Div([
                        html.A('Description of epidemiology variables'
                                 , href='https://github.com/mety19/covid19/blob/master/covid-track%20epidemiology%20variables.txt', target='_blank'
                                 , style = {'color': 'Yellow','textAlign': 'center'}
                            )
                        ], style = {'textAlign': 'center'}, className = 'row')
                               
                ],
                className='four columns',
                        style={'margin-top': '20'}
                ),
                
        html.Div([
                html.P('Scope:', style = {'backgroundcolor': '#030A32', 'color': '#FEFCFC', 'size': 10}),
                dcc.RadioItems(
                    id = 'Scope',
                    options = [
                            {'label': k, 'value': k} for k in all_options.keys()
                            ],
                    style={'backgroundcolor': '#030A32', 'color': '#FEFCFC'},
                    value = 'All'
                    )
                ], className = 'one columns', style = {'margin-top': '20'}),     

        html.Div([
            html.P('State or Country:', style = {'backgroundcolor': '#030A32', 'color': '#FEFCFC'}),
            dcc.Dropdown(
                    id = 'State',
                    value=['United States'],
                    multi=True
                    )  
                ],
                className='two columns',
                        style={'margin-top': '20'}
                ),
        html.Div([
            html.P('Values:', style = {'backgroundcolor': '#030A32', 'color': '#FEFCFC'}),
            dcc.RadioItems(
                    id = 'CumulIncr',
                    options=[
                        {'label': 'Cumulative', 'value': 'Cumulative'},
                        {'label': 'Daily', 'value': 'Incremental'},
                        {'label': 'Rate Per Million', 'value': 'Rate Per Million'},
                        {'label': 'Other Rates', 'value': 'Other Rates'}
                        ],
                    style={'backgroundcolor': '#030A32', 'color': '#FEFCFC', 'size': 10},
                    value='Cumulative'
                    )  
            ],
            className='two columns',
                    style={'margin-top': '20'}
            )
       ,
        html.Div([
            html.P('Smoothing:', style = {'backgroundcolor': '#030A32', 'color': '#FEFCFC'}),
            dcc.RadioItems(
                    id = 'MovingAverage',
                    options=[
                        {'label': 'None', 'value': 'None'},
                        {'label': 'Moving Average 3-Day', 'value': 'Moving Average 3-Day'},
                        {'label': 'Moving Average 7-Day', 'value': 'Moving Average 7-Day'}
                        ],
                    style={'backgroundcolor': '#030A32', 'color': '#FEFCFC', 'size': 10},
                    value='None'
                    )  
            ],
            className='two columns',
                    style={'margin-top': '20'}
            ),
        html.Div([
            html.P('Scale:', style = {'backgroundcolor': '#030A32', 'color': '#FEFCFC', 'size': 10}),
            dcc.RadioItems(
                    id = 'Scale',
                    options=[
                        {'label': 'Raw', 'value': 'Raw'},
                        {'label': 'Log10', 'value': 'Log10'}
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
           html.P('')
           ], className='four columns'),
       
       html.Div([
           dcc.DatePickerRange(
           id = 'DateChoice',
           start_date = dt.datetime(2019, 12, 31),
           end_date = dt.datetime(2020, 12, 31)
           )], className='four columns', style={'text-align': 'center'}),
       html.Div([
           html.P('')
           ], className='four columns')
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
                        'plot_bgcolor': '#030A32',#colors['background'],
                        'paper_bgcolor': '#030A32',
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
                        'plot_bgcolor': '#030A32',
                        'paper_bgcolor': '#030A32',
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
                        'plot_bgcolor': '#030A32',
                        'paper_bgcolor': '#030A32',
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
                        'plot_bgcolor': '#030A32',
                        'paper_bgcolor': '#030A32',
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
        dash.dependencies.Output('State', 'options'),
        [dash.dependencies.Input('Scope', 'value')]
        )
def set_scope_option(selected_scope):
    return [{'label': k, 'value': k} for k in all_options[selected_scope]]
    
@app.callback(
        dash.dependencies.Output('tests', 'figure'),
        [dash.dependencies.Input('State', 'value')
        , dash.dependencies.Input('CumulIncr', 'value')
        , dash.dependencies.Input('Scale', 'value')
        , dash.dependencies.Input('MovingAverage', 'value')
        , dash.dependencies.Input('DateChoice', 'start_date')
        , dash.dependencies.Input('DateChoice', 'end_date')
        ])
def update_graph_src(statesel, cumulincr, scale, movingaverage, start_date, end_date):
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
        covsel.iloc[:,2:7] = 1000000*covsel.iloc[:,2:7].div(covsel.population, axis=0)
        covsel = covsel.round(0)
        plottitle = 'Number of Tests per Million Residents'
    elif cumulincr=='Other Rates':
        covsel = covall[Cumulative]
        covsel.iloc[:,2:7] = covsel.iloc[:,2:7].div(covsel.population, axis=0)
        covsel = covsel.round(4)
        plottitle = 'Number of Tests per Resident'
        
    if scale =='Raw':
        covsel = covsel
    elif scale=='Log10':
        covsel.iloc[:,2:7] = np.log10(covsel.iloc[:,2:7])      
        
    covsel = covsel.sort_values(by='Dateindex')
    covsel.set_index('Dateindex', inplace=True)
    covsel = covsel.loc[start_date:end_date]
        
    for state in statesel:
        covstate = pd.DataFrame(covsel.loc[covsel['states'] == state])
        if movingaverage =='None':
            covstate = covstate
        elif movingaverage == 'Moving Average 3-Day':
            covstate.iloc[:,2] = covstate.iloc[:,2].rolling(3).mean().shift(-2)
        elif movingaverage == 'Moving Average 7-Day':
            covstate.iloc[:,2] = covstate.iloc[:,2].rolling(7).mean().shift(-6)
        data.append({'x':  covstate.Date, 'y': covstate.iloc[:,2], 'type': 'line'
                     , 'mode': 'lines+markers', 'type': 'line', 'marker': {'size': 8}, 'line': {'width' : 3}, 'name': state})
                               
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
    
    elif scale == 'Log10':                         
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
        , dash.dependencies.Input('MovingAverage', 'value')
        , dash.dependencies.Input('DateChoice', 'start_date')
        , dash.dependencies.Input('DateChoice', 'end_date')
        ])
def update_graph_src(statesel, cumulincr, scale, movingaverage, start_date, end_date):
    data = []
    if cumulincr=='Cumulative':
        covsel = covall[Cumulative]
        plottitle = 'Cumulative Number of Positive Tests'
    elif cumulincr=='Incremental':
        covsel = covall[Incremental]
        plottitle = 'Daily Number of Positive Tests'
    elif cumulincr=='Rate Per Million':
        covsel = covall[Cumulative]
        covsel.iloc[:,2:7] = 1000000*(covsel.iloc[:,2:7].div(covsel.population, axis=0))
        covsel = covsel.round(0)
        plottitle = 'Number of Positive Tests per Million Residents'
    elif cumulincr=='Other Rates':
        covsel = covall[Cumulative]
        covsel.iloc[:,2:7] = (covsel.iloc[:,2:7].div(covsel.total, axis=0))
        covsel = covsel.round(4)
        covsel.iloc[:,2:7]=covsel.iloc[:,2:7].mask(covsel.iloc[:,2:7].gt(0.99),0)
        plottitle = 'Number of Positive Tests per Test'
        
    if scale =='Raw':
        covsel = covsel
    elif scale=='Log10':
        covsel.iloc[:,2:7] = np.log10(covsel.iloc[:,2:7])      
        
    covsel = covsel.sort_values(by='Dateindex')
    covsel.set_index('Dateindex', inplace=True)
    covsel = covsel.loc[start_date:end_date]   
    
    for state in statesel:
        covstate = pd.DataFrame(covsel.loc[covsel['states'] == state])
        if movingaverage =='None':
            covstate = covstate
        elif movingaverage == 'Moving Average 3-Day':
            covstate.iloc[:,3] = covstate.iloc[:,3].rolling(3).mean().shift(-2)
        elif movingaverage == 'Moving Average 7-Day':
            covstate.iloc[:,3] = covstate.iloc[:,3].rolling(7).mean().shift(-6)
        data.append({'x':  covstate.Date, 'y': covstate.iloc[:,3], 'type': 'line'
                     , 'mode': 'lines+markers', 'type': 'line', 'marker': {'size': 8}, 'line': {'width' : 3}, 'name': state})
        
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
    
    elif scale == 'Log10':                         
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
        , dash.dependencies.Input('MovingAverage', 'value')
        , dash.dependencies.Input('DateChoice', 'start_date')
        , dash.dependencies.Input('DateChoice', 'end_date')
        ])
def update_graph_src(statesel, cumulincr, scale, movingaverage, start_date, end_date):
    data = []
    if cumulincr=='Cumulative':
        covsel = covall[Cumulative]
        plottitle = 'Cumulative Number of Hospitalized Patients'
    elif cumulincr=='Incremental':
        covsel = covall[Incremental]
        plottitle = 'Daily Number of Hospitalized Patients'
    elif cumulincr=='Rate Per Million':
        covsel = covall[Cumulative]
        covsel.iloc[:,2:7] = 1000000*covsel.iloc[:,2:7].div(covsel.population, axis=0)
        covsel = covsel.round(0)
        plottitle = 'Number of Hospitalized Patients per Million Residents'
    elif cumulincr=='Other Rates':
        covsel = covall[Cumulative]
        covsel.iloc[:,2:7] = covsel.iloc[:,2:7].div(covsel.iloc[:,3], axis=0)
        covsel = covsel.round(4)
        plottitle = 'Number of Hospitalized Patients per Positive Test'
        
    if scale =='Raw':
        covsel = covsel
    elif scale=='Log10':
        covsel.iloc[:,2:7] = np.log10(covsel.iloc[:,2:7])      
        
    covsel = covsel.sort_values(by='Dateindex')
    covsel.set_index('Dateindex', inplace=True)
    covsel = covsel.loc[start_date:end_date]
        
    for state in statesel:
        covstate = pd.DataFrame(covsel.loc[covsel['states'] == state])
        if movingaverage =='None':
            covstate = covstate
        elif movingaverage == 'Moving Average 3-Day':
            covstate.iloc[:,4] = covstate.iloc[:,4].rolling(3).mean().shift(-2)
        elif movingaverage == 'Moving Average 7-Day':
            covstate.iloc[:,4] = covstate.iloc[:,4].rolling(7).mean().shift(-6)
        data.append({'x':  covstate.Date, 'y': covstate.iloc[:,4], 'type': 'line'
                     , 'mode': 'lines+markers', 'type': 'line', 'marker': {'size': 8}, 'line': {'width' : 3}, 'name': state})
                                  
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
    
    elif scale == 'Log10':                         
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
        , dash.dependencies.Input('MovingAverage', 'value')
        , dash.dependencies.Input('DateChoice', 'start_date')
        , dash.dependencies.Input('DateChoice', 'end_date')
        ])
def update_graph_src(statesel, cumulincr, scale, movingaverage, start_date, end_date):
    data = []
    if cumulincr=='Cumulative':
        covsel = covall[Cumulative]
        plottitle = 'Cumulative Number of Deaths'
    elif cumulincr=='Incremental':
        covsel = covall[Incremental]
        plottitle = 'Daily Number Deaths'
    elif cumulincr=='Rate Per Million':
        covsel = covall[Cumulative]
        covsel.iloc[:,2:7] = 1000000*covsel.iloc[:,2:7].div(covsel.population, axis=0)
        covsel = covsel.round(0)
        plottitle = 'Number of Deaths per Million Residents'
    elif cumulincr=='Other Rates':
        covsel = covall[Cumulative]
        covsel.iloc[:,2:7] = covsel.iloc[:,2:7].div(covsel.iloc[:,3], axis=0)
        covsel = covsel.round(4)
        plottitle = 'Number of Deaths per Positive Test'
    
    if scale =='Raw':
        covsel = covsel
    elif scale=='Log10':
        covsel.iloc[:,2:7] = np.log10(covsel.iloc[:,2:7])      
        
    covsel = covsel.sort_values(by='Dateindex')
    covsel.set_index('Dateindex', inplace=True)
    covsel = covsel.loc[start_date:end_date]
        
    for state in statesel:
        covstate = pd.DataFrame(covsel.loc[covsel['states'] == state])
        if movingaverage =='None':
            covstate = covstate
        elif movingaverage == 'Moving Average 3-Day':
            covstate.iloc[:,5] = covstate.iloc[:,5].rolling(3).mean().shift(-2)
        elif movingaverage == 'Moving Average 7-Day':
            covstate.iloc[:,5] = covstate.iloc[:,5].rolling(7).mean().shift(-6)
        data.append({'x':  covstate.Date, 'y': covstate.iloc[:,5], 'type': 'line'
                     , 'mode': 'lines+markers', 'type': 'line', 'marker': {'size': 8}, 'line': {'width' : 3}, 'name': state})
                               
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
    
    elif scale == 'Log10':                         
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
    app.server.run()

