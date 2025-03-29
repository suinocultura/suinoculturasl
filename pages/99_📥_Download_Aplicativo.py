import streamlit as st
import base64
import os
import sys
import json
import datetime
import importlib.util

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

# Mostrar a versão atual e última atualização
try:
    update_file = "data/updates_history.json"
    if os.path.exists(update_file):
        with open(update_file, "r", encoding="utf-8") as f:
            updates_data = json.load(f)
        
        if updates_data.get("versoes"):
            ultima = updates_data["versoes"][0]
            versao = ultima.get('versao', '2.1')
            data_update = ultima.get('data', datetime.datetime.now().strftime("%Y-%m-%d"))
            st.markdown(f'<p style="text-align:center; font-weight:bold; color:#4CAF50;">Versão {versao} disponível! <span style="color:#757575; font-size:0.9em;">(Última atualização: {data_update})</span></p>', unsafe_allow_html=True)
        else:
            st.markdown('<p style="text-align:center; font-weight:bold; color:#4CAF50;">Nova versão 2.1 disponível!</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="text-align:center; font-weight:bold; color:#4CAF50;">Nova versão 2.1 disponível!</p>', unsafe_allow_html=True)
except Exception as e:
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
    - Aplicativo Android Offline (kivy_app_offline)
    
    ### Novidades da Versão 2.2
    - **Aplicativo Android Offline** - Utilize o sistema mesmo sem conexão com internet
    - **Banco de dados SQLite** - Armazenamento local de dados no aplicativo offline
    - **Sincronização de dados** - Exporte e importe dados entre o aplicativo e o sistema web
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

# Adicionando seção para o aplicativo Android Offline
st.subheader("📱 Aplicativo Android Offline (Novo!)")
st.markdown("Esta opção permite utilizar o sistema sem conexão de internet em dispositivos Android, com armazenamento local de dados.")

# Abas para escolher entre APK completo, Pydroid3 ou Streamlit Pydroid3
tab_apk, tab_pydroid, tab_streamlit = st.tabs(["APK Compilado", "Pacote Pydroid3 (Kivy)", "Pacote Streamlit Pydroid3"])

with tab_apk:
    # Colapsar expansão para mostrar a estrutura de diretórios
    with st.expander("Ver estrutura do aplicativo offline", expanded=False):
        st.code("""
kivy_app_offline/
├── assets/
│   ├── logo_placeholder.png
│   └── logo_placeholder.svg
├── main.py           # Aplicativo principal
├── buildozer.spec    # Configuração para build do APK
├── suinocultura.kv   # Layout em Kivy Language
└── README.md         # Instruções de uso
        """)

with tab_pydroid:
    st.markdown("""
    ### Pacote para Pydroid3 com Kivy 🚀
    
    Esta versão permite executar o aplicativo diretamente no **Pydroid3**, um ambiente Python para Android, 
    sem necessidade de compilar um APK.
    
    #### Vantagens:
    - **Instalação simplificada**: Execute diretamente no Pydroid3
    - **Atualizações fáceis**: Substitua apenas os arquivos Python
    - **Ambiente flexível**: Acesse o código-fonte e faça adaptações personalizadas
    - **Mesmo banco de dados SQLite**: Total compatibilidade com a versão APK
    
    #### Como usar:
    1. Baixe o pacote Pydroid3 abaixo
    2. Instale o Pydroid3 da Google Play Store
    3. Extraia o arquivo ZIP em seu dispositivo Android
    4. Abra o Pydroid3 e navegue até o arquivo main.py
    5. Execute o aplicativo
    """)
    
    # Link para download do pacote Pydroid3
    pydroid_zip_path = f"suinocultura_pydroid3_{current_date}.zip"
    
    if os.path.exists(pydroid_zip_path):
        st.markdown(get_download_link(pydroid_zip_path, "BAIXAR PACOTE KIVY PYDROID3"), unsafe_allow_html=True)
        file_size = round(os.path.getsize(pydroid_zip_path) / (1024), 2)
        st.caption(f"Tamanho do arquivo: {file_size} KB")
    else:
        st.warning("Pacote Pydroid3 não encontrado. Você pode criá-lo executando o script create_pydroid3_package.py.")
        
        if st.button("Gerar Pacote Pydroid3 Kivy", type="primary"):
            try:
                spec = importlib.util.spec_from_file_location("create_pydroid3_package", "create_pydroid3_package.py")
                module = importlib.util.module_from_spec(spec)
                sys.modules["create_pydroid3_package"] = module
                spec.loader.exec_module(module)
                
                # Executar a função
                with st.spinner("Gerando pacote Pydroid3 Kivy..."):
                    module.create_pydroid3_package()
                    st.success("Pacote Pydroid3 Kivy gerado com sucesso!")
                    st.rerun()
            except Exception as e:
                st.error(f"Erro ao gerar pacote Pydroid3 Kivy: {str(e)}")
                
    with st.expander("Detalhes sobre o Pydroid3 com Kivy", expanded=False):
        st.markdown("""
        O **Pydroid3** é um ambiente de desenvolvimento Python completo para Android que inclui:
        
        - Interpretador Python 3
        - Editor com syntax highlighting
        - Terminal pip para instalação de pacotes
        - Suporte a bibliotecas como Kivy, NumPy, etc.
        - Terminal interativo
        
        O pacote Pydroid3 com Kivy do Sistema Suinocultura inclui todos os arquivos necessários para 
        executar o aplicativo neste ambiente, mantendo as mesmas funcionalidades da versão APK.
        """)
        
        st.info("O pacote inclui um arquivo README_PYDROID3.md com instruções detalhadas de instalação e uso.")

