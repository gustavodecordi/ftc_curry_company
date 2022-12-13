# Libraries
import pandas as pd
import numpy as np
from haversine import haversine   # Biblioteca para o cálculo das distâncias (latitude, longitude)

from matplotlib import pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config( 
        page_title = 'Visão Empresa',
        page_icon = '📈',
        layout = 'wide'
)

# =================================================
# Funções
# =================================================
def order_metric( dfm ):
    dfm_sel_1 = dfm.loc[:,['ID','Order_Date']].groupby(['Order_Date']).count().reset_index()
    fig = px.bar(dfm_sel_1, x='Order_Date', y='ID')

    return fig

def traffic_order_share( dfm ):
    dfm_sel_3 = ( dfm.loc[:, ['ID','Road_traffic_density']]
                     .groupby(['Road_traffic_density'])
                     .count()
                     .reset_index() )
    dfm_sel_3['delivery_percent_by_traffic'] = dfm_sel_3['ID'].apply( lambda x: 100*x / dfm_sel_3['ID'].sum() )
                                                
    px.pie(dfm_sel_3, values = 'delivery_percent_by_traffic', names = 'Road_traffic_density')
    fig = px.pie(dfm_sel_3, values = 'delivery_percent_by_traffic', names = 'Road_traffic_density')
    return fig

def traffic_order_city( dfm ):
    cols = ['ID','City','Road_traffic_density']
    dfm_sel_4 = dfm.loc[:,cols].groupby(['City','Road_traffic_density']).count().reset_index()
    fig = px.scatter(dfm_sel_4, x='City',y='Road_traffic_density',size='ID',color='City',
                      title='Relação entre o tipo de trânsito e a cidade de entrega', 
                      labels = {'City': 'Cidade', 'Road_traffic_density': 'Tipo de trânsito'},
                      width=800, height=500 
                     )
    return fig

def order_by_week( dfm ):
    # Cria a coluna de semanas
    dfm['Week_of_year'] = dfm['Order_Date'].dt.strftime( '%U' )   
    dfm_sel_2 = dfm.loc[:,['ID','Week_of_year']].groupby(['Week_of_year']).count().reset_index()
    fig = px.line(dfm_sel_2, x='Week_of_year', y='ID', 
                    title='Distribuição das entregas por semana', 
                    labels = {'Week_of_year': 'Semana', 'ID': 'Quantidade de entregas'}
                 )
    return fig

def order_share_by_week( dfm ):
    # Qte de pedidos por semana
    df_aux01 = dfm.loc[:,['ID','Week_of_year']].groupby(['Week_of_year']).count().reset_index()
    # Qte de trabalhadores únicos por semana
    df_new = ( dfm.loc[:,['Delivery_person_ID','Week_of_year']]
                  .groupby(['Week_of_year'])
                  .nunique()
                  .reset_index() )
    # a qte de pedidos por entregador por semana.
    df_aux01['Qte_pedidos_entregador_por_semana'] = df_aux01['ID'] / df_new['Delivery_person_ID']

    fig = px.line( df_aux01, x='Week_of_year', y='Qte_pedidos_entregador_por_semana', 
                    title='Evolução das entregas por semana por entregador', 
                    labels = {'Week_of_year': 'Semana', 'Qte_pedidos_entregador_por_semana': 'Número_de_pedidos_por_entregador_por_semana'},
                    width=800, height=500 
                 )
    return fig

def india_map( dfm ):
    cols = ['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']
    dfm_sel_6 = dfm.loc[:,cols].groupby(['City','Road_traffic_density']).median().reset_index()

    map = folium.Map()

    for i in range(len(dfm_sel_6)):
        folium.Marker([dfm_sel_6.loc[i,'Delivery_location_latitude'], dfm_sel_6.loc[i,'Delivery_location_longitude']],
                       popup = dfm_sel_6.loc[i,['City','Road_traffic_density']]).add_to(map)
    folium_static( map, width=1024, height=600 )
    
    return None

