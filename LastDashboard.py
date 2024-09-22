# -*- coding: utf-8 -
"""
Created on Tue Aug  6 14:37:21 2024

@author: Legion-pc-polimi
"""

import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd
import sqlite3
import plotly.express as px

# Connect to the database and load the data
#db_path = r"C:\Users\Legion-pc-polimi\OneDrive - Politecnico di Milano\Altro\Volley\Conco2324\Palau\Ritorno\2024-04-13 - Serie B1F A - Rit - Giornata 22 - CENTEMERO CONCOR MB Vs CAPO D ORSO PALAU SS - 3-2.db"
db_path = r"C:\Users\mirko\OneDrive - Politecnico di Milano\Altro\Volley\Conco2324\Palau\Ritorno\2024-04-13 - Serie B1F A - Rit - Giornata 22 - CENTEMERO CONCOR MB Vs CAPO D ORSO PALAU SS - 3-2.db"
conn = sqlite3.connect(db_path)
event_df = pd.read_sql_query("SELECT * FROM event", conn)
# Query to get all tables
table_query = "SELECT name FROM sqlite_master WHERE type='table';"
tables = pd.read_sql_query(table_query, conn)

# Create a dictionary to store dataframes
dataframes = {}

# Extract each table into a pandas dataframe
for table_name in tables['name']:
    query = f"SELECT * FROM {table_name}"
    dataframes[table_name] = pd.read_sql_query(query, conn)
conn.close()

# Map IP_fondamentale to skill names
skill_mapping = {
    1: 'Attacco',
    2: "Difesa",
    3: "Muro",
    4: 'Ricezione',
    5: "Alzata",
    6: 'Battuta'
}

event_df['skill'] = event_df['IP_fondamentale'].map(skill_mapping)

# Function to calculate efficiency and positivity
def calculate_metrics(group):
    total = len(group)
    count_5 = len(group[group['mark'] == 5])
    count_4 = len(group[group['mark'] == 4])
    count_0 = len(group[group['mark'] == 0])
    efficiency = (count_5 - count_0) / total if total > 0 else 0
    positivity = (count_5 + count_4) / total if total > 0 else 0
    return pd.Series({'efficiency': efficiency, 'positivity': positivity, 'total': total})

# Calculate metrics for each player and skill
player_metrics = event_df.groupby(['IP_player', 'skill', 'team']).apply(calculate_metrics).reset_index()
# Merge player metrics with player data to get player names
merged_df = player_metrics.merge(dataframes['player'], left_on='IP_player', right_on='id', how='left')
merged_df = merged_df.merge(dataframes['team'], left_on='team', right_on='id', how='left')

# Drop unnecessary columns and rename columns
merged_df.drop(columns=['IP_player', 'id_x', 'id_y','team','ourteam'], inplace=True)
merged_df.rename(columns={'name_x': 'Player'}, inplace=True)
merged_df.rename(columns={'name_y': 'Team'}, inplace=True)
teams_unique = merged_df['Team'].unique().tolist()

# Setter distribution data
setter_actions = event_df[event_df['IP_fondamentale'] == 5]
setter_actions = setter_actions.merge(dataframes['team'], left_on='team', right_on='id', how='left')
setter_actions.drop(columns=['OP_other_type', 'ATT_cono', 'SERVE_type','SUBSTITUTION_player_in','SUBSTITUTION_player_out','special_code','ourteam'], inplace=True)
setter_actions.rename(columns={'name': 'Team'}, inplace=True)
#setter_actionsB = setter_actions[setter_actions['team'] == 1]
#setter_actionsA = setter_actions[setter_actions['team'] == 26]

groupings = {
    '1': ['A1', 'M1', 'T1', 'S1'],
    '2': ['A2', 'M2', 'T2', 'S2'],
    '4': ['A4', 'M4', 'T4', 'S4'],
    '6': ['A6', 'M6', 'S6'],
    '3': ['V1', 'V7', 'F1', 'VC', 'F2', 'V2']
}

