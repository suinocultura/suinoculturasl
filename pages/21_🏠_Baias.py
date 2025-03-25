import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
import plotly.express as px
from utils import (
    load_animals, 
    load_pens, 
    save_pens, 
    load_pen_allocations, 
    save_pen_allocations,
    get_pen_occupancy,
    get_available_pens,
    get_animal_details
,
    check_permission
)

# Page configuration
st.set_page_config(
    page_title="Gestão de Baias - Sistema de Gestão de Suinocultura",
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
pens_df = load_pens()
allocations_df = load_pen_allocations()

# Título da página
st.title("Gestão de Baias 🏠")
st.markdown("Cadastre e gerencie as baias da sua granja, alocando animais nos espaços disponíveis.")

# Abas para diferentes funcionalidades
tab1, tab2, tab3, tab4 = st.tabs(["Cadastrar Baia", "Alocar Animal", "Realocar/Remover", "Visualizar Ocupação"])

with tab1:
    st.header("Cadastrar Nova Baia")
    
    col1, col2 = st.columns(2)
    
    with col1:
        identificacao = st.text_input("Identificação da Baia", placeholder="Ex: Baia 01", help="Código ou número de identificação da baia")
        
        setor = st.selectbox(
            "Setor",
            options=["Creche", "Crescimento", "Terminação", "Gestação", "Maternidade", "Reprodução", "Quarentena", "Outro"],
            help="Setor da granja onde a baia está localizada"
        )
        
        capacidade = st.number_input(
            "Capacidade (número de animais)",
            min_value=1,
            max_value=100,
            value=10,
            help="Número máximo de animais que a baia pode comportar"
        )
        
        tipo_piso = st.selectbox(
            "Tipo de Piso",
            options=["Concreto", "Ripado", "Semi-ripado", "Cama Sobreposta", "Outro"],
            help="Material do piso da baia"
        )
        
    with col2:
        largura = st.number_input(
            "Largura (metros)",
            min_value=0.1,
            max_value=30.0,
            value=3.0,
            step=0.1,
            format="%.1f",
            help="Largura da baia em metros"
        )
        
        comprimento = st.number_input(
            "Comprimento (metros)",
            min_value=0.1,
            max_value=30.0,
            value=4.0,
            step=0.1,
            format="%.1f",
            help="Comprimento da baia em metros"
        )
        
        # Calcular a área automaticamente
        area = largura * comprimento
        st.metric("Área (m²)", f"{area:.2f}")
        
        observacao = st.text_area(
            "Observações",
            placeholder="Informações adicionais sobre a baia...",
            help="Notas ou observações relevantes sobre a baia"
        )
    
    # Botão para cadastrar
    if st.button("Cadastrar Baia"):
        # Verificar se já existe uma baia com essa identificação
        if not pens_df.empty and identificacao in pens_df['identificacao'].values:
            st.error(f"Já existe uma baia cadastrada com a identificação '{identificacao}'. Por favor, escolha outra identificação.")
        else:
            # Criar novo registro
            nova_baia = {
                'id_baia': str(uuid.uuid4()),
                'identificacao': identificacao,
                'setor': setor,
                'capacidade': capacidade,
                'largura': largura,
                'comprimento': comprimento,
                'area': area,
                'tipo_piso': tipo_piso,
                'data_cadastro': datetime.now().strftime('%Y-%m-%d'),
                'observacao': observacao
            }
            
            # Adicionar ao DataFrame
            if pens_df.empty:
                pens_df = pd.DataFrame([nova_baia])
            else:
                pens_df = pd.concat([pens_df, pd.DataFrame([nova_baia])], ignore_index=True)
            
            # Salvar DataFrame atualizado
            save_pens(pens_df)
            
            st.success(f"Baia '{identificacao}' cadastrada com sucesso!")
            st.rerun()

with tab2:
    st.header("Alocar Animal em Baia")
    
    if pens_df.empty:
        st.warning("Não há baias cadastradas. Por favor, cadastre uma baia primeiro.")
    elif animals_df.empty:
        st.warning("Não há animais cadastrados. Por favor, cadastre um animal primeiro.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            # Selecionar animal
            selected_animal = st.selectbox(
                "Selecione o Animal",
                options=animals_df['id_animal'].tolist(),
                format_func=lambda x: f"{animals_df[animals_df['id_animal'] == x]['identificacao'].iloc[0]} - {animals_df[animals_df['id_animal'] == x]['nome'].iloc[0]}" if animals_df[animals_df['id_animal'] == x]['nome'].iloc[0] else animals_df[animals_df['id_animal'] == x]['identificacao'].iloc[0]
            )
            
            # Exibir detalhes do animal
            animal_details = get_animal_details(selected_animal, animals_df)
            if animal_details is not None:
                st.write(f"**Categoria:** {animal_details['categoria']}")
                if 'sexo' in animal_details:
                    st.write(f"**Sexo:** {animal_details['sexo']}")
            
            # Verificar se o animal já está alocado
            animal_allocated = False
            current_pen = None
            
            if not allocations_df.empty and selected_animal in allocations_df['id_animal'].values:
                current_allocations = allocations_df[(allocations_df['id_animal'] == selected_animal) & 
                                                    (allocations_df['data_saida'].isna())]
                
                if not current_allocations.empty:
                    animal_allocated = True
                    current_pen_id = current_allocations.iloc[0]['id_baia']
                    if not pens_df.empty and current_pen_id in pens_df['id_baia'].values:
                        current_pen = pens_df[pens_df['id_baia'] == current_pen_id].iloc[0]['identificacao']
            
            if animal_allocated:
                st.warning(f"Este animal já está alocado na baia '{current_pen}'. Para realocar, use a aba 'Realocar/Remover'.")
        
        with col2:
            # Filtrar baias disponíveis com base na categoria do animal, se possível
            animal_category = animal_details['categoria'] if animal_details is not None and 'categoria' in animal_details else None
            available_pens = get_available_pens(pens_df, allocations_df, animal_category)
            
            if available_pens.empty:
                st.error("Não há baias disponíveis para alocar este animal.")
            else:
                selected_pen = st.selectbox(
                    "Selecione a Baia",
                    options=available_pens['id_baia'].tolist(),
                    format_func=lambda x: f"{available_pens[available_pens['id_baia'] == x]['identificacao'].iloc[0]} - Setor: {available_pens[available_pens['id_baia'] == x]['setor'].iloc[0]} ({available_pens[available_pens['id_baia'] == x]['ocupacao_atual'].iloc[0]}/{available_pens[available_pens['id_baia'] == x]['capacidade'].iloc[0]} ocupada)"
                )
                
                data_entrada = st.date_input(
                    "Data de Entrada",
                    value=datetime.now().date()
                )
                
                observacao = st.text_area("Observações")
                
                # Botão para alocar animal
                if st.button("Alocar Animal") and not animal_allocated:
                    # Criar novo registro de alocação
                    nova_alocacao = {
                        'id_alocacao': str(uuid.uuid4()),
                        'id_baia': selected_pen,
                        'id_animal': selected_animal,
                        'data_entrada': data_entrada.strftime('%Y-%m-%d'),
                        'data_saida': None,
                        'motivo_saida': None,
                        'status': 'Ativo',
                        'observacao': observacao
                    }
                    
                    # Adicionar ao DataFrame
                    if allocations_df.empty:
                        allocations_df = pd.DataFrame([nova_alocacao])
                    else:
                        allocations_df = pd.concat([allocations_df, pd.DataFrame([nova_alocacao])], ignore_index=True)
                    
                    # Salvar DataFrame atualizado
                    save_pen_allocations(allocations_df)
                    
                    st.success(f"Animal alocado com sucesso!")
                    st.rerun()

with tab3:
    st.header("Realocar ou Remover Animal")
    
    if allocations_df.empty:
        st.warning("Não há alocações cadastradas.")
    else:
        # Filtrar apenas alocações ativas
        active_allocations = allocations_df[allocations_df['data_saida'].isna()]
        
        if active_allocations.empty:
            st.warning("Não há alocações ativas no momento.")
        else:
            # Preparar dados para exibição
            display_allocations = active_allocations.copy()
            
            # Adicionar informações do animal e da baia
            display_allocations['animal'] = display_allocations['id_animal'].apply(
                lambda x: f"{animals_df[animals_df['id_animal'] == x]['identificacao'].iloc[0]}" if x in animals_df['id_animal'].values else "Desconhecido"
            )
            
            display_allocations['baia'] = display_allocations['id_baia'].apply(
                lambda x: f"{pens_df[pens_df['id_baia'] == x]['identificacao'].iloc[0]}" if x in pens_df['id_baia'].values else "Desconhecida"
            )
            
            # Selecionar alocação
            selected_allocation_id = st.selectbox(
                "Selecione a Alocação",
                options=display_allocations['id_alocacao'].tolist(),
                format_func=lambda x: f"Animal: {display_allocations[display_allocations['id_alocacao'] == x]['animal'].iloc[0]} - Baia: {display_allocations[display_allocations['id_alocacao'] == x]['baia'].iloc[0]} (desde {display_allocations[display_allocations['id_alocacao'] == x]['data_entrada'].iloc[0]})"
            )
            
            selected_allocation = display_allocations[display_allocations['id_alocacao'] == selected_allocation_id].iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Remover da Baia")
                
                data_saida = st.date_input(
                    "Data de Saída",
                    value=datetime.now().date()
                )
                
                motivo_saida = st.selectbox(
                    "Motivo da Saída",
                    options=["Transferência", "Venda", "Óbito", "Outro"]
                )
                
                observacao_saida = st.text_area("Observações sobre a Saída")
                
                if st.button("Remover Animal da Baia"):
                    # Atualizar registro existente
                    allocations_df.loc[allocations_df['id_alocacao'] == selected_allocation_id, 'data_saida'] = data_saida.strftime('%Y-%m-%d')
                    allocations_df.loc[allocations_df['id_alocacao'] == selected_allocation_id, 'motivo_saida'] = motivo_saida
                    allocations_df.loc[allocations_df['id_alocacao'] == selected_allocation_id, 'status'] = 'Inativo'
                    allocations_df.loc[allocations_df['id_alocacao'] == selected_allocation_id, 'observacao'] = observacao_saida
                    
                    # Salvar DataFrame atualizado
                    save_pen_allocations(allocations_df)
                    
                    st.success(f"Animal removido da baia com sucesso!")
                    st.rerun()
            
            with col2:
                st.subheader("Realocar para Outra Baia")
                
                # Filtrar baias disponíveis
                animal_id = selected_allocation['id_animal']
                animal_details = get_animal_details(animal_id, animals_df)
                animal_category = animal_details['categoria'] if animal_details is not None and 'categoria' in animal_details else None
                
                available_pens = get_available_pens(pens_df, allocations_df, animal_category)
                
                if available_pens.empty:
                    st.error("Não há baias disponíveis para realocar este animal.")
                else:
                    new_pen = st.selectbox(
                        "Selecione a Nova Baia",
                        options=available_pens['id_baia'].tolist(),
                        format_func=lambda x: f"{available_pens[available_pens['id_baia'] == x]['identificacao'].iloc[0]} - Setor: {available_pens[available_pens['id_baia'] == x]['setor'].iloc[0]} ({available_pens[available_pens['id_baia'] == x]['ocupacao_atual'].iloc[0]}/{available_pens[available_pens['id_baia'] == x]['capacidade'].iloc[0]} ocupada)"
                    )
                    
                    data_realocacao = st.date_input(
                        "Data da Realocação",
                        value=datetime.now().date()
                    )
                    
                    observacao_realocacao = st.text_area("Observações sobre a Realocação")
                    
                    if st.button("Realocar Animal"):
                        # 1. Marcar a alocação atual como encerrada
                        allocations_df.loc[allocations_df['id_alocacao'] == selected_allocation_id, 'data_saida'] = data_realocacao.strftime('%Y-%m-%d')
                        allocations_df.loc[allocations_df['id_alocacao'] == selected_allocation_id, 'motivo_saida'] = "Transferência"
                        allocations_df.loc[allocations_df['id_alocacao'] == selected_allocation_id, 'status'] = 'Inativo'
                        allocations_df.loc[allocations_df['id_alocacao'] == selected_allocation_id, 'observacao'] = f"Realocado para outra baia. {observacao_realocacao}"
                        
                        # 2. Criar nova alocação
                        nova_alocacao = {
                            'id_alocacao': str(uuid.uuid4()),
                            'id_baia': new_pen,
                            'id_animal': animal_id,
                            'data_entrada': data_realocacao.strftime('%Y-%m-%d'),
                            'data_saida': None,
                            'motivo_saida': None,
                            'status': 'Ativo',
                            'observacao': f"Realocado de outra baia. {observacao_realocacao}"
                        }
                        
                        # Adicionar ao DataFrame
                        allocations_df = pd.concat([allocations_df, pd.DataFrame([nova_alocacao])], ignore_index=True)
                        
                        # Salvar DataFrame atualizado
                        save_pen_allocations(allocations_df)
                        
                        st.success(f"Animal realocado com sucesso!")
                        st.rerun()

with tab4:
    st.header("Visualizar Ocupação das Baias")
    
    if pens_df.empty:
        st.warning("Não há baias cadastradas.")
    else:
        # Preparar dados de ocupação
        pens_occupancy = pens_df.copy()
        pens_occupancy['ocupacao_atual'] = pens_occupancy['id_baia'].apply(
            lambda x: get_pen_occupancy(x, allocations_df)
        )
        pens_occupancy['vagas_disponiveis'] = pens_occupancy['capacidade'] - pens_occupancy['ocupacao_atual']
        pens_occupancy['percentual_ocupacao'] = (pens_occupancy['ocupacao_atual'] / pens_occupancy['capacidade'] * 100).round(1)
        
        # Mostrar dados de todas as baias
        setor_filter = st.multiselect(
            "Filtrar por Setor",
            options=pens_occupancy['setor'].unique(),
            default=pens_occupancy['setor'].unique()
        )
        
        filtered_pens = pens_occupancy[pens_occupancy['setor'].isin(setor_filter)]
        
        st.write("### Ocupação Atual das Baias")
        
        # Exibir tabela de ocupação
        st.dataframe(
            filtered_pens[[
                'identificacao', 'setor', 'capacidade', 'ocupacao_atual', 
                'vagas_disponiveis', 'percentual_ocupacao', 'area'
            ]].rename(columns={
                'identificacao': 'Baia',
                'setor': 'Setor',
                'capacidade': 'Capacidade Total',
                'ocupacao_atual': 'Ocupação Atual',
                'vagas_disponiveis': 'Vagas Disponíveis',
                'percentual_ocupacao': '% Ocupação',
                'area': 'Área (m²)'
            }).sort_values('Setor')
        )
        
        # Visualizar graficamente
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de ocupação por baia
            fig_bars = px.bar(
                filtered_pens,
                x='identificacao',
                y=['ocupacao_atual', 'vagas_disponiveis'],
                title="Ocupação e Disponibilidade por Baia",
                labels={
                    'identificacao': 'Baia',
                    'value': 'Número de Animais',
                    'variable': 'Status'
                },
                barmode='stack',
                color_discrete_map={
                    'ocupacao_atual': '#FF4B4B',
                    'vagas_disponiveis': '#4BD964'
                }
            )
            fig_bars.update_layout(legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ))
            st.plotly_chart(fig_bars, use_container_width=True)
        
        with col2:
            # Gráfico de ocupação por setor
            setor_summary = filtered_pens.groupby('setor').agg({
                'capacidade': 'sum',
                'ocupacao_atual': 'sum'
            }).reset_index()
            
            setor_summary['vagas_disponiveis'] = setor_summary['capacidade'] - setor_summary['ocupacao_atual']
            setor_summary['percentual_ocupacao'] = (setor_summary['ocupacao_atual'] / setor_summary['capacidade'] * 100).round(1)
            
            fig_pie = px.pie(
                setor_summary,
                values='ocupacao_atual',
                names='setor',
                title="Distribuição de Animais por Setor",
                hole=0.4
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # Lista de animais por baia selecionada
        st.write("### Detalhes de Ocupação por Baia")
        
        selected_pen_id = st.selectbox(
            "Selecione uma Baia para ver os Animais",
            options=filtered_pens['id_baia'].tolist(),
            format_func=lambda x: f"{filtered_pens[filtered_pens['id_baia'] == x]['identificacao'].iloc[0]} ({filtered_pens[filtered_pens['id_baia'] == x]['ocupacao_atual'].iloc[0]}/{filtered_pens[filtered_pens['id_baia'] == x]['capacidade'].iloc[0]} animais)"
        )
        
        if not allocations_df.empty:
            # Listar animais na baia selecionada
            pen_animals = allocations_df[
                (allocations_df['id_baia'] == selected_pen_id) & 
                (allocations_df['data_saida'].isna())
            ]
            
            if not pen_animals.empty:
                # Adicionar informações do animal
                pen_animals['animal_id'] = pen_animals['id_animal']
                pen_animals['identificacao'] = pen_animals['animal_id'].apply(
                    lambda x: animals_df[animals_df['id_animal'] == x]['identificacao'].iloc[0] if x in animals_df['id_animal'].values else "Desconhecido"
                )
                pen_animals['categoria'] = pen_animals['animal_id'].apply(
                    lambda x: animals_df[animals_df['id_animal'] == x]['categoria'].iloc[0] if x in animals_df['id_animal'].values else "Desconhecida" 
                )
                
                st.dataframe(
                    pen_animals[[
                        'identificacao', 'categoria', 'data_entrada', 'observacao'
                    ]].rename(columns={
                        'identificacao': 'Animal',
                        'categoria': 'Categoria',
                        'data_entrada': 'Data de Entrada',
                        'observacao': 'Observação'
                    })
                )
            else:
                st.info("Esta baia está vazia no momento.")
        else:
            st.info("Não há animais alocados em nenhuma baia.")