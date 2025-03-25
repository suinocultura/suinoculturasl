import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Configurar o título da página principal como "Entrar"
st.set_page_config(
    page_title="Entrar",
    page_icon="🔑",
    layout="wide",
    initial_sidebar_state="expanded"
)

from utils import (
    load_animals, 
    load_breeding_cycles, 
    load_gestation, 
    load_weight_records,
    load_insemination,
    load_pens,
    load_pen_allocations,
    load_maternity,
    load_litters,
    load_piglets,
    load_weaning,
    load_nursery,
    load_nursery_batches,
    load_nursery_movements,
    load_gilts,
    load_gilts_selection,
    load_gilts_discard,
    calculate_statistics,
    authenticate_employee,
    register_employee,
    load_employees,
    check_developer_access,
    check_permission
)

# Função para criar um usuário administrador padrão se necessário
def setup_default_admin():
    employees_df = load_employees()
    
    # Se não houver funcionários cadastrados, cria um administrador padrão
    if employees_df.empty:
        success, message = register_employee(
            nome="Administrador", 
            matricula="admin",
            cargo="Administrador",
            setor="Administrativo",
            observacao="Usuário administrador padrão"
        )
        if success:
            st.sidebar.info("Um usuário administrador padrão foi criado. Use a matrícula 'admin' para fazer login.")

# Add before any other content
def check_authentication():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None

    if not st.session_state.authenticated:
        st.write("## Entrar")
        matricula = st.text_input("Matrícula", key="login_matricula")

        if st.button("Entrar"):
            if matricula:
                user = authenticate_employee(matricula)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.current_user = user
                    st.rerun()
                else:
                    st.error("Matrícula inválida ou usuário inativo.")
            else:
                st.error("Por favor, informe a matrícula.")
        return False
    return True

# A configuração de página já foi definida no início do script