set_type_mapping = {
    1: 'Alta',
    2: 'Mezza',
    3: 'Super',
    4: 'Tesa',
    5: 'Veloce',
    6: 'Fast',
    7: 'Altre',
    8: 'Bagher'
}

setter_actions['SET_type_text'] = setter_actions['SET_type'].map(set_type_mapping)


# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Volleyball Match Analysis Dashboard"), width=12, className="text-center my-4")
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='skill-dropdown',
                options=[{'label': skill, 'value': skill} for skill in ['Attacco', 'Ricezione', 'Battuta']],
                value='Attacco',
                clearable=False
            ),
            dcc.Dropdown(
                id='team-dropdown',
                options=[{'label': team, 'value': team} for team in teams_unique],
                value='CENTEMERO CONCOR. MB', ## To be changed!
                clearable=False
            )
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Highest number", className="card-title"),
                    html.H2(id="top-player-count", className="card-text"),
                    html.P(id="top-player-count-name", className="card-text"),
                    html.P(id="top-player-count-team", className="card-text")
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Top Player (Efficiency)", className="card-title"),
                    html.H2(id="top-player-efficiency", className="card-text"),
                    html.P(id="top-player-efficiency-name", className="card-text"),
                    html.P(id="top-player-efficiency-team", className="card-text")
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Top Player (Positivity)", className="card-title"),
                    html.H2(id="top-player-positivity", className="card-text"),
                    html.P(id="top-player-positivity-name", className="card-text"),
                    html.P(id="top-player-positivity-team", className="card-text")
                ])
            ])
        ], width=3)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Tabs([
                dcc.Tab(label='Player Performance', value='performance'),
                dcc.Tab(label='Setter Distribution', value='setter')
            ], id='tabs', value='performance')
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            html.Div(id='tab-content')
        ], width=12)
    ])
], fluid=True)

# Callback to update top players and graph based on selected skill
@app.callback(
    [Output('top-player-count', 'children'),
     Output('top-player-count-name', 'children'),
     Output('top-player-count-team', 'children'),
     Output('top-player-efficiency', 'children'),
     Output('top-player-efficiency-name', 'children'),
     Output('top-player-efficiency-team', 'children'),
     Output('top-player-positivity', 'children'),
     Output('top-player-positivity-name', 'children'),
     Output('top-player-positivity-team', 'children'),
     Output('player-performance-graph', 'figure')],
    [Input('skill-dropdown', 'value'),
     Input('team-dropdown', 'value')]
)
def update_dashboard(selected_skill, selected_team):
    filtered_df = merged_df[merged_df['skill'] == selected_skill]
    filtered_df = filtered_df[filtered_df['Team'] == selected_team]
    
    # Top player by count
    top_count = filtered_df.loc[filtered_df['total'].idxmax()]
    # Top player by efficiency
    top_efficiency = filtered_df.loc[filtered_df['efficiency'].idxmax()]
    # Top player by positivity
    top_positivity = filtered_df.loc[filtered_df['positivity'].idxmax()]
    print(filtered_df)
    
    fig = px.bar(filtered_df, 
                 x='Player', 
                 y=['efficiency', 'positivity','total'], 
                 title=f'{selected_skill} Performance by Player: Efficiency',
                 labels={'value': 'Value', 'Player': 'Player', 'variable': 'Metric'},
                 #color=filtered_df['total'],
                 barmode='group'
                 )
    
    
    return (
        f"{top_count['total']:.0f}",
        f"Name: {top_count['Player']}",
        f"Team: {top_count['Team']}",
        f"{top_efficiency['efficiency']:.2f}",
        f"Name: {top_efficiency['Player']}",
        f"Team: {top_efficiency['Team']}",
        f"{top_positivity['positivity']:.2f}",
        f"Name: {top_positivity['Player']}",
        f"Team: {top_positivity['Team']}",
        fig
    )

