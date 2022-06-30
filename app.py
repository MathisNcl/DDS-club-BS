import dash
from dash import html, dcc, dash_table
import dash_daq as daq
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output, State
import dash_daq as daq
import dash_bootstrap_components as dbc
from flask import Flask
from dash.exceptions import PreventUpdate
import numpy as np
import re

# for deployment, pass app.server (which is the actual flask app) to WSGI etc
server = Flask(__name__)
PORT = 8080
HOST = "localhost"
app = dash.Dash(__name__, title="local BS", external_stylesheets=[dbc.themes.BOOTSTRAP], server=server)
paper_bgcolor = '#f9f9f9'
bg_color = "#F2F2F2"
#app = dash.Dash(__name__, title="DDS ligue BS", external_stylesheets=[dbc.themes.BOOTSTRAP])
pretty_container = {"border-radius": "5px",
  "background-color": "#f9f9f9",
  "margin": 10,
  "padding": 15,
  "position": "relative",
  "box-shadow": "2px 2px 2px lightgrey",
  "text-align":"center"}
  #"flex": 1}
H3 = {}

config_no_zoom = {"showAxisRangeEntryBoxes":False, "showAxisDragHandles":False, "scrollZoom": False, 'displayModeBar':False, "editable":False }
legend_top =dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1) 

couleur={"vert": "#2ECC71", "orange":"#F39C12", "rouge":"#E74C3C", "jaune":"#F4D03F", "bleu":"#3498DBS"}
###############################################################################
#import des données
###############################################################################
df = pd.read_csv("database.csv")
df['WR'] = [1 if i else 0 for i in df['result']=="victory"]
df = df[df["season"].str.find("-") == -1]
afk = ["bazook.F","je suis groot","⭐️TTB|Apsou™️✨","Louis"]
df = df[~df["name"].isin(afk)]

df_WR = df.groupby("seasonday").agg({"WR": np.mean, "points":"sum", "used_tickets" : "sum", "name": lambda x: x.nunique()}).reset_index()
df_WR['WR'] = np.round(df_WR['WR']*100,2)
df_WR.sort_values("seasonday", inplace=True)
####Création des tops 10
##par joueur
df_top10joueurs = df.groupby("name").agg({"WR": np.mean, "points": np.mean, "used_tickets" :  np.mean, "starplayer":np.mean}).reset_index()
df_top10joueurs['WR'] = np.round(df_top10joueurs['WR']*100,2)
df_top10joueurs['starplayer'] = np.round(df_top10joueurs['starplayer']*100,2)
df_top10joueurs['points_mean'] = np.round(df_top10joueurs['points'],2)
df_top10joueurs['starplayer_mean'] = np.round(df_top10joueurs['starplayer'],2)
temp = df.groupby("name").agg({"points": "sum", "starplayer":"sum"}).reset_index()
df_top10joueurs['points'] = temp["points"]
df_top10joueurs['starplayer'] = [int(i) if i!="False" else 0 for i in temp["starplayer"].fillna(0)]
best_starplayer=df_top10joueurs.sort_values(["starplayer","starplayer_mean", "name"], ascending=False).iloc[0]
##par joueur saison
df_joueurs_saison = df.groupby(["season", "name"]).agg({"WR": np.mean, "points": np.mean, "used_tickets" :  np.mean, "starplayer":np.mean}).reset_index()
df_joueurs_saison['WR'] = np.round(df_joueurs_saison['WR']*100,2)
df_joueurs_saison['starplayer'] = np.round(df_joueurs_saison['starplayer']*100,2)
df_joueurs_saison['points_mean'] = np.round(df_joueurs_saison['points'],2)
df_joueurs_saison['starplayer_mean'] = np.round(df_joueurs_saison['starplayer'],2)
temp = df.groupby(["season", "name"]).agg({"points": "sum", "starplayer":"sum"}).reset_index()
df_joueurs_saison['points'] = temp["points"]
df_joueurs_saison['starplayer'] = [int(i) if i!="False" else 0 for i in temp["starplayer"].fillna(0)]
best_starplayer_season=df_joueurs_saison.sort_values(["season", "starplayer","starplayer_mean", "name"], ascending=False).iloc[0]

##par brawler
df_top10brawlers = df.groupby("brawler").agg({"WR": np.mean, "points": np.mean, "used_tickets" :  np.mean, "tag":"count"}).reset_index()
df_top10brawlers['WR'] = np.round(df_top10brawlers['WR']*100,2)
df_top10brawlers['points_mean'] = np.round(df_top10brawlers['points'],2)
temp = df.groupby("brawler").agg({"points": "sum", }).reset_index()
df_top10brawlers['points'] = temp["points"]
df_top10brawlers.rename(columns={"tag":"nb_picks"}, inplace=True)
####Création des modes de jeu
pie_mode = df.groupby("mode").agg({"tag": "count"}).reset_index()
df_mode = df.groupby(["mode", "seasonday"]).agg({"WR": np.mean, "points": "sum", "used_tickets" :  "sum", "tag" : "count"}).reset_index()
df_mode['WR'] = np.round(df_mode['WR']*100,2)
df_mode.rename(columns={"tag":"nb"}, inplace=True)

####Création des bases de joueurs
df_joueur = df.groupby("name").agg({"WR": np.mean, "points": np.mean, "used_tickets" :  np.mean, "tag":"count"}).reset_index()
df_joueur['WR'] = np.round(df_joueur['WR']*100,2)
df_joueur.sort_values('WR', inplace=True, ascending=False)     
df_joueur["rank"] = [i+1 for i in range(len(df_joueur))]  
df_joueur.rename(columns={"tag":"nb"}, inplace=True)
df_joueur.sort_values(['name', 'WR', 'nb'], inplace=True, ascending=False) 

df_joueur_brawler = df.groupby(["name", "brawler"]).agg({"WR": np.mean, "points": np.mean, "used_tickets" :  np.mean, "tag":"count"}).reset_index()
df_joueur_brawler['WR'] = np.round(df_joueur_brawler['WR']*100,2)
df_joueur_brawler['points'] = np.round(df_joueur_brawler['points'],2)
df_joueur_brawler.rename(columns={"tag":"nb"}, inplace=True)
temp = df.groupby(["name", "mode"]).agg({"points": "sum", }).reset_index()
df_joueur_brawler['points_totaux'] = temp["points"]
df_joueur_brawler.sort_values(['name', 'WR', 'nb'], inplace=True, ascending=False) 

df_joueur_brawler_mode = df.groupby(["name", "brawler", "mode"]).agg({"tag":"count", "WR": np.mean}).reset_index()
df_joueur_brawler_mode.sort_values(["name", "brawler", "tag"], inplace=True, ascending=False)
df_joueur_brawler_mode2 = df_joueur_brawler_mode.copy()
df_joueur_brawler_mode2['WR'] = np.round(df_joueur_brawler_mode2['WR']*100,2)
df_joueur_brawler_mode=df_joueur_brawler_mode.groupby(["name", "brawler"]).first().reset_index()
df_joueur_brawler_mode["mode"] = ["{} ({})".format(df_joueur_brawler_mode.iloc[i]["mode"], df_joueur_brawler_mode.iloc[i]["tag"]) for i in range(len(df_joueur_brawler_mode))]

#dataframe des tickets et teammate
df_ticket_teammate = df.groupby(["name", "used_tickets"]).agg({"with_club_mate" : "count"}).reset_index().rename(columns={"with_club_mate":"count_used_tickets"})
df_ticket_teammate2 = df.groupby(["name", "with_club_mate"]).agg({"used_tickets" : "count"}).reset_index().rename(columns={"used_tickets":"count_with_club_mate"})
df_ticket_teammate = df_ticket_teammate.merge(df_ticket_teammate2, on="name", how="inner")
df_ticket_teammate["used_tickets"] = ["1 ticket" if df_ticket_teammate.iloc[i]["used_tickets"]==1 else "2 tickets" for i in range(len(df_ticket_teammate))]
df_ticket_teammate["with_club_mate"] = ["En équipe" if df_ticket_teammate.iloc[i]["with_club_mate"]==True else "Solo" for i in range(len(df_ticket_teammate))]

