import streamlit as st
import pandas as pd
import uuid
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
from utils import (
    load_animals,
    load_weaning,
    load_pens,
    load_pen_allocations,
    save_pen_allocations,
    load_nursery,
    save_nursery,
    load_nursery_batches,
    save_nursery_batches,
    load_nursery_movements,
    save_nursery_movements,
    get_active_nursery_batches,
    calculate_nursery_metrics,
    get_batch_details,
    get_available_pens
,
    check_permission
)

# Configuração da página
st.set_page_config(
    page_title="Creche - Sistema de Gestão de Suinocultura",
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
weaning_df = load_weaning()
pens_df = load_pens()
pen_allocations_df = load_pen_allocations()
nursery_df = load_nursery()
nursery_batches_df = load_nursery_batches()
nursery_movements_df = load_nursery_movements()

# Título da página
st.title("Creche 🐖")
st.markdown("""
Gerencie os lotes de leitões na fase de creche, com acompanhamento de peso, mortalidade, e movimentações.
A creche é uma fase crucial para o desenvolvimento dos leitões após o desmame.
""")

# Abas para diferentes funcionalidades
tab1, tab2, tab3, tab4 = st.tabs(["Visão Geral", "Novo Lote", "Registro de Eventos", "Relatórios"])

with tab1:
    st.header("Visão Geral da Creche")
    
    # Obter lotes ativos
    lotes_ativos = get_active_nursery_batches(nursery_batches_df)
    
    if lotes_ativos.empty:
        st.info("Não há lotes ativos na creche no momento. Utilize a aba 'Novo Lote' para iniciar um novo lote.")
    else:
        # Exibir métricas gerais
        total_lotes = len(lotes_ativos)
        total_leitoes = lotes_ativos['quantidade_atual'].sum() if 'quantidade_atual' in lotes_ativos.columns else 0
        
        # Calcular média de peso
        peso_medio = lotes_ativos['peso_medio_atual'].mean() if 'peso_medio_atual' in lotes_ativos.columns else 0
        
        # Calcular taxa média de mortalidade
        mortalidade_media = lotes_ativos['mortalidade'].mean() if 'mortalidade' in lotes_ativos.columns else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Lotes", total_lotes)
        
        with col2:
            st.metric("Total de Leitões", int(total_leitoes))
            
        with col3:
            st.metric("Peso Médio (kg)", f"{peso_medio:.2f}")
            
        with col4:
            st.metric("Mortalidade Média (%)", f"{mortalidade_media:.1f}")
        
        # Listar lotes com detalhes
        st.subheader("Lotes Ativos")
        
        for _, lote in lotes_ativos.iterrows():
            lote_id = lote['id_lote']
            
            with st.expander(f"Lote: {lote['identificacao']} - {lote['quantidade_atual']} leitões"):
                # Calcular dias na creche
                if pd.notna(lote['data_entrada']):
                    data_entrada = pd.to_datetime(lote['data_entrada']).date()
                    dias_creche = (datetime.now().date() - data_entrada).days
                else:
                    dias_creche = 0
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Dias na Creche", dias_creche)
                    st.metric("Peso Médio Entrada (kg)", f"{lote['peso_medio_entrada']:.2f}")
                    
                with col2:
                    st.metric("Idade Média Entrada (dias)", int(lote['idade_media_entrada']))
                    st.metric("Idade Atual (dias)", int(lote['idade_media_entrada']) + dias_creche)
                
                with col3:
                    st.metric("Peso Atual (kg)", f"{lote['peso_medio_atual']:.2f}")
                    st.metric("Mortalidade (%)", f"{lote['mortalidade']:.1f}")
                
                # Exibir histórico de eventos
                if not nursery_movements_df.empty:
                    lote_events = nursery_movements_df[nursery_movements_df['id_lote'] == lote_id].sort_values('data', ascending=False)
                    
                    if not lote_events.empty:
                        st.subheader("Histórico de Eventos")
                        
                        # Formatar para exibição
                        display_events = lote_events[['data', 'tipo', 'quantidade', 'peso_medio', 'ganho_diario', 'causa', 'observacao']].copy()
                        display_events['data'] = pd.to_datetime(display_events['data']).dt.strftime('%d/%m/%Y')
                        
                        st.dataframe(
                            display_events.rename(columns={
                                'data': 'Data',
                                'tipo': 'Tipo',
                                'quantidade': 'Quantidade',
                                'peso_medio': 'Peso Médio (kg)',
                                'ganho_diario': 'GMD (g/dia)',
                                'causa': 'Causa',
                                'observacao': 'Observação'
                            }),
                            hide_index=True
                        )
                    else:
                        st.info("Nenhum evento registrado para este lote.")
                        
                # Visualização gráfica de evolução de peso
                if not nursery_movements_df.empty:
                    peso_events = nursery_movements_df[(nursery_movements_df['id_lote'] == lote_id) & 
                                                      (nursery_movements_df['tipo'] == 'Pesagem')].sort_values('data')
                    
                    if not peso_events.empty and len(peso_events) > 1:
                        st.subheader("Evolução de Peso")
                        
                        # Adicionar peso inicial (entrada)
                        initial_data = {
                            'data': pd.to_datetime(lote['data_entrada']),
                            'peso_medio': lote['peso_medio_entrada'],
                            'idade': lote['idade_media_entrada']
                        }
                        
                        # Criar dataframe para o gráfico
                        peso_df = peso_events[['data', 'peso_medio']].copy()
                        peso_df['data'] = pd.to_datetime(peso_df['data'])
                        
                        # Adicionar o dado inicial
                        peso_df = pd.concat([pd.DataFrame([initial_data]), peso_df], ignore_index=True)
                        
                        # Calcular idade para cada pesagem
                        peso_df['dias_creche'] = (peso_df['data'] - pd.to_datetime(lote['data_entrada'])).dt.days
                        peso_df['idade'] = lote['idade_media_entrada'] + peso_df['dias_creche']
                        
                        # Criar gráfico
                        fig = px.line(
                            peso_df,
                            x='dias_creche',
                            y='peso_medio',
                            markers=True,
                            labels={
                                'dias_creche': 'Dias na Creche',
                                'peso_medio': 'Peso Médio (kg)'
                            },
                            title="Evolução de Peso do Lote"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Gráfico de ganho diário
                        if 'ganho_diario' in peso_events.columns:
                            st.subheader("Ganho Médio Diário")
                            
                            fig = px.bar(
                                peso_events,
                                x='data',
                                y='ganho_diario',
                                labels={
                                    'data': 'Data',
                                    'ganho_diario': 'GMD (g/dia)'
                                },
                                title="Ganho Médio Diário (g/dia)"
                            )
                            st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("Registrar Novo Lote na Creche")
    
    # Opções de origem do lote
    origem_options = ["Desmame Interno", "Transferência", "Compra Externa"]
    origem_lote = st.selectbox("Origem do Lote", origem_options)
    
    if origem_lote == "Desmame Interno":
        # Lista de desmames recentes sem lote de creche associado
        if not weaning_df.empty:
            # Verificar quais desmames já têm lotes associados
            desmames_com_lote = []
            if not nursery_batches_df.empty and 'id_desmame' in nursery_batches_df.columns:
                desmames_com_lote = nursery_batches_df['id_desmame'].dropna().unique().tolist()
            
            # Filtrar desmames disponíveis (destino = Creche e sem lote associado)
            desmames_disponiveis = weaning_df[
                (weaning_df['destino_leitoes'] == 'Creche') & 
                (~weaning_df['id_desmame'].isin(desmames_com_lote))
            ].sort_values('data_desmame', ascending=False)
            
            if desmames_disponiveis.empty:
                st.warning("Não há desmames disponíveis para criação de lotes. Registre um novo desmame ou escolha outra origem.")
            else:
                # Formatação das opções de seleção
                desmame_options = []
                for _, desmame in desmames_disponiveis.iterrows():
                    data_desmame = pd.to_datetime(desmame['data_desmame']).strftime('%d/%m/%Y')
                    id_animal = desmame['id_animal_mae']
                    identificacao_matriz = "Desconhecida"
                    
                    if not animals_df.empty and id_animal in animals_df['id_animal'].values:
                        identificacao_matriz = animals_df[animals_df['id_animal'] == id_animal]['identificacao'].iloc[0]
                    
                    label = f"Desmame de {data_desmame} - Matriz: {identificacao_matriz} - {desmame['total_desmamados']} leitões"
                    desmame_options.append({
                        'label': label,
                        'id_desmame': desmame['id_desmame'],
                        'quantidade': desmame['total_desmamados'],
                        'peso_medio': desmame['peso_medio_desmame'],
                        'data_desmame': desmame['data_desmame'],
                        'idade_desmame': desmame['idade_desmame']
                    })
                
                selected_desmame = st.selectbox(
                    "Selecione o Desmame",
                    options=[d['id_desmame'] for d in desmame_options],
                    format_func=lambda x: next(d['label'] for d in desmame_options if d['id_desmame'] == x)
                )
                
                # Obter dados do desmame selecionado
                selected_data = next(d for d in desmame_options if d['id_desmame'] == selected_desmame)
                
                # Formulário para o novo lote
                with st.form("novo_lote_form"):
                    st.subheader("Dados do Novo Lote")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        identificacao_lote = st.text_input(
                            "Identificação do Lote",
                            value=f"Lote-{datetime.now().strftime('%Y%m%d')}"
                        )
                        
                        quantidade_inicial = st.number_input(
                            "Quantidade de Leitões",
                            min_value=1,
                            max_value=1000,
                            value=int(selected_data['quantidade'])
                        )
                        
                        peso_medio_entrada = st.number_input(
                            "Peso Médio de Entrada (kg)",
                            min_value=0.1,
                            max_value=30.0,
                            value=float(selected_data['peso_medio']),
                            step=0.1,
                            format="%.1f"
                        )
                        
                        idade_media_entrada = st.number_input(
                            "Idade Média de Entrada (dias)",
                            min_value=1,
                            max_value=100,
                            value=int(selected_data['idade_desmame'])
                        )
                    
                    with col2:
                        data_entrada = st.date_input(
                            "Data de Entrada na Creche",
                            value=pd.to_datetime(selected_data['data_desmame']).date()
                        )
                        
                        # Definir data prevista de saída (geralmente 42 dias após entrada)
                        data_saida_prevista = st.date_input(
                            "Data Prevista de Saída",
                            value=data_entrada + timedelta(days=42)
                        )
                        
                        # Selecionar baia
                        if not pens_df.empty:
                            creche_pens = pens_df[pens_df['setor'] == 'Creche']
                            
                            if creche_pens.empty:
                                st.error("Não há baias de creche cadastradas. Por favor, cadastre uma baia no setor 'Creche' primeiro.")
                                id_baia = None
                            else:
                                available_pens = get_available_pens(creche_pens, pen_allocations_df, 'Leitão')
                                
                                if available_pens.empty:
                                    st.error("Não há baias de creche disponíveis no momento.")
                                    id_baia = None
                                else:
                                    id_baia = st.selectbox(
                                        "Baia de Destino",
                                        options=available_pens['id_baia'].tolist(),
                                        format_func=lambda x: f"{available_pens[available_pens['id_baia'] == x]['identificacao'].iloc[0]} ({available_pens[available_pens['id_baia'] == x]['ocupacao_atual'].iloc[0]}/{available_pens[available_pens['id_baia'] == x]['capacidade'].iloc[0]} ocupada)"
                                    )
                        else:
                            st.error("Não há baias cadastradas. Por favor, cadastre baias primeiro.")
                            id_baia = None
                        
                        observacao = st.text_area(
                            "Observações",
                            placeholder="Informações adicionais sobre o lote..."
                        )
                    
                    submit_button = st.form_submit_button("Registrar Novo Lote")
                    
                    if submit_button:
                        if id_baia is None:
                            st.error("É necessário selecionar uma baia válida para continuar.")
                        else:
                            # 1. Criar registro de creche
                            id_creche = str(uuid.uuid4())
                            
                            nova_creche = {
                                'id_creche': id_creche,
                                'id_baia': id_baia,
                                'data_inicio': data_entrada.strftime('%Y-%m-%d'),
                                'data_fim_prevista': data_saida_prevista.strftime('%Y-%m-%d'),
                                'data_fim_real': None,
                                'status': 'Ativo',
                                'observacao': observacao
                            }
                            
                            # Adicionar ao DataFrame
                            if nursery_df.empty:
                                nursery_df = pd.DataFrame([nova_creche])
                            else:
                                nursery_df = pd.concat([nursery_df, pd.DataFrame([nova_creche])], ignore_index=True)
                            
                            # Salvar DataFrame atualizado
                            save_nursery(nursery_df)
                            
                            # 2. Criar registro de lote
                            id_lote = str(uuid.uuid4())
                            
                            novo_lote = {
                                'id_lote': id_lote,
                                'id_creche': id_creche,
                                'id_desmame': selected_desmame,
                                'identificacao': identificacao_lote,
                                'quantidade_inicial': quantidade_inicial,
                                'quantidade_atual': quantidade_inicial,
                                'peso_medio_entrada': peso_medio_entrada,
                                'idade_media_entrada': idade_media_entrada,
                                'peso_medio_atual': peso_medio_entrada,
                                'mortalidade': 0.0,
                                'origem': 'Desmame',
                                'data_entrada': data_entrada.strftime('%Y-%m-%d'),
                                'data_saida': None,
                                'destino': None,
                                'status': 'Ativo',
                                'observacao': observacao
                            }
                            
                            # Adicionar ao DataFrame
                            if nursery_batches_df.empty:
                                nursery_batches_df = pd.DataFrame([novo_lote])
                            else:
                                nursery_batches_df = pd.concat([nursery_batches_df, pd.DataFrame([novo_lote])], ignore_index=True)
                            
                            # Salvar DataFrame atualizado
                            save_nursery_batches(nursery_batches_df)
                            
                            # 3. Criar primeira movimentação (entrada)
                            id_movimentacao = str(uuid.uuid4())
                            
                            nova_movimentacao = {
                                'id_movimentacao': id_movimentacao,
                                'id_lote': id_lote,
                                'tipo': 'Entrada',
                                'data': data_entrada.strftime('%Y-%m-%d'),
                                'quantidade': quantidade_inicial,
                                'peso_total': quantidade_inicial * peso_medio_entrada,
                                'peso_medio': peso_medio_entrada,
                                'ganho_diario': 0,
                                'causa': None,
                                'destino': None,
                                'medicamento': None,
                                'dosagem': None,
                                'via_aplicacao': None,
                                'responsavel': 'Sistema',
                                'observacao': f"Entrada na creche via desmame ID: {selected_desmame}"
                            }
                            
                            # Adicionar ao DataFrame
                            if nursery_movements_df.empty:
                                nursery_movements_df = pd.DataFrame([nova_movimentacao])
                            else:
                                nursery_movements_df = pd.concat([nursery_movements_df, pd.DataFrame([nova_movimentacao])], ignore_index=True)
                            
                            # Salvar DataFrame atualizado
                            save_nursery_movements(nursery_movements_df)
                            
                            st.success("Lote registrado com sucesso!")
                            st.rerun()
        else:
            st.warning("Não há registros de desmame disponíveis. Registre um desmame primeiro.")
    
    elif origem_lote == "Transferência" or origem_lote == "Compra Externa":
        # Formulário para entrada manual de lote
        with st.form("novo_lote_manual_form"):
            st.subheader("Dados do Novo Lote")
            
            col1, col2 = st.columns(2)
            
            with col1:
                identificacao_lote = st.text_input(
                    "Identificação do Lote",
                    value=f"Lote-{datetime.now().strftime('%Y%m%d')}"
                )
                
                quantidade_inicial = st.number_input(
                    "Quantidade de Leitões",
                    min_value=1,
                    max_value=1000,
                    value=20
                )
                
                peso_medio_entrada = st.number_input(
                    "Peso Médio de Entrada (kg)",
                    min_value=0.1,
                    max_value=30.0,
                    value=7.0,
                    step=0.1,
                    format="%.1f"
                )
                
                idade_media_entrada = st.number_input(
                    "Idade Média de Entrada (dias)",
                    min_value=1,
                    max_value=100,
                    value=28
                )
            
            with col2:
                data_entrada = st.date_input(
                    "Data de Entrada na Creche",
                    value=datetime.now().date()
                )
                
                # Definir data prevista de saída (geralmente 42 dias após entrada)
                data_saida_prevista = st.date_input(
                    "Data Prevista de Saída",
                    value=data_entrada + timedelta(days=42)
                )
                
                # Selecionar baia
                if not pens_df.empty:
                    creche_pens = pens_df[pens_df['setor'] == 'Creche']
                    
                    if creche_pens.empty:
                        st.error("Não há baias de creche cadastradas. Por favor, cadastre uma baia no setor 'Creche' primeiro.")
                        id_baia = None
                    else:
                        available_pens = get_available_pens(creche_pens, pen_allocations_df, 'Leitão')
                        
                        if available_pens.empty:
                            st.error("Não há baias de creche disponíveis no momento.")
                            id_baia = None
                        else:
                            id_baia = st.selectbox(
                                "Baia de Destino",
                                options=available_pens['id_baia'].tolist(),
                                format_func=lambda x: f"{available_pens[available_pens['id_baia'] == x]['identificacao'].iloc[0]} ({available_pens[available_pens['id_baia'] == x]['ocupacao_atual'].iloc[0]}/{available_pens[available_pens['id_baia'] == x]['capacidade'].iloc[0]} ocupada)"
                            )
                else:
                    st.error("Não há baias cadastradas. Por favor, cadastre baias primeiro.")
                    id_baia = None
                
                observacao = st.text_area(
                    "Observações",
                    placeholder=f"Informações adicionais sobre o lote de {origem_lote}..."
                )
            
            submit_button = st.form_submit_button("Registrar Novo Lote")
            
            if submit_button:
                if id_baia is None:
                    st.error("É necessário selecionar uma baia válida para continuar.")
                else:
                    # 1. Criar registro de creche
                    id_creche = str(uuid.uuid4())
                    
                    nova_creche = {
                        'id_creche': id_creche,
                        'id_baia': id_baia,
                        'data_inicio': data_entrada.strftime('%Y-%m-%d'),
                        'data_fim_prevista': data_saida_prevista.strftime('%Y-%m-%d'),
                        'data_fim_real': None,
                        'status': 'Ativo',
                        'observacao': observacao
                    }
                    
                    # Adicionar ao DataFrame
                    if nursery_df.empty:
                        nursery_df = pd.DataFrame([nova_creche])
                    else:
                        nursery_df = pd.concat([nursery_df, pd.DataFrame([nova_creche])], ignore_index=True)
                    
                    # Salvar DataFrame atualizado
                    save_nursery(nursery_df)
                    
                    # 2. Criar registro de lote
                    id_lote = str(uuid.uuid4())
                    
                    novo_lote = {
                        'id_lote': id_lote,
                        'id_creche': id_creche,
                        'id_desmame': None,
                        'identificacao': identificacao_lote,
                        'quantidade_inicial': quantidade_inicial,
                        'quantidade_atual': quantidade_inicial,
                        'peso_medio_entrada': peso_medio_entrada,
                        'idade_media_entrada': idade_media_entrada,
                        'peso_medio_atual': peso_medio_entrada,
                        'mortalidade': 0.0,
                        'origem': origem_lote,
                        'data_entrada': data_entrada.strftime('%Y-%m-%d'),
                        'data_saida': None,
                        'destino': None,
                        'status': 'Ativo',
                        'observacao': observacao
                    }
                    
                    # Adicionar ao DataFrame
                    if nursery_batches_df.empty:
                        nursery_batches_df = pd.DataFrame([novo_lote])
                    else:
                        nursery_batches_df = pd.concat([nursery_batches_df, pd.DataFrame([novo_lote])], ignore_index=True)
                    
                    # Salvar DataFrame atualizado
                    save_nursery_batches(nursery_batches_df)
                    
                    # 3. Criar primeira movimentação (entrada)
                    id_movimentacao = str(uuid.uuid4())
                    
                    nova_movimentacao = {
                        'id_movimentacao': id_movimentacao,
                        'id_lote': id_lote,
                        'tipo': 'Entrada',
                        'data': data_entrada.strftime('%Y-%m-%d'),
                        'quantidade': quantidade_inicial,
                        'peso_total': quantidade_inicial * peso_medio_entrada,
                        'peso_medio': peso_medio_entrada,
                        'ganho_diario': 0,
                        'causa': None,
                        'destino': None,
                        'medicamento': None,
                        'dosagem': None,
                        'via_aplicacao': None,
                        'responsavel': 'Sistema',
                        'observacao': f"Entrada na creche via {origem_lote}"
                    }
                    
                    # Adicionar ao DataFrame
                    if nursery_movements_df.empty:
                        nursery_movements_df = pd.DataFrame([nova_movimentacao])
                    else:
                        nursery_movements_df = pd.concat([nursery_movements_df, pd.DataFrame([nova_movimentacao])], ignore_index=True)
                    
                    # Salvar DataFrame atualizado
                    save_nursery_movements(nursery_movements_df)
                    
                    # 4. Criar alocação de baia para o lote
                    nova_alocacao = {
                        'id_alocacao': str(uuid.uuid4()),
                        'id_baia': id_baia,
                        'id_animal': None,  # Não é um animal específico, é um lote
                        'data_entrada': data_entrada.strftime('%Y-%m-%d'),
                        'data_saida': None,
                        'motivo_saida': None,
                        'status': 'Ativo',
                        'observacao': f"Lote de {quantidade_inicial} leitões - {origem_lote} - Lote ID: {id_lote}"
                    }
                    
                    # Adicionar ao DataFrame de alocações
                    if pen_allocations_df.empty:
                        pen_allocations_df = pd.DataFrame([nova_alocacao])
                    else:
                        pen_allocations_df = pd.concat([pen_allocations_df, pd.DataFrame([nova_alocacao])], ignore_index=True)
                    
                    # Salvar DataFrame atualizado
                    save_pen_allocations(pen_allocations_df)
                    
                    st.success("Lote registrado com sucesso!")
                    st.rerun()

with tab3:
    st.header("Registro de Eventos na Creche")
    
    # Verificar se há lotes ativos
    lotes_ativos = get_active_nursery_batches(nursery_batches_df)
    
    if lotes_ativos.empty:
        st.info("Não há lotes ativos na creche no momento. Utilize a aba 'Novo Lote' para iniciar um novo lote.")
    else:
        # Selecionar o lote
        lote_id = st.selectbox(
            "Selecione o Lote",
            options=lotes_ativos['id_lote'].tolist(),
            format_func=lambda x: f"{lotes_ativos[lotes_ativos['id_lote'] == x]['identificacao'].iloc[0]} - {int(lotes_ativos[lotes_ativos['id_lote'] == x]['quantidade_atual'].iloc[0])} leitões"
        )
        
        # Obter dados do lote selecionado
        lote_data = lotes_ativos[lotes_ativos['id_lote'] == lote_id].iloc[0]
        
        # Exibir informações básicas do lote
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Identificação", lote_data['identificacao'])
            
        with col2:
            st.metric("Leitões Atuais", int(lote_data['quantidade_atual']))
            
        with col3:
            st.metric("Peso Médio (kg)", f"{lote_data['peso_medio_atual']:.2f}")
            
        with col4:
            # Calcular dias na creche
            if pd.notna(lote_data['data_entrada']):
                data_entrada = pd.to_datetime(lote_data['data_entrada']).date()
                dias_creche = (datetime.now().date() - data_entrada).days
            else:
                dias_creche = 0
            
            st.metric("Dias na Creche", dias_creche)
        
        # Selecionar tipo de evento
        evento_options = ["Pesagem", "Mortalidade", "Medicação", "Transferência", "Saída", "Outro"]
        tipo_evento = st.selectbox("Tipo de Evento", evento_options)
        
        # Formulário específico para cada tipo de evento
        if tipo_evento == "Pesagem":
            with st.form("pesagem_form"):
                st.subheader("Registro de Pesagem")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    data_pesagem = st.date_input(
                        "Data da Pesagem",
                        value=datetime.now().date()
                    )
                    
                    amostragem = st.radio(
                        "Método de Pesagem",
                        options=["Pesagem Total", "Amostragem"]
                    )
                    
                    if amostragem == "Amostragem":
                        tamanho_amostra = st.number_input(
                            "Tamanho da Amostra",
                            min_value=1,
                            max_value=int(lote_data['quantidade_atual']),
                            value=min(10, int(lote_data['quantidade_atual']))
                        )
                    else:
                        tamanho_amostra = int(lote_data['quantidade_atual'])
                
                with col2:
                    peso_total = st.number_input(
                        "Peso Total da Amostra (kg)",
                        min_value=0.1,
                        value=float(tamanho_amostra * lote_data['peso_medio_atual']),
                        step=0.1,
                        format="%.1f"
                    )
                    
                    # Calcular peso médio
                    peso_medio = peso_total / tamanho_amostra if tamanho_amostra > 0 else 0
                    st.metric("Peso Médio Calculado (kg)", f"{peso_medio:.2f}")
                    
                    # Calcular ganho diário desde a última pesagem ou entrada
                    ultima_pesagem = None
                    if not nursery_movements_df.empty:
                        pesagens = nursery_movements_df[(nursery_movements_df['id_lote'] == lote_id) & 
                                                        (nursery_movements_df['tipo'].isin(['Pesagem', 'Entrada']))].sort_values('data', ascending=False)
                        
                        if not pesagens.empty:
                            ultima_pesagem = pesagens.iloc[0]
                    
                    if ultima_pesagem is not None:
                        ultimo_peso = ultima_pesagem['peso_medio']
                        data_ultima = pd.to_datetime(ultima_pesagem['data']).date()
                        dias_desde_ultima = (data_pesagem - data_ultima).days
                        
                        if dias_desde_ultima > 0:
                            ganho_diario = ((peso_medio - ultimo_peso) * 1000) / dias_desde_ultima  # em gramas por dia
                        else:
                            ganho_diario = 0
                    else:
                        # Usar peso de entrada como referência
                        ultimo_peso = lote_data['peso_medio_entrada']
                        data_entrada = pd.to_datetime(lote_data['data_entrada']).date()
                        dias_desde_entrada = (data_pesagem - data_entrada).days
                        
                        if dias_desde_entrada > 0:
                            ganho_diario = ((peso_medio - ultimo_peso) * 1000) / dias_desde_entrada  # em gramas por dia
                        else:
                            ganho_diario = 0
                    
                    st.metric("Ganho Médio Diário (g/dia)", f"{ganho_diario:.0f}")
                    
                    responsavel = st.text_input(
                        "Responsável pela Pesagem",
                        value="Operador"
                    )
                    
                    observacao = st.text_area(
                        "Observações",
                        placeholder="Informações adicionais sobre a pesagem..."
                    )
                
                submit_button = st.form_submit_button("Registrar Pesagem")
                
                if submit_button:
                    # Registrar evento de pesagem
                    id_movimentacao = str(uuid.uuid4())
                    
                    nova_movimentacao = {
                        'id_movimentacao': id_movimentacao,
                        'id_lote': lote_id,
                        'tipo': 'Pesagem',
                        'data': data_pesagem.strftime('%Y-%m-%d'),
                        'quantidade': tamanho_amostra,
                        'peso_total': peso_total,
                        'peso_medio': peso_medio,
                        'ganho_diario': ganho_diario,
                        'causa': None,
                        'destino': None,
                        'medicamento': None,
                        'dosagem': None,
                        'via_aplicacao': None,
                        'responsavel': responsavel,
                        'observacao': f"{'Pesagem por amostragem' if amostragem == 'Amostragem' else 'Pesagem total'}{': ' + observacao if observacao else ''}"
                    }
                    
                    # Adicionar ao DataFrame
                    if nursery_movements_df.empty:
                        nursery_movements_df = pd.DataFrame([nova_movimentacao])
                    else:
                        nursery_movements_df = pd.concat([nursery_movements_df, pd.DataFrame([nova_movimentacao])], ignore_index=True)
                    
                    # Salvar DataFrame atualizado
                    save_nursery_movements(nursery_movements_df)
                    
                    # Atualizar peso médio atual do lote
                    nursery_batches_df.loc[nursery_batches_df['id_lote'] == lote_id, 'peso_medio_atual'] = peso_medio
                    
                    # Salvar DataFrame atualizado
                    save_nursery_batches(nursery_batches_df)
                    
                    st.success("Pesagem registrada com sucesso!")
                    st.rerun()
        
        elif tipo_evento == "Mortalidade":
            with st.form("mortalidade_form"):
                st.subheader("Registro de Mortalidade")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    data_mortalidade = st.date_input(
                        "Data da Ocorrência",
                        value=datetime.now().date()
                    )
                    
                    quantidade = st.number_input(
                        "Quantidade de Animais",
                        min_value=1,
                        max_value=int(lote_data['quantidade_atual']),
                        value=1
                    )
                    
                    causa_options = [
                        "Diarreia", "Problemas Respiratórios", "Esmagamento", 
                        "Anemia", "Subnutrição", "Má Formação", "Doença Infecciosa",
                        "Artrite", "Desconhecida", "Outro"
                    ]
                    causa = st.selectbox("Causa da Morte", causa_options)
                    
                    if causa == "Outro":
                        outra_causa = st.text_input("Especifique a Causa")
                        causa_final = outra_causa
                    else:
                        causa_final = causa
                
                with col2:
                    peso_medio_mortos = st.number_input(
                        "Peso Médio Estimado (kg)",
                        min_value=0.1,
                        value=lote_data['peso_medio_atual'],
                        step=0.1,
                        format="%.1f"
                    )
                    
                    responsavel = st.text_input(
                        "Responsável pelo Registro",
                        value="Operador"
                    )
                    
                    observacao = st.text_area(
                        "Observações",
                        placeholder="Informações adicionais sobre a mortalidade..."
                    )
                
                submit_button = st.form_submit_button("Registrar Mortalidade")
                
                if submit_button:
                    # Registrar evento de mortalidade
                    id_movimentacao = str(uuid.uuid4())
                    
                    nova_movimentacao = {
                        'id_movimentacao': id_movimentacao,
                        'id_lote': lote_id,
                        'tipo': 'Mortalidade',
                        'data': data_mortalidade.strftime('%Y-%m-%d'),
                        'quantidade': quantidade,
                        'peso_total': quantidade * peso_medio_mortos,
                        'peso_medio': peso_medio_mortos,
                        'ganho_diario': None,
                        'causa': causa_final,
                        'destino': None,
                        'medicamento': None,
                        'dosagem': None,
                        'via_aplicacao': None,
                        'responsavel': responsavel,
                        'observacao': observacao
                    }
                    
                    # Adicionar ao DataFrame
                    if nursery_movements_df.empty:
                        nursery_movements_df = pd.DataFrame([nova_movimentacao])
                    else:
                        nursery_movements_df = pd.concat([nursery_movements_df, pd.DataFrame([nova_movimentacao])], ignore_index=True)
                    
                    # Salvar DataFrame atualizado
                    save_nursery_movements(nursery_movements_df)
                    
                    # Atualizar quantidade atual do lote
                    nova_quantidade = lote_data['quantidade_atual'] - quantidade
                    nursery_batches_df.loc[nursery_batches_df['id_lote'] == lote_id, 'quantidade_atual'] = nova_quantidade
                    
                    # Calcular nova taxa de mortalidade
                    mortalidade_total = lote_data['quantidade_inicial'] - nova_quantidade
                    nova_mortalidade = (mortalidade_total / lote_data['quantidade_inicial']) * 100
                    nursery_batches_df.loc[nursery_batches_df['id_lote'] == lote_id, 'mortalidade'] = nova_mortalidade
                    
                    # Salvar DataFrame atualizado
                    save_nursery_batches(nursery_batches_df)
                    
                    st.success("Mortalidade registrada com sucesso!")
                    st.rerun()
        
        elif tipo_evento == "Medicação":
            with st.form("medicacao_form"):
                st.subheader("Registro de Medicação")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    data_medicacao = st.date_input(
                        "Data da Aplicação",
                        value=datetime.now().date()
                    )
                    
                    medicamento = st.text_input(
                        "Medicamento",
                        placeholder="Nome do medicamento..."
                    )
                    
                    dosagem = st.text_input(
                        "Dosagem",
                        placeholder="Ex: 2 ml/animal, 5 mg/kg..."
                    )
                    
                    via_options = [
                        "Água", "Ração", "Injetável", "Oral", "Tópica", "Outra"
                    ]
                    via = st.selectbox("Via de Aplicação", via_options)
                    
                    if via == "Outra":
                        outra_via = st.text_input("Especifique a Via")
                        via_final = outra_via
                    else:
                        via_final = via
                
                with col2:
                    quantidade = st.number_input(
                        "Quantidade de Animais Tratados",
                        min_value=1,
                        max_value=int(lote_data['quantidade_atual']),
                        value=int(lote_data['quantidade_atual'])
                    )
                    
                    causa_options = [
                        "Preventivo", "Diarreia", "Problemas Respiratórios", 
                        "Febre", "Artrite", "Doença Infecciosa", "Parasitas",
                        "Outro"
                    ]
                    causa = st.selectbox("Motivo do Tratamento", causa_options)
                    
                    if causa == "Outro":
                        outra_causa = st.text_input("Especifique o Motivo")
                        causa_final = outra_causa
                    else:
                        causa_final = causa
                    
                    responsavel = st.text_input(
                        "Responsável pela Aplicação",
                        value="Operador"
                    )
                    
                    observacao = st.text_area(
                        "Observações",
                        placeholder="Informações adicionais sobre a medicação..."
                    )
                
                submit_button = st.form_submit_button("Registrar Medicação")
                
                if submit_button:
                    # Validação de campos obrigatórios
                    if not medicamento:
                        st.error("O campo Medicamento é obrigatório.")
                    elif not dosagem:
                        st.error("O campo Dosagem é obrigatório.")
                    else:
                        # Registrar evento de medicação
                        id_movimentacao = str(uuid.uuid4())
                        
                        nova_movimentacao = {
                            'id_movimentacao': id_movimentacao,
                            'id_lote': lote_id,
                            'tipo': 'Medicação',
                            'data': data_medicacao.strftime('%Y-%m-%d'),
                            'quantidade': quantidade,
                            'peso_total': None,
                            'peso_medio': None,
                            'ganho_diario': None,
                            'causa': causa_final,
                            'destino': None,
                            'medicamento': medicamento,
                            'dosagem': dosagem,
                            'via_aplicacao': via_final,
                            'responsavel': responsavel,
                            'observacao': observacao
                        }
                        
                        # Adicionar ao DataFrame
                        if nursery_movements_df.empty:
                            nursery_movements_df = pd.DataFrame([nova_movimentacao])
                        else:
                            nursery_movements_df = pd.concat([nursery_movements_df, pd.DataFrame([nova_movimentacao])], ignore_index=True)
                        
                        # Salvar DataFrame atualizado
                        save_nursery_movements(nursery_movements_df)
                        
                        st.success("Medicação registrada com sucesso!")
                        st.rerun()
        
        elif tipo_evento == "Transferência":
            with st.form("transferencia_form"):
                st.subheader("Registro de Transferência")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    data_transferencia = st.date_input(
                        "Data da Transferência",
                        value=datetime.now().date()
                    )
                    
                    quantidade = st.number_input(
                        "Quantidade de Animais",
                        min_value=1,
                        max_value=int(lote_data['quantidade_atual']),
                        value=int(lote_data['quantidade_atual'])
                    )
                    
                    peso_medio_transferencia = st.number_input(
                        "Peso Médio (kg)",
                        min_value=0.1,
                        value=lote_data['peso_medio_atual'],
                        step=0.1,
                        format="%.1f"
                    )
                
                with col2:
                    destino_options = [
                        "Crescimento", "Terminação", "Outra Granja", "Venda", "Outro"
                    ]
                    destino = st.selectbox("Destino dos Animais", destino_options)
                    
                    if destino == "Outro":
                        outro_destino = st.text_input("Especifique o Destino")
                        destino_final = outro_destino
                    else:
                        destino_final = destino
                    
                    responsavel = st.text_input(
                        "Responsável pela Transferência",
                        value="Operador"
                    )
                    
                    observacao = st.text_area(
                        "Observações",
                        placeholder="Informações adicionais sobre a transferência..."
                    )
                
                submit_button = st.form_submit_button("Registrar Transferência")
                
                if submit_button:
                    # Registrar evento de transferência
                    id_movimentacao = str(uuid.uuid4())
                    
                    nova_movimentacao = {
                        'id_movimentacao': id_movimentacao,
                        'id_lote': lote_id,
                        'tipo': 'Transferência',
                        'data': data_transferencia.strftime('%Y-%m-%d'),
                        'quantidade': quantidade,
                        'peso_total': quantidade * peso_medio_transferencia,
                        'peso_medio': peso_medio_transferencia,
                        'ganho_diario': None,
                        'causa': None,
                        'destino': destino_final,
                        'medicamento': None,
                        'dosagem': None,
                        'via_aplicacao': None,
                        'responsavel': responsavel,
                        'observacao': observacao
                    }
                    
                    # Adicionar ao DataFrame
                    if nursery_movements_df.empty:
                        nursery_movements_df = pd.DataFrame([nova_movimentacao])
                    else:
                        nursery_movements_df = pd.concat([nursery_movements_df, pd.DataFrame([nova_movimentacao])], ignore_index=True)
                    
                    # Salvar DataFrame atualizado
                    save_nursery_movements(nursery_movements_df)
                    
                    # Atualizar quantidade atual do lote
                    nova_quantidade = lote_data['quantidade_atual'] - quantidade
                    nursery_batches_df.loc[nursery_batches_df['id_lote'] == lote_id, 'quantidade_atual'] = nova_quantidade
                    
                    # Se transferiu todos os animais, finalizar o lote
                    if nova_quantidade == 0:
                        nursery_batches_df.loc[nursery_batches_df['id_lote'] == lote_id, 'status'] = 'Finalizado'
                        nursery_batches_df.loc[nursery_batches_df['id_lote'] == lote_id, 'data_saida'] = data_transferencia.strftime('%Y-%m-%d')
                        nursery_batches_df.loc[nursery_batches_df['id_lote'] == lote_id, 'destino'] = destino_final
                        
                        # Finalizar período de creche
                        id_creche = lote_data['id_creche']
                        if not nursery_df.empty and id_creche in nursery_df['id_creche'].values:
                            nursery_df.loc[nursery_df['id_creche'] == id_creche, 'data_fim_real'] = data_transferencia.strftime('%Y-%m-%d')
                            nursery_df.loc[nursery_df['id_creche'] == id_creche, 'status'] = 'Finalizado'
                            save_nursery(nursery_df)
                        
                        # Finalizar alocação de baia
                        if not pen_allocations_df.empty:
                            pen_allocations = pen_allocations_df[
                                (pen_allocations_df['observacao'].str.contains(f"Lote ID: {lote_id}", na=False)) &
                                (pen_allocations_df['data_saida'].isna())
                            ]
                            
                            if not pen_allocations.empty:
                                for idx in pen_allocations.index:
                                    pen_allocations_df.loc[idx, 'data_saida'] = data_transferencia.strftime('%Y-%m-%d')
                                    pen_allocations_df.loc[idx, 'motivo_saida'] = 'Transferência'
                                    pen_allocations_df.loc[idx, 'status'] = 'Inativo'
                                
                                save_pen_allocations(pen_allocations_df)
                    
                    # Salvar DataFrame atualizado
                    save_nursery_batches(nursery_batches_df)
                    
                    st.success("Transferência registrada com sucesso!")
                    st.rerun()
        
        elif tipo_evento == "Saída":
            with st.form("saida_form"):
                st.subheader("Registro de Saída da Creche")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    data_saida = st.date_input(
                        "Data da Saída",
                        value=datetime.now().date()
                    )
                    
                    destino_options = [
                        "Crescimento", "Terminação", "Outra Granja", "Venda", "Outro"
                    ]
                    destino = st.selectbox("Destino dos Animais", destino_options)
                    
                    if destino == "Outro":
                        outro_destino = st.text_input("Especifique o Destino")
                        destino_final = outro_destino
                    else:
                        destino_final = destino
                
                with col2:
                    peso_medio_saida = st.number_input(
                        "Peso Médio de Saída (kg)",
                        min_value=0.1,
                        value=lote_data['peso_medio_atual'],
                        step=0.1,
                        format="%.1f"
                    )
                    
                    responsavel = st.text_input(
                        "Responsável pela Saída",
                        value="Operador"
                    )
                    
                    observacao = st.text_area(
                        "Observações",
                        placeholder="Informações adicionais sobre a saída..."
                    )
                
                submit_button = st.form_submit_button("Registrar Saída")
                
                if submit_button:
                    # Registrar evento de saída
                    id_movimentacao = str(uuid.uuid4())
                    
                    nova_movimentacao = {
                        'id_movimentacao': id_movimentacao,
                        'id_lote': lote_id,
                        'tipo': 'Saída',
                        'data': data_saida.strftime('%Y-%m-%d'),
                        'quantidade': lote_data['quantidade_atual'],
                        'peso_total': lote_data['quantidade_atual'] * peso_medio_saida,
                        'peso_medio': peso_medio_saida,
                        'ganho_diario': None,
                        'causa': None,
                        'destino': destino_final,
                        'medicamento': None,
                        'dosagem': None,
                        'via_aplicacao': None,
                        'responsavel': responsavel,
                        'observacao': observacao
                    }
                    
                    # Adicionar ao DataFrame
                    if nursery_movements_df.empty:
                        nursery_movements_df = pd.DataFrame([nova_movimentacao])
                    else:
                        nursery_movements_df = pd.concat([nursery_movements_df, pd.DataFrame([nova_movimentacao])], ignore_index=True)
                    
                    # Salvar DataFrame atualizado
                    save_nursery_movements(nursery_movements_df)
                    
                    # Finalizar o lote
                    nursery_batches_df.loc[nursery_batches_df['id_lote'] == lote_id, 'status'] = 'Finalizado'
                    nursery_batches_df.loc[nursery_batches_df['id_lote'] == lote_id, 'data_saida'] = data_saida.strftime('%Y-%m-%d')
                    nursery_batches_df.loc[nursery_batches_df['id_lote'] == lote_id, 'destino'] = destino_final
                    nursery_batches_df.loc[nursery_batches_df['id_lote'] == lote_id, 'peso_medio_atual'] = peso_medio_saida
                    
                    # Finalizar período de creche
                    id_creche = lote_data['id_creche']
                    if not nursery_df.empty and id_creche in nursery_df['id_creche'].values:
                        nursery_df.loc[nursery_df['id_creche'] == id_creche, 'data_fim_real'] = data_saida.strftime('%Y-%m-%d')
                        nursery_df.loc[nursery_df['id_creche'] == id_creche, 'status'] = 'Finalizado'
                        save_nursery(nursery_df)
                    
                    # Finalizar alocação de baia
                    if not pen_allocations_df.empty:
                        pen_allocations = pen_allocations_df[
                            (pen_allocations_df['observacao'].str.contains(f"Lote ID: {lote_id}", na=False)) &
                            (pen_allocations_df['data_saida'].isna())
                        ]
                        
                        if not pen_allocations.empty:
                            for idx in pen_allocations.index:
                                pen_allocations_df.loc[idx, 'data_saida'] = data_saida.strftime('%Y-%m-%d')
                                pen_allocations_df.loc[idx, 'motivo_saida'] = f'Saída para {destino_final}'
                                pen_allocations_df.loc[idx, 'status'] = 'Inativo'
                            
                            save_pen_allocations(pen_allocations_df)
                    
                    # Salvar DataFrame atualizado
                    save_nursery_batches(nursery_batches_df)
                    
                    st.success("Saída registrada com sucesso!")
                    st.rerun()
        
        elif tipo_evento == "Outro":
            with st.form("outro_evento_form"):
                st.subheader("Registro de Outro Evento")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    data_evento = st.date_input(
                        "Data do Evento",
                        value=datetime.now().date()
                    )
                    
                    tipo_especifico = st.text_input(
                        "Tipo Específico do Evento",
                        placeholder="Ex: Vacinação, Manejo, Limpeza..."
                    )
                    
                    quantidade = st.number_input(
                        "Quantidade de Animais Afetados",
                        min_value=0,
                        max_value=int(lote_data['quantidade_atual']),
                        value=int(lote_data['quantidade_atual'])
                    )
                
                with col2:
                    responsavel = st.text_input(
                        "Responsável pelo Evento",
                        value="Operador"
                    )
                    
                    observacao = st.text_area(
                        "Observações",
                        placeholder="Descrição detalhada do evento...",
                        height=125
                    )
                
                submit_button = st.form_submit_button("Registrar Evento")
                
                if submit_button:
                    # Validação de campos obrigatórios
                    if not tipo_especifico:
                        st.error("O campo Tipo Específico do Evento é obrigatório.")
                    else:
                        # Registrar outro tipo de evento
                        id_movimentacao = str(uuid.uuid4())
                        
                        nova_movimentacao = {
                            'id_movimentacao': id_movimentacao,
                            'id_lote': lote_id,
                            'tipo': tipo_especifico,
                            'data': data_evento.strftime('%Y-%m-%d'),
                            'quantidade': quantidade,
                            'peso_total': None,
                            'peso_medio': None,
                            'ganho_diario': None,
                            'causa': None,
                            'destino': None,
                            'medicamento': None,
                            'dosagem': None,
                            'via_aplicacao': None,
                            'responsavel': responsavel,
                            'observacao': observacao
                        }
                        
                        # Adicionar ao DataFrame
                        if nursery_movements_df.empty:
                            nursery_movements_df = pd.DataFrame([nova_movimentacao])
                        else:
                            nursery_movements_df = pd.concat([nursery_movements_df, pd.DataFrame([nova_movimentacao])], ignore_index=True)
                        
                        # Salvar DataFrame atualizado
                        save_nursery_movements(nursery_movements_df)
                        
                        st.success("Evento registrado com sucesso!")
                        st.rerun()

with tab4:
    st.header("Relatórios e Análises da Creche")
    
    col1, col2 = st.columns(2)
    
    with col1:
        periodo = st.selectbox(
            "Selecione o Período",
            options=["Todos os Tempos", "Último Ano", "Últimos 6 Meses", "Últimos 3 Meses", "Último Mês"]
        )
    
    with col2:
        status = st.selectbox(
            "Status dos Lotes",
            options=["Todos", "Ativos", "Finalizados"]
        )
    
    # Filtrar dados com base nos parâmetros selecionados
    if not nursery_batches_df.empty:
        # Aplicar filtro de período
        filtered_df = nursery_batches_df.copy()
        filtered_df['data_entrada'] = pd.to_datetime(filtered_df['data_entrada'])
        
        today = datetime.now().date()
        
        if periodo == "Último Ano":
            cutoff_date = today - timedelta(days=365)
            filtered_df = filtered_df[filtered_df['data_entrada'].dt.date >= cutoff_date]
        elif periodo == "Últimos 6 Meses":
            cutoff_date = today - timedelta(days=180)
            filtered_df = filtered_df[filtered_df['data_entrada'].dt.date >= cutoff_date]
        elif periodo == "Últimos 3 Meses":
            cutoff_date = today - timedelta(days=90)
            filtered_df = filtered_df[filtered_df['data_entrada'].dt.date >= cutoff_date]
        elif periodo == "Último Mês":
            cutoff_date = today - timedelta(days=30)
            filtered_df = filtered_df[filtered_df['data_entrada'].dt.date >= cutoff_date]
        
        # Aplicar filtro de status
        if status == "Ativos":
            filtered_df = filtered_df[filtered_df['status'] == 'Ativo']
        elif status == "Finalizados":
            filtered_df = filtered_df[filtered_df['status'] == 'Finalizado']
        
        if filtered_df.empty:
            st.info(f"Não há dados para o período e status selecionados.")
        else:
            # Estatísticas gerais
            st.subheader("Estatísticas Gerais")
            
            col1, col2, col3, col4 = st.columns(4)
            
            # Total de lotes
            total_lotes = len(filtered_df)
            
            # Total de animais
            total_entrada = filtered_df['quantidade_inicial'].sum()
            
            # Animais finalizados
            if status in ["Todos", "Finalizados"] and 'quantidade_atual' in filtered_df.columns:
                lotes_finalizados = filtered_df[filtered_df['status'] == 'Finalizado']
                total_saida = lotes_finalizados['quantidade_inicial'].sum() - lotes_finalizados['quantidade_atual'].sum()
            else:
                total_saida = 0
            
            # Taxa média de mortalidade
            mortalidade_media = filtered_df['mortalidade'].mean() if 'mortalidade' in filtered_df.columns else 0
            
            with col1:
                st.metric("Total de Lotes", total_lotes)
                
            with col2:
                st.metric("Animais Entrada", int(total_entrada))
                
            with col3:
                st.metric("Animais Saída/Transferência", int(total_saida))
                
            with col4:
                st.metric("Mortalidade Média (%)", f"{mortalidade_media:.1f}")
            
            # Gráficos
            st.subheader("Análises de Desempenho")
            
            # Calcular dados para gráficos
            if not filtered_df.empty and not nursery_movements_df.empty:
                # Criar dataframes para análise
                
                # 1. Análise de peso por idade
                if 'status' in filtered_df.columns and len(filtered_df[filtered_df['status'] == 'Finalizado']) > 0:
                    lotes_finalizados = filtered_df[filtered_df['status'] == 'Finalizado'].copy()
                    
                    # Adicionar dados de pesagens e eventos importantes
                    pesagens_data = []
                    
                    for _, lote in lotes_finalizados.iterrows():
                        lote_id = lote['id_lote']
                        
                        # Obter movimentações de pesagem
                        lote_pesagens = nursery_movements_df[(nursery_movements_df['id_lote'] == lote_id) & 
                                                             (nursery_movements_df['tipo'] == 'Pesagem')].copy()
                        
                        # Adicionar pesagem inicial
                        entrada_data = {
                            'id_lote': lote_id,
                            'identificacao': lote['identificacao'],
                            'tipo': 'Entrada',
                            'data': lote['data_entrada'],
                            'peso_medio': lote['peso_medio_entrada'],
                            'idade': lote['idade_media_entrada']
                        }
                        pesagens_data.append(entrada_data)
                        
                        # Adicionar pesagens intermediárias
                        for _, pesagem in lote_pesagens.iterrows():
                            dias_creche = (pd.to_datetime(pesagem['data']) - pd.to_datetime(lote['data_entrada'])).days
                            idade = lote['idade_media_entrada'] + dias_creche
                            
                            pesagem_data = {
                                'id_lote': lote_id,
                                'identificacao': lote['identificacao'],
                                'tipo': 'Pesagem',
                                'data': pesagem['data'],
                                'peso_medio': pesagem['peso_medio'],
                                'idade': idade
                            }
                            pesagens_data.append(pesagem_data)
                        
                        # Adicionar pesagem de saída se houver
                        if pd.notna(lote['data_saida']):
                            saida_pesagens = nursery_movements_df[(nursery_movements_df['id_lote'] == lote_id) & 
                                                                 (nursery_movements_df['tipo'].isin(['Saída', 'Transferência']))]
                            
                            if not saida_pesagens.empty:
                                ultima_saida = saida_pesagens.iloc[0]
                                dias_creche = (pd.to_datetime(ultima_saida['data']) - pd.to_datetime(lote['data_entrada'])).days
                                idade = lote['idade_media_entrada'] + dias_creche
                                
                                saida_data = {
                                    'id_lote': lote_id,
                                    'identificacao': lote['identificacao'],
                                    'tipo': 'Saída',
                                    'data': ultima_saida['data'],
                                    'peso_medio': ultima_saida['peso_medio'],
                                    'idade': idade
                                }
                                pesagens_data.append(saida_data)
                    
                    if pesagens_data:
                        pesagens_df = pd.DataFrame(pesagens_data)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Gráfico de peso por idade
                            st.subheader("Curva de Crescimento")
                            
                            fig = px.scatter(
                                pesagens_df,
                                x='idade',
                                y='peso_medio',
                                color='identificacao',
                                size='peso_medio',
                                hover_name='identificacao',
                                trendline='lowess',
                                labels={
                                    'idade': 'Idade (dias)',
                                    'peso_medio': 'Peso Médio (kg)',
                                    'identificacao': 'Lote'
                                },
                                title="Peso x Idade em Diferentes Lotes"
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            # Gráfico de distribuição de mortalidade
                            st.subheader("Mortalidade por Lote")
                            
                            # Filtrar lotes com mortalidade
                            lotes_com_mortalidade = filtered_df[['identificacao', 'mortalidade']].copy()
                            
                            fig = px.bar(
                                lotes_com_mortalidade.sort_values('mortalidade', ascending=False),
                                x='identificacao',
                                y='mortalidade',
                                labels={
                                    'identificacao': 'Lote',
                                    'mortalidade': 'Mortalidade (%)'
                                },
                                title="Taxa de Mortalidade por Lote"
                            )
                            st.plotly_chart(fig, use_container_width=True)
                            
                        # Análise de ganho diário médio
                        st.subheader("Análise de Ganho Médio Diário")
                        
                        # Obter dados de GMD
                        ganhos_data = []
                        
                        for lote_id in filtered_df['id_lote']:
                            ganho_pesagens = nursery_movements_df[(nursery_movements_df['id_lote'] == lote_id) & 
                                                                (nursery_movements_df['tipo'] == 'Pesagem') &
                                                                (~nursery_movements_df['ganho_diario'].isna())]
                            
                            if not ganho_pesagens.empty:
                                lote_info = filtered_df[filtered_df['id_lote'] == lote_id].iloc[0]
                                
                                for _, pesagem in ganho_pesagens.iterrows():
                                    ganho_data = {
                                        'id_lote': lote_id,
                                        'identificacao': lote_info['identificacao'],
                                        'data': pesagem['data'],
                                        'ganho_diario': pesagem['ganho_diario']
                                    }
                                    ganhos_data.append(ganho_data)
                        
                        if ganhos_data:
                            ganhos_df = pd.DataFrame(ganhos_data)
                            ganhos_df['data'] = pd.to_datetime(ganhos_df['data'])
                            
                            fig = px.box(
                                ganhos_df,
                                x='identificacao',
                                y='ganho_diario',
                                labels={
                                    'identificacao': 'Lote',
                                    'ganho_diario': 'GMD (g/dia)'
                                },
                                title="Ganho Médio Diário (GMD) por Lote"
                            )
                            st.plotly_chart(fig, use_container_width=True)
                            
                    else:
                        st.info("Não há dados suficientes para gerar gráficos de crescimento.")
                else:
                    st.info("Não há lotes finalizados para análise no período selecionado.")
            
            # Tabela de lotes
            st.subheader("Lista de Lotes")
            
            # Preparar dados para exibição
            display_df = filtered_df[['identificacao', 'data_entrada', 'data_saida', 
                                      'quantidade_inicial', 'quantidade_atual', 
                                      'peso_medio_entrada', 'peso_medio_atual', 
                                      'mortalidade', 'status']].copy()
            
            # Formatar datas
            display_df['data_entrada'] = pd.to_datetime(display_df['data_entrada']).dt.strftime('%d/%m/%Y')
            display_df['data_saida'] = pd.to_datetime(display_df['data_saida']).dt.strftime('%d/%m/%Y')
            
            # Renomear colunas
            display_df = display_df.rename(columns={
                'identificacao': 'Identificação',
                'data_entrada': 'Data de Entrada',
                'data_saida': 'Data de Saída',
                'quantidade_inicial': 'Qtd. Inicial',
                'quantidade_atual': 'Qtd. Atual',
                'peso_medio_entrada': 'Peso Entrada (kg)',
                'peso_medio_atual': 'Peso Atual (kg)',
                'mortalidade': 'Mortalidade (%)',
                'status': 'Status'
            })
            
            st.dataframe(display_df.sort_values('Data de Entrada', ascending=False), hide_index=True)
            
            # Botão para exportar dados
            if st.button("Exportar Dados para CSV"):
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="Baixar Relatório",
                    data=csv,
                    file_name=f"relatorio_creche_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
    else:
        st.info("Não há dados de lotes de creche disponíveis. Utilize a aba 'Novo Lote' para criar lotes.")