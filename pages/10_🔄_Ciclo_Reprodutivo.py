import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import uuid
import os
import sys
import plotly.express as px

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import load_animals, load_breeding_cycles, save_breeding_cycles, predict_heat_date, check_permission

st.set_page_config(
    page_title="Ciclo Reprodutivo",
    page_icon="🐷",
    layout="wide"
)

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# Verificar se o usuário está autenticado
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Você precisa estar autenticado para acessar esta página.")
    st.stop()

# Verificar se o usuário tem permissão para acessar esta página
if not check_permission(st.session_state.current_user, 'manage_reproduction'):
    st.error("Você não tem permissão para acessar esta página.")
    st.stop()


st.title("Ciclo Reprodutivo 🐷")
st.write("Gerencie os ciclos reprodutivos e cios dos animais.")

# Load existing data
animals_df = load_animals()
breeding_df = load_breeding_cycles()

# Filter only female animals for breeding
female_animals = animals_df[animals_df['sexo'] == 'Fêmea'] if not animals_df.empty else pd.DataFrame()
female_ids = female_animals['id_animal'].tolist() if not female_animals.empty else []

# Tab for data entry and visualization
tab1, tab2 = st.tabs(["Registrar Ciclo", "Visualizar Ciclos"])

with tab1:
    st.header("Registrar Ciclo Reprodutivo")
    
    if not female_animals.empty:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_animal = st.selectbox(
                "Selecione a Fêmea",
                options=female_animals['id_animal'].tolist(),
                format_func=lambda x: f"{female_animals[female_animals['id_animal'] == x]['identificacao'].iloc[0]} - {female_animals[female_animals['id_animal'] == x]['nome'].iloc[0]}" if female_animals[female_animals['id_animal'] == x]['nome'].iloc[0] else female_animals[female_animals['id_animal'] == x]['identificacao'].iloc[0]
            )
            
            # Get existing cycle count for this animal
            if not breeding_df.empty and selected_animal in breeding_df['id_animal'].values:
                existing_cycles = breeding_df[breeding_df['id_animal'] == selected_animal]
                cycle_number = existing_cycles['numero_ciclo'].max() + 1 if 'numero_ciclo' in existing_cycles.columns else 1
            else:
                cycle_number = 1
                
            cycle_num = st.number_input("Número do Ciclo", min_value=1, value=int(cycle_number))
            
            date_cio = st.date_input(
                "Data do Cio",
                value=datetime.now().date()
            )
            
        with col2:
            intensidade_cio = st.select_slider(
                "Intensidade do Cio",
                options=["Fraco", "Moderado", "Forte", "Muito Forte"]
            )
            
            status = st.selectbox(
                "Status",
                options=["Detectado", "Inseminado", "Não Inseminado", "Irregular"]
            )
            
            # Opção para selecionar fêmeas que estão com cio simultaneamente
            st.subheader("Irmãs de Cio")
            st.write("Selecione outras fêmeas que estão em cio junto com esta:")
            
        with col3:
            # Mostrar lista de checkboxes com outras fêmeas
            other_females = female_animals[female_animals['id_animal'] != selected_animal]
            irmas_cio_dict = {}
            
            if not other_females.empty:
                for _, female in other_females.iterrows():
                    female_id = female['id_animal']
                    female_name = f"{female['identificacao']} - {female['nome']}" if female['nome'] else female['identificacao']
                    irmas_cio_dict[female_id] = st.checkbox(female_name, key=f"irma_{female_id}")
            
            quantidade_irmas = st.number_input("Quantidade de Irmãs de Cio", min_value=0, value=0)
            observacao = st.text_area("Observações")
        
        # Submit button
        if st.button("Registrar Ciclo"):
            # Create list of sister animals in heat
            irmas_selecionadas = [female_id for female_id, selected in irmas_cio_dict.items() if selected]
            irmas_cio_str = ','.join(irmas_selecionadas) if irmas_selecionadas else ""
            
            # Create new cycle record
            new_cycle = {
                'id_ciclo': str(uuid.uuid4()),
                'id_animal': selected_animal,
                'numero_ciclo': cycle_num,
                'data_cio': date_cio.strftime('%Y-%m-%d'),
                'intensidade_cio': intensidade_cio,
                'irmas_cio': irmas_cio_str,
                'quantidade_irmas_cio': quantidade_irmas,
                'status': status,
                'observacao': observacao
            }
            
            # Add to DataFrame
            if breeding_df.empty:
                breeding_df = pd.DataFrame([new_cycle])
            else:
                breeding_df = pd.concat([breeding_df, pd.DataFrame([new_cycle])], ignore_index=True)
            
            # Save updated DataFrame
            save_breeding_cycles(breeding_df)
            
            st.success(f"Ciclo reprodutivo registrado com sucesso!")
            st.rerun()
    else:
        st.warning("Não há fêmeas cadastradas no sistema. Cadastre animais primeiro.")

