import streamlit as st

# Adicionar import do utils para check_permission
from utils import check_permission

st.set_page_config(page_title="RELATÓRIOS", page_icon="📊", layout="wide")

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
if not check_permission(st.session_state.current_user, 'view_reports'):
    st.error("Você não tem permissão para acessar esta página.")
    st.stop()


# Verificar autenticação
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Você precisa estar autenticado para acessar esta página.")
    st.stop()

st.title("🔹 RELATÓRIOS")
st.write("Acesse os relatórios gerenciais através do menu lateral")

st.write("""
## Módulos de Relatórios
         
Esta seção contém relatórios gerenciais e análises de desempenho, incluindo:

- Relatórios de Produção
- Relatórios de Reprodução
- Indicadores de Desempenho
- Análises Financeiras
- Estatísticas do Plantel

Navegue para os relatórios específicos a partir do menu lateral.
""")

# Adicionar alguns cards para acesso rápido
col1, col2, col3 = st.columns(3)

with col1:
    st.info("""
    ### Relatórios de Produção
    Análises de produtividade e eficiência
    """)
    
with col2:
    st.info("""
    ### Indicadores Reprodutivos
    Análise do desempenho reprodutivo do plantel
    """)
    
with col3:
    st.info("""
    ### Análises Financeiras
    Custos, receitas e indicadores econômicos
    """)