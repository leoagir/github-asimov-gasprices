import dash
from   dash import html, dcc, Input, Output, State

import dash_bootstrap_components as dbc
from   dash_bootstrap_templates  import ThemeSwitchAIO

import plotly.express as px
import plotly.graph_objects as go

import pandas as pd

# ========= App ============== #
FONT_AWESOME = ["https://use.fontawesome.com/releases/v5.10.2/css/all.css"]
dbc_css      = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.4/dbc.min.css"

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY, dbc_css])
app.scripts.config.serve_locally = True
server = app.server

# ========== Styles ============ #

template_theme1 = "flatly"
template_theme2 = "vapor"

url_theme1 = dbc.themes.FLATLY
url_theme2 = dbc.themes.VAPOR

style_tab_card = {'height': '100%'}

# ===== Reading n cleaning File ====== #
# Lendo o arquivo CSV com os dados de preços de gasolina
df_main = pd.read_csv("data_gas.csv")

# Convertendo as colunas de datas para o formato datetime
df_main['DATA INICIAL'] = pd.to_datetime(df_main['DATA INICIAL'])
df_main['DATA FINAL']   = pd.to_datetime(df_main['DATA FINAL'])

# Calculando a data média entre DATA INICIAL e DATA FINAL
df_main['DATA MEDIA'] = ((df_main['DATA FINAL'] - df_main['DATA INICIAL'])/2) + df_main['DATA INICIAL']

# Ordenando o DataFrame pela data média em ordem crescente
df_main = df_main.sort_values(by='DATA MEDIA', ascending=True)

# Renomeando colunas para nomes mais descritivos
df_main.rename(columns={'DATA MEDIA':'DATA'}, inplace=True)
df_main.rename(columns={'PREÇO MÉDIO REVENDA': 'VALOR REVENDA (R$/L)'}, inplace=True)

# Criando uma nova coluna 'ANO' extraindo o ano da coluna 'DATA'
df_main["ANO"] = df_main["DATA"].apply(lambda x: str(x.year))

# Resetando o index por uma questão organizacional
df_main = df_main.reset_index()

# Filtrando pois só falaremos da gasolina comum
df_main = df_main[df_main.PRODUTO == 'GASOLINA COMUM'] # ou podemos deixar todos os produtos e depois utilizar como um filtro geral

# Excluindo colunas que não usaremos
df_main.drop([
    'UNIDADE DE MEDIDA'             , 'COEF DE VARIAÇÃO REVENDA' , 'COEF DE VARIAÇÃO DISTRIBUIÇÃO'  , 
    'NÚMERO DE POSTOS PESQUISADOS'  , 'DATA INICIAL'             , 'DATA FINAL'                     , 
    'PREÇO MÁXIMO DISTRIBUIÇÃO'     , 'PREÇO MÍNIMO DISTRIBUIÇÃO', 'DESVIO PADRÃO DISTRIBUIÇÃO'     , 
    'MARGEM MÉDIA REVENDA'          , 'PREÇO MÍNIMO REVENDA'     , 'PREÇO MÁXIMO REVENDA'           ,
    'DESVIO PADRÃO REVENDA'         , 'PRODUTO'                  , 'PREÇO MÉDIO DISTRIBUIÇÃO'
], inplace=True, axis=1)

# Verifying the data types
# df_main.info()

# To dict - para salvar no dcc.store
df_store = df_main.to_dict()

