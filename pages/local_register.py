import streamlit as st
from services.comum_services import writer, delete

with st.form(key='add_form'):
    st.markdown("CADASTRAR NOVO BARCO!", unsafe_allow_html=True) # Título do formulário
    col1, col2 = st.columns([1, 1])
    
    with col1: name = st.text_input("Nome")
    with col2:mmsi = st.text_input("MMSI")

    submit_button = st.form_submit_button("Adicionar") # Botão para submeter o formulário

if submit_button:
    writer(name, mmsi)

########################################################################################

with st.form(key='delete_form'):
    st.markdown("EXCLUIR BARCO!", unsafe_allow_html=True) # Título do formulário
    col1, col2 = st.columns([1, 1])
    
    with col1: name = st.text_input("Nome")
    with col2: mmsi = st.text_input("MMSI")

    submit_button = st.form_submit_button("Excluir") # Botão para submeter o formulário

if submit_button:
    delete(name, mmsi)