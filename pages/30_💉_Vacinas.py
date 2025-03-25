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
    load_vaccination_records,
    save_vaccination_records,
    calculate_age
,
    check_permission
)

st.set_page_config(
    page_title="Controle de Vacinação",
    page_icon="💉",
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


st.title("Controle de Vacinação 💉")
st.write("Registre e acompanhe a vacinação dos animais.")

# Carregar dados
animals_df = load_animals()
vaccination_df = load_vaccination_records()

# Tabs para organização
tab1, tab2, tab3 = st.tabs(["Registrar Vacina", "Histórico de Vacinação", "Próximas Vacinas"])

with tab1:
    st.header("Registrar Nova Vacinação")
    
    if not animals_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Seleção do animal
            selected_animal = st.selectbox(
                "Selecione o Animal",
                options=animals_df['id_animal'].tolist(),
                format_func=lambda x: f"{animals_df[animals_df['id_animal'] == x]['identificacao'].iloc[0]} - {animals_df[animals_df['id_animal'] == x]['nome'].iloc[0]}" if animals_df[animals_df['id_animal'] == x]['nome'].iloc[0] else animals_df[animals_df['id_animal'] == x]['identificacao'].iloc[0]
            )
            
            # Mostrar informações do animal selecionado
            if selected_animal:
                animal_info = animals_df[animals_df['id_animal'] == selected_animal].iloc[0]
                st.write(f"**Categoria:** {animal_info['categoria']}")
                
                if 'data_nascimento' in animal_info and pd.notna(animal_info['data_nascimento']):
                    birth_date = pd.to_datetime(animal_info['data_nascimento']).date()
                    age_days = calculate_age(birth_date)
                    st.write(f"**Idade:** {age_days} dias ({age_days//30} meses)")
                
                # Mostrar última vacina, se existir
                if not vaccination_df.empty and selected_animal in vaccination_df['id_animal'].values:
                    last_vaccine = vaccination_df[vaccination_df['id_animal'] == selected_animal].sort_values('data_aplicacao', ascending=False).iloc[0]
                    st.write(f"**Última vacina:** {last_vaccine['nome_vacina']} em {last_vaccine['data_aplicacao']}")
        
        with col2:
            with st.form("vaccine_form"):
                # Data de aplicação
                data_aplicacao = st.date_input(
                    "Data da Aplicação",
                    value=datetime.now().date()
                )
                
                # Nome da vacina
                nome_vacina = st.text_input(
                    "Nome da Vacina",
                    help="Digite o nome ou tipo da vacina aplicada"
                )
                
                # Dose
                dose = st.selectbox(
                    "Dose",
                    options=["Única", "1ª Dose", "2ª Dose", "3ª Dose", "Reforço"]
                )
                
                # Lote
                lote = st.text_input(
                    "Lote da Vacina",
                    help="Número do lote da vacina"
                )
                
                # Data da próxima dose
                proxima_dose = st.date_input(
                    "Data da Próxima Dose (se necessário)",
                    value=(datetime.now() + timedelta(days=30)).date(),
                    help="Deixe a data atual se não houver próxima dose"
                )
                
                # Responsável
                responsavel = st.text_input(
                    "Responsável pela Aplicação",
                    help="Nome do veterinário ou técnico responsável"
                )
                
                # Observações
                observacao = st.text_area(
                    "Observações",
                    help="Anotações adicionais sobre a vacinação"
                )
                
                submitted = st.form_submit_button("Registrar Vacinação")
                
                if submitted:
                    if not nome_vacina:
                        st.error("Por favor, informe o nome da vacina.")
                    elif not responsavel:
                        st.error("Por favor, informe o responsável pela aplicação.")
                    else:
                        # Criar novo registro
                        new_vaccine = {
                            'id_vacinacao': str(uuid.uuid4()),
                            'id_animal': selected_animal,
                            'data_aplicacao': data_aplicacao.strftime('%Y-%m-%d'),
                            'nome_vacina': nome_vacina,
                            'dose': dose,
                            'lote': lote,
                            'proxima_dose': proxima_dose.strftime('%Y-%m-%d'),
                            'responsavel': responsavel,
                            'observacao': observacao
                        }
                        
                        # Adicionar ao DataFrame
                        if vaccination_df.empty:
                            vaccination_df = pd.DataFrame([new_vaccine])
                        else:
                            vaccination_df = pd.concat([vaccination_df, pd.DataFrame([new_vaccine])], ignore_index=True)
                        
                        # Salvar dados
                        save_vaccination_records(vaccination_df)
                        
                        st.success("Vacinação registrada com sucesso!")
                        st.rerun()
    else:
        st.warning("Não há animais cadastrados. Cadastre animais primeiro.")

with tab2:
    st.header("Histórico de Vacinação")
    
    if not vaccination_df.empty:
        # Filtros
        col_filter1, col_filter2 = st.columns([1, 2])
        
        with col_filter1:
            # Filtro por categoria
            merged_df = pd.merge(vaccination_df, animals_df, on='id_animal')
            filter_category = st.multiselect(
                "Filtrar por Categoria",
                options=sorted(animals_df['categoria'].unique()),
                default=[]
            )
        
        with col_filter2:
            # Filtro por animal
            filter_animal = st.multiselect(
                "Filtrar por Animal",
                options=animals_df['id_animal'].tolist(),
                format_func=lambda x: f"{animals_df[animals_df['id_animal'] == x]['identificacao'].iloc[0]} - {animals_df[animals_df['id_animal'] == x]['categoria'].iloc[0]}",
                default=[]
            )
        
        # Aplicar filtros
        filtered_df = merged_df.copy()
        
        if filter_category:
            filtered_df = filtered_df[filtered_df['categoria'].isin(filter_category)]
        
        if filter_animal:
            filtered_df = filtered_df[filtered_df['id_animal'].isin(filter_animal)]
        
        if not filtered_df.empty:
            # Tabela de histórico
            st.subheader("Registros de Vacinação")
            
            display_df = filtered_df[[
                'identificacao', 'categoria', 'data_aplicacao',
                'nome_vacina', 'dose', 'lote', 'responsavel'
            ]].copy()
            
            display_df['data_aplicacao'] = pd.to_datetime(display_df['data_aplicacao']).dt.strftime('%d/%m/%Y')
            
            display_df.columns = [
                'Identificação', 'Categoria', 'Data',
                'Vacina', 'Dose', 'Lote', 'Responsável'
            ]
            
            st.dataframe(
                display_df.sort_values('Data', ascending=False),
                hide_index=True,
                use_container_width=True
            )
            
            # Gráficos
            st.subheader("Análise de Vacinação")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Vacinas por categoria
                vaccines_by_category = filtered_df.groupby(['categoria', 'nome_vacina']).size().reset_index(name='count')
                fig = px.bar(
                    vaccines_by_category,
                    x='categoria',
                    y='count',
                    color='nome_vacina',
                    title='Vacinas Aplicadas por Categoria',
                    labels={
                        'categoria': 'Categoria',
                        'count': 'Quantidade',
                        'nome_vacina': 'Vacina'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Distribuição de doses
                doses_dist = filtered_df['dose'].value_counts()
                fig = px.pie(
                    values=doses_dist.values,
                    names=doses_dist.index,
                    title='Distribuição de Doses'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Evolução temporal
            st.subheader("Evolução da Vacinação")
            
            filtered_df['data_aplicacao'] = pd.to_datetime(filtered_df['data_aplicacao'])
            vaccines_over_time = filtered_df.groupby(['data_aplicacao', 'nome_vacina']).size().reset_index(name='count')
            
            fig = px.line(
                vaccines_over_time,
                x='data_aplicacao',
                y='count',
                color='nome_vacina',
                markers=True,
                title='Evolução da Vacinação ao Longo do Tempo',
                labels={
                    'data_aplicacao': 'Data',
                    'count': 'Quantidade',
                    'nome_vacina': 'Vacina'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Exportar dados
            if st.button("Exportar Dados"):
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    "Baixar CSV",
                    data=csv,
                    file_name="historico_vacinacao.csv",
                    mime="text/csv"
                )
        else:
            st.info("Nenhum dado encontrado com os filtros selecionados.")
    else:
        st.info("Não há registros de vacinação. Utilize o formulário acima para registrar.")

with tab3:
    st.header("Próximas Vacinas")
    
    if not vaccination_df.empty:
        # Filtrar vacinas futuras
        today = datetime.now().date()
        merged_df = pd.merge(vaccination_df, animals_df, on='id_animal')
        future_vaccines = merged_df[pd.to_datetime(merged_df['proxima_dose']).dt.date >= today].copy()
        
        if not future_vaccines.empty:
            # Ordenar por data
            future_vaccines = future_vaccines.sort_values('proxima_dose')
            
            # Calcular dias restantes
            future_vaccines['dias_restantes'] = (pd.to_datetime(future_vaccines['proxima_dose']).dt.date - today).dt.days
            
            # Preparar dados para exibição
            display_df = future_vaccines[[
                'identificacao', 'categoria', 'nome_vacina',
                'dose', 'proxima_dose', 'dias_restantes'
            ]].copy()
            
            display_df['proxima_dose'] = pd.to_datetime(display_df['proxima_dose']).dt.strftime('%d/%m/%Y')
            
            display_df.columns = [
                'Identificação', 'Categoria', 'Vacina',
                'Próxima Dose', 'Data Prevista', 'Dias Restantes'
            ]
            
            # Agrupar por período
            st.subheader("Próximos 7 dias")
            proxima_semana = display_df[display_df['Dias Restantes'] <= 7]
            if not proxima_semana.empty:
                st.dataframe(proxima_semana, hide_index=True, use_container_width=True)
            else:
                st.info("Não há vacinas previstas para os próximos 7 dias.")
            
            st.subheader("Próximos 30 dias")
            proximo_mes = display_df[(display_df['Dias Restantes'] > 7) & (display_df['Dias Restantes'] <= 30)]
            if not proximo_mes.empty:
                st.dataframe(proximo_mes, hide_index=True, use_container_width=True)
            else:
                st.info("Não há vacinas previstas para os próximos 30 dias.")
            
            st.subheader("Após 30 dias")
            futuro = display_df[display_df['Dias Restantes'] > 30]
            if not futuro.empty:
                st.dataframe(futuro, hide_index=True, use_container_width=True)
            else:
                st.info("Não há vacinas previstas para após 30 dias.")
            
            # Calendário visual
            st.subheader("Calendário de Vacinação")
            
            # Agrupar por data
            vaccines_by_date = future_vaccines.groupby('proxima_dose').size().reset_index(name='count')
            vaccines_by_date['proxima_dose'] = pd.to_datetime(vaccines_by_date['proxima_dose'])
            
            fig = px.bar(
                vaccines_by_date,
                x='proxima_dose',
                y='count',
                title='Distribuição de Vacinas Futuras',
                labels={
                    'proxima_dose': 'Data',
                    'count': 'Quantidade de Vacinas'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Não há vacinas programadas para o futuro.")
    else:
        st.info("Não há registros de vacinação no sistema.")