#Création par brawler mode
df_brawlers_mode = df.groupby(["brawler", "mode"]).agg({"WR": np.mean, "points": np.mean, "used_tickets" :  np.mean, "tag":"count"}).reset_index()
df_brawlers_mode['WR'] = np.round(df_brawlers_mode['WR']*100,2)
df_brawlers_mode['points_mean'] = np.round(df_brawlers_mode['points'],2)
temp = df.groupby(["brawler", "mode"]).agg({"points": "sum", }).reset_index()
df_brawlers_mode['points'] = temp["points"]
df_brawlers_mode.rename(columns={"tag":"nb_picks"}, inplace=True)

#Création par brawler saison
df_brawlers_season = df.groupby(["brawler", "season"]).agg({"WR": np.mean, "points": np.mean, "tag":"count"}).reset_index()
df_brawlers_season['WR'] = np.round(df_brawlers_season['WR']*100,2)
df_brawlers_season['points_mean'] = np.round(df_brawlers_season['points'],2)
temp = df.groupby(["brawler", "season"]).agg({"points": "sum", }).reset_index()
df_brawlers_season['points'] = temp["points"]
df_brawlers_season.rename(columns={"tag":"nb_picks"}, inplace=True)

#Création par brawler saison mode
df_brawlers_season_mode = df.groupby(["brawler", "season", "mode"]).agg({"WR": np.mean, "points": np.mean, "tag":"count"}).reset_index()
df_brawlers_season_mode['WR'] = np.round(df_brawlers_season_mode['WR']*100,2)
df_brawlers_season_mode['points_mean'] = np.round(df_brawlers_season_mode['points'],2)
temp = df.groupby(["brawler", "season"]).agg({"points": "sum", }).reset_index()
df_brawlers_season_mode['points'] = temp["points"]
df_brawlers_season_mode.rename(columns={"tag":"nb_picks"}, inplace=True)

#Création par mode, map par brawler
df_map = df.groupby(["map_id","map_name","mode"]).agg({"WR": np.mean, "points": np.mean, "tag":"count"}).reset_index()
df_map['WR'] = np.round(df_map['WR']*100,2)
df_map['points_mean'] = np.round(df_map['points'],2)
temp = df.groupby(["map_id","map_name","mode", "brawler"]).agg({"points": "sum", }).reset_index()
df_map['points'] = temp["points"]
df_map.rename(columns={"tag":"nb_picks"}, inplace=True)

#Création par mode, map par brawler
df_map_brawlers = df.groupby(["map_id","map_name","mode", "brawler"]).agg({"WR": np.mean, "points": np.mean, "tag":"count"}).reset_index()
df_map_brawlers['WR'] = np.round(df_map_brawlers['WR']*100,2)
df_map_brawlers['points_mean'] = np.round(df_map_brawlers['points'],2)
temp = df.groupby(["map_id","map_name","mode", "brawler"]).agg({"points": "sum", }).reset_index()
df_map_brawlers['points'] = temp["points"]
df_map_brawlers.rename(columns={"tag":"nb_picks"}, inplace=True)

#Création par mode, map par joueur
df_map_joueurs = df.groupby(["map_id","map_name","mode", "name"]).agg({"WR": np.mean, "points": np.mean, "tag":"count"}).reset_index()
df_map_joueurs['WR'] = np.round(df_map_joueurs['WR']*100,2)
df_map_joueurs['points_mean'] = np.round(df_map_joueurs['points'],2)
temp = df.groupby(["map_id","map_name","mode", "name"]).agg({"points": "sum", }).reset_index()
df_map_joueurs['points'] = temp["points"]
df_map_joueurs.rename(columns={"tag":"nb_picks"}, inplace=True)

#calcul du nombre de games avec chaque joueur
#J1J2
df_J1 = df.groupby(["name", 'Joueur1']).agg({"WR": "sum", "points": "sum", "tag":"count"}).reset_index()
df_J1 = df_J1[df_J1.name != df_J1.Joueur1]
df_J1.columns = ['name', 'teammate', 'nbwin_J1', 'pointsJ1', 'nb_J1']

#J2
df_J2 = df.groupby(["name", 'Joueur2']).agg({"WR": "sum", "points": "sum", "tag":"count"}).reset_index()
df_J2 = df_J2[df_J2.name != df_J2.Joueur2]
df_J2.columns = ['name', 'teammate', 'nbwin_J2', 'pointsJ2', 'nb_J2']

#J3
df_J3 = df.groupby(['name', "Joueur3"]).agg({"WR": "sum", "points": "sum", "tag":"count"}).reset_index()
df_J3 = df_J3[df_J3.name != df_J3.Joueur3]
df_J3.columns = ['name', 'teammate', 'nbwin_J3', 'pointsJ3', 'nb_J3']

#merge 
df_coequipiers = df_J1.merge(df_J2, how='outer', on=['name', 'teammate'])
df_coequipiers = df_coequipiers.merge(df_J3, how='outer',  on=['name', 'teammate']).fillna(0)
df_coequipiers["nb_win"] = df_coequipiers["nbwin_J1"] +df_coequipiers["nbwin_J3"] +df_coequipiers["nbwin_J2"]
df_coequipiers["points"] = df_coequipiers["pointsJ1"] +df_coequipiers["pointsJ2"] +df_coequipiers["pointsJ3"]
df_coequipiers["nb_games"] = df_coequipiers["nb_J1"] +df_coequipiers["nb_J2"] +df_coequipiers["nb_J3"]
df_coequipiers["WR"] = round(df_coequipiers["nb_win"]/df_coequipiers["nb_games"]*100,2)
df_coequipiers["points_mean"] = round(df_coequipiers["points"]/df_coequipiers["nb_games"],2)
to_remove = ["nbwin_J1", "nbwin_J2", "nbwin_J3", "pointsJ1", "pointsJ2", "pointsJ3", "nb_J1", "nb_J2", "nb_J3"]
for i in to_remove:
    del df_coequipiers[i]

###############################################################################
#Layout de l'application vue par vue
###############################################################################
Header = dbc.Row([
    dbc.Col([html.H1('Dashboard Ligue - DDS', style={"text-align":"center"})],xs=12,lg=4),
    dbc.Col([html.H5('Star all time : {}'.format(best_starplayer['name'])),
            html.Div('{}% ({} games)'.format(best_starplayer['starplayer_mean'], best_starplayer['starplayer']), style={"text-align": "center"})
            ], style=pretty_container),
    dbc.Col([html.H5('Star {} : {}'.format(best_starplayer_season["season"],best_starplayer_season['name'])),
            html.Div('{}% ({} games)'.format(best_starplayer_season['starplayer_mean'], best_starplayer_season['starplayer']), style={"text-align": "center"})
            ], style=pretty_container),
    
])

Tabs = dcc.Tabs(id='tabs_dataviz', value='accueil', children=[
            dcc.Tab(label='Accueil', value='accueil'),
            dcc.Tab(label='Résultats par joueur', value='res_joueur'),
            dcc.Tab(label="Résultats par brawler", value='res_brawler'),
            dcc.Tab(label="Résultats par map", value='res_map'),
            ])