with tab_streamlit:
    st.markdown("""
    ### Pacote Streamlit para Pydroid3 (Novidade!) 🌟
    
    Esta é a versão web completa do Sistema Suinocultura adaptada para execução no **Pydroid3**.
    Ao invés da interface Kivy, utiliza o Streamlit para fornecer a mesma experiência da versão web.
    
    #### Vantagens:
    - **Interface Web Completa**: Mesma experiência da versão Streamlit Cloud
    - **Funcionalidades Avançadas**: Acesso a todos os módulos e recursos do sistema web
    - **Visualizações Interativas**: Gráficos, tabelas e componentes visuais completos
    - **Sistema Multiusuário**: Suporte a autenticação e níveis de permissão
    - **Versão Standalone**: Funciona completamente offline no seu dispositivo
    
    #### Como usar:
    1. Baixe o pacote Streamlit Pydroid3 abaixo
    2. Instale o Pydroid3 da Google Play Store
    3. Extraia o arquivo ZIP em seu dispositivo Android
    4. Abra o Pydroid3 e execute o arquivo setup.py para instalar dependências
    5. Depois, execute app.py para iniciar o sistema
    6. O sistema estará disponível no navegador em http://localhost:8501
    """)
    
    # Link para download do pacote Streamlit Pydroid3
    streamlit_pydroid_zip_path = f"suinocultura_streamlit_pydroid3_{current_date}.zip"
    
    if os.path.exists(streamlit_pydroid_zip_path):
        st.markdown(get_download_link(streamlit_pydroid_zip_path, "BAIXAR PACOTE STREAMLIT PYDROID3"), unsafe_allow_html=True)
        file_size = round(os.path.getsize(streamlit_pydroid_zip_path) / (1024), 2)
        st.caption(f"Tamanho do arquivo: {file_size} KB")
    else:
        st.warning("Pacote Streamlit Pydroid3 não encontrado. Você pode criá-lo executando o script create_streamlit_pydroid3_package.py.")
        
        if st.button("Gerar Pacote Streamlit Pydroid3", type="primary"):
            try:
                spec = importlib.util.spec_from_file_location("create_streamlit_pydroid3_package", "create_streamlit_pydroid3_package.py")
                module = importlib.util.module_from_spec(spec)
                sys.modules["create_streamlit_pydroid3_package"] = module
                spec.loader.exec_module(module)
                
                # Executar a função
                with st.spinner("Gerando pacote Streamlit Pydroid3..."):
                    module.create_streamlit_pydroid3_package()
                    st.success("Pacote Streamlit Pydroid3 gerado com sucesso!")
                    st.rerun()
            except Exception as e:
                st.error(f"Erro ao gerar pacote Streamlit Pydroid3: {str(e)}")
                
    with st.expander("Detalhes sobre o Streamlit no Pydroid3", expanded=False):
        st.markdown("""
        Esta versão combina:
        
        - **Streamlit**: Framework web para criar interfaces de usuário interativas com Python
        - **Pydroid3**: Ambiente Python completo para Android
        - **Sistema Suinocultura**: Versão completa com todas as funcionalidades web
        
        O pacote vem com:
        - Script de setup para instalação automatizada das dependências
        - Configuração otimizada para o ambiente Android
        - Páginas principais do sistema já pré-configuradas
        - Dados de exemplo para uso imediato
        
        **Requisitos de Hardware**:
        - Dispositivo Android 7.0 ou superior
        - Mínimo de 3GB de RAM (4GB ou mais recomendado)
        - 250MB de espaço livre para as dependências
        """)
        
        st.info("O pacote inclui um README com instruções detalhadas de instalação e uso, além de um script de setup para configuração automática.")
    