# Limpeza dos dados
def clean_code( dfm ):
    """Esta função possui a responsabilidade de limpar o dataframe.
       Tipos de limpeza:
       
       1 - Remoção de dados faltantes do tipo NaN
       2 - Conversão de tipos de dados nas colunas
       3 - Remoção dos espaços nas colunas (vaiáveis de texto)
       4 - Formatação da coluna de datas
       5 - Limpeza da coluna de tempo (remoção do texto ans do número)
       
       Input: Dataframe
       Output: Dataframe
    """
    # Exclui as linhas com dados faltantes na coluna 'Delivery_person_Age'
    linhas_selecionadas = dfm['Delivery_person_Age'] != 'NaN '
    dfm = dfm.loc[linhas_selecionadas, :].copy()

    # Exclui as linhas com dados faltantes na coluna 'Road_traffic_density'
    linhas_selecionadas = dfm['Road_traffic_density'] != 'NaN '
    dfm = dfm.loc[linhas_selecionadas, :].copy()

    # Exclui as linhas com dados faltantes na coluna 'City'
    linhas_selecionadas = dfm['City'] != 'NaN '
    dfm = dfm.loc[linhas_selecionadas, :].copy()

    # Exclui as linhas com dados faltantes na coluna 'Festival'
    linhas_selecionadas = dfm['Festival'] != 'NaN '
    dfm = dfm.loc[linhas_selecionadas, :].copy()

    # Converte os dados dessa coluna de texto para int
    dfm['Delivery_person_Age'] = dfm['Delivery_person_Age'].astype(int)

    # Converte os dados dessa coluna de texto para float
    dfm['Delivery_person_Ratings'] = dfm['Delivery_person_Ratings'].astype(float)

    # Converte as datas anteriormente em formato de objeto para datetime
    dfm['Order_Date'] = pd.to_datetime(dfm['Order_Date'], format = '%d-%m-%Y' )

    # Exclui as linhas com dados faltantes na coluna 'multiple_deliveries'
    linhas_selecionadas_multiple_deliveries = dfm['multiple_deliveries'] != 'NaN '
    dfm = dfm.loc[linhas_selecionadas_multiple_deliveries, :].copy()
    # Converte os dados dessa coluna de texto para int
    dfm['multiple_deliveries'] = dfm['multiple_deliveries'].astype(int)

    # Reordena os índices do DF
    dfm = dfm.reset_index(drop=True)
    # Extrai os espaços em branco dos dados na colunas 'ID', 'Road_traffic_density', 'Type_of_order', 'Type_of_vehicle', 'Festival' e 'City'
    dfm.loc[:,'ID'] = dfm.loc[:,'ID'].str.strip()
    dfm.loc[:,'Road_traffic_density'] = dfm.loc[:,'Road_traffic_density'].str.strip()
    dfm.loc[:,'Type_of_order'] = dfm.loc[:,'Type_of_order'].str.strip()
    dfm.loc[:,'Type_of_vehicle'] = dfm.loc[:,'Type_of_vehicle'].str.strip()
    dfm.loc[:,'City'] = dfm.loc[:,'City'].str.strip()
    dfm.loc[:,'Festival'] = dfm.loc[:,'Festival'].str.strip()

    # Retira o '(min) ', deixando apenas o tempo.
    dfm['Time_taken(min)'] = dfm['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1] )
    # Transformar em inteiro
    dfm['Time_taken(min)'] = dfm['Time_taken(min)'].astype(int)
    
    return dfm 

#---------------------------- Início da estrutura lógica do código -----------------------
# importando o dataset
df = pd.read_csv('train.csv')

# Guarda o conteúdo do DF original em uma cópia dfm (data frame moderado)
dfm = df.copy()

#------------------------------
# Limpando o dataframe
#------------------------------
dfm = clean_code( dfm )

# =================================================
# Barra lateral
# =================================================
st.header('Marketplace - Visão do Cliente')

# Importação de imagem
# image_path = 'C:\\Users\\gusta\\Desktop\\comunidade_ds\\cursos\\ftc\\ciclo7\\segunda_5_dezembro\\logo.png'
image = Image.open( 'logo.png' )
st.sidebar.image( image, width = 120 )

st.markdown(
     """
     <style>
     [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
         width: 250px;
       }
       [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
           width: 500px;
           margin-left: -500px;
        }
        </style>
        """,
        unsafe_allow_html=True)


# Barra do lado
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

# Filtro
st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
                    'Até qual valor?',
                    # valor default
                    value = pd.datetime(2022, 4, 13),
                    # valor minimo
                    min_value = pd.datetime(2022, 2, 11),
                    # valor máximo
                    max_value = pd.datetime(2022, 4, 6),
                    format = 'DD-MM-YYYY'
)

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect( 'Quais as condições do trânsito?',
                         ['Low','Medium','High','Jam'],
                          default = 'Low'
                      )

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by CDS')

# Filtro de data (datas menores do que a selecionada)
linhas_selecionadas = dfm['Order_Date'] < date_slider 
dfm = dfm.loc[ linhas_selecionadas, :] 

# Filtro de trânsito 
# A função 'isin' seleciona apenas as linhas cujas condições de tráfego foram passadas pelo usuário na seleção 
linhas_selecionadas = dfm['Road_traffic_density'].isin( traffic_options )
dfm = dfm.loc[ linhas_selecionadas, :] 

#st.dataframe(dfm)
# =================================================
# Layout no Streamlit
# =================================================
# Criar três abas das visões do Dashboard
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial','Visão Tática','Visão Geográfica'] )

# Tudo o que estiver indentado dentro de 'with' vai ficar dentro da tab1 ('Visão Gerencial')
with tab1:
    # Visão Gerencial
    with st.container(): # Cria um container para alocar a figura de 'Pedidos por dia'
        st.markdown('# Orders by day')
        fig = order_metric( dfm )
        st.plotly_chart( fig, use_container_width = True )
        
    with st.container(): # Cria um outro container para alocar as duas colunas abaixo
        # Cria duas colunas dentro da tab1
        col1, col2 = st.columns( 2 )
        with col1:
            st.header('Traffic Order share')
            fig = traffic_order_share( dfm )
            st.plotly_chart( fig, use_container_width = True )
                                                 
        with col2:
            st.header('Traffic Order city')
            fig = traffic_order_city( dfm )
            st.plotly_chart( fig, use_container_width = True )
            
with tab2:
    with st.container(): 
        st.markdown('# Orders by week')
        fig = order_by_week( dfm )
        st.plotly_chart( fig, use_container_width = True )
    
    with st.container(): 
        st.markdown('# Order share by week')
        fig = order_share_by_week( dfm )
        st.plotly_chart( fig, use_container_width = True )
    
with tab3:
    st.header('India Map')
    india_map( dfm )
   