##Accueil
accueil_div = html.Div([
        dbc.Row([
            dbc.Col([
                dcc.Graph(figure = {
                    "data":[
                        go.Bar(
                            x=df_WR['seasonday'],
                            y=df_WR.WR,
                            marker={"color":[couleur['vert'] if WR>=60 else couleur['jaune'] if WR>=50 else couleur["orange"] if WR>=35 else couleur["rouge"] for WR in df_WR.WR]},
                            text=df_WR.WR,
                            textposition='outside',
                            cliponaxis=False,
                            name="Win rate par journée/saison",
                            showlegend=False),
                
                        go.Scatter(
                            x = df_WR['seasonday'],
                            y = [60 for i in df_WR['seasonday']],
                            name = "Goal",
                            mode="lines"
                        )
                    ],
                    "layout":go.Layout(
                                title = "Win rate par journée/saison",
                                legend=legend_top,
                                margin=dict(l=17, r=17))
                }
                )

            ],id="graph_WR_per_season", xs=12, lg=6),
            dbc.Col([
                dcc.Graph(figure = {
                    "data":[
                        go.Bar(
                            x=df_WR['seasonday'],
                            y=df_WR.points,
                            text=df_WR.points,
                            textposition='outside',
                            cliponaxis=False,
                            name="Points par journée/saison",
                            showlegend=False),

                        go.Scatter(
                            x = df_WR['seasonday'],
                            y = [df_WR['points'].mean() for i in df_WR['seasonday']],
                            name = "Moyenne",
                            mode="lines"
                        )
                    ],
                    "layout":go.Layout(
                                title = "Points par journée/saison",
                                legend=legend_top,
                                margin=dict(l=17, r=17))
                }
                )
            ], xs=12, lg=6)
        ]),
        #Tableau des tops 10
        dbc.Row([
            dbc.Col([
                dcc.Tabs(id='tabs_top10joueurs', value='WR', vertical = True, children=[
                    dcc.Tab(label='Win Rate moyen', value='WR'),
                    dcc.Tab(label='Points moyen', value='points'),
                    dcc.Tab(label='Points totaux', value='points_sum')
                ])
            ],xs=3, lg=2),
            dbc.Col([html.Div(id="ranking_table_joueur")],  xs=9, lg=4),
            dbc.Col([
                dcc.Tabs(id='tabs_top10brawlers', value='WR', vertical = True, children=[
                    dcc.Tab(label='Win Rate moyen', value='WR'),
                    dcc.Tab(label='Points moyen', value='points'),
                    dcc.Tab(label='Points totaux', value='points_sum'),
                    dcc.Tab(label='Nombre de picks', value='nb_picks'),
                ])
            ],xs=3, lg=2),
            dbc.Col([html.Div(id="ranking_table_brawlers")],  xs=9, lg=4),
        ]),


        dbc.Row([
            dbc.Col([
                dcc.Graph(figure = {
                    "data":[
                        go.Bar(
                            x=df_WR['seasonday'],
                            y=df_WR.name,
                            text=df_WR.name,
                            textposition='outside',
                            cliponaxis=False,
                            name="Nombre de joueurs par journée/saison",
                            showlegend=False),

                        go.Scatter(
                            x = df_WR['seasonday'],
                            y = [df_WR['name'].mean() for i in df_WR['seasonday']],
                            name = "Moyenne",
                            mode="lines"
                        )
                    ],
                    "layout":go.Layout(
                                title = "Nombre de joueurs par journée/saison",
                                legend = legend_top,
                                margin=dict(l=17, r=17) )
                }
                )
            ], xs=12, lg=6),
            dbc.Col([
                dcc.Graph(figure = {
                    "data":[
                        go.Bar(
                            x=df_WR['seasonday'],
                            y=df_WR.used_tickets,
                            text=df_WR.used_tickets,
                            textposition='outside',
                            cliponaxis=False,
                            name="Nombre de tickets joués par journée/saison",
                            showlegend=False),

                        go.Scatter(
                            x = df_WR['seasonday'],
                            y = [df_WR['used_tickets'].mean() for i in df_WR['seasonday']],
                            name = "Moyenne",
                            mode="lines"
                        )
                    ],
                    "layout":go.Layout(
                                title = "Nombre de tickets joués par journée/saison",
                                legend = legend_top,
                                margin=dict(l=17, r=17) )
                }
                )
            ], xs=12, lg=6)
        ]),
    ##Mode de jeu
        dbc.Row([
            dbc.Col([dcc.Graph(figure = {
                    "data":[
                        go.Pie(
                            labels=pie_mode['mode'],
                            values=pie_mode['tag'],
                        )

                        
                    ],
                    "layout":go.Layout(
                                title = "Mode de jeux joués",
                                hovermode="closest",
                                clickmode='event+select' )
                    }, id="piechart_mode_accueil"
                )
            ], xs=12, lg=4),
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        dcc.Dropdown(pie_mode['mode'], 'gemGrab', id='dropdown_chart_mode'),
                    ])
                ]),
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id="chart_mode_WR")
                    ])
                ])
            ], xs=12, lg=8),


        ])
    ],
    id="accueil_id")


##Résultats par joueur
res_joueur_div = html.Div([
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(df_joueur['name'], 'Paffiver', id='dropdown_joueur')
        ])
    ]),
    dbc.Row([
        dbc.Col([
            html.H3("Win Rate"),
            html.H4(id="winrate_selected_joueur")
        ],style=pretty_container, xs=5, lg=3),
        dbc.Col([
            html.H3("Rang dans le club"),
            html.H4(id="rank_selected_joueur")
        ],style=pretty_container, xs=5, lg=3),
        dbc.Col([
            html.H3("Top 1 brawler (Win rate)"),
            html.Div(id="brawler_selected_joueur"),
            html.H3("Top 1 pick"),
            html.Div(id="pick_selected_joueur")
        ],style=pretty_container, xs=12, lg=4)
    ],justify="center"),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="graph_spider_top6_brawler", config=config_no_zoom)
        ])
    ]),
    dbc.Row([
        html.Div(id="tableau_joueur_brawler")
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="graph_WR_brawler_intreact")
        ], width=8),
        dbc.Col([
            html.Div(dash_table.DataTable(
                    #style_as_list_view=True,
                    fixed_rows={'headers': True},
                    columns=[{"name": i, "id": i} for i in ['Brawler', 'Win Rate', 'Nb Games', '% pick'] if i != 'id'],
                    data=[],
                    row_selectable="single",
                    style_cell={
                        'padding': '10px',
                        'width': 'auto',
                        'textAlign': 'left',
                        'whiteSpace': 'normal',
                        'fontSize': 15,
                    },
                    style_table={
                        'overflowY': 'auto',
                        'height': 700,
                        'width': '100%'
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(240, 240, 240)',
                        }
                    ],
                        style_header={
                            'backgroundColor': 'rgb(210, 210, 210)',
                            'color': 'black',
                            'fontWeight': 'bold'
                        }
                ,id="tableau_joueur_brawler_interact"))
        ], width=4),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="graph_pie_teammate")
        ],xs=12, lg=6),
        dbc.Col([
            dcc.Graph(id="graph_pie_used_ticket")
        ],xs=12, lg=6)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="graph_evolution_season")
        ])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="graph_teammates")
        ])
    ]),
],id="res_joueur_id")

############################################################################
##Résultats par brawler
liste_saison    = df_brawlers_season['season'].copy().unique()
liste_saison    = sorted(liste_saison, reverse=True)
liste_saison    = np.insert(liste_saison, 0, "Toutes")
liste_mode      = df_brawlers_season_mode['mode'].copy().unique()
liste_mode.sort()
liste_mode      = np.insert(liste_mode, 0, "Tous")