# =========  Layout  =========== #
app.layout = dbc.Container(children=[
    # Armazenamento de dataset
    dcc.Store(id='dataset', data=df_store),
    dcc.Store(id='dataset_fixed', data=df_store),

    # Row 1
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([  
                            html.Legend("Gas Prices Analysis")
                        ], sm=8),
                        dbc.Col([        
                            html.I(className='fa fa-filter', style={'font-size': '300%'})
                        ], sm=4, align="center")
                    ]),
                    dbc.Row([
                        dbc.Col([
                            ThemeSwitchAIO(aio_id="theme", themes=[url_theme1, url_theme2]),
                            html.Legend("Asimov Academy")
                        ])
                    ], style={'margin-top': '10px'}),
                    dbc.Row([
                        dbc.Col([
                            dbc.Button("Visite o Site", href="https://asimov.academy/", target="_blank")
                        ])
                    ], style={'margin-top': '10px'})
                ])
            ], style=style_tab_card)
        ], sm=4, lg=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H3('Máximos e Mínimos'),
                            dcc.Graph(id='static-maxmin', config={"displayModeBar": False, "showTips": False})
                        ])
                    ])
                ])
            ], style=style_tab_card)
        ], sm=8, lg=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H6('Ano de análise:'),
                            dcc.Dropdown(
                                id="select_ano",
                                value=df_main.at[df_main.index[1],'ANO'],
                                clearable = False,
                                options=[
                                    {"label": x, "value": x} for x in df_main.ANO.unique()
                            ], style={'background-color': 'rgba(0, 0, 0, 0.3'}),
                        ], sm=6),
                        dbc.Col([
                            html.H6('Região de análise:'),
                            dcc.Dropdown(
                                id="select_regiao",
                                value=df_main.at[df_main.index[1],'REGIÃO'],
                                clearable = False,
                                options=[
                                    {"label": x, "value": x} for x in df_main.REGIÃO.unique()
                            ], style={'background-color': 'rgba(0, 0, 0, 0.3'}),
                        ], sm=6)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='regiaobar_graph', config={"displayModeBar": False, "showTips": False})
                        ], sm=12, md=6),
                        dbc.Col([
                            dcc.Graph(id='estadobar_graph', config={"displayModeBar": False, "showTips": False})
                        ], sm=12, md=6)    
                    ], style={'column-gap': '0px'})
                ])
            ], style=style_tab_card)
        ], sm=12, lg=7)
    ], className='g-2 my-auto', style={'margin-top': '7px'}), # end row
    
    # Row 2
    dbc.Row([
        dbc.Col([       
            dbc.Card([
                dbc.CardBody([
                    html.H3('Preço x Estado'),
                    html.H6('Comparação temporal entre estados'),
                    dbc.Row([
                        dbc.Col([
                                dcc.Dropdown(
                                id="select_estados0",
                                value=[df_main.at[df_main.index[3],'ESTADO'], df_main.at[df_main.index[13],'ESTADO'], df_main.at[df_main.index[6],'ESTADO']],
                                clearable = False,
                                multi=True,
                                options=[
                                    {"label": x, "value": x} for x in df_main.ESTADO.unique()
                                ], style={'background-color': 'rgba(0, 0, 0, 0.3'}),
                        ], sm=10),
                    ]),
                    dcc.Graph(id='animation_graph', config={"displayModeBar": False, "showTips": False})
                ])
            ], style=style_tab_card)
        ], sm=12, md=6, lg=5),
        dbc.Col([    
            dbc.Card([
                dbc.CardBody([
                    html.H3('Comparação Direta'),
                    html.H6('Qual preço é menor em um dado período de tempo?'),
                    dbc.Row([
                        dbc.Col([                                   
                            dcc.Dropdown(
                                id="select_estado1",
                                value=df_main.at[df_main.index[3],'ESTADO'],
                                clearable = False,
                                options=[
                                    {"label": x, "value": x} for x in df_main.ESTADO.unique()
                            ], style={'background-color': 'rgba(0, 0, 0, 0.3'}),
                        ], sm=10, md=5),
                        dbc.Col([
                            dcc.Dropdown(
                                id="select_estado2",
                                value=df_main.at[df_main.index[1],'ESTADO'],
                                clearable = False,
                                options=[
                                    {"label": x, "value": x} for x in df_main.ESTADO.unique()
                            ], style={'background-color': 'rgba(0, 0, 0, 0.3'}),
                        ], sm=10, md=6),
                    ], style={'margin-top': '20px'}, justify='center'),
                    dcc.Graph(id='direct_comparison_graph', config={"displayModeBar": False, "showTips": False}),
                    html.P(id='desc_comparison', style={'color': 'gray', 'font-size': '80%'}),
                ])
            ], style=style_tab_card)
        ], sm=12, md=6, lg=4),
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id='card1_indicators', config={"displayModeBar": False, "showTips": False}, style={'margin-top': '30px'})
                        ])
                    ], style=style_tab_card)
                ])
            ], justify='center', style={'padding-bottom': '7px', 'height': '50%'}),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id='card2_indicators', config={"displayModeBar": False, "showTips": False}, style={'margin-top': '30px'})
                        ])
                    ], style=style_tab_card)
                ])
            ], justify='center', style={'height': '50%'})
        ], sm=12, lg=3, style={'height': '100%'})
    ], justify='center', className='g-2 my-auto'),

    # Row 3 - RangeSlider
    dbc.Row([
        dbc.Col([
            dbc.Card([                
                dbc.Row([
                    dbc.Col([
                        dbc.Button([html.I(className='fa fa-play')], id="play-button", style={'margin-right': '15px'}),  
                        dbc.Button([html.I(className='fa fa-stop')], id="stop-button")
                    ], sm=12, md=1, style={'justify-content': 'center', 'margin-top': '10px'}),
                    dbc.Col([
                        dcc.RangeSlider(
                            id='rangeslider',
                            marks= {int(x): f'{x}' for x in df_main['ANO'].unique()},
                            step=3,                
                            min=2004,
                            max=2021,
                            value=[2004,2021],   
                            dots=True,             
                            pushable=3,
                            tooltip={'always_visible':False, 'placement':'bottom'},
                        )
                    ], sm=12, md=10, style={'margin-top': '15px'}),
                    # componente invisivel
                    dcc.Interval(id='interval', interval=10000),
                ], className='g-1', style={'height': '20%', 'justify-content': 'center'})
                
            ], style=style_tab_card)
        ])
    ], className='g-2 my-auto')
], fluid=True, style={'height': '100%'})

# ======== Callbacks ========== #


# Run server
if __name__ == '__main__':
    app.run_server(debug=True)
