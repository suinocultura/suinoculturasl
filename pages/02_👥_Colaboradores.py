import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import os
import sys

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import (
    load_employees,
    save_employees,
    register_employee,
    update_employee_status,
    check_permission
)

st.set_page_config(
    page_title="Colaboradores",
    page_icon="👥",
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
if not check_permission(st.session_state.current_user, 'manage_users'):
    st.error("Você não tem permissão para acessar esta página.")
    st.stop()


# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# Verificar se o usuário está autenticado
if not st.session_state.authenticated:
    st.error("Você precisa estar autenticado para acessar esta página.")
    st.stop()

# Verificar se o usuário tem permissão para gerenciar usuários
if not check_permission(st.session_state.current_user, 'manage_users'):
    st.error("Você não tem permissão para acessar esta página. Apenas Administradores e Desenvolvedores têm acesso.")
    st.stop()

st.title("Gestão de Colaboradores 👥")
st.write("Registre e gerencie os colaboradores do sistema.")

# Tab for registration and management
tab1, tab2 = st.tabs(["Registrar Colaborador", "Gerenciar Colaboradores"])

with tab1:
    st.header("Registrar Novo Colaborador")
    
    with st.form("employee_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input(
                "Nome Completo",
                help="Nome completo do colaborador"
            )
            
            matricula = st.text_input(
                "Matrícula",
                help="Número de matrícula único do colaborador"
            )
        
        with col2:
            cargo = st.selectbox(
                "Cargo",
                options=[
                    "Administrador",
                    "Desenvolvedor",
                    "Veterinário",
                    "Técnico",
                    "Operador",
                    "Auxiliar"
                ]
            )
            
            setor = st.selectbox(
                "Setor",
                options=[
                    "Gestação",
                    "Maternidade",
                    "Creche",
                    "Terminação",
                    "Administrativo",
                    "Desenvolvimento"
                ]
            )
        
        observacao = st.text_area(
            "Observações",
            help="Informações adicionais sobre o colaborador"
        )
        
        submitted = st.form_submit_button("Registrar Colaborador")
        
        if submitted:
            if not nome or not matricula:
                st.error("Por favor, preencha nome e matrícula.")
            else:
                success, message = register_employee(
                    nome=nome,
                    matricula=matricula,
                    cargo=cargo,
                    setor=setor,
                    observacao=observacao
                )
                
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

with tab2:
    st.header("Gerenciar Colaboradores")
    
    # Load employee data
    employees_df = load_employees()
    
    if not employees_df.empty:
        # Filter options
        col1, col2 = st.columns(2)
        
        with col1:
            filter_status = st.multiselect(
                "Filtrar por Status",
                options=employees_df['status'].unique(),
                default=["Ativo"]
            )
        
        with col2:
            filter_sector = st.multiselect(
                "Filtrar por Setor",
                options=employees_df['setor'].unique()
            )
        
        # Apply filters
        filtered_df = employees_df.copy()
        if filter_status:
            filtered_df = filtered_df[filtered_df['status'].isin(filter_status)]
        if filter_sector:
            filtered_df = filtered_df[filtered_df['setor'].isin(filter_sector)]
        
        if not filtered_df.empty:
            # Display employee table
            st.dataframe(
                filtered_df[[
                    'nome', 'matricula', 'cargo', 'setor',
                    'data_admissao', 'status', 'ultimo_acesso'
                ]].rename(columns={
                    'nome': 'Nome',
                    'matricula': 'Matrícula',
                    'cargo': 'Cargo',
                    'setor': 'Setor',
                    'data_admissao': 'Data de Admissão',
                    'status': 'Status',
                    'ultimo_acesso': 'Último Acesso'
                }),
                hide_index=True,
                use_container_width=True
            )
            
            # Employee management
            st.subheader("Atualizar Status")
            
            col1, col2 = st.columns(2)
            
            with col1:
                selected_employee = st.selectbox(
                    "Selecione o Colaborador",
                    options=filtered_df['matricula'].tolist(),
                    format_func=lambda x: f"{filtered_df[filtered_df['matricula'] == x]['nome'].iloc[0]} ({x})"
                )
            
            with col2:
                new_status = st.selectbox(
                    "Novo Status",
                    options=["Ativo", "Inativo", "Férias", "Afastado"]
                )
            
            if st.button("Atualizar Status"):
                success, message = update_employee_status(selected_employee, new_status)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            
            # Export functionality
            st.markdown("---")
            if st.button("📥 Exportar Dados"):
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    "📥 Baixar CSV",
                    data=csv,
                    file_name="colaboradores.csv",
                    mime="text/csv"
                )
        else:
            st.info("Nenhum colaborador encontrado com os filtros selecionados.")
    else:
        st.info("Nenhum colaborador cadastrado. Utilize o formulário de registro para adicionar.")
