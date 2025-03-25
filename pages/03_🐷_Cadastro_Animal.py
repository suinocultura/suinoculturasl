import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import os
import sys

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import load_animals, save_animals, date_to_pig_calendar, pig_calendar_to_date, check_permission
from check_page_permissions import check_page_permission

st.set_page_config(
    page_title="Cadastro de Animais",
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
if not check_page_permission():
    st.error("Você não tem permissão para acessar esta página.")
    st.stop()


st.title("Cadastro de Animais 🐷")
st.write("Registre novos animais e gerencie os existentes nesta página.")

# Load existing data
animals_df = load_animals()

# Tab for data entry and visualization
tab1, tab2 = st.tabs(["Cadastrar Novo Animal", "Visualizar/Editar Animais"])

with tab1:
    st.header("Cadastrar Novo Animal")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        identificacao = st.text_input("Identificação")
        brinco = st.text_input("Número do Brinco")
        tatuagem = st.text_input("Tatuagem")
        nome = st.text_input("Nome (opcional)")
        
    with col2:
        categoria = st.selectbox(
            "Categoria",
            options=["Matriz", "Reprodutor", "Leitão", "Leitoa", "Recria", "Engorda"]
        )
        
        # Opção para escolher o formato da data de nascimento
        data_format = st.radio(
            "Formato da Data de Nascimento",
            options=["Calendário Normal", "Calendário Suíno (1-1000)"],
            horizontal=True
        )
        
        if data_format == "Calendário Normal":
            data_nascimento = st.date_input(
                "Data de Nascimento",
                value=datetime.now().date()
            )
            # Mostra o dia equivalente no calendário suíno
            pig_day = date_to_pig_calendar(data_nascimento)
            st.caption(f"Dia do calendário suíno: {pig_day}")
        else:
            # Entrada para o calendário suíno
            pig_day = st.number_input(
                "Dia no Calendário Suíno (1-1000)",
                min_value=1,
                max_value=1000,
                value=date_to_pig_calendar(datetime.now().date())
            )
            
            # Ano de referência
            ref_year = st.selectbox(
                "Ano de Referência",
                options=list(range(datetime.now().year - 5, datetime.now().year + 1)),
                index=5  # Seleciona o ano atual por padrão
            )
            
            # Converte para data normal
            data_nascimento = pig_calendar_to_date(pig_day, ref_year)
            st.caption(f"Data equivalente: {data_nascimento.strftime('%d/%m/%Y')}")
        
        sexo = st.selectbox(
            "Sexo",
            options=["Fêmea", "Macho"]
        )
        
    with col3:
        raca = st.text_input("Raça")
        origem = st.text_input("Origem/Procedência")
        st.info("Para gerenciar irmãs de cio, use a página 'Irmãs de Cio' após cadastrar os animais.")
        observacoes = st.text_area("Observações")
    
    # Submit button
    if st.button("Cadastrar Animal"):
        if not identificacao:
            st.error("A identificação do animal é obrigatória.")
        else:
            # Check if ID already exists
            if not animals_df.empty and identificacao in animals_df['identificacao'].values:
                st.error(f"Já existe um animal com a identificação {identificacao}.")
            else:
                # Create new animal record
                new_animal = {
                    'id_animal': str(uuid.uuid4()),
                    'identificacao': identificacao,
                    'brinco': brinco,
                    'tatuagem': tatuagem,
                    'nome': nome,
                    'categoria': categoria,
                    'data_nascimento': data_nascimento.strftime('%Y-%m-%d'),
                    'sexo': sexo,
                    'raca': raca,
                    'origem': origem,

                    'data_cadastro': datetime.now().strftime('%Y-%m-%d'),
                    'observacao': observacoes
                }
                
                # Add to DataFrame
                if animals_df.empty:
                    animals_df = pd.DataFrame([new_animal])
                else:
                    animals_df = pd.concat([animals_df, pd.DataFrame([new_animal])], ignore_index=True)
                
                # Save updated DataFrame
                save_animals(animals_df)
                
                st.success(f"Animal {identificacao} cadastrado com sucesso!")
                st.rerun()

with tab2:
    st.header("Animais Cadastrados")
    
    # Search and filter options
    search_col1, search_col2 = st.columns([1, 2])
    
    with search_col1:
        filter_category = st.multiselect(
            "Filtrar por Categoria",
            options=["Matriz", "Reprodutor", "Leitão", "Leitoa", "Recria", "Engorda"],
            default=[]
        )
    
    with search_col2:
        search_term = st.text_input("Buscar por Identificação ou Nome")
    
    # Apply filters
    filtered_df = animals_df.copy()
    
    if filter_category:
        filtered_df = filtered_df[filtered_df['categoria'].isin(filter_category)]
        
    if search_term:
        id_mask = filtered_df['identificacao'].str.contains(search_term, case=False, na=False)
        name_mask = filtered_df['nome'].str.contains(search_term, case=False, na=False)
        filtered_df = filtered_df[id_mask | name_mask]
    
    # Display data
    if not filtered_df.empty:
        st.dataframe(
            filtered_df[[
                'identificacao', 'nome', 'categoria', 'data_nascimento', 
                'sexo', 'raca', 'origem', 'data_cadastro'
            ]],
            use_container_width=True
        )
        
        # Animal details
        st.subheader("Detalhes do Animal")
        selected_id = st.selectbox(
            "Selecione um animal para ver detalhes:",
            options=filtered_df['identificacao'].tolist(),
            format_func=lambda x: f"{x} - {filtered_df[filtered_df['identificacao'] == x]['nome'].iloc[0]}" if filtered_df[filtered_df['identificacao'] == x]['nome'].iloc[0] else x
        )
        
        if selected_id:
            selected_animal = filtered_df[filtered_df['identificacao'] == selected_id].iloc[0]
            animal_id = selected_animal['id_animal']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Identificação:** {selected_animal['identificacao']}")
                st.write(f"**Brinco:** {selected_animal.get('brinco', 'N/A')}")
                st.write(f"**Tatuagem:** {selected_animal.get('tatuagem', 'N/A')}")
                st.write(f"**Nome:** {selected_animal['nome']}")
                st.write(f"**Categoria:** {selected_animal['categoria']}")
                
                # Exibir a data de nascimento em ambos os formatos
                birth_date = pd.to_datetime(selected_animal['data_nascimento']).date()
                pig_day = date_to_pig_calendar(birth_date)
                st.write(f"**Data de Nascimento:** {birth_date.strftime('%d/%m/%Y')}")
                st.write(f"**Dia no Calendário Suíno:** {pig_day}")
                
            with col2:
                st.write(f"**Sexo:** {selected_animal['sexo']}")
                st.write(f"**Raça:** {selected_animal['raca']}")
                st.write(f"**Origem:** {selected_animal['origem']}")
                # Campo de irmãs de ninhada removido
                # Campo de irmãs de cio removido - gerenciado na página específica
                st.write(f"**Data de Cadastro:** {selected_animal['data_cadastro']}")
            
            # Edit animal
            st.subheader("Editar Animal")
            
            edit_col1, edit_col2, edit_col3 = st.columns(3)
            
            with edit_col1:
                new_identificacao = st.text_input("Identificação", value=selected_animal['identificacao'], key="edit_id")
                new_brinco = st.text_input("Brinco", value=selected_animal.get('brinco', ''), key="edit_brinco")
                new_tatuagem = st.text_input("Tatuagem", value=selected_animal.get('tatuagem', ''), key="edit_tatuagem")
                
            with edit_col2:
                new_nome = st.text_input("Nome", value=selected_animal['nome'], key="edit_nome")
                new_categoria = st.selectbox(
                    "Categoria",
                    options=["Matriz", "Reprodutor", "Leitão", "Leitoa", "Recria", "Engorda"],
                    index=["Matriz", "Reprodutor", "Leitão", "Leitoa", "Recria", "Engorda"].index(selected_animal['categoria']),
                    key="edit_categoria"
                )
                
                # Opção para escolher o formato da data de nascimento na edição
                data_format_edit = st.radio(
                    "Formato da Data de Nascimento",
                    options=["Calendário Normal", "Calendário Suíno (1-1000)"],
                    horizontal=True,
                    key="edit_data_format"
                )
                
                # Converter a data de nascimento existente
                birth_date = pd.to_datetime(selected_animal['data_nascimento']).date()
                
                if data_format_edit == "Calendário Normal":
                    new_data_nascimento = st.date_input(
                        "Data de Nascimento",
                        value=birth_date,
                        key="edit_birth_date"
                    )
                    # Mostra o dia equivalente no calendário suíno
                    pig_day_edit = date_to_pig_calendar(new_data_nascimento)
                    st.caption(f"Dia do calendário suíno: {pig_day_edit}")
                else:
                    # Entrada para o calendário suíno
                    pig_day_edit = st.number_input(
                        "Dia no Calendário Suíno (1-1000)",
                        min_value=1,
                        max_value=1000,
                        value=date_to_pig_calendar(birth_date),
                        key="edit_pig_day"
                    )
                    
                    # Ano de referência
                    ref_year_edit = st.selectbox(
                        "Ano de Referência",
                        options=list(range(datetime.now().year - 5, datetime.now().year + 1)),
                        index=5,  # Seleciona o ano atual por padrão
                        key="edit_ref_year"
                    )
                    
                    # Converte para data normal
                    new_data_nascimento = pig_calendar_to_date(pig_day_edit, ref_year_edit)
                    st.caption(f"Data equivalente: {new_data_nascimento.strftime('%d/%m/%Y')}")
                
                st.info("Para gerenciar grupos de irmãs de cio, use a página 'Irmãs de Cio'.")
                
            with edit_col3:
                new_raca = st.text_input("Raça", value=selected_animal['raca'], key="edit_raca")
                new_origem = st.text_input("Origem", value=selected_animal['origem'], key="edit_origem")
                new_observacoes = st.text_area("Observações", value=selected_animal.get('observacao', ''), key="edit_obs")
            
            if st.button("Atualizar Animal"):
                # Update animal in DataFrame
                animals_df.loc[animals_df['id_animal'] == animal_id, 'identificacao'] = new_identificacao
                animals_df.loc[animals_df['id_animal'] == animal_id, 'nome'] = new_nome
                animals_df.loc[animals_df['id_animal'] == animal_id, 'categoria'] = new_categoria
                animals_df.loc[animals_df['id_animal'] == animal_id, 'raca'] = new_raca
                animals_df.loc[animals_df['id_animal'] == animal_id, 'origem'] = new_origem
                animals_df.loc[animals_df['id_animal'] == animal_id, 'observacao'] = new_observacoes
                
                # Atualizar a data de nascimento
                animals_df.loc[animals_df['id_animal'] == animal_id, 'data_nascimento'] = new_data_nascimento.strftime('%Y-%m-%d')
                
                # Update new fields if they exist
                if 'brinco' in animals_df.columns:
                    animals_df.loc[animals_df['id_animal'] == animal_id, 'brinco'] = new_brinco
                if 'tatuagem' in animals_df.columns:
                    animals_df.loc[animals_df['id_animal'] == animal_id, 'tatuagem'] = new_tatuagem
                # Campos de gestão de irmãs removidos - gerenciados na página específica
                
                # Save updated DataFrame
                save_animals(animals_df)
                
                st.success(f"Animal {new_identificacao} atualizado com sucesso!")
                st.rerun()
            
            # Delete animal
            if st.button("Excluir Animal", type="primary", use_container_width=True):
                # Remove animal from DataFrame
                animals_df = animals_df[animals_df['id_animal'] != animal_id]
                
                # Save updated DataFrame
                save_animals(animals_df)
                
                st.success(f"Animal {selected_animal['identificacao']} excluído com sucesso!")
                st.rerun()
    else:
        st.info("Nenhum animal encontrado. Cadastre novos animais na aba 'Cadastrar Novo Animal'.")
