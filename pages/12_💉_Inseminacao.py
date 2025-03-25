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
    save_breeding_cycles,
    load_insemination,
    save_insemination
,
    check_permission
)

st.set_page_config(
    page_title="Inseminação",
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


st.title("Inseminação Artificial 💉")
st.write("Registre e acompanhe inseminações artificiais das matrizes.")

# Load existing data
animals_df = load_animals()
breeding_df = load_breeding_cycles()
insemination_df = load_insemination()

# Filter only female animals (matrizes and leitoas)
female_animals = animals_df[
    (animals_df['sexo'] == 'Fêmea') & 
    (animals_df['categoria'].isin(['Matriz', 'Leitoa']))
].copy() if not animals_df.empty else pd.DataFrame()

# Create tabs for different sections
tab1, tab2 = st.tabs(["Registrar Inseminação", "Histórico de Inseminações"])

with tab1:
    st.header("Registrar Nova Inseminação")
    
    if not female_animals.empty:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Selecionar animal
            selected_animal_id = st.selectbox(
                "Selecione a Fêmea",
                options=female_animals['id_animal'].tolist(),
                format_func=lambda x: f"{female_animals[female_animals['id_animal'] == x]['identificacao'].iloc[0]} - {female_animals[female_animals['id_animal'] == x]['nome'].iloc[0]}" if female_animals[female_animals['id_animal'] == x]['nome'].iloc[0] else female_animals[female_animals['id_animal'] == x]['identificacao'].iloc[0]
            )
            
            selected_animal = female_animals[female_animals['id_animal'] == selected_animal_id].iloc[0]
            
            # Mostrar detalhes do animal selecionado
            st.write(f"**Categoria:** {selected_animal['categoria']}")
            st.write(f"**Brinco:** {selected_animal.get('brinco', 'N/A')}")
            
            # Tipo de matriz
            tipo_marran = st.selectbox(
                "Tipo de Matriz",
                options=["AM (Avó Materna)", "Avó", "Bisavó", "Matriz Comercial"],
                index=0,
                help="AM = Avó Materna, usada para produção de leitoas multiplicadoras"
            )
            
            # Data da inseminação
            data_inseminacao = st.date_input(
                "Data da Inseminação",
                value=datetime.now().date()
            )
            
        with col2:
            # Informações do sêmen
            col_semen1, col_semen2 = st.columns(2)
            with col_semen1:
                num_identificacao_semen = st.text_input("Número de Identificação do Sêmen")
            
            with col_semen2:
                linhagem_semen = st.selectbox(
                    "Linhagem do Sêmen", 
                    options=["Agroceres", "Danbred", "Topigs", "Penarlan", "Outra"],
                    help="Linhagem genética do sêmen utilizado"
                )
            
            # Idade do sêmen (opcional)
            idade_semen = st.number_input("Idade do Sêmen (dias)", min_value=0, value=0)
            
            # Dose utilizada
            dose = st.number_input("Dose Utilizada (ml)", min_value=0.0, value=80.0, step=10.0)
            
            # Ordem da dose
            ordem_dose = st.selectbox(
                "Ordem da Dose",
                options=["Primeira", "Segunda", "Terceira", "Quarta", "Quinta+"]
            )
            
        with col3:
            # Método de inseminação
            metodo_inseminacao = st.selectbox(
                "Método de Inseminação",
                options=["Tradicional", "Pós-Cervical", "Intra-Uterina Profunda"]
            )
            
            # Técnico responsável
            tecnico = st.text_input("Técnico Responsável")
            
            # Calendário suíno
            semana_suina = st.number_input("Semana do Calendário Suíno", min_value=1, max_value=52, step=1)
            
            # Observações
            observacoes = st.text_area("Observações")
            
        # Submeter formulário
        if st.button("Registrar Inseminação"):
            if not num_identificacao_semen:
                st.error("O número de identificação do sêmen é obrigatório.")
            else:
                # Create new insemination record
                novo_registro = {
                    'id_inseminacao': str(uuid.uuid4()),
                    'id_animal': selected_animal_id,
                    'brinco': selected_animal.get('brinco', ''),
                    'categoria': selected_animal['categoria'],
                    'tipo_marran': tipo_marran,
                    'data_inseminacao': data_inseminacao.strftime('%Y-%m-%d'),
                    'num_semen': num_identificacao_semen,
                    'linhagem_semen': linhagem_semen,
                    'idade_semen': idade_semen,
                    'dose': dose,
                    'ordem_dose': ordem_dose,
                    'metodo': metodo_inseminacao,
                    'tecnico': tecnico,
                    'semana_suina': semana_suina,
                    'data_registro': datetime.now().strftime('%Y-%m-%d'),
                    'observacao': observacoes
                }
                
                # Add to DataFrame
                if insemination_df.empty:
                    insemination_df = pd.DataFrame([novo_registro])
                else:
                    insemination_df = pd.concat([insemination_df, pd.DataFrame([novo_registro])], ignore_index=True)
                
                # Save updated DataFrame
                save_insemination(insemination_df)
                
                # Update breeding cycle if exists
                if not breeding_df.empty and selected_animal_id in breeding_df['id_animal'].values:
                    # Get latest cycle
                    cycles = breeding_df[breeding_df['id_animal'] == selected_animal_id].sort_values('data_cio', ascending=False)
                    if not cycles.empty:
                        latest_cycle = cycles.iloc[0]
                        latest_cycle_id = latest_cycle['id_ciclo']
                        latest_cycle_date = pd.to_datetime(latest_cycle['data_cio']).date()
                        
                        # If insemination date is close to the cycle date (within 5 days)
                        if abs((data_inseminacao - latest_cycle_date).days) <= 5:
                            breeding_df.loc[breeding_df['id_ciclo'] == latest_cycle_id, 'status'] = "Inseminado"
                            breeding_df.loc[breeding_df['id_ciclo'] == latest_cycle_id, 'observacao'] = f"Inseminação registrada em {data_inseminacao.strftime('%d/%m/%Y')}, ID do sêmen: {num_identificacao_semen}"
                            save_breeding_cycles(breeding_df)
                
                st.success(f"Inseminação registrada com sucesso!")
                st.rerun()
    else:
        st.warning("Não há fêmeas (matrizes ou leitoas) cadastradas no sistema. Cadastre matrizes primeiro.")

with tab2:
    st.header("Histórico de Inseminações")
    
    if not insemination_df.empty:
        # Adicionar identificação dos animais
        display_df = pd.merge(
            insemination_df,
            animals_df[['id_animal', 'identificacao', 'nome']],
            on='id_animal',
            how='left'
        )
        
        # Opções de filtro
        col1, col2 = st.columns(2)
        
        with col1:
            filter_animal = st.multiselect(
                "Filtrar por Animal",
                options=animals_df[animals_df['id_animal'].isin(insemination_df['id_animal'])]['identificacao'].unique(),
                default=[]
            )
            
            data_inicio = st.date_input(
                "Data de Início",
                value=(datetime.now() - timedelta(days=90)).date(),
                key="data_inicio"
            )
        
        with col2:
            filter_tecnico = st.multiselect(
                "Filtrar por Técnico",
                options=insemination_df['tecnico'].unique(),
                default=[]
            )
            
            data_fim = st.date_input(
                "Data de Fim",
                value=datetime.now().date(),
                key="data_fim"
            )
        
        # Aplicar filtros
        filtered_df = display_df.copy()
        
        if filter_animal:
            filtered_df = filtered_df[filtered_df['identificacao'].isin(filter_animal)]
            
        if filter_tecnico:
            filtered_df = filtered_df[filtered_df['tecnico'].isin(filter_tecnico)]
        
        # Filtrar por período
        filtered_df['data_inseminacao'] = pd.to_datetime(filtered_df['data_inseminacao'])
        filtered_df = filtered_df[
            (filtered_df['data_inseminacao'].dt.date >= data_inicio) &
            (filtered_df['data_inseminacao'].dt.date <= data_fim)
        ]
        
        # Ordenar por data de inseminação (mais recentes primeiro)
        filtered_df = filtered_df.sort_values('data_inseminacao', ascending=False)
        
        # Mostrar dados
        if not filtered_df.empty:
            st.dataframe(
                filtered_df[[
                    'identificacao', 'brinco', 'categoria', 'tipo_marran', 'data_inseminacao',
                    'num_semen', 'linhagem_semen', 'ordem_dose', 'metodo', 'tecnico', 'semana_suina'
                ]].rename(columns={
                    'identificacao': 'Identificação',
                    'brinco': 'Brinco',
                    'categoria': 'Categoria',
                    'tipo_marran': 'Tipo de Matriz',
                    'data_inseminacao': 'Data da Inseminação',
                    'num_semen': 'Nº do Sêmen',
                    'linhagem_semen': 'Linhagem do Sêmen',
                    'ordem_dose': 'Ordem da Dose',
                    'metodo': 'Método',
                    'tecnico': 'Técnico',
                    'semana_suina': 'Semana Suína'
                }),
                use_container_width=True
            )
            
            # Visualizações
            st.subheader("Análise de Inseminações")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Inseminações por semana do calendário suíno
                semanas_df = filtered_df.groupby('semana_suina').size().reset_index()
                semanas_df.columns = ['Semana Suína', 'Quantidade']
                
                fig = px.bar(
                    semanas_df,
                    x='Semana Suína',
                    y='Quantidade',
                    title='Inseminações por Semana do Calendário Suíno'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Inseminações por tipo de marran
                tipo_df = filtered_df.groupby('tipo_marran').size().reset_index()
                tipo_df.columns = ['Tipo de Matriz', 'Quantidade']
                
                fig = px.pie(
                    tipo_df,
                    values='Quantidade',
                    names='Tipo de Matriz',
                    title='Distribuição por Tipo de Matriz'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Detalhes da inseminação selecionada
            st.subheader("Detalhes da Inseminação")
            
            selected_insemination = st.selectbox(
                "Selecione um registro para ver detalhes:",
                options=filtered_df['id_inseminacao'].tolist(),
                format_func=lambda x: f"{filtered_df[filtered_df['id_inseminacao'] == x]['identificacao'].iloc[0]} - {filtered_df[filtered_df['id_inseminacao'] == x]['data_inseminacao'].dt.strftime('%d/%m/%Y').iloc[0]} ({filtered_df[filtered_df['id_inseminacao'] == x]['num_semen'].iloc[0]})"
            )
            
            if selected_insemination:
                selected_record = filtered_df[filtered_df['id_inseminacao'] == selected_insemination].iloc[0]
                record_id = selected_record['id_inseminacao']
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Animal:** {selected_record['identificacao']} - {selected_record['nome']}")
                    st.write(f"**Brinco:** {selected_record['brinco']}")
                    st.write(f"**Categoria:** {selected_record['categoria']}")
                    st.write(f"**Tipo de Matriz:** {selected_record['tipo_marran']}")
                    st.write(f"**Data da Inseminação:** {selected_record['data_inseminacao'].strftime('%d/%m/%Y')}")
                    st.write(f"**Nº do Sêmen:** {selected_record['num_semen']}")
                    
                    # Verificar se existe registro de linhagem do sêmen (compatibilidade com registros antigos)
                    if 'linhagem_semen' in selected_record:
                        st.write(f"**Linhagem do Sêmen:** {selected_record['linhagem_semen']}")
                
                with col2:
                    st.write(f"**Idade do Sêmen:** {selected_record['idade_semen']} dias")
                    st.write(f"**Dose:** {selected_record['dose']} ml")
                    st.write(f"**Ordem da Dose:** {selected_record['ordem_dose']}")
                    st.write(f"**Método:** {selected_record['metodo']}")
                    st.write(f"**Técnico:** {selected_record['tecnico']}")
                    st.write(f"**Semana Suína:** {selected_record['semana_suina']}")
                    st.write(f"**Observações:** {selected_record.get('observacao', '')}")
                
                # Editar inseminação
                st.subheader("Editar Inseminação")
                
                edit_col1, edit_col2, edit_col3 = st.columns(3)
                
                with edit_col1:
                    opcoes_tipos = ["AM (Avó Materna)", "Avó", "Bisavó", "Matriz Comercial"]
                    # Compatibilidade para registros antigos
                    tipo_atual = selected_record['tipo_marran']
                    if tipo_atual not in opcoes_tipos:
                        if tipo_atual == "AM":
                            tipo_atual = "AM (Avó Materna)"
                        elif tipo_atual == "Outro":
                            tipo_atual = "Matriz Comercial"
                    try:
                        tipo_index = opcoes_tipos.index(tipo_atual)
                    except ValueError:
                        tipo_index = 0
                        
                    new_tipo_marran = st.selectbox(
                        "Tipo de Matriz",
                        options=opcoes_tipos,
                        index=tipo_index,
                        key="edit_tipo",
                        help="AM = Avó Materna, usada para produção de leitoas multiplicadoras"
                    )
                    
                    new_data_inseminacao = st.date_input(
                        "Data da Inseminação",
                        value=selected_record['data_inseminacao'].date(),
                        key="edit_data"
                    )
                    
                    new_num_semen = st.text_input(
                        "Número de Identificação do Sêmen",
                        value=selected_record['num_semen'],
                        key="edit_semen"
                    )
                    
                    # Campo para linhagem do sêmen (compatibilidade com registros antigos)
                    if 'linhagem_semen' in selected_record:
                        linhagem_atual = selected_record['linhagem_semen']
                    else:
                        linhagem_atual = "Outra"
                        
                    new_linhagem_semen = st.selectbox(
                        "Linhagem do Sêmen", 
                        options=["Agroceres", "Danbred", "Topigs", "Penarlan", "Outra"],
                        index=["Agroceres", "Danbred", "Topigs", "Penarlan", "Outra"].index(linhagem_atual) if linhagem_atual in ["Agroceres", "Danbred", "Topigs", "Penarlan", "Outra"] else 4,
                        key="edit_linhagem",
                        help="Linhagem genética do sêmen utilizado"
                    )
                
                with edit_col2:
                    new_idade_semen = st.number_input(
                        "Idade do Sêmen",
                        min_value=0,
                        value=int(selected_record['idade_semen']),
                        key="edit_idade"
                    )
                    
                    new_dose = st.number_input(
                        "Dose Utilizada (ml)",
                        min_value=0.0,
                        value=float(selected_record['dose']),
                        step=10.0,
                        key="edit_dose"
                    )
                    
                    new_ordem_dose = st.selectbox(
                        "Ordem da Dose",
                        options=["Primeira", "Segunda", "Terceira", "Quarta", "Quinta+"],
                        index=["Primeira", "Segunda", "Terceira", "Quarta", "Quinta+"].index(selected_record['ordem_dose']),
                        key="edit_ordem"
                    )
                
                with edit_col3:
                    new_metodo = st.selectbox(
                        "Método de Inseminação",
                        options=["Tradicional", "Pós-Cervical", "Intra-Uterina Profunda"],
                        index=["Tradicional", "Pós-Cervical", "Intra-Uterina Profunda"].index(selected_record['metodo']),
                        key="edit_metodo"
                    )
                    
                    new_tecnico = st.text_input(
                        "Técnico Responsável",
                        value=selected_record['tecnico'],
                        key="edit_tecnico"
                    )
                    
                    new_semana_suina = st.number_input(
                        "Semana do Calendário Suíno",
                        min_value=1,
                        max_value=52,
                        value=int(selected_record['semana_suina']),
                        key="edit_semana"
                    )
                    
                    new_observacao = st.text_area(
                        "Observações",
                        value=selected_record.get('observacao', ''),
                        key="edit_obs"
                    )
                
                if st.button("Atualizar Inseminação"):
                    # Update insemination record
                    insemination_df.loc[insemination_df['id_inseminacao'] == record_id, 'tipo_marran'] = new_tipo_marran
                    insemination_df.loc[insemination_df['id_inseminacao'] == record_id, 'data_inseminacao'] = new_data_inseminacao.strftime('%Y-%m-%d')
                    insemination_df.loc[insemination_df['id_inseminacao'] == record_id, 'num_semen'] = new_num_semen
                    
                    # Atualizar linhagem do sêmen se o campo existir
                    if 'linhagem_semen' in insemination_df.columns:
                        insemination_df.loc[insemination_df['id_inseminacao'] == record_id, 'linhagem_semen'] = new_linhagem_semen
                    
                    insemination_df.loc[insemination_df['id_inseminacao'] == record_id, 'idade_semen'] = new_idade_semen
                    insemination_df.loc[insemination_df['id_inseminacao'] == record_id, 'dose'] = new_dose
                    insemination_df.loc[insemination_df['id_inseminacao'] == record_id, 'ordem_dose'] = new_ordem_dose
                    insemination_df.loc[insemination_df['id_inseminacao'] == record_id, 'metodo'] = new_metodo
                    insemination_df.loc[insemination_df['id_inseminacao'] == record_id, 'tecnico'] = new_tecnico
                    insemination_df.loc[insemination_df['id_inseminacao'] == record_id, 'semana_suina'] = new_semana_suina
                    insemination_df.loc[insemination_df['id_inseminacao'] == record_id, 'observacao'] = new_observacao
                    
                    # Save updated DataFrame
                    save_insemination(insemination_df)
                    
                    st.success(f"Inseminação atualizada com sucesso!")
                    st.rerun()
                
                # Delete insemination
                if st.button("Excluir Inseminação", type="primary", use_container_width=True):
                    # Remove from DataFrame
                    insemination_df = insemination_df[insemination_df['id_inseminacao'] != record_id]
                    
                    # Save updated DataFrame
                    save_insemination(insemination_df)
                    
                    st.success(f"Inseminação excluída com sucesso!")
                    st.rerun()
        else:
            st.info("Nenhuma inseminação encontrada com os filtros aplicados.")
    else:
        st.info("Nenhum registro de inseminação encontrado. Adicione novos registros na aba 'Registrar Inseminação'.")