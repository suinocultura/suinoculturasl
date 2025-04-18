#!/usr/bin/env python3
"""
Ferramenta para verificar e otimizar a compatibilidade das páginas com o Streamlit Cloud
Este script identifica e corrige problemas comuns que podem causar falhas no Streamlit Cloud
"""

import os
import re
import sys
import shutil
from collections import defaultdict

def list_streamlit_pages(directory="pages"):
    """
    Lista todas as páginas Streamlit em um diretório
    
    Args:
        directory (str): Diretório para buscar as páginas
        
    Returns:
        list: Lista de arquivos Python encontrados
    """
    if not os.path.exists(directory):
        print(f"Diretório {directory} não encontrado")
        return []
        
    files = [f for f in os.listdir(directory) if f.endswith(".py")]
    return files

def detect_prefix_conflicts(pages):
    """
    Detecta conflitos de prefixo nas páginas
    
    Args:
        pages (list): Lista de nomes de arquivos
        
    Returns:
        dict: Dicionário com prefixos e páginas conflitantes
    """
    prefix_map = defaultdict(list)
    
    for page in pages:
        # Extrai o prefixo numérico (ex: 01_, 02_, etc)
        prefix_match = re.match(r"^(\d+)[_\-]", page)
        if prefix_match:
            prefix = prefix_match.group(1)
            prefix_map[prefix].append(page)
    
    # Filtrar para manter apenas prefixos com múltiplas páginas
    conflicts = {k: v for k, v in prefix_map.items() if len(v) > 1}
    return conflicts

def detect_name_similarity_conflicts(pages):
    """
    Detecta conflitos de similaridade de nomes (caso insensitivo) nas páginas
    
    Args:
        pages (list): Lista de nomes de arquivos
        
    Returns:
        list: Lista de grupos de páginas com nomes similares
    """
    # Extrair nomes das páginas (descartando o prefixo numérico e a extensão)
    name_map = defaultdict(list)
    emoji_map = defaultdict(list)
    
    for page in pages:
        # Remove prefixo numérico e extensão
        name = re.sub(r"^\d+[_\-]", "", page)
        name = os.path.splitext(name)[0]
        
        # Armazena a versão original (apenas sem prefixo e extensão) para verificação de emojis
        original_name = name
        
        # Verifica se contém emojis ou caracteres especiais Unicode
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # símbolos e pictogramas
            "\U0001F680-\U0001F6FF"  # transporte e símbolos de mapas
            "\U0001F700-\U0001F77F"  # alchemical symbols
            "\U0001F780-\U0001F7FF"  # Geometric Shapes
            "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA00-\U0001FA6F"  # Chess Symbols
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "\u2702-\u27B0"          # Dingbats
            "\u24C2-\u2BEF"          # Miscellaneous Symbols
            "]+", flags=re.UNICODE
        )
        
        # Detectar páginas que contêm emojis para verificação especial
        if emoji_pattern.search(original_name):
            # Extrair apenas o primeiro emoji
            emoji_match = emoji_pattern.search(original_name)
            if emoji_match:
                first_emoji = emoji_match.group(0)
                emoji_map[first_emoji].append(page)
        
        # Remove emojis e caracteres especiais (mais agressivamente)
        name = re.sub(r"[^\w\s]", "", name)
        
        # Remove underscores, hífens e espaços
        name = re.sub(r"[_\-\s]", "", name)
        
        # Converte para lowercase
        name = name.lower()
        
        name_map[name].append(page)
    
    # Filtrar para manter apenas nomes com múltiplas páginas
    conflicts = {k: v for k, v in name_map.items() if len(v) > 1}
    
    # Adicionar conflitos de emojis
    emoji_conflicts = {k: v for k, v in emoji_map.items() if len(v) > 1}
    for emoji, pages_with_emoji in emoji_conflicts.items():
        # Criar uma chave única para este grupo de conflitos de emoji
        key = f"emoji_{emoji}"
        conflicts[key] = pages_with_emoji
    
    return conflicts

