import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from utils import (
    load_recria, save_recria,
    load_recria_lotes, save_recria_lotes,
    load_recria_pesagens, save_recria_pesagens,
    load_recria_transferencias, save_recria_transferencias,
    load_recria_alimentacao, save_recria_alimentacao,
    load_recria_medicacao, save_recria_medicacao,
    criar_lote_recria, adicionar_animal_recria,
    registrar_pesagem_recria, transferir_animal_recria,
    registrar_alimentacao_recria, registrar_medicacao_recria,
    finalizar_recria, finalizar_lote_recria,
    obter_lotes_recria_ativos, obter_animais_recria_ativos,
    calcular_estatisticas_recria, load_animals, load_pens
,
    check_permission
)

st.set_page_config(page_title="Sistema de Recria", page_icon="🐷", layout="wide")

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


# Verificar autenticação
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Você precisa estar autenticado para acessar esta página.")
    st.stop()

# Título e descrição
st.title("Sistema de Recria")
st.write("Gerenciamento de animais em recria")

# Inicializar variáveis de sessão se necessário
if "tab_recria" not in st.session_state:
    st.session_state.tab_recria = "Dashboard"

# Funções utilitárias
def formatar_data(data):
    """Formatar data para exibição"""
    if pd.isna(data) or data is None:
        return "-"
    return pd.to_datetime(data).strftime("%d/%m/%Y")

def formatar_numero(numero, decimais=2):
    """Formatar número para exibição"""
    if pd.isna(numero) or numero is None:
        return "-"
    return f"{float(numero):,.{decimais}f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Tabs para diferentes funcionalidades
tabs = st.tabs([
    "Dashboard", 
    "Lotes de Recria", 
    "Animais", 
    "Pesagens", 
    "Transferências", 
    "Alimentação",
    "Medicação"
])

