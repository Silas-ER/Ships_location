import asyncio, requests, json, folium, os
import streamlit as st
import pandas as pd
from folium.plugins import BeautifyIcon, PolyLineTextPath
from streamlit_folium import folium_static
from datetime import datetime, timedelta, timezone 
from services.comum_services import read_file
from dotenv import load_dotenv

# Configuração de api
load_dotenv()
key = os.getenv('API_KEY')

# Configuração da página
st.set_page_config(layout="wide")

async def fetch_data(url):
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, requests.get, url)
    return json.loads(response.content.decode('utf-8'))

async def historic_points(date_init, date_final, MMSI):
    url = f'http://api.shipdt.com/DataApiServer/apicall/GetShipAllVesselTrack?k={key}&id={MMSI}&btm={date_init}&etm={date_final}'
    response_dict = await fetch_data(url)

    if response_dict.get('points') is not None:
        return pd.json_normalize(response_dict, record_path=['points'])
    return None

def formated_df(df):
    df['datetime'] = pd.to_datetime(df['utc'], unit='s')
    df.sort_values(by='datetime', inplace=True) 
    time_delta = timedelta(hours=6)

    filtered_df = df[df['datetime'].diff().dt.total_seconds().ge(time_delta.total_seconds()) | df['datetime'].isna()]

    filtered_df.loc[:, 'lat'] = filtered_df['lat'] / 1e6
    filtered_df.loc[:, 'lon'] = filtered_df['lon'] / 1e6
    filtered_df.loc[:, 'cog'] = filtered_df['cog'] / 100

    return filtered_df

def map_creation_consult(df):
    map = folium.Map(location=[-5.79448, -35.211], zoom_start=5)

    map.options['minZoom'] = 4  # Definir um zoom mínimo para a área
    map.options['maxZoom'] = 8  # Limitar o zoom máximo
    
    last_point = None
    for _, row in df.iterrows():
        current_point = (row['lat'], row['lon'])
        data = row['datetime'].strftime('%d/%m/%Y')      
        lat_map = round(row['lat'], 2)
        lon_map = round(row['lon'], 2)
        popup_content = f"<span>{data}</span><br><font size='1'>latitude: {lat_map} <br> longitude: {lon_map}</font>"

        folium.Marker(current_point, popup=popup_content).add_to(map)

        if last_point:
            line = folium.PolyLine([last_point, current_point], color="blue").add_to(map)
            PolyLineTextPath(line, '►', repeat=True, offset=10, attributes={'fill': 'blue', 'font-size': '18'}).add_to(map)

        last_point = current_point

    return map

st.title('Histórico de Movimentação')

current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, '../data/list_boats.txt')
boats, fleet = read_file(file_path)

col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1: date_init = st.date_input("Data Inicial:", value=None, format="DD/MM/YYYY", key='data_incial') 
with col2: date_final = st.date_input("Data Final:", value=None, format="DD/MM/YYYY", key='data_fim')
with col3: boat_entry = st.selectbox('Selecione o barco', options=boats)

with col4:    
    if date_init and date_final:
        st.metric(label='Dias Selecionados', value=(date_final - date_init).days)

if date_init and date_final and date_init != date_final:
    if date_init > date_final:
        st.error('Data final não pode ser menor que data inicial')
    else:
        date_init = datetime.combine(date_init, datetime.min.time()).replace(tzinfo=timezone.utc)
        date_final = datetime.combine(date_final, datetime.min.time()).replace(tzinfo=timezone.utc)

        date_init_unix = int(date_init.timestamp())
        date_final_unix = int(date_final.timestamp())
            
        boat_MMSI = fleet[boats.index(boat_entry)]

        df = asyncio.run(historic_points(date_init_unix, date_final_unix, boat_MMSI))
        
        if df is None:
            st.error('Não há dados para o período selecionado')
        else:
            df_exibition = formated_df(df)
                
            m = map_creation_consult(df_exibition)
                
            st.write(f'Histórico de movimentação do barco {boat_entry}')
            folium_static(m, width=1200, height=600)
            st.table(df_exibition)

else:
    st.error('Selecione um intervalo de datas válido')