def detect_backup_files(pages):
    """
    Detecta arquivos de backup no diretório de páginas
    
    Args:
        pages (list): Lista de nomes de arquivos
        
    Returns:
        list: Lista de arquivos de backup encontrados
    """
    backup_patterns = [
        r"\.bak$",
        r"\.backup$", 
        r"_backup\.py$",
        r"-backup\.py$",
        r"_old\.py$",
        r"-old\.py$",
        r"~$",
        r"_copy\.py$",
        r"-copy\.py$",
        r"_\d+\.py$",  # Arquivos com sufixo numérico (ex: arquivo_1.py)
        r"-\d+\.py$",  # Arquivos com sufixo numérico com hífen
        r"\(\d+\)\.py$",  # Arquivos com sufixo numérico entre parênteses
        r"_temp\.py$",
        r"-temp\.py$",
        r"_draft\.py$",
        r"-draft\.py$",
        r"_novo\.py$",
        r"_new\.py$",
        r"_bak_.*\.py$",  # Qualquer arquivo com _bak_ no nome
        r"_bak\.py$",     # Arquivos terminando com _bak.py
        r"\.py\.bak$",    # Arquivos terminando com .py.bak
        r"\.py~$",        # Arquivos terminando com .py~
        r"#.*#\.py$"      # Arquivos com # no nome (comuns em editores como Emacs)
    ]
    
    # Identificar arquivos com padrões explícitos de backup
    explicit_backup_patterns = [
        re.compile(r'^\d+_bak[_\-].*\.py$'),  # 98_bak_Nome.py
        re.compile(r'.*_bak_\d+\.py$'),       # Nome_bak_123.py
        re.compile(r'.*\.py\.swp$'),          # Arquivo.py.swp (Vim swap)
        re.compile(r'.*\.py\.swo$'),          # Arquivo.py.swo (Vim swap)
        re.compile(r'\.#.*\.py$'),            # .#Arquivo.py (Emacs temp)
        re.compile(r'.*_bkp.*\.py$')          # Qualquer coisa com _bkp
    ]
    
    # Identificar arquivos com nomes duplicados (diff apenas por case ou caracteres especiais)
    lowercase_map = {}
    duplicates_by_case = []
    
    for page in pages:
        # Criar uma versão normalizada do nome (lowercase, sem especiais)
        normalized = page.lower()
        normalized = re.sub(r'[^\w\.]', '', normalized)
        
        if normalized in lowercase_map:
            # Já existe um arquivo com este mesmo nome normalizado
            original = lowercase_map[normalized]
            # Se não são idênticos, um deles é potencialmente um backup
            if original != page and page not in duplicates_by_case:
                duplicates_by_case.append(page)
        else:
            lowercase_map[normalized] = page
    
    backups = []
    for page in pages:
        # Verificar padrões comuns
        for pattern in backup_patterns:
            if re.search(pattern, page):
                backups.append(page)
                break
        
        # Se ainda não foi adicionado, verificar padrões explícitos
        if page not in backups:
            for pattern in explicit_backup_patterns:
                if pattern.match(page):
                    backups.append(page)
                    break
        
        # Verificar se é uma duplicata por case
        if page not in backups and page in duplicates_by_case:
            backups.append(page)
    
    return backups

def suggest_filename_fixes(conflicts, conflict_type="prefix"):
    """
    Sugere correções para nomes de arquivos conflitantes
    
    Args:
        conflicts (dict): Dicionário de conflitos
        conflict_type (str): Tipo de conflito ("prefix" ou "name")
        
    Returns:
        dict: Dicionário com sugestões de renomeação
    """
    rename_suggestions = {}
    
    if conflict_type == "prefix":
        for prefix, files in conflicts.items():
            # Manter o primeiro arquivo com este prefixo
            keep_original = files[0]
            
            # Sugerir novos nomes para os outros
            for i, file in enumerate(files[1:], 1):
                new_prefix = f"{prefix}{chr(96+i)}"  # 96+1=a, 96+2=b, etc.
                new_name = re.sub(r"^\d+", new_prefix, file)
                rename_suggestions[file] = new_name
    
    elif conflict_type == "name":
        for name, files in conflicts.items():
            # Manter o primeiro arquivo com este nome
            keep_original = files[0]
            
            # Sugerir variações de nomes para os outros
            for i, file in enumerate(files[1:], 1):
                file_prefix = re.match(r"^(\d+[_\-])", file)
                file_name = re.sub(r"^\d+[_\-]", "", file)
                file_ext = os.path.splitext(file_name)[1]
                file_name_no_ext = os.path.splitext(file_name)[0]
                
                # Adicionar um sufixo numérico
                new_name = f"{file_name_no_ext}_{i}{file_ext}"
                if file_prefix:
                    new_name = f"{file_prefix.group(1)}{new_name}"
                
                rename_suggestions[file] = new_name
    
    return rename_suggestions

