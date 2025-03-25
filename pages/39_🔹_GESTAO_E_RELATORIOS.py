import streamlit as st

st.set_page_config(page_title="GESTÃO E RELATÓRIOS", page_icon="🔹", layout="wide")

# Verificar autenticação
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Você precisa estar autenticado para acessar esta página.")
    st.stop()

# Elementos de estilo personalizado para a barra lateral
# Isso é injetado para criar um efeito de "seção" colorida no sidebar
st.markdown("""
<style>
    [data-testid="stSidebarNav"] li:has(div p:contains("🔹 GESTAO")) div p {
        color: #8C52FF !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        background-color: rgba(140, 82, 255, 0.1);
        padding: 5px;
        border-radius: 5px;
        margin-bottom: 10px;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Estilo com fundo colorido para a categoria
st.markdown("""
<div style="background-color:#8C52FF; padding: 10px; border-radius: 10px; margin-bottom: 10px;">
    <h1 style="color:white; text-align:center;">🔹 GESTÃO E RELATÓRIOS</h1>
</div>
""", unsafe_allow_html=True)
st.write("Acesse as funcionalidades de gestão e relatórios através do menu lateral")

st.write("""
## Módulos de Gestão e Relatórios
         
Esta seção contém ferramentas para gestão e relatórios, incluindo:

- Gestão Geral
- Controle de Produção
- Saúde do Plantel
- Desenvolvimento do Plantel
- Relatórios Gerenciais

Navegue para as páginas específicas a partir do menu lateral.
""")

# Adicionar alguns cards para acesso rápido
col1, col2, col3 = st.columns(3)

with col1:
    st.info("""
    ### Gestão
    Visão geral e ferramentas de gestão
    """)
    
with col2:
    st.info("""
    ### Produção
    Controle e análise de produção
    """)
    
with col3:
    st.info("""
    ### Relatórios
    Relatórios gerenciais e exportação de dados
    """)