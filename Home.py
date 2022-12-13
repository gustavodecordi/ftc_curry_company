import streamlit as st
from PIL import Image

# Para poder juntar as 3 páginas da pasta 'pages' usamos a função abaixo
# O streamlit entende que os 3 arquivos buscados estão na pasta 'pages'
st.set_page_config( 
        page_title = 'Home',
        page_icon = '💎',
        layout = 'wide'
)

# image_path = 'C:\\Users\\gusta\\Desktop\\comunidade_ds\\cursos\\ftc\\ciclo7\\quarta_7_dezembro\\'
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

st.markdown(
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos restaurantes
    ### Ask for Help
    - Time de Data Science no Discord
        - @gustavo
""" )
