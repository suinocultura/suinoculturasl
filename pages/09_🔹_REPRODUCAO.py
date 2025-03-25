import streamlit as st

st.set_page_config(page_title="REPRODUÇÃO", page_icon="🔹", layout="wide")

# Verificar autenticação
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Você precisa estar autenticado para acessar esta página.")
    st.stop()

# Elementos de estilo personalizado para a barra lateral
# Isso é injetado para criar um efeito de "seção" colorida no sidebar
st.markdown("""
<style>
    [data-testid="stSidebarNav"] li:has(div p:contains("🔹 REPRODU")) div p {
        color: #FF6B6B !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        background-color: rgba(255, 107, 107, 0.1);
        padding: 5px;
        border-radius: 5px;
        margin-bottom: 10px;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Estilo com fundo colorido para a categoria
st.markdown("""
<div style="background-color:#FF6B6B; padding: 10px; border-radius: 10px; margin-bottom: 10px;">
    <h1 style="color:white; text-align:center;">🔹 REPRODUÇÃO</h1>
</div>
""", unsafe_allow_html=True)
st.write("Acesse as funcionalidades de reprodução através do menu lateral")

st.write("""
## Módulos de Reprodução
         
Esta seção contém ferramentas para o gerenciamento reprodutivo do plantel, incluindo:

- Ciclos Reprodutivos
- Gestação
- Inseminação Artificial
- Detecção de Cio
- Rufia

Navegue para as páginas específicas a partir do menu lateral.
""")

# Adicionar alguns cards para acesso rápido
col1, col2, col3 = st.columns(3)

with col1:
    st.info("""
    ### Ciclo Reprodutivo
    Gerenciamento dos ciclos de reprodução
    """)
    
with col2:
    st.info("""
    ### Gestação
    Acompanhamento das gestações
    """)
    
with col3:
    st.info("""
    ### Inseminação
    Registro e controle de inseminações artificiais
    """)