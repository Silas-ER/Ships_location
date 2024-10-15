import requests
import asyncio
import aiohttp
import pandas as pd
import json
import os
import folium
from dotenv import load_dotenv
import streamlit as st
from streamlit_folium import folium_static

load_dotenv()
key = os.getenv('API_KEY')

# Configuração da página
st.set_page_config(layout="wide")

# Limitação de 10 requisições simultâneas
sem = asyncio.Semaphore(10)

# Funções de consulta
def api_consult(parameter):
    url = f'http://api.shipdt.com/DataApiServer/apicall/QueryShip?k={key}&kw={parameter}&max=100'
    response = requests.get(url).content
    response_dict = json.loads(response.decode('utf-8'))
    df = pd.json_normalize(response_dict, record_path=['data'])
    return df

def consult_filter(df):
    df = df[(df['shiptype'] == 0) | (df['shiptype'] == 30)]
    if df.empty:
        return df
    else:
        df_copy = df[['mmsi', 'name', 'lasttime']].copy()
        df_copy = df_copy.rename(columns={
            'mmsi': 'MMSI',
            'name': 'Nome',
            'lasttime': 'Última Atualização',
        })
        df_copy['Última Atualização'] = pd.to_datetime(df_copy['Última Atualização'], unit='s')
        df_copy['Última Atualização'] = df_copy['Última Atualização'].dt.strftime('%d/%m/%Y %H:%M:%S')
        df_copy['MMSI'] = df_copy['MMSI'].astype(str)
        return df_copy

async def fetch_data(session, MMSI):
    url_consult = f'http://api.shipdt.com/DataApiServer/apicall/GetSingleVesselShip?k={key}&id={MMSI}'
    async with sem:
        try:
            async with session.get(url_consult, timeout=10) as response:
                response.raise_for_status()
                response_dict = await response.json()
                return response_dict['data']
        except aiohttp.ClientError as e:
            st.error(f"Erro na consulta do MMSI {MMSI}: {e}")
            return {}

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

        if df_list:
            df = pd.concat(df_list, ignore_index=True)
            df['lat'] = df['lat'] / 1e6
            df['lon'] = df['lon'] / 1e6
            return df
        return pd.DataFrame()  # Retorna um DataFrame vazio se não houver dados

def map_creation(df):
    df = df.dropna(subset=['lat', 'lon'])
    map = folium.Map(location=[-5.79448, -35.211], zoom_start=3)
    
    map.options['minZoom'] = 3  # Definir um zoom mínimo para a área
    map.options['maxZoom'] = 5  # Limitar o zoom máximo
    
    folium.TileLayer('openstreetmap').add_to(map)

    for index, row in df.iterrows():
        lat_map = round(row['lat'], 2)
        lon_map = round(row['lon'], 2)
        popup_content = f"<strong>{row['name']}</strong><br><font size='1'>latitude: {lat_map} <br> longitude: {lon_map}</font>"
        
        folium.Marker(
            [row['lat'], row['lon']],
            popup=popup_content
        ).add_to(map)

    return map

# Definição da página
st.title('Consulta Geral de Barcos')

barcos_tosearch = st.text_input('Nome do Barco').upper()

if barcos_tosearch:
    col1, col2 = st.columns(2)
    
    result_consult = api_consult(barcos_tosearch)
    result_filter = consult_filter(result_consult)

    if result_filter.empty:
        st.error('Não há dados de pesca para o barco pesquisado')
    else:
        with col1:
            st.markdown(f'Barcos pesqueiros com o nome {barcos_tosearch}: <br>', unsafe_allow_html=True)
            st.table(result_filter)

        list_MMSI = result_filter['MMSI'].tolist()
        
        # Executando a consulta assíncrona e esperando o resultado
        df = asyncio.run(df_map_async(list_MMSI))

        if not df.empty:
            with col2:    
                st.markdown(f'Localização dos barcos com o nome {barcos_tosearch}: <br>', unsafe_allow_html=True)
                map = map_creation(df)
                folium_static(map)
        else:
            st.error('Não foram encontrados dados de localização para os barcos.')
else:
    st.warning('Digite o nome do barco para realizar a consulta')