res_brawler_div = html.Div([
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(df_top10brawlers['brawler'], df_top10brawlers["brawler"][np.argmax(df_top10brawlers['nb_picks'])], id='dropdown_brawler')
        ], xs=12, lg=3),
        dbc.Col([
            html.Div(id='info_brawler_selected')
        ], xs=12, lg=9),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='graph_spider_mode_par_brawler', config=config_no_zoom)
        ], xs=12, lg=7),
        dbc.Col([
            html.Div(id='info_brawler_selected_joueur')
        ], xs=12, lg=5),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='graph_WR_nb_brawler_season')
        ])
    ]),
    dbc.Row([
        dbc.Col([dcc.Dropdown(liste_saison, liste_saison[0], id='dropdown_brawler_season')],width=6),
        dbc.Col([dcc.Dropdown(liste_mode, liste_mode[0], id='dropdown_brawler_mode')],width=6),
        dbc.Col([dcc.Graph(id='graph_scatter_WR_nb_brawler_season')],width=12)
    ], style={"margin-top":20}),
    dbc.Row([
        html.H4(id="title_tableau_brawler_joueur", style={"text-align":"center", "margin-top":20}),
        html.Div(id="tableau_brawler_joueur")
    ]),
],id="res_brawler_id")


############################################################################
##Résultats par map
def url_mode(mode, size=80):
    return("https://media.brawltime.ninja/modes/{}/icon.png?size={}".format(str(mode).lower(), size))
def url_map(map, size=180):
    return("https://media.brawltime.ninja/maps/{}.png?size={}".format(map, size))
def url_brawler(brawler, size=80): 
    return("https://media.brawltime.ninja/brawlers/{}/avatar.png?size={}".format(brawler.replace(" ", "_").replace(".", "_").lower(), size))
res_map_div = html.Div([
    #sélection
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(df_map_brawlers['mode'].unique(), "gemGrab", id='dropdown_mode')
        ], width=6),
        dbc.Col([
            dcc.Dropdown(id='dropdown_mode_map')
        ], width=6)
    ]),
    #affichage infos générales
    dbc.Row([
        dbc.Col([
            html.Img(id="affiche_map", style=pretty_container)
        ], style={"textalign":"center"}),
        dbc.Col([
            html.Div(id='info_map_WR', style=pretty_container)
        ]),
        dbc.Col([
            html.Div(id='info_map_TOP3', style=pretty_container)
        ]),
        dbc.Col([
            html.Div(id='info_map_worst3', style=pretty_container)
        ])
    ],justify="center"),
    #tableau par joueur et par brawler
    dbc.Row([
        dbc.Col([
            html.Div(id='tableau_map_brawler')
        ],xs=12, lg=6),
        dbc.Col([
            html.Div(id='tableau_map_joueur')
        ],xs=12, lg=6)
    ]),
])

app.layout = html.Div([
    Header, 
    Tabs,
    html.Div(id="selected_tab")
    ],style= {"background-color":bg_color, "padding-left": "2%", "padding-right": "2%"}
)

###############################################################################
#Callbacks
###############################################################################
#selected tab shown
@app.callback(
    Output('selected_tab', 'children'),
    [Input('tabs_dataviz', 'value')])
def selection_onglet(tab):
    if tab=='accueil':
        return (accueil_div)
    elif tab=='res_joueur':
        return (res_joueur_div)
    elif tab=='res_brawler':
        return (res_brawler_div)
    elif tab=='res_map':
        return (res_map_div)
    

#TOP10 joueurs
@app.callback(
    Output('ranking_table_joueur', 'children'),
    [
     Input("tabs_top10joueurs", "value")])
def affichage_ranking_top10joueurs(selected_var):   
    if selected_var is None:
        raise PreventUpdate
    else:  
        if selected_var=="WR":
            cols = ['name', 'WR']     
            table = df_top10joueurs[cols].copy()
            table.sort_values('WR', inplace=True, ascending=False) 
            table = table[:10]  
            table["Rang"] = [1,2,3,4,5,6,7,8,9,10]
            table.columns = ['Nom', 'Win Rate', 'Rang']
            table = table[['Rang', 'Nom', 'Win Rate']]
        elif selected_var=="points_sum":
            cols = ['name', 'points']
            table = df_top10joueurs[cols].copy()
            table.sort_values('points', inplace=True, ascending=False)     
            table = table[:10]  
            table["Rang"] = [1,2,3,4,5,6,7,8,9,10]       
            table.columns = ['Nom', 'Points totaux', 'Rang']
            table = table[['Rang', 'Nom', 'Points totaux']]
        else:
            cols = ['name', 'points_mean']
            table = df_top10joueurs[cols].copy()
            table.sort_values('points_mean', inplace=True, ascending=False)     
            table = table[:10]  
            table["Rang"] = [1,2,3,4,5,6,7,8,9,10]       
            table.columns = ['Nom', 'Points moyens', 'Rang']
            table = table[['Rang', 'Nom', 'Points moyens']]

        return(
            dash_table.DataTable(
                    id="table_joueur",
                    style_as_list_view=True,
                    virtualization=False,
                    fixed_rows={'headers': True},
                    columns=[{"name": i, "id": i} for i in table.columns if i != 'id'],
                    data=table.to_dict("records"),
                    # page_size=14,
                    style_cell={
                        'padding': '10px',
                        'width': 'auto',
                        'textAlign': 'left',
                        'whiteSpace': 'normal',
                        'fontSize': 15,
                    },
                    style_table={
                        'overflowY': 'auto',
                        'height': 550,
                        'width': '100%',
                    },
                    # selected_cells = [{"row": row}],
                    style_data_conditional=[
                                        {
                                        'if': {'row_index': 'odd'},
                                        'backgroundColor': 'rgb(248, 248, 248)'
                                        }
                    ]
                )
            )


#TOP10 joueurs
@app.callback(
    Output('ranking_table_brawlers', 'children'),
    [
     Input("tabs_top10brawlers", "value")])
def affichage_ranking_top10joueurs(selected_var):   
    if selected_var is None:
        raise PreventUpdate
    else:  
        if selected_var=="WR":
            cols = ['brawler', 'WR']     
            table = df_top10brawlers[cols].copy()
            table.sort_values('WR', inplace=True, ascending=False) 
            table["Rang"] = [i+1 for i in range(len(table))]
            table.columns = ['Brawler', 'Win Rate', 'Rang']
            table = table[['Rang', 'Brawler', 'Win Rate']]

        elif selected_var=="points_sum":
            cols = ['brawler', 'points']
            table = df_top10brawlers[cols].copy()
            table.sort_values('points', inplace=True, ascending=False)     
            table["Rang"] = [i+1 for i in range(len(table))]   
            table.columns = ['Brawler', 'Points totaux', 'Rang']
            table = table[['Rang', 'Brawler', 'Points totaux']]
        elif selected_var=="nb_picks":
            cols = ['brawler', 'nb_picks']
            table = df_top10brawlers[cols].copy()
            table.sort_values('nb_picks', inplace=True, ascending=False)     
            table["Rang"] = [i+1 for i in range(len(table))]   
            table.columns = ['Brawler', 'Nombre de picks', 'Rang']
            table = table[['Rang', 'Brawler', 'Nombre de picks']]
        else:
            cols = ['brawler', 'points_mean']
            table = df_top10brawlers[cols].copy()
            table.sort_values('points_mean', inplace=True, ascending=False)     
            table["Rang"] = [i+1 for i in range(len(table))]  
            table.columns = ['Brawler', 'Points moyens', 'Rang']
            table = table[['Rang', 'Brawler', 'Points moyens']]

        return(
            dash_table.DataTable(
                    id="table_brawler",
                    style_as_list_view=True,
                    virtualization=False,
                    fixed_rows={'headers': True},
                    columns=[{"name": i, "id": i} for i in table.columns if i != 'id'],
                    data=table.to_dict("records"),
                    # page_size=14,
                    style_cell={
                        'padding': '10px',
                        'width': 'auto',
                        'textAlign': 'left',
                        'whiteSpace': 'normal',
                        'fontSize': 15,
                    },
                    style_table={
                        'overflowY': 'auto',
                        'height': 550,
                        'width': '100%',
                    },
                    # selected_cells = [{"row": row}],
                    style_data_conditional=[
                                        {
                                        'if': {'row_index': 'odd'},
                                        'backgroundColor': 'rgb(248, 248, 248)'
                                        }
                    ]
                )
            )

