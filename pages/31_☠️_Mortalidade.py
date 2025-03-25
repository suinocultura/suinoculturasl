import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import uuid
import os
import sys

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import (
    load_animals,
    load_mortality_records,
    save_mortality_records,
    calculate_mortality_statistics,
    generate_mortality_report,
    calculate_age
,
    check_permission
)

st.set_page_config(
    page_title="Registro de Mortalidade",
    page_icon="⚠️",
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
if not check_permission(st.session_state.current_user, 'manage_health'):
    st.error("Você não tem permissão para acessar esta página.")
    st.stop()


st.title("Registro de Mortalidade ⚠️")
st.write("Registre e acompanhe a mortalidade do plantel.")

# Carregar dados
animals_df = load_animals()
mortality_df = load_mortality_records()

# Tabs para organização
tab1, tab2, tab3 = st.tabs(["Registrar Morte", "Análise de Mortalidade", "Relatórios"])

with tab1:
    st.header("Registrar Nova Morte")
    
    if not animals_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Seleção do animal
            selected_animal = st.selectbox(
                "Selecione o Animal",
                options=animals_df['id_animal'].tolist(),
                format_func=lambda x: f"{animals_df[animals_df['id_animal'] == x]['identificacao'].iloc[0]} - {animals_df[animals_df['id_animal'] == x]['categoria'].iloc[0]}"
            )
            
            if selected_animal:
                animal_info = animals_df[animals_df['id_animal'] == selected_animal].iloc[0]
                st.write(f"**Categoria:** {animal_info['categoria']}")
                
                if pd.notna(animal_info['data_nascimento']):
                    birth_date = pd.to_datetime(animal_info['data_nascimento']).date()
                    age_days = calculate_age(birth_date)
                    st.write(f"**Idade:** {age_days} dias ({age_days//30} meses)")
        
        with col2:
            with st.form("mortality_form"):
                # Data da morte
                data_morte = st.date_input(
                    "Data da Morte",
                    value=datetime.now().date()
                )
                
                # Causa da morte
                causa_morte = st.selectbox(
                    "Causa da Morte",
                    options=[
                        "Doença Respiratória",
                        "Doença Digestiva",
                        "Problemas Cardíacos",
                        "Problemas Reprodutivos",
                        "Acidentes",
                        "Eutanásia",
                        "Causas Desconhecidas",
                        "Outras Causas"
                    ]
                )
                
                # Local da morte
                local_morte = st.selectbox(
                    "Local da Morte",
                    options=[
                        "Maternidade",
                        "Creche",
                        "Gestação",
                        "Terminação",
                        "Quarentena",
                        "Outro"
                    ]
                )
                
                # Peso na morte
                peso_morte = st.number_input(
                    "Peso na Morte (kg)",
                    min_value=0.0,
                    value=0.0,
                    step=0.1
                )
                
                # Necropsia
                necropsia = st.radio(
                    "Realizou Necropsia?",
                    options=["Não", "Sim"]
                )
                
                if necropsia == "Sim":
                    resultado_necropsia = st.text_area(
                        "Resultado da Necropsia",
                        height=100
                    )
                else:
                    resultado_necropsia = ""
                
                # Medidas preventivas
                medidas_preventivas = st.text_area(
                    "Medidas Preventivas Adotadas",
                    height=100,
                    help="Descreva as medidas tomadas para prevenir casos similares"
                )
                
                # Responsável
                responsavel = st.text_input(
                    "Responsável pelo Registro"
                )
                
                # Observações
                observacao = st.text_area(
                    "Observações",
                    height=100
                )
                
                submitted = st.form_submit_button("Registrar Morte")
                
                if submitted:
                    if not responsavel:
                        st.error("Por favor, informe o responsável pelo registro.")
                    else:
                        # Calcular idade em dias
                        idade_dias = calculate_age(pd.to_datetime(animal_info['data_nascimento']).date())
                        
                        # Criar novo registro
                        new_record = {
                            'id_morte': str(uuid.uuid4()),
                            'id_animal': selected_animal,
                            'data_morte': data_morte.strftime('%Y-%m-%d'),
                            'causa_morte': causa_morte,
                            'categoria': animal_info['categoria'],
                            'idade_dias': idade_dias,
                            'peso_morte': peso_morte,
                            'local_morte': local_morte,
                            'necropsia': necropsia,
                            'resultado_necropsia': resultado_necropsia,
                            'medidas_preventivas': medidas_preventivas,
                            'responsavel': responsavel,
                            'observacao': observacao
                        }
                        
                        # Adicionar ao DataFrame
                        if mortality_df.empty:
                            mortality_df = pd.DataFrame([new_record])
                        else:
                            mortality_df = pd.concat([mortality_df, pd.DataFrame([new_record])], ignore_index=True)
                        
                        # Salvar dados
                        save_mortality_records(mortality_df)
                        
                        st.success("Morte registrada com sucesso!")
                        st.rerun()
    else:
        st.warning("Não há animais cadastrados. Cadastre animais primeiro.")

with tab2:
    st.header("Análise de Mortalidade")
    
    if not mortality_df.empty:
        # Filtros para análise
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        
        with col_filter1:
            start_date = st.date_input(
                "Data Inicial",
                value=(datetime.now() - timedelta(days=30)).date()
            )
        
        with col_filter2:
            end_date = st.date_input(
                "Data Final",
                value=datetime.now().date()
            )
        
        with col_filter3:
            filter_category = st.multiselect(
                "Filtrar por Categoria",
                options=sorted(mortality_df['categoria'].unique()),
                default=[]
            )
        
        # Calcular estatísticas
        filtered_df = mortality_df.copy()
        
        # Aplicar filtros
        filtered_df['data_morte'] = pd.to_datetime(filtered_df['data_morte'])
        filtered_df = filtered_df[
            (filtered_df['data_morte'].dt.date >= start_date) &
            (filtered_df['data_morte'].dt.date <= end_date)
        ]
        
        if filter_category:
            filtered_df = filtered_df[filtered_df['categoria'].isin(filter_category)]
        
        if not filtered_df.empty:
            # Métricas principais
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total de Mortes", len(filtered_df))
            
            with col2:
                avg_age = filtered_df['idade_dias'].mean()
                st.metric("Idade Média (dias)", f"{avg_age:.1f}")
            
            with col3:
                avg_weight = filtered_df['peso_morte'].mean()
                st.metric("Peso Médio (kg)", f"{avg_weight:.1f}")
            
            # Gráficos
            col1, col2 = st.columns(2)
            
            with col1:
                # Mortes por causa
                fig = px.pie(
                    filtered_df,
                    names='causa_morte',
                    title='Distribuição por Causa da Morte'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Mortes por local
                fig = px.pie(
                    filtered_df,
                    names='local_morte',
                    title='Distribuição por Local da Morte'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Evolução temporal
            st.subheader("Evolução da Mortalidade")
            
            deaths_by_date = filtered_df.groupby(
                filtered_df['data_morte'].dt.date
            ).size().reset_index(name='count')
            
            fig = px.line(
                deaths_by_date,
                x='data_morte',
                y='count',
                title='Mortes por Data',
                labels={'data_morte': 'Data', 'count': 'Número de Mortes'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabela detalhada
            st.subheader("Registros Detalhados")
            
            display_df = filtered_df[[
                'data_morte', 'categoria', 'causa_morte',
                'local_morte', 'idade_dias', 'peso_morte'
            ]].copy()
            
            display_df['data_morte'] = display_df['data_morte'].dt.strftime('%d/%m/%Y')
            
            display_df.columns = [
                'Data', 'Categoria', 'Causa',
                'Local', 'Idade (dias)', 'Peso (kg)'
            ]
            
            st.dataframe(
                display_df.sort_values('Data', ascending=False),
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("Nenhum dado encontrado para o período e filtros selecionados.")
    else:
        st.info("Não há registros de mortalidade. Utilize o formulário acima para registrar.")

with tab3:
    st.header("Relatórios de Mortalidade")
    
    if not mortality_df.empty:
        # Opções de relatório
        report_type = st.selectbox(
            "Tipo de Relatório",
            options=[
                "Relatório Geral",
                "Relatório por Categoria",
                "Relatório por Causa",
                "Relatório por Local"
            ]
        )
        
        # Período do relatório
        col1, col2 = st.columns(2)
        
        with col1:
            report_start = st.date_input(
                "Data Inicial do Relatório",
                value=(datetime.now() - timedelta(days=30)).date(),
                key="report_start"
            )
        
        with col2:
            report_end = st.date_input(
                "Data Final do Relatório",
                value=datetime.now().date(),
                key="report_end"
            )
        
        # Gerar relatório
        report_df = generate_mortality_report(mortality_df, animals_df, report_start, report_end)
        
        if not report_df.empty:
            # Estatísticas do período
            stats = calculate_mortality_statistics(report_df)
            
            st.subheader("Resumo do Período")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total de Mortes", stats['total_deaths'])
            
            with col2:
                st.metric("Idade Média", f"{stats['avg_age_death']:.1f} dias")
            
            with col3:
                st.metric("Principais Causas", 
                         list(stats['deaths_by_cause'].keys())[0] if stats['deaths_by_cause'] else "N/A")
            
            # Tabela detalhada baseada no tipo de relatório
            st.subheader("Detalhamento")
            
            if report_type == "Relatório Geral":
                display_df = report_df[[
                    'data_morte', 'identificacao', 'categoria',
                    'causa_morte', 'local_morte', 'idade_morte',
                    'peso_morte'
                ]].copy()
            
            elif report_type == "Relatório por Categoria":
                display_df = report_df.groupby('categoria').agg({
                    'id_morte': 'count',
                    'idade_morte': 'mean',
                    'peso_morte': 'mean'
                }).reset_index()
                
                display_df.columns = ['Categoria', 'Total de Mortes', 'Idade Média', 'Peso Médio']
            
            elif report_type == "Relatório por Causa":
                display_df = report_df.groupby('causa_morte').agg({
                    'id_morte': 'count',
                    'idade_morte': 'mean',
                    'peso_morte': 'mean'
                }).reset_index()
                
                display_df.columns = ['Causa', 'Total de Mortes', 'Idade Média', 'Peso Médio']
            
            else:  # Relatório por Local
                display_df = report_df.groupby('local_morte').agg({
                    'id_morte': 'count',
                    'idade_morte': 'mean',
                    'peso_morte': 'mean'
                }).reset_index()
                
                display_df.columns = ['Local', 'Total de Mortes', 'Idade Média', 'Peso Médio']
            
            # Formatar datas e números
            if 'data_morte' in display_df.columns:
                display_df['data_morte'] = pd.to_datetime(display_df['data_morte']).dt.strftime('%d/%m/%Y')
            
            for col in display_df.columns:
                if display_df[col].dtype in ['float64', 'int64']:
                    display_df[col] = display_df[col].round(2)
            
            st.dataframe(display_df, hide_index=True, use_container_width=True)
            
            # Exportar relatório
            if st.button("📥 Exportar Relatório"):
                csv = display_df.to_csv(index=False)
                st.download_button(
                    "📥 Baixar CSV",
                    data=csv,
                    file_name=f"relatorio_mortalidade_{report_start}_{report_end}.csv",
                    mime="text/csv"
                )
        else:
            st.info("Nenhum dado encontrado para o período selecionado.")
    else:
        st.info("Não há dados de mortalidade registrados no sistema.")
