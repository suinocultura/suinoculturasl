#!/usr/bin/env python3
"""
Script para enviar arquivos do pacote Streamlit Cloud diretamente para o GitHub
Este script permite a criação automática de um repositório e envio dos arquivos necessários para o Streamlit Cloud
"""

import os
import sys
import json
import base64
import zipfile
import requests
import tempfile
import datetime
import subprocess
import hashlib
from pathlib import Path

def load_github_credentials():
    """
    Carrega as credenciais do GitHub de data/github_credentials.json
    
    Returns:
        dict: Credenciais do GitHub ou None se não existir
    """
    credentials_file = os.path.join("data", "github_credentials.json")
    if os.path.exists(credentials_file):
        with open(credentials_file, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print("Erro ao carregar as credenciais do GitHub. Formato inválido.")
    return None

def save_github_credentials(username, token, repo_name=None, repo_owner=None):
    """
    Salva as credenciais do GitHub de forma segura
    
    Args:
        username (str): Nome de usuário do GitHub
        token (str): Token de acesso pessoal do GitHub
        repo_name (str, optional): Nome do repositório
        repo_owner (str, optional): Proprietário do repositório
    
    Returns:
        bool: True se salvo com sucesso, False caso contrário
    """
    credentials = {
        "username": username,
        "token": token
    }
    
    if repo_name:
        credentials["repo_name"] = repo_name
    
    if repo_owner:
        credentials["repo_owner"] = repo_owner
    
    credentials_file = os.path.join("data", "github_credentials.json")
    
    # Garantir que o diretório data existe
    os.makedirs(os.path.dirname(credentials_file), exist_ok=True)
    
    try:
        with open(credentials_file, "w") as f:
            json.dump(credentials, f, indent=2)
        return True
    except Exception as e:
        print(f"Erro ao salvar as credenciais: {e}")
        return False

def create_github_repository(token, repo_name, description):
    """
    Cria um novo repositório no GitHub
    
    Args:
        token (str): Token de acesso pessoal do GitHub
        repo_name (str): Nome do repositório
        description (str): Descrição do repositório
    
    Returns:
        dict, str: Dados do repositório e mensagem de status
    """
    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "name": repo_name,
        "description": description,
        "private": False,  # Público para permitir deploy no Streamlit Cloud gratuito
        "auto_init": True  # Inicializar com um README
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            return response.json(), "Repositório criado com sucesso!"
        else:
            return None, f"Erro ao criar repositório: {response.json().get('message', 'Erro desconhecido')}"
    except Exception as e:
        return None, f"Erro na comunicação com o GitHub: {str(e)}"

def upload_file_to_github(token, repo_owner, repo_name, file_path, file_content, commit_message):
    """
    Envia um arquivo para o repositório GitHub
    
    Args:
        token (str): Token de acesso pessoal do GitHub
        repo_owner (str): Nome do usuário/organização proprietária do repositório
        repo_name (str): Nome do repositório
        file_path (str): Caminho do arquivo no repositório
        file_content (bytes): Conteúdo do arquivo em bytes
        commit_message (str): Mensagem do commit
    
    Returns:
        bool, str: Sucesso e mensagem
    """
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Codificar conteúdo em base64
    content_encoded = base64.b64encode(file_content).decode("utf-8")
    
    data = {
        "message": commit_message,
        "content": content_encoded
    }
    
    # Verificar se o arquivo já existe
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            # O arquivo existe, precisamos incluir o SHA para atualizá-lo
            sha = response.json()["sha"]
            data["sha"] = sha
    except Exception as e:
        # Ignorar erros, assumir que o arquivo não existe
        pass
    
    try:
        response = requests.put(url, headers=headers, json=data)
        if response.status_code in [200, 201]:
            return True, f"Arquivo {file_path} enviado com sucesso"
        else:
            return False, f"Erro ao enviar {file_path}: {response.json().get('message', 'Erro desconhecido')}"
    except Exception as e:
        return False, f"Erro na comunicação com o GitHub: {str(e)}"

def verify_file_changed(token, repo_owner, repo_name, file_path, local_content):
    """
    Verifica se um arquivo foi modificado em relação à versão no GitHub
    
    Args:
        token (str): Token de acesso pessoal do GitHub
        repo_owner (str): Nome do usuário/organização proprietária do repositório
        repo_name (str): Nome do repositório
        file_path (str): Caminho do arquivo no repositório
        local_content (bytes): Conteúdo do arquivo local
    
    Returns:
        bool: True se o arquivo foi modificado ou não existe no GitHub, False caso contrário
    """
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            # Arquivo existe no GitHub, verificar conteúdo
            github_content = base64.b64decode(response.json()["content"])
            
            # Calcular hashes para comparação
            local_hash = hashlib.md5(local_content).hexdigest()
            github_hash = hashlib.md5(github_content).hexdigest()
            
            # Se os hashes forem diferentes, o arquivo foi modificado
            return local_hash != github_hash
        else:
            # Arquivo não existe no GitHub, considerar como modificado
            return True
    except Exception as e:
        # Em caso de erro, considerar o arquivo como modificado por segurança
        print(f"Erro ao verificar arquivo {file_path}: {str(e)}")
        return True

def validate_streamlit_cloud_compatibility(temp_dir):
    """
    Valida e corrige problemas comuns de compatibilidade com o Streamlit Cloud
    
    Args:
        temp_dir (str): Diretório temporário com os arquivos extraídos
        
    Returns:
        list: Lista de correções aplicadas
    """
    fixes_applied = []
    
    # Verificar configuração do Streamlit
    config_file = os.path.join(temp_dir, ".streamlit", "config.toml")
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            config_content = f.read()
            
        # Remover configuração específica de porta se existir
        if "port =" in config_content:
            config_content = config_content.replace("port = 5000", "")
            config_content = config_content.replace("port = 8501", "")
            
            with open(config_file, "w") as f:
                f.write(config_content)
                
            fixes_applied.append("Configuração de porta removida para compatibilidade com Streamlit Cloud")
    
    # Verificar duplicidade de páginas
    pages_dir = os.path.join(temp_dir, "pages")
    if os.path.exists(pages_dir):
        pages = os.listdir(pages_dir)
        page_names = [p.split("_", 1)[1] if "_" in p else p for p in pages]
        duplicates = set([x for x in page_names if page_names.count(x) > 1])
        
        if duplicates:
            fixes_applied.append(f"Atenção: Encontradas páginas com nomes potencialmente conflitantes: {duplicates}")
    
    # Garantir que o requirements.txt existe e contém as dependências essenciais
    req_file = os.path.join(temp_dir, "requirements.txt")
    required_deps = ["streamlit", "pandas", "numpy", "plotly", "matplotlib"]
    
    if os.path.exists(req_file):
        with open(req_file, "r") as f:
            req_content = f.read()
            
        for dep in required_deps:
            if dep not in req_content:
                with open(req_file, "a") as f:
                    f.write(f"\n{dep}")
                fixes_applied.append(f"Adicionada dependência obrigatória: {dep}")
    
    return fixes_applied

def extract_and_upload_to_github(zip_path, token, repo_owner, repo_name, only_modified=False):
    """
    Extrai os arquivos do pacote ZIP e envia para o GitHub
    
    Args:
        zip_path (str): Caminho para o arquivo ZIP
        token (str): Token de acesso pessoal do GitHub
        repo_owner (str): Nome do usuário/organização proprietária do repositório
        repo_name (str): Nome do repositório
        only_modified (bool, optional): Se True, verifica e envia apenas arquivos modificados
    
    Returns:
        bool, str: Sucesso e mensagem
    """
    if not os.path.exists(zip_path):
        return False, f"Arquivo {zip_path} não encontrado"
    
    success_count = 0
    error_count = 0
    skipped_count = 0
    error_messages = []
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Extrair ZIP para diretório temporário
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Validar e corrigir problemas de compatibilidade com o Streamlit Cloud
        fixes = validate_streamlit_cloud_compatibility(temp_dir)
        fixes_messages = []
        if fixes:
            print("As seguintes correções foram aplicadas para garantir compatibilidade com o Streamlit Cloud:")
            for fix in fixes:
                print(f"- {fix}")
                fixes_messages.append(fix)
            print()
        
        # Upload dos arquivos
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                repo_path = os.path.relpath(file_path, temp_dir)
                
                with open(file_path, "rb") as f:
                    file_content = f.read()
                
                # Verificar se o arquivo foi modificado, se a opção estiver ativada
                if only_modified and check_repository_exists(token, repo_owner, repo_name):
                    is_modified = verify_file_changed(
                        token, repo_owner, repo_name, repo_path, file_content
                    )
                    
                    if not is_modified:
                        skipped_count += 1
                        continue
                
                success, message = upload_file_to_github(
                    token, repo_owner, repo_name, 
                    repo_path, file_content, 
                    f"Add {repo_path} for Streamlit Cloud deploy"
                )
                
                if success:
                    success_count += 1
                else:
                    error_count += 1
                    error_messages.append(message)
    
    if skipped_count > 0:
        skip_msg = f"{skipped_count} arquivos não modificados foram ignorados. "
    else:
        skip_msg = ""
    
    fixes_info = ""
    if fixes_messages:
        fixes_info = "\n\nCorreções realizadas para compatibilidade com Streamlit Cloud:\n"
        fixes_info += "\n".join([f"- {fix}" for fix in fixes_messages])
    
    if error_count == 0:
        return True, f"{skip_msg}Todos os {success_count} arquivos foram enviados com sucesso para o GitHub{fixes_info}"
    else:
        return success_count > 0, f"{skip_msg}{success_count} arquivos enviados com sucesso, {error_count} erros.\nErros: {', '.join(error_messages[:5])}{fixes_info}"

def deploy_to_github(username=None, token=None, repo_name=None, repo_owner=None, use_saved_credentials=True, only_modified=False):
    """
    Função principal para enviar o pacote para o GitHub
    
    Args:
        username (str, optional): Nome de usuário do GitHub
        token (str, optional): Token de acesso pessoal do GitHub
        repo_name (str, optional): Nome do repositório
        repo_owner (str, optional): Proprietário do repositório
        use_saved_credentials (bool): Se deve usar as credenciais salvas
        only_modified (bool): Se True, verifica e envia apenas arquivos modificados
    
    Returns:
        bool, str: Sucesso e mensagem
    """
    # Verificar se temos os parâmetros necessários
    if use_saved_credentials:
        credentials = load_github_credentials()
        if credentials:
            username = credentials.get("username", username)
            token = credentials.get("token", token)
            repo_name = credentials.get("repo_name", repo_name or "suinocultura-cloud")
            repo_owner = credentials.get("repo_owner", repo_owner or username)
    
    if not username or not token:
        return False, "Credenciais do GitHub não fornecidas"
    
    repo_owner = repo_owner or username
    repo_name = repo_name or f"suinocultura-streamlit-{datetime.datetime.now().strftime('%Y%m%d')}"
    
    # Verificar se o repositório já existe
    repo_exists = check_repository_exists(token, repo_owner, repo_name)
    
    if not repo_exists:
        # Criar novo repositório
        repo_data, message = create_github_repository(
            token, repo_name, 
            "Sistema de Gestão Suinocultura para deploy no Streamlit Cloud"
        )
        
        if not repo_data:
            return False, message
    
    # Preparar o pacote Streamlit Cloud
    data_atual = datetime.datetime.now().strftime("%Y%m%d")
    zip_path = f"suinocultura_cloud_deploy_{data_atual}.zip"
    
    # Verificar se o pacote existe, caso contrário criar
    if not os.path.exists(zip_path):
        from prepare_streamlit_cloud import create_deploy_package
        zip_path = create_deploy_package()
    
    # Enviar arquivos para o GitHub
    success, message = extract_and_upload_to_github(
        zip_path, token, repo_owner, repo_name, only_modified
    )
    
    if success:
        # Salvar as credenciais e detalhes do repositório
        save_github_credentials(username, token, repo_name, repo_owner)
        
        # Gerar link para o Streamlit Cloud
        streamlit_url = f"https://streamlit.io/deploy?repository={repo_owner}/{repo_name}&branch=main&mainModule=app.py"
        
        message += f"\n\nDeploye seu aplicativo no Streamlit Cloud: {streamlit_url}"
    
    return success, message

def check_repository_exists(token, owner, repo_name):
    """
    Verifica se um repositório existe no GitHub
    
    Args:
        token (str): Token de acesso pessoal do GitHub
        owner (str): Nome do usuário/organização proprietária do repositório
        repo_name (str): Nome do repositório
    
    Returns:
        bool: True se o repositório existe, False caso contrário
    """
    url = f"https://api.github.com/repos/{owner}/{repo_name}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python github_deploy.py <username> <token> [repo_name] [repo_owner]")
        sys.exit(1)
    
    username = sys.argv[1]
    token = sys.argv[2]
    repo_name = sys.argv[3] if len(sys.argv) > 3 else None
    repo_owner = sys.argv[4] if len(sys.argv) > 4 else None
    
    success, message = deploy_to_github(username, token, repo_name, repo_owner, False)
    print(message)
    sys.exit(0 if success else 1)