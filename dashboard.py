import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, dcc, html, Input, Output,State
from datetime import date
from dash import dash_table as dt
import main_script
pd.options.plotting.backend = "plotly"


benchmark_stats = pd.DataFrame({'Values': ["N/A","N/A","N/A","N/A"],'Backtest': ["N/A","N/A","N/A","N/A"], 'Sector': ["N/A","N/A","N/A","N/A"]})
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)
# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([

    html.H1("Web Application Dashboards with Dash", style={'text-align': 'center'}),

    dcc.Dropdown(id="select_sector",
                 options=[
                     {"label": "BANK", "value": "BANK"},
                     {"label": "ENERG", "value": "ENERG"},
                     {"label": "SET50", "value": "SET50"},
                     #{"label": "PERSON", "value": "PERSON"},
                     {"label": "AGRO", "value": "AGRO"},
                     #{"label": "CONSUMP", "value": "CONSUMP"}, # not a single stock got more than 36000 datapoints
                     {"label": "FINCIAL", "value": "FINCIAL"},
                     #{"label": "INDUS", "value": "INDUS"}, #got only two stocks investigate later
                     {"label": "RESOURC", "value": "RESOURC"},
                     {"label": "SERVICE", "value": "SERVICE"},
                     {"label": "TECH", "value": "TECH"},
                     ],
                 multi=False,
                 style={'width': "40%"}
                 ),
    dcc.DatePickerRange(
        id='date_range',
        min_date_allowed=date(2018, 1, 1),
        max_date_allowed=date(2020, 11, 23),
        initial_visible_month=date(2018, 1, 1),
        end_date=date(2020, 11, 23),
        style={'width': "40%"}
    ),
    #dt.DataTable(
    #    id='trade_stats', data=df.to_dict('records'),
    #    columns=[{"name": i, "id": i} for i in df.columns],
    #),
    html.Br(),
    dcc.Input(
            id="start_cash",
            type="number",
            placeholder="start cash",
            style={'width': "40%"}
    ),
    html.Button(id='submit-button-state', n_clicks=0, children='Submit'),
    html.Div(id='benchmark_stats',children=[]),
    html.Br(),
    html.Div(id='trade_stats',children=[]),
    html.Br(),
    dcc.Graph(id='port_compare', figure={}),
    html.Br(),
    dcc.Graph(id='drawdown_compare', figure={}),
    html.Br(),
    dcc.Graph(id='port_z_score', figure={}),
    

])


# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    Output(component_id='port_compare', component_property='figure'),
    Output(component_id='drawdown_compare', component_property='figure'),
    Output(component_id='port_z_score', component_property='figure'),
    Output(component_id='benchmark_stats',component_property='children'),
    Output(component_id='trade_stats',component_property='children'),
    Input('submit-button-state', 'n_clicks'),
    State(component_id='select_sector',component_property="value"),
    State(component_id='date_range',component_property="start_date"),
    State(component_id='date_range',component_property="end_date"),
    State(component_id='start_cash',component_property="value"),

)
def update(n_clicks,sector,start_date,end_date,start_cash):
    print(sector)
    print(type(sector))
    print(start_date)
    print(type(start_date))
    print(end_date)
    print(type(end_date))
    print(start_cash)
    print(type(start_cash))
    global benchmark_stats
    #container = f"{sector} from {start_date} to {end_date} with {start_cash} start_cash."
    trade_stats,benchmark_stats,port_val_log,benchmark_price,z_score = main_script.main(sector,start_date,end_date,start_cash)
    
    ## Plot
    #Compare Backtest and Benchmark Port
    fig_compare = benchmark_price[['BacktestPort','SectorPort']].plot(title="Portfolio value Backtest vs Sector(benchmark)", template="simple_white",
              labels=dict(index="time", value="money"))
    #Compare Backtest and Benchmark DrawDown
    fig_DD = go.Figure()
    fig_DD.add_trace(go.Scatter(x = benchmark_price.index,y= benchmark_price["BackTestPortDD"],mode = 'lines',name="Backtest",fill = 'tozeroy'))
    fig_DD.add_trace(go.Scatter(x = benchmark_price.index,y= benchmark_price["SectorPriceDD"],mode = 'lines',name="Sector",fill = 'tozeroy'))
    fig_DD.update_layout(
        title="DrawDown Backtest vs Sector(Benchmark) (The less negative The better)",
        xaxis_title="Time",
        yaxis_title="DrawDown(%)",
    )
    print(type(fig_DD))
    #Port with z_score
    fig_z_score = make_subplots(specs=[[{"secondary_y": True}]])
    fig_z_score.add_trace(go.Scatter(x = z_score["Time"],y= z_score["z_score"],mode = 'lines',name="z_score",line=dict(color='rgba(0, 0, 255, 0.25)')),secondary_y= True)
    fig_z_score.add_trace(go.Scatter(x = port_val_log.index,y= port_val_log["PortValue"],mode = 'lines',name="BacktestPort",),secondary_y= False)
    fig_z_score.add_hline(y=0.5,secondary_y = True,line_dash="dash",line=dict(color='rgba(0, 0, 0, 0.5)'))
    fig_z_score.add_hline(y=-0.5,secondary_y = True,line_dash="dash",line=dict(color='rgba(0, 0, 0, 0.5)'))
    fig_z_score.add_hline(y=2.0,secondary_y = True,line=dict(color='rgba(0, 0, 0, 0.5)'))
    fig_z_score.add_hline(y=-2.0,secondary_y = True,line=dict(color='rgba(0, 0, 0, 0.5)'))
    fig_z_score.update_layout(
        title="BacktestPort with z_score",
        xaxis_title="Time",
    )
    print(type(fig_z_score))

    
    benchmark_stats_table = dt.DataTable(data = benchmark_stats.to_dict('records'), columns =  [{"name": i, "id": i} for i in benchmark_stats.columns])
    print("BackTest Success")
    trade_stats_table = dt.DataTable(data = trade_stats.to_dict('records'), columns =  [{"name": i, "id": i} for i in trade_stats.columns])
    return fig_compare,fig_DD,fig_z_score,benchmark_stats_table,trade_stats_table
    #return fig_compare,benchmark_stats_table,trade_stats_table


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
