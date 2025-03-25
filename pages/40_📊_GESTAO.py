import streamlit as st

# Adicionar import do utils para check_permission
from utils import check_permission

st.set_page_config(page_title="GESTÃO", page_icon="📊", layout="wide")

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

st.title("🔹 GESTÃO")
st.write("Acesse as funcionalidades de gestão através do menu lateral")

st.write("""
## Módulos de Gestão
         
Esta seção contém ferramentas para a administração geral do sistema, incluindo:

- Administração do Sistema
- Gestão de Colaboradores
- Cadastro de Animais
- Gestão de Baias
- Relatórios Gerais

Navegue para as páginas específicas a partir do menu lateral.
""")

# Adicionar alguns cards para acesso rápido
col1, col2, col3 = st.columns(3)

with col1:
    st.info("""
    ### Administração
    Configurações gerais do sistema e controle de acesso
    """)
    
with col2:
    st.info("""
    ### Colaboradores
    Cadastro e gestão de colaboradores
    """)
    
with col3:
    st.info("""
    ### Relatórios
    Geração de relatórios e estatísticas
    """)