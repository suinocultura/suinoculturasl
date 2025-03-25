import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import (
    load_employees,
    save_employees,
    register_employee,
    update_employee_status,
    load_animals,
    load_breeding_cycles,
    load_gestation,
    load_weight_records,
    load_heat_records,
    load_vaccination_records,
    load_mortality_records,
    check_permission,
    EMPLOYEES_FILE,
    ANIMALS_FILE,
    BREEDING_FILE,
    GESTATION_FILE,
    WEIGHT_FILE,
    HEAT_DETECTION_FILE,
    HEAT_RECORDS_FILE,
    VACCINATION_RECORDS_FILE,
    MORTALITY_FILE
)

st.set_page_config(
    page_title="Administração",
    page_icon="⚙️",
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
if not check_permission(st.session_state.current_user, 'admin'):
    st.error("Você não tem permissão para acessar esta página.")
    st.stop()


# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# Verificar se o usuário está autenticado e tem permissão de administração
if not st.session_state.authenticated:
    st.warning("Você precisa fazer login para acessar esta página.")
    st.stop()
elif not check_permission(st.session_state.current_user, 'admin'):
    st.error("Você não tem permissão para acessar esta página. Apenas administradores, gerentes e desenvolvedores têm acesso.")
    st.stop()

st.title("Painel Administrativo ⚙️")

# Tabs para diferentes seções
tab1, tab2, tab3, tab4 = st.tabs([
    "Visão Geral",
    "Gestão de Colaboradores",
    "Monitoramento",
    "Configurações"
])

with tab1:
    st.header("Visão Geral do Sistema")
    
    # Carregar dados necessários
    employees_df = load_employees()
    animals_df = load_animals()
    breeding_df = load_breeding_cycles()
    gestation_df = load_gestation()
    weight_df = load_weight_records()
    heat_df = load_heat_records()
    vaccination_df = load_vaccination_records()
    mortality_df = load_mortality_records()

    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_employees = len(employees_df) if not employees_df.empty else 0
        active_employees = len(employees_df[employees_df['status'] == 'Ativo']) if not employees_df.empty else 0
        st.metric("Colaboradores Ativos", f"{active_employees}/{total_employees}")

    with col2:
        total_animals = len(animals_df) if not animals_df.empty else 0
        st.metric("Total de Animais", total_animals)

    with col3:
        vaccinations_today = len(vaccination_df[
            pd.to_datetime(vaccination_df['data_aplicacao']).dt.date == datetime.now().date()
        ]) if not vaccination_df.empty else 0
        st.metric("Vacinações Hoje", vaccinations_today)

    with col4:
        mortality_rate = (len(mortality_df) / total_animals * 100) if total_animals > 0 and not mortality_df.empty else 0
        st.metric("Taxa de Mortalidade", f"{mortality_rate:.2f}%")

    # Gráficos e análises
    st.subheader("Análises")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Atividade por setor
        if not employees_df.empty:
            setor_counts = employees_df[employees_df['status'] == 'Ativo']['setor'].value_counts()
            fig = px.pie(
                values=setor_counts.values,
                names=setor_counts.index,
                title="Distribuição de Colaboradores por Setor"
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Evolução do plantel
        if not animals_df.empty:
            animals_df['data_cadastro'] = pd.to_datetime(animals_df['data_cadastro'])
            animals_by_date = animals_df.groupby('data_cadastro').size().cumsum()
            fig = px.line(
                x=animals_by_date.index,
                y=animals_by_date.values,
                title="Evolução do Plantel",
                labels={'x': 'Data', 'y': 'Total de Animais'}
            )
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("Gestão de Colaboradores")
    
    # Formulário para adicionar novo colaborador
    with st.expander("➕ Adicionar Novo Colaborador"):
        with st.form("employee_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("Nome Completo")
                matricula = st.text_input("Matrícula")
                cargo = st.selectbox(
                    "Cargo",
                    ["Administrador", "Gerente", "Técnico", "Operador", "Veterinário", "Visitante", "Desenvolvedor"]
                )
            
            with col2:
                setor = st.selectbox(
                    "Setor",
                    ["Gestação", "Maternidade", "Creche", "Terminação", "Administrativo", "Desenvolvimento"]
                )
                observacao = st.text_area("Observações")
            
            submitted = st.form_submit_button("Registrar")
            
            if submitted:
                if not nome or not matricula:
                    st.error("Nome e matrícula são obrigatórios.")
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
    
    # Lista de colaboradores
    if not employees_df.empty:
        st.subheader("Colaboradores Cadastrados")
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            filter_status = st.multiselect(
                "Status",
                options=employees_df['status'].unique(),
                default=["Ativo"]
            )
        with col2:
            filter_sector = st.multiselect(
                "Setor",
                options=employees_df['setor'].unique()
            )
        
        # Aplicar filtros
        filtered_df = employees_df.copy()
        if filter_status:
            filtered_df = filtered_df[filtered_df['status'].isin(filter_status)]
        if filter_sector:
            filtered_df = filtered_df[filtered_df['setor'].isin(filter_sector)]
        
        # Exibir tabela
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
        
        # Atualização de status
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
        
        if st.button("Atualizar"):
            success, message = update_employee_status(selected_employee, new_status)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

with tab3:
    st.header("Monitoramento do Sistema")
    
    # Seleção de período
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Data Inicial",
            value=datetime.now().date() - timedelta(days=30)
        )
    with col2:
        end_date = st.date_input(
            "Data Final",
            value=datetime.now().date()
        )
    
    # Atividades do sistema
    st.subheader("Atividades do Sistema")
    
    # Acessos por colaborador
    if not employees_df.empty:
        # Filtrar entradas que têm último acesso (não nulo)
        valid_accesses = employees_df[employees_df['ultimo_acesso'].notna()].copy()
        
        if not valid_accesses.empty:
            valid_accesses['ultimo_acesso'] = pd.to_datetime(valid_accesses['ultimo_acesso'])
            recent_accesses = valid_accesses[
                (valid_accesses['ultimo_acesso'].dt.date >= start_date) &
                (valid_accesses['ultimo_acesso'].dt.date <= end_date)
            ]
            
            if not recent_accesses.empty:
                st.write("Últimos Acessos:")
                st.dataframe(
                    recent_accesses[['nome', 'cargo', 'ultimo_acesso']].rename(columns={
                        'nome': 'Nome',
                        'cargo': 'Cargo',
                        'ultimo_acesso': 'Último Acesso'
                    }).sort_values('Último Acesso', ascending=False),
                    hide_index=True
                )
    
    # Estatísticas de uso
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Registros de vacinação
        if not vaccination_df.empty:
            vaccination_df['data_aplicacao'] = pd.to_datetime(vaccination_df['data_aplicacao'])
            vacc_count = len(vaccination_df[
                (vaccination_df['data_aplicacao'].dt.date >= start_date) &
                (vaccination_df['data_aplicacao'].dt.date <= end_date)
            ])
            st.metric("Vacinações no Período", vacc_count)
    
    with col2:
        # Registros de peso
        if not weight_df.empty:
            weight_df['data_registro'] = pd.to_datetime(weight_df['data_registro'])
            weight_count = len(weight_df[
                (weight_df['data_registro'].dt.date >= start_date) &
                (weight_df['data_registro'].dt.date <= end_date)
            ])
            st.metric("Pesagens no Período", weight_count)
    
    with col3:
        # Registros de cio
        if not heat_df.empty:
            heat_df['data_deteccao'] = pd.to_datetime(heat_df['data_deteccao'])
            heat_count = len(heat_df[
                (heat_df['data_deteccao'].dt.date >= start_date) &
                (heat_df['data_deteccao'].dt.date <= end_date)
            ])
            st.metric("Detecções de Cio no Período", heat_count)

with tab4:
    st.header("Configurações do Sistema")
    
    # Configurações gerais
    st.subheader("Configurações Gerais")
    
    # Backup de dados
    st.write("### 💾 Backup de Dados")
    if st.button("Gerar Backup"):
        # Lista de todos os arquivos CSV
        backup_files = [
            EMPLOYEES_FILE,
            ANIMALS_FILE,
            BREEDING_FILE,
            GESTATION_FILE,
            WEIGHT_FILE,
            HEAT_DETECTION_FILE,
            HEAT_RECORDS_FILE,
            VACCINATION_RECORDS_FILE,
            MORTALITY_FILE
        ]
        
        # Criar DataFrames para cada arquivo
        backup_data = {}
        for file in backup_files:
            if os.path.exists(file):
                df = pd.read_csv(file)
                backup_data[os.path.basename(file)] = df
        
        # Gerar arquivo ZIP com todos os CSVs
        import zipfile
        from io import BytesIO
        
        buffer = BytesIO()
        with zipfile.ZipFile(buffer, 'w') as zip_file:
            for filename, df in backup_data.items():
                csv_buffer = BytesIO()
                df.to_csv(csv_buffer, index=False)
                zip_file.writestr(filename, csv_buffer.getvalue())
        
        # Oferecer download
        st.download_button(
            "📥 Baixar Backup",
            data=buffer.getvalue(),
            file_name=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            mime="application/zip"
        )
    
    # Gerenciamento de dados
    st.write("### 🗄️ Gerenciamento de Dados")
    
    data_options = {
        "Colaboradores": "employees",
        "Animais": "animals",
        "Ciclos Reprodutivos": "breeding",
        "Gestações": "gestation",
        "Registros de Peso": "weight",
        "Detecção de Cio": "heat",
        "Vacinações": "vaccination",
        "Mortalidade": "mortality"
    }
    
    export_data = st.selectbox(
        "Selecione os dados para exportar",
        options=list(data_options.keys())
    )
    
    if st.button("Exportar CSV"):
        data_key = data_options[export_data]
        if data_key == "employees":
            df = load_employees()
        elif data_key == "animals":
            df = load_animals()
        elif data_key == "breeding":
            df = load_breeding_cycles()
        elif data_key == "gestation":
            df = load_gestation()
        elif data_key == "weight":
            df = load_weight_records()
        elif data_key == "heat":
            df = load_heat_records()
        elif data_key == "vaccination":
            df = load_vaccination_records()
        elif data_key == "mortality":
            df = load_mortality_records()
        
        if not df.empty:
            csv = df.to_csv(index=False)
            st.download_button(
                "📥 Baixar CSV",
                data=csv,
                file_name=f"{data_key}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("Não há dados para exportar.")
    
    # Informações do sistema
    st.write("### ℹ️ Informações do Sistema")
    st.write("**Versão:** 1.0.0")
    st.write("**Última Atualização:** 20/03/2025")
