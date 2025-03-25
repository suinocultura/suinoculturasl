import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import base64
from io import BytesIO

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import (
    load_animals, 
    load_breeding_cycles, 
    load_gestation, 
    load_weight_records,
    export_data
,
    check_permission
)

st.set_page_config(
    page_title="Relatórios",
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
if not check_permission(st.session_state.current_user, 'view_reports'):
    st.error("Você não tem permissão para acessar esta página.")
    st.stop()


st.title("Relatórios 📊")
st.write("Visualize e exporte relatórios sobre seus animais.")

# Load existing data
animals_df = load_animals()
breeding_df = load_breeding_cycles()
gestation_df = load_gestation()
weight_df = load_weight_records()

# Tab for different reports
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Resumo Geral", 
    "Reprodução", 
    "Gestação", 
    "Crescimento",
    "Irmãs de Cio", 
    "Exportar Dados"
])

with tab1:
    st.header("Resumo Geral")
    
    # Basic statistics
    col1, col2, col3, col4 = st.columns(4)
    
    total_animals = len(animals_df) if not animals_df.empty else 0
    
    # Count animals by category
    categories = {}
    if not animals_df.empty and 'categoria' in animals_df.columns:
        categories = animals_df['categoria'].value_counts().to_dict()
    
    # Count active gestations
    active_gestations = 0
    if not gestation_df.empty and 'data_parto' in gestation_df.columns:
        active_gestations = len(gestation_df[gestation_df['data_parto'].isna()])
    
    # Count upcoming heat cycles
    upcoming_heats = 0
    if not breeding_df.empty and 'ultima_data' in breeding_df.columns:
        today = datetime.now().date()
        breeding_df['ultima_data'] = pd.to_datetime(breeding_df['ultima_data']).dt.date
        breeding_df['next_heat'] = breeding_df['ultima_data'] + pd.to_timedelta([21]*len(breeding_df), unit='d')
        upcoming_heats = len(breeding_df[
            (breeding_df['next_heat'] >= today) & 
            (breeding_df['next_heat'] <= today + timedelta(days=7))
        ])
    
    with col1:
        st.metric("Total de Animais", total_animals)
    
    with col2:
        matrices = categories.get("Matriz", 0)
        st.metric("Matrizes", matrices)
    
    with col3:
        st.metric("Gestações Ativas", active_gestations)
    
    with col4:
        st.metric("Cios nos Próximos 7 Dias", upcoming_heats)
    
    # Distribution charts
    if not animals_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Category distribution
            category_counts = animals_df['categoria'].value_counts().reset_index()
            category_counts.columns = ['Categoria', 'Contagem']
            
            fig = px.pie(
                category_counts,
                values='Contagem',
                names='Categoria',
                title='Distribuição por Categoria'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Sex distribution
            if 'sexo' in animals_df.columns:
                sex_counts = animals_df['sexo'].value_counts().reset_index()
                sex_counts.columns = ['Sexo', 'Contagem']
                
                fig = px.pie(
                    sex_counts,
                    values='Contagem',
                    names='Sexo',
                    title='Distribuição por Sexo'
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # Recent activities
    st.subheader("Atividades Recentes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Últimos Registros de Peso**")
        if not weight_df.empty:
            # Add animal identification
            display_weight = weight_df.copy()
            display_weight['identificacao'] = display_weight['id_animal'].apply(
                lambda x: animals_df[animals_df['id_animal'] == x]['identificacao'].iloc[0] if x in animals_df['id_animal'].values else "Desconhecido"
            )
            
            # Sort and display
            display_weight = display_weight.sort_values('data_registro', ascending=False).head(5)
            
            st.dataframe(
                display_weight[[
                    'identificacao', 'data_registro', 'peso'
                ]].rename(columns={
                    'identificacao': 'Animal',
                    'data_registro': 'Data',
                    'peso': 'Peso (kg)'
                }),
                use_container_width=True
            )
        else:
            st.info("Nenhum registro de peso encontrado.")
    
    with col2:
        st.write("**Últimos Registros de Reprodução**")
        if not breeding_df.empty:
            # Add animal identification
            display_breeding = breeding_df.copy()
            display_breeding['identificacao'] = display_breeding['id_animal'].apply(
                lambda x: animals_df[animals_df['id_animal'] == x]['identificacao'].iloc[0] if x in animals_df['id_animal'].values else "Desconhecido"
            )
            
            # Sort and display
            display_breeding = display_breeding.sort_values('ultima_data', ascending=False).head(5)
            
            st.dataframe(
                display_breeding[[
                    'identificacao', 'ultima_data', 'status'
                ]].rename(columns={
                    'identificacao': 'Animal',
                    'ultima_data': 'Data do Cio',
                    'status': 'Status'
                }),
                use_container_width=True
            )
        else:
            st.info("Nenhum registro de ciclo reprodutivo encontrado.")

with tab2:
    st.header("Relatório de Reprodução")
    
    if not breeding_df.empty:
        # Calculate breeding statistics
        breeding_counts = breeding_df['id_animal'].value_counts().reset_index()
        breeding_counts.columns = ['id_animal', 'contagem_ciclos']
        
        # Add animal data
        breeding_stats = pd.merge(breeding_counts, animals_df, on='id_animal', how='left')
        
        # Display statistics
        st.subheader("Estatísticas de Ciclos por Animal")
        
        stats_display = breeding_stats[[
            'identificacao', 'nome', 'categoria', 'contagem_ciclos'
        ]].rename(columns={
            'identificacao': 'Identificação',
            'nome': 'Nome',
            'categoria': 'Categoria',
            'contagem_ciclos': 'Total de Ciclos'
        }).sort_values('Total de Ciclos', ascending=False)
        
        st.dataframe(stats_display, use_container_width=True)
        
        # Heat cycle regularity analysis
        st.subheader("Análise de Regularidade de Cios")
        
        # Group by animal
        animal_cycles = {}
        
        for _, row in breeding_df.iterrows():
            animal_id = row['id_animal']
            date = pd.to_datetime(row['ultima_data'])
            
            if animal_id not in animal_cycles:
                animal_cycles[animal_id] = []
            
            animal_cycles[animal_id].append(date)
        
        # Calculate intervals for animals with multiple cycles
        intervals_data = []
        
        for animal_id, dates in animal_cycles.items():
            if len(dates) >= 2:
                # Sort dates
                dates.sort()
                
                # Calculate intervals
                intervals = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
                
                # Get animal info
                animal_info = animals_df[animals_df['id_animal'] == animal_id].iloc[0]
                
                intervals_data.append({
                    'id_animal': animal_id,
                    'identificacao': animal_info['identificacao'],
                    'nome': animal_info.get('nome', ''),
                    'num_ciclos': len(dates),
                    'intervalo_medio': sum(intervals) / len(intervals),
                    'intervalo_min': min(intervals),
                    'intervalo_max': max(intervals),
                    'regularidade': np.std(intervals) if len(intervals) > 1 else 0
                })
        
        if intervals_data:
            intervals_df = pd.DataFrame(intervals_data)
            
            # Display intervals data
            st.dataframe(
                intervals_df[[
                    'identificacao', 'nome', 'num_ciclos', 'intervalo_medio', 
                    'intervalo_min', 'intervalo_max', 'regularidade'
                ]].rename(columns={
                    'identificacao': 'Identificação',
                    'nome': 'Nome',
                    'num_ciclos': 'Nº de Ciclos',
                    'intervalo_medio': 'Intervalo Médio (dias)',
                    'intervalo_min': 'Intervalo Mínimo',
                    'intervalo_max': 'Intervalo Máximo',
                    'regularidade': 'Desvio Padrão'
                }).sort_values('Nº de Ciclos', ascending=False).style.format({
                    'Intervalo Médio (dias)': '{:.1f}',
                    'Desvio Padrão': '{:.1f}'
                }),
                use_container_width=True
            )
            
            # Interval visualization
            fig = px.scatter(
                intervals_df,
                x='num_ciclos',
                y='intervalo_medio',
                size='regularidade',
                hover_name='identificacao',
                labels={
                    'num_ciclos': 'Número de Ciclos',
                    'intervalo_medio': 'Intervalo Médio (dias)',
                    'regularidade': 'Variabilidade (Desvio Padrão)'
                },
                title='Regularidade de Ciclos por Animal'
            )
            
            # Add reference line for ideal cycle length (21 days)
            fig.add_hline(y=21, line_dash="dash", line_color="red", 
                         annotation_text="Ciclo Ideal (21 dias)", 
                         annotation_position="bottom right")
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Não há dados suficientes para análise de intervalos. Registre mais ciclos por animal.")
        
        # Upcoming heat prediction
        st.subheader("Previsão de Próximos Cios")
        
        # Get latest cycle for each animal
        latest_cycles = breeding_df.sort_values('ultima_data').groupby('id_animal').last().reset_index()
        
        # Calculate next heat date (21-day cycle)
        latest_cycles['ultima_data'] = pd.to_datetime(latest_cycles['ultima_data'])
        latest_cycles['proxima_data'] = latest_cycles['ultima_data'] + pd.to_timedelta([21]*len(latest_cycles), unit='d')
        
        # Add animal information
        latest_cycles = pd.merge(latest_cycles, animals_df[['id_animal', 'identificacao', 'nome']], on='id_animal', how='left')
        
        # Sort by upcoming date
        latest_cycles = latest_cycles.sort_values('proxima_data')
        
        # Display upcoming heats
        st.dataframe(
            latest_cycles[[
                'identificacao', 'nome', 'ultima_data', 'proxima_data'
            ]].rename(columns={
                'identificacao': 'Identificação',
                'nome': 'Nome',
                'ultima_data': 'Último Cio',
                'proxima_data': 'Próximo Cio Previsto'
            }),
            use_container_width=True
        )
        
        # Calendar view of upcoming heats
        st.subheader("Calendário de Cios")
        
        # Get current date and next 30 days
        today = datetime.now().date()
        next_month = today + timedelta(days=30)
        
        # Filter cycles in the next 30 days
        upcoming_cycles = latest_cycles[
            (latest_cycles['proxima_data'].dt.date >= today) & 
            (latest_cycles['proxima_data'].dt.date <= next_month)
        ]
        
        if not upcoming_cycles.empty:
            # Create figure
            fig = go.Figure()
            
            # Add events to calendar
            for _, row in upcoming_cycles.iterrows():
                animal_name = f"{row['identificacao']} - {row['nome']}" if row['nome'] else row['identificacao']
                date = row['proxima_data'].date()
                
                # Determine marker color based on days from now
                days_away = (date - today).days
                if days_away <= 3:
                    color = 'red'  # Imminent
                elif days_away <= 7:
                    color = 'orange'  # Soon
                else:
                    color = 'blue'  # Later
                
                fig.add_trace(go.Scatter(
                    x=[date],
                    y=[animal_name],
                    mode='markers',
                    marker=dict(size=15, color=color),
                    text=f"Data: {date}",
                    name=animal_name
                ))
            
            # Update layout
            fig.update_layout(
                title="Próximos Cios nos Próximos 30 Dias",
                xaxis_title="Data",
                yaxis_title="Animal",
                height=max(300, len(upcoming_cycles) * 30),
                margin=dict(l=120)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Não há cios previstos para os próximos 30 dias.")
    else:
        st.info("Nenhum registro de ciclo reprodutivo encontrado.")

with tab3:
    st.header("Relatório de Gestação")
    
    if not gestation_df.empty:
        # Add animal information
        gestation_with_animal = pd.merge(
            gestation_df, 
            animals_df[['id_animal', 'identificacao', 'nome']], 
            on='id_animal', 
            how='left'
        )
        
        # Active gestations
        st.subheader("Gestações Ativas")
        
        active_gestations = gestation_with_animal[gestation_with_animal['data_parto'].isna()]
        
        if not active_gestations.empty:
            # Calculate days in gestation
            today = datetime.now().date()
            active_gestations['data_cobertura'] = pd.to_datetime(active_gestations['data_cobertura']).dt.date
            active_gestations['data_prevista_parto'] = pd.to_datetime(active_gestations['data_prevista_parto']).dt.date
            
            active_gestations['dias_gestacao'] = active_gestations['data_cobertura'].apply(lambda x: (today - x).days)
            active_gestations['dias_restantes'] = active_gestations['data_prevista_parto'].apply(lambda x: max(0, (x - today).days))
            
            # Sort by due date
            active_gestations = active_gestations.sort_values('dias_restantes')
            
            # Display active gestations
            st.dataframe(
                active_gestations[[
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
            
            # Gestation timeline
            st.subheader("Linha do Tempo de Gestações")
            
            fig = px.timeline(
                active_gestations,
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
                title="Linha do Tempo de Gestações Ativas"
            )
            
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Não há gestações ativas no momento.")
        
        # Historical gestations
        st.subheader("Histórico de Partos")
        
        completed_gestations = gestation_with_animal[~gestation_with_animal['data_parto'].isna()]
        
        if not completed_gestations.empty:
            # Convert dates for calculations
            completed_gestations['data_cobertura'] = pd.to_datetime(completed_gestations['data_cobertura'])
            completed_gestations['data_parto'] = pd.to_datetime(completed_gestations['data_parto'])
            
            # Calculate gestation length
            completed_gestations['duracao_gestacao'] = (completed_gestations['data_parto'] - completed_gestations['data_cobertura']).dt.days
            
            # Sort by birth date
            completed_gestations = completed_gestations.sort_values('data_parto', ascending=False)
            
            # Display completed gestations
            st.dataframe(
                completed_gestations[[
                    'identificacao', 'nome', 'data_cobertura', 'data_parto', 
                    'duracao_gestacao', 'quantidade_leitoes'
                ]].rename(columns={
                    'identificacao': 'Identificação',
                    'nome': 'Nome',
                    'data_cobertura': 'Data da Cobertura',
                    'data_parto': 'Data do Parto',
                    'duracao_gestacao': 'Duração (dias)',
                    'quantidade_leitoes': 'Qtd. Leitões'
                }),
                use_container_width=True
            )
            
            # Statistics
            col1, col2 = st.columns(2)
            
            with col1:
                # Average litter size by animal
                avg_by_animal = completed_gestations.groupby(['identificacao', 'nome'])['quantidade_leitoes'].mean().reset_index()
                avg_by_animal.columns = ['Identificação', 'Nome', 'Média de Leitões']
                
                fig = px.bar(
                    avg_by_animal,
                    x='Identificação',
                    y='Média de Leitões',
                    hover_data=['Nome'],
                    title='Média de Leitões por Matriz'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Gestation duration analysis
                fig = px.histogram(
                    completed_gestations,
                    x='duracao_gestacao',
                    nbins=20,
                    labels={
                        'duracao_gestacao': 'Duração da Gestação (dias)',
                        'count': 'Frequência'
                    },
                    title='Distribuição da Duração de Gestação'
                )
                
                # Add vertical line at 114 days (typical gestation)
                fig.add_vline(x=114, line_dash="dash", line_color="red",
                             annotation_text="Padrão (114 dias)",
                             annotation_position="top right")
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Productivity over time
            st.subheader("Produtividade ao Longo do Tempo")
            
            # Group by month
            completed_gestations['month'] = completed_gestations['data_parto'].dt.to_period('M')
            monthly_births = completed_gestations.groupby('month').agg({
                'id_gestacao': 'count',
                'quantidade_leitoes': 'sum'
            }).reset_index()
            
            monthly_births['month'] = monthly_births['month'].astype(str)
            monthly_births.columns = ['Mês', 'Partos', 'Leitões']
            
            # Create figure with dual y-axis
            fig = go.Figure()
            
            # Add bars for litter count
            fig.add_trace(go.Bar(
                x=monthly_births['Mês'],
                y=monthly_births['Leitões'],
                name='Total de Leitões',
                marker_color='blue'
            ))
            
            # Add line for number of births
            fig.add_trace(go.Scatter(
                x=monthly_births['Mês'],
                y=monthly_births['Partos'],
                name='Número de Partos',
                marker_color='red',
                mode='lines+markers',
                yaxis='y2'
            ))
            
            # Update layout for dual y-axis
            fig.update_layout(
                title='Produção Mensal',
                xaxis_title='Mês',
                yaxis=dict(
                    title='Total de Leitões',
                    titlefont=dict(color='blue'),
                    tickfont=dict(color='blue')
                ),
                yaxis2=dict(
                    title='Número de Partos',
                    titlefont=dict(color='red'),
                    tickfont=dict(color='red'),
                    anchor='x',
                    overlaying='y',
                    side='right'
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
        else:
            st.info("Nenhum registro de parto encontrado.")
    else:
        st.info("Nenhum registro de gestação encontrado.")

with tab4:
    st.header("Relatório de Crescimento")
    
    if not weight_df.empty and not animals_df.empty:
        # Merge data
        growth_data = pd.merge(
            weight_df,
            animals_df[['id_animal', 'identificacao', 'nome', 'categoria', 'data_nascimento']],
            on='id_animal',
            how='left'
        )
        
        # Calculate age at weighing
        growth_data['data_registro'] = pd.to_datetime(growth_data['data_registro'])
        growth_data['data_nascimento'] = pd.to_datetime(growth_data['data_nascimento'])
        
        growth_data['idade_dias'] = (growth_data['data_registro'] - growth_data['data_nascimento']).dt.days
        
        # Filter out potentially erroneous data (negative ages)
        growth_data = growth_data[growth_data['idade_dias'] >= 0]
        
        if not growth_data.empty:
            # Weight by age analysis
            st.subheader("Análise de Peso por Idade")
            
            # Group by category and age group
            growth_data['idade_meses'] = (growth_data['idade_dias'] / 30).astype(int)
            
            # Allow category selection
            selected_categories = st.multiselect(
                "Selecionar Categorias",
                options=growth_data['categoria'].unique(),
                default=growth_data['categoria'].unique()
            )
            
            if selected_categories:
                filtered_data = growth_data[growth_data['categoria'].isin(selected_categories)]
                
                # Weight vs. Age scatter plot
                fig = px.scatter(
                    filtered_data,
                    x='idade_dias',
                    y='peso',
                    color='categoria',
                    hover_data=['identificacao', 'nome', 'data_registro'],
                    labels={
                        'idade_dias': 'Idade (dias)',
                        'peso': 'Peso (kg)',
                        'categoria': 'Categoria'
                    },
                    title='Relação Peso x Idade'
                )
                
                # Add trend lines for each category
                for category in selected_categories:
                    cat_data = filtered_data[filtered_data['categoria'] == category]
                    
                    if len(cat_data) >= 2:  # Need at least 2 points for a line
                        fig.add_trace(
                            px.scatter(
                                cat_data, x='idade_dias', y='peso', trendline='ols'
                            ).data[1]
                        )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Average weight by age group and category
                st.subheader("Peso Médio por Faixa Etária")
                
                avg_by_age = filtered_data.groupby(['categoria', 'idade_meses'])['peso'].mean().reset_index()
                
                fig = px.line(
                    avg_by_age,
                    x='idade_meses',
                    y='peso',
                    color='categoria',
                    markers=True,
                    labels={
                        'idade_meses': 'Idade (meses)',
                        'peso': 'Peso Médio (kg)',
                        'categoria': 'Categoria'
                    },
                    title='Curva de Crescimento por Categoria'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Growth rate analysis
                st.subheader("Análise de Taxa de Crescimento")
                
                # Calculate weight gain for animals with multiple records
                animal_growth = []
                
                for animal_id in filtered_data['id_animal'].unique():
                    animal_records = filtered_data[filtered_data['id_animal'] == animal_id].sort_values('data_registro')
                    
                    if len(animal_records) >= 2:
                        for i in range(len(animal_records) - 1):
                            current = animal_records.iloc[i]
                            next_record = animal_records.iloc[i + 1]
                            
                            days_diff = (next_record['data_registro'] - current['data_registro']).days
                            
                            if days_diff > 0:
                                weight_diff = next_record['peso'] - current['peso']
                                daily_gain = weight_diff / days_diff
                                
                                animal_growth.append({
                                    'id_animal': animal_id,
                                    'identificacao': current['identificacao'],
                                    'categoria': current['categoria'],
                                    'idade_inicial': current['idade_dias'],
                                    'idade_final': next_record['idade_dias'],
                                    'peso_inicial': current['peso'],
                                    'peso_final': next_record['peso'],
                                    'periodo_dias': days_diff,
                                    'ganho_diario': daily_gain
                                })
                
                if animal_growth:
                    growth_df = pd.DataFrame(animal_growth)
                    
                    # Growth rate by age group
                    growth_df['faixa_idade'] = pd.cut(
                        growth_df['idade_inicial'],
                        bins=[0, 30, 60, 90, 180, 365, float('inf')],
                        labels=['0-1 mês', '1-2 meses', '2-3 meses', '3-6 meses', '6-12 meses', '12+ meses']
                    )
                    
                    # Average daily gain by age group and category
                    gain_by_age = growth_df.groupby(['categoria', 'faixa_idade'])['ganho_diario'].mean().reset_index()
                    
                    fig = px.bar(
                        gain_by_age,
                        x='faixa_idade',
                        y='ganho_diario',
                        color='categoria',
                        barmode='group',
                        labels={
                            'faixa_idade': 'Faixa Etária',
                            'ganho_diario': 'Ganho Médio Diário (kg/dia)',
                            'categoria': 'Categoria'
                        },
                        title='Ganho Médio Diário por Faixa Etária'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Growth efficiency (gain per initial weight)
                    growth_df['eficiencia'] = growth_df['ganho_diario'] / growth_df['peso_inicial'] * 100
                    
                    # Average efficiency by age group and category
                    efficiency_by_age = growth_df.groupby(['categoria', 'faixa_idade'])['eficiencia'].mean().reset_index()
                    
                    fig = px.bar(
                        efficiency_by_age,
                        x='faixa_idade',
                        y='eficiencia',
                        color='categoria',
                        barmode='group',
                        labels={
                            'faixa_idade': 'Faixa Etária',
                            'eficiencia': 'Eficiência de Crescimento (%)',
                            'categoria': 'Categoria'
                        },
                        title='Eficiência de Crescimento por Faixa Etária (Ganho Diário / Peso Inicial)'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Não há dados suficientes para análise de taxa de crescimento. Registre mais medições por animal.")
            else:
                st.warning("Selecione pelo menos uma categoria para visualizar os dados.")
        else:
            st.info("Não há dados válidos de idade para análise.")
    else:
        st.info("Dados insuficientes para análise. Registre animais e pesos primeiro.")

with tab5:
    st.header("Análise de Irmãs de Cio")
    
    if not breeding_df.empty and 'irmas_cio' in breeding_df.columns:
        st.subheader("Grupos de Irmãs de Cio")
        
        # Identificar ciclos com irmãs registradas
        ciclos_com_irmas = breeding_df[breeding_df['irmas_cio'].notna() & (breeding_df['irmas_cio'] != "")]
        
        if not ciclos_com_irmas.empty:
            # Adicionar informações dos animais 
            ciclos_com_irmas = pd.merge(
                ciclos_com_irmas,
                animals_df[['id_animal', 'identificacao', 'nome', 'irmas_ninhada']],
                on='id_animal',
                how='left'
            )
            
            # Agrupar irmãs de cio por data
            ciclos_com_irmas['data_cio'] = pd.to_datetime(ciclos_com_irmas['data_cio']).dt.date
            
            # Mostrar dados agrupados por data
            st.subheader("Ocorrências de Cios em Grupo")
            
            # Ordenar por data
            ciclos_com_irmas = ciclos_com_irmas.sort_values('data_cio', ascending=False)
            
            data_agrupada = ciclos_com_irmas.groupby('data_cio').agg({
                'id_animal': 'count',
                'intensidade_cio': lambda x: ', '.join(x),
                'quantidade_irmas_cio': 'sum'
            }).reset_index()
            
            data_agrupada.columns = ['Data do Cio', 'Número de Animais', 'Intensidades', 'Total de Irmãs']
            
            st.dataframe(data_agrupada, use_container_width=True)
            
            # Mostrar detalhes por data
            selected_date = st.selectbox(
                "Selecione uma data para ver detalhes:",
                options=sorted(ciclos_com_irmas['data_cio'].unique(), reverse=True),
                format_func=lambda x: x.strftime('%d/%m/%Y')
            )
            
            if selected_date:
                st.write(f"### Detalhes dos Cios em {selected_date.strftime('%d/%m/%Y')}")
                
                ciclos_na_data = ciclos_com_irmas[ciclos_com_irmas['data_cio'] == selected_date]
                
                for _, ciclo in ciclos_na_data.iterrows():
                    animal_name = f"{ciclo['identificacao']} - {ciclo['nome']}" if ciclo['nome'] else ciclo['identificacao']
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Animal:** {animal_name}")
                        st.write(f"**Intensidade:** {ciclo['intensidade_cio']}")
                        st.write(f"**Status:** {ciclo['status']}")
                    
                    with col2:
                        st.write(f"**Irmãs de Ninhada:** {ciclo['irmas_ninhada'] if pd.notna(ciclo['irmas_ninhada']) else 'Nenhuma'}")
                        st.write(f"**Quantidade de Irmãs de Cio:** {ciclo['quantidade_irmas_cio']}")
                        
                        # Mostrar IDs das irmãs de cio
                        irmas_ids = ciclo['irmas_cio'].split(',') if pd.notna(ciclo['irmas_cio']) else []
                        if irmas_ids:
                            irmas_nomes = []
                            for irma_id in irmas_ids:
                                if irma_id in animals_df['id_animal'].values:
                                    irma = animals_df[animals_df['id_animal'] == irma_id].iloc[0]
                                    irmas_nomes.append(f"{irma['identificacao']} - {irma['nome']}" if irma['nome'] else irma['identificacao'])
                            
                            if irmas_nomes:
                                st.write(f"**Irmãs identificadas no cio:** {', '.join(irmas_nomes)}")
                    
                    st.markdown("---")
            
            # Visualização de Irmãs de Cio ao Longo do Tempo
            st.subheader("Irmãs de Cio ao Longo do Tempo")
            
            # Preparar dados para gráfico
            heat_group_size = ciclos_com_irmas.groupby('data_cio').size().reset_index()
            heat_group_size.columns = ['Data', 'Tamanho do Grupo']
            
            fig = px.line(
                heat_group_size,
                x='Data',
                y='Tamanho do Grupo',
                markers=True,
                title='Tamanho dos Grupos de Cio ao Longo do Tempo'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Análise de correlação entre irmãs de ninhada e irmãs de cio
            st.subheader("Correlação entre Irmãs de Ninhada e Irmãs de Cio")
            
            # Verificar animais que são irmãs de ninhada e entraram em cio juntas
            correlacoes = []
            
            for _, ciclo in ciclos_com_irmas.iterrows():
                # Pular se não tiver irmãs de ninhada registradas
                if not pd.notna(ciclo['irmas_ninhada']) or ciclo['irmas_ninhada'] == "":
                    continue
                    
                # Comparar irmãs de ninhada com irmãs de cio
                irmas_ninhada = ciclo['irmas_ninhada'].split(',')
                irmas_cio = ciclo['irmas_cio'].split(',') if pd.notna(ciclo['irmas_cio']) else []
                
                # Contar quantas irmãs de ninhada estão entre as irmãs de cio
                irmas_comuns = set(irmas_ninhada).intersection(set(irmas_cio))
                
                correlacoes.append({
                    'id_animal': ciclo['id_animal'],
                    'identificacao': ciclo['identificacao'],
                    'data_cio': ciclo['data_cio'],
                    'total_irmas_ninhada': len(irmas_ninhada),
                    'total_irmas_cio': len(irmas_cio),
                    'irmas_comuns': len(irmas_comuns),
                    'porcentagem': len(irmas_comuns) / len(irmas_ninhada) * 100 if irmas_ninhada else 0
                })
            
            if correlacoes:
                correlacoes_df = pd.DataFrame(correlacoes)
                
                fig = px.scatter(
                    correlacoes_df,
                    x='total_irmas_ninhada',
                    y='irmas_comuns',
                    size='porcentagem',
                    hover_name='identificacao',
                    hover_data=['data_cio', 'porcentagem'],
                    labels={
                        'total_irmas_ninhada': 'Total de Irmãs de Ninhada',
                        'irmas_comuns': 'Irmãs de Ninhada em Cio Simultâneo',
                        'porcentagem': '% de Irmãs de Ninhada em Cio'
                    },
                    title='Correlação entre Irmãs de Ninhada e Cios Simultâneos'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Estatísticas resumidas
                media_porcentagem = correlacoes_df['porcentagem'].mean()
                
                st.metric(
                    "Média de Sincronização de Cio entre Irmãs", 
                    f"{media_porcentagem:.1f}%",
                    help="Porcentagem média de irmãs de ninhada que entram em cio simultaneamente"
                )
            else:
                st.info("Não há dados suficientes para análise de correlação entre irmãs de ninhada e irmãs de cio.")
        else:
            st.info("Não foram encontrados registros de ciclos com irmãs de cio.")
    else:
        st.info("Não há dados de irmãs de cio registrados no sistema ou o formato dos dados não é compatível com esta análise.")
        
with tab6:
    st.header("Exportar Dados")
    
    # Select data to export
    export_data_type = st.selectbox(
        "Selecione o Tipo de Dados para Exportar",
        options=["Animais", "Ciclos Reprodutivos", "Gestações", "Registros de Peso"]
    )
    
    export_format = st.selectbox(
        "Formato de Exportação",
        options=["CSV", "Excel", "JSON"]
    )
    
    # Get data to export
    data_to_export = None
    filename = ""
    
    if export_data_type == "Animais":
        data_to_export = animals_df
        filename = "animais"
    elif export_data_type == "Ciclos Reprodutivos":
        data_to_export = breeding_df
        filename = "ciclos_reprodutivos"
    elif export_data_type == "Gestações":
        data_to_export = gestation_df
        filename = "gestacoes"
    elif export_data_type == "Registros de Peso":
        data_to_export = weight_df
        filename = "registros_peso"
    
    # Preview data
    if data_to_export is not None and not data_to_export.empty:
        st.subheader("Prévia dos Dados")
        st.dataframe(data_to_export.head(10), use_container_width=True)
        
        # Export button
        if st.button("Exportar Dados"):
            format_map = {"CSV": "csv", "Excel": "excel", "JSON": "json"}
            format_type = format_map[export_format].lower()
            
            exported_data = export_data(data_to_export, format_type)
            
            file_extension = "csv" if format_type in ["csv", "excel"] else "json"
            
            # Create download link
            b64 = base64.b64encode(exported_data.encode()).decode()
            href = f'<a href="data:file/{file_extension};base64,{b64}" download="{filename}.{file_extension}">Clique aqui para baixar o arquivo</a>'
            st.markdown(href, unsafe_allow_html=True)
            
            st.success(f"Dados exportados com sucesso!")
    else:
        st.info(f"Não há dados de {export_data_type.lower()} para exportar.")
