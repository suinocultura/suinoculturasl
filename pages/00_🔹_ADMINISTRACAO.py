import streamlit as st

st.set_page_config(page_title="ADMINISTRAÇÃO", page_icon="🔹", layout="wide")

# Verificar autenticação
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Você precisa estar autenticado para acessar esta página.")
    st.stop()

# Elementos de estilo personalizado para a barra lateral
# Isso é injetado para criar um efeito de "seção" colorida no sidebar
st.markdown("""
<style>
    [data-testid="stSidebarNav"] li:has(div p:contains("🔹 ADMINIS")) div p {
        color: #1B98E0 !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        background-color: rgba(27, 152, 224, 0.1);
        padding: 5px;
        border-radius: 5px;
        margin-bottom: 10px;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Estilo com fundo colorido para a categoria
st.markdown("""
<div style="background-color:#1B98E0; padding: 10px; border-radius: 10px; margin-bottom: 10px;">
    <h1 style="color:white; text-align:center;">🔹 ADMINISTRAÇÃO</h1>
</div>
""", unsafe_allow_html=True)
st.write("Acesse as funcionalidades de administração através do menu lateral")

st.write("""
## Módulos de Administração
         
Esta seção contém ferramentas para a administração geral do sistema, incluindo:

- Administração do Sistema
- Gestão de Colaboradores
- Cadastro e Gestão de Animais

Navegue para as páginas específicas a partir do menu lateral.
""")

# Adicionar alguns cards para acesso rápido
col1, col2, col3 = st.columns(3)

with col1:
    st.info("""
    ### Administração do Sistema
    Configurações gerais e parâmetros do sistema
    """)
    
with col2:
    st.info("""
    ### Colaboradores
    Cadastro e gestão de colaboradores
    """)
    
with col3:
    st.info("""
    ### Cadastro Animal
    Registro e manutenção de cadastro de animais
    """)