import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import uuid
import os
import sys
import plotly.express as px
import plotly.graph_objects as go

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import load_animals, load_gestation, save_gestation, calculate_gestation_details, check_permission

st.set_page_config(
    page_title="Gestação",
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


st.title("Gestação 🐷")
st.write("Registre e acompanhe as gestações dos animais.")

# Load existing data
animals_df = load_animals()
gestation_df = load_gestation()

# Filter only female animals
female_animals = animals_df[animals_df['sexo'] == 'Fêmea'] if not animals_df.empty else pd.DataFrame()
female_ids = female_animals['id_animal'].tolist() if not female_animals.empty else []

# Tab for data entry and visualization
tab1, tab2 = st.tabs(["Registrar Gestação", "Acompanhar Gestações"])

with tab1:
    st.header("Registrar Nova Gestação")
    
    if not female_animals.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            selected_animal = st.selectbox(
                "Selecione a Matriz",
                options=female_animals['id_animal'].tolist(),
                format_func=lambda x: f"{female_animals[female_animals['id_animal'] == x]['identificacao'].iloc[0]} - {female_animals[female_animals['id_animal'] == x]['nome'].iloc[0]}" if female_animals[female_animals['id_animal'] == x]['nome'].iloc[0] else female_animals[female_animals['id_animal'] == x]['identificacao'].iloc[0]
            )
            
            data_cobertura = st.date_input(
                "Data da Cobertura/Inseminação",
                value=datetime.now().date()
            )
            
            # Calculate expected delivery date (114 days gestation period for pigs)
            data_prevista = data_cobertura + timedelta(days=114)
            st.write(f"**Data Prevista para o Parto:** {data_prevista.strftime('%d/%m/%Y')}")
            
        with col2:
            status = st.selectbox(
                "Status da Gestação",
                options=["Confirmada", "Suspeita", "Em Observação"]
            )
            
            observacao = st.text_area("Observações")
        
        # Submit button
        if st.button("Registrar Gestação"):
            # Check if animal already has an active gestation
            active_gestation = False
            if not gestation_df.empty and selected_animal in gestation_df['id_animal'].values:
                animal_gestations = gestation_df[gestation_df['id_animal'] == selected_animal]
                active_gestation = any(pd.isna(row['data_parto']) for _, row in animal_gestations.iterrows())
            
            if active_gestation:
                st.error("Este animal já possui uma gestação ativa. Finalize a gestação atual antes de registrar uma nova.")
            else:
                # Create new gestation record
                new_gestation = {
                    'id_gestacao': str(uuid.uuid4()),
                    'id_animal': selected_animal,
                    'data_cobertura': data_cobertura.strftime('%Y-%m-%d'),
                    'data_prevista_parto': data_prevista.strftime('%Y-%m-%d'),
                    'data_parto': None,
                    'quantidade_leitoes': None,
                    'status': status,
                    'observacao': observacao
                }
                
                # Add to DataFrame
                if gestation_df.empty:
                    gestation_df = pd.DataFrame([new_gestation])
                else:
                    gestation_df = pd.concat([gestation_df, pd.DataFrame([new_gestation])], ignore_index=True)
                
                # Save updated DataFrame
                save_gestation(gestation_df)
                
                st.success(f"Gestação registrada com sucesso!")
                st.rerun()
    else:
        st.warning("Não há fêmeas cadastradas no sistema. Cadastre animais primeiro.")

with tab2:
    st.header("Gestações Ativas")
    
    if not gestation_df.empty:
        # Filter active gestations (where data_parto is NaN)
        active_gestations = gestation_df[gestation_df['data_parto'].isna()]
        
        if not active_gestations.empty:
            # Add animal identification to display
            display_df = active_gestations.copy()
            display_df['identificacao'] = display_df['id_animal'].apply(
                lambda x: animals_df[animals_df['id_animal'] == x]['identificacao'].iloc[0] if x in animals_df['id_animal'].values else "Desconhecido"
            )
            display_df['nome'] = display_df['id_animal'].apply(
                lambda x: animals_df[animals_df['id_animal'] == x]['nome'].iloc[0] if x in animals_df['id_animal'].values else ""
            )
            
            # Calculate days elapsed and remaining
            today = datetime.now().date()
            display_df['data_cobertura'] = pd.to_datetime(display_df['data_cobertura']).dt.date
            display_df['data_prevista_parto'] = pd.to_datetime(display_df['data_prevista_parto']).dt.date
            
            display_df['dias_gestacao'] = display_df['data_cobertura'].apply(lambda x: (today - x).days)
            display_df['dias_restantes'] = display_df['data_prevista_parto'].apply(lambda x: (x - today).days)
            
            # Sort by days remaining
            display_df = display_df.sort_values('dias_restantes')
            
            st.dataframe(
                display_df[[
                    'identificacao', 'nome', 'data_cobertura', 'data_prevista_parto', 
                    'dias_gestacao', 'dias_restantes', 'status'
                ]].rename(columns={
                    'identificacao': 'Identificação',
                    'nome': 'Nome',
                    'data_cobertura': 'Data da Cobertura',
                    'data_prevista_parto': 'Data Prevista do Parto',
                    'dias_gestacao': 'Dias de Gestação',
                    'dias_restantes': 'Dias Restantes',
                    'status': 'Status'
                }),
                use_container_width=True
            )
            
            # Visualizations
            st.subheader("Cronograma de Partos")
            
            # Timeline of upcoming births
            fig = px.timeline(
                display_df,
                x_start='data_cobertura',
                x_end='data_prevista_parto',
                y='identificacao',
                color='status',
                hover_data=['nome', 'dias_gestacao', 'dias_restantes'],
                labels={
                    'identificacao': 'Animal',
                    'data_cobertura': 'Período de Gestação',
                    'data_prevista_parto': '',
                    'status': 'Status'
                },
                title="Linha do Tempo de Gestações"
            )
            
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)
            
            # Detailed gestation tracking
            st.subheader("Acompanhamento Detalhado")
            
            selected_gestation = st.selectbox(
                "Selecione uma gestação para acompanhar:",
                options=display_df['id_gestacao'].tolist(),
                format_func=lambda x: f"{display_df[display_df['id_gestacao'] == x]['identificacao'].iloc[0]} - {display_df[display_df['id_gestacao'] == x]['nome'].iloc[0]}"
            )
            
            if selected_gestation:
                selected_data = display_df[display_df['id_gestacao'] == selected_gestation].iloc[0]
                gestation_id = selected_data['id_gestacao']
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Animal:** {selected_data['identificacao']} - {selected_data['nome']}")
                    st.write(f"**Data da Cobertura:** {selected_data['data_cobertura']}")
                    st.write(f"**Data Prevista do Parto:** {selected_data['data_prevista_parto']}")
                    st.write(f"**Status:** {selected_data['status']}")
                
                with col2:
                    st.write(f"**Dias de Gestação:** {selected_data['dias_gestacao']}")
                    st.write(f"**Dias Restantes:** {selected_data['dias_restantes']}")
                    st.write(f"**Progresso:** {min(100, int((selected_data['dias_gestacao'] / 114) * 100))}%")
                    st.write(f"**Observações:** {selected_data.get('observacao', '')}")
                
                # Progress bar
                progress = min(100, int((selected_data['dias_gestacao'] / 114) * 100))
                st.progress(progress / 100)
                
                # Gestation stages visualization
                st.subheader("Estágios da Gestação")
                
                fig = go.Figure()
                
                # Define gestation stages
                stages = [
                    {"name": "Implantação", "start": 0, "end": 14, "color": "lightblue"},
                    {"name": "Desenvolvimento Fetal 1", "start": 14, "end": 35, "color": "lightgreen"},
                    {"name": "Desenvolvimento Fetal 2", "start": 35, "end": 70, "color": "yellow"},
                    {"name": "Preparação para o Parto", "start": 70, "end": 114, "color": "orange"}
                ]
                
                # Add stages to timeline
                for stage in stages:
                    fig.add_trace(go.Bar(
                        x=[stage["end"] - stage["start"]],
                        y=["Estágios"],
                        orientation='h',
                        name=stage["name"],
                        marker=dict(color=stage["color"]),
                        hoverinfo="name",
                        showlegend=True,
                        base=stage["start"]
                    ))
                
                # Add current day marker
                fig.add_trace(go.Scatter(
                    x=[selected_data['dias_gestacao']],
                    y=["Estágios"],
                    mode="markers",
                    marker=dict(size=15, color="red", symbol="line-ns"),
                    name="Dia Atual",
                    hoverinfo="name"
                ))
                
                # Update layout
                fig.update_layout(
                    barmode='stack',
                    height=150,
                    margin=dict(l=0, r=0, t=30, b=0),
                    xaxis=dict(
                        title="Dias de Gestação",
                        range=[0, 114]
                    ),
                    yaxis=dict(
                        showticklabels=False
                    ),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Register birth
                st.subheader("Registrar Parto")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    data_parto = st.date_input(
                        "Data do Parto",
                        value=datetime.now().date()
                    )
                
                with col2:
                    qtd_leitoes = st.number_input("Quantidade de Leitões", min_value=0, value=0)
                    observacoes_parto = st.text_area("Observações do Parto", value="", key="obs_parto")
                
                if st.button("Registrar Parto", type="primary"):
                    # Update gestation in DataFrame
                    gestation_df.loc[gestation_df['id_gestacao'] == gestation_id, 'data_parto'] = data_parto.strftime('%Y-%m-%d')
                    gestation_df.loc[gestation_df['id_gestacao'] == gestation_id, 'quantidade_leitoes'] = qtd_leitoes
                    gestation_df.loc[gestation_df['id_gestacao'] == gestation_id, 'observacao'] = observacoes_parto
                    
                    # Save updated DataFrame
                    save_gestation(gestation_df)
                    
                    st.success(f"Parto registrado com sucesso!")
                    st.rerun()
        else:
            st.info("Não há gestações ativas no momento.")
    else:
        st.info("Nenhuma gestação registrada. Adicione novos registros na aba 'Registrar Gestação'.")
    
    # Historical gestations
    st.header("Histórico de Partos")
    
    if not gestation_df.empty:
        # Filter completed gestations (where data_parto is not NaN)
        completed_gestations = gestation_df[~gestation_df['data_parto'].isna()]
        
        if not completed_gestations.empty:
            # Add animal identification to display
            display_completed_df = completed_gestations.copy()
            display_completed_df['identificacao'] = display_completed_df['id_animal'].apply(
                lambda x: animals_df[animals_df['id_animal'] == x]['identificacao'].iloc[0] if x in animals_df['id_animal'].values else "Desconhecido"
            )
            
            # Sort by parto date
            display_completed_df = display_completed_df.sort_values('data_parto', ascending=False)
            
            st.dataframe(
                display_completed_df[[
                    'identificacao', 'data_cobertura', 'data_parto', 'quantidade_leitoes'
                ]].rename(columns={
                    'identificacao': 'Identificação',
                    'data_cobertura': 'Data da Cobertura',
                    'data_parto': 'Data do Parto',
                    'quantidade_leitoes': 'Qtd. Leitões'
                }),
                use_container_width=True
            )
            
            # Visualizations
            if 'quantidade_leitoes' in display_completed_df.columns:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Average litter size by animal
                    avg_by_animal = display_completed_df.groupby('identificacao')['quantidade_leitoes'].mean().reset_index()
                    avg_by_animal.columns = ['Animal', 'Média de Leitões']
                    
                    fig = px.bar(
                        avg_by_animal,
                        x='Animal',
                        y='Média de Leitões',
                        title='Média de Leitões por Matriz'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Total litter count over time
                    display_completed_df['data_parto'] = pd.to_datetime(display_completed_df['data_parto'])
                    display_completed_df['month'] = display_completed_df['data_parto'].dt.to_period('M')
                    monthly_count = display_completed_df.groupby('month')['quantidade_leitoes'].sum().reset_index()
                    monthly_count['month'] = monthly_count['month'].astype(str)
                    
                    fig = px.line(
                        monthly_count,
                        x='month',
                        y='quantidade_leitoes',
                        title='Total de Leitões por Mês',
                        labels={'month': 'Mês', 'quantidade_leitoes': 'Quantidade de Leitões'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Não há histórico de partos registrados.")
    else:
        st.info("Nenhuma gestação registrada. Adicione novos registros na aba 'Registrar Gestação'.")