# Exemplo de interface fora do expander
st.subheader("Exemplo de interface Streamlit no Android")
st.image("https://streamlit.io/images/brand/streamlit-logo-primary-colormark-darktext.png", width=200)
st.caption("Interface web com todas as funcionalidades do sistema Suinocultura executando localmente no seu dispositivo Android.")
    

# Mostrar recursos do aplicativo offline
st.markdown("""
### Funcionalidades do Aplicativo Offline:

- **Banco de dados SQLite** para armazenamento local de dados
- **Cadastro e gerenciamento de animais** mesmo sem conexão
- **Exportação e importação de dados** para sincronização com o sistema web
- **Interface amigável** seguindo o mesmo estilo visual do sistema web
- **Login simplificado** para acesso rápido
- **Sincronização com Cloud** para manter os dados atualizados entre dispositivos

### Sincronização com Firestore:

O aplicativo permite sincronizar os dados locais com o Firebase Firestore:

- **Exportação Automática**: Os dados são exportados em formato JSON
- **Sincronização Online**: Quando conectado à internet, os dados são enviados para o Firestore
- **Armazenamento Seguro**: Os dados são armazenados com isolamento por usuário
- **Recuperação de Dados**: Possibilidade de recuperar dados do Firestore em caso de perda do dispositivo

### Como compilar o APK:

Para compilar o aplicativo Android, você precisará do ambiente Buildozer configurado:

```bash
cd kivy_app_offline
buildozer -v android debug
```

O APK será gerado na pasta bin/ e poderá ser instalado em qualquer dispositivo Android compatível.
""")

st.markdown("---")

# Adicionando seção para Firebase
st.subheader("📱 Deploy no Firebase")
st.markdown("Esta opção cria uma landing page e uma plataforma de download para o aplicativo Android no Firebase Hosting.")

# Verificar se os arquivos Firebase existem
firebase_files_exist = os.path.exists("firebase.json") and os.path.exists(".firebaserc") and os.path.exists("build-firebase.js")

if firebase_files_exist:
    st.success("Configuração Firebase pronta! Use os arquivos para fazer o deploy.")
    
    col_f1, col_f2 = st.columns(2)
    
    with col_f1:
        # Link para README_DEPLOY.md
        with open("README_DEPLOY.md", "r") as f:
            readme_content = f.read()
        
        st.download_button(
            label="BAIXAR INSTRUÇÕES FIREBASE",
            data=readme_content,
            file_name="INSTRUCOES_FIREBASE.md",
            mime="text/markdown",
            use_container_width=True
        )
        
    with col_f2:
        if st.button("EXECUTAR BUILD FIREBASE", 
                    key="firebase_build", 
                    use_container_width=True,
                    type="primary"):
            with st.spinner("Executando build para Firebase..."):
                try:
                    import subprocess
                    result = subprocess.run(["node", "build-firebase.js"], capture_output=True, text=True)
                    if result.returncode == 0:
                        st.success("Build Firebase concluído com sucesso!")
                    else:
                        st.error(f"Erro no build: {result.stderr}")
                except Exception as e:
                    st.error(f"Erro ao executar o build Firebase: {str(e)}")
    
    # Mostrar os arquivos Firebase
    st.subheader("Arquivos de Configuração Firebase")
    
    # Configuração Firebase em duas colunas
    col_config1, col_config2 = st.columns(2)
    
    with col_config1:
        st.markdown("**📄 .firebaserc**")
        st.code("""
{
  "projects": {
    "default": "suinocultura-app"
  }
}
        """, language="json")
    
    with col_config2:
        st.markdown("**📄 firebase.json**")
        st.code("""
{
  "hosting": {
    "public": "build",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
    "rewrites": [
      {
        "source": "**",
        "destination": "/index.html"
      }
    ]
  }
}
        """, language="json")
    
    # Script de build em expander separado
    with st.expander("Script de Build (build-firebase.js)", expanded=False):
        with open("build-firebase.js", "r") as f:
            firebase_script = f.read()
        st.code(firebase_script, language="javascript")
