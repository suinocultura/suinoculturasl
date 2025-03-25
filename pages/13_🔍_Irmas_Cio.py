import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import uuid
import os
import sys
import plotly.express as px

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import (
    load_animals,
    save_animals,
    load_breeding_cycles,
    save_breeding_cycles
,
    check_permission
)

st.set_page_config(
    page_title="Irmãs de Cio",
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
if not check_permission(st.session_state.current_user, 'manage_reproduction'):
    st.error("Você não tem permissão para acessar esta página.")
    st.stop()


st.title("Gerenciamento de Irmãs de Cio 🔄")
st.write("Agrupe e gerencie fêmeas que entram em cio juntas para melhor manejo reprodutivo.")

# Load existing data
animals_df = load_animals()
breeding_df = load_breeding_cycles()

# Filter only female animals (matrizes and leitoas)
if not animals_df.empty:
    female_animals = animals_df[
        (animals_df['sexo'] == 'Fêmea') & 
        (animals_df['categoria'].isin(['Matriz', 'Leitoa']))
    ].copy()
else:
    female_animals = pd.DataFrame()

# Create tabs for different sections
tab1, tab2 = st.tabs(["Criar Grupo de Irmãs de Cio", "Visualizar Grupos"])

with tab1:
    st.header("Criar Novo Grupo de Irmãs de Cio")

    if not female_animals.empty:
        # Form para criar grupo de irmãs de cio
        with st.form("grupo_irmas_cio"):
            st.subheader("Selecione as fêmeas que entram em cio juntas")
            
            # Listar todas as fêmeas disponíveis
            selected_animals = st.multiselect(
                "Selecione as matrizes/leitoas que sincronizam o cio",
                options=female_animals['id_animal'].tolist(),
                format_func=lambda x: f"{female_animals[female_animals['id_animal'] == x]['identificacao'].iloc[0]} - {female_animals[female_animals['id_animal'] == x]['nome'].iloc[0] if pd.notna(female_animals[female_animals['id_animal'] == x]['nome'].iloc[0]) else 'Sem nome'}"
            )
            
            # Data estimada do cio comum do grupo
            data_estimada = st.date_input(
                "Data estimada do próximo cio do grupo",
                value=datetime.now().date()
            )
            
            # Nome do grupo (opcional)
            nome_grupo = st.text_input("Nome do grupo (opcional)")
            
            # Observações
            observacoes = st.text_area("Observações sobre o grupo")
            
            # Botão de submissão
            submit_button = st.form_submit_button("Criar Grupo de Irmãs de Cio")
            
            if submit_button:
                if len(selected_animals) < 2:
                    st.error("Selecione pelo menos duas fêmeas para formar um grupo de irmãs de cio.")
                else:
                    grupo_id = str(uuid.uuid4())
                    success_count = 0

                    # Atualizar o ciclo reprodutivo de cada animal selecionado
                    for animal_id in selected_animals:
                        # Verificar se já existe um ciclo para este animal
                        animal_rows = breeding_df[breeding_df['id_animal'] == animal_id]
                        num_ciclo = 1
                        
                        if not animal_rows.empty:
                            # Pegar o último ciclo e incrementar
                            last_cycle = animal_rows.sort_values('data_cio', ascending=False).iloc[0]
                            num_ciclo = last_cycle['numero_ciclo'] + 1
                        
                        # Criar novo registro de ciclo
                        novo_ciclo = {
                            'id_ciclo': str(uuid.uuid4()),
                            'id_animal': animal_id,
                            'numero_ciclo': num_ciclo,
                            'data_cio': data_estimada.strftime('%Y-%m-%d'),
                            'intensidade_cio': 'Normal',
                            'irmas_cio': ','.join([a for a in selected_animals if a != animal_id]),
                            'quantidade_irmas_cio': len(selected_animals) - 1,
                            'status': 'Aguardando',
                            'observacao': f"Grupo de irmãs de cio: {nome_grupo if nome_grupo else grupo_id}. {observacoes}"
                        }
                        
                        # Adicionar à DataFrame
                        if breeding_df.empty:
                            breeding_df = pd.DataFrame([novo_ciclo])
                        else:
                            breeding_df = pd.concat([breeding_df, pd.DataFrame([novo_ciclo])], ignore_index=True)
                        
                        success_count += 1
                    
                    # Salvar DataFrame atualizado
                    save_breeding_cycles(breeding_df)
                    
                    st.success(f"Grupo de {success_count} irmãs de cio criado com sucesso!")
                    st.rerun()
    else:
        st.warning("Não há fêmeas (matrizes ou leitoas) cadastradas no sistema. Cadastre matrizes primeiro.")

with tab2:
    st.header("Grupos de Irmãs de Cio")
    
    if not breeding_df.empty and not female_animals.empty:
        # Agrupar ciclos com irmãs de cio
        cycles_with_sisters = breeding_df[breeding_df['irmas_cio'].notna() & (breeding_df['irmas_cio'] != '')]
        
        if not cycles_with_sisters.empty:
            # Agrupar por data para identificar grupos
            cycles_with_sisters['data_cio'] = pd.to_datetime(cycles_with_sisters['data_cio'])
            
            # Mostrar grupos por data
            unique_dates = cycles_with_sisters['data_cio'].dt.strftime('%Y-%m-%d').unique()
            
            selected_date = st.selectbox(
                "Selecione a data do grupo", 
                options=unique_dates,
                format_func=lambda x: f"{pd.to_datetime(x).strftime('%d/%m/%Y')}"
            )
            
            if selected_date:
                # Filtrar ciclos desta data
                date_group = cycles_with_sisters[cycles_with_sisters['data_cio'].dt.strftime('%Y-%m-%d') == selected_date]
                
                # Adicionar informações dos animais
                display_df = pd.merge(
                    date_group,
                    animals_df[['id_animal', 'identificacao', 'nome', 'categoria', 'brinco']],
                    on='id_animal',
                    how='left'
                )
                
                st.subheader(f"Grupo de cio de {pd.to_datetime(selected_date).strftime('%d/%m/%Y')}")
                
                # Buscar informações dos animais no grupo
                animals_in_group = []
                for _, row in display_df.iterrows():
                    animal_info = {
                        'id_ciclo': row['id_ciclo'],
                        'id_animal': row['id_animal'],
                        'identificacao': row['identificacao'],
                        'nome': row['nome'] if pd.notna(row['nome']) else '',
                        'categoria': row['categoria'],
                        'brinco': row['brinco'] if pd.notna(row['brinco']) else 'N/A',
                        'status': row['status'],
                        'observacao': row['observacao'] if pd.notna(row['observacao']) else ''
                    }
                    animals_in_group.append(animal_info)
                
                # Mostrar animais do grupo
                group_df = pd.DataFrame(animals_in_group)
                st.dataframe(
                    group_df[[
                        'identificacao', 'nome', 'categoria', 'brinco', 'status'
                    ]].rename(columns={
                        'identificacao': 'Identificação',
                        'nome': 'Nome',
                        'categoria': 'Categoria',
                        'brinco': 'Brinco',
                        'status': 'Status'
                    }),
                    use_container_width=True
                )
                
                # Opções para editar grupo
                st.subheader("Gerenciar Grupo")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Adicionar animal ao grupo
                    st.write("Adicionar animal ao grupo:")
                    
                    # Buscar animais que não fazem parte deste grupo
                    animals_not_in_group = female_animals[~female_animals['id_animal'].isin(group_df['id_animal'])].copy()
                    
                    if not animals_not_in_group.empty:
                        new_animal = st.selectbox(
                            "Selecione um animal para adicionar",
                            options=animals_not_in_group['id_animal'].tolist(),
                            format_func=lambda x: f"{animals_not_in_group[animals_not_in_group['id_animal'] == x]['identificacao'].iloc[0]} - {animals_not_in_group[animals_not_in_group['id_animal'] == x]['nome'].iloc[0] if pd.notna(animals_not_in_group[animals_not_in_group['id_animal'] == x]['nome'].iloc[0]) else 'Sem nome'}"
                        )
                        
                        if st.button("Adicionar ao Grupo"):
                            # Pegar os IDs de todos os animais do grupo
                            animals_ids = group_df['id_animal'].tolist()
                            animals_ids.append(new_animal)
                            
                            # Pegar uma observação do grupo (todas devem ser iguais)
                            group_obs = group_df['observacao'].iloc[0] if not group_df['observacao'].empty else ""
                            
                            # Criar novo ciclo para o animal adicionado
                            num_ciclo = 1
                            animal_rows = breeding_df[breeding_df['id_animal'] == new_animal]
                            if not animal_rows.empty:
                                last_cycle = animal_rows.sort_values('data_cio', ascending=False).iloc[0]
                                num_ciclo = last_cycle['numero_ciclo'] + 1
                            
                            # Criar novo registro de ciclo
                            novo_ciclo = {
                                'id_ciclo': str(uuid.uuid4()),
                                'id_animal': new_animal,
                                'numero_ciclo': num_ciclo,
                                'data_cio': pd.to_datetime(selected_date).strftime('%Y-%m-%d'),
                                'intensidade_cio': 'Normal',
                                'irmas_cio': ','.join([a for a in animals_ids if a != new_animal]),
                                'quantidade_irmas_cio': len(animals_ids) - 1,
                                'status': 'Aguardando',
                                'observacao': group_obs
                            }
                            
                            # Adicionar à DataFrame
                            breeding_df = pd.concat([breeding_df, pd.DataFrame([novo_ciclo])], ignore_index=True)
                            
                            # Atualizar registros dos outros animais
                            for animal_id in animals_ids:
                                if animal_id != new_animal:
                                    # Encontrar o ciclo deste animal no grupo
                                    animal_cycle = date_group[date_group['id_animal'] == animal_id]
                                    if not animal_cycle.empty:
                                        cycle_id = animal_cycle.iloc[0]['id_ciclo']
                                        breeding_df.loc[breeding_df['id_ciclo'] == cycle_id, 'irmas_cio'] = ','.join([a for a in animals_ids if a != animal_id])
                                        breeding_df.loc[breeding_df['id_ciclo'] == cycle_id, 'quantidade_irmas_cio'] = len(animals_ids) - 1
                            
                            # Salvar DataFrame atualizado
                            save_breeding_cycles(breeding_df)
                            
                            st.success(f"Animal adicionado ao grupo com sucesso!")
                            st.rerun()
                    else:
                        st.info("Não há mais animais disponíveis para adicionar ao grupo.")
                
                with col2:
                    # Remover animal do grupo
                    st.write("Remover animal do grupo:")
                    
                    animal_to_remove = st.selectbox(
                        "Selecione um animal para remover",
                        options=group_df['id_animal'].tolist(),
                        format_func=lambda x: f"{group_df[group_df['id_animal'] == x]['identificacao'].iloc[0]} - {group_df[group_df['id_animal'] == x]['nome'].iloc[0] if pd.notna(group_df[group_df['id_animal'] == x]['nome'].iloc[0]) else 'Sem nome'}"
                    )
                    
                    if st.button("Remover do Grupo"):
                        # Verificar se o grupo ficará com pelo menos 2 animais
                        if len(group_df) <= 2:
                            st.error("Não é possível remover este animal pois o grupo ficaria com apenas um animal. Exclua o grupo inteiro se necessário.")
                        else:
                            # Remover o animal selecionado
                            cycle_to_remove = date_group[date_group['id_animal'] == animal_to_remove].iloc[0]['id_ciclo']
                            
                            # Remover este ciclo
                            breeding_df = breeding_df[breeding_df['id_ciclo'] != cycle_to_remove]
                            
                            # Atualizar as irmãs de cio dos outros animais do grupo
                            remaining_animals = [a for a in group_df['id_animal'].tolist() if a != animal_to_remove]
                            
                            for animal_id in remaining_animals:
                                # Encontrar o ciclo deste animal no grupo
                                animal_cycle = date_group[date_group['id_animal'] == animal_id]
                                if not animal_cycle.empty:
                                    cycle_id = animal_cycle.iloc[0]['id_ciclo']
                                    breeding_df.loc[breeding_df['id_ciclo'] == cycle_id, 'irmas_cio'] = ','.join([a for a in remaining_animals if a != animal_id])
                                    breeding_df.loc[breeding_df['id_ciclo'] == cycle_id, 'quantidade_irmas_cio'] = len(remaining_animals) - 1
                            
                            # Salvar DataFrame atualizado
                            save_breeding_cycles(breeding_df)
                            
                            st.success(f"Animal removido do grupo com sucesso!")
                            st.rerun()
                
                # Excluir grupo inteiro
                st.subheader("Excluir Grupo Inteiro")
                if st.button("Excluir Todo o Grupo", type="primary"):
                    cycle_ids_to_remove = group_df['id_ciclo'].tolist()
                    
                    # Remover todos os ciclos deste grupo
                    breeding_df = breeding_df[~breeding_df['id_ciclo'].isin(cycle_ids_to_remove)]
                    
                    # Salvar DataFrame atualizado
                    save_breeding_cycles(breeding_df)
                    
                    st.success(f"Grupo excluído com sucesso!")
                    st.rerun()
        else:
            st.info("Não há grupos de irmãs de cio registrados. Crie um novo grupo na aba 'Criar Grupo de Irmãs de Cio'.")
    else:
        st.info("Não há dados suficientes para exibir grupos de irmãs de cio.")
        
# Estatísticas e visualizações
if not breeding_df.empty and 'irmas_cio' in breeding_df.columns:
    st.header("Estatísticas de Irmãs de Cio")
    
    # Filtrar ciclos com irmãs de cio
    cycles_with_sisters = breeding_df[breeding_df['irmas_cio'].notna() & (breeding_df['irmas_cio'] != '')]
    
    if not cycles_with_sisters.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Quantidade de animais por grupo
            cycles_with_sisters['quantidade_total'] = cycles_with_sisters['quantidade_irmas_cio'] + 1
            quantity_df = cycles_with_sisters.groupby('quantidade_total').size().reset_index()
            quantity_df.columns = ['Tamanho do Grupo', 'Quantidade de Grupos']
            
            fig = px.bar(
                quantity_df,
                x='Tamanho do Grupo',
                y='Quantidade de Grupos',
                title='Distribuição de Tamanho dos Grupos de Irmãs de Cio'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Grupos por mês
            cycles_with_sisters['mes'] = pd.to_datetime(cycles_with_sisters['data_cio']).dt.strftime('%Y-%m')
            months_df = cycles_with_sisters.groupby('mes').size().reset_index()
            months_df.columns = ['Mês', 'Quantidade de Grupos']
            
            # Converter para formato legível
            months_df['Mês'] = pd.to_datetime(months_df['Mês'], format='%Y-%m').dt.strftime('%b/%Y')
            
            fig = px.line(
                months_df,
                x='Mês',
                y='Quantidade de Grupos',
                title='Grupos de Irmãs de Cio por Mês',
                markers=True
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Não há dados suficientes para gerar estatísticas de irmãs de cio.")