#changement du dropdown en fonction du graphique
@app.callback(
    Output('dropdown_chart_mode', 'value'),
    [
     Input("piechart_mode_accueil", "clickData")])
def selection_mode(clickData):
    if clickData is None:
        selected_mode = "gemGrab"
    else:
        selected_mode = str(clickData["points"][0]["label"])
    return(selected_mode)


#affichage du graphique de win rate par saison par mode de jeu
@app.callback(
    Output('chart_mode_WR', 'figure'),
    [
     Input("dropdown_chart_mode", "value")])
def affichage_winrate_per_mode(selected_mode):
    df_mode_final = df_mode[df_mode['mode']==selected_mode]
    custom_data = np.transpose(np.array([df_mode_final.points, df_mode_final.nb]))
    return {"data":[
                        go.Bar(
                            x=df_mode_final['seasonday'],
                            y=df_mode_final.WR,
                            text=df_mode_final.WR,
                            textposition='outside',
                            cliponaxis=False,
                            name=selected_mode,
                            customdata=custom_data,
                            hovertemplate=
                                "<b>Win rate : %{y}</b><br><br>" +
                                "Nb games : %{customdata[1]}<br>" +
                                "Nb points gagnés : %{customdata[0]}<br>" +
                                "<extra></extra>",
                            showlegend=False),

                        go.Scatter(
                            x = df_mode_final['seasonday'],
                            y = [df_mode_final['WR'].mean() for i in df_mode_final['seasonday']],
                            name = "Moyenne",
                            mode="lines"
                        )
                    ],
                    "layout":go.Layout(
                                title = "Win Rate {} par journée/saison".format(selected_mode),
                                legend=legend_top,
                                margin=dict(l=17, r=17))
                }
                
#affichage première ligne de la vue joueur
@app.callback(
    Output('winrate_selected_joueur', 'children'),
    Output('winrate_selected_joueur', 'style'),
    Output('rank_selected_joueur', 'children'),
    Output('rank_selected_joueur', 'style'),
    Output('brawler_selected_joueur', 'children'),
    Output('pick_selected_joueur', 'children'),
    [
     Input("dropdown_joueur", "value")])
def affichage_joueur_first(selected_name):
    if selected_name is None:
        raise PreventUpdate
    else:  
        df_final = df_joueur[df_joueur["name"]==selected_name]
        top_brawler = str(df_joueur_brawler[df_joueur_brawler["name"]==selected_name].iloc[0]["brawler"]).replace(" ", "_").replace(".", "_").lower()
        top_brawler_nb = str(df_joueur_brawler[df_joueur_brawler["name"]==selected_name].iloc[0]["nb"])
        top_brawler_WR = str(df_joueur_brawler[df_joueur_brawler["name"]==selected_name].iloc[0]["WR"])

        df_final2 = df_joueur_brawler[df_joueur_brawler["name"]==selected_name]
        top_brawler_pick = str(df_final2.iloc[df_final2['nb'].argmax()]["brawler"]).replace(" ", "_").lower()
        top_brawler_pick_nb = str(df_final2.iloc[df_final2['nb'].argmax()]["nb"])
        top_brawler_pick_WR = str(df_final2.iloc[df_final2['nb'].argmax()]["WR"])
        url_WR = "https://media.brawltime.ninja/brawlers/{}/avatar.png?size=80".format(top_brawler)
        url_pick = "https://media.brawltime.ninja/brawlers/{}/avatar.png?size=80".format(top_brawler_pick)
        rang = str(df_final.iloc[0]["rank"])
        WR = df_final.iloc[0]["WR"]
        couleur_rang = couleur['vert'] if int(rang)<=10 else couleur['jaune'] if int(rang)<=20 else couleur["orange"]
        couleur_WR = couleur['vert'] if WR>=60 else couleur['jaune'] if WR>=40 else couleur["orange"] if WR>=25 else couleur["rouge"]
        return(
            "{}%".format(WR),
            {"color":couleur_WR},
            "1er" if rang=="1" else "{}eme".format(rang),
            {"color":couleur_rang},
            dbc.Row([
                dbc.Col([html.Img(src=url_WR, alt=top_brawler, title =top_brawler)]),
                dbc.Col([html.H4("{}%".format(top_brawler_WR), style=H3),
                        html.H4("{} games".format(top_brawler_nb), style=H3)
                ],style=pretty_container),
            ]),
            dbc.Row([
                dbc.Col([html.Img(src=url_pick, alt = top_brawler_pick, title =top_brawler_pick)]),
                dbc.Col([html.H4("{}% (WR)".format(top_brawler_pick_WR), style=H3),
                        html.H4("{} games".format(top_brawler_pick_nb), style=H3)
                ],style=pretty_container),
            ])            
            )

#araignée top 6 brawler avec le WR
@app.callback(
    Output('graph_spider_top6_brawler', 'figure'),
    [
     Input("dropdown_joueur", "value")])
def graph_spider_top6_brawler(selected_name):
    if selected_name is None:
        raise PreventUpdate
    else: 
    #sélection du joueur
    
        df_final = df_joueur_brawler.sort_values(['name', 'nb'], ascending=False) 
        df_final = df_final[df_final["name"]==selected_name][:6]
        custom_data = np.transpose(np.array([df_final.nb, df_final.points_totaux]))
                
        fig = go.Figure(data=go.Scatterpolar(
            r=df_final['WR'],
            theta=df_final['brawler'],
            fill='toself', 
            name="Win rate",
            customdata=custom_data,
            hovertemplate=
                "<b>Win rate : %{r}%</b><br>" +
                "Nb games : %{customdata[0]}<br>" +
                "Total points : %{customdata[1]}<br>" +
                "<extra></extra>",
            ))

        fig.update_layout(
        title_text="TOP 6 des brawlers les plus joués",
        title_x=0.5,
        margin=dict(l=40, r=40,  b=10),
        polar=dict(
            radialaxis=dict(
            range=[0,100],
            visible=True
            )
        ),
        showlegend=False
        )
        return(fig)

#Tableau général par joueur et brawler
@app.callback(
    Output('tableau_joueur_brawler', 'children'),
    [
     Input("dropdown_joueur", "value")])
def tableau_general(selected_name):
    if selected_name is None:
        raise PreventUpdate
    else: 
    #sélection du joueur
        df_final = df_joueur_brawler[df_joueur_brawler["name"]==selected_name]
        cols = ['brawler', 'WR', 'nb']     
        table = df_final[cols].copy()
        table.sort_values('WR', inplace=True, ascending=False)
        #calcul des deux autres indicateurs
        table["percent_pick"]=np.round(table["nb"]/np.sum(table["nb"])*100,2)
        df_final2 = df_joueur_brawler_mode[df_joueur_brawler_mode["name"]==selected_name]
        table = table.merge(df_final2[['brawler', 'mode']], on=('brawler'), how="inner")
        table.columns = ['Brawler', 'Win Rate', 'Nb Games', '% pick', 'Mode le + joué']

        return(
            dash_table.DataTable(
                    #style_as_list_view=True,
                    fixed_rows={'headers': True},
                    columns=[{"name": i, "id": i} for i in table.columns if i != 'id'],
                    data=table.to_dict("records"),
                    filter_action="native",
                    sort_action="native",
                    style_cell={
                        'padding': '10px',
                        'width': 'auto',
                        'textAlign': 'left',
                        'whiteSpace': 'normal',
                        'fontSize': 15,
                    },
                    style_table={
                        'overflowY': 'auto',
                        'height': 700,
                        'width': '100%'
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(240, 240, 240)',
                        }
                    ],
                        style_header={
                            'backgroundColor': 'rgb(210, 210, 210)',
                            'color': 'black',
                            'fontWeight': 'bold'
                        }
                )
        )

#Tableau général par joueur et brawler interactif
@app.callback(
    Output('tableau_joueur_brawler_interact', 'data'),
    [
     Input("dropdown_joueur", "value")])