# Callback to update tab content
@app.callback(Output('tab-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'performance':
        return dcc.Graph(id='player-performance-graph')
    elif tab == 'setter':
        return html.Div([
            dcc.Dropdown(
                id='setter-position-dropdown',
                options=[{'label': f'Position {pos}', 'value': pos} for pos in setter_actions['pos_palleggiatore'].unique()],
                value=setter_actions['pos_palleggiatore'].unique()[0],
                clearable=False
            ),
            dcc.Graph(id='setter-distribution-graph')
        ])

# Callback to update setter distribution graph
@app.callback(
    Output('setter-distribution-graph', 'figure'),
    [Input('setter-position-dropdown', 'value'),
     Input('team-dropdown', 'value'),
     Input('skill-dropdown', 'value'),
     ]
)

def update_setter_distribution(pos_palleggiatore, team_selected, skill_selected):
    # skill_selected set only to try to fix the error: not working
    data = setter_actions[setter_actions['pos_palleggiatore'] == pos_palleggiatore]
    data = data[data['Team'] == team_selected]
    
    data_fake = {
        'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47],
        'descr': ['A4', 'A5', 'A2', 'A1', 'A6', 'A8', 'A9', 'M2', 'M4', 'M8', 'M3', 'M7', 'M5', 'M6', 'M1', 'S4', 'S5', 'S2', 'S1', 'T4', 'T5', 'T2', 'T1', 'V7', 'VC', 'V5', 'V4', 'V6', 'V8', 'V1', 'V2', 'V3', 'F2', 'F1', 'F3', 'F4', 'OR', 'OP', 'O2', 'O3', 'T3', 'A3', 'S3', 'F5', 'S6', 'T6', 'F6']
    }
    SET_chiamata = pd.DataFrame(data_fake)

    # Create a mapping from descr to id
    descr_to_id = SET_chiamata.set_index('descr')['id'].to_dict()
    
    # Update the groupings with the corresponding IDs
    updated_groupings = {key: [descr_to_id[descr] for descr in value] for key, value in groupings.items()}
    
    # Count occurrences for each group
    counts = {k: data['SET_chiamata'].isin(v).sum() for k, v in updated_groupings.items()}
    
    # Create the court
    fig = go.Figure()
    
    # Add court outline
    fig.add_shape(type="rect", x0=0, y0=0, x1=9, y1=9, line=dict(color="Black"))
    
    # Add attack line
    fig.add_shape(type="line", x0=0, y0=3, x1=9, y1=3, line=dict(color="Red"))
    
    # Plot circles for each group
    positions = {
        '1': (1.5, 4.5),
        '2': (4.5, 4.5),
        '3': (4.5, 1.5),
        '4': (7.5, 1.5),
        '5': (7.5, 4.5),
        '6': (1.5, 1.5)
    }
    
    for pos, count in counts.items():
        if pos not in positions:
            continue
        x, y = positions[pos]
        fig.add_trace(go.Scatter(
            x=[x], y=[y],
            mode='markers+text',
            marker=dict(
                size=count*3,
                sizemode='area',
                #sizeref=3.*max(counts.values())/(60.**2),  # Adjust the scaling factor as needed
                #sizemin=4,
                color='blue',
                opacity=0.5
            ),
            text=[count],
            textfont=dict(size=18),
            textposition='middle center',
            name=f'Position {pos}'
        ))
    
    fig.update_layout(
        title=f'Setter Distribution (pos_palleggiatore = {pos_palleggiatore})',
        xaxis=dict(range=[0, 9], showticklabels=False),
        yaxis=dict(range=[0, 9], showticklabels=False),
        showlegend=False,
        height=600,
        #width=600, #to be changed with other style
    )
    '''
    filtered_df = merged_df[merged_df['skill'] == skill_selected]
    filtered_df = filtered_df[filtered_df['Team'] == team_selected]
    
    # Top player by count
    top_count = filtered_df.loc[filtered_df['total'].idxmax()]
    # Top player by efficiency
    top_efficiency = filtered_df.loc[filtered_df['efficiency'].idxmax()]
    # Top player by positivity
    top_positivity = filtered_df.loc[filtered_df['positivity'].idxmax()]
    print(filtered_df)
    '''
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(host='192.168.1.9', port=8050)