else:
    st.warning("Os arquivos de configuração do Firebase não foram encontrados.")

st.markdown("---")

# Instruções rápidas para Firebase
with st.expander("Como fazer deploy no Firebase", expanded=True):
    st.markdown("""
    ### Passo a passo para Deploy no Firebase
    
    1. **Baixe o arquivo de instruções** detalhadas (botão acima)
    2. **Crie um projeto no Firebase**:
       - Acesse [console.firebase.google.com](https://console.firebase.google.com/)
       - Clique em "Adicionar projeto"
       - Siga as instruções do assistente
    
    3. **Em seu computador local** (recomendado):
       - Instale as ferramentas do Firebase:
       ```bash
       npm install -g firebase-tools
       ```
       - Faça login no Firebase:
       ```bash
       firebase login
       ```
       - Gere um token para usar no Replit:
       ```bash
       firebase login:ci
       # Copie o token gerado
       ```
    
    4. **Alternativa: Use o arquivo ZIP completo**:
       - Baixe o pacote completo (botão acima na página)
       - Descompacte em seu computador
       - Faça todos os passos localmente
    
    5. **Execute o build** (botão acima ou comando):
       ```bash
       node build-firebase.js
       ```
    
    6. **Configure as credenciais** do Firebase em build/firebase-config.js
    
    7. **Faça o deploy**:
       ```bash
       # Em ambiente local onde você fez login:
       firebase deploy
       
       # OU no Replit usando o token (substitua pelo seu token):
       firebase deploy --token "TOKEN"
       ```
    
    8. **Acesse seu site**: O URL será exibido após o deploy
    """)

st.markdown("---")

st.subheader("📊 Pacote para Deploy no Streamlit Cloud")
st.markdown("""
Este pacote contém apenas os arquivos necessários para deploy no Streamlit Community Cloud, 
otimizado para publicação online com todas as correções aplicadas.

#### ✅ Melhorias no pacote Streamlit Cloud:
- **Verificação avançada de conflitos**: Detecta e corrige conflitos de nomes entre páginas
- **Remoção de arquivos duplicados**: Elimina automaticamente arquivos que possam causar erros
- **Normalização de emojis**: Resolve conflitos causados por caracteres especiais
- **Compatibilidade garantida**: Testado para funcionar sem problemas no Streamlit Cloud
- **Estrutura otimizada**: Inclui apenas os arquivos essenciais para o deploy
""")

col1, col2 = st.columns(2)

with col1:
    if os.path.exists(cloud_zip_path):
        st.markdown(get_download_link(cloud_zip_path, "BAIXAR PACOTE PARA STREAMLIT CLOUD"), unsafe_allow_html=True)
        
        file_size = round(os.path.getsize(cloud_zip_path) / (1024), 2)
        st.caption(f"Tamanho do arquivo: {file_size} KB")
    st.caption("Baixe e envie manualmente para o GitHub")

with col2:
    # Criando botão via Streamlit
    if st.button("ENVIAR DIRETAMENTE PARA O GITHUB", 
                key="github_button", 
                use_container_width=True,
                type="primary"):
        st.session_state.show_github_form = True
        st.rerun()
        
    st.caption("Envia os arquivos e cria um repositório automaticamente")

# Inicializar estado de sessão para o formulário de GitHub se ainda não existir
if 'show_github_form' not in st.session_state:
    st.session_state.show_github_form = False

