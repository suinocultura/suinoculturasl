import streamlit as st

st.set_page_config(page_title="SAÚDE", page_icon="🔹", layout="wide")

# Verificar autenticação
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Você precisa estar autenticado para acessar esta página.")
    st.stop()

# Elementos de estilo personalizado para a barra lateral
# Isso é injetado para criar um efeito de "seção" colorida no sidebar
st.markdown("""
<style>
    [data-testid="stSidebarNav"] li:has(div p:contains("🔹 SAUDE")) div p {
        color: #F7B801 !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        background-color: rgba(247, 184, 1, 0.1);
        padding: 5px;
        border-radius: 5px;
        margin-bottom: 10px;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Estilo com fundo colorido para a categoria
st.markdown("""
<div style="background-color:#F7B801; padding: 10px; border-radius: 10px; margin-bottom: 10px;">
    <h1 style="color:white; text-align:center;">🔹 SAÚDE</h1>
</div>
""", unsafe_allow_html=True)
st.write("Acesse as funcionalidades de saúde através do menu lateral")

st.write("""
## Módulos de Saúde
         
Esta seção contém ferramentas para o gerenciamento da saúde do plantel, incluindo:

- Gerenciamento de Vacinas
- Controle de Mortalidade

Navegue para as páginas específicas a partir do menu lateral.
""")

# Adicionar alguns cards para acesso rápido
col1, col2 = st.columns(2)

with col1:
    st.info("""
    ### Vacinas
    Gerenciamento do programa de vacinação
    """)
    
with col2:
    st.info("""
    ### Mortalidade
    Registro e análise de mortalidade
    """)