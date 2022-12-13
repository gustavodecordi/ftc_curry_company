# Libraries
import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image

st.set_page_config( 
        page_title = 'Visão Entregadores',
        page_icon = '📦',
        layout = 'wide'
)

# -------------------------------------
# Funções
# -------------------------------------
def avg_by_traffic_or_weather( dfm, col):
    dfm_sel_mean_std = ( dfm.loc[:,['Delivery_person_Ratings', col]]
                            .groupby([col])
                            .agg( {'Delivery_person_Ratings':['mean','std']} ) )
    dfm_sel_mean_std.columns = ['mean','std']
    return dfm_sel_mean_std.reset_index()
        
def top_delivers( dfm, parameter_asc ):
    cols = ['Delivery_person_ID','City','Time_taken(min)']
    dfm_sel_6 = dfm.loc[:,cols].groupby(['City','Delivery_person_ID']).mean()
    dfm_sel_6 = dfm_sel_6.sort_values(['City','Time_taken(min)'], ascending = parameter_asc ).reset_index()
    return dfm_sel_6
        
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


def recorte_data_frame(lista, data):
    lista_data_frames = []
    # Gera uma lista formada pelos data frames representativos de cada cidade
    # com 10 linhas cada.
    for elem in lista:
        lista_data_frames.append(data.loc[data["City"]==elem,:].head(10)) 
    # Concatena os data frames da lista para compor um novo data frame
    for i in range(len(lista_data_frames)):
        df_final = pd.concat(lista_data_frames).reset_index(drop=True)
    
    return df_final

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
# ===============================================
st.header('Marketplace - Visão Entregadores')

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
# Esse primeiro container vai conter quatro colunas com os dados de maior, menor idades; melhor, pior condições 
with st.container():
    st.title( 'Overall Metrics' )
    col1, col2, col3, col4 = st.columns( 4, gap = 'large' ) 
    # Esse 'gap' fornece a distância entre entre as colunas
    with col1:
        # A maior idade dos entregadores
        maior_idade = dfm['Delivery_person_Age'].max()
        col1.metric( 'Maior idade', maior_idade )

    with col2:
        # A menor idade dos entregadores
        menor_idade = dfm['Delivery_person_Age'].min()
        col2.metric( 'Menor idade', menor_idade )

    with col3:
        # A melhor condição dos veículos
        melhor = dfm['Vehicle_condition'].max()
        col3.metric( 'Melhor condição', melhor )

    with col4:
        # A pior condição dos veículos
        pior = dfm['Vehicle_condition'].min()
        col4.metric( 'Pior condição', pior )

with st.container():
    st.markdown( """---""" )  # Cria-se uma linha para separar do outro container
    st.title( 'Avaliações' )
    col1, col2 = st.columns( 2 )

    with col1:
        st.subheader( 'Avaliações médias por entregador' )
        cols = ['Delivery_person_ID','Delivery_person_Ratings']
        dfm_sel_3 = ( dfm.loc[:,cols].groupby(['Delivery_person_ID'])
                                   .mean()
                                   .reset_index() )
        dfm_sel_3.columns = ['Delivery_person_ID','Nota_media_por_entregador']
        st.dataframe( dfm_sel_3 )

    with col2:
        st.subheader( 'Avaliações médias por trânsito' )
        st.dataframe( avg_by_traffic_or_weather( dfm, 'Road_traffic_density') )

        st.subheader( 'Avaliações médias por condições climáticas' )
        st.dataframe( avg_by_traffic_or_weather( dfm, 'Weatherconditions') )

with st.container():
    st.markdown( """---""" )  # Cria-se uma linha para separar do outro container
    st.title( 'Velocidade de entrega' )
    col1, col2 = st.columns( 2 )
    with col1:
        st.subheader( 'Top entregadores mais rápidos' )
        lista_cidades = list(dfm['City'].unique())
        st.dataframe( recorte_data_frame(lista_cidades, top_delivers( dfm, parameter_asc = True )) )

    with col2:
        st.subheader( 'Top entregadores mais lentos' )
        st.dataframe( recorte_data_frame(lista_cidades, top_delivers( dfm, parameter_asc = False )) )