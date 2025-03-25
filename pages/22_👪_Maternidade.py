import streamlit as st
import pandas as pd
import uuid
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
from utils import (
    load_animals,
    load_maternity,
    save_maternity,
    load_litters,
    save_litters,
    load_piglets,
    save_piglets,
    load_pens,
    get_available_pens,
    load_pen_allocations,
    save_pen_allocations,
    check_litter_exists,
    get_active_maternity_sows
,
    check_permission
)

# Configuração da página
st.set_page_config(
    page_title="Maternidade - Sistema de Gestão de Suinocultura",
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
maternity_df = load_maternity()
litters_df = load_litters()
piglets_df = load_piglets()
pens_df = load_pens()
pen_allocations_df = load_pen_allocations()

# Filtrar apenas matrizes (fêmeas reprodutoras)
if not animals_df.empty:
    female_animals = animals_df[(animals_df['sexo'] == 'Fêmea') & 
                               (animals_df['categoria'].isin(['Matriz', 'Matriz Lactante']))]
else:
    female_animals = pd.DataFrame()

# Título da página
st.title("Maternidade 🐖")
st.markdown("""
Gerencie as matrizes em fase de maternidade, registre os partos e acompanhe o desenvolvimento dos leitões.
""")

# Abas para diferentes funcionalidades
tab1, tab2, tab3, tab4 = st.tabs(["Entrada na Maternidade", "Registro de Parto", "Leitões", "Monitoramento"])

with tab1:
    st.header("Entrada de Matriz na Maternidade")
    
    if not female_animals.empty and not pens_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Selecionar matriz
            selected_animal = st.selectbox(
                "Selecione a Matriz",
                options=female_animals['id_animal'].tolist(),
                format_func=lambda x: f"{female_animals[female_animals['id_animal'] == x]['identificacao'].iloc[0]} - {female_animals[female_animals['id_animal'] == x]['nome'].iloc[0]}" if female_animals[female_animals['id_animal'] == x]['nome'].iloc[0] else female_animals[female_animals['id_animal'] == x]['identificacao'].iloc[0]
            )
            
            # Verificar se a matriz já está na maternidade
            matriz_na_maternidade = False
            if not maternity_df.empty and selected_animal in maternity_df['id_animal'].values:
                entradas_ativas = maternity_df[(maternity_df['id_animal'] == selected_animal) & 
                                              (maternity_df['data_saida'].isna())]
                if not entradas_ativas.empty:
                    matriz_na_maternidade = True
                    st.warning("Esta matriz já está na maternidade. Para registrar um parto, use a aba 'Registro de Parto'.")
            
            # Data de entrada
            data_entrada = st.date_input(
                "Data de Entrada na Maternidade",
                value=datetime.now().date()
            )
            
        with col2:
            # Filtrar baias de maternidade disponíveis
            maternidade_pens = pens_df[pens_df['setor'] == 'Maternidade']
            
            if maternidade_pens.empty:
                st.error("Não há baias de maternidade cadastradas. Por favor, cadastre uma baia no setor 'Maternidade'.")
            else:
                available_pens = get_available_pens(maternidade_pens, pen_allocations_df)
                
                if available_pens.empty:
                    st.error("Não há baias de maternidade disponíveis no momento.")
                else:
                    selected_pen = st.selectbox(
                        "Selecione a Baia de Maternidade",
                        options=available_pens['id_baia'].tolist(),
                        format_func=lambda x: f"{available_pens[available_pens['id_baia'] == x]['identificacao'].iloc[0]} ({available_pens[available_pens['id_baia'] == x]['ocupacao_atual'].iloc[0]}/{available_pens[available_pens['id_baia'] == x]['capacidade'].iloc[0]} ocupada)"
                    )
                    
                    observacao = st.text_area(
                        "Observações",
                        height=100
                    )
                    
                    # Botão para registrar entrada
                    if st.button("Registrar Entrada na Maternidade") and not matriz_na_maternidade:
                        # Criar registro de maternidade
                        novo_registro = {
                            'id_maternidade': str(uuid.uuid4()),
                            'id_animal': selected_animal,
                            'id_baia': selected_pen,
                            'data_entrada': data_entrada.strftime('%Y-%m-%d'),
                            'data_parto': None,
                            'data_saida': None,
                            'status': 'Ativa',
                            'observacao': observacao
                        }
                        
                        # Adicionar ao DataFrame
                        if maternity_df.empty:
                            maternity_df = pd.DataFrame([novo_registro])
                        else:
                            maternity_df = pd.concat([maternity_df, pd.DataFrame([novo_registro])], ignore_index=True)
                        
                        # Salvar DataFrame atualizado
                        save_maternity(maternity_df)
                        
                        # Atualizar categoria da matriz para "Matriz Lactante"
                        animals_df.loc[animals_df['id_animal'] == selected_animal, 'categoria'] = 'Matriz Lactante'
                        
                        # Alocar a matriz na baia selecionada
                        nova_alocacao = {
                            'id_alocacao': str(uuid.uuid4()),
                            'id_baia': selected_pen,
                            'id_animal': selected_animal,
                            'data_entrada': data_entrada.strftime('%Y-%m-%d'),
                            'data_saida': None,
                            'motivo_saida': None,
                            'status': 'Ativo',
                            'observacao': 'Entrada na maternidade'
                        }
                        
                        # Adicionar ao DataFrame de alocações
                        if pen_allocations_df.empty:
                            pen_allocations_df = pd.DataFrame([nova_alocacao])
                        else:
                            pen_allocations_df = pd.concat([pen_allocations_df, pd.DataFrame([nova_alocacao])], ignore_index=True)
                        
                        # Salvar DataFrame atualizado
                        save_pen_allocations(pen_allocations_df)
                        
                        st.success("Entrada na maternidade registrada com sucesso!")
                        st.rerun()
    else:
        if female_animals.empty:
            st.warning("Não há matrizes cadastradas. Por favor, cadastre uma matriz primeiro.")
        if pens_df.empty:
            st.warning("Não há baias cadastradas. Por favor, cadastre uma baia primeiro.")

with tab2:
    st.header("Registro de Parto")
    
    # Obter matrizes ativas na maternidade
    active_sows = get_active_maternity_sows(maternity_df, animals_df)
    
    if active_sows.empty:
        st.warning("Não há matrizes na maternidade. Registre uma entrada na aba 'Entrada na Maternidade'.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            # Selecionar matriz
            selected_sow = st.selectbox(
                "Selecione a Matriz",
                options=active_sows['id_animal'].tolist(),
                format_func=lambda x: f"{active_sows[active_sows['id_animal'] == x]['identificacao'].iloc[0]} - {active_sows[active_sows['id_animal'] == x]['nome'].iloc[0]}" if active_sows[active_sows['id_animal'] == x]['nome'].iloc[0] else active_sows[active_sows['id_animal'] == x]['identificacao'].iloc[0],
                key="parto_matriz"
            )
            
            # Obter ID da maternidade correspondente
            maternity_id = active_sows[active_sows['id_animal'] == selected_sow]['id_maternidade'].iloc[0]
            
            # Verificar se já existe leitegada registrada para esta entrada na maternidade
            leitegada_existente = check_litter_exists(litters_df, maternity_id)
            if leitegada_existente:
                st.warning("Já existe um parto registrado para esta matriz na maternidade atual.")
            
            # Data do parto
            data_parto = st.date_input(
                "Data do Parto",
                value=datetime.now().date()
            )
            
            # Total de leitões nascidos
            total_nascidos = st.number_input(
                "Total de Leitões Nascidos",
                min_value=0,
                max_value=30,
                value=12
            )
            
            # Leitões nascidos vivos
            nascidos_vivos = st.number_input(
                "Leitões Nascidos Vivos",
                min_value=0,
                max_value=total_nascidos,
                value=min(total_nascidos, 10)
            )
            
            # Leitões natimortos
            natimortos = st.number_input(
                "Leitões Natimortos",
                min_value=0,
                max_value=total_nascidos - nascidos_vivos,
                value=min(1, total_nascidos - nascidos_vivos)
            )
            
            # Leitões mumificados
            mumificados = total_nascidos - nascidos_vivos - natimortos
            st.metric("Leitões Mumificados", mumificados)
            
        with col2:
            # Peso total da leitegada
            peso_total = st.number_input(
                "Peso Total da Leitegada (kg)",
                min_value=0.0,
                max_value=50.0,
                value=float(nascidos_vivos * 1.4),
                step=0.1,
                format="%.1f"
            )
            
            # Calcular e mostrar peso médio
            peso_medio = peso_total / nascidos_vivos if nascidos_vivos > 0 else 0
            st.metric("Peso Médio por Leitão (kg)", round(peso_medio, 2))
            
            # Observações
            observacao = st.text_area(
                "Observações sobre o Parto",
                placeholder="Detalhes sobre o parto, complicações, etc.",
                height=150
            )
            
            # Botão para registrar parto
            if st.button("Registrar Parto") and not leitegada_existente:
                # 1. Atualizar registro de maternidade com a data do parto
                maternity_df.loc[maternity_df['id_maternidade'] == maternity_id, 'data_parto'] = data_parto.strftime('%Y-%m-%d')
                save_maternity(maternity_df)
                
                # 2. Criar registro de leitegada
                id_leitegada = str(uuid.uuid4())
                nova_leitegada = {
                    'id_leitegada': id_leitegada,
                    'id_maternidade': maternity_id,
                    'id_animal': selected_sow,
                    'data_parto': data_parto.strftime('%Y-%m-%d'),
                    'total_nascidos': total_nascidos,
                    'nascidos_vivos': nascidos_vivos,
                    'natimortos': natimortos,
                    'mumificados': mumificados,
                    'peso_total': peso_total,
                    'peso_medio': peso_medio,
                    'tamanho_leitegada_ajustado': nascidos_vivos,
                    'observacao': observacao
                }
                
                # Adicionar ao DataFrame
                if litters_df.empty:
                    litters_df = pd.DataFrame([nova_leitegada])
                else:
                    litters_df = pd.concat([litters_df, pd.DataFrame([nova_leitegada])], ignore_index=True)
                
                # Salvar DataFrame atualizado
                save_litters(litters_df)
                
                st.success("Parto registrado com sucesso! Agora você pode registrar os leitões na aba 'Leitões'.")
                st.rerun()

with tab3:
    st.header("Cadastro e Gerenciamento de Leitões")
    
    if litters_df.empty:
        st.warning("Não há leitegadas registradas. Registre um parto na aba 'Registro de Parto'.")
    else:
        # Organizar em subabas
        subtab1, subtab2, subtab3 = st.tabs(["Cadastro Individual", "Cadastro em Lote", "Gerenciamento"])
        
        # Obter lista de leitegadas, ordenada por data de parto (mais recente primeiro)
        litters_df['data_parto'] = pd.to_datetime(litters_df['data_parto'])
        sorted_litters = litters_df.sort_values('data_parto', ascending=False)
        
        # Adicionar informação da matriz em cada leitegada para exibição
        if not animals_df.empty:
            sorted_litters['matriz'] = sorted_litters['id_animal'].apply(
                lambda x: animals_df[animals_df['id_animal'] == x]['identificacao'].iloc[0] 
                if x in animals_df['id_animal'].values else "Desconhecida"
            )
        
        with subtab1:
            st.subheader("Cadastro Individual de Leitão")
            
            # Selecionar leitegada
            selected_litter = st.selectbox(
                "Selecione a Leitegada",
                options=sorted_litters['id_leitegada'].tolist(),
                format_func=lambda x: f"Matriz: {sorted_litters[sorted_litters['id_leitegada'] == x]['matriz'].iloc[0]} - Parto: {sorted_litters[sorted_litters['id_leitegada'] == x]['data_parto'].dt.strftime('%d/%m/%Y').iloc[0]} ({sorted_litters[sorted_litters['id_leitegada'] == x]['nascidos_vivos'].iloc[0]} leitões vivos)"
            )
            
            # Obter detalhes da leitegada selecionada
            litter_data = sorted_litters[sorted_litters['id_leitegada'] == selected_litter].iloc[0]
            matriz_id = litter_data['id_animal']
            
            # Contar leitões já cadastrados para esta leitegada
            leitoes_cadastrados = 0
            if not piglets_df.empty and selected_litter in piglets_df['id_leitegada'].values:
                leitoes_cadastrados = len(piglets_df[piglets_df['id_leitegada'] == selected_litter])
            
            st.write(f"**Leitões cadastrados:** {leitoes_cadastrados} de {int(litter_data['nascidos_vivos'])}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Identificação do leitão
                identificacao = st.text_input(
                    "Identificação do Leitão",
                    placeholder="Ex: #001, B123, etc."
                )
                
                # Sexo
                sexo = st.selectbox(
                    "Sexo",
                    options=["Macho", "Fêmea"]
                )
                
                # Data de nascimento (padrão = data do parto)
                data_nascimento = st.date_input(
                    "Data de Nascimento",
                    value=litter_data['data_parto'].date()
                )
                
            with col2:
                # Peso ao nascer
                peso_nascimento = st.number_input(
                    "Peso ao Nascer (kg)",
                    min_value=0.1,
                    max_value=3.0,
                    value=1.4,
                    step=0.1,
                    format="%.1f"
                )
                
                # Status atual
                status_atual = st.selectbox(
                    "Status Atual",
                    options=["Vivo", "Morto"]
                )
                
                # Causa da morte (se aplicável)
                causa_morte = None
                if status_atual == "Morto":
                    causa_morte = st.selectbox(
                        "Causa da Morte",
                        options=["Esmagamento", "Diarreia", "Baixo Peso", "Má Formação", "Inanição", "Doença Respiratória", "Outro"]
                    )
                
                # Observações
                observacao = st.text_area(
                    "Observações",
                    height=100
                )
            
            if st.button("Cadastrar Leitão"):
                # Verificar duplicação de identificação
                id_duplicado = False
                if not piglets_df.empty and 'identificacao' in piglets_df.columns and identificacao in piglets_df['identificacao'].values:
                    id_duplicado = True
                    st.error(f"Já existe um leitão com a identificação '{identificacao}'. Por favor, escolha outra identificação.")
                
                if not id_duplicado:
                    # Criar registro do leitão
                    novo_leitao = {
                        'id_leitao': str(uuid.uuid4()),
                        'id_leitegada': selected_litter,
                        'id_animal_mae': matriz_id,
                        'id_animal_adotiva': None,
                        'identificacao': identificacao,
                        'sexo': sexo,
                        'data_nascimento': data_nascimento.strftime('%Y-%m-%d'),
                        'peso_nascimento': peso_nascimento,
                        'peso_atual': peso_nascimento,  # Inicialmente igual ao peso de nascimento
                        'status_atual': status_atual,
                        'data_status': datetime.now().strftime('%Y-%m-%d'),
                        'causa_morte': causa_morte,
                        'observacao': observacao
                    }
                    
                    # Adicionar ao DataFrame
                    if piglets_df.empty:
                        piglets_df = pd.DataFrame([novo_leitao])
                    else:
                        piglets_df = pd.concat([piglets_df, pd.DataFrame([novo_leitao])], ignore_index=True)
                    
                    # Salvar DataFrame atualizado
                    save_piglets(piglets_df)
                    
                    st.success("Leitão cadastrado com sucesso!")
                    st.rerun()
        
        with subtab2:
            st.subheader("Cadastro em Lote de Leitões")
            
            # Selecionar leitegada
            selected_litter_batch = st.selectbox(
                "Selecione a Leitegada",
                options=sorted_litters['id_leitegada'].tolist(),
                format_func=lambda x: f"Matriz: {sorted_litters[sorted_litters['id_leitegada'] == x]['matriz'].iloc[0]} - Parto: {sorted_litters[sorted_litters['id_leitegada'] == x]['data_parto'].dt.strftime('%d/%m/%Y').iloc[0]} ({sorted_litters[sorted_litters['id_leitegada'] == x]['nascidos_vivos'].iloc[0]} leitões vivos)",
                key="lote_leitegada"
            )
            
            # Obter detalhes da leitegada selecionada
            litter_data_batch = sorted_litters[sorted_litters['id_leitegada'] == selected_litter_batch].iloc[0]
            matriz_id_batch = litter_data_batch['id_animal']
            
            # Contar leitões já cadastrados para esta leitegada
            leitoes_cadastrados_batch = 0
            if not piglets_df.empty and selected_litter_batch in piglets_df['id_leitegada'].values:
                leitoes_cadastrados_batch = len(piglets_df[piglets_df['id_leitegada'] == selected_litter_batch])
            
            leitoes_restantes = int(litter_data_batch['nascidos_vivos']) - leitoes_cadastrados_batch
            st.write(f"**Leitões cadastrados:** {leitoes_cadastrados_batch} de {int(litter_data_batch['nascidos_vivos'])}")
            
            if leitoes_restantes <= 0:
                st.info("Todos os leitões desta leitegada já foram cadastrados.")
            else:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Quantidade a cadastrar
                    quantidade = st.number_input(
                        "Quantidade de Leitões a Cadastrar",
                        min_value=1,
                        max_value=leitoes_restantes,
                        value=min(leitoes_restantes, 10)
                    )
                    
                    # Prefixo de identificação
                    prefixo = st.text_input(
                        "Prefixo de Identificação",
                        placeholder="Ex: LT-",
                        value="LT-"
                    )
                    
                    # Numeração inicial
                    numero_inicial = st.number_input(
                        "Número Inicial",
                        min_value=1,
                        value=1
                    )
                    
                    # Data de nascimento (padrão = data do parto)
                    data_nascimento_lote = st.date_input(
                        "Data de Nascimento",
                        value=litter_data_batch['data_parto'].date(),
                        key="data_nasc_lote"
                    )
                    
                with col2:
                    # Distribuição de sexo
                    st.write("**Distribuição de Sexo**")
                    percentual_machos = st.slider(
                        "Percentual de Machos",
                        min_value=0,
                        max_value=100,
                        value=50
                    )
                    num_machos = round(quantidade * percentual_machos / 100)
                    num_femeas = quantidade - num_machos
                    st.write(f"Machos: {num_machos}, Fêmeas: {num_femeas}")
                    
                    # Peso médio ao nascer
                    peso_medio_nascer = st.number_input(
                        "Peso Médio ao Nascer (kg)",
                        min_value=0.5,
                        max_value=2.5,
                        value=litter_data_batch['peso_medio'],
                        step=0.1,
                        format="%.1f"
                    )
                    
                    # Variação de peso (%)
                    variacao_peso = st.slider(
                        "Variação de Peso (%)",
                        min_value=0,
                        max_value=30,
                        value=10
                    )
                
                exemplo_ids = [f"{prefixo}{i}" for i in range(numero_inicial, numero_inicial + min(3, quantidade))]
                if quantidade > 3:
                    exemplo_ids.append("...")
                    exemplo_ids.append(f"{prefixo}{numero_inicial + quantidade - 1}")
                
                st.write(f"**Exemplo de identificações:** {', '.join(exemplo_ids)}")
                
                if st.button("Cadastrar Lote de Leitões"):
                    # Verificar duplicação de identificações
                    novos_ids = [f"{prefixo}{i}" for i in range(numero_inicial, numero_inicial + quantidade)]
                    ids_duplicados = []
                    
                    if not piglets_df.empty and 'identificacao' in piglets_df.columns:
                        for novo_id in novos_ids:
                            if novo_id in piglets_df['identificacao'].values:
                                ids_duplicados.append(novo_id)
                    
                    if ids_duplicados:
                        st.error(f"As seguintes identificações já existem: {', '.join(ids_duplicados)}. Por favor, ajuste o prefixo ou número inicial.")
                    else:
                        # Criar lista de sexos (distribuir aleatoriamente)
                        sexos = ['Macho'] * num_machos + ['Fêmea'] * num_femeas
                        np.random.shuffle(sexos)
                        
                        # Criar registros de leitões
                        novos_leitoes = []
                        for i in range(quantidade):
                            # Calcular peso com variação
                            variacao = np.random.uniform(-variacao_peso/100, variacao_peso/100)
                            peso = max(0.3, peso_medio_nascer * (1 + variacao))
                            
                            novo_leitao = {
                                'id_leitao': str(uuid.uuid4()),
                                'id_leitegada': selected_litter_batch,
                                'id_animal_mae': matriz_id_batch,
                                'id_animal_adotiva': None,
                                'identificacao': f"{prefixo}{numero_inicial + i}",
                                'sexo': sexos[i],
                                'data_nascimento': data_nascimento_lote.strftime('%Y-%m-%d'),
                                'peso_nascimento': round(peso, 2),
                                'peso_atual': round(peso, 2),
                                'status_atual': 'Vivo',
                                'data_status': datetime.now().strftime('%Y-%m-%d'),
                                'causa_morte': None,
                                'observacao': f"Cadastrado em lote em {datetime.now().strftime('%d/%m/%Y')}"
                            }
                            novos_leitoes.append(novo_leitao)
                        
                        # Adicionar ao DataFrame
                        if piglets_df.empty:
                            piglets_df = pd.DataFrame(novos_leitoes)
                        else:
                            piglets_df = pd.concat([piglets_df, pd.DataFrame(novos_leitoes)], ignore_index=True)
                        
                        # Salvar DataFrame atualizado
                        save_piglets(piglets_df)
                        
                        st.success(f"{quantidade} leitões cadastrados com sucesso!")
                        st.rerun()
        
        with subtab3:
            st.subheader("Gerenciamento de Leitões")
            
            if piglets_df.empty:
                st.warning("Não há leitões cadastrados. Cadastre leitões nas abas 'Cadastro Individual' ou 'Cadastro em Lote'.")
            else:
                # Selecionar leitegada para gerenciar
                selected_litter_manage = st.selectbox(
                    "Selecione a Leitegada",
                    options=sorted_litters['id_leitegada'].tolist(),
                    format_func=lambda x: f"Matriz: {sorted_litters[sorted_litters['id_leitegada'] == x]['matriz'].iloc[0]} - Parto: {sorted_litters[sorted_litters['id_leitegada'] == x]['data_parto'].dt.strftime('%d/%m/%Y').iloc[0]}",
                    key="gerenciar_leitegada"
                )
                
                # Filtrar leitões da leitegada selecionada
                if selected_litter_manage in piglets_df['id_leitegada'].values:
                    litter_piglets = piglets_df[piglets_df['id_leitegada'] == selected_litter_manage].copy()
                    
                    # Métricas resumidas
                    total_leitoes = len(litter_piglets)
                    vivos = len(litter_piglets[litter_piglets['status_atual'] == 'Vivo'])
                    mortos = total_leitoes - vivos
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total de Leitões", total_leitoes)
                    with col2:
                        st.metric("Vivos", vivos)
                    with col3:
                        st.metric("Mortos", mortos)
                    
                    # Tabela de leitões com ações
                    st.write("### Lista de Leitões")
                    
                    # Adicionar botões de ação para cada leitão
                    litter_piglets['acoes'] = litter_piglets.index
                    
                    # Exibir tabela editável
                    edited_df = st.data_editor(
                        litter_piglets[['identificacao', 'sexo', 'peso_nascimento', 'peso_atual', 'status_atual', 'observacao']],
                        column_config={
                            "identificacao": st.column_config.TextColumn("Identificação"),
                            "sexo": st.column_config.SelectboxColumn("Sexo", options=["Macho", "Fêmea"]),
                            "peso_nascimento": st.column_config.NumberColumn("Peso Nasc. (kg)", format="%.2f"),
                            "peso_atual": st.column_config.NumberColumn("Peso Atual (kg)", format="%.2f"),
                            "status_atual": st.column_config.SelectboxColumn("Status", options=["Vivo", "Morto", "Desmamado", "Transferido"]),
                            "observacao": st.column_config.TextColumn("Observações"),
                        },
                        use_container_width=True,
                        hide_index=True,
                        num_rows="dynamic"
                    )
                    
                    # Detectar alterações e salvar
                    if st.button("Salvar Alterações"):
                        # Atualizar o DataFrame original com as alterações
                        for i, row in edited_df.iterrows():
                            idx = litter_piglets.iloc[i].name
                            for col in ['identificacao', 'sexo', 'peso_nascimento', 'peso_atual', 'status_atual', 'observacao']:
                                piglets_df.loc[idx, col] = row[col]
                            
                            # Se o status mudou para "Morto", atualizar a data do status
                            if row['status_atual'] == 'Morto' and litter_piglets.iloc[i]['status_atual'] != 'Morto':
                                piglets_df.loc[idx, 'data_status'] = datetime.now().strftime('%Y-%m-%d')
                        
                        # Salvar DataFrame atualizado
                        save_piglets(piglets_df)
                        st.success("Alterações salvas com sucesso!")
                        st.rerun()
                    
                    # Opção para registrar mortalidade em lote
                    with st.expander("Registrar Mortalidade em Lote"):
                        st.write("Selecione os leitões que morreram e a causa da morte.")
                        
                        # Filtrar apenas leitões vivos
                        vivos_df = litter_piglets[litter_piglets['status_atual'] == 'Vivo']
                        
                        if vivos_df.empty:
                            st.info("Não há leitões vivos nesta leitegada.")
                        else:
                            # Multi-select para leitões
                            leitoes_para_mortalidade = st.multiselect(
                                "Selecione os Leitões",
                                options=vivos_df['id_leitao'].tolist(),
                                format_func=lambda x: vivos_df[vivos_df['id_leitao'] == x]['identificacao'].iloc[0]
                            )
                            
                            if leitoes_para_mortalidade:
                                # Causa da morte
                                causa_morte_lote = st.selectbox(
                                    "Causa da Morte",
                                    options=["Esmagamento", "Diarreia", "Baixo Peso", "Má Formação", "Inanição", "Doença Respiratória", "Outro"],
                                    key="causa_morte_lote"
                                )
                                
                                # Data da morte
                                data_morte = st.date_input(
                                    "Data da Morte",
                                    value=datetime.now().date()
                                )
                                
                                # Observação
                                obs_morte = st.text_area(
                                    "Observação",
                                    placeholder="Detalhes sobre a mortalidade..."
                                )
                                
                                if st.button("Registrar Mortalidade"):
                                    # Atualizar cada leitão selecionado
                                    for leitao_id in leitoes_para_mortalidade:
                                        piglets_df.loc[piglets_df['id_leitao'] == leitao_id, 'status_atual'] = 'Morto'
                                        piglets_df.loc[piglets_df['id_leitao'] == leitao_id, 'data_status'] = data_morte.strftime('%Y-%m-%d')
                                        piglets_df.loc[piglets_df['id_leitao'] == leitao_id, 'causa_morte'] = causa_morte_lote
                                        
                                        # Adicionar à observação existente
                                        atual_obs = piglets_df.loc[piglets_df['id_leitao'] == leitao_id, 'observacao'].iloc[0]
                                        nova_obs = f"{atual_obs}\nMorte em {data_morte.strftime('%d/%m/%Y')}: {obs_morte}" if atual_obs else f"Morte em {data_morte.strftime('%d/%m/%Y')}: {obs_morte}"
                                        piglets_df.loc[piglets_df['id_leitao'] == leitao_id, 'observacao'] = nova_obs
                                    
                                    # Salvar DataFrame atualizado
                                    save_piglets(piglets_df)
                                    st.success(f"Mortalidade registrada para {len(leitoes_para_mortalidade)} leitões.")
                                    st.rerun()
                                    
                    # Opção para registrar peso em lote
                    with st.expander("Registrar Peso em Lote"):
                        st.write("Atualize o peso de múltiplos leitões ao mesmo tempo.")
                        
                        # Filtrar apenas leitões vivos
                        vivos_peso_df = litter_piglets[litter_piglets['status_atual'] == 'Vivo']
                        
                        if vivos_peso_df.empty:
                            st.info("Não há leitões vivos nesta leitegada.")
                        else:
                            # Estratégia de atualização
                            estrategia = st.radio(
                                "Como deseja atualizar os pesos?",
                                options=["Atualizar todos com o mesmo incremento", "Especificar peso para cada leitão"]
                            )
                            
                            if estrategia == "Atualizar todos com o mesmo incremento":
                                # Selecionar todos os leitões ou específicos
                                selecao = st.radio(
                                    "Selecionar leitões",
                                    options=["Todos os leitões vivos", "Selecionar leitões específicos"]
                                )
                                
                                if selecao == "Todos os leitões vivos":
                                    leitoes_para_peso = vivos_peso_df['id_leitao'].tolist()
                                    st.write(f"Serão atualizados {len(leitoes_para_peso)} leitões.")
                                else:
                                    leitoes_para_peso = st.multiselect(
                                        "Selecione os Leitões",
                                        options=vivos_peso_df['id_leitao'].tolist(),
                                        format_func=lambda x: f"{vivos_peso_df[vivos_peso_df['id_leitao'] == x]['identificacao'].iloc[0]} (atual: {vivos_peso_df[vivos_peso_df['id_leitao'] == x]['peso_atual'].iloc[0]} kg)",
                                        key="leitoes_peso_incremental"
                                    )
                                
                                if leitoes_para_peso:
                                    # Incremento de peso
                                    incremento = st.number_input(
                                        "Incremento de Peso (kg)",
                                        min_value=0.1,
                                        max_value=10.0,
                                        value=0.5,
                                        step=0.1,
                                        format="%.1f"
                                    )
                                    
                                    # Data da pesagem
                                    data_pesagem = st.date_input(
                                        "Data da Pesagem",
                                        value=datetime.now().date(),
                                        key="data_pesagem_incremento"
                                    )
                                    
                                    if st.button("Atualizar Pesos (Incremento)"):
                                        # Atualizar cada leitão selecionado
                                        for leitao_id in leitoes_para_peso:
                                            peso_atual = piglets_df.loc[piglets_df['id_leitao'] == leitao_id, 'peso_atual'].iloc[0]
                                            novo_peso = peso_atual + incremento
                                            piglets_df.loc[piglets_df['id_leitao'] == leitao_id, 'peso_atual'] = novo_peso
                                            
                                            # Adicionar à observação existente
                                            atual_obs = piglets_df.loc[piglets_df['id_leitao'] == leitao_id, 'observacao'].iloc[0]
                                            nova_obs = f"{atual_obs}\nPesagem em {data_pesagem.strftime('%d/%m/%Y')}: {peso_atual} kg → {novo_peso} kg" if atual_obs else f"Pesagem em {data_pesagem.strftime('%d/%m/%Y')}: {peso_atual} kg → {novo_peso} kg"
                                            piglets_df.loc[piglets_df['id_leitao'] == leitao_id, 'observacao'] = nova_obs
                                        
                                        # Salvar DataFrame atualizado
                                        save_piglets(piglets_df)
                                        st.success(f"Peso atualizado para {len(leitoes_para_peso)} leitões.")
                                        st.rerun()
                            else:
                                # Mostrar tabela para edição direta
                                pesos_df = vivos_peso_df[['id_leitao', 'identificacao', 'peso_atual']].copy()
                                pesos_df['novo_peso'] = pesos_df['peso_atual']
                                
                                edited_pesos = st.data_editor(
                                    pesos_df[['identificacao', 'peso_atual', 'novo_peso']],
                                    column_config={
                                        "identificacao": st.column_config.TextColumn("Identificação", disabled=True),
                                        "peso_atual": st.column_config.NumberColumn("Peso Atual (kg)", format="%.2f", disabled=True),
                                        "novo_peso": st.column_config.NumberColumn("Novo Peso (kg)", format="%.2f"),
                                    },
                                    use_container_width=True,
                                    hide_index=True
                                )
                                
                                # Data da pesagem
                                data_pesagem_individual = st.date_input(
                                    "Data da Pesagem",
                                    value=datetime.now().date(),
                                    key="data_pesagem_individual"
                                )
                                
                                if st.button("Atualizar Pesos (Individual)"):
                                    alteracoes = 0
                                    for i, row in edited_pesos.iterrows():
                                        if row['novo_peso'] != row['peso_atual']:
                                            leitao_id = pesos_df.iloc[i]['id_leitao']
                                            piglets_df.loc[piglets_df['id_leitao'] == leitao_id, 'peso_atual'] = row['novo_peso']
                                            
                                            # Adicionar à observação existente
                                            atual_obs = piglets_df.loc[piglets_df['id_leitao'] == leitao_id, 'observacao'].iloc[0]
                                            nova_obs = f"{atual_obs}\nPesagem em {data_pesagem_individual.strftime('%d/%m/%Y')}: {row['peso_atual']} kg → {row['novo_peso']} kg" if atual_obs else f"Pesagem em {data_pesagem_individual.strftime('%d/%m/%Y')}: {row['peso_atual']} kg → {row['novo_peso']} kg"
                                            piglets_df.loc[piglets_df['id_leitao'] == leitao_id, 'observacao'] = nova_obs
                                            alteracoes += 1
                                    
                                    if alteracoes > 0:
                                        # Salvar DataFrame atualizado
                                        save_piglets(piglets_df)
                                        st.success(f"Peso atualizado para {alteracoes} leitões.")
                                        st.rerun()
                                    else:
                                        st.info("Nenhuma alteração de peso detectada.")
                else:
                    st.info("Não há leitões cadastrados para esta leitegada.")

with tab4:
    st.header("Monitoramento da Maternidade")
    
    # Métricas resumidas
    col1, col2, col3, col4 = st.columns(4)
    
    # Total de matrizes na maternidade
    total_matrizes_maternidade = 0
    if not maternity_df.empty:
        matrizes_ativas = maternity_df[maternity_df['data_saida'].isna()]
        total_matrizes_maternidade = len(matrizes_ativas)
    
    # Total de leitegadas
    total_leitegadas = len(litters_df) if not litters_df.empty else 0
    
    # Total de leitões vivos
    total_leitoes_vivos = 0
    if not piglets_df.empty:
        total_leitoes_vivos = len(piglets_df[piglets_df['status_atual'] == 'Vivo'])
    
    # Taxa de mortalidade
    taxa_mortalidade = 0
    if not piglets_df.empty and len(piglets_df) > 0:
        mortos = len(piglets_df[piglets_df['status_atual'] == 'Morto'])
        taxa_mortalidade = (mortos / len(piglets_df)) * 100
    
    with col1:
        st.metric("Matrizes na Maternidade", total_matrizes_maternidade)
        
    with col2:
        st.metric("Leitegadas Ativas", total_leitegadas)
        
    with col3:
        st.metric("Leitões Vivos", total_leitoes_vivos)
        
    with col4:
        st.metric("Taxa de Mortalidade", f"{taxa_mortalidade:.1f}%")
    
    # Gráficos e visualizações
    if not litters_df.empty and not piglets_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de tamanho das leitegadas
            st.subheader("Tamanho das Leitegadas")
            
            litter_sizes = litters_df[['id_leitegada', 'data_parto', 'nascidos_vivos', 'natimortos', 'mumificados']].copy()
            litter_sizes['data_parto'] = pd.to_datetime(litter_sizes['data_parto'])
            litter_sizes = litter_sizes.sort_values('data_parto')
            
            # Adicionar identificação da matriz
            if not animals_df.empty and 'id_animal' in litters_df.columns:
                litter_sizes['matriz'] = litters_df['id_animal'].apply(
                    lambda x: animals_df[animals_df['id_animal'] == x]['identificacao'].iloc[0] 
                    if x in animals_df['id_animal'].values else "Desconhecida"
                )
                
                fig = px.bar(
                    litter_sizes,
                    x='matriz',
                    y=['nascidos_vivos', 'natimortos', 'mumificados'],
                    title="Composição das Leitegadas por Matriz",
                    labels={'value': 'Número de Leitões', 'variable': 'Tipo', 'matriz': 'Matriz'},
                    color_discrete_map={
                        'nascidos_vivos': '#2E7D32',
                        'natimortos': '#D32F2F',
                        'mumificados': '#757575'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Gráfico de causas de mortalidade
            st.subheader("Causas de Mortalidade")
            
            if 'causa_morte' in piglets_df.columns:
                mortos_df = piglets_df[piglets_df['status_atual'] == 'Morto']
                
                if not mortos_df.empty and not mortos_df['causa_morte'].isna().all():
                    causas_morte = mortos_df['causa_morte'].value_counts().reset_index()
                    causas_morte.columns = ['Causa', 'Quantidade']
                    
                    fig = px.pie(
                        causas_morte,
                        values='Quantidade',
                        names='Causa',
                        title="Causas de Mortalidade",
                        hole=0.4
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Não há dados suficientes sobre causas de mortalidade.")
        
        # Timeline de partos
        st.subheader("Timeline de Partos")
        
        if 'data_parto' in litters_df.columns:
            timeline_df = litters_df[['id_leitegada', 'id_animal', 'data_parto', 'total_nascidos', 'nascidos_vivos']].copy()
            timeline_df['data_parto'] = pd.to_datetime(timeline_df['data_parto'])
            
            # Adicionar identificação da matriz
            if not animals_df.empty:
                timeline_df['matriz'] = timeline_df['id_animal'].apply(
                    lambda x: animals_df[animals_df['id_animal'] == x]['identificacao'].iloc[0] 
                    if x in animals_df['id_animal'].values else "Desconhecida"
                )
            else:
                timeline_df['matriz'] = "Desconhecida"
            
            # Ordenar por data
            timeline_df = timeline_df.sort_values('data_parto')
            
            # Criar gráfico de linha do tempo
            fig = px.scatter(
                timeline_df,
                x='data_parto',
                y='matriz',
                size='nascidos_vivos',
                color='nascidos_vivos',
                hover_name='matriz',
                hover_data={
                    'data_parto': True,
                    'total_nascidos': True,
                    'nascidos_vivos': True,
                    'matriz': False
                },
                title="Timeline de Partos por Matriz",
                labels={
                    'data_parto': 'Data do Parto',
                    'matriz': 'Matriz',
                    'nascidos_vivos': 'Leitões Vivos'
                },
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
        # Tabela de leitegadas ativas
        st.subheader("Leitegadas Ativas")
        
        if not litters_df.empty:
            display_litters = litters_df.copy()
            display_litters['data_parto'] = pd.to_datetime(display_litters['data_parto']).dt.strftime('%d/%m/%Y')
            
            # Adicionar informações da matriz
            if not animals_df.empty:
                display_litters['matriz'] = display_litters['id_animal'].apply(
                    lambda x: animals_df[animals_df['id_animal'] == x]['identificacao'].iloc[0]
                    if x in animals_df['id_animal'].values else "Desconhecida"
                )
            
            # Adicionar contagem de leitões vivos atualmente
            display_litters['leitoes_vivos_atuais'] = display_litters['id_leitegada'].apply(
                lambda x: len(piglets_df[(piglets_df['id_leitegada'] == x) & (piglets_df['status_atual'] == 'Vivo')])
                if not piglets_df.empty else 0
            )
            
            # Calcular idade da leitegada em dias
            display_litters['data_parto_dt'] = pd.to_datetime(display_litters['data_parto'])
            today = pd.Timestamp(datetime.now().date())
            display_litters['idade_dias'] = (today - display_litters['data_parto_dt']).dt.days
            
            # Exibir colunas relevantes
            st.dataframe(
                display_litters[[
                    'matriz', 'data_parto', 'nascidos_vivos', 'leitoes_vivos_atuais', 
                    'idade_dias', 'peso_medio'
                ]].rename(columns={
                    'matriz': 'Matriz',
                    'data_parto': 'Data do Parto',
                    'nascidos_vivos': 'Nascidos Vivos',
                    'leitoes_vivos_atuais': 'Vivos Atualmente',
                    'idade_dias': 'Idade (dias)',
                    'peso_medio': 'Peso Médio ao Nascer (kg)'
                }).sort_values('Data do Parto', ascending=False),
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("Cadastre matrizes na maternidade e registre partos para visualizar estatísticas e gráficos.")