def tableau_general_interact(selected_name):
    if selected_name is None:
        raise PreventUpdate
    else: 
    #sélection du joueur
        df_final = df_joueur_brawler[df_joueur_brawler["name"]==selected_name]
        cols = ['brawler', 'WR', 'nb']     
        table = df_final[cols].copy()
        table.sort_values('WR', inplace=True, ascending=False)
        #calcul des deux autres indicateurs
        table["percent_pick"]=np.round(table["nb"]/np.sum(table["nb"])*100,2)
        table.columns = ['Brawler', 'Win Rate', 'Nb Games', '% pick']

        return(table.to_dict("records")
            
        )

#graphique interactif par mode de jeu
@app.callback(
    Output('graph_WR_brawler_intreact', 'figure'),
    [Input("dropdown_joueur", "value"),
    Input('tableau_joueur_brawler_interact', 'derived_virtual_selected_rows')])
def tableau_general_interact(selected_name, selected_brawler_idx):
    if selected_name is None:
        raise PreventUpdate
    else: 
        df_final = df_joueur_brawler_mode2[df_joueur_brawler_mode2['name']==selected_name]
        
        if selected_brawler_idx is None or len(selected_brawler_idx)==0:
            selected_brawler = df_final.iloc[0]['brawler']
        else:
            table = df_joueur_brawler[df_joueur_brawler["name"]==selected_name][['brawler', 'WR'] ].copy()
            table.sort_values('WR', inplace=True, ascending=False)
            selected_brawler = list(table.iloc[selected_brawler_idx]['brawler'])[0]
        df_final = df_final[df_final['brawler']==selected_brawler]

        custom_data = np.transpose(np.array([df_final.tag]))
        return {"data":[
                            go.Bar(
                                x=df_final['mode'],
                                y=df_final.WR,
                                text=df_final.WR,
                                textposition='outside',
                                cliponaxis=False,
                                name=selected_brawler,
                                customdata=custom_data,
                                hovertemplate=
                                    "<b>Win rate : %{y}</b><br><br>" +
                                    "Nb games : %{customdata[0]}<br>" +
                                    "<extra></extra>",
                                showlegend=False)
                        ],
                        "layout":go.Layout(
                                    title = "Win Rate {} par mode de jeu".format(selected_brawler))
                    }

#graphique des pie fin page
@app.callback(
    Output('graph_pie_teammate', 'figure'),
    Output('graph_pie_used_ticket', 'figure'),
    [Input("dropdown_joueur", "value")])
def double_pie(selected_name):
    if selected_name is None:
        raise PreventUpdate
    else: 
        df_final1 = df_ticket_teammate[df_ticket_teammate['name']==selected_name][["name", "used_tickets", "count_used_tickets"]].drop_duplicates()
        df_final2 = df_ticket_teammate[df_ticket_teammate['name']==selected_name][["name", "with_club_mate", "count_with_club_mate"]].drop_duplicates()
        graph1 = {"data":[
                        go.Pie(
                            labels=df_final1['used_tickets'],
                            values=df_final1['count_used_tickets'],
                        )
                    ],
                    "layout":go.Layout(
                                title = "Nombre de tickets utilisés / partie",
                                hovermode="closest",
                                legend=legend_top)
                    }
        graph2 = {"data":[
                        go.Pie(
                            labels=df_final2['with_club_mate'],
                            values=df_final2['count_with_club_mate'],
                        )
                    ],
                    "layout":go.Layout(
                                title = "Taux de parties jouées en équipe",
                                hovermode="closest",
                                legend=legend_top)
                    }

        return(graph1, graph2)

#graphique de l'évolution par saison du WR
@app.callback(
    Output('graph_evolution_season', 'figure'),
    [Input("dropdown_joueur", "value")])
def evolution_graph(selected_name):
    if selected_name is None:
        raise PreventUpdate
    else:
        
        df_final = df.groupby(["name","season"]).agg({"WR": np.mean}).reset_index()
        df_final['WR'] = np.round(df_final['WR']*100,2)

        df_final = df_final[df_final["name"]==selected_name]
        df_final.sort_values("season", inplace=True)
    return {"data":[
                            go.Bar(
                                x=df_final['season'],
                                y=df_final.WR,
                                text=df_final.WR,
                                textposition='outside',
                                cliponaxis=False,
                                marker={"color":[couleur['vert'] if WR>=60 else couleur['jaune'] if WR>=50 else couleur["orange"] if WR>=35 else couleur["rouge"] for WR in df_final.WR]},
                                hovertemplate=
                                    "<b>Win rate : %{y}</b><br><br>" +
                                    "<extra></extra>",
                                showlegend=False)
                        ],
                        "layout":go.Layout(
                                    title = "Evolution du win rate par saison",
                                    margin=dict(l=17, r=17))
                    }        

#graphique des coéquipiers
@app.callback(
    Output('graph_teammates', 'figure'),
    [Input("dropdown_joueur", "value")])
def teamate_graph(selected_name):
    if selected_name is None:
        raise PreventUpdate
    else:
        
        df_final = df_coequipiers[df_coequipiers["name"]==selected_name].sort_values("nb_games", ascending=False)
        custom_data = np.transpose(np.array([df_final.WR, df_final.nb_win, df_final.points]))
            
    return {"data":[
                            go.Bar(
                                x=df_final['teammate'],
                                y=df_final.nb_games,
                                text=df_final.nb_games,
                                textposition='outside',
                                cliponaxis=False,
                                customdata=custom_data,
                                marker={"color":[couleur['vert'] if WR>=60 else couleur['jaune'] if WR>=50 else couleur["orange"] if WR>=35 else couleur["rouge"] for WR in df_final.WR]},
                                hovertemplate=
                                    "<b>Avec %{x}</b><br>" +
                                    "Win rate : %{customdata[0]}%<br>"
                                    "Nb games : %{y}<br>" +
                                    "Nb win : %{customdata[1]}<br>" +
                                    "Total points : %{customdata[2]}<br>" +
                                    "<extra></extra>",
                                showlegend=False)
                        ],
                        "layout":go.Layout(
                                    title = "Coéquipiers les + sollicités par {}".format(selected_name),
                                    margin=dict(l=17, r=17))
                    }  

#Info générale sur le brawler sélectionné
@app.callback(
    Output('info_brawler_selected', 'children'),
    [Input("dropdown_brawler", "value")])
def brawler_infos(selected_brawler):
    if selected_brawler is None:
        raise PreventUpdate
    else:
        ligne = df_top10brawlers[df_top10brawlers["brawler"]==selected_brawler]
        url_brawler = "https://media.brawltime.ninja/brawlers/{}/avatar.png?size=80".format(selected_brawler.replace(" ", "_").replace(".", "_").lower())
        return(
            dbc.Row([
                dbc.Col([html.Img(src=url_brawler, alt=selected_brawler, title =selected_brawler)],style=pretty_container, width=2),
                dbc.Col([html.H4("Win rate : {}%".format(ligne["WR"].ravel()[0]), style=H3)],style=pretty_container),
                dbc.Col([html.H4("{} games".format(ligne['nb_picks'].ravel()[0]), style=H3)],style=pretty_container),
                dbc.Col([html.H4("{} points rapportés".format(ligne["points"].ravel()[0]), style=H3)],style=pretty_container)
                ])
            )


#spider par mode du brawler et info sur le meilleur joueur avec
@app.callback(
    Output('info_brawler_selected_joueur', 'children'),
    Output('graph_spider_mode_par_brawler', 'figure'),
    [Input("dropdown_brawler", "value")])
