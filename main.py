import streamlit as st

#páginas de mapas
api_map = st.Page("pages/api_map.py", title="Mapa Atual", icon="🗺️", default=True)

api_historic = st.Page("pages/api_historic.py", title="Histórico de Movimentação", icon="🧭")

#Cadastro de novos barcos para o mapa principal
cadastrar_novo_barco =  st.Page("pages/local_register.py", title="Add novo barco ao mapa", icon="🗂️")

#Buscar informações de barcos com base no seu nome
api_consult = st.Page("pages/api_consult.py", title="Consultar Embarcações", icon="🔍")

pg = st.navigation(
    {
        "Mapas": [api_map, api_historic],
        "Cadastro": [cadastrar_novo_barco],
        "Consulta Geral:": [api_consult],
    }
)

pg.run()