# Seção para Deploy no GitHub
if st.session_state.show_github_form:
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
            
            # Opção para selecionar quais arquivos enviar
            st.markdown("### Opções de Envio")
            upload_option = st.radio(
                "Selecione como deseja enviar os arquivos:",
                ["Enviar apenas arquivos modificados", "Enviar todos os arquivos"],
                index=0,
                horizontal=True,
                help="Escolha enviar apenas os arquivos modificados (mais rápido) ou todos os arquivos (mais completo)"
            )
            only_modified = upload_option == "Enviar apenas arquivos modificados"
            
            # Opção para tratar conflitos
            conflict_option = st.radio(
                "Como tratar conflitos de página:",
                ["Renomear arquivos conflitantes", "Mover arquivos conflitantes para backup"],
                index=0,
                horizontal=True,
                help="Escolha como resolver problemas de conflitos entre nomes de páginas"
            )
            move_conflicts = conflict_option == "Mover arquivos conflitantes para backup"
            
            if move_conflicts:
                st.success("Em caso de conflitos, os arquivos serão movidos para o diretório 'pages_backup' em vez de apenas renomeá-los. Isso evita problemas persistentes de duplicação no Streamlit Cloud.")
            else:
                st.info("Arquivos conflitantes serão renomeados mantendo-os no diretório 'pages', permitindo que continuem disponíveis na navegação.")
            
            if not only_modified:
                st.info("Todos os arquivos serão enviados para o GitHub, mesmo os que não foram modificados. Isso garante um repositório completo, mas pode levar mais tempo.")
            else:
                st.success("Apenas arquivos modificados serão enviados, tornando o processo mais rápido. Ideal para atualizações incrementais.")
            
            col_submit, col_cancel = st.columns([3, 1])
            
            with col_submit:
                submit_button = st.form_submit_button(label="Enviar para o GitHub")
            
            with col_cancel:
                cancel_button = st.form_submit_button(label="Cancelar")
                if cancel_button:
                    st.session_state.show_github_form = False
                    st.rerun()
            
            if submit_button:
                if not username or not token:
                    st.error("Por favor, preencha o usuário e token do GitHub")
                else:
                    with st.spinner("Enviando arquivos para o GitHub..."):
                        
                        # Antes do deploy, executar verificação de compatibilidade se move_conflicts estiver ativo
                        if move_conflicts:
                            try:
                                # Importar o módulo de verificação de compatibilidade
                                compat_spec = importlib.util.spec_from_file_location("check_pages_compatibility", "check_pages_compatibility.py")
                                compat_module = importlib.util.module_from_spec(compat_spec)
                                sys.modules["check_pages_compatibility"] = compat_module
                                compat_spec.loader.exec_module(compat_module)
                                
                                # Executar a verificação com a opção de mover conflitos
                                compat_module.fix_conflicts(apply_fixes=True, move_conflicts=True)
                                st.info("Verificação de conflitos concluída. Arquivos problemáticos foram movidos para 'pages_backup'.")
                            except Exception as compat_error:
                                st.warning(f"Não foi possível executar a verificação de compatibilidade: {str(compat_error)}")
                        
                        # Preparar pacote com a opção de move_conflicts
                        try:
                            prep_spec = importlib.util.spec_from_file_location("prepare_streamlit_cloud", "prepare_streamlit_cloud.py")
                            prep_module = importlib.util.module_from_spec(prep_spec)
                            sys.modules["prepare_streamlit_cloud"] = prep_module
                            prep_spec.loader.exec_module(prep_module)
                            
                            # Criar o pacote com a opção apropriada
                            if move_conflicts:
                                prep_module.main(["prepare_streamlit_cloud.py", "--move-conflicts"])
                            else:
                                prep_module.main(["prepare_streamlit_cloud.py"])
                        except Exception as prep_error:
                            st.warning(f"Não foi possível preparar o pacote de deploy com opções personalizadas: {str(prep_error)}")
                            
                        success, message = github_module.deploy_to_github(
                            username=username,
                            token=token,
                            repo_name=repo_name,
                            repo_owner=repo_owner if repo_owner else username,
                            use_saved_credentials=False,
                            only_modified=only_modified
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
                            match = re.search(r'(https://streamlit\.io/deploy\?.*)', message)
                            if match:
                                streamlit_url = match.group(1)
                                st.markdown(f"""
                                ### ✨ Pronto para deploy! 
                                
                                [CLIQUE AQUI PARA IMPLANTAR NO STREAMLIT CLOUD]({streamlit_url})
                                
                                Lembre-se de configurar as secrets após o deploy inicial.
                                """, unsafe_allow_html=False)
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
       pip install streamlit pandas numpy matplotlib plotly firebase-admin
       ```
    3. Execute a aplicação com o comando:
       ```
       streamlit run app.py
       ```
    
    ### Como fazer deploy no Streamlit Cloud:
    
    1. Descompacte o arquivo "suinocultura_cloud_deploy_XXXXXXXX.zip"
    2. Crie um novo repositório público no GitHub
    3. Faça upload de todos os arquivos extraídos para o repositório
    4. Acesse o Streamlit Community Cloud (https://streamlit.io)
    5. Faça login com sua conta GitHub
    6. Vá para "Your apps" e clique em "New app"
    7. Selecione o repositório que você criou
    8. Em "Main file path", mantenha "app.py"
    9. Clique em "Deploy!"
    10. **IMPORTANTE:** Configure as secrets nas configurações do aplicativo conforme o arquivo `.streamlit/secrets.toml.example`
    
    #### Observações importantes para o deploy:
    
    - O arquivo `.streamlit/config.toml` foi configurado para ser compatível com o Streamlit Cloud
    - NÃO especifique uma porta personalizada no Streamlit Cloud, deixe usar a porta padrão (8501)
    - O arquivo `requirements.txt` já contém todas as dependências necessárias
    
    #### 🚨 Resolução de problemas no Streamlit Cloud:
    
    Este pacote inclui ferramentas avançadas para evitar problemas comuns de deploy. O sistema:
    
    1. **Detecta e corrige automaticamente conflitos** entre nomes de páginas
    2. **Normaliza arquivos com emojis** que podem causar problemas de navegação
    3. **Remove arquivos de backup duplicados** que geram StreamlitAPIException
    4. **Verifica estrutura de arquivos** para garantir compatibilidade total
    5. **Detecta conflitos de case-insensitive** que causam problemas no Streamlit Cloud
    6. **Reconhece arquivos temporários ocultos** criados por editores de código
    
    Se mesmo assim você encontrar erros durante o deploy:
    
    1. **Execute check_pages_compatibility.py**: Use `python check_pages_compatibility.py --fix` para renomear arquivos conflitantes
    2. **Use a opção de mover conflitos**: `python check_pages_compatibility.py --fix --move-conflicts` para mover arquivos com conflitos persistentes
    3. **Gere um novo pacote**: `python prepare_streamlit_cloud.py --move-conflicts` para garantir a resolução de todos os conflitos
    4. **Verifique as secrets**: Configure corretamente as credenciais em Settings > Secrets
    5. **Confirme dependências**: Certifique-se que o `requirements.txt` está completo
    6. **Consulte o INSTRUCOES_DEPLOY.txt e README_DEPLOY.md**: Contém soluções específicas para os problemas mais comuns
    
    ### Como configurar o Firebase e Firestore:
    
    1. Crie um projeto no Firebase Console: https://console.firebase.google.com/
    2. Ative o Firestore no modo de produção ou teste
    3. Gere uma chave de conta de serviço em Configurações do Projeto > Contas de serviço
    4. Baixe o arquivo JSON de credenciais
    5. No Streamlit Cloud, adicione as credenciais nas secrets:
       ```toml
       [firebase]
       type = "service_account"
       project_id = "seu-projeto-id"
       private_key_id = "chave-privada-id"
       private_key = "-----BEGIN PRIVATE KEY-----\nSua chave privada aqui\n-----END PRIVATE KEY-----\n"
       client_email = "firebase-adminsdk-xxxx@seu-projeto.iam.gserviceaccount.com"
       client_id = "id-do-cliente"
       auth_uri = "https://accounts.google.com/o/oauth2/auth"
       token_uri = "https://oauth2.googleapis.com/token"
       auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
       client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxx%40seu-projeto.iam.gserviceaccount.com"
       universe_domain = "googleapis.com"
       ```
    
    ### Como usar o aplicativo Android offline:
    
    1. Acesse a pasta `kivy_app_offline` dentro do pacote baixado
    2. Se você já tem um APK compilado:
       - Instale o APK diretamente em seu dispositivo Android
    3. Para compilar o aplicativo:
       - Instale o Buildozer (ferramenta para criar APKs com Python/Kivy)
       - Execute `buildozer -v android debug` na pasta kivy_app_offline
       - O APK será gerado na pasta bin/
    4. Para utilizar o aplicativo:
       - Login padrão inicial: Matrícula 123456
       - Utilize o app mesmo sem conexão com internet
       - Para sincronizar, use o botão "Sincronizar com Cloud" no menu principal
       - A sincronização automática acontece quando o dispositivo está online
    """)

with st.expander("Guia Completo de Deployment"):
    st.markdown("""
    ### 📚 Documentação detalhada de deployment
    
    O arquivo `README_DEPLOY.md` contém instruções completas e detalhadas sobre:
    
    - Deploy no Streamlit Community Cloud (passo a passo)
    - Solução de problemas comuns no deploy
    - Melhores práticas para o Streamlit Cloud
    - Deploy no Firebase Hosting
    - Criação de APK Android
    - Perguntas frequentes
    
    👉 **Confira o [guia completo](README_DEPLOY.md) para mais informações.**
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