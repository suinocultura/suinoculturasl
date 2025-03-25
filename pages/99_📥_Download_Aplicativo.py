import streamlit as st
import base64
import os
import sys

# Adicionar diretório raiz ao path para importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import check_developer_access, check_permission

# Configuração da página
st.set_page_config(
    page_title="Download do Aplicativo",
    page_icon="📥",
    layout="centered"
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
if not check_permission(st.session_state.current_user, 'developer_tools'):
    st.error("Você não tem permissão para acessar esta página.")
    st.stop()


# Verificar se o usuário está autenticado e tem permissão para baixar o aplicativo
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.error("Você precisa estar autenticado para acessar esta página.")
    st.stop()

if "current_user" not in st.session_state or not check_permission(st.session_state.current_user, 'developer_tools'):
    st.error("Você não tem permissão para acessar esta página. Apenas desenvolvedores têm acesso.")
    st.stop()

# Estilo CSS personalizado
st.markdown("""
<style>
    .download-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .header-style {
        color: #4527A0;
        text-align: center;
    }
    .subheader-style {
        color: #5E35B1;
        text-align: center;
    }
    .new-method-badge {
        background-color: #E53935;
        color: white;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 12px;
        margin-left: 8px;
    }
    .method-container {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        background-color: white;
    }
    .method-header {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="header-style">Download - Sistema de Gestão Suinocultura</h1>', unsafe_allow_html=True)
st.markdown('<h3 class="subheader-style">Faça o download do aplicativo completo para uso offline</h3>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; font-weight:bold; color:#4CAF50;">Nova versão 2.1 disponível!</p>', unsafe_allow_html=True)

st.markdown("---")

with st.container():
    st.markdown('<div class="download-container">', unsafe_allow_html=True)
    
    st.markdown("""
    ### Conteúdo do Pacote
    Este arquivo ZIP contém o código-fonte completo do Sistema de Gestão Suinocultura, incluindo:
    - Todos os arquivos Python
    - Todas as páginas da aplicação
    - Arquivos de dados (CSVs)
    - Arquivos de configuração
    
    ### Novidades da Versão 2.1
    - **Suporte à integração com GitHub** - Permite sincronização direta com repositórios
    - **Visualização destacada de notas importantes** - Melhor organização das informações críticas
    - **Histórico de atualizações completo** - Acompanhe todas as mudanças do sistema
    """)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Função para gerar o link de download
def get_download_link(file_path, link_text):
    if not os.path.exists(file_path):
        st.error(f"Arquivo {file_path} não encontrado!")
        return ""
    
    with open(file_path, "rb") as f:
        data = f.read()
    
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:application/zip;base64,{b64}" download="{os.path.basename(file_path)}" style="text-decoration:none;">'\
           f'<div style="background-color:#4CAF50; color:white; padding:12px 20px; border-radius:8px; '\
           f'cursor:pointer; text-align:center; font-weight:bold; margin:20px 0px;">{link_text}</div></a>'
    
    return href

# Sempre criar um novo arquivo ZIP com a data atual
import datetime
current_date = datetime.datetime.now().strftime("%Y%m%d")
zip_path = f"suinocultura_{current_date}.zip"
cloud_zip_path = f"suinocultura_cloud_deploy_{current_date}.zip"

# Forçar a criação de um novo arquivo para garantir que esteja atualizado
st.info("Preparando os arquivos para download... Por favor, aguarde.")
import sys
import importlib.util

# Carregar e executar o script create_download_package.py para pacote completo
spec = importlib.util.spec_from_file_location("create_download_package", "create_download_package.py")
module = importlib.util.module_from_spec(spec)
sys.modules["create_download_package"] = module
spec.loader.exec_module(module)

# Executar a função
module.create_download_package()

# Carregar e executar o script prepare_streamlit_cloud.py para pacote do Streamlit Cloud
spec_cloud = importlib.util.spec_from_file_location("prepare_streamlit_cloud", "prepare_streamlit_cloud.py")
module_cloud = importlib.util.module_from_spec(spec_cloud)
sys.modules["prepare_streamlit_cloud"] = module_cloud
spec_cloud.loader.exec_module(module_cloud)

# Executar a função
module_cloud.create_deploy_package()

# Verificar se os arquivos foram criados
if not os.path.exists(zip_path):
    st.error("Não foi possível criar o arquivo completo para download. Por favor, tente novamente mais tarde.")

if not os.path.exists(cloud_zip_path):
    st.error("Não foi possível criar o arquivo para deploy no Streamlit Cloud. Por favor, tente novamente mais tarde.")

# Mostrar os botões de download
st.subheader("Pacote Completo")
st.markdown("Este pacote contém todos os arquivos do sistema, incluindo utilitários de desenvolvimento e ferramentas auxiliares.")
if os.path.exists(zip_path):
    st.markdown(get_download_link(zip_path, "CLIQUE AQUI PARA BAIXAR O PACOTE COMPLETO"), unsafe_allow_html=True)
    
    file_size = round(os.path.getsize(zip_path) / (1024), 2)
    st.caption(f"Tamanho do arquivo: {file_size} KB")

st.markdown("---")

st.subheader("Pacote para Deploy no Streamlit Cloud")
st.markdown("Este pacote contém apenas os arquivos necessários para deploy no Streamlit Community Cloud, otimizado para publicação online.")

col1, col2 = st.columns(2)

with col1:
    if os.path.exists(cloud_zip_path):
        st.markdown(get_download_link(cloud_zip_path, "BAIXAR PACOTE PARA STREAMLIT CLOUD"), unsafe_allow_html=True)
        
        file_size = round(os.path.getsize(cloud_zip_path) / (1024), 2)
        st.caption(f"Tamanho do arquivo: {file_size} KB")

with col2:
    st.markdown("""
    <div style="background-color:#1E88E5; color:white; padding:12px 20px; border-radius:8px; cursor:pointer; text-align:center; font-weight:bold; margin:20px 0px;">
    <a href="#" id="deploy-github" style="text-decoration:none; color:white;">ENVIAR DIRETAMENTE PARA O GITHUB</a>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Envia os arquivos e cria um repositório automaticamente")

# Seção para Deploy no GitHub
st.markdown("---")
st.subheader("Deploy Direto no GitHub")
st.markdown("Envie os arquivos diretamente para um repositório GitHub e prepare para o deploy no Streamlit Cloud.")

# Importar o módulo
import importlib.util
try:
    spec = importlib.util.spec_from_file_location("github_deploy", "github_deploy.py")
    github_module = importlib.util.module_from_spec(spec)
    sys.modules["github_deploy"] = github_module
    spec.loader.exec_module(github_module)
    
    # Carregar credenciais salvas, se existirem
    github_credentials = github_module.load_github_credentials()
    
    with st.form(key="github_deploy_form"):
        st.markdown("### Credenciais do GitHub")
        
        username = st.text_input("Usuário do GitHub", 
                               value=github_credentials.get("username", "") if github_credentials else "",
                               help="Seu nome de usuário do GitHub")
        
        token = st.text_input("Token de Acesso Pessoal", 
                            value=github_credentials.get("token", "") if github_credentials else "",
                            type="password",
                            help="Token de acesso pessoal do GitHub com permissões para criar repositórios e enviar arquivos")
        
        repo_name = st.text_input("Nome do Repositório", 
                                value=github_credentials.get("repo_name", f"suinocultura-streamlit-{current_date}") if github_credentials else f"suinocultura-streamlit-{current_date}",
                                help="Nome do repositório no GitHub (será criado se não existir)")
        
        repo_owner = st.text_input("Proprietário do Repositório", 
                                 value=github_credentials.get("repo_owner", "") if github_credentials else "",
                                 help="Usuário ou organização proprietária do repositório (deixe em branco para usar seu usuário)")
        
        save_credentials = st.checkbox("Salvar credenciais para uso futuro", value=True)
        
        submit_button = st.form_submit_button(label="Enviar para o GitHub")
        
        if submit_button:
            if not username or not token:
                st.error("Por favor, preencha o usuário e token do GitHub")
            else:
                with st.spinner("Enviando arquivos para o GitHub..."):
                    success, message = github_module.deploy_to_github(
                        username=username,
                        token=token,
                        repo_name=repo_name,
                        repo_owner=repo_owner if repo_owner else username,
                        use_saved_credentials=False
                    )
                    
                    if save_credentials:
                        github_module.save_github_credentials(
                            username=username,
                            token=token,
                            repo_name=repo_name,
                            repo_owner=repo_owner if repo_owner else username
                        )
                    
                    if success:
                        st.success(message)
                        
                        # Extrair a URL do Streamlit Cloud da mensagem
                        import re
                        match = re.search(r'(https://share\.streamlit\.io/deploy\?.*)', message)
                        if match:
                            streamlit_url = match.group(1)
                            st.markdown(f"[Clique aqui para implantar no Streamlit Cloud]({streamlit_url})", unsafe_allow_html=False)
                    else:
                        st.error(message)
except Exception as e:
    st.error(f"Erro ao carregar o módulo de deploy para GitHub: {str(e)}")
    st.info("Você pode baixar o pacote e enviá-lo manualmente para o GitHub.")



# Instruções adicionais
with st.expander("Instruções para usar o arquivo baixado", expanded=True):
    st.markdown("""
    ### Como usar o pacote completo:
    
    1. Descompacte o arquivo ZIP em seu computador
    2. Certifique-se de ter o Python e as bibliotecas necessárias instaladas:
       ```
       pip install streamlit pandas numpy matplotlib plotly
       ```
    3. Execute a aplicação com o comando:
       ```
       streamlit run app.py
       ```
    
    ### Como fazer deploy no Streamlit Cloud:
    
    1. Descompacte o arquivo "suinocultura_cloud_deploy_XXXXXXXX.zip"
    2. Crie um novo repositório público no GitHub
    3. Faça upload de todos os arquivos extraídos para o repositório
    4. Acesse o Streamlit Community Cloud (https://streamlit.io/cloud)
    5. Conecte-se com sua conta GitHub
    6. Clique em "New app"
    7. Selecione o repositório que você criou
    8. Em "Main file path", mantenha "app.py"
    9. Clique em "Deploy!"
    10. Configure as secrets conforme o arquivo .streamlit/secrets.toml.example
    """)

with st.expander("Problemas ao baixar?"):
    st.markdown("""
    Se você estiver enfrentando problemas para baixar o arquivo, tente estas alternativas:
    
    1. Use um navegador diferente (Chrome, Firefox, Edge)
    2. Desabilite temporariamente bloqueadores de pop-up ou extensões
    3. Entre em contato com o desenvolvedor para receber o arquivo por e-mail
    """)

# Rodapé
st.markdown("---")
st.caption("Sistema de Gestão Suinocultura © 2025 - Todos os direitos reservados")