with tab2:
    st.header("Ciclos Reprodutivos")
    
    # Filter options
    filter_col1, filter_col2 = st.columns([1, 2])
    
    with filter_col1:
        filter_status = st.multiselect(
            "Filtrar por Status",
            options=["Detectado", "Inseminado", "Não Inseminado", "Irregular"],
            default=[]
        )
    
    with filter_col2:
        filter_animal = st.multiselect(
            "Filtrar por Animal",
            options=female_ids,
            format_func=lambda x: f"{animals_df[animals_df['id_animal'] == x]['identificacao'].iloc[0]} - {animals_df[animals_df['id_animal'] == x]['nome'].iloc[0]}" if animals_df[animals_df['id_animal'] == x]['nome'].iloc[0] else animals_df[animals_df['id_animal'] == x]['identificacao'].iloc[0],
            default=[]
        )
    
    # Apply filters
    filtered_df = breeding_df.copy() if not breeding_df.empty else pd.DataFrame()
    
    if not filtered_df.empty:
        if filter_status:
            filtered_df = filtered_df[filtered_df['status'].isin(filter_status)]
            
        if filter_animal:
            filtered_df = filtered_df[filtered_df['id_animal'].isin(filter_animal)]
    
    # Display data
    if not filtered_df.empty:
        # Add animal identification to display
        display_df = filtered_df.copy()
        display_df['identificacao'] = display_df['id_animal'].apply(
            lambda x: animals_df[animals_df['id_animal'] == x]['identificacao'].iloc[0] if x in animals_df['id_animal'].values else "Desconhecido"
        )
        display_df['proxima_data'] = pd.to_datetime(display_df['data_cio']) + pd.to_timedelta([21]*len(display_df), unit='d')
        
        st.dataframe(
            display_df[[
                'identificacao', 'numero_ciclo', 'data_cio', 'intensidade_cio', 'quantidade_irmas_cio', 'proxima_data', 'status'
            ]].rename(columns={
                'identificacao': 'Identificação',
                'numero_ciclo': 'Ciclo Nº',
                'data_cio': 'Data do Cio',
                'intensidade_cio': 'Intensidade',
                'quantidade_irmas_cio': 'Qtd. Irmãs Cio', 
                'proxima_data': 'Próximo Cio Previsto',
                'status': 'Status'
            }),
            use_container_width=True
        )
        
        # Visualizations
        st.subheader("Análise de Ciclos Reprodutivos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Status distribution
            status_counts = display_df['status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Contagem']
            
            fig = px.pie(
                status_counts, 
                values='Contagem', 
                names='Status',
                title='Distribuição de Status dos Ciclos'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Upcoming heat periods
            display_df['proxima_data'] = pd.to_datetime(display_df['proxima_data'])
            upcoming_df = display_df.sort_values('proxima_data').head(10)
            
            fig = px.bar(
                upcoming_df,
                x='identificacao',
                y=[(upcoming_df['proxima_data'][i] - pd.Timestamp.now()).days for i in upcoming_df.index],
                labels={'x': 'Animal', 'y': 'Dias até o Próximo Cio'},
                title='Próximos Cios Previstos'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Animal details
        st.subheader("Detalhes do Ciclo")
        selected_cycle_id = st.selectbox(
            "Selecione um ciclo para ver detalhes:",
            options=filtered_df['id_ciclo'].tolist(),
            format_func=lambda x: f"{display_df[display_df['id_ciclo'] == x]['identificacao'].iloc[0]} - Ciclo {display_df[display_df['id_ciclo'] == x]['numero_ciclo'].iloc[0]}"
        )
        
        if selected_cycle_id:
            selected_cycle = filtered_df[filtered_df['id_ciclo'] == selected_cycle_id].iloc[0]
            cycle_id = selected_cycle['id_ciclo']
            
            col1, col2 = st.columns(2)
            
            animal_id = selected_cycle['id_animal']
            animal_info = animals_df[animals_df['id_animal'] == animal_id].iloc[0]
            
            with col1:
                st.write(f"**Animal:** {animal_info['identificacao']} - {animal_info['nome']}")
                st.write(f"**Número do Ciclo:** {selected_cycle['numero_ciclo']}")
                st.write(f"**Data do Cio:** {selected_cycle.get('data_cio', selected_cycle.get('ultima_data', 'N/A'))}")
                st.write(f"**Intensidade do Cio:** {selected_cycle.get('intensidade_cio', 'N/A')}")
                
            with col2:
                st.write(f"**Status:** {selected_cycle['status']}")
                st.write(f"**Próximo Cio Previsto:** {predict_heat_date(selected_cycle.get('data_cio', selected_cycle.get('ultima_data'))).strftime('%Y-%m-%d')}")
                st.write(f"**Qtd. Irmãs de Cio:** {selected_cycle.get('quantidade_irmas_cio', 0)}")
                st.write(f"**Observações:** {selected_cycle.get('observacao', '')}")
            
            # Edit cycle
            st.subheader("Editar Ciclo")
            
            edit_col1, edit_col2 = st.columns(2)
            
            with edit_col1:
                new_cycle_num = st.number_input("Número do Ciclo", value=int(selected_cycle['numero_ciclo']), key="edit_cycle_num")
                date_field = 'data_cio' if 'data_cio' in selected_cycle else 'ultima_data'
                new_date = st.date_input("Data do Cio", value=pd.to_datetime(selected_cycle[date_field]).date(), key="edit_date")
                new_intensidade = st.select_slider(
                    "Intensidade do Cio",
                    options=["Fraco", "Moderado", "Forte", "Muito Forte"],
                    value=selected_cycle.get('intensidade_cio', "Moderado"),
                    key="edit_intensidade"
                )
                
            with edit_col2:
                new_status = st.selectbox(
                    "Status",
                    options=["Detectado", "Inseminado", "Não Inseminado", "Irregular"],
                    index=["Detectado", "Inseminado", "Não Inseminado", "Irregular"].index(selected_cycle['status']),
                    key="edit_status"
                )
                new_qtd_irmas = st.number_input(
                    "Quantidade de Irmãs de Cio",
                    min_value=0,
                    value=int(selected_cycle.get('quantidade_irmas_cio', 0)),
                    key="edit_qtd_irmas"
                )
                new_observacao = st.text_area("Observações", value=selected_cycle.get('observacao', ''), key="edit_obs")
            
            if st.button("Atualizar Ciclo"):
                # Update cycle in DataFrame
                breeding_df.loc[breeding_df['id_ciclo'] == cycle_id, 'numero_ciclo'] = new_cycle_num
                
                # Update with proper field name based on what's available
                if 'data_cio' in breeding_df.columns:
                    breeding_df.loc[breeding_df['id_ciclo'] == cycle_id, 'data_cio'] = new_date.strftime('%Y-%m-%d')
                else:
                    breeding_df.loc[breeding_df['id_ciclo'] == cycle_id, 'ultima_data'] = new_date.strftime('%Y-%m-%d')
                
                # Update new fields if they exist in the DataFrame
                if 'intensidade_cio' in breeding_df.columns:
                    breeding_df.loc[breeding_df['id_ciclo'] == cycle_id, 'intensidade_cio'] = new_intensidade
                if 'quantidade_irmas_cio' in breeding_df.columns:
                    breeding_df.loc[breeding_df['id_ciclo'] == cycle_id, 'quantidade_irmas_cio'] = new_qtd_irmas
                    
                breeding_df.loc[breeding_df['id_ciclo'] == cycle_id, 'status'] = new_status
                breeding_df.loc[breeding_df['id_ciclo'] == cycle_id, 'observacao'] = new_observacao
                
                # Save updated DataFrame
                save_breeding_cycles(breeding_df)
                
                st.success(f"Ciclo atualizado com sucesso!")
                st.rerun()
            
            # Delete cycle
            if st.button("Excluir Ciclo", type="primary", use_container_width=True):
                # Remove cycle from DataFrame
                breeding_df = breeding_df[breeding_df['id_ciclo'] != cycle_id]
                
                # Save updated DataFrame
                save_breeding_cycles(breeding_df)
                
                st.success(f"Ciclo excluído com sucesso!")
                st.rerun()
    else:
        st.info("Nenhum ciclo reprodutivo registrado. Adicione novos registros na aba 'Registrar Ciclo'.")