def brawler_infos_mode(selected_brawler):
    if selected_brawler is None:
        raise PreventUpdate
    else:
        df_final1 = df_brawlers_mode[df_brawlers_mode["brawler"]==selected_brawler].sort_values(['mode'], ascending=False) 
        custom_data = np.transpose(np.array([df_final1.nb_picks, df_final1.points]))
                
        fig = go.Figure(data=go.Scatterpolar(
            r=df_final1['WR'],
            theta=df_final1['mode'],
            fill='toself', 
            name="Win rate",
            customdata=custom_data,
            hovertemplate=
                "<b>Win rate : %{r}%</b><br>" +
                "Nb games : %{customdata[0]}<br>" +
                "Total points : %{customdata[1]}<br>" +
                "<extra></extra>",
            ))
                                

        fig.update_layout(
        title_text="Win rate par mode de jeu",
        title_x=0.5,
        margin=dict(l=40, r=40,  b=10),
        polar=dict(
            radialaxis=dict(
            range=[0,100],
            visible=True
            )
        ),
        showlegend=False
        )

        df_final2 = df_joueur_brawler[df_joueur_brawler["brawler"]==selected_brawler].sort_values(['WR', "nb"], ascending=False) 
        joueur_plus_joue = [df_final2["name"].ravel()[df_final2["nb"].argmax()], np.max(df_final2["nb"])]
        meilleur_WR = [df_final2.iloc[0]["name"], df_final2.iloc[0]["WR"], df_final2.iloc[0]["nb"]]

        return(html.Div([html.H3("Le plus joué par :"),
                        html.H4("{} ({} games)".format(joueur_plus_joue[0], joueur_plus_joue[1])),
                        html.Br(),
                        html.Br(),
                        html.H3("Meilleur Win rate :"),
                        html.H4("{}, {}%({} games)".format(meilleur_WR[0], meilleur_WR[1], meilleur_WR[2])),
                        ], style=pretty_container),
                fig)

#Win Rate et nb pick par brawler par saison
@app.callback(
    Output('graph_WR_nb_brawler_season', 'figure'),
    [Input("dropdown_brawler", "value")])
def brawler_graph_WR_nb(selected_brawler):
    if selected_brawler is None:
        raise PreventUpdate
    else:
        df_final = df_brawlers_season[df_brawlers_season["brawler"]==selected_brawler]
        return(
                {
                    "data":[
                        go.Bar(
                            x=df_final['season'],
                            y=df_final.WR,
                            text=df_final.WR,
                            textposition='outside',
                            cliponaxis=False,
                            name="Win rate par saison ({})".format(selected_brawler),
                            showlegend=True),
                
                        go.Bar(
                            x=df_final['season'],
                            y=df_final.nb_picks,
                            text=df_final.nb_picks,
                            textposition='outside',
                            cliponaxis=False,
                            name="Nombre de picks par saison ({})".format(selected_brawler),
                            showlegend=True),
                    ],
                    "layout":go.Layout(
                                title_text = "WR et pick par saison",
                                legend=legend_top,
                                margin=dict(l=17, r=17) )
            }
        )

def improve_text_position(x):
    positions = ['top center', 'middle left', 'bottom center', 'middle right']  
    return([positions[i % len(positions)] for i in range(len(x))])

#Win Rate et nb pick par brawler par saison
@app.callback(
    Output('graph_scatter_WR_nb_brawler_season', 'figure'),
    [Input("dropdown_brawler_season", "value"),
    Input("dropdown_brawler_mode", "value")])
def brawler_graph_WR_nb(selected_season, selected_mode):
    if selected_season is None or selected_mode is None:
        raise PreventUpdate
    else:
        if selected_season =="Toutes":
            if selected_mode =="Tous":
                #brawler
                df_final = df_top10brawlers.sort_values("nb_picks")
            else:
                #brawler_mode
                df_final = df_brawlers_mode[df_brawlers_mode["mode"]==selected_mode].sort_values("nb_picks") 
        else : 
            if selected_mode =="Tous":
                #season brawler
                df_final = df_brawlers_season[df_brawlers_season["season"]==selected_season].sort_values("nb_picks")
            else:
                #season brawler mode
                df_final = df_brawlers_season_mode[df_brawlers_season_mode["season"]==selected_season]
                df_final = df_final[df_final["mode"]==selected_mode].sort_values("nb_picks")
        return(
                {
                    "data":[
                        go.Scatter(
                            x = df_final['nb_picks'],
                            y = df_final['WR'],
                            name = selected_season,
                            mode="markers+text",
                            text=df_final['brawler'],
                            hovertemplate = 
                                "<b>%{text}</b><br>" +
                                "Win rate : %{y}%<br>"
                                "Nb games : %{x}<br>" +
                                "<extra></extra>",
                            textposition=improve_text_position(df_final['nb_picks'])
                        )
                
                    ],
                    "layout":go.Layout(
                                title_text = "Win rate par nombre de picks<br />{}<br />Mode : {}".format(selected_season, selected_mode),
                                legend=legend_top,
                                yaxis=dict(title="WR"),
                                xaxis=dict(title="Nb picks"),
                                margin=dict(l=17, r=17))
            }
        )


#Tableau général par joueur et brawler
@app.callback(
    Output('tableau_brawler_joueur', 'children'),
    Output('title_tableau_brawler_joueur', 'children'),
    [Input("dropdown_brawler", "value")])
def tableau_general(selected_brawler):
    if selected_brawler is None:
        raise PreventUpdate
    else: 
    #sélection du joueur
        df_final = df_joueur_brawler[df_joueur_brawler["brawler"]==selected_brawler]
        cols = ['name', 'WR', 'nb']     
        table = df_final[cols].copy()
        table.sort_values('WR', inplace=True, ascending=False)
        #calcul des deux autres indicateurs
        table["percent_pick"]=np.round(table["nb"]/np.sum(table["nb"])*100,2)
        table.columns = ['Joueur', 'Win Rate', 'Nb Games', '% pick']

        tableau =dash_table.DataTable(
                    fixed_rows={'headers': True},
                    columns=[{"name": i, "id": i} for i in table.columns if i != 'id'],
                    data=table.to_dict("records"),
                    filter_action="native",
                    sort_action="native",
                    style_cell={
                        'padding': '10px',
                        'width': 'auto',
                        'textAlign': 'left',
                        'whiteSpace': 'normal',
                        'fontSize': 15,
                    },
                    style_table={
                        'overflowY': 'auto',
                        'height': 700,
                        'width': '100%'
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(240, 240, 240)',
                        }
                    ],
                        style_header={
                            'backgroundColor': 'rgb(210, 210, 210)',
                            'color': 'black',
                            'fontWeight': 'bold'
                        }
                )
        return(tableau, "Résultats pour {}".format(selected_brawler))

#Création du dropdown des maps sélectionnables
@app.callback(
    Output('dropdown_mode_map', 'options'),
    Output('dropdown_mode_map', 'value'),
    [Input("dropdown_mode", "value")])
def dropdown_mode_map(selected_mode):
    if selected_mode is None:
        raise PreventUpdate
    else: 
        #print(re.sub(r"(\w)([A-Z])", r"\1-\2", selected_mode).lower())
        df_final = df_map_brawlers[df_map_brawlers["mode"]==selected_mode]
        return(df_final['map_name'].unique(), df_final['map_name'].unique()[0])

  
#Afficahge des infos de la map sélectionnées
@app.callback(
    Output('affiche_map', 'src'),
    Output('info_map_WR', 'children'),
    Output('info_map_TOP3', 'children'),
    Output('info_map_worst3', 'children'),
    [Input("dropdown_mode_map", "value")])
