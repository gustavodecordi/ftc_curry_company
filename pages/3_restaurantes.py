# Libraries
import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image
from haversine import haversine   # Biblioteca para o cálculo das distâncias (latitude, longitude)

# from matplotlib import pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static

st.set_page_config( 
        page_title = 'Visão Restaurantes',
        page_icon = '🍽',
        layout = 'wide'
)

# -------------------------------------
# Funções
# -------------------------------------
def pizza_sunburst( dfm ):
    cols = ['City','Road_traffic_density','Time_taken(min)']
    dfm_sel_5 = dfm.loc[:,cols].groupby(['City','Road_traffic_density']).agg( { 'Time_taken(min)': ['mean','std'] }).reset_index()
    dfm_sel_5.columns = ['City','Road_traffic_density','mean','std']

    return px.sunburst( dfm_sel_5, path = ['City','Road_traffic_density'], values = 'mean', color = 'std', 
                       color_continuous_scale = 'RdBu', color_continuous_midpoint = np.average( dfm_sel_5['std'] ) )
        
def avg_std_time_plot( dfm ):
    df_sel_3 = dfm.loc[:,['City','Time_taken(min)']].groupby('City').agg( { 'Time_taken(min)': ['mean','std'] }).reset_index()
    df_sel_3.columns = ['City','mean','std']
    fig = go.Figure()
    fig.add_trace( go.Bar( name = 'Control',
                           x = df_sel_3['City'],
                           y = df_sel_3['mean'],
                           error_y = dict( type = 'data', array = df_sel_3['std'] )
                         ) 
                 )
    return fig.update_layout( barmode = 'group')

def distance( dfm, metrica = 'Yes' ):
    cols = ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
    dfm['Distance (km)'] = ( dfm.loc[:,cols]
                              .apply( lambda x: haversine( 
                                                         (x['Restaurant_latitude'],x['Restaurant_longitude']),                                                                                                    (x['Delivery_location_latitude'],x['Delivery_location_longitude']) 
                                                         ), 
                                      axis = 1 ) 
                           ) 
    if metrica == 'Yes':
        return round( dfm.loc[:,'Distance (km)'].mean(), 2)
    else:
        return dfm.loc[:,['City','Distance (km)']].groupby(['City']).mean().reset_index()
            
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

# --------------------------- Inicio da Estrutura lógica do código --------------------------
# ------------------------
# Import dataset
# ------------------------
df = pd.read_csv('train.csv')

# Guarda o conteúdo do DF original em uma cópia dfm (data frame moderado)
dfm = df.copy()

# ------------------------
# Limpando os dados
# ------------------------
dfm = clean_code( dfm )

# =================================================
# Barra lateral
# =================================================
st.header('Marketplace - Visão dos Restaurantes')

# Importação de imagem
# image_path = 'C:\\Users\\gusta\\Desktop\\comunidade_ds\\cursos\\ftc\\ciclo7\\segunda_5_dezembro\\logo.png'
image = Image.open( 'logo.png' )
st.sidebar.image( image, width = 120 )

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

# =================================================
# Layout no Streamlit
# =================================================
with st.container():
    st.title( 'Overall Metrics' )
    col1, col2, col3, col4, col5, col6 = st.columns( 6 )
    with col1:
        # Entregadores únicos
        qte_entregadores_unicos = dfm['Delivery_person_ID'].nunique()
        col1.metric( 'Entregadores únicos', qte_entregadores_unicos )

    with col2:
        # Distância média
        col2.metric( 'Distância média (km)', distance( dfm, metrica = 'Yes' ) )

    with col3:
        # Tempo de entrega médio c/Festival
        dfm_sel_6 = dfm.loc[:,['Festival','Time_taken(min)']].groupby(['Festival']).agg( { 'Time_taken(min)': ['mean','std'] })
        dfm_sel_6.columns = ['mean','std']
        dfm_sel_6 = dfm_sel_6.reset_index()
        tm_festival = round( dfm_sel_6.iloc[1,1], 2)
        col3.metric( 'Tempo médio C/Festival', tm_festival )


    with col4:
        # Desvio padrão do Tempo de entrega médio c/Festival
        std_festival = round( dfm_sel_6.iloc[1,2], 2)
        col4.metric( 'Std C/Festival', std_festival )

    with col5:
        # Tempo de entrega médio SEM /Festival
        tm_sem_festival = round( dfm_sel_6.iloc[0,1], 2)
        col5.metric( 'Tempo médio S/Festival', tm_sem_festival )

    with col6:
        # Desvio padrão do Tempo de entrega médio SEM/Festival
        std_sem_festival = round( dfm_sel_6.iloc[0,2], 2)
        col6.metric( 'Std S/Festival', std_sem_festival )

with st.container():
    st.markdown("""---""")
    st.markdown("#### Distribuição da distância")
    avg_distance = distance( dfm, metrica = 'No' )
    fig = go.Figure( data=[ go.Pie( labels=avg_distance['City'], values=avg_distance['Distance (km)'], pull=[0, 0.1, 0])])
    st.plotly_chart( fig )

with st.container():
    st.markdown("""---""")
    col1, col2 = st.columns( 2 )
    with col1:
        st.markdown("#### Tempo médio de entrega por cidade")
        st.plotly_chart( avg_std_time_plot( dfm ), use_container_width = True )

    with col2:
        st.markdown("##### Distribuição do desvio padrão por cidade e trânsito")
        st.plotly_chart( pizza_sunburst( dfm ) )

with st.container():
    st.markdown("""---""")
    st.markdown("##### Distribuição do desvio padrão por cidade e pedido")
    cols = ['City','Type_of_order','Time_taken(min)']
    dfm_sel_4 = dfm.loc[:,cols].groupby(['City','Type_of_order']).agg( { 'Time_taken(min)': ['mean','std'] }).reset_index()
    dfm_sel_4.columns = ['City','Type_of_order','mean','std']
    st.dataframe( dfm_sel_4 )


