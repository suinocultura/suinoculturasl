import streamlit as st
import pandas as pd
import uuid
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
from utils import (
    load_animals,
    load_gilts,
    save_gilts,
    load_gilts_selection,
    save_gilts_selection,
    load_gilts_discard,
    save_gilts_discard,
    calculate_age,
    get_available_gilts,
    get_discarded_gilts,
    calculate_gilts_statistics
,
    check_permission
)

# Configuração da página
st.set_page_config(
    page_title="Seleção de Leitoas - Sistema de Gestão de Suinocultura",
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
if not check_permission(st.session_state.current_user, 'manage_growth'):
    st.error("Você não tem permissão para acessar esta página.")
    st.stop()


# Carregar dados
animals_df = load_animals()
gilts_df = load_gilts()
gilts_selection_df = load_gilts_selection()
gilts_discard_df = load_gilts_discard()

# Título da página
st.title("Seleção de Leitoas 🐖")
st.markdown("""
Sistema de cadastro, seleção e descarte de leitoas para reprodução. 
Registre dados como brinco, tatuagem, chip e características para seleção.
""")

# Abas para diferentes funcionalidades
tab1, tab2, tab3, tab4 = st.tabs(["Visão Geral", "Cadastro de Leitoas", "Avaliação e Seleção", "Descarte"])

with tab1:
    st.header("Visão Geral de Leitoas")
    
    # Estatísticas
    stats = calculate_gilts_statistics(gilts_df, gilts_selection_df, gilts_discard_df)
    
    # Mostrar métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Leitoas", stats['total_gilts'])
        
    with col2:
        # Contar leitoas por status
        selecionadas = stats['gilts_by_status'].get('Selecionada', 0)
        st.metric("Leitoas Selecionadas", selecionadas)
        
    with col3:
        # Taxa de seleção
        st.metric("Taxa de Seleção", f"{stats['selection_rate']:.1f}%")
        
    with col4:
        # Contar leitoas descartadas
        descartadas = stats['gilts_by_status'].get('Descartada', 0)
        st.metric("Leitoas Descartadas", descartadas)
    
    # Gráficos e análises
    if not gilts_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de status
            if 'status' in gilts_df.columns:
                status_counts = gilts_df['status'].value_counts().reset_index()
                status_counts.columns = ['Status', 'Contagem']
                
                fig = px.pie(
                    status_counts,
                    values='Contagem',
                    names='Status',
                    title='Distribuição de Leitoas por Status',
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Gráfico de motivos de descarte
            if not gilts_discard_df.empty and 'motivo_principal' in gilts_discard_df.columns:
                discard_reasons = gilts_discard_df['motivo_principal'].value_counts().reset_index()
                discard_reasons.columns = ['Motivo', 'Contagem']
                
                fig = px.bar(
                    discard_reasons,
                    x='Motivo',
                    y='Contagem',
                    title='Principais Motivos de Descarte',
                    color='Contagem',
                    color_continuous_scale=px.colors.sequential.Reds
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Não há dados de descarte disponíveis.")
        
        # Tabela de leitoas ativas
        st.subheader("Leitoas Ativas")
        
        # Obter leitoas disponíveis (não descartadas)
        available_gilts = get_available_gilts(gilts_df)
        
        if not available_gilts.empty:
            # Preparar dados para exibição
            display_df = available_gilts[[
                'identificacao', 'brinco', 'tatuagem', 'data_nascimento', 
                'peso_selecao', 'status', 'data_selecao'
            ]].copy()
            
            # Formatar datas
            if 'data_nascimento' in display_df.columns:
                display_df['data_nascimento'] = pd.to_datetime(display_df['data_nascimento']).dt.strftime('%d/%m/%Y')
            
            if 'data_selecao' in display_df.columns:
                display_df['data_selecao'] = pd.to_datetime(display_df['data_selecao']).dt.strftime('%d/%m/%Y')
            
            # Adicionar idade em dias
            if 'data_nascimento' in available_gilts.columns:
                display_df['idade_dias'] = available_gilts['data_nascimento'].apply(
                    lambda x: calculate_age(x) if pd.notna(x) else None
                )
            
            # Renomear colunas
            display_df = display_df.rename(columns={
                'identificacao': 'Identificação',
                'brinco': 'Brinco',
                'tatuagem': 'Tatuagem',
                'data_nascimento': 'Data de Nascimento',
                'peso_selecao': 'Peso (kg)',
                'status': 'Status',
                'data_selecao': 'Data de Seleção',
                'idade_dias': 'Idade (dias)'
            })
            
            st.dataframe(
                display_df.sort_values('Data de Nascimento', ascending=False),
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("Não há leitoas ativas cadastradas.")
    else:
        st.info("Não há leitoas cadastradas. Utilize a aba 'Cadastro de Leitoas' para cadastrar novas leitoas.")

with tab2:
    st.header("Cadastro de Leitoas")
    
    # Formulário para cadastro de nova leitoa
    with st.form("form_cadastro_leitoa"):
        st.subheader("Dados da Leitoa")
        
        col1, col2 = st.columns(2)
        
        with col1:
            identificacao = st.text_input(
                "Identificação da Leitoa",
                placeholder="ID único para identificação"
            )
            
            brinco = st.text_input(
                "Brinco",
                placeholder="Número do brinco"
            )
            
            tatuagem = st.text_input(
                "Tatuagem",
                placeholder="Número ou código da tatuagem"
            )
            
            chip = st.text_input(
                "Chip",
                placeholder="Número do chip eletrônico (opcional)"
            )
            
            data_nascimento = st.date_input(
                "Data de Nascimento",
                value=datetime.now().date() - timedelta(days=160)  # Leitoas com ~5 meses
            )
        
        with col2:
            origem_options = ["Própria", "Comprada", "Transferência", "Outra"]
            origem = st.selectbox("Origem", origem_options)
            
            genetica = st.text_input(
                "Linhagem Genética",
                placeholder="Linhagem da leitoa"
            )
            
            mae = st.text_input(
                "Identificação da Mãe",
                placeholder="ID da matriz (se conhecida)"
            )
            
            pai = st.text_input(
                "Identificação do Pai",
                placeholder="ID do reprodutor (se conhecido)"
            )
            
            observacao = st.text_area(
                "Observações",
                placeholder="Informações adicionais sobre a leitoa...",
                height=123
            )
        
        submitted = st.form_submit_button("Cadastrar Leitoa")
        
        if submitted:
            # Validar campos obrigatórios
            if not identificacao:
                st.error("O campo Identificação é obrigatório.")
            else:
                # Verificar se já existe leitoa com a mesma identificação
                if not gilts_df.empty and identificacao in gilts_df['identificacao'].values:
                    st.error(f"Já existe uma leitoa cadastrada com a identificação {identificacao}.")
                else:
                    # Criar novo registro
                    id_leitoa = str(uuid.uuid4())
                    
                    nova_leitoa = {
                        'id_leitoa': id_leitoa,
                        'id_animal': None,  # Pode ser vinculado a um animal existente, se necessário
                        'identificacao': identificacao,
                        'brinco': brinco,
                        'tatuagem': tatuagem,
                        'chip': chip,
                        'data_nascimento': data_nascimento.strftime('%Y-%m-%d'),
                        'origem': origem,
                        'genetica': genetica,
                        'mae': mae,
                        'pai': pai,
                        'data_selecao': None,
                        'peso_selecao': None,
                        'idade_selecao': None,
                        'status': 'Cadastrada',  # Status inicial
                        'data_primeiro_cio': None,
                        'observacao': observacao
                    }
                    
                    # Adicionar ao DataFrame
                    if gilts_df.empty:
                        gilts_df = pd.DataFrame([nova_leitoa])
                    else:
                        gilts_df = pd.concat([gilts_df, pd.DataFrame([nova_leitoa])], ignore_index=True)
                    
                    # Salvar DataFrame atualizado
                    save_gilts(gilts_df)
                    
                    st.success(f"Leitoa {identificacao} cadastrada com sucesso!")
                    st.rerun()
    
    # Lista de leitoas cadastradas para edição rápida
    if not gilts_df.empty:
        st.subheader("Leitoas Cadastradas")
        
        # Filtrar por status
        status_filter = st.multiselect(
            "Filtrar por Status",
            options=gilts_df['status'].unique(),
            default=['Cadastrada']
        )
        
        filtered_gilts = gilts_df[gilts_df['status'].isin(status_filter)] if status_filter else gilts_df
        
        if not filtered_gilts.empty:
            # Exibir tabela com leitoas
            display_df = filtered_gilts[[
                'identificacao', 'brinco', 'tatuagem', 'data_nascimento', 'origem', 'status'
            ]].copy()
            
            # Formatar datas
            if 'data_nascimento' in display_df.columns:
                display_df['data_nascimento'] = pd.to_datetime(display_df['data_nascimento']).dt.strftime('%d/%m/%Y')
            
            # Renomear colunas
            display_df = display_df.rename(columns={
                'identificacao': 'Identificação',
                'brinco': 'Brinco',
                'tatuagem': 'Tatuagem',
                'data_nascimento': 'Data de Nascimento',
                'origem': 'Origem',
                'status': 'Status'
            })
            
            st.dataframe(
                display_df,
                hide_index=True,
                use_container_width=True
            )
            
            # Editar leitoa existente
            st.subheader("Editar Leitoa")
            
            # Selecionar leitoa para edição
            selected_id = st.selectbox(
                "Selecione a Leitoa para Edição",
                options=filtered_gilts['identificacao'].tolist()
            )
            
            if selected_id:
                # Obter os dados da leitoa selecionada
                selected_gilt = gilts_df[gilts_df['identificacao'] == selected_id].iloc[0]
                
                with st.form("form_edicao_leitoa"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        brinco_edit = st.text_input(
                            "Brinco",
                            value=selected_gilt['brinco'] if pd.notna(selected_gilt['brinco']) else ""
                        )
                        
                        tatuagem_edit = st.text_input(
                            "Tatuagem",
                            value=selected_gilt['tatuagem'] if pd.notna(selected_gilt['tatuagem']) else ""
                        )
                        
                        chip_edit = st.text_input(
                            "Chip",
                            value=selected_gilt['chip'] if pd.notna(selected_gilt['chip']) else ""
                        )
                        
                        data_nascimento_edit = st.date_input(
                            "Data de Nascimento",
                            value=pd.to_datetime(selected_gilt['data_nascimento']).date() if pd.notna(selected_gilt['data_nascimento']) else datetime.now().date()
                        )
                    
                    with col2:
                        origem_options = ["Própria", "Comprada", "Transferência", "Outra"]
                        origem_edit = st.selectbox(
                            "Origem",
                            options=origem_options,
                            index=origem_options.index(selected_gilt['origem']) if selected_gilt['origem'] in origem_options else 0
                        )
                        
                        genetica_edit = st.text_input(
                            "Linhagem Genética",
                            value=selected_gilt['genetica'] if pd.notna(selected_gilt['genetica']) else ""
                        )
                        
                        mae_edit = st.text_input(
                            "Identificação da Mãe",
                            value=selected_gilt['mae'] if pd.notna(selected_gilt['mae']) else ""
                        )
                        
                        pai_edit = st.text_input(
                            "Identificação do Pai",
                            value=selected_gilt['pai'] if pd.notna(selected_gilt['pai']) else ""
                        )
                    
                    observacao_edit = st.text_area(
                        "Observações",
                        value=selected_gilt['observacao'] if pd.notna(selected_gilt['observacao']) else "",
                        height=100
                    )
                    
                    update_button = st.form_submit_button("Atualizar Leitoa")
                    
                    if update_button:
                        # Atualizar o registro
                        idx = gilts_df[gilts_df['identificacao'] == selected_id].index[0]
                        
                        gilts_df.loc[idx, 'brinco'] = brinco_edit
                        gilts_df.loc[idx, 'tatuagem'] = tatuagem_edit
                        gilts_df.loc[idx, 'chip'] = chip_edit
                        gilts_df.loc[idx, 'data_nascimento'] = data_nascimento_edit.strftime('%Y-%m-%d')
                        gilts_df.loc[idx, 'origem'] = origem_edit
                        gilts_df.loc[idx, 'genetica'] = genetica_edit
                        gilts_df.loc[idx, 'mae'] = mae_edit
                        gilts_df.loc[idx, 'pai'] = pai_edit
                        gilts_df.loc[idx, 'observacao'] = observacao_edit
                        
                        # Salvar DataFrame atualizado
                        save_gilts(gilts_df)
                        
                        st.success(f"Leitoa {selected_id} atualizada com sucesso!")
                        st.rerun()
        else:
            st.info(f"Não há leitoas com os status selecionados: {', '.join(status_filter)}")
    else:
        st.info("Não há leitoas cadastradas.")

with tab3:
    st.header("Avaliação e Seleção de Leitoas")
    
    # Verificar se há leitoas cadastradas
    if gilts_df.empty:
        st.info("Não há leitoas cadastradas. Utilize a aba 'Cadastro de Leitoas' para cadastrar novas leitoas.")
    else:
        # Filtrar leitoas disponíveis para seleção (não selecionadas e não descartadas)
        leitoas_para_selecao = gilts_df[gilts_df['status'].isin(['Cadastrada', 'Em Avaliação'])]
        
        if leitoas_para_selecao.empty:
            st.info("Não há leitoas disponíveis para seleção. Todas as leitoas cadastradas já foram selecionadas ou descartadas.")
        else:
            # Selecionar leitoa para avaliação
            selected_id = st.selectbox(
                "Selecione a Leitoa para Avaliação",
                options=leitoas_para_selecao['identificacao'].tolist(),
                format_func=lambda x: f"{x} - Brinco: {leitoas_para_selecao[leitoas_para_selecao['identificacao'] == x]['brinco'].iloc[0] if pd.notna(leitoas_para_selecao[leitoas_para_selecao['identificacao'] == x]['brinco'].iloc[0]) else 'N/A'} - Tatuagem: {leitoas_para_selecao[leitoas_para_selecao['identificacao'] == x]['tatuagem'].iloc[0] if pd.notna(leitoas_para_selecao[leitoas_para_selecao['identificacao'] == x]['tatuagem'].iloc[0]) else 'N/A'}"
            )
            
            if selected_id:
                # Obter dados da leitoa selecionada
                selected_gilt = leitoas_para_selecao[leitoas_para_selecao['identificacao'] == selected_id].iloc[0]
                
                # Mostrar detalhes da leitoa
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Identificação", selected_gilt['identificacao'])
                    
                with col2:
                    brinco_display = selected_gilt['brinco'] if pd.notna(selected_gilt['brinco']) else "N/A"
                    st.metric("Brinco", brinco_display)
                    
                with col3:
                    tatuagem_display = selected_gilt['tatuagem'] if pd.notna(selected_gilt['tatuagem']) else "N/A"
                    st.metric("Tatuagem", tatuagem_display)
                    
                with col4:
                    if pd.notna(selected_gilt['data_nascimento']):
                        idade_dias = calculate_age(selected_gilt['data_nascimento'])
                        st.metric("Idade (dias)", idade_dias)
                    else:
                        st.metric("Idade (dias)", "N/A")
                
                # Formulário de avaliação
                with st.form("form_avaliacao"):
                    st.subheader("Critérios de Avaliação")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        data_avaliacao = st.date_input(
                            "Data da Avaliação",
                            value=datetime.now().date()
                        )
                        
                        peso = st.number_input(
                            "Peso (kg)",
                            min_value=0.0,
                            max_value=500.0,
                            value=120.0,
                            step=0.5,
                            format="%.1f"
                        )
                        
                        idade = 0
                        if pd.notna(selected_gilt['data_nascimento']):
                            idade = calculate_age(selected_gilt['data_nascimento'])
                        
                        st.metric("Idade na Seleção (dias)", idade)
                        
                        espessura_toucinho = st.number_input(
                            "Espessura de Toucinho (mm)",
                            min_value=0.0,
                            max_value=50.0,
                            value=12.0,
                            step=0.1,
                            format="%.1f"
                        )
                        
                        profundidade_lombo = st.number_input(
                            "Profundidade de Lombo (mm)",
                            min_value=0.0,
                            max_value=100.0,
                            value=50.0,
                            step=0.5,
                            format="%.1f"
                        )
                        
                        comprimento_corporal = st.number_input(
                            "Comprimento Corporal (cm)",
                            min_value=0,
                            max_value=200,
                            value=120
                        )
                    
                    with col2:
                        largura_ombros = st.number_input(
                            "Largura dos Ombros (cm)",
                            min_value=0,
                            max_value=100,
                            value=35
                        )
                        
                        largura_quadril = st.number_input(
                            "Largura do Quadril (cm)",
                            min_value=0,
                            max_value=100,
                            value=36
                        )
                        
                        altura_posterior = st.number_input(
                            "Altura Posterior (cm)",
                            min_value=0,
                            max_value=150,
                            value=65
                        )
                        
                        numero_tetos = st.number_input(
                            "Número de Tetos Funcionais",
                            min_value=0,
                            max_value=20,
                            value=14
                        )
                        
                        tetos_invertidos = st.number_input(
                            "Número de Tetos Invertidos",
                            min_value=0,
                            max_value=20,
                            value=0
                        )
                        
                        qualidade_aprumos = st.selectbox(
                            "Qualidade dos Aprumos",
                            options=["Excelente", "Boa", "Regular", "Ruim"]
                        )
                        
                        temperamento = st.selectbox(
                            "Temperamento",
                            options=["Dócil", "Normal", "Agressivo"]
                        )
                    
                    # Avaliação visual e escore geral
                    avaliacao_visual = st.selectbox(
                        "Avaliação Visual",
                        options=["Excelente", "Boa", "Regular", "Ruim"]
                    )
                    
                    escore_geral = st.slider(
                        "Escore Geral (1-5)",
                        min_value=1,
                        max_value=5,
                        value=3,
                        help="1 = Ruim, 5 = Excelente"
                    )
                    
                    # Recomendação
                    recomendacao = st.selectbox(
                        "Recomendação",
                        options=["Selecionada", "Descartada"]
                    )
                    
                    if recomendacao == "Descartada":
                        motivo_descarte_options = [
                            "Baixo Peso", "Tamanho Reduzido", "Problemas de Aprumos", 
                            "Poucos Tetos", "Tetos Invertidos", "Temperamento Agressivo",
                            "Conformação Ruim", "Excesso de Gordura", "Problemas Genéticos",
                            "Outro"
                        ]
                        motivo_recomendacao = st.selectbox(
                            "Motivo do Descarte",
                            options=motivo_descarte_options
                        )
                        
                        if motivo_recomendacao == "Outro":
                            motivo_personalizado = st.text_input(
                                "Especifique o Motivo",
                                placeholder="Descreva o motivo do descarte..."
                            )
                            motivo_recomendacao_final = motivo_personalizado
                        else:
                            motivo_recomendacao_final = motivo_recomendacao
                    else:
                        motivo_recomendacao_final = "Adequada para reprodução"
                    
                    tecnico_responsavel = st.text_input(
                        "Técnico Responsável",
                        value="Responsável"
                    )
                    
                    observacao = st.text_area(
                        "Observações",
                        placeholder="Observações adicionais sobre a avaliação..."
                    )
                    
                    # Botão de submissão
                    submitted = st.form_submit_button("Registrar Avaliação")
                    
                    if submitted:
                        # 1. Criar registro de avaliação
                        id_selecao = str(uuid.uuid4())
                        
                        nova_selecao = {
                            'id_selecao': id_selecao,
                            'id_leitoa': selected_gilt['id_leitoa'],
                            'data_selecao': data_avaliacao.strftime('%Y-%m-%d'),
                            'peso': peso,
                            'idade': idade,
                            'espessura_toucinho': espessura_toucinho,
                            'profundidade_lombo': profundidade_lombo,
                            'comprimento_corporal': comprimento_corporal,
                            'largura_ombros': largura_ombros,
                            'largura_quadril': largura_quadril,
                            'altura_posterior': altura_posterior,
                            'numero_tetos': numero_tetos,
                            'tetos_invertidos': tetos_invertidos,
                            'qualidade_aprumos': qualidade_aprumos,
                            'temperamento': temperamento,
                            'avaliacao_visual': avaliacao_visual,
                            'escore_geral': escore_geral,
                            'recomendacao': recomendacao,
                            'motivo_recomendacao': motivo_recomendacao_final,
                            'tecnico_responsavel': tecnico_responsavel,
                            'observacao': observacao
                        }
                        
                        # Adicionar ao DataFrame de seleção
                        if gilts_selection_df.empty:
                            gilts_selection_df = pd.DataFrame([nova_selecao])
                        else:
                            gilts_selection_df = pd.concat([gilts_selection_df, pd.DataFrame([nova_selecao])], ignore_index=True)
                        
                        # Salvar DataFrame de seleção
                        save_gilts_selection(gilts_selection_df)
                        
                        # 2. Atualizar status da leitoa
                        idx = gilts_df[gilts_df['id_leitoa'] == selected_gilt['id_leitoa']].index[0]
                        
                        gilts_df.loc[idx, 'status'] = recomendacao
                        gilts_df.loc[idx, 'data_selecao'] = data_avaliacao.strftime('%Y-%m-%d')
                        gilts_df.loc[idx, 'peso_selecao'] = peso
                        gilts_df.loc[idx, 'idade_selecao'] = idade
                        
                        # 3. Se for descartada, criar registro de descarte
                        if recomendacao == "Descartada":
                            id_descarte = str(uuid.uuid4())
                            
                            novo_descarte = {
                                'id_descarte': id_descarte,
                                'id_leitoa': selected_gilt['id_leitoa'],
                                'data_descarte': data_avaliacao.strftime('%Y-%m-%d'),
                                'peso_descarte': peso,
                                'idade_descarte': idade,
                                'motivo_principal': motivo_recomendacao_final,
                                'motivos_secundarios': None,
                                'destino': "Não especificado",
                                'valor_venda': None,
                                'tecnico_responsavel': tecnico_responsavel,
                                'observacao': observacao
                            }
                            
                            # Adicionar ao DataFrame de descarte
                            if gilts_discard_df.empty:
                                gilts_discard_df = pd.DataFrame([novo_descarte])
                            else:
                                gilts_discard_df = pd.concat([gilts_discard_df, pd.DataFrame([novo_descarte])], ignore_index=True)
                            
                            # Salvar DataFrame de descarte
                            save_gilts_discard(gilts_discard_df)
                        
                        # Salvar DataFrame de leitoas
                        save_gilts(gilts_df)
                        
                        # Exibir mensagem de sucesso
                        if recomendacao == "Selecionada":
                            st.success(f"Leitoa {selected_id} avaliada e selecionada com sucesso!")
                        else:
                            st.success(f"Leitoa {selected_id} avaliada e marcada para descarte!")
                        
                        st.rerun()
            
            # Histórico de avaliações
            if not gilts_selection_df.empty:
                st.subheader("Histórico de Avaliações")
                
                # Filtrar por recomendação
                recomendacao_filter = st.multiselect(
                    "Filtrar por Recomendação",
                    options=gilts_selection_df['recomendacao'].unique(),
                    default=gilts_selection_df['recomendacao'].unique().tolist()
                )
                
                filtered_selections = gilts_selection_df[gilts_selection_df['recomendacao'].isin(recomendacao_filter)] if recomendacao_filter else gilts_selection_df
                
                if not filtered_selections.empty:
                    # Adicionar identificação da leitoa
                    filtered_selections = pd.merge(
                        filtered_selections,
                        gilts_df[['id_leitoa', 'identificacao']],
                        on='id_leitoa',
                        how='left'
                    )
                    
                    # Preparar dados para exibição
                    display_df = filtered_selections[[
                        'identificacao', 'data_selecao', 'idade', 'peso', 
                        'numero_tetos', 'escore_geral', 'recomendacao', 'motivo_recomendacao'
                    ]].copy()
                    
                    # Formatar datas
                    display_df['data_selecao'] = pd.to_datetime(display_df['data_selecao']).dt.strftime('%d/%m/%Y')
                    
                    # Renomear colunas
                    display_df = display_df.rename(columns={
                        'identificacao': 'Identificação',
                        'data_selecao': 'Data da Avaliação',
                        'idade': 'Idade (dias)',
                        'peso': 'Peso (kg)',
                        'numero_tetos': 'Nº Tetos',
                        'escore_geral': 'Escore (1-5)',
                        'recomendacao': 'Recomendação',
                        'motivo_recomendacao': 'Motivo'
                    })
                    
                    st.dataframe(
                        display_df.sort_values('Data da Avaliação', ascending=False),
                        hide_index=True,
                        use_container_width=True
                    )
                else:
                    st.info(f"Não há avaliações com as recomendações selecionadas: {', '.join(recomendacao_filter)}")
            else:
                st.info("Não há avaliações registradas.")

with tab4:
    st.header("Descarte de Leitoas")
    
    # Duas abas: Registrar Descarte e Histórico de Descartes
    descarte_tab1, descarte_tab2 = st.tabs(["Registrar Descarte", "Histórico de Descartes"])
    
    with descarte_tab1:
        if gilts_df.empty:
            st.info("Não há leitoas cadastradas.")
        else:
            # Filtrar leitoas não descartadas
            available_gilts = get_available_gilts(gilts_df)
            
            if available_gilts.empty:
                st.info("Não há leitoas disponíveis para descarte.")
            else:
                # Selecionar leitoa para descarte
                selected_id = st.selectbox(
                    "Selecione a Leitoa para Descarte",
                    options=available_gilts['identificacao'].tolist(),
                    format_func=lambda x: f"{x} - Brinco: {available_gilts[available_gilts['identificacao'] == x]['brinco'].iloc[0] if pd.notna(available_gilts[available_gilts['identificacao'] == x]['brinco'].iloc[0]) else 'N/A'} - Status: {available_gilts[available_gilts['identificacao'] == x]['status'].iloc[0]}"
                )
                
                if selected_id:
                    # Obter dados da leitoa selecionada
                    selected_gilt = available_gilts[available_gilts['identificacao'] == selected_id].iloc[0]
                    
                    # Mostrar detalhes da leitoa
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Identificação", selected_gilt['identificacao'])
                        
                    with col2:
                        brinco_display = selected_gilt['brinco'] if pd.notna(selected_gilt['brinco']) else "N/A"
                        st.metric("Brinco", brinco_display)
                        
                    with col3:
                        tatuagem_display = selected_gilt['tatuagem'] if pd.notna(selected_gilt['tatuagem']) else "N/A"
                        st.metric("Tatuagem", tatuagem_display)
                        
                    with col4:
                        status_display = selected_gilt['status'] if pd.notna(selected_gilt['status']) else "N/A"
                        st.metric("Status Atual", status_display)
                    
                    # Formulário de descarte
                    with st.form("form_descarte"):
                        st.subheader("Informações do Descarte")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            data_descarte = st.date_input(
                                "Data do Descarte",
                                value=datetime.now().date()
                            )
                            
                            peso_descarte = st.number_input(
                                "Peso no Descarte (kg)",
                                min_value=0.0,
                                max_value=500.0,
                                value=float(selected_gilt['peso_selecao']) if pd.notna(selected_gilt['peso_selecao']) else 120.0,
                                step=0.5,
                                format="%.1f"
                            )
                            
                            # Calcular idade no descarte
                            idade_descarte = 0
                            if pd.notna(selected_gilt['data_nascimento']):
                                idade_descarte = (data_descarte - pd.to_datetime(selected_gilt['data_nascimento']).date()).days
                            
                            st.metric("Idade no Descarte (dias)", idade_descarte)
                            
                            motivo_principal_options = [
                                "Baixo Desempenho", "Problemas de Aprumos", "Poucos Tetos", 
                                "Tetos Invertidos", "Temperamento Agressivo", "Problemas Reprodutivos",
                                "Idade Avançada", "Problemas Sanitários", "Excesso de Animais",
                                "Reforma do Plantel", "Outro"
                            ]
                            motivo_principal = st.selectbox(
                                "Motivo Principal do Descarte",
                                options=motivo_principal_options
                            )
                            
                            if motivo_principal == "Outro":
                                motivo_principal_outro = st.text_input(
                                    "Especifique o Motivo Principal",
                                    placeholder="Descreva o motivo principal do descarte..."
                                )
                                motivo_principal_final = motivo_principal_outro
                            else:
                                motivo_principal_final = motivo_principal
                        
                        with col2:
                            motivos_secundarios = st.multiselect(
                                "Motivos Secundários",
                                options=[op for op in motivo_principal_options if op != motivo_principal and op != "Outro"]
                            )
                            
                            destino_options = ["Abate", "Venda", "Outro"]
                            destino = st.selectbox(
                                "Destino da Leitoa",
                                options=destino_options
                            )
                            
                            if destino == "Venda":
                                valor_venda = st.number_input(
                                    "Valor de Venda (R$)",
                                    min_value=0.0,
                                    value=0.0,
                                    step=10.0,
                                    format="%.2f"
                                )
                            else:
                                valor_venda = None
                            
                            tecnico_responsavel = st.text_input(
                                "Técnico Responsável",
                                value="Responsável"
                            )
                        
                        observacao = st.text_area(
                            "Observações",
                            placeholder="Observações adicionais sobre o descarte..."
                        )
                        
                        # Botão de submissão
                        submitted = st.form_submit_button("Registrar Descarte")
                        
                        if submitted:
                            # 1. Criar registro de descarte
                            id_descarte = str(uuid.uuid4())
                            
                            novo_descarte = {
                                'id_descarte': id_descarte,
                                'id_leitoa': selected_gilt['id_leitoa'],
                                'data_descarte': data_descarte.strftime('%Y-%m-%d'),
                                'peso_descarte': peso_descarte,
                                'idade_descarte': idade_descarte,
                                'motivo_principal': motivo_principal_final,
                                'motivos_secundarios': ", ".join(motivos_secundarios) if motivos_secundarios else None,
                                'destino': destino,
                                'valor_venda': valor_venda,
                                'tecnico_responsavel': tecnico_responsavel,
                                'observacao': observacao
                            }
                            
                            # Adicionar ao DataFrame de descarte
                            if gilts_discard_df.empty:
                                gilts_discard_df = pd.DataFrame([novo_descarte])
                            else:
                                gilts_discard_df = pd.concat([gilts_discard_df, pd.DataFrame([novo_descarte])], ignore_index=True)
                            
                            # Salvar DataFrame de descarte
                            save_gilts_discard(gilts_discard_df)
                            
                            # 2. Atualizar status da leitoa para "Descartada"
                            idx = gilts_df[gilts_df['id_leitoa'] == selected_gilt['id_leitoa']].index[0]
                            gilts_df.loc[idx, 'status'] = 'Descartada'
                            
                            # Adicionar observação sobre o descarte
                            current_obs = gilts_df.loc[idx, 'observacao']
                            new_obs = f"{current_obs}\nDescartada em {data_descarte.strftime('%d/%m/%Y')} por: {motivo_principal_final}" if pd.notna(current_obs) else f"Descartada em {data_descarte.strftime('%d/%m/%Y')} por: {motivo_principal_final}"
                            gilts_df.loc[idx, 'observacao'] = new_obs
                            
                            # Salvar DataFrame de leitoas
                            save_gilts(gilts_df)
                            
                            # Exibir mensagem de sucesso
                            st.success(f"Leitoa {selected_id} descartada com sucesso!")
                            st.rerun()
    
    with descarte_tab2:
        st.subheader("Histórico de Descartes")
        
        if gilts_discard_df.empty:
            st.info("Não há registros de descarte.")
        else:
            # Adicionar identificação da leitoa
            display_discard = pd.merge(
                gilts_discard_df,
                gilts_df[['id_leitoa', 'identificacao', 'brinco', 'tatuagem']],
                on='id_leitoa',
                how='left'
            )
            
            # Preparar dados para exibição
            display_df = display_discard[[
                'identificacao', 'brinco', 'data_descarte', 'idade_descarte', 
                'peso_descarte', 'motivo_principal', 'destino'
            ]].copy()
            
            # Formatar datas
            display_df['data_descarte'] = pd.to_datetime(display_df['data_descarte']).dt.strftime('%d/%m/%Y')
            
            # Renomear colunas
            display_df = display_df.rename(columns={
                'identificacao': 'Identificação',
                'brinco': 'Brinco',
                'data_descarte': 'Data de Descarte',
                'idade_descarte': 'Idade (dias)',
                'peso_descarte': 'Peso (kg)',
                'motivo_principal': 'Motivo Principal',
                'destino': 'Destino'
            })
            
            st.dataframe(
                display_df.sort_values('Data de Descarte', ascending=False),
                hide_index=True,
                use_container_width=True
            )
            
            # Análise de descartes
            st.subheader("Análise de Descartes")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de motivos de descarte
                motivos_count = display_discard['motivo_principal'].value_counts().reset_index()
                motivos_count.columns = ['Motivo', 'Contagem']
                
                fig = px.pie(
                    motivos_count,
                    values='Contagem',
                    names='Motivo',
                    title='Motivos de Descarte',
                    color_discrete_sequence=px.colors.qualitative.Bold
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Gráfico de destino dos animais descartados
                destino_count = display_discard['destino'].value_counts().reset_index()
                destino_count.columns = ['Destino', 'Contagem']
                
                fig = px.bar(
                    destino_count,
                    x='Destino',
                    y='Contagem',
                    title='Destino dos Animais Descartados',
                    color='Destino',
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Gráfico de idade no descarte
            st.subheader("Idade no Descarte")
            
            fig = px.histogram(
                display_discard,
                x='idade_descarte',
                nbins=20,
                title='Distribuição de Idade no Descarte',
                labels={'idade_descarte': 'Idade (dias)', 'count': 'Frequência'},
                color_discrete_sequence=['#2E86C1']
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Exportar dados
            if st.button("Exportar Dados de Descarte (CSV)"):
                csv = display_discard.to_csv(index=False)
                st.download_button(
                    label="Baixar CSV",
                    data=csv,
                    file_name=f"descartes_leitoas_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )