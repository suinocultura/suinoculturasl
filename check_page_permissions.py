import os
import sys
import json
import streamlit as st
import importlib.util

def load_page_permissions():
    """
    Carrega as permissões configuradas para cada página
    
    Returns:
        dict: Dicionário com as permissões para cada página
    """
    page_permissions_file = ".streamlit/page_config/page_permissions.json"
    
    if os.path.exists(page_permissions_file):
        try:
            with open(page_permissions_file, "r") as f:
                return json.load(f)
        except:
            return {}
    else:
        return {}

def check_page_permission():
    """
    Verifica se o usuário autenticado tem permissão para acessar a página atual
    
    Returns:
        bool: True se o usuário tem permissão, False caso contrário
    """
    # Se não estiver autenticado, não tem permissão
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        return False
    
    # Importar a função de verificação de permissões
    sys_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if sys_path not in sys.path:
        sys.path.append(sys_path)
    
    try:
        from utils import check_permission
    except ImportError:
        # Se não conseguir importar a função, não pode verificar as permissões
        return False
    
    # Obter o nome do arquivo da página atual
    script_path = __file__
    page_filename = os.path.basename(script_path)
    
    # Carregar as permissões das páginas
    page_permissions = load_page_permissions()
    
    # Obter as permissões necessárias para esta página
    required_permissions = page_permissions.get(page_filename, [])
    
    # Se não houver permissões necessárias, todos os usuários autenticados podem acessar
    if not required_permissions:
        return True
    
    # Verificar se o usuário tem pelo menos uma das permissões necessárias
    user = st.session_state.current_user
    for permission in required_permissions:
        if check_permission(user, permission):
            return True
    
    # Se chegou aqui, o usuário não tem nenhuma das permissões necessárias
    return False