# Estilização do menu lateral
st.markdown("""
<style>
    /* Estilo para o título do menu lateral */
    .css-1d391kg [data-testid="stSidebarNav"] {
        background-color: #F0F2F6;
        padding-top: 20px;
        padding-bottom: 20px;
    }
    
    /* Não precisamos mais deste código aqui, ele foi movido para baixo */
    
    /* Estilo para as seções do menu */
    [data-testid="stSidebarNav"] li div p {
        font-size: 14px;
    }
    
    /* Estilo para o item header do menu (seções com 🔹) */
    [data-testid="stSidebarNav"] li:has(div p:contains("🔹")) div {
        border-bottom: 1px solid #e0e0e0;
        margin-top: 20px !important;
        padding-bottom: 5px;
        width: 100%;
    }
    
    /* Estilo para o texto dos headers - cores específicas para cada seção */
    /* ADMINISTRAÇÃO - Azul */
    [data-testid="stSidebarNav"] li:has(div p:contains("🔹 ADMINIS")) div p {
        color: #1B98E0 !important; /* Azul */
        font-size: 16px !important;
        font-weight: 600 !important;
        margin: 0;
    }
    
    /* REPRODUÇÃO - Rosa */
    [data-testid="stSidebarNav"] li:has(div p:contains("🔹 REPRODU")) div p {
        color: #FF6B6B !important; /* Rosa */
        font-size: 16px !important;
        font-weight: 600 !important;
        margin: 0;
    }
    
    /* CRESCIMENTO - Verde */
    [data-testid="stSidebarNav"] li:has(div p:contains("🔹 CRESCI")) div p {
        color: #38B000 !important; /* Verde */
        font-size: 16px !important;
        font-weight: 600 !important;
        margin: 0;
    }
    
    /* SAÚDE - Amarelo */
    [data-testid="stSidebarNav"] li:has(div p:contains("🔹 SAUDE")) div p {
        color: #F7B801 !important; /* Amarelo */
        font-size: 16px !important;
        font-weight: 600 !important;
        margin: 0;
    }
    
    /* GESTÃO E RELATÓRIOS - Roxo */
    [data-testid="stSidebarNav"] li:has(div p:contains("🔹 GEST")) div p {
        color: #8C52FF !important; /* Roxo */
        font-size: 16px !important;
        font-weight: 600 !important;
        margin: 0;
    }
    
    /* Ajuste de espaçamento e estilo nos itens normais */
    [data-testid="stSidebarNav"] li:not(:has(div p:contains("🔹"))) {
        margin-left: 10px;
    }
    
    /* Estilo vermelho e negrito apenas para as categorias do menu (itens que começam com emoji) */
    [data-testid="stSidebarNav"] li:not(:has(div p:contains("🔹"))) div p:has-text("🐷"), 
    [data-testid="stSidebarNav"] li:not(:has(div p:contains("🔹"))) div p:has-text("👥"),
    [data-testid="stSidebarNav"] li:not(:has(div p:contains("🔹"))) div p:has-text("🔄"),
    [data-testid="stSidebarNav"] li:not(:has(div p:contains("🔹"))) div p:has-text("🤰"),
    [data-testid="stSidebarNav"] li:not(:has(div p:contains("🔹"))) div p:has-text("💉"),
    [data-testid="stSidebarNav"] li:not(:has(div p:contains("🔹"))) div p:has-text("🔍"),
    [data-testid="stSidebarNav"] li:not(:has(div p:contains("🔹"))) div p:has-text("🐗"),
    [data-testid="stSidebarNav"] li:not(:has(div p:contains("🔹"))) div p:has-text("⚖️"),
    [data-testid="stSidebarNav"] li:not(:has(div p:contains("🔹"))) div p:has-text("🏠"),
    [data-testid="stSidebarNav"] li:not(:has(div p:contains("🔹"))) div p:has-text("👪"),
    [data-testid="stSidebarNav"] li:not(:has(div p:contains("🔹"))) div p:has-text("🐽"),
    [data-testid="stSidebarNav"] li:not(:has(div p:contains("🔹"))) div p:has-text("🏫"),
    [data-testid="stSidebarNav"] li:not(:has(div p:contains("🔹"))) div p:has-text("✅"),
    [data-testid="stSidebarNav"] li:not(:has(div p:contains("🔹"))) div p:has-text("🔧"),
    [data-testid="stSidebarNav"] li:not(:has(div p:contains("🔹"))) div p:has-text("📊"),
    [data-testid="stSidebarNav"] li:not(:has(div p:contains("🔹"))) div p:has-text("🏭"),
    [data-testid="stSidebarNav"] li:not(:has(div p:contains("🔹"))) div p:has-text("🏥"),
    [data-testid="stSidebarNav"] li:not(:has(div p:contains("🔹"))) div p:has-text("🚀"),
    [data-testid="stSidebarNav"] li:not(:has(div p:contains("🔹"))) div p:has-text("📝"),
    [data-testid="stSidebarNav"] li:not(:has(div p:contains("🔹"))) div p:has-text("📋"),
    [data-testid="stSidebarNav"] li:not(:has(div p:contains("🔹"))) div p:has-text("⚙️") {
        color: #FF0000 !important;
        font-weight: 700 !important;
    }
    
    /* Para mudar o nome "Recria" */
    [data-testid="stSidebarNav"] li:has(div p:contains("⚙️")) div p {
        position: relative;
        visibility: hidden;
    }
    
    [data-testid="stSidebarNav"] li:has(div p:contains("⚙️")) div p:after {
        content: "⚙️ Recria";
        visibility: visible;
        position: absolute;
        left: 0;
        top: 0;
        color: #FF0000 !important;
        font-weight: 700 !important;
    }
    
    /* Área do Desenvolvedor - estilo especial para o menu de desenvolvedor */
    [data-testid="stSidebarNav"] li:has(div p:contains("🛠️")) div p {
        color: #00C853 !important;
        font-weight: 700 !important;
        background-color: rgba(0, 200, 83, 0.1);
        padding: 5px;
        border-radius: 5px;
    }
    
    /* Esconde o item de Download de Aplicativo para não-desenvolvedores */
    /* Será mostrado apenas via JavaScript condicionalmente */
    [data-testid="stSidebarNav"] li:has(div p:contains("📥")) {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# Configuração inicial: cria usuário administrador padrão se necessário
setup_default_admin()

# Add as first line after setting page config
if not check_authentication():
    st.stop()

# Initialize session states
if 'language' not in st.session_state:
    st.session_state.language = 'pt'  # Default to Portuguese
    
# Customizar a barra lateral
with st.sidebar:
    # Aplica CSS para a barra lateral em modo escuro
    st.markdown("""
    <style>
    /* Estilo base da barra lateral em modo escuro */
    [data-testid="stSidebar"] {
        background-color: #1E1E1E;
        color: #E0E0E0;
    }
    
    /* Estilo para cabeçalhos */
    [data-testid="stSidebar"] .st-emotion-cache-16txtl3 h1,
    [data-testid="stSidebar"] .st-emotion-cache-16txtl3 h2,
    [data-testid="stSidebar"] .st-emotion-cache-16txtl3 h3,
    [data-testid="stSidebar"] .st-emotion-cache-16txtl3 h4,
    [data-testid="stSidebar"] .st-emotion-cache-16txtl3 h5,
    [data-testid="stSidebar"] .st-emotion-cache-16txtl3 h6 {
        color: #E0E0E0;
    }
    
    /* Estilo para texto normal */
    [data-testid="stSidebar"] .st-emotion-cache-16txtl3 p,
    [data-testid="stSidebar"] .st-emotion-cache-16txtl3 ol,
    [data-testid="stSidebar"] .st-emotion-cache-16txtl3 ul,
    [data-testid="stSidebar"] .st-emotion-cache-16txtl3 li {
        color: #CCCCCC;
    }
    
    /* Mudar o nome do item "app" para "Entrar" */
    [data-testid="stSidebar"] a[href="/"] {
        visibility: hidden;
        position: relative;
    }
    
    [data-testid="stSidebar"] a[href="/"]:after {
        content: "🔑 Entrar";
        visibility: visible;
        position: absolute;
        left: 0;
        top: 0;
        color: #B8B8B8 !important;
        font-weight: bold !important;
    }
    
    /* Destaque para categorias principais (arquivos que começam com 🔹) */
    [data-testid="stSidebar"] a[href*="🔹"] {
        color: #FF6B6B !important;
        font-weight: bold !important;
        font-size: 1.1em !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        margin-top: 10px !important;
        display: block !important;
    }
    
    /* Estilo para links na barra lateral */
    [data-testid="stSidebar"] a {
        color: #B8B8B8 !important;
        text-decoration: none !important;
        transition: all 0.2s ease !important;
    }
    
    /* Efeito hover nos links */
    [data-testid="stSidebar"] a:hover {
        color: #FFFFFF !important;
        background-color: rgba(255, 255, 255, 0.1) !important;
        padding-left: 5px !important;
    }
    
    /* Linha divisória entre seções */
    .sidebar-divider {
        border-top: 1px solid #3D3D3D;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Logo em modo escuro - Atualizado com ano 2025
    st.markdown("""
    <div style="text-align:center; background-color: #2D2D2D; padding: 15px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.3); border: 2px solid #FF6B6B;">
        <h1 style="color:#FF6B6B; margin-bottom:0; font-size: 42px;">🐷</h1>
        <h3 style="margin-top:5px; color: #E0E0E0; font-weight: bold;">Suinocultura</h3>
        <div style="background-color: #FF6B6B; height: 3px; width: 80%; margin: 8px auto;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.current_user:
        # Estilo melhorado para informações do usuário no topo da sidebar
        st.markdown(f"""
        <div style="background-color: #2D2D2D; padding: 12px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.3); border-left: 4px solid #38B000;">
            <div style="display: flex; align-items: center;">
                <div style="background-color: #38B000; width: 40px; height: 40px; border-radius: 50%; display: flex; justify-content: center; align-items: center; margin-right: 12px;">
                    <div style="font-size: 22px;">👤</div>
                </div>
                <div>
                    <div style="font-weight: bold; font-size: 16px; color: #FFFFFF;">{st.session_state.current_user['nome']}</div>
                    <div style="color: #B0B0B0; font-size: 14px; margin-top: 2px;">{st.session_state.current_user['cargo']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Adiciona CSS personalizado para o botão de sair no modo escuro
        st.markdown("""
        <style>
        div[data-testid="stButton"] button {
            background-color: #FF6B6B;
            color: white;
            border: none;
            padding: 10px 16px;
            border-radius: 50px;
            width: 100%;
            font-weight: 600;
            margin-top: 5px;
            transition: all 0.3s;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-size: 14px;
        }
        div[data-testid="stButton"] button:hover {
            background-color: #FF4040;
            color: white;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            transform: translateY(-1px);
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Botão de sair com estilo melhorado
        st.button("🚪 Encerrar Sessão", key="btn_sair", on_click=lambda: [
            setattr(st.session_state, 'authenticated', False),
            setattr(st.session_state, 'current_user', None),
            st.rerun()
        ])
        st.markdown("---")
        
        # Adiciona JavaScript para controlar a visibilidade dos itens do menu com base nas permissões
        if 'current_user' in st.session_state and st.session_state.current_user:
            has_dev_tools_perm = check_permission(st.session_state.current_user, 'developer_tools')
            has_admin_perm = check_permission(st.session_state.current_user, 'admin')
            
            # Injetar JS para mostrar/esconder itens do menu com base nas permissões
            dev_display = '"block"' if has_dev_tools_perm else '"none"'
            admin_display = '"block"' if has_admin_perm else '"none"'
            manage_users_display = '"block"' if check_permission(st.session_state.current_user, 'manage_users') else '"none"'
            manage_animals_display = '"block"' if check_permission(st.session_state.current_user, 'manage_animals') else '"none"'
            manage_reproduction_display = '"block"' if check_permission(st.session_state.current_user, 'manage_reproduction') else '"none"'
            manage_health_display = '"block"' if check_permission(st.session_state.current_user, 'manage_health') else '"none"'
            manage_growth_display = '"block"' if check_permission(st.session_state.current_user, 'manage_growth') else '"none"'
            view_reports_display = '"block"' if check_permission(st.session_state.current_user, 'view_reports') else '"none"'
            
            js_code = f"""
            <script>
                // Função para mostrar ou esconder os itens do menu com base nas permissões
                function configurarMenuPermissoes() {{
                    // Aguarda a barra lateral carregar completamente
                    const interval = setInterval(() => {{
                        // Verificar se os elementos que precisamos existem
                        const sidebar = document.querySelector('[data-testid="stSidebarNav"]');
                        
                        if (sidebar) {{
                            try {{
                                // Selecionar itens do menu com base nos emojis/títulos
                                // Ferramentas de desenvolvedor e download de aplicativo
                                const downloadLink = sidebar.querySelector('li:has(div p:contains("📥"))');
                                const devToolsLink = sidebar.querySelector('li:has(div p:contains("🛠️"))');
                                
                                // Administração e Colaboradores
                                const adminLink = sidebar.querySelector('li:has(div p:contains("🔧"))');
                                const employeesLink = sidebar.querySelector('li:has(div p:contains("👥"))');
                                
                                // Gerenciamento de animais
                                const animalsLink = sidebar.querySelector('li:has(div p:contains("🐷"))');
                                
                                // Reprodução
                                const reproductionLinks = sidebar.querySelectorAll('li:has(div p:contains("🔄")), li:has(div p:contains("🤰")), li:has(div p:contains("💉")), li:has(div p:contains("🔍")), li:has(div p:contains("🐗"))');
                                
                                // Crescimento
                                const growthLinks = sidebar.querySelectorAll('li:has(div p:contains("⚖️")), li:has(div p:contains("🏠")), li:has(div p:contains("👪")), li:has(div p:contains("🐽")), li:has(div p:contains("🏫")), li:has(div p:contains("✅"))');
                                
                                // Saúde
                                const healthLinks = sidebar.querySelectorAll('li:has(div p:contains("💉 Vacinas")), li:has(div p:contains("☠️"))');
                                
                                // Relatórios e Gestão
                                const reportLinks = sidebar.querySelectorAll('li:has(div p:contains("📊")), li:has(div p:contains("🏭")), li:has(div p:contains("🏥")), li:has(div p:contains("🚀")), li:has(div p:contains("📝")), li:has(div p:contains("📋"))');
                                
                                // Recria
                                const recriaLink = sidebar.querySelector('li:has(div p:contains("⚙️"))');
                                
                                // Configurar visibilidade com base nas permissões do usuário
                                if (downloadLink) downloadLink.style.display = {dev_display};
                                if (devToolsLink) devToolsLink.style.display = {dev_display};
                                
                                if (adminLink) adminLink.style.display = {admin_display};
                                if (employeesLink) employeesLink.style.display = {manage_users_display};
                                
                                if (animalsLink) animalsLink.style.display = {manage_animals_display};
                                
                                reproductionLinks.forEach(link => {{
                                    if (link) link.style.display = {manage_reproduction_display};
                                }});
                                
                                growthLinks.forEach(link => {{
                                    if (link) link.style.display = {manage_growth_display};
                                }});
                                
                                healthLinks.forEach(link => {{
                                    if (link) link.style.display = {manage_health_display};
                                }});
                                
                                reportLinks.forEach(link => {{
                                    if (link) link.style.display = {view_reports_display};
                                }});
                                
                                if (recriaLink) recriaLink.style.display = {manage_growth_display};
                                
                                // Configuração concluída, parar o intervalo
                                clearInterval(interval);
                            }} catch (error) {{
                                // Continuar tentando
                                console.log('Aguardando carregar menu: ' + error);
                            }}
                        }}
                    }}, 200);
                }}
                
                // Executar a função quando o documento estiver pronto
                document.addEventListener("DOMContentLoaded", configurarMenuPermissoes);
                // Também executar quando a visibilidade da página mudar
                document.addEventListener("visibilitychange", configurarMenuPermissoes);
                // E executar agora para o caso de o DOM já estar carregado
                configurarMenuPermissoes();
                // Executar novamente após 1 segundo para garantir
                setTimeout(configurarMenuPermissoes, 1000);
            </script>
            """
            st.markdown(js_code, unsafe_allow_html=True)

# Title and description
st.title("Sistema de Gestão Suinocultura 🐷")

# Add in the title section, after the main title
if st.session_state.current_user:
    st.write(f"👤 Usuário: {st.session_state.current_user['nome']} ({st.session_state.current_user['cargo']})")

st.markdown("""
Este sistema ajuda a gerenciar sua granja de suínos, monitorando:
- Ciclos reprodutivos
- Períodos de gestação
- Idade dos animais
- Peso e crescimento
""")

# Create data directory if it doesn't exist
if not os.path.exists("data"):
    os.makedirs("data")

# Load data
animals_df = load_animals()
breeding_df = load_breeding_cycles()
gestation_df = load_gestation()
weight_df = load_weight_records()
insemination_df = load_insemination()
pens_df = load_pens()
pen_allocations_df = load_pen_allocations()
maternity_df = load_maternity()
litters_df = load_litters()
piglets_df = load_piglets()
weaning_df = load_weaning()
nursery_df = load_nursery()
nursery_batches_df = load_nursery_batches()
nursery_movements_df = load_nursery_movements()
gilts_df = load_gilts()
gilts_selection_df = load_gilts_selection()
gilts_discard_df = load_gilts_discard()

# Dashboard metrics
col1, col2, col3, col4, col5 = st.columns(5)

# Calculate key metrics
total_animals = len(animals_df) if not animals_df.empty else 0
pregnant_animals = len(gestation_df[gestation_df['data_parto'].isna()]) if not gestation_df.empty else 0
in_heat_animals = 0
if not breeding_df.empty:
    today = datetime.now().date()
    breeding_df['ultima_data'] = pd.to_datetime(breeding_df['ultima_data']).dt.date
    # Animals expected to be in heat (assuming 21-day cycle)
    breeding_df['proxima_data'] = breeding_df['ultima_data'] + pd.to_timedelta([21]*len(breeding_df), unit='d')
    in_heat_animals = len(breeding_df[(breeding_df['proxima_data'] >= today) & 
                                      (breeding_df['proxima_data'] <= today + timedelta(days=3))])

avg_weight = weight_df['peso'].mean() if not weight_df.empty else 0

# Pen metrics
total_pens = len(pens_df) if not pens_df.empty else 0
pen_capacity = pens_df['capacidade'].sum() if not pens_df.empty else 0

# Calculate current occupancy
current_occupancy = 0
if not pen_allocations_df.empty:
    current_allocations = pen_allocations_df[pen_allocations_df['data_saida'].isna()]
    current_occupancy = len(current_allocations)

occupancy_rate = (current_occupancy / pen_capacity * 100) if pen_capacity > 0 else 0

with col1:
    st.metric("Total de Animais", total_animals)
    
with col2:
    st.metric("Animais em Gestação", pregnant_animals)
    
with col3:
    st.metric("Animais Próximos ao Cio", in_heat_animals)
    
with col4:
    st.metric("Peso Médio (kg)", f"{avg_weight:.2f}" if avg_weight else "N/A")
    
with col5:
    st.metric("Taxa de Ocupação", f"{occupancy_rate:.1f}%" if pen_capacity > 0 else "N/A", 
             help=f"Total de {current_occupancy} animais alocados em baias com capacidade total para {pen_capacity} animais")

# Display charts
st.subheader("Visão Geral")

if not animals_df.empty and not weight_df.empty:
    # Merge data for visualization
    merged_df = pd.merge(weight_df, animals_df, on='id_animal')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribuição de Peso")
        if not merged_df.empty:
            fig = px.histogram(merged_df, x="peso", nbins=10, 
                              labels={"peso": "Peso (kg)", "count": "Contagem"},
                              title="Distribuição de Peso dos Animais")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sem dados de peso para exibir.")
    
    with col2:
        st.subheader("Animais por Categoria")
        if not animals_df.empty:
            category_counts = animals_df['categoria'].value_counts().reset_index()
            category_counts.columns = ['Categoria', 'Contagem']
            fig = px.pie(category_counts, values='Contagem', names='Categoria', 
                        title='Distribuição de Animais por Categoria')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sem animais cadastrados.")

# Recent activities
st.subheader("Atividades Recentes")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Ciclos Reprodutivos", "Gestações", "Registros de Peso", "Inseminações", "Baias"])

with tab1:
    if not breeding_df.empty:
        st.dataframe(breeding_df.sort_values('ultima_data', ascending=False).head(5))
    else:
        st.info("Nenhum registro de ciclo reprodutivo encontrado.")

with tab2:
    if not gestation_df.empty:
        st.dataframe(gestation_df.sort_values('data_cobertura', ascending=False).head(5))
    else:
        st.info("Nenhum registro de gestação encontrado.")

with tab3:
    if not weight_df.empty:
        st.dataframe(weight_df.sort_values('data_registro', ascending=False).head(5))
    else:
        st.info("Nenhum registro de peso encontrado.")
        
with tab4:
    if not insemination_df.empty:
        st.dataframe(insemination_df.sort_values('data_inseminacao', ascending=False).head(5))
    else:
        st.info("Nenhum registro de inseminação encontrado.")
        
with tab5:
    # Show recent pen allocations
    if not pen_allocations_df.empty:
        # Get recent allocations with animal and pen information
        recent_allocations = pen_allocations_df.sort_values('data_entrada', ascending=False).head(5).copy()
        
        # Add animal identification
        if not animals_df.empty:
            recent_allocations['animal'] = recent_allocations['id_animal'].apply(
                lambda x: animals_df[animals_df['id_animal'] == x]['identificacao'].iloc[0] 
                if x in animals_df['id_animal'].values else "Desconhecido"
            )
        else:
            recent_allocations['animal'] = "Desconhecido"
            
        # Add pen identification
        if not pens_df.empty:
            recent_allocations['baia'] = recent_allocations['id_baia'].apply(
                lambda x: pens_df[pens_df['id_baia'] == x]['identificacao'].iloc[0] 
                if x in pens_df['id_baia'].values else "Desconhecida"
            )
        else:
            recent_allocations['baia'] = "Desconhecida"
        
        # Display only relevant columns
        display_cols = ['animal', 'baia', 'data_entrada', 'data_saida', 'status']
        st.dataframe(recent_allocations[display_cols].rename(columns={
            'animal': 'Animal', 
            'baia': 'Baia', 
            'data_entrada': 'Data de Entrada', 
            'data_saida': 'Data de Saída', 
            'status': 'Status'
        }))
    else:
        st.info("Nenhum registro de alocação de baias encontrado.")

# Get started guide
st.subheader("Como Começar")
st.markdown("""
1. Use a página de **Cadastro Animal** para adicionar novos animais
2. Registre os ciclos reprodutivos na página **Ciclo Reprodutivo**
3. Monitore os rufiões e detecção de cio na página **Rufia**
4. Monitore as gestações na página **Gestação**
5. Registre medições de peso na página **Peso e Idade**
6. Registre inseminações na página **Inseminação**
7. Cadastre e gerencie baias na página **Baias**
8. Gerencie a maternidade na página **Maternidade**
9. Registre desmame de leitões na página **Desmame**
10. Gerencie os lotes na creche na página **Creche**
11. Cadastre e selecione leitoas na página **Seleção de Leitoas**
12. Gerencie o programa de vacinação na página **Vacinas**
13. Registre e monitore a mortalidade na página **Mortalidade**
14. Visualize relatórios e exporte dados na página **Relatórios**

**Dicas importantes:**
- Mantenha os registros de vacinação atualizados para garantir a saúde do plantel
- Use o sistema de rufia regularmente para detecção precisa do cio
- Registre todas as mortes e suas causas para análise e prevenção
- Acompanhe os relatórios para identificar tendências e tomar decisões informadas
""")

# Footer
st.markdown("---")
st.markdown("© 2025 Sistema de Gestão Suinocultura")