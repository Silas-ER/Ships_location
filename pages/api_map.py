import requests, json, folium, os, asyncio, aiohttp
import pandas as pd
import streamlit as st

from datetime import datetime
from dotenv import load_dotenv
from services.comum_services import read_file
from streamlit_folium import folium_static

# Configuração de api
load_dotenv()
key = os.getenv('API_KEY')

# Configuração da página
st.set_page_config(layout="wide")

# Aplicando CSS
st.markdown(
    """
    <style>
        .element-container {
            padding-top: 5px;
            margin-top: 0px;
        }
        .stMarkdown hr {
            margin-top: 5px;
            margin-bottom: 5px;
        }
        .st-emotion-cache-gi0tri {
            margin-top: 5px;
            margin-bottom: 5px;
        }
        h1 {
            text-align: center;
        }
        h3 {
            padding-bottom: 1px !important;
            line-height: 0.25 !important;
            text-align: center;
        }
        p {
            text-align: center;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Leitura do arquivo de barcos
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, '../data/list_boats.txt')
boats, fleet = read_file(file_path)

#Limitação de 10 requisições simultâneas
sem = asyncio.Semaphore(10)  

# Função assíncrona para obter os dados de cada barco
async def fetch_data(session, MMSI):
    url_consult = f'http://api.shipdt.com/DataApiServer/apicall/GetSingleVesselShip?k={key}&id={MMSI}'
    async with sem:
        try:
            async with session.get(url_consult, timeout=30) as response:
                response.raise_for_status()
                response_dict = await response.json()
                return response_dict['data']
        except aiohttp.ClientError as e:
            st.error(f"Erro na consulta do MMSI {MMSI}: {e}")
            return {}

# Função para realizar as chamadas de forma assíncrona
async def df_map_async(list_MMSI):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_data(session, MMSI) for MMSI in list_MMSI]
        df_list = []
        progress_bar = st.progress(0)
        
        for i, task in enumerate(asyncio.as_completed(tasks)):
            result = await task
            if result:
                df_list.append(pd.json_normalize(result))
            progress_bar.progress((i + 1) / len(list_MMSI))
        
        df = pd.concat(df_list, ignore_index=True)
        #st.write("Colunas antes da renomeação: ", df.columns.tolist())  # Verificando o conteúdo do DataFrame após o processamento
        
        # Conversão direta de lat/lon dentro da função
        df['lat'] = df['lat'] / 1e6
        df['lon'] = df['lon'] / 1e6
        
        return df

# Cachear apenas o resultado serializável (DataFrame)
@st.cache_data(ttl=3600)
def get_cached_data(fleet):
    df = asyncio.run(df_map_async(fleet))
    return df

# Função de formatação para exibição da tabela
def df_to_view(df):
    # Remover colunas que não serão utilizadas e ajustar tipos
    df = df.drop(['ShipID', 'imo', 'nationality', 'shiptype', 'left', 'trail', 'draught', 
                  'dest', 'dest_std', 'destcode', 'eta', 'eta_std', 'navistat', 'rot',
                  'cog', 'hdg', 'length', 'width'], axis=1)
    
    df = df.astype({
        'mmsi': 'string',
        'name': 'string',
        'callsign': 'string'
    })

    # Renomear e ajustar colunas
    df = df.rename(columns={
        'mmsi': 'MMSI',
        'name': 'Nome',
        'callsign': 'ID Equipamento',
        'lat': 'Latitude',
        'lon': 'Longitude',
        'sog': 'Velocidade',
        'lasttime': 'Última Atualização'
    })

    # Formatação de colunas
    df['Última Atualização'] = df['Última Atualização'].apply(lambda x: datetime.fromtimestamp(x).strftime('%d/%m/%Y %H:%M:%S'))
    df['Velocidade'] = (df['Velocidade'] * 3.6).round(2)

    return df

# Função de criação do mapa com os dados do dataframe
def map_creation(df):
    map = folium.Map(location=[-5.79448, -35.211], zoom_start=3)
    folium.TileLayer('openstreetmap').add_to(map)
    
    map.options['minZoom'] = 3  # Definir um zoom mínimo para a área
    map.options['maxZoom'] = 5  # Limitar o zoom máximo

    for index, row in df.iterrows():
        lat_map = round(row['Latitude'], 2)
        lon_map = round(row['Longitude'], 2)
        popup_content = f"<strong>{row['Nome']}</strong><br><font size='1'>Latitude: {lat_map}<br>Longitude: {lon_map}</font>"
        folium.Marker([row['Latitude'], row['Longitude']], popup=popup_content).add_to(map)

    return map

# Obter o DataFrame cacheado
df = get_cached_data(fleet)
df_exibition = df_to_view(df)
m = map_creation(df_exibition)

# Exibição no Streamlit
st.title('Localização de Barcos')

col1, col2, col3 = st.columns([0.05, 1, 0.05])

with col2:
    # Exibição do mapa ao usuário
    st.write('Mapa de localização atual:')
    folium_static(m, width=1200, height=600)

    # Exibição de tabela ao usuário
    date_today = datetime.today().strftime('%d/%m/%Y')

    st.markdown('----')

    with st.container():
        st.write(f'<h3>Dados referentes a {date_today}:<h3>', unsafe_allow_html=True)
        st.markdown('----')
        
        col2_1, col2_2, col2_3, col2_4, col2_5, col2_6, col2_7 = st.columns([0.75, 2, 0.75, 1, 1, 0.85, 1.15])

        # Cabeçalhos das colunas
        with col2_1: st.markdown('MMSI')
        with col2_2: st.markdown('Nome')
        with col2_3: st.markdown('ID Equip.')
        with col2_4: st.markdown('Latitude')
        with col2_5: st.markdown('Longitude')
        with col2_6: st.markdown('Velocidade')
        with col2_7: st.markdown('Última Atualização')

        st.markdown('----')

        # Exibição dos dados em linhas
        for _, row in df_exibition.iterrows():
            col2_1, col2_2, col2_3, col2_4, col2_5, col2_6, col2_7 = st.columns([0.75, 1.5, 0.75, 0.75, 0.75, 0.75, 1])
            
            with col2_1: st.write(row['MMSI'])
            with col2_2: st.write(row['Nome'])
            with col2_3: st.write(row['ID Equipamento'])
            with col2_4: st.write(row['Latitude'])
            with col2_5: st.write(row['Longitude'])
            with col2_6: st.write(row['Velocidade'])
            with col2_7: st.write(row['Última Atualização'])

            st.markdown('----')
