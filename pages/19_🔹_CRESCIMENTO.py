import streamlit as st

st.set_page_config(page_title="CRESCIMENTO E ALOJAMENTO", page_icon="🔹", layout="wide")

# Verificar autenticação
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Você precisa estar autenticado para acessar esta página.")
    st.stop()

# Elementos de estilo personalizado para a barra lateral
# Isso é injetado para criar um efeito de "seção" colorida no sidebar
st.markdown("""
<style>
    [data-testid="stSidebarNav"] li:has(div p:contains("🔹 CRESCI")) div p {
        color: #38B000 !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        background-color: rgba(56, 176, 0, 0.1);
        padding: 5px;
        border-radius: 5px;
        margin-bottom: 10px;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Estilo com fundo colorido para a categoria
st.markdown("""
<div style="background-color:#38B000; padding: 10px; border-radius: 10px; margin-bottom: 10px;">
    <h1 style="color:white; text-align:center;">🔹 CRESCIMENTO E ALOJAMENTO</h1>
</div>
""", unsafe_allow_html=True)
st.write("Acesse as funcionalidades de crescimento e alojamento através do menu lateral")

st.write("""
## Módulos de Crescimento e Alojamento
         
Esta seção contém ferramentas para o gerenciamento do crescimento e alojamento dos animais, incluindo:

- Registro de Peso e Idade
- Gerenciamento de Baias
- Maternidade
- Desmame
- Creche
- Seleção de Leitoas

Navegue para as páginas específicas a partir do menu lateral.
""")

# Adicionar alguns cards para acesso rápido
col1, col2, col3 = st.columns(3)

with col1:
    st.info("""
    ### Peso e Idade
    Registro e análise de peso por idade
    """)
    
with col2:
    st.info("""
    ### Baias
    Gerenciamento de instalações e alojamento
    """)
    
with col3:
    st.info("""
    ### Maternidade
    Acompanhamento da maternidade
    """)