def suggest_backup_fixes(backups):
    """
    Sugere ações para arquivos de backup
    
    Args:
        backups (list): Lista de arquivos de backup
        
    Returns:
        dict: Dicionário com sugestões para cada arquivo
    """
    suggestions = {}
    
    for backup in backups:
        if backup.endswith(".py"):
            # Sugerir mover para um diretório de backups
            suggestions[backup] = f"Mover para pages_backup/{backup}"
        else:
            # Sugerir remoção para arquivos não Python
            suggestions[backup] = f"Remover {backup}"
    
    return suggestions

def fix_conflicts(directory="pages", apply_fixes=False, move_conflicts=False):
    """
    Identifica e opcionalmente corrige conflitos nas páginas
    
    Args:
        directory (str): Diretório das páginas
        apply_fixes (bool): Se True, aplica as correções sugeridas
        move_conflicts (bool): Se True, move arquivos conflitantes para o diretório de backup em vez de renomeá-los
        
    Returns:
        dict: Resumo das ações realizadas
    """
    pages = list_streamlit_pages(directory)
    if not pages:
        return {"status": "error", "message": "Nenhuma página encontrada"}
    
    # Criar diretório de backup se não existir
    backup_dir = "pages_backup"
    if (apply_fixes or move_conflicts) and not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Verificar conflitos
    prefix_conflicts = detect_prefix_conflicts(pages)
    name_conflicts = detect_name_similarity_conflicts(pages)
    backup_files = detect_backup_files(pages)
    
    # Gerar sugestões
    prefix_fixes = suggest_filename_fixes(prefix_conflicts, "prefix")
    name_fixes = suggest_filename_fixes(name_conflicts, "name")
    backup_fixes = suggest_backup_fixes(backup_files)
    
    actions_taken = {
        "prefix_conflicts": {},
        "name_conflicts": {},
        "backup_files": {}
    }
    
    # Aplicar correções, se solicitado
    if apply_fixes:
        # Corrigir conflitos de prefixo
        for old_name, new_name in prefix_fixes.items():
            old_path = os.path.join(directory, old_name)
            
            if move_conflicts:
                # Mover para diretório de backup se solicitado
                new_path = os.path.join(backup_dir, old_name)
                try:
                    shutil.move(old_path, new_path)
                    actions_taken["prefix_conflicts"][old_name] = f"Movido para {backup_dir}/{old_name}"
                    print(f"Movido: {old_name} -> {backup_dir}/{old_name}")
                except Exception as e:
                    actions_taken["prefix_conflicts"][old_name] = f"Erro ao mover: {str(e)}"
                    print(f"Erro ao mover {old_name}: {str(e)}")
            else:
                # Caso contrário, renomear no mesmo diretório
                new_path = os.path.join(directory, new_name)
                try:
                    shutil.move(old_path, new_path)
                    actions_taken["prefix_conflicts"][old_name] = f"Renomeado para {new_name}"
                    print(f"Renomeado: {old_name} -> {new_name}")
                except Exception as e:
                    actions_taken["prefix_conflicts"][old_name] = f"Erro ao renomear: {str(e)}"
                    print(f"Erro ao renomear {old_name}: {str(e)}")
        
        # Corrigir conflitos de nomes similares
        for old_name, new_name in name_fixes.items():
            old_path = os.path.join(directory, old_name)
            
            if move_conflicts:
                # Mover para diretório de backup se solicitado
                new_path = os.path.join(backup_dir, old_name)
                try:
                    shutil.move(old_path, new_path)
                    actions_taken["name_conflicts"][old_name] = f"Movido para {backup_dir}/{old_name}"
                    print(f"Movido: {old_name} -> {backup_dir}/{old_name}")
                except Exception as e:
                    actions_taken["name_conflicts"][old_name] = f"Erro ao mover: {str(e)}"
                    print(f"Erro ao mover {old_name}: {str(e)}")
            else:
                # Caso contrário, renomear no mesmo diretório
                new_path = os.path.join(directory, new_name)
                try:
                    shutil.move(old_path, new_path)
                    actions_taken["name_conflicts"][old_name] = f"Renomeado para {new_name}"
                    print(f"Renomeado: {old_name} -> {new_name}")
                except Exception as e:
                    actions_taken["name_conflicts"][old_name] = f"Erro ao renomear: {str(e)}"
                    print(f"Erro ao renomear {old_name}: {str(e)}")
        
        # Tratar arquivos de backup
        for backup_file in backup_files:
            old_path = os.path.join(directory, backup_file)
            
            if backup_file.endswith(".py"):
                # Mover arquivos Python para o diretório de backup
                new_path = os.path.join(backup_dir, backup_file)
                try:
                    shutil.move(old_path, new_path)
                    actions_taken["backup_files"][backup_file] = f"Movido para {backup_dir}/{backup_file}"
                    print(f"Movido: {backup_file} -> {backup_dir}/{backup_file}")
                except Exception as e:
                    actions_taken["backup_files"][backup_file] = f"Erro ao mover: {str(e)}"
                    print(f"Erro ao mover {backup_file}: {str(e)}")
            else:
                # Remover arquivos não Python
                try:
                    os.remove(old_path)
                    actions_taken["backup_files"][backup_file] = "Removido"
                    print(f"Removido: {backup_file}")
                except Exception as e:
                    actions_taken["backup_files"][backup_file] = f"Erro ao remover: {str(e)}"
                    print(f"Erro ao remover {backup_file}: {str(e)}")
    else:
        # Apenas reportar as sugestões
        actions_taken["prefix_conflicts"] = prefix_fixes
        actions_taken["name_conflicts"] = name_fixes
        actions_taken["backup_files"] = backup_fixes
    
    # Resumo
    total_issues = len(prefix_fixes) + len(name_fixes) + len(backup_fixes)
    summary = {
        "status": "success",
        "total_issues": total_issues,
        "prefix_conflicts": len(prefix_fixes),
        "name_conflicts": len(name_fixes),
        "backup_files": len(backup_fixes),
        "actions": actions_taken
    }
    
    return summary

