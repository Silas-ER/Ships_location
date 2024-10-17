import requests, json, folium, os
from folium.plugins import BeautifyIcon, PolyLineTextPath
import streamlit as st
import pandas as pd

from streamlit_folium import folium_static
from datetime import datetime, timedelta, timezone 
from services.comum_services import read_file
from dotenv import load_dotenv

load_dotenv()
key = os.getenv('API_KEY')

#Configuração da página
st.set_page_config(
    layout="wide",
)

def historic_points(date_init, date_final, MMSI):
    df = pd.DataFrame() #iniciando dataframe vazio
    url = f'http://api.shipdt.com/DataApiServer/apicall/GetShipAllVesselTrack?k={key}&id={MMSI}&btm={date_init}&etm={date_final}'
    response = requests.get(url).content
    response_dict = json.loads(response.decode('utf-8'))

    if response_dict.get('points') is not None:
        df = pd.json_normalize(response_dict, record_path=['points'])._append(df, ignore_index=True)
        return df
    else:
        return None

def formated_df(df):
    df['datetime'] = pd.to_datetime(df['utc'], unit='s')
    df.sort_values(by='datetime', inplace=True) 
    time_delta = timedelta(hours=6)
    filtered_df = pd.DataFrame()

    last_point_time = df.iloc[0]['datetime'] - time_delta

    for index, row in df.iterrows():
        if row['datetime'] - last_point_time >= time_delta:
            filtered_df = filtered_df._append(row)
            last_point_time = row['datetime']

    filtered_df['lat'] = filtered_df['lat'] / 1e6
    filtered_df['lon'] = filtered_df['lon'] / 1e6
    filtered_df['cog'] = filtered_df['cog'] / 100

    return filtered_df

def map_creation_consult(df):
    map = folium.Map(location=[-5.79448, -35.211], zoom_start=5)

    last_point = None

    for index, row in df.iterrows():

        current_point = (row['lat'], row['lon'])

        data = row['datetime'].strftime('%d/%m/%Y')      
        lat_map = round(row['lat'], 2)
        lon_map = round(row['lon'], 2)
        popup_content = f"<span>{data}</span><br><font size='1'>latitude: {lat_map} <br> longitude: {lon_map}</font>"

        folium.Marker([
            row['lat'], row['lon']], 
            popup=popup_content
        ).add_to(map)

        if last_point is not None:
            # Desenhar a linha entre o ponto anterior e o atual
            line = folium.PolyLine([last_point, current_point], color="blue").add_to(map)
            
            # Adicionar a seta na linha
            PolyLineTextPath(line, '►', repeat=True, offset=10, attributes={'fill': 'blue', 'font-size': '18'}).add_to(map)

        last_point = current_point

    return map

st.title('Histórico de Movimentação')

current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, '../data/list_boats.txt')
boats, fleet = read_file(file_path)

col1, col2, col3 , col4 = st.columns([1, 1, 1, 1])

with col1:
    date_init= st.date_input(
            "Data Inicial:", value=None,
            format="DD/MM/YYYY",
            key='data_incial',
            label_visibility="visible"
    )
        
with col2:    
    date_final= st.date_input(
            "Data Final:", value=None,
            format="DD/MM/YYYY",
            key='data_fim',
            label_visibility="visible"
    )

with col3:    
    boat_entry = st.selectbox('Selecione o barco', options=boats)

with col4:    
    if date_init is not None and date_final is not None:
        st.metric(label='Dias Selecionados', value=(date_final - date_init).days)

if date_init is not None and date_final is not None and date_init != date_final:
    if date_init > date_final:
        st.error('Data final não pode ser menor que data inicial')
    else:
        date_init = datetime.combine(date_init, datetime.min.time())
        date_final = datetime.combine(date_final, datetime.min.time())

        date_init_utc = date_init.replace(tzinfo=timezone.utc)
        date_final_utc = date_final.replace(tzinfo=timezone.utc)

        date_init_unix = int(date_init_utc.timestamp())
        date_final_unix = int(date_final_utc.timestamp())
            
        boat_MMSI = fleet[boats.index(boat_entry)]
            
        df = historic_points(date_init_unix, date_final_unix, boat_MMSI)
            
        if df is None:
            st.error('Não há dados para o período selecionado')

        else:
            df_exibition = formated_df(df)
                
            m = map_creation_consult(df_exibition)
                
            st.write(f'Histórico de movimentação do barco {boat_entry}')
            folium_static(m, width=1200, height=600)
            st.write(df_exibition)

else:
    st.error('Selecione um intervalo de datas válido')