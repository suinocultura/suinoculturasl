import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import uuid
import os
import sys

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import (
    load_animals,
    load_heat_detection,
    save_heat_detection,
    load_heat_records,
    save_heat_records,
    calculate_heat_interval,
    predict_next_heat,
    generate_heat_report
,
    check_permission
)

st.set_page_config(
    page_title="Sistema de Rufia",
    page_icon="🔍",
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


st.title("Sistema de Rufia 🔍")
st.write("Gerenciamento de rufiões e detecção de cio")

# Carregar dados
animals_df = load_animals()
heat_detection_df = load_heat_detection()
heat_records_df = load_heat_records()

# Tabs para organização
tab1, tab2, tab3 = st.tabs(["Registro de Rufiões", "Detecção de Cio", "Análise e Relatórios"])

with tab1:
    st.header("Cadastro e Gestão de Rufiões")
    
    # Formulário de cadastro
    with st.form("rufiao_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Seleção do animal
            available_animals = animals_df[
                (animals_df['categoria'] == 'Rufião') & 
                (~animals_df['id_animal'].isin(heat_detection_df['id_animal']))
            ] if not animals_df.empty and not heat_detection_df.empty else animals_df
            
            selected_animal = st.selectbox(
                "Selecione o Animal",
                options=available_animals['id_animal'].tolist() if not available_animals.empty else [],
                format_func=lambda x: f"{available_animals[available_animals['id_animal'] == x]['identificacao'].iloc[0]}"
            )
            
            nome_rufiao = st.text_input(
                "Nome do Rufião",
                help="Nome ou identificação específica para este rufião"
            )
        
        with col2:
            data_inicio = st.date_input(
                "Data de Início",
                value=datetime.now().date()
            )
            
            status = st.selectbox(
                "Status",
                options=["Ativo", "Inativo"]
            )
            
            observacao = st.text_area(
                "Observações",
                help="Anotações adicionais sobre o rufião"
            )
        
        submitted = st.form_submit_button("Registrar Rufião")
        
        if submitted and selected_animal:
            # Criar novo registro
            new_rufiao = {
                'id_rufia': str(uuid.uuid4()),
                'id_animal': selected_animal,
                'nome': nome_rufiao,
                'status': status,
                'data_inicio': data_inicio.strftime('%Y-%m-%d'),
                'data_fim': None if status == "Ativo" else datetime.now().strftime('%Y-%m-%d'),
                'observacao': observacao
            }
            
            # Adicionar ao DataFrame
            if heat_detection_df.empty:
                heat_detection_df = pd.DataFrame([new_rufiao])
            else:
                heat_detection_df = pd.concat([heat_detection_df, pd.DataFrame([new_rufiao])], ignore_index=True)
            
            # Salvar dados
            save_heat_detection(heat_detection_df)
            
            st.success("Rufião registrado com sucesso!")
            st.rerun()
    
    # Lista de rufiões ativos
    if not heat_detection_df.empty:
        st.subheader("Rufiões Cadastrados")
        
        # Merge com dados dos animais
        rufioes_df = pd.merge(
            heat_detection_df,
            animals_df[['id_animal', 'identificacao', 'data_nascimento']],
            on='id_animal',
            how='left'
        )
        
        # Preparar dados para exibição
        display_df = rufioes_df[[
            'identificacao', 'nome', 'status',
            'data_inicio', 'data_fim'
        ]].copy()
        
        # Formatar datas
        display_df['data_inicio'] = pd.to_datetime(display_df['data_inicio']).dt.strftime('%d/%m/%Y')
        display_df['data_fim'] = pd.to_datetime(display_df['data_fim']).dt.strftime('%d/%m/%Y')
        
        display_df.columns = [
            'Identificação', 'Nome', 'Status',
            'Início', 'Término'
        ]
        
        st.dataframe(
            display_df,
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("Não há rufiões cadastrados no sistema.")

with tab2:
    st.header("Registro de Detecção de Cio")
    
    if not heat_detection_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Seleção do rufião
            rufioes_ativos = heat_detection_df[heat_detection_df['status'] == 'Ativo']
            
            if not rufioes_ativos.empty:
                selected_rufiao = st.selectbox(
                    "Selecione o Rufião",
                    options=rufioes_ativos['id_rufia'].tolist(),
                    format_func=lambda x: rufioes_ativos[rufioes_ativos['id_rufia'] == x]['nome'].iloc[0]
                )
                
                # Seleção da matriz
                matrizes = animals_df[animals_df['categoria'].isin(['Matriz', 'Leitoa'])]
                
                if not matrizes.empty:
                    selected_matriz = st.selectbox(
                        "Selecione a Matriz",
                        options=matrizes['id_animal'].tolist(),
                        format_func=lambda x: f"{matrizes[matrizes['id_animal'] == x]['identificacao'].iloc[0]} - {matrizes[matrizes['id_animal'] == x]['categoria'].iloc[0]}"
                    )
                    
                    # Mostrar histórico de cios da matriz selecionada
                    if selected_matriz:
                        st.subheader("Histórico da Matriz")
                        
                        matriz_records = heat_records_df[
                            heat_records_df['id_matriz'] == selected_matriz
                        ].sort_values('data_deteccao', ascending=False)
                        
                        if not matriz_records.empty:
                            last_heat = matriz_records.iloc[0]
                            st.write(f"**Último cio:** {pd.to_datetime(last_heat['data_deteccao']).strftime('%d/%m/%Y')}")
                            
                            # Calcular próximo cio previsto
                            prediction = predict_next_heat(selected_matriz, heat_records_df)
                            if prediction:
                                st.write(f"**Próximo cio previsto:** {prediction['predicted_next']} (Confiança: {prediction['confidence']})")
                        else:
                            st.info("Sem registros anteriores de cio.")
                else:
                    st.warning("Não há matrizes cadastradas no sistema.")
            else:
                st.warning("Não há rufiões ativos no sistema.")
        
        with col2:
            with st.form("heat_detection_form"):
                # Data e hora da detecção
                data_deteccao = st.date_input(
                    "Data da Detecção",
                    value=datetime.now().date()
                )
                
                hora_deteccao = st.time_input(
                    "Hora da Detecção",
                    value=datetime.now().time()
                )
                
                # Intensidade e comportamento
                intensidade = st.select_slider(
                    "Intensidade do Cio",
                    options=["Fraco", "Médio", "Forte"]
                )
                
                comportamento = st.multiselect(
                    "Comportamento Observado",
                    options=["Reflexo de Imobilidade", "Monta", "Aceitação da Monta", "Vulva Inchada", "Inquietação"],
                    default=[]
                )
                
                duracao = st.number_input(
                    "Duração (minutos)",
                    min_value=0,
                    value=10,
                    step=1
                )
                
                sinais = st.multiselect(
                    "Sinais Externos",
                    options=["Vermelhidão", "Inchaço", "Descarga", "Nenhum"],
                    default=["Nenhum"]
                )
                
                confirmado = st.checkbox("Cio Confirmado")
                
                responsavel = st.text_input(
                    "Responsável pela Detecção"
                )
                
                observacao = st.text_area(
                    "Observações"
                )
                
                submitted = st.form_submit_button("Registrar Detecção")
                
                if submitted:
                    if not responsavel:
                        st.error("Por favor, informe o responsável pela detecção.")
                    else:
                        # Criar novo registro
                        new_record = {
                            'id_registro': str(uuid.uuid4()),
                            'id_rufia': selected_rufiao,
                            'id_matriz': selected_matriz,
                            'data_deteccao': data_deteccao.strftime('%Y-%m-%d'),
                            'hora_deteccao': hora_deteccao.strftime('%H:%M'),
                            'intensidade_cio': intensidade,
                            'comportamento': ", ".join(comportamento),
                            'duracao_minutos': duracao,
                            'sinais_externos': ", ".join(sinais),
                            'confirmado': confirmado,
                            'responsavel': responsavel,
                            'observacao': observacao
                        }
                        
                        # Adicionar ao DataFrame
                        if heat_records_df.empty:
                            heat_records_df = pd.DataFrame([new_record])
                        else:
                            heat_records_df = pd.concat([heat_records_df, pd.DataFrame([new_record])], ignore_index=True)
                        
                        # Salvar dados
                        save_heat_records(heat_records_df)
                        
                        st.success("Detecção de cio registrada com sucesso!")
                        st.rerun()
    else:
        st.warning("Cadastre um rufião primeiro para registrar detecções de cio.")

with tab3:
    st.header("Análise e Relatórios")
    
    if not heat_records_df.empty:
        # Filtros
        col_filter1, col_filter2 = st.columns(2)
        
        with col_filter1:
            start_date = st.date_input(
                "Data Inicial",
                value=(datetime.now() - timedelta(days=30)).date(),
                key="report_start"
            )
        
        with col_filter2:
            end_date = st.date_input(
                "Data Final",
                value=datetime.now().date(),
                key="report_end"
            )
        
        # Gerar relatório
        report_df = generate_heat_report(heat_records_df, animals_df, start_date, end_date)
        
        if not report_df.empty:
            # Métricas principais
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_detections = len(report_df)
                st.metric("Total de Detecções", total_detections)
            
            with col2:
                confirmed = len(report_df[report_df['confirmado'] == True])
                st.metric("Cios Confirmados", confirmed)
            
            with col3:
                confirmation_rate = (confirmed / total_detections * 100) if total_detections > 0 else 0
                st.metric("Taxa de Confirmação", f"{confirmation_rate:.1f}%")
            
            # Gráficos
            st.subheader("Análise de Detecções")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Detecções por intensidade
                intensity_counts = report_df['intensidade_cio'].value_counts()
                fig = px.pie(
                    values=intensity_counts.values,
                    names=intensity_counts.index,
                    title='Distribuição por Intensidade de Cio'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Evolução temporal
                report_df['data_deteccao'] = pd.to_datetime(report_df['data_deteccao'])
                detections_by_date = report_df.groupby('data_deteccao').size().reset_index(name='count')
                
                fig = px.line(
                    detections_by_date,
                    x='data_deteccao',
                    y='count',
                    title='Detecções por Data',
                    labels={'data_deteccao': 'Data', 'count': 'Número de Detecções'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Tabela detalhada
            st.subheader("Registros Detalhados")
            
            display_df = report_df[[
                'identificacao', 'data_deteccao', 'hora_deteccao',
                'intensidade_cio', 'confirmado', 'responsavel'
            ]].copy()
            
            display_df['data_deteccao'] = pd.to_datetime(display_df['data_deteccao']).dt.strftime('%d/%m/%Y')
            
            display_df.columns = [
                'Matriz', 'Data', 'Hora',
                'Intensidade', 'Confirmado', 'Responsável'
            ]
            
            st.dataframe(
                display_df.sort_values('Data', ascending=False),
                hide_index=True,
                use_container_width=True
            )
            
            # Exportar relatório
            if st.button("📥 Exportar Relatório"):
                csv = display_df.to_csv(index=False)
                st.download_button(
                    "📥 Baixar CSV",
                    data=csv,
                    file_name=f"relatorio_rufia_{start_date}_{end_date}.csv",
                    mime="text/csv"
                )
        else:
            st.info("Nenhum dado encontrado para o período selecionado.")
    else:
        st.info("Não há registros de detecção de cio no sistema.")