def print_summary(summary):
    """
    Imprime um resumo formatado das verificações
    
    Args:
        summary (dict): Resumo das verificações
    """
    print("\n===== RESUMO DE VERIFICAÇÃO DE PÁGINAS =====\n")
    
    if summary["status"] == "error":
        print(f"ERRO: {summary['message']}")
        return
    
    print(f"Total de problemas encontrados: {summary['total_issues']}")
    print(f"Conflitos de prefixo: {summary['prefix_conflicts']}")
    print(f"Conflitos de nomes similares: {summary['name_conflicts']}")
    print(f"Arquivos de backup: {summary['backup_files']}")
    
    print("\n--- DETALHES ---\n")
    
    if summary["prefix_conflicts"] > 0:
        print("Conflitos de prefixo:")
        for old_name, action in summary["actions"]["prefix_conflicts"].items():
            print(f"  - {old_name}: {action}")
        print("")
    
    if summary["name_conflicts"] > 0:
        print("Conflitos de nomes similares:")
        for old_name, action in summary["actions"]["name_conflicts"].items():
            print(f"  - {old_name}: {action}")
        print("")
    
    if summary["backup_files"] > 0:
        print("Arquivos de backup:")
        for backup_file, action in summary["actions"]["backup_files"].items():
            print(f"  - {backup_file}: {action}")
        print("")

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Verificar e corrigir problemas de compatibilidade nas páginas Streamlit")
    parser.add_argument("--directory", "-d", default="pages", help="Diretório contendo as páginas Streamlit")
    parser.add_argument("--fix", "-f", action="store_true", help="Aplicar correções sugeridas")
    parser.add_argument("--move-conflicts", "-m", action="store_true", help="Mover arquivos conflitantes para diretório de backup em vez de renomeá-los")
    parser.add_argument("--quiet", "-q", action="store_true", help="Modo silencioso (apenas erros)")
    
    args = parser.parse_args()
    
    # Executar verificação
    summary = fix_conflicts(directory=args.directory, apply_fixes=args.fix, move_conflicts=args.move_conflicts)
    
    # Imprimir resumo
    if not args.quiet:
        print_summary(summary)
    
    return 0 if summary["status"] == "success" else 1

if __name__ == "__main__":
    sys.exit(main())