def affiche_info_map(selected_map):
    if selected_map is None:
        raise PreventUpdate
    else: 
        #affiche map
        selected_map_id = df_map_brawlers[df_map_brawlers["map_name"]==selected_map]["map_id"].iloc[0]

        #affiche info map WR
        df_final_WR = df_map[df_map["map_name"]==selected_map].iloc[0]
        infos_WR = (re.sub(r"(\w)([A-Z])", r"\1-\2", df_final_WR["mode"]).lower(), df_final_WR["WR"], int(round(df_final_WR["WR"]*df_final_WR["nb_picks"]/100,0)), df_final_WR["nb_picks"])
        info_WR_div = [
            html.H4(["Win Rate (gagnées/jouées)"]),
            html.Img(src=url_mode(infos_WR[0]), alt=selected_map, title=selected_map, style={"text-align":"center"}),
            html.Br(),
            html.Br(),
            html.Div("{}%".format(infos_WR[1])),
            html.Div("({} gagnées/{} jouées)".format(infos_WR[2], infos_WR[3]))
        ]

        #affiche Top 3 brawlers
        df_final_top3 = df_map_brawlers[df_map_brawlers["map_name"]==selected_map].copy()
        df_final_top3.sort_values(["nb_picks", "WR", "points"], ascending=False, inplace=True)
        infos_top3 = {"top{}".format(i) : [df_final_top3.iloc[i]["brawler"], df_final_top3.iloc[i]["WR"], df_final_top3.iloc[i]["nb_picks"], df_final_top3.iloc[i]["points"]] for i in range(3)}
        infos_top3_div = [
                    html.H4("Top Picks"),
                    dbc.Row([
                        dbc.Col([html.H4("1.")]),
                        dbc.Col([html.Img(src=url_brawler(infos_top3["top0"][0]), alt=infos_top3["top0"][0], title=infos_top3["top0"][0])]),
                        dbc.Col([html.Div("{} games\nWR : {}%".format(infos_top3["top0"][2], infos_top3["top0"][1]))])
                    ]),
                    html.Br(),
                    dbc.Row([
                        dbc.Col([html.H4("2.")]),
                        dbc.Col([html.Img(src=url_brawler(infos_top3["top1"][0]), alt=infos_top3["top1"][0], title=infos_top3["top1"][0])]),
                        dbc.Col([html.Div("{} games\nWR : {}%".format(infos_top3["top1"][2], infos_top3["top1"][1]))])
                    ]),
                    html.Br(),
                    dbc.Row([
                        dbc.Col([html.H4("3.")]),
                        dbc.Col([html.Img(src=url_brawler(infos_top3["top2"][0]), alt=infos_top3["top2"][0], title=infos_top3["top2"][0])]),
                        dbc.Col([html.Div("{} games\nWR : {}%".format(infos_top3["top2"][2], infos_top3["top2"][1]))])
                    ])
        ]

         #affiche worst 3 brawlers
        df_final_worst3 = df_map_brawlers[df_map_brawlers["map_name"]==selected_map].copy()
        df_final_worst3.sort_values(["WR","nb_picks", "points"], ascending=True, inplace=True)
        infos_worst3 = {"worst{}".format(i) : [df_final_worst3.iloc[i]["brawler"], df_final_worst3.iloc[i]["WR"], df_final_worst3.iloc[i]["nb_picks"], df_final_worst3.iloc[i]["points"]] for i in range(3)}
        infos_worst3_div=[
                    html.H4("Worst Picks"),
                    dbc.Row([
                        dbc.Col([html.H4("1.")]),
                        dbc.Col([html.Img(src=url_brawler(infos_worst3["worst0"][0]), alt=infos_worst3["worst0"][0], title=infos_worst3["worst0"][0])]),
                        dbc.Col([html.Div("{} games\nWR : {}%".format(infos_worst3["worst0"][2], infos_worst3["worst0"][1]))])
                    ]),
                    html.Br(),
                    dbc.Row([
                        dbc.Col([html.H4("2.")]),
                        dbc.Col([html.Img(src=url_brawler(infos_worst3["worst1"][0]), alt=infos_worst3["worst1"][0], title=infos_worst3["worst1"][0])]),
                        dbc.Col([html.Div("{} games\nWR : {}%".format(infos_worst3["worst1"][2], infos_worst3["worst1"][1]))])
                    ]),
                    html.Br(),
                    dbc.Row([
                        dbc.Col([html.H4("3.")]),
                        dbc.Col([html.Img(src=url_brawler(infos_worst3["worst2"][0]), alt=infos_worst3["worst2"][0], title=infos_worst3["worst2"][0])]),
                        dbc.Col([html.Div("{} games\nWR : {}%".format(infos_worst3["worst2"][2], infos_worst3["worst2"][1]))])
                    ])
        ]
        
        #url_brawler
        return(url_map(int(selected_map_id)), info_WR_div, infos_top3_div, infos_worst3_div)

#tableau des résultats des maps par brawler et par joueurs
@app.callback( 
    Output('tableau_map_brawler', 'children'),
    Output('tableau_map_joueur', 'children'),
    [Input("dropdown_mode_map", "value")])
def affiche_tableaux_map(selected_map):
    if selected_map is None:
        raise PreventUpdate
    else: 
        #brawlers
        df_final = df_map_brawlers[df_map_brawlers["map_name"]==selected_map]
        cols = ['brawler', 'WR', 'points', "nb_picks"]     
        table = df_final[cols].copy()
        table.sort_values(['nb_picks','WR', 'points'], inplace=True, ascending=False)
        table = table[['brawler', "nb_picks",'WR', 'points']]
        table.columns = ['Brawler', 'Nb Games', 'Win Rate', 'Points gagnées']

        #brawlers
        table_brawler = dash_table.DataTable(
                    id="table_map_brawler",
                    style_as_list_view=True,
                    virtualization=False,
                    filter_action="native",
                    sort_action="native",
                    fixed_rows={'headers': True},
                    columns=[{"name": i, "id": i} for i in table.columns if i != 'id'],
                    data=table.to_dict("records"),
                    # page_size=14,
                    style_cell={
                        'padding': '10px',
                        'width': 'auto',
                        'textAlign': 'left',
                        'whiteSpace': 'normal',
                        'fontSize': 15,
                    },
                    style_table={
                        'overflowY': 'auto',
                        'height': 550,
                        'width': '100%',
                    },
                    # selected_cells = [{"row": row}],
                    style_data_conditional=[
                                        {
                                        'if': {'row_index': 'odd'},
                                        'backgroundColor': 'rgb(248, 248, 248)'
                                        }
                    ],
                    style_header={
                            'backgroundColor': 'rgb(210, 210, 210)',
                            'color': 'black',
                            'fontWeight': 'bold'
                        }
                )

        #par joueur
        df_final2 = df_map_joueurs[df_map_joueurs["map_name"]==selected_map]
        cols = ['name', 'WR', 'points', "nb_picks"]     
        table2 = df_final2[cols].copy()
        table2.sort_values(['nb_picks','WR', 'points'], inplace=True, ascending=False)
        table2 = table2[['name', "nb_picks",'WR', 'points']]
        table2.columns = ['Joueur', 'Nb Games', 'Win Rate', 'Points gagnées']

        table_joueur = dash_table.DataTable(
                    id="table_map_joueur",
                    style_as_list_view=True,
                    virtualization=True,
                    fixed_rows={'headers': True},
                    filter_action="native",
                    sort_action="native",
                    columns=[{"name": i, "id": i} for i in table2.columns if i != 'id'],
                    data=table2.to_dict("records"),
                    style_cell={
                        'padding': '10px',
                        'width': 'auto',
                        'textAlign': 'left',
                        'whiteSpace': 'normal',
                        'fontSize': 15,
                    },
                    style_table={
                        'overflowY': 'auto',
                        'height': 550,
                        'width': '100%',
                    },
                    # selected_cells = [{"row": row}],
                    style_data_conditional=[
                                        {
                                        'if': {'row_index': 'odd'},
                                        'backgroundColor': 'rgb(248, 248, 248)'
                                        }
                    ],
                    style_header={
                            'backgroundColor': 'rgb(210, 210, 210)',
                            'color': 'black',
                            'fontWeight': 'bold'
                        }
                )
        return(table_brawler, table_joueur)


if __name__ == '__main__':
    app.run_server(host = HOST, port = PORT, debug=True)