# Dashboard
with tabs[0]:
    st.header("Dashboard de Recria")
    
    # Filtros 
    col1, col2, col3 = st.columns(3)
    with col1:
        lotes_df = obter_lotes_recria_ativos()
        lote_id = st.selectbox(
            "Filtrar por Lote:", 
            options=["Todos"] + list(lotes_df["id_lote"].unique() if not lotes_df.empty else []),
            format_func=lambda x: "Todos" if x == "Todos" else lotes_df[lotes_df["id_lote"] == x]["codigo"].iloc[0]
        )
        lote_id = None if lote_id == "Todos" else lote_id
        
    with col2:
        recria_df = load_recria()
        fases = ["Todas"] + list(recria_df["fase_recria"].unique() if not recria_df.empty else [])
        fase = st.selectbox("Filtrar por Fase:", options=fases)
        fase = None if fase == "Todas" else fase
        
    with col3:
        data_inicio = st.date_input("Data Inicial:", value=datetime.now() - timedelta(days=30))
        data_fim = st.date_input("Data Final:", value=datetime.now())
    
    # Calcular estatísticas
    try:
        stats = calcular_estatisticas_recria(
            id_lote=lote_id, 
            fase=fase, 
            periodo_inicio=data_inicio.strftime("%Y-%m-%d"),
            periodo_fim=data_fim.strftime("%Y-%m-%d")
        )
        
        # Métricas principais
        st.subheader("Métricas Principais")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total de Animais Ativos", stats.get('total_animais_ativos', 0))
        with col2:
            st.metric("Total de Lotes Ativos", stats.get('total_lotes_ativos', 0))
        with col3:
            st.metric("Peso Médio (kg)", formatar_numero(stats.get('peso_medio', 0)))
        with col4:
            st.metric("GPD Médio (g/dia)", formatar_numero(stats.get('gpd_medio', 0)))
        
        # Gráficos
        st.subheader("Análises")
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribuição de Pesos
            if stats.get('distribuicao_pesos'):
                pesos_df = pd.DataFrame({
                    'Faixa': list(stats['distribuicao_pesos'].keys()),
                    'Contagem': list(stats['distribuicao_pesos'].values())
                })
                fig = px.bar(
                    pesos_df, 
                    x='Faixa', 
                    y='Contagem',
                    title='Distribuição de Pesos',
                    labels={'Faixa': 'Faixa de Peso', 'Contagem': 'Quantidade de Animais'}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sem dados de pesagem disponíveis para exibir a distribuição de pesos.")
        
        with col2:
            # Consumo por tipo de ração
            if stats.get('consumo_por_tipo'):
                racao_df = pd.DataFrame({
                    'Tipo': list(stats['consumo_por_tipo'].keys()),
                    'Quantidade (kg)': list(stats['consumo_por_tipo'].values())
                })
                fig = px.pie(
                    racao_df, 
                    names='Tipo', 
                    values='Quantidade (kg)',
                    title='Consumo por Tipo de Ração'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sem dados de alimentação disponíveis para exibir o consumo por tipo de ração.")
        
        # Mais indicadores
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Indicadores de Alimentação")
            st.metric("Consumo Total (kg)", formatar_numero(stats.get('consumo_total', 0)))
            st.metric("Custo Total (R$)", formatar_numero(stats.get('custo_total_alimentacao', 0)))
            st.metric("Custo Médio por Animal (R$)", formatar_numero(stats.get('custo_medio_animal', 0)))
            
        with col2:
            st.subheader("Medicações")
            st.metric("Total de Medicações", stats.get('total_medicacoes', 0))
            st.metric("Medicações Individuais", stats.get('medicacoes_individuais', 0))
            st.metric("Medicações Coletivas", stats.get('medicacoes_coletivas', 0))
            
            # Medicações por motivo
            if stats.get('medicacoes_por_motivo'):
                st.write("Medicações por Motivo:")
                motivo_df = pd.DataFrame({
                    'Motivo': list(stats['medicacoes_por_motivo'].keys()),
                    'Quantidade': list(stats['medicacoes_por_motivo'].values())
                })
                st.dataframe(motivo_df, use_container_width=True)
    
    except Exception as e:
        st.error(f"Erro ao calcular estatísticas: {str(e)}")

# Lotes de Recria
with tabs[1]:
    st.header("Lotes de Recria")
    
    # Abas para gerenciar lotes
    lote_tabs = st.tabs(["Lotes Ativos", "Criar Novo Lote", "Finalizar Lote"])
    
    # Lotes Ativos
    with lote_tabs[0]:
        lotes_df = load_recria_lotes()
        
        if lotes_df.empty:
            st.info("Não há lotes de recria cadastrados.")
        else:
            # Filtrar apenas lotes ativos
            lotes_ativos = lotes_df[lotes_df['status'] == 'Ativo']
            
            if lotes_ativos.empty:
                st.info("Não há lotes de recria ativos.")
            else:
                # Exibir lotes ativos em uma tabela
                lotes_display = lotes_ativos[['id_lote', 'codigo', 'data_formacao', 'quantidade_inicial', 
                                             'peso_medio_inicial', 'idade_media', 'id_baia', 'responsavel']]
                
                # Formatar datas e números
                lotes_display['data_formacao'] = lotes_display['data_formacao'].apply(formatar_data)
                lotes_display['peso_medio_inicial'] = lotes_display['peso_medio_inicial'].apply(formatar_numero)
                
                # Renomear colunas para exibição
                lotes_display = lotes_display.rename(columns={
                    'id_lote': 'ID',
                    'codigo': 'Código',
                    'data_formacao': 'Data de Formação',
                    'quantidade_inicial': 'Quantidade',
                    'peso_medio_inicial': 'Peso Médio (kg)',
                    'idade_media': 'Idade Média (dias)',
                    'id_baia': 'Baia',
                    'responsavel': 'Responsável'
                })
                
                st.dataframe(lotes_display, use_container_width=True)
                
                # Detalhes do lote selecionado
                st.subheader("Detalhes do Lote")
                lote_id_selecionado = st.selectbox(
                    "Selecione um lote para ver detalhes:",
                    options=lotes_ativos['id_lote'].tolist(),
                    format_func=lambda x: lotes_ativos[lotes_ativos['id_lote'] == x]['codigo'].iloc[0]
                )
                
                if lote_id_selecionado:
                    lote = lotes_ativos[lotes_ativos['id_lote'] == lote_id_selecionado].iloc[0]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Código:** {lote['codigo']}")
                        st.write(f"**Data de Formação:** {formatar_data(lote['data_formacao'])}")
                        st.write(f"**Quantidade de Animais:** {int(lote['quantidade_inicial'])}")
                        st.write(f"**Idade Média:** {lote['idade_media']} dias")
                    
                    with col2:
                        st.write(f"**Peso Médio Inicial:** {formatar_numero(lote['peso_medio_inicial'])} kg")
                        st.write(f"**Baia:** {lote['id_baia']}")
                        st.write(f"**Responsável:** {lote['responsavel']}")
                        st.write(f"**Observação:** {lote['observacao'] if not pd.isna(lote['observacao']) else '-'}")
                    
                    # Animais no lote
                    st.subheader("Animais neste Lote")
                    recria_df = load_recria()
                    animais_lote = recria_df[
                        (recria_df['id_lote'] == lote_id_selecionado) & 
                        (recria_df['status'] == 'Ativo')
                    ]
                    
                    if animais_lote.empty:
                        st.info("Não há animais ativos neste lote.")
                    else:
                        # Exibir animais em uma tabela
                        animais_display = animais_lote[['id_animal', 'identificacao', 'data_entrada', 
                                                      'peso_entrada', 'fase_recria', 'origem']]
                        
                        # Formatar datas e números
                        animais_display['data_entrada'] = animais_display['data_entrada'].apply(formatar_data)
                        animais_display['peso_entrada'] = animais_display['peso_entrada'].apply(formatar_numero)
                        
                        # Renomear colunas para exibição
                        animais_display = animais_display.rename(columns={
                            'id_animal': 'ID',
                            'identificacao': 'Identificação',
                            'data_entrada': 'Data de Entrada',
                            'peso_entrada': 'Peso de Entrada (kg)',
                            'fase_recria': 'Fase',
                            'origem': 'Origem'
                        })
                        
                        st.dataframe(animais_display, use_container_width=True)
    
    # Criar Novo Lote
    with lote_tabs[1]:
        st.subheader("Criar Novo Lote de Recria")
        
        with st.form("form_novo_lote"):
            col1, col2 = st.columns(2)
            
            with col1:
                codigo = st.text_input("Código do Lote", help="Um código único para identificar o lote")
                data_formacao = st.date_input("Data de Formação", value=datetime.now())
                quantidade_inicial = st.number_input("Quantidade Inicial de Animais", min_value=1, value=10)
                idade_media = st.number_input("Idade Média (dias)", min_value=1, value=21)
            
            with col2:
                peso_medio_inicial = st.number_input("Peso Médio Inicial (kg)", min_value=0.1, value=6.0, step=0.1)
                
                # Carregar baias disponíveis
                pens_df = load_pens()
                if not pens_df.empty:
                    id_baia = st.selectbox(
                        "Baia", 
                        options=pens_df['id_baia'].tolist(),
                        format_func=lambda x: f"{pens_df[pens_df['id_baia'] == x]['codigo'].iloc[0]} - {pens_df[pens_df['id_baia'] == x]['descricao'].iloc[0]}"
                    )
                else:
                    id_baia = st.text_input("ID da Baia", help="Identificador da baia onde o lote está alojado")
                
                responsavel = st.text_input("Responsável", help="Nome do responsável pelo lote")
                observacao = st.text_area("Observação", help="Observações adicionais sobre o lote")
            
            submit_lote = st.form_submit_button("Criar Lote")
        
        if submit_lote:
            if not codigo or not responsavel:
                st.error("Código e Responsável são campos obrigatórios.")
            else:
                try:
                    sucesso, mensagem, lote_id = criar_lote_recria(
                        codigo=codigo,
                        data_formacao=data_formacao.strftime("%Y-%m-%d"),
                        quantidade_inicial=quantidade_inicial,
                        idade_media=idade_media,
                        peso_medio_inicial=peso_medio_inicial,
                        id_baia=id_baia,
                        responsavel=responsavel,
                        observacao=observacao
                    )
                    
                    if sucesso:
                        st.success(f"{mensagem} (ID: {lote_id})")
                        # Limpar formulário ou redirecionar
                    else:
                        st.error(mensagem)
                except Exception as e:
                    st.error(f"Erro ao criar lote: {str(e)}")
    
    # Finalizar Lote
    with lote_tabs[2]:
        st.subheader("Finalizar Lote de Recria")
        
        # Carregar lotes ativos
        lotes_df = load_recria_lotes()
        lotes_ativos = lotes_df[lotes_df['status'] == 'Ativo'] if not lotes_df.empty else pd.DataFrame()
        
        if lotes_ativos.empty:
            st.info("Não há lotes ativos para finalizar.")
        else:
            with st.form("form_finalizar_lote"):
                id_lote = st.selectbox(
                    "Selecione o Lote a Finalizar:",
                    options=lotes_ativos['id_lote'].tolist(),
                    format_func=lambda x: f"{lotes_ativos[lotes_ativos['id_lote'] == x]['codigo'].iloc[0]}"
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    data_encerramento = st.date_input("Data de Encerramento", value=datetime.now())
                    peso_medio_final = st.number_input("Peso Médio Final (kg)", min_value=0.1, value=25.0, step=0.1)
                
                with col2:
                    gpd = st.number_input("Ganho de Peso Diário (g/dia)", min_value=0, value=350)
                    ca = st.number_input("Conversão Alimentar", min_value=0.1, value=1.8, step=0.1)
                    observacao = st.text_area("Observação", help="Observações adicionais sobre o encerramento do lote")
                
                submit_finalizar = st.form_submit_button("Finalizar Lote")
            
            if submit_finalizar:
                try:
                    sucesso, mensagem = finalizar_lote_recria(
                        id_lote=id_lote,
                        data_encerramento=data_encerramento.strftime("%Y-%m-%d"),
                        peso_medio_final=peso_medio_final,
                        gpd=gpd,
                        ca=ca,
                        observacao=observacao
                    )
                    
                    if sucesso:
                        st.success(mensagem)
                        # Atualizar visualização ou redirecionar
                    else:
                        st.error(mensagem)
                except Exception as e:
                    st.error(f"Erro ao finalizar lote: {str(e)}")

# Animais
with tabs[2]:
    st.header("Animais em Recria")
    
    # Abas para gerenciar animais
    animal_tabs = st.tabs(["Animais Ativos", "Adicionar Animal", "Finalizar Recria"])
    
    # Animais Ativos
    with animal_tabs[0]:
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            lotes_df = obter_lotes_recria_ativos()
            lote_filtro = st.selectbox(
                "Filtrar por Lote:", 
                options=["Todos"] + list(lotes_df["id_lote"].unique() if not lotes_df.empty else []),
                format_func=lambda x: "Todos" if x == "Todos" else lotes_df[lotes_df["id_lote"] == x]["codigo"].iloc[0],
                key="animal_lote_filtro"
            )
            lote_id_filtro = None if lote_filtro == "Todos" else lote_filtro
        
        with col2:
            recria_df = load_recria()
            fases = ["Todas"] + list(recria_df["fase_recria"].unique() if not recria_df.empty else [])
            fase_filtro = st.selectbox("Filtrar por Fase:", options=fases, key="animal_fase_filtro")
            fase_id_filtro = None if fase_filtro == "Todas" else fase_filtro
        
        # Carregar animais
        animais_df = obter_animais_recria_ativos(id_lote=lote_id_filtro, fase=fase_id_filtro)
        
        if animais_df.empty:
            st.info("Não há animais em recria que correspondam aos filtros selecionados.")
        else:
            # Exibir animais em uma tabela
            animais_display = animais_df[['id_animal', 'identificacao', 'data_entrada', 
                                        'peso_entrada', 'fase_recria', 'origem', 'id_lote']]
            
            # Formatar datas e números
            animais_display['data_entrada'] = animais_display['data_entrada'].apply(formatar_data)
            animais_display['peso_entrada'] = animais_display['peso_entrada'].apply(formatar_numero)
            
            # Acrescentar código do lote
            if not lotes_df.empty:
                animais_display = pd.merge(
                    animais_display,
                    lotes_df[['id_lote', 'codigo']],
                    on='id_lote',
                    how='left'
                )
                animais_display = animais_display.rename(columns={'codigo': 'codigo_lote'})
            
            # Renomear colunas para exibição
            animais_display = animais_display.rename(columns={
                'id_animal': 'ID',
                'identificacao': 'Identificação',
                'data_entrada': 'Data de Entrada',
                'peso_entrada': 'Peso de Entrada (kg)',
                'fase_recria': 'Fase',
                'origem': 'Origem',
                'codigo_lote': 'Lote'
            })
            
            # Remover coluna id_lote da exibição
            if 'id_lote' in animais_display.columns:
                animais_display = animais_display.drop('id_lote', axis=1)
            
            st.dataframe(animais_display, use_container_width=True)
            
            # Detalhes do animal selecionado
            st.subheader("Detalhes do Animal")
            animal_id_selecionado = st.selectbox(
                "Selecione um animal para ver detalhes:",
                options=animais_df['id_animal'].tolist(),
                format_func=lambda x: animais_df[animais_df['id_animal'] == x]['identificacao'].iloc[0]
            )
            
            if animal_id_selecionado:
                animal = animais_df[animais_df['id_animal'] == animal_id_selecionado].iloc[0]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**ID:** {animal['id_animal']}")
                    st.write(f"**Identificação:** {animal['identificacao']}")
                    st.write(f"**Data de Entrada:** {formatar_data(animal['data_entrada'])}")
                    st.write(f"**Peso de Entrada:** {formatar_numero(animal['peso_entrada'])} kg")
                
                with col2:
                    st.write(f"**Fase:** {animal['fase_recria']}")
                    st.write(f"**Origem:** {animal['origem']}")
                    lote_codigo = lotes_df[lotes_df['id_lote'] == animal['id_lote']]['codigo'].iloc[0] if not lotes_df.empty else animal['id_lote']
                    st.write(f"**Lote:** {lote_codigo}")
                    st.write(f"**Observação:** {animal['observacao'] if not pd.isna(animal['observacao']) else '-'}")
                
                # Histórico de pesagens
                st.subheader("Histórico de Pesagens")
                pesagens_df = load_recria_pesagens()
                if not pesagens_df.empty:
                    pesagens_animal = pesagens_df[pesagens_df['id_animal'] == animal_id_selecionado].sort_values('data_pesagem', ascending=False)
                    
                    if pesagens_animal.empty:
                        st.info("Não há pesagens registradas para este animal.")
                    else:
                        # Exibir pesagens em uma tabela
                        pesagens_display = pesagens_animal[['data_pesagem', 'peso', 'ganho_desde_ultima', 'gpd_periodo', 'fase_recria']]
                        
                        # Formatar datas e números
                        pesagens_display['data_pesagem'] = pesagens_display['data_pesagem'].apply(formatar_data)
                        pesagens_display['peso'] = pesagens_display['peso'].apply(formatar_numero)
                        pesagens_display['ganho_desde_ultima'] = pesagens_display['ganho_desde_ultima'].apply(
                            lambda x: formatar_numero(x) if x is not None and not pd.isna(x) else "-"
                        )
                        pesagens_display['gpd_periodo'] = pesagens_display['gpd_periodo'].apply(
                            lambda x: formatar_numero(x) if x is not None and not pd.isna(x) else "-"
                        )
                        
                        # Renomear colunas para exibição
                        pesagens_display = pesagens_display.rename(columns={
                            'data_pesagem': 'Data',
                            'peso': 'Peso (kg)',
                            'ganho_desde_ultima': 'Ganho (kg)',
                            'gpd_periodo': 'GPD (g/dia)',
                            'fase_recria': 'Fase'
                        })
                        
                        st.dataframe(pesagens_display, use_container_width=True)
                        
                        # Gráfico de evolução do peso
                        pesagens_grafico = pesagens_animal.sort_values('data_pesagem')
                        if not pesagens_grafico.empty:
                            fig = px.line(
                                pesagens_grafico, 
                                x='data_pesagem', 
                                y='peso', 
                                title='Evolução do Peso',
                                labels={'data_pesagem': 'Data', 'peso': 'Peso (kg)'}
                            )
                            st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Não há pesagens registradas para este animal.")
    
    # Adicionar Animal
    with animal_tabs[1]:
        st.subheader("Adicionar Animal à Recria")
        
        with st.form("form_adicionar_animal"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Seleção de animal existente ou novo
                animals_df = load_animals()
                animal_option = st.radio(
                    "Tipo de Animal:",
                    options=["Animal Existente", "Novo Animal"],
                    horizontal=True
                )
                
                if animal_option == "Animal Existente" and not animals_df.empty:
                    id_animal = st.selectbox(
                        "Selecione o Animal:",
                        options=animals_df['id_animal'].tolist(),
                        format_func=lambda x: f"{animals_df[animals_df['id_animal'] == x]['identificacao'].iloc[0]} ({animals_df[animals_df['id_animal'] == x]['categoria'].iloc[0]})"
                    )
                    identificacao = animals_df[animals_df['id_animal'] == id_animal]['identificacao'].iloc[0]
                else:
                    id_animal = f"NEW_{str(uuid.uuid4())}"
                    identificacao = st.text_input("Identificação (Brinco)", help="Número do brinco ou identificação do animal")
                
                data_entrada = st.date_input("Data de Entrada", value=datetime.now())
                peso_entrada = st.number_input("Peso de Entrada (kg)", min_value=0.1, value=6.0, step=0.1)
            
            with col2:
                origem = st.selectbox(
                    "Origem", 
                    options=["Desmame", "Compra", "Transferência", "Outro"]
                )
                
                # Carregar lotes ativos
                lotes_df = obter_lotes_recria_ativos()
                if not lotes_df.empty:
                    id_lote = st.selectbox(
                        "Lote", 
                        options=lotes_df['id_lote'].tolist(),
                        format_func=lambda x: lotes_df[lotes_df['id_lote'] == x]['codigo'].iloc[0]
                    )
                else:
                    st.error("Não há lotes ativos disponíveis. Crie um lote antes de adicionar animais.")
                    id_lote = None
                
                fase_recria = st.selectbox(
                    "Fase de Recria", 
                    options=["Fase 1", "Fase 2", "Fase 3"]
                )
                
                observacao = st.text_area("Observação", help="Observações adicionais sobre o animal")
            
            submit_animal = st.form_submit_button("Adicionar Animal")
        
        if submit_animal:
            if not identificacao or not id_lote:
                st.error("Identificação e Lote são campos obrigatórios.")
            else:
                try:
                    sucesso, mensagem = adicionar_animal_recria(
                        id_animal=id_animal,
                        identificacao=identificacao,
                        data_entrada=data_entrada.strftime("%Y-%m-%d"),
                        peso_entrada=peso_entrada,
                        origem=origem,
                        id_lote=id_lote,
                        fase_recria=fase_recria,
                        observacao=observacao
                    )
                    
                    if sucesso:
                        st.success(mensagem)
                        # Limpar formulário ou redirecionar
                    else:
                        st.error(mensagem)
                except Exception as e:
                    st.error(f"Erro ao adicionar animal: {str(e)}")
    
    # Finalizar Recria
    with animal_tabs[2]:
        st.subheader("Finalizar Recria de Animal")
        
        # Carregar animais ativos
        animais_df = obter_animais_recria_ativos()
        
        if animais_df.empty:
            st.info("Não há animais ativos em recria para finalizar.")
        else:
            with st.form("form_finalizar_animal"):
                id_animal = st.selectbox(
                    "Selecione o Animal:",
                    options=animais_df['id_animal'].tolist(),
                    format_func=lambda x: f"{animais_df[animais_df['id_animal'] == x]['identificacao'].iloc[0]}"
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    data_saida = st.date_input("Data de Saída", value=datetime.now())
                    peso_saida = st.number_input("Peso de Saída (kg)", min_value=0.1, value=25.0, step=0.1)
                
                with col2:
                    destino = st.selectbox(
                        "Destino", 
                        options=["Terminação", "Reprodução", "Venda", "Abate", "Outro"]
                    )
                    observacao = st.text_area("Observação", help="Observações adicionais sobre a finalização")
                
                submit_finalizar = st.form_submit_button("Finalizar Recria")
            
            if submit_finalizar:
                try:
                    sucesso, mensagem = finalizar_recria(
                        id_animal=id_animal,
                        data_saida=data_saida.strftime("%Y-%m-%d"),
                        peso_saida=peso_saida,
                        destino=destino,
                        observacao=observacao
                    )
                    
                    if sucesso:
                        st.success(mensagem)
                        # Atualizar visualização ou redirecionar
                    else:
                        st.error(mensagem)
                except Exception as e:
                    st.error(f"Erro ao finalizar recria: {str(e)}")

# Pesagens
with tabs[3]:
    st.header("Pesagens")
    
    # Abas para gerenciar pesagens
    pesagem_tabs = st.tabs(["Histórico de Pesagens", "Registrar Pesagem"])
    
    # Histórico de Pesagens
    with pesagem_tabs[0]:
        # Filtros
        col1, col2, col3 = st.columns(3)
        with col1:
            lotes_df = obter_lotes_recria_ativos()
            lote_filtro = st.selectbox(
                "Filtrar por Lote:", 
                options=["Todos"] + list(lotes_df["id_lote"].unique() if not lotes_df.empty else []),
                format_func=lambda x: "Todos" if x == "Todos" else lotes_df[lotes_df["id_lote"] == x]["codigo"].iloc[0],
                key="pesagem_lote_filtro"
            )
        
        with col2:
            recria_df = load_recria()
            fases = ["Todas"] + list(recria_df["fase_recria"].unique() if not recria_df.empty else [])
            fase_filtro = st.selectbox("Filtrar por Fase:", options=fases, key="pesagem_fase_filtro")
        
        with col3:
            periodo = st.date_input(
                "Período:",
                value=(datetime.now() - timedelta(days=30), datetime.now()),
                key="pesagem_periodo"
            )
        
        # Carregar pesagens
        pesagens_df = load_recria_pesagens()
        
        if pesagens_df.empty:
            st.info("Não há pesagens registradas.")
        else:
            # Aplicar filtros
            if len(periodo) == 2:
                pesagens_df = pesagens_df[
                    (pd.to_datetime(pesagens_df['data_pesagem']) >= pd.to_datetime(periodo[0])) &
                    (pd.to_datetime(pesagens_df['data_pesagem']) <= pd.to_datetime(periodo[1]))
                ]
            
            if lote_filtro != "Todos":
                pesagens_df = pesagens_df[pesagens_df['id_lote'] == lote_filtro]
            
            if fase_filtro != "Todas":
                pesagens_df = pesagens_df[pesagens_df['fase_recria'] == fase_filtro]
            
            if pesagens_df.empty:
                st.info("Não há pesagens que correspondam aos filtros selecionados.")
            else:
                # Combinar com informações dos animais
                recria_df = load_recria()
                if not recria_df.empty:
                    pesagens_df = pd.merge(
                        pesagens_df,
                        recria_df[['id_animal', 'identificacao']],
                        on='id_animal',
                        how='left'
                    )
                
                # Combinar com informações dos lotes
                if not lotes_df.empty:
                    pesagens_df = pd.merge(
                        pesagens_df,
                        lotes_df[['id_lote', 'codigo']],
                        on='id_lote',
                        how='left'
                    )
                    pesagens_df = pesagens_df.rename(columns={'codigo': 'codigo_lote'})
                
                # Exibir pesagens em uma tabela
                pesagens_display = pesagens_df[['id_pesagem', 'identificacao', 'data_pesagem', 
                                             'peso', 'ganho_desde_ultima', 'gpd_periodo', 
                                             'fase_recria', 'codigo_lote', 'tipo_pesagem']]
                
                # Formatar datas e números
                pesagens_display['data_pesagem'] = pesagens_display['data_pesagem'].apply(formatar_data)
                pesagens_display['peso'] = pesagens_display['peso'].apply(formatar_numero)
                pesagens_display['ganho_desde_ultima'] = pesagens_display['ganho_desde_ultima'].apply(
                    lambda x: formatar_numero(x) if x is not None and not pd.isna(x) else "-"
                )
                pesagens_display['gpd_periodo'] = pesagens_display['gpd_periodo'].apply(
                    lambda x: formatar_numero(x) if x is not None and not pd.isna(x) else "-"
                )
                
                # Renomear colunas para exibição
                pesagens_display = pesagens_display.rename(columns={
                    'id_pesagem': 'ID',
                    'identificacao': 'Animal',
                    'data_pesagem': 'Data',
                    'peso': 'Peso (kg)',
                    'ganho_desde_ultima': 'Ganho (kg)',
                    'gpd_periodo': 'GPD (g/dia)',
                    'fase_recria': 'Fase',
                    'codigo_lote': 'Lote',
                    'tipo_pesagem': 'Tipo'
                })
                
                st.dataframe(pesagens_display, use_container_width=True)
                
                # Estatísticas das pesagens
                st.subheader("Estatísticas de Pesagens")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total de Pesagens", len(pesagens_df))
                
                with col2:
                    st.metric("Peso Médio (kg)", formatar_numero(pesagens_df['peso'].mean()))
                
                with col3:
                    st.metric("GPD Médio (g/dia)", 
                             formatar_numero(pesagens_df['gpd_periodo'].dropna().mean()))
                
                # Gráfico de evolução do peso
                st.subheader("Evolução do Peso Médio")
                
                # Agrupar pesagens por data
                pesagens_por_data = pesagens_df.groupby('data_pesagem')['peso'].mean().reset_index()
                pesagens_por_data = pesagens_por_data.sort_values('data_pesagem')
                
                if not pesagens_por_data.empty:
                    fig = px.line(
                        pesagens_por_data, 
                        x='data_pesagem', 
                        y='peso', 
                        title='Evolução do Peso Médio',
                        labels={'data_pesagem': 'Data', 'peso': 'Peso Médio (kg)'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
    
    # Registrar Pesagem
    with pesagem_tabs[1]:
        st.subheader("Registrar Nova Pesagem")
        
        # Escolher tipo de pesagem
        tipo_pesagem = st.radio(
            "Tipo de Pesagem:",
            options=["Individual", "Grupo"],
            horizontal=True
        )
        
        if tipo_pesagem == "Individual":
            with st.form("form_pesagem_individual"):
                col1, col2 = st.columns(2)
                
                with col1:
                    # Carregar animais ativos em recria
                    animais_df = obter_animais_recria_ativos()
                    
                    if animais_df.empty:
                        st.error("Não há animais ativos em recria para pesar.")
                        id_animal = None
                    else:
                        id_animal = st.selectbox(
                            "Selecione o Animal:",
                            options=animais_df['id_animal'].tolist(),
                            format_func=lambda x: f"{animais_df[animais_df['id_animal'] == x]['identificacao'].iloc[0]}"
                        )
                    
                    data_pesagem = st.date_input("Data da Pesagem", value=datetime.now())
                    peso = st.number_input("Peso (kg)", min_value=0.1, step=0.1)
                
                with col2:
                    # Se um animal for selecionado, pré-preencher o lote e a fase
                    if id_animal and not animais_df.empty:
                        animal_info = animais_df[animais_df['id_animal'] == id_animal].iloc[0]
                        id_lote = animal_info['id_lote']
                        fase_recria = animal_info['fase_recria']
                        
                        # Exibir informações do lote
                        lotes_df = load_recria_lotes()
                        if not lotes_df.empty and id_lote in lotes_df['id_lote'].values:
                            lote_info = lotes_df[lotes_df['id_lote'] == id_lote].iloc[0]
                            st.write(f"**Lote:** {lote_info['codigo']}")
                        else:
                            st.write(f"**Lote ID:** {id_lote}")
                        
                        st.write(f"**Fase Atual:** {fase_recria}")
                        
                        # Permitir alterar a fase
                        fase_recria = st.selectbox(
                            "Nova Fase de Recria (opcional)", 
                            options=["Manter Atual", "Fase 1", "Fase 2", "Fase 3"]
                        )
                        
                        if fase_recria == "Manter Atual":
                            fase_recria = animal_info['fase_recria']
                    else:
                        id_lote = None
                        fase_recria = st.selectbox(
                            "Fase de Recria", 
                            options=["Fase 1", "Fase 2", "Fase 3"]
                        )
                    
                    responsavel = st.text_input("Responsável pela Pesagem")
                    observacao = st.text_area("Observação", help="Observações adicionais sobre a pesagem")
                
                submit_pesagem = st.form_submit_button("Registrar Pesagem")
            
            if submit_pesagem:
                if not id_animal or not peso:
                    st.error("Animal e Peso são campos obrigatórios.")
                else:
                    try:
                        sucesso, mensagem = registrar_pesagem_recria(
                            id_animal=id_animal,
                            data_pesagem=data_pesagem.strftime("%Y-%m-%d"),
                            peso=peso,
                            tipo_pesagem="Individual",
                            fase_recria=fase_recria,
                            id_lote=id_lote,
                            responsavel=responsavel,
                            observacao=observacao
                        )
                        
                        if sucesso:
                            st.success(mensagem)
                            # Limpar formulário ou redirecionar
                        else:
                            st.error(mensagem)
                    except Exception as e:
                        st.error(f"Erro ao registrar pesagem: {str(e)}")
        
        else:  # Pesagem em Grupo
            with st.form("form_pesagem_grupo"):
                col1, col2 = st.columns(2)
                
                with col1:
                    # Carregar lotes ativos
                    lotes_df = obter_lotes_recria_ativos()
                    
                    if lotes_df.empty:
                        st.error("Não há lotes ativos para pesagem em grupo.")
                        id_lote = None
                    else:
                        id_lote = st.selectbox(
                            "Selecione o Lote:",
                            options=lotes_df['id_lote'].tolist(),
                            format_func=lambda x: lotes_df[lotes_df['id_lote'] == x]['codigo'].iloc[0]
                        )
                    
                    data_pesagem = st.date_input("Data da Pesagem", value=datetime.now(), key="pesagem_grupo_data")
                    peso_medio = st.number_input("Peso Médio do Grupo (kg)", min_value=0.1, step=0.1)
                
                with col2:
                    fase_recria = st.selectbox(
                        "Fase de Recria", 
                        options=["Fase 1", "Fase 2", "Fase 3"],
                        key="pesagem_grupo_fase"
                    )
                    
                    responsavel = st.text_input("Responsável pela Pesagem", key="pesagem_grupo_responsavel")
                    observacao = st.text_area("Observação", help="Observações adicionais sobre a pesagem em grupo", key="pesagem_grupo_obs")
                
                submit_pesagem_grupo = st.form_submit_button("Registrar Pesagem em Grupo")
            
            if submit_pesagem_grupo:
                if not id_lote or not peso_medio:
                    st.error("Lote e Peso Médio são campos obrigatórios.")
                else:
                    try:
                        sucesso, mensagem = registrar_pesagem_recria(
                            id_animal=None,  # Pesagem em grupo não tem animal específico
                            data_pesagem=data_pesagem.strftime("%Y-%m-%d"),
                            peso=peso_medio,
                            tipo_pesagem="Grupo",
                            fase_recria=fase_recria,
                            id_lote=id_lote,
                            responsavel=responsavel,
                            observacao=observacao
                        )
                        
                        if sucesso:
                            st.success(mensagem)
                            # Limpar formulário ou redirecionar
                        else:
                            st.error(mensagem)
                    except Exception as e:
                        st.error(f"Erro ao registrar pesagem em grupo: {str(e)}")

# Transferências
with tabs[4]:
    st.header("Transferências")
    
    # Abas para gerenciar transferências
    transferencia_tabs = st.tabs(["Histórico de Transferências", "Registrar Transferência"])
    
    # Histórico de Transferências
    with transferencia_tabs[0]:
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            periodo_transf = st.date_input(
                "Período:",
                value=(datetime.now() - timedelta(days=30), datetime.now()),
                key="transferencia_periodo"
            )
        
        with col2:
            lotes_df = obter_lotes_recria_ativos()
            lote_filtro_transf = st.selectbox(
                "Filtrar por Lote de Origem:", 
                options=["Todos"] + list(lotes_df["id_lote"].unique() if not lotes_df.empty else []),
                format_func=lambda x: "Todos" if x == "Todos" else lotes_df[lotes_df["id_lote"] == x]["codigo"].iloc[0],
                key="transferencia_lote_filtro"
            )
        
        # Carregar transferências
        transferencias_df = load_recria_transferencias()
        
        if transferencias_df.empty:
            st.info("Não há transferências registradas.")
        else:
            # Aplicar filtros
            if len(periodo_transf) == 2:
                transferencias_df = transferencias_df[
                    (pd.to_datetime(transferencias_df['data_transferencia']) >= pd.to_datetime(periodo_transf[0])) &
                    (pd.to_datetime(transferencias_df['data_transferencia']) <= pd.to_datetime(periodo_transf[1]))
                ]
            
            if lote_filtro_transf != "Todos":
                transferencias_df = transferencias_df[transferencias_df['id_lote_origem'] == lote_filtro_transf]
            
            if transferencias_df.empty:
                st.info("Não há transferências que correspondam aos filtros selecionados.")
            else:
                # Combinar com informações dos animais
                recria_df = load_recria()
                if not recria_df.empty:
                    transferencias_df = pd.merge(
                        transferencias_df,
                        recria_df[['id_animal', 'identificacao']],
                        on='id_animal',
                        how='left'
                    )
                
                # Combinar com informações dos lotes
                if not lotes_df.empty:
                    # Lote de origem
                    transferencias_df = pd.merge(
                        transferencias_df,
                        lotes_df[['id_lote', 'codigo']],
                        left_on='id_lote_origem',
                        right_on='id_lote',
                        how='left'
                    )
                    transferencias_df = transferencias_df.rename(columns={'codigo': 'lote_origem'})
                    transferencias_df = transferencias_df.drop('id_lote', axis=1)
                    
                    # Lote de destino
                    transferencias_df = pd.merge(
                        transferencias_df,
                        lotes_df[['id_lote', 'codigo']],
                        left_on='id_lote_destino',
                        right_on='id_lote',
                        how='left'
                    )
                    transferencias_df = transferencias_df.rename(columns={'codigo': 'lote_destino'})
                    transferencias_df = transferencias_df.drop('id_lote', axis=1)
                
                # Exibir transferências em uma tabela
                transferencias_display = transferencias_df[['id_transferencia', 'identificacao', 'data_transferencia',
                                                         'lote_origem', 'lote_destino', 'peso_transferencia',
                                                         'fase_origem', 'fase_destino', 'motivo']]
                
                # Formatar datas e números
                transferencias_display['data_transferencia'] = transferencias_display['data_transferencia'].apply(formatar_data)
                transferencias_display['peso_transferencia'] = transferencias_display['peso_transferencia'].apply(formatar_numero)
                
                # Renomear colunas para exibição
                transferencias_display = transferencias_display.rename(columns={
                    'id_transferencia': 'ID',
                    'identificacao': 'Animal',
                    'data_transferencia': 'Data',
                    'lote_origem': 'Lote Origem',
                    'lote_destino': 'Lote Destino',
                    'peso_transferencia': 'Peso (kg)',
                    'fase_origem': 'Fase Origem',
                    'fase_destino': 'Fase Destino',
                    'motivo': 'Motivo'
                })
                
                st.dataframe(transferencias_display, use_container_width=True)
    
    # Registrar Transferência
    with transferencia_tabs[1]:
        st.subheader("Registrar Nova Transferência")
        
        with st.form("form_transferencia"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Carregar animais ativos em recria
                animais_df = obter_animais_recria_ativos()
                
                if animais_df.empty:
                    st.error("Não há animais ativos em recria para transferir.")
                    id_animal = None
                else:
                    id_animal = st.selectbox(
                        "Selecione o Animal:",
                        options=animais_df['id_animal'].tolist(),
                        format_func=lambda x: f"{animais_df[animais_df['id_animal'] == x]['identificacao'].iloc[0]}"
                    )
                
                # Se um animal for selecionado, mostrar suas informações atuais
                if id_animal and not animais_df.empty:
                    animal_info = animais_df[animais_df['id_animal'] == id_animal].iloc[0]
                    id_lote_atual = animal_info['id_lote']
                    fase_atual = animal_info['fase_recria']
                    
                    # Exibir informações do lote atual
                    lotes_df = obter_lotes_recria_ativos()
                    if not lotes_df.empty and id_lote_atual in lotes_df['id_lote'].values:
                        lote_info = lotes_df[lotes_df['id_lote'] == id_lote_atual].iloc[0]
                        st.write(f"**Lote Atual:** {lote_info['codigo']}")
                        st.write(f"**Baia Atual:** {lote_info['id_baia']}")
                    else:
                        st.write(f"**Lote Atual ID:** {id_lote_atual}")
                    
                    st.write(f"**Fase Atual:** {fase_atual}")
                
                data_transferencia = st.date_input("Data da Transferência", value=datetime.now())
                peso_transferencia = st.number_input("Peso na Transferência (kg)", min_value=0.1, step=0.1)
            
            with col2:
                # Selecionar lote de destino
                lotes_df = obter_lotes_recria_ativos()
                
                if lotes_df.empty:
                    st.error("Não há lotes ativos para transferência.")
                    id_lote_destino = None
                else:
                    # Filtrar para não mostrar o lote atual do animal
                    if id_animal and not animais_df.empty:
                        lotes_disponiveis = lotes_df[lotes_df['id_lote'] != animal_info['id_lote']]
                        if lotes_disponiveis.empty:
                            st.error("Não há outros lotes disponíveis para transferência.")
                            id_lote_destino = None
                        else:
                            id_lote_destino = st.selectbox(
                                "Lote de Destino:",
                                options=lotes_disponiveis['id_lote'].tolist(),
                                format_func=lambda x: lotes_disponiveis[lotes_disponiveis['id_lote'] == x]['codigo'].iloc[0]
                            )
                    else:
                        id_lote_destino = st.selectbox(
                            "Lote de Destino:",
                            options=lotes_df['id_lote'].tolist(),
                            format_func=lambda x: lotes_df[lotes_df['id_lote'] == x]['codigo'].iloc[0]
                        )
                
                # Obter a baia do lote de destino
                if id_lote_destino and not lotes_df.empty:
                    id_baia_destino = lotes_df[lotes_df['id_lote'] == id_lote_destino]['id_baia'].iloc[0]
                    st.write(f"**Baia de Destino:** {id_baia_destino}")
                else:
                    id_baia_destino = st.text_input("ID da Baia de Destino", help="Identificador da baia de destino")
                
                fase_destino = st.selectbox(
                    "Fase de Destino", 
                    options=["Fase 1", "Fase 2", "Fase 3"]
                )
                
                motivo = st.selectbox(
                    "Motivo da Transferência", 
                    options=["Mudança de Fase", "Reagrupamento", "Problemas Sanitários", "Adequação de Espaço", "Outro"]
                )
                
                responsavel = st.text_input("Responsável pela Transferência")
                observacao = st.text_area("Observação", help="Observações adicionais sobre a transferência")
            
            submit_transferencia = st.form_submit_button("Registrar Transferência")
        
        if submit_transferencia:
            if not id_animal or not id_lote_destino or not id_baia_destino or not peso_transferencia:
                st.error("Animal, Lote de Destino, Baia de Destino e Peso são campos obrigatórios.")
            else:
                try:
                    sucesso, mensagem = transferir_animal_recria(
                        id_animal=id_animal,
                        id_lote_destino=id_lote_destino,
                        id_baia_destino=id_baia_destino,
                        data_transferencia=data_transferencia.strftime("%Y-%m-%d"),
                        motivo=motivo,
                        peso_transferencia=peso_transferencia,
                        fase_destino=fase_destino,
                        responsavel=responsavel,
                        observacao=observacao
                    )
                    
                    if sucesso:
                        st.success(mensagem)
                        # Limpar formulário ou redirecionar
                    else:
                        st.error(mensagem)
                except Exception as e:
                    st.error(f"Erro ao registrar transferência: {str(e)}")

# Alimentação
with tabs[5]:
    st.header("Alimentação")
    
    # Abas para gerenciar alimentação
    alimentacao_tabs = st.tabs(["Histórico de Alimentação", "Registrar Alimentação"])
    
    # Histórico de Alimentação
    with alimentacao_tabs[0]:
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            periodo_alim = st.date_input(
                "Período:",
                value=(datetime.now() - timedelta(days=30), datetime.now()),
                key="alimentacao_periodo"
            )
        
        with col2:
            lotes_df = obter_lotes_recria_ativos()
            lote_filtro_alim = st.selectbox(
                "Filtrar por Lote:", 
                options=["Todos"] + list(lotes_df["id_lote"].unique() if not lotes_df.empty else []),
                format_func=lambda x: "Todos" if x == "Todos" else lotes_df[lotes_df["id_lote"] == x]["codigo"].iloc[0],
                key="alimentacao_lote_filtro"
            )
        
        # Carregar registros de alimentação
        alimentacao_df = load_recria_alimentacao()
        
        if alimentacao_df.empty:
            st.info("Não há registros de alimentação.")
        else:
            # Aplicar filtros
            if len(periodo_alim) == 2:
                alimentacao_df = alimentacao_df[
                    (pd.to_datetime(alimentacao_df['data_inicio']) >= pd.to_datetime(periodo_alim[0])) &
                    (pd.to_datetime(alimentacao_df['data_fim']) <= pd.to_datetime(periodo_alim[1]))
                ]
            
            if lote_filtro_alim != "Todos":
                alimentacao_df = alimentacao_df[alimentacao_df['id_lote'] == lote_filtro_alim]
            
            if alimentacao_df.empty:
                st.info("Não há registros de alimentação que correspondam aos filtros selecionados.")
            else:
                # Combinar com informações dos lotes
                if not lotes_df.empty:
                    alimentacao_df = pd.merge(
                        alimentacao_df,
                        lotes_df[['id_lote', 'codigo']],
                        on='id_lote',
                        how='left'
                    )
                    alimentacao_df = alimentacao_df.rename(columns={'codigo': 'codigo_lote'})
                
                # Exibir registros de alimentação em uma tabela
                alimentacao_display = alimentacao_df[['id_alimentacao', 'codigo_lote', 'data_inicio', 'data_fim',
                                                   'tipo_racao', 'quantidade_kg', 'custo_kg', 'custo_total',
                                                   'consumo_animal_dia', 'fase_recria']]
                
                # Formatar datas e números
                alimentacao_display['data_inicio'] = alimentacao_display['data_inicio'].apply(formatar_data)
                alimentacao_display['data_fim'] = alimentacao_display['data_fim'].apply(formatar_data)
                alimentacao_display['quantidade_kg'] = alimentacao_display['quantidade_kg'].apply(formatar_numero)
                alimentacao_display['custo_kg'] = alimentacao_display['custo_kg'].apply(formatar_numero)
                alimentacao_display['custo_total'] = alimentacao_display['custo_total'].apply(formatar_numero)
                alimentacao_display['consumo_animal_dia'] = alimentacao_display['consumo_animal_dia'].apply(
                    lambda x: formatar_numero(x) if x is not None and not pd.isna(x) else "-"
                )
                
                # Renomear colunas para exibição
                alimentacao_display = alimentacao_display.rename(columns={
                    'id_alimentacao': 'ID',
                    'codigo_lote': 'Lote',
                    'data_inicio': 'Data Início',
                    'data_fim': 'Data Fim',
                    'tipo_racao': 'Tipo de Ração',
                    'quantidade_kg': 'Quantidade (kg)',
                    'custo_kg': 'Custo/kg (R$)',
                    'custo_total': 'Custo Total (R$)',
                    'consumo_animal_dia': 'Consumo/Animal/Dia (kg)',
                    'fase_recria': 'Fase'
                })
                
                st.dataframe(alimentacao_display, use_container_width=True)
                
                # Estatísticas de alimentação
                st.subheader("Estatísticas de Alimentação")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total de Registros", len(alimentacao_df))
                
                with col2:
                    st.metric("Quantidade Total (kg)", formatar_numero(alimentacao_df['quantidade_kg'].sum()))
                
                with col3:
                    st.metric("Custo Total (R$)", formatar_numero(alimentacao_df['custo_total'].sum()))
                
                # Gráfico de consumo por tipo de ração
                st.subheader("Consumo por Tipo de Ração")
                consumo_por_tipo = alimentacao_df.groupby('tipo_racao')['quantidade_kg'].sum().reset_index()
                
                if not consumo_por_tipo.empty:
                    fig = px.pie(
                        consumo_por_tipo, 
                        names='tipo_racao', 
                        values='quantidade_kg',
                        title='Consumo por Tipo de Ração (kg)'
                    )
                    st.plotly_chart(fig, use_container_width=True)
    
    # Registrar Alimentação
    with alimentacao_tabs[1]:
        st.subheader("Registrar Nova Alimentação")
        
        with st.form("form_alimentacao"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Carregar lotes ativos
                lotes_df = obter_lotes_recria_ativos()
                
                if lotes_df.empty:
                    st.error("Não há lotes ativos para registrar alimentação.")
                    id_lote = None
                else:
                    id_lote = st.selectbox(
                        "Lote:",
                        options=lotes_df['id_lote'].tolist(),
                        format_func=lambda x: lotes_df[lotes_df['id_lote'] == x]['codigo'].iloc[0]
                    )
                
                data_inicio = st.date_input("Data de Início", value=datetime.now() - timedelta(days=7))
                data_fim = st.date_input("Data de Fim", value=datetime.now())
                tipo_racao = st.selectbox(
                    "Tipo de Ração", 
                    options=["Pré-Inicial 1", "Pré-Inicial 2", "Inicial 1", "Inicial 2", "Crescimento", "Outro"]
                )
            
            with col2:
                quantidade_kg = st.number_input("Quantidade (kg)", min_value=0.1, step=0.1)
                custo_kg = st.number_input("Custo por kg (R$)", min_value=0.01, step=0.01, value=2.50)
                
                # Se um lote for selecionado, pré-preencher a fase
                if id_lote and not lotes_df.empty:
                    # Verificar se há animais neste lote
                    animais_df = obter_animais_recria_ativos(id_lote=id_lote)
                    if not animais_df.empty:
                        # Obter a fase mais comum entre os animais do lote
                        fase_predominante = animais_df['fase_recria'].mode().iloc[0]
                        st.write(f"**Fase Predominante no Lote:** {fase_predominante}")
                        fase_options = ["Fase 1", "Fase 2", "Fase 3"]
                        if fase_predominante in fase_options:
                            fase_options.remove(fase_predominante)
                            fase_options.insert(0, fase_predominante)
                        fase_recria = st.selectbox("Fase de Recria", options=fase_options)
                    else:
                        fase_recria = st.selectbox(
                            "Fase de Recria", 
                            options=["Fase 1", "Fase 2", "Fase 3"]
                        )
                else:
                    fase_recria = st.selectbox(
                        "Fase de Recria", 
                        options=["Fase 1", "Fase 2", "Fase 3"]
                    )
                
                responsavel = st.text_input("Responsável")
                observacao = st.text_area("Observação", help="Observações adicionais sobre o fornecimento")
            
            submit_alimentacao = st.form_submit_button("Registrar Alimentação")
        
        if submit_alimentacao:
            if not id_lote or not quantidade_kg or not custo_kg:
                st.error("Lote, Quantidade e Custo por kg são campos obrigatórios.")
            else:
                try:
                    sucesso, mensagem = registrar_alimentacao_recria(
                        id_lote=id_lote,
                        data_inicio=data_inicio.strftime("%Y-%m-%d"),
                        data_fim=data_fim.strftime("%Y-%m-%d"),
                        tipo_racao=tipo_racao,
                        quantidade_kg=quantidade_kg,
                        custo_kg=custo_kg,
                        fase_recria=fase_recria,
                        responsavel=responsavel,
                        observacao=observacao
                    )
                    
                    if sucesso:
                        st.success(mensagem)
                        # Limpar formulário ou redirecionar
                    else:
                        st.error(mensagem)
                except Exception as e:
                    st.error(f"Erro ao registrar alimentação: {str(e)}")

# Medicação
with tabs[6]:
    st.header("Medicação")
    
    # Abas para gerenciar medicação
    medicacao_tabs = st.tabs(["Histórico de Medicações", "Registrar Medicação"])
    
    # Histórico de Medicações
    with medicacao_tabs[0]:
        # Filtros
        col1, col2, col3 = st.columns(3)
        with col1:
            periodo_med = st.date_input(
                "Período:",
                value=(datetime.now() - timedelta(days=30), datetime.now()),
                key="medicacao_periodo"
            )
        
        with col2:
            tipo_filtro = st.radio(
                "Filtrar por:",
                options=["Todos", "Individual", "Coletiva"],
                horizontal=True,
                key="medicacao_tipo_filtro"
            )
        
        with col3:
            lotes_df = obter_lotes_recria_ativos()
            lote_filtro_med = st.selectbox(
                "Filtrar por Lote:", 
                options=["Todos"] + list(lotes_df["id_lote"].unique() if not lotes_df.empty else []),
                format_func=lambda x: "Todos" if x == "Todos" else lotes_df[lotes_df["id_lote"] == x]["codigo"].iloc[0],
                key="medicacao_lote_filtro"
            )
        
        # Carregar medicações
        medicacao_df = load_recria_medicacao()
        
        if medicacao_df.empty:
            st.info("Não há medicações registradas.")
        else:
            # Aplicar filtros
            if len(periodo_med) == 2:
                medicacao_df = medicacao_df[
                    (pd.to_datetime(medicacao_df['data_aplicacao']) >= pd.to_datetime(periodo_med[0])) &
                    (pd.to_datetime(medicacao_df['data_aplicacao']) <= pd.to_datetime(periodo_med[1]))
                ]
            
            if tipo_filtro != "Todos":
                medicacao_df = medicacao_df[medicacao_df['tipo_aplicacao'] == tipo_filtro]
            
            if lote_filtro_med != "Todos":
                medicacao_df = medicacao_df[
                    (medicacao_df['id_lote'] == lote_filtro_med) | 
                    (medicacao_df['tipo_aplicacao'] == "Individual")
                ]
            
            if medicacao_df.empty:
                st.info("Não há medicações que correspondam aos filtros selecionados.")
            else:
                # Combinar com informações dos animais para aplicações individuais
                recria_df = load_recria()
                if not recria_df.empty:
                    medicacao_df = pd.merge(
                        medicacao_df,
                        recria_df[['id_animal', 'identificacao']],
                        on='id_animal',
                        how='left'
                    )
                
                # Combinar com informações dos lotes para aplicações coletivas
                if not lotes_df.empty:
                    medicacao_df = pd.merge(
                        medicacao_df,
                        lotes_df[['id_lote', 'codigo']],
                        on='id_lote',
                        how='left'
                    )
                    medicacao_df = medicacao_df.rename(columns={'codigo': 'codigo_lote'})
                
                # Exibir medicações em uma tabela
                medicacao_display = medicacao_df[['id_medicacao', 'data_aplicacao', 'medicamento', 
                                               'tipo_aplicacao', 'identificacao', 'codigo_lote',
                                               'via_aplicacao', 'dose', 'unidade_dose', 'motivo']]
                
                # Formatar datas e números
                medicacao_display['data_aplicacao'] = medicacao_display['data_aplicacao'].apply(formatar_data)
                medicacao_display['dose'] = medicacao_display['dose'].apply(
                    lambda x: formatar_numero(x) if x is not None and not pd.isna(x) else "-"
                )
                
                # Renomear colunas para exibição
                medicacao_display = medicacao_display.rename(columns={
                    'id_medicacao': 'ID',
                    'data_aplicacao': 'Data',
                    'medicamento': 'Medicamento',
                    'tipo_aplicacao': 'Tipo',
                    'identificacao': 'Animal',
                    'codigo_lote': 'Lote',
                    'via_aplicacao': 'Via',
                    'dose': 'Dose',
                    'unidade_dose': 'Unidade',
                    'motivo': 'Motivo'
                })
                
                st.dataframe(medicacao_display, use_container_width=True)
                
                # Estatísticas de medicações
                st.subheader("Estatísticas de Medicações")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total de Medicações", len(medicacao_df))
                
                with col2:
                    st.metric("Medicações Individuais", len(medicacao_df[medicacao_df['tipo_aplicacao'] == 'Individual']))
                
                with col3:
                    st.metric("Medicações Coletivas", len(medicacao_df[medicacao_df['tipo_aplicacao'] == 'Coletiva']))
                
                # Gráficos
                col1, col2 = st.columns(2)
                
                with col1:
                    # Medicações por motivo
                    med_por_motivo = medicacao_df.groupby('motivo').size().reset_index(name='contagem')
                    if not med_por_motivo.empty:
                        fig = px.pie(
                            med_por_motivo, 
                            names='motivo', 
                            values='contagem',
                            title='Medicações por Motivo'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Medicações por medicamento
                    med_por_medicamento = medicacao_df.groupby('medicamento').size().reset_index(name='contagem')
                    if not med_por_medicamento.empty:
                        fig = px.bar(
                            med_por_medicamento, 
                            x='medicamento', 
                            y='contagem',
                            title='Medicações por Medicamento',
                            labels={'medicamento': 'Medicamento', 'contagem': 'Quantidade'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
    
    # Registrar Medicação
    with medicacao_tabs[1]:
        st.subheader("Registrar Nova Medicação")
        
        # Tipo de aplicação
        tipo_aplicacao = st.radio(
            "Tipo de Aplicação:",
            options=["Individual", "Coletiva"],
            horizontal=True
        )
        
        with st.form("form_medicacao"):
            col1, col2 = st.columns(2)
            
            with col1:
                data_aplicacao = st.date_input("Data da Aplicação", value=datetime.now())
                medicamento = st.text_input("Medicamento", help="Nome do medicamento aplicado")
                via_aplicacao = st.selectbox(
                    "Via de Aplicação", 
                    options=["Oral", "Intramuscular", "Subcutânea", "Intravenosa", "Tópica", "Na Ração", "Na Água", "Outra"]
                )
                
                dose = st.number_input("Dose", min_value=0.01, step=0.01)
                unidade_dose = st.selectbox(
                    "Unidade de Dose", 
                    options=["ml", "mg", "g", "kg", "UI", "Outra"]
                )
            
            with col2:
                motivo = st.selectbox(
                    "Motivo", 
                    options=["Prevenção", "Tratamento", "Vacinação", "Controle de Parasitas", "Outro"]
                )
                
                periodo_carencia = st.number_input("Período de Carência (dias)", min_value=0, value=0)
                
                # Seleção de animal ou lote dependendo do tipo de aplicação
                if tipo_aplicacao == "Individual":
                    # Carregar animais ativos em recria
                    animais_df = obter_animais_recria_ativos()
                    
                    if animais_df.empty:
                        st.error("Não há animais ativos em recria para medicar.")
                        id_animal = None
                    else:
                        id_animal = st.selectbox(
                            "Selecione o Animal:",
                            options=animais_df['id_animal'].tolist(),
                            format_func=lambda x: f"{animais_df[animais_df['id_animal'] == x]['identificacao'].iloc[0]}"
                        )
                    
                    id_lote = None
                else:  # Coletiva
                    id_animal = None
                    
                    # Carregar lotes ativos
                    lotes_df = obter_lotes_recria_ativos()
                    
                    if lotes_df.empty:
                        st.error("Não há lotes ativos para medicação coletiva.")
                        id_lote = None
                    else:
                        id_lote = st.selectbox(
                            "Selecione o Lote:",
                            options=lotes_df['id_lote'].tolist(),
                            format_func=lambda x: lotes_df[lotes_df['id_lote'] == x]['codigo'].iloc[0]
                        )
                
                responsavel = st.text_input("Responsável pela Medicação")
                observacao = st.text_area("Observação", help="Observações adicionais sobre a medicação")
            
            submit_medicacao = st.form_submit_button("Registrar Medicação")
        
        if submit_medicacao:
            if not medicamento or not dose or (tipo_aplicacao == "Individual" and not id_animal) or (tipo_aplicacao == "Coletiva" and not id_lote):
                st.error("Preencha todos os campos obrigatórios.")
            else:
                try:
                    sucesso, mensagem = registrar_medicacao_recria(
                        data_aplicacao=data_aplicacao.strftime("%Y-%m-%d"),
                        medicamento=medicamento,
                        via_aplicacao=via_aplicacao,
                        dose=dose,
                        unidade_dose=unidade_dose,
                        motivo=motivo,
                        tipo_aplicacao=tipo_aplicacao,
                        periodo_carencia=periodo_carencia,
                        responsavel=responsavel,
                        id_animal=id_animal,
                        id_lote=id_lote,
                        observacao=observacao
                    )
                    
                    if sucesso:
                        st.success(mensagem)
                        # Limpar formulário ou redirecionar
                    else:
                        st.error(mensagem)
                except Exception as e:
                    st.error(f"Erro ao registrar medicação: {str(e)}")