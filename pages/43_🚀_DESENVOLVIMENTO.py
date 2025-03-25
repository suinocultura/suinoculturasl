import streamlit as st

# Adicionar import do utils para check_permission
from utils import check_permission

st.set_page_config(page_title="DESENVOLVIMENTO", page_icon="📈", layout="wide")

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

st.title("🔹 DESENVOLVIMENTO")
st.write("Acesse as funcionalidades de desenvolvimento através do menu lateral")

st.write("""
## Módulos de Desenvolvimento
         
Esta seção contém ferramentas para o gerenciamento do desenvolvimento dos animais, incluindo:

- Sistema de Recria
- Seleção de Leitoas
- Nutrição Animal
- Desempenho Zootécnico
- Análise de Conversão Alimentar

Navegue para as páginas específicas a partir do menu lateral.
""")

# Adicionar alguns cards para acesso rápido
col1, col2 = st.columns(2)

with col1:
    st.info("""
    ### Sistema de Recria
    Gestão completa do sistema de recria com formação de lotes, 
    monitoramento de peso, alimentação e medicação
    """)
    
with col2:
    st.info("""
    ### Seleção de Leitoas
    Processo de seleção e descarte de leitoas para reprodução
    """)