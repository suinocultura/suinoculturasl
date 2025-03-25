import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import uuid

# File paths for different data
ANIMALS_FILE = "data/animals.csv"
BREEDING_FILE = "data/breeding_cycles.csv"
GESTATION_FILE = "data/gestation.csv"
WEIGHT_FILE = "data/weight.csv"
INSEMINATION_FILE = "data/inseminacao.csv"
PENS_FILE = "data/baias.csv"
PENS_ALLOCATION_FILE = "data/baias_alocacao.csv"
MATERNITY_FILE = "data/maternidade.csv"
LITTERS_FILE = "data/leitegadas.csv"
PIGLETS_FILE = "data/leitoes.csv"
WEANING_FILE = "data/desmame.csv"
NURSERY_FILE = "data/creche.csv"
NURSERY_BATCHES_FILE = "data/lotes_creche.csv"
NURSERY_MOVEMENTS_FILE = "data/movimentacoes_creche.csv"
GILTS_FILE = "data/leitoas.csv"
GILTS_SELECTION_FILE = "data/selecao_leitoas.csv"
GILTS_DISCARD_FILE = "data/descarte_leitoas.csv"

# Adding new file paths after existing paths
VACCINES_FILE = "data/vaccines.csv"
VACCINATION_PROTOCOLS_FILE = "data/vaccination_protocols.csv"
VACCINATION_RECORDS_FILE = "data/vaccination_records.csv"

# Add after the existing file paths
HEAT_DETECTION_FILE = "data/heat_detection.csv"
HEAT_RECORDS_FILE = "data/heat_records.csv"

# Arquivos para sistema de recria
RECRIA_FILE = "data/recria.csv"
RECRIA_LOTES_FILE = "data/recria_lotes.csv"
RECRIA_PESAGENS_FILE = "data/recria_pesagens.csv"
RECRIA_TRANSFERENCIAS_FILE = "data/recria_transferencias.csv"
RECRIA_ALIMENTACAO_FILE = "data/recria_alimentacao.csv"
RECRIA_MEDICACAO_FILE = "data/recria_medicacao.csv"

# Calendário suíno de 1000 dias
def date_to_pig_calendar(date):
    """
    Converte uma data para o número do calendário suíno de 1000 dias
    O calendário suíno vai de 1 a 1000, sendo que 1 geralmente representa o primeiro dia do primeiro ano do ciclo
    """
    if isinstance(date, str):
        date = pd.to_datetime(date).date()
    
    # Dia 1 do calendário suíno é 1º de janeiro de 2020 (definido como referência)
    reference_date = datetime(2020, 1, 1).date()
    days_diff = (date - reference_date).days
    
    # Calcula o dia do calendário (de 1 a 1000) com referência cíclica
    pig_day = (days_diff % 1000) + 1
    
    return pig_day

def pig_calendar_to_date(pig_day, reference_year=None):
    """
    Converte um número do calendário suíno (1-1000) para uma data
    Se o ano de referência não for fornecido, usa o ano atual
    """
    # Verifica se o pig_day está no intervalo válido
    if not (1 <= pig_day <= 1000):
        raise ValueError("O dia do calendário suíno deve estar entre 1 e 1000")
    
    # Usa o ano atual se não for fornecido um ano de referência
    if reference_year is None:
        reference_year = datetime.now().year
    
    # Dia 1 do calendário é 1º de janeiro do ano de referência
    reference_date = datetime(reference_year, 1, 1).date()
    
    # Ajusta para o dia correto no calendário suíno
    target_date = reference_date + timedelta(days=pig_day - 1)
    
    return target_date

def load_animals():
    """Load animals data from CSV or create empty DataFrame if file doesn't exist"""
    if os.path.exists(ANIMALS_FILE):
        return pd.read_csv(ANIMALS_FILE)
    else:
        return pd.DataFrame({
            'id_animal': [],
            'identificacao': [], 
            'brinco': [],
            'tatuagem': [],
            'nome': [],
            'categoria': [],
            'data_nascimento': [],
            'sexo': [],
            'raca': [],
            'origem': [],
            'data_cadastro': []
        })

def save_animals(df):
    """Save animals data to CSV"""
    df.to_csv(ANIMALS_FILE, index=False)

def load_breeding_cycles():
    """Load breeding cycles data from CSV or create empty DataFrame if file doesn't exist"""
    if os.path.exists(BREEDING_FILE):
        return pd.read_csv(BREEDING_FILE)
    else:
        return pd.DataFrame({
            'id_ciclo': [],
            'id_animal': [],
            'numero_ciclo': [],
            'data_cio': [],
            'intensidade_cio': [],
            'irmas_cio': [],
            'quantidade_irmas_cio': [],
            'status': [],
            'observacao': []
        })

def save_breeding_cycles(df):
    """Save breeding cycles data to CSV"""
    df.to_csv(BREEDING_FILE, index=False)

def load_gestation():
    """Load gestation data from CSV or create empty DataFrame if file doesn't exist"""
    if os.path.exists(GESTATION_FILE):
        return pd.read_csv(GESTATION_FILE)
    else:
        return pd.DataFrame({
            'id_gestacao': [],
            'id_animal': [],
            'data_cobertura': [],
            'data_prevista_parto': [],
            'data_parto': [],
            'quantidade_leitoes': [],
            'status': [],
            'observacao': []
        })

def save_gestation(df):
    """Save gestation data to CSV"""
    df.to_csv(GESTATION_FILE, index=False)

def load_weight_records():
    """Load weight records data from CSV or create empty DataFrame if file doesn't exist"""
    if os.path.exists(WEIGHT_FILE):
        return pd.read_csv(WEIGHT_FILE)
    else:
        return pd.DataFrame({
            'id_registro': [],
            'id_animal': [],
            'data_registro': [],
            'peso': [],
            'observacao': []
        })

def save_weight_records(df):
    """Save weight records data to CSV"""
    df.to_csv(WEIGHT_FILE, index=False)

def calculate_statistics(animals_df, breeding_df, gestation_df, weight_df):
    """Calculate various statistics for dashboard"""
    stats = {}
    
    # Total animals
    stats['total_animals'] = len(animals_df) if not animals_df.empty else 0
    
    # Animals by category
    if not animals_df.empty:
        stats['animals_by_category'] = animals_df['categoria'].value_counts().to_dict()
    else:
        stats['animals_by_category'] = {}
    
    # Animals in gestation
    if not gestation_df.empty:
        stats['pregnant_animals'] = len(gestation_df[gestation_df['data_parto'].isna()])
    else:
        stats['pregnant_animals'] = 0
        
    # Animals in heat or near heat cycle
    if not breeding_df.empty:
        today = datetime.now().date()
        breeding_df['data_cio'] = pd.to_datetime(breeding_df['data_cio']).dt.date
        breeding_df['next_heat'] = breeding_df['data_cio'] + pd.to_timedelta([21]*len(breeding_df), unit='d')
        stats['animals_in_heat'] = len(breeding_df[
            (breeding_df['next_heat'] >= today) & 
            (breeding_df['next_heat'] <= today + timedelta(days=3))
        ])
    else:
        stats['animals_in_heat'] = 0
        
    # Weight statistics
    if not weight_df.empty:
        stats['avg_weight'] = weight_df['peso'].mean()
        stats['min_weight'] = weight_df['peso'].min()
        stats['max_weight'] = weight_df['peso'].max()
    else:
        stats['avg_weight'] = 0
        stats['min_weight'] = 0
        stats['max_weight'] = 0
        
    return stats

def calculate_age(birth_date):
    """Calculate age in days from birth date"""
    birth_date = pd.to_datetime(birth_date).date()
    today = datetime.now().date()
    return (today - birth_date).days

def get_animal_details(animal_id, animals_df):
    """Get details for a specific animal"""
    if animal_id in animals_df['id_animal'].values:
        return animals_df[animals_df['id_animal'] == animal_id].iloc[0]
    return None

def predict_heat_date(last_heat_date):
    """Predict next heat date based on typical 21-day cycle"""
    last_heat_date = pd.to_datetime(last_heat_date).date()
    return last_heat_date + timedelta(days=21)

def calculate_gestation_details(gestation_date):
    """Calculate expected delivery date and current gestation stage"""
    gestation_date = pd.to_datetime(gestation_date).date()
    today = datetime.now().date()
    
    # Typical gestation period for pigs is 114 days
    expected_delivery = gestation_date + timedelta(days=114)
    
    # Calculate current day of gestation
    current_day = (today - gestation_date).days
    
    # Calculate percentage complete
    if current_day <= 0:
        percentage = 0
    elif current_day >= 114:
        percentage = 100
    else:
        percentage = (current_day / 114) * 100
        
    return {
        'expected_delivery': expected_delivery,
        'current_day': current_day,
        'percentage': percentage
    }

def load_insemination():
    """Load insemination data from CSV or create empty DataFrame if file doesn't exist"""
    if os.path.exists(INSEMINATION_FILE):
        return pd.read_csv(INSEMINATION_FILE)
    else:
        return pd.DataFrame({
            'id_inseminacao': [],
            'id_animal': [],
            'brinco': [],
            'categoria': [],
            'tipo_marran': [],
            'data_inseminacao': [],
            'num_semen': [],
            'linhagem_semen': [],
            'idade_semen': [],
            'dose': [],
            'ordem_dose': [],
            'metodo': [],
            'tecnico': [],
            'semana_suina': [],
            'data_registro': [],
            'observacao': []
        })

def save_insemination(df):
    """Save insemination data to CSV"""
    df.to_csv(INSEMINATION_FILE, index=False)

def export_data(dataframe, format_type):
    """Export dataframe to various formats"""
    if format_type == 'csv':
        return dataframe.to_csv(index=False)
    elif format_type == 'excel':
        # Return as CSV since we can't generate binary Excel files
        return dataframe.to_csv(index=False)
    elif format_type == 'json':
        return dataframe.to_json(orient='records')
    else:
        return dataframe.to_csv(index=False)

def load_pens():
    """Load pens data from CSV or create empty DataFrame if file doesn't exist"""
    if os.path.exists(PENS_FILE):
        return pd.read_csv(PENS_FILE)
    else:
        return pd.DataFrame({
            'id_baia': [],
            'identificacao': [],
            'setor': [],
            'capacidade': [],
            'largura': [],
            'comprimento': [],
            'area': [],
            'tipo_piso': [],
            'data_cadastro': [],
            'observacao': []
        })

def save_pens(df):
    """Save pens data to CSV"""
    df.to_csv(PENS_FILE, index=False)

def load_pen_allocations():
    """Load pen allocation data from CSV or create empty DataFrame if file doesn't exist"""
    if os.path.exists(PENS_ALLOCATION_FILE):
        return pd.read_csv(PENS_ALLOCATION_FILE)
    else:
        return pd.DataFrame({
            'id_alocacao': [],
            'id_baia': [],
            'id_animal': [],
            'data_entrada': [],
            'data_saida': [],
            'motivo_saida': [],
            'status': [],
            'observacao': []
        })

def save_pen_allocations(df):
    """Save pen allocation data to CSV"""
    df.to_csv(PENS_ALLOCATION_FILE, index=False)

def get_pen_occupancy(pen_id, allocations_df):
    """Get current occupancy for a specific pen"""
    if allocations_df.empty:
        return 0
    
    # Filter for the specific pen and active allocations (no exit date)
    current_occupants = allocations_df[(allocations_df['id_baia'] == pen_id) & 
                                       (allocations_df['data_saida'].isna())]
    
    return len(current_occupants)

def get_available_pens(pens_df, allocations_df, animal_category=None):
    """Get list of available pens with capacity information"""
    if pens_df.empty:
        return pd.DataFrame()
    
    pens_with_occupancy = pens_df.copy()
    pens_with_occupancy['ocupacao_atual'] = pens_with_occupancy['id_baia'].apply(
        lambda x: get_pen_occupancy(x, allocations_df)
    )
    
    pens_with_occupancy['vagas_disponiveis'] = pens_with_occupancy['capacidade'] - pens_with_occupancy['ocupacao_atual']
    
    # Filter by sector if animal category is provided
    if animal_category:
        # Map animal categories to appropriate sectors
        category_sector_map = {
            'Leitão': 'Creche',
            'Matriz': 'Gestação',
            'Reprodutor': 'Reprodução',
            'Matriz Lactante': 'Maternidade'
            # Add more mappings as needed
        }
        
        if animal_category in category_sector_map:
            recommended_sector = category_sector_map[animal_category]
            pens_with_occupancy = pens_with_occupancy[pens_with_occupancy['setor'] == recommended_sector]
    
    # Return only pens with available space
    return pens_with_occupancy[pens_with_occupancy['vagas_disponiveis'] > 0]

# Funções para o sistema de maternidade
def load_maternity():
    """Load maternity data from CSV or create empty DataFrame if file doesn't exist"""
    if os.path.exists(MATERNITY_FILE):
        return pd.read_csv(MATERNITY_FILE)
    else:
        return pd.DataFrame({
            'id_maternidade': [],
            'id_animal': [],        # ID da matriz
            'id_baia': [],          # ID da baia de maternidade
            'data_entrada': [],     # Data de entrada na maternidade
            'data_parto': [],       # Data do parto
            'data_saida': [],       # Data de saída da maternidade
            'status': [],           # Status (Ativa, Finalizada)
            'observacao': []
        })

def save_maternity(df):
    """Save maternity data to CSV"""
    df.to_csv(MATERNITY_FILE, index=False)

def load_litters():
    """Load litters data from CSV or create empty DataFrame if file doesn't exist"""
    if os.path.exists(LITTERS_FILE):
        return pd.read_csv(LITTERS_FILE)
    else:
        return pd.DataFrame({
            'id_leitegada': [],
            'id_maternidade': [],     # Referência à entrada na maternidade
            'id_animal': [],          # ID da matriz
            'data_parto': [],
            'total_nascidos': [],     # Total de leitões nascidos
            'nascidos_vivos': [],     # Leitões nascidos vivos
            'natimortos': [],         # Leitões nascidos mortos
            'mumificados': [],        # Leitões mumificados
            'peso_total': [],         # Peso total da leitegada (kg)
            'peso_medio': [],         # Peso médio dos leitões (kg)
            'tamanho_leitegada_ajustado': [], # Tamanho após transferências/adoções
            'observacao': []
        })

def save_litters(df):
    """Save litters data to CSV"""
    df.to_csv(LITTERS_FILE, index=False)

def load_piglets():
    """Load piglets data from CSV or create empty DataFrame if file doesn't exist"""
    if os.path.exists(PIGLETS_FILE):
        return pd.read_csv(PIGLETS_FILE)
    else:
        return pd.DataFrame({
            'id_leitao': [],
            'id_leitegada': [],        # Referência à leitegada
            'id_animal_mae': [],       # ID da matriz biológica
            'id_animal_adotiva': [],   # ID da matriz adotiva (se houver)
            'identificacao': [],       # Identificação do leitão (número, brinco, etc.)
            'sexo': [],                # Sexo do leitão
            'data_nascimento': [],     # Data de nascimento
            'peso_nascimento': [],     # Peso ao nascer (kg)
            'status_atual': [],        # Status (Vivo, Morto, Desmamado, Transferido)
            'data_status': [],         # Data do último status
            'causa_morte': [],         # Causa da morte (se aplicável)
            'observacao': []
        })

def save_piglets(df):
    """Save piglets data to CSV"""
    df.to_csv(PIGLETS_FILE, index=False)

def load_weaning():
    """Load weaning data from CSV or create empty DataFrame if file doesn't exist"""
    if os.path.exists(WEANING_FILE):
        return pd.read_csv(WEANING_FILE)
    else:
        return pd.DataFrame({
            'id_desmame': [],
            'id_leitegada': [],        # Referência à leitegada
            'id_animal_mae': [],       # ID da matriz
            'data_desmame': [],        # Data do desmame
            'idade_desmame': [],       # Idade média ao desmame (dias)
            'total_desmamados': [],    # Total de leitões desmamados
            'peso_total_desmame': [],  # Peso total dos leitões ao desmame (kg)
            'peso_medio_desmame': [],  # Peso médio dos leitões ao desmame (kg)
            'ganho_medio_diario': [],  # Ganho médio diário de peso (g/dia)
            'destino_leitoes': [],     # Destino dos leitões (Creche, Venda, etc.)
            'destino_matriz': [],      # Destino da matriz (Gestação, Descarte, etc.)
            'id_baia_destino': [],     # ID da baia de destino dos leitões
            'observacao': []
        })

def save_weaning(df):
    """Save weaning data to CSV"""
    df.to_csv(WEANING_FILE, index=False)

def calculate_weaning_metrics(litter_id, piglets_df):
    """Calculate metrics for weaning based on piglet data"""
    if piglets_df.empty or litter_id not in piglets_df['id_leitegada'].values:
        return {
            'total_desmamados': 0,
            'peso_total_desmame': 0,
            'peso_medio_desmame': 0,
            'ganho_medio_diario': 0
        }
    
    # Filtrar leitões da leitegada selecionada que estão vivos
    litter_piglets = piglets_df[(piglets_df['id_leitegada'] == litter_id) & 
                                (piglets_df['status_atual'] == 'Vivo')]
    
    total_piglets = len(litter_piglets)
    
    # Se não houver dados de peso, retorna zeros
    if 'peso_atual' not in litter_piglets.columns or litter_piglets['peso_atual'].isna().all():
        return {
            'total_desmamados': total_piglets,
            'peso_total_desmame': 0,
            'peso_medio_desmame': 0,
            'ganho_medio_diario': 0
        }
    
    # Calcular métricas com os dados disponíveis
    peso_total = litter_piglets['peso_atual'].sum()
    peso_medio = peso_total / total_piglets if total_piglets > 0 else 0
    
    # Calcular ganho médio diário, se possível
    ganho_medio = 0
    if 'peso_nascimento' in litter_piglets.columns and 'data_nascimento' in litter_piglets.columns:
        # Calcular idade média em dias
        today = datetime.now().date()
        litter_piglets['data_nascimento'] = pd.to_datetime(litter_piglets['data_nascimento']).dt.date
        litter_piglets['idade_dias'] = litter_piglets['data_nascimento'].apply(lambda x: (today - x).days)
        
        # Calcular ganho médio diário (g/dia)
        litter_piglets['ganho_diario'] = (litter_piglets['peso_atual'] - litter_piglets['peso_nascimento']) * 1000 / litter_piglets['idade_dias']
        ganho_medio = litter_piglets['ganho_diario'].mean()
    
    return {
        'total_desmamados': total_piglets,
        'peso_total_desmame': peso_total,
        'peso_medio_desmame': peso_medio,
        'ganho_medio_diario': ganho_medio
    }

def get_active_maternity_sows(maternity_df, animals_df):
    """Get list of sows currently in maternity"""
    if maternity_df.empty:
        return pd.DataFrame()
    
    # Filter for active maternity entries (no exit date)
    active_entries = maternity_df[maternity_df['data_saida'].isna()]
    
    if active_entries.empty or animals_df.empty:
        return pd.DataFrame()
    
    # Get animal details for each active maternity sow
    sow_ids = active_entries['id_animal'].unique()
    sows = animals_df[animals_df['id_animal'].isin(sow_ids)].copy()
    
    # Add maternity information
    sows['id_maternidade'] = sows['id_animal'].apply(
        lambda x: active_entries[active_entries['id_animal'] == x]['id_maternidade'].iloc[0]
    )
    
    return sows

def check_litter_exists(litters_df, maternity_id):
    """Check if a litter already exists for a given maternity entry"""
    if litters_df.empty:
        return False
    
    return maternity_id in litters_df['id_maternidade'].values

# Funções para o sistema de creche
def load_nursery():
    """Load nursery data from CSV or create empty DataFrame if file doesn't exist"""
    if os.path.exists(NURSERY_FILE):
        return pd.read_csv(NURSERY_FILE)
    else:
        return pd.DataFrame({
            'id_creche': [],
            'id_baia': [],           # ID da baia onde os leitões estão
            'data_inicio': [],       # Data de início do período de creche
            'data_fim_prevista': [], # Data prevista para o fim (saída para crescimento/terminação)
            'data_fim_real': [],     # Data real de saída da creche
            'status': [],            # Status (Ativo, Finalizado)
            'observacao': []
        })

def save_nursery(df):
    """Save nursery data to CSV"""
    df.to_csv(NURSERY_FILE, index=False)

def load_nursery_batches():
    """Load nursery batches data from CSV or create empty DataFrame if file doesn't exist"""
    if os.path.exists(NURSERY_BATCHES_FILE):
        return pd.read_csv(NURSERY_BATCHES_FILE)
    else:
        return pd.DataFrame({
            'id_lote': [],
            'id_creche': [],         # Referência ao período de creche
            'id_desmame': [],        # Referência ao desmame que originou o lote (se aplicável)
            'identificacao': [],     # Identificação do lote
            'quantidade_inicial': [], # Quantidade inicial de leitões no lote
            'quantidade_atual': [],  # Quantidade atual de leitões
            'peso_medio_entrada': [], # Peso médio na entrada (kg)
            'idade_media_entrada': [], # Idade média na entrada (dias)
            'peso_medio_atual': [],  # Peso médio atual (kg)
            'mortalidade': [],       # Taxa de mortalidade (%)
            'origem': [],            # Origem dos leitões (Desmame, Transferência, Compra)
            'data_entrada': [],      # Data de entrada na creche
            'data_saida': [],        # Data de saída da creche (se aplicável)
            'destino': [],           # Destino após a creche (Crescimento, Terminação, Venda)
            'status': [],            # Status (Ativo, Finalizado)
            'observacao': []
        })

def save_nursery_batches(df):
    """Save nursery batches data to CSV"""
    df.to_csv(NURSERY_BATCHES_FILE, index=False)

def load_nursery_movements():
    """Load nursery movements data from CSV or create empty DataFrame if file doesn't exist"""
    if os.path.exists(NURSERY_MOVEMENTS_FILE):
        return pd.read_csv(NURSERY_MOVEMENTS_FILE)
    else:
        return pd.DataFrame({
            'id_movimentacao': [],
            'id_lote': [],          # Referência ao lote
            'tipo': [],             # Tipo (Pesagem, Mortalidade, Medicação, Transferência, etc.)
            'data': [],             # Data da movimentação
            'quantidade': [],       # Quantidade de animais afetados
            'peso_total': [],       # Peso total (para pesagens) (kg)
            'peso_medio': [],       # Peso médio (kg)
            'ganho_diario': [],     # Ganho diário desde a última pesagem (g/dia)
            'causa': [],            # Causa (para mortalidade, medicação)
            'destino': [],          # Destino (para transferências)
            'medicamento': [],      # Medicamento (para medicação)
            'dosagem': [],          # Dosagem (para medicação)
            'via_aplicacao': [],    # Via de aplicação (para medicação)
            'responsavel': [],      # Responsável pela movimentação
            'observacao': []
        })

def save_nursery_movements(df):
    """Save nursery movements data to CSV"""
    df.to_csv(NURSERY_MOVEMENTS_FILE, index=False)

def get_active_nursery_batches(nursery_batches_df):
    """Get list of active nursery batches"""
    if nursery_batches_df.empty:
        return pd.DataFrame()
    
    return nursery_batches_df[nursery_batches_df['status'] == 'Ativo']

def calculate_nursery_metrics(batch_id, movements_df):
    """Calculate metrics for a nursery batch based on movement data"""
    if movements_df.empty or batch_id not in movements_df['id_lote'].values:
        return {
            'ultimo_peso_medio': 0,
            'ultimo_ganho_diario': 0,
            'data_ultima_pesagem': None,
            'idade_atual': 0,
            'dias_na_creche': 0
        }
    
    # Filtrar movimentações do lote
    batch_movements = movements_df[movements_df['id_lote'] == batch_id]
    
    # Obter pesagens
    pesagens = batch_movements[batch_movements['tipo'] == 'Pesagem'].sort_values('data')
    
    if pesagens.empty:
        return {
            'ultimo_peso_medio': 0,
            'ultimo_ganho_diario': 0,
            'data_ultima_pesagem': None,
            'idade_atual': 0,
            'dias_na_creche': 0
        }
    
    # Obter última pesagem
    ultima_pesagem = pesagens.iloc[-1]
    
    return {
        'ultimo_peso_medio': ultima_pesagem['peso_medio'],
        'ultimo_ganho_diario': ultima_pesagem['ganho_diario'],
        'data_ultima_pesagem': ultima_pesagem['data'],
        'idade_atual': 0,  # Calculado separadamente
        'dias_na_creche': 0  # Calculado separadamente
    }

def get_batch_details(batch_id, nursery_batches_df, movements_df):
    """Get detailed information about a nursery batch"""
    if nursery_batches_df.empty or batch_id not in nursery_batches_df['id_lote'].values:
        return None
    
    # Obter dados do lote
    batch_data = nursery_batches_df[nursery_batches_df['id_lote'] == batch_id].iloc[0]
    
    # Calcular métricas adicionais
    metrics = calculate_nursery_metrics(batch_id, movements_df)
    
    # Calcular idade atual e dias na creche
    today = datetime.now().date()
    
    # Calcular idade média atual (dias)
    idade_entrada = batch_data['idade_media_entrada']
    data_entrada = pd.to_datetime(batch_data['data_entrada']).date() if not pd.isna(batch_data['data_entrada']) else None
    idade_atual = idade_entrada + (today - data_entrada).days if data_entrada else idade_entrada
    
    # Calcular dias na creche
    dias_na_creche = (today - data_entrada).days if data_entrada else 0
    
    # Combinar dados
    result = batch_data.to_dict()
    result.update(metrics)
    result['idade_atual'] = idade_atual
    result['dias_na_creche'] = dias_na_creche
    
    return result

# Funções para o sistema de seleção de leitoas
def load_gilts():
    """Load gilts data from CSV or create empty DataFrame if file doesn't exist"""
    if os.path.exists(GILTS_FILE):
        return pd.read_csv(GILTS_FILE)
    else:
        return pd.DataFrame({
            'id_leitoa': [],
            'id_animal': [],          # ID do animal no cadastro geral (se aplicável)
            'identificacao': [],      # Identificação da leitoa
            'brinco': [],             # Número do brinco
            'tatuagem': [],           # Tatuagem
            'chip': [],               # Número do chip (se aplicável)
            'data_nascimento': [],    # Data de nascimento
            'origem': [],             # Origem (Própria, Comprada, etc.)
            'genetica': [],           # Linhagem genética
            'mae': [],                # Identificação da mãe
            'pai': [],                # Identificação do pai
            'data_selecao': [],       # Data de seleção para reprodução
            'peso_selecao': [],       # Peso na seleção (kg)
            'idade_selecao': [],      # Idade na seleção (dias)
            'status': [],             # Status (Selecionada, Em Adaptação, Em Reprodução, Descartada)
            'data_primeiro_cio': [],  # Data do primeiro cio observado
            'observacao': []
        })

def save_gilts(df):
    """Save gilts data to CSV"""
    df.to_csv(GILTS_FILE, index=False)

def load_gilts_selection():
    """Load gilts selection data from CSV or create empty DataFrame if file doesn't exist"""
    if os.path.exists(GILTS_SELECTION_FILE):
        return pd.read_csv(GILTS_SELECTION_FILE)
    else:
        return pd.DataFrame({
            'id_selecao': [],
            'id_leitoa': [],                  # ID da leitoa
            'data_selecao': [],               # Data da seleção
            'peso': [],                       # Peso (kg)
            'idade': [],                      # Idade (dias)
            'espessura_toucinho': [],         # Espessura de toucinho (mm)
            'profundidade_lombo': [],         # Profundidade de lombo (mm)
            'comprimento_corporal': [],       # Comprimento corporal (cm)
            'largura_ombros': [],             # Largura dos ombros (cm)
            'largura_quadril': [],            # Largura do quadril (cm)
            'altura_posterior': [],           # Altura posterior (cm)
            'numero_tetos': [],               # Número de tetos funcionais
            'tetos_invertidos': [],           # Número de tetos invertidos
            'qualidade_aprumos': [],          # Qualidade dos aprumos (Excelente, Boa, Regular, Ruim)
            'temperamento': [],               # Temperamento (Dócil, Normal, Agressivo)
            'avaliacao_visual': [],           # Avaliação visual (Excelente, Bom, Regular, Ruim)
            'escore_geral': [],               # Escore geral (1-5)
            'recomendacao': [],               # Recomendação (Selecionada, Descartada)
            'motivo_recomendacao': [],        # Motivo da recomendação
            'tecnico_responsavel': [],        # Técnico responsável pela avaliação
            'observacao': []
        })

def save_gilts_selection(df):
    """Save gilts selection data to CSV"""
    df.to_csv(GILTS_SELECTION_FILE, index=False)

def load_gilts_discard():
    """Load gilts discard data from CSV or create empty DataFrame if file doesn't exist"""
    if os.path.exists(GILTS_DISCARD_FILE):
        return pd.read_csv(GILTS_DISCARD_FILE)
    else:
        return pd.DataFrame({
            'id_descarte': [],
            'id_leitoa': [],              # ID da leitoa
            'data_descarte': [],          # Data do descarte
            'peso_descarte': [],          # Peso no descarte (kg)
            'idade_descarte': [],         # Idade no descarte (dias)
            'motivo_principal': [],       # Motivo principal do descarte
            'motivos_secundarios': [],    # Motivos secundários (separados por vírgula)
            'destino': [],                # Destino (Abate, Venda, Outro)
            'valor_venda': [],            # Valor de venda (se aplicável)
            'tecnico_responsavel': [],    # Técnico responsável pelo descarte
            'observacao': []
        })

def save_gilts_discard(df):
    """Save gilts discard data to CSV"""
    df.to_csv(GILTS_DISCARD_FILE, index=False)

def get_available_gilts(gilts_df):
    """Get list of available gilts (not discarded)"""
    if gilts_df.empty:
        return pd.DataFrame()
    
    return gilts_df[gilts_df['status'] != 'Descartada']

def get_discarded_gilts(gilts_df):
    """Get list of discarded gilts"""
    if gilts_df.empty:
        return pd.DataFrame()
    
    return gilts_df[gilts_df['status'] == 'Descartada']

def load_caliber_scores():
    """Load caliber scores data from CSV or create empty DataFrame if file doesn't exist"""
    file_path = "data/caliber_scores.csv"
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        return pd.DataFrame({
            'id_score': [],
            'id_animal': [],
            'data_medicao': [],
            'medida_p1': [],  # P1 (Primeira vértebra lombar)
            'medida_p2': [],  # P2 (Última costela)
            'medida_p3': [],  # P3 (Última vértebra torácica)
            'score_calculado': [],
            'condicao_corporal': [],
            'tecnico': [],
            'observacao': []
        })

def save_caliber_scores(df):
    """Save caliber scores data to CSV"""
    df.to_csv("data/caliber_scores.csv", index=False)

def calculate_body_condition(p2_value):
    """Calculate body condition score based on P2 measurement (mm)"""
    if p2_value < 10:
        return "Muito Magra (1)", 1
    elif p2_value < 14:
        return "Magra (2)", 2
    elif p2_value >= 14 and p2_value <= 19:
        return "Ideal (3)", 3
    elif p2_value > 19 and p2_value <= 25:
        return "Gorda (4)", 4
    else:
        return "Muito Gorda (5)", 5

def calculate_gilts_statistics(gilts_df, selection_df, discard_df):
    """Calculate statistics for gilts management"""
    stats = {}
    
    # Total gilts
    stats['total_gilts'] = len(gilts_df) if not gilts_df.empty else 0
    
    # Gilts by status
    if not gilts_df.empty:
        stats['gilts_by_status'] = gilts_df['status'].value_counts().to_dict()
    else:
        stats['gilts_by_status'] = {}
    
    # Selection rate
    if not gilts_df.empty and not selection_df.empty and 'recomendacao' in selection_df.columns:
        selected = selection_df[selection_df['recomendacao'] == 'Selecionada']
        total_evaluated = len(selection_df)
        stats['selection_rate'] = (len(selected) / total_evaluated * 100) if total_evaluated > 0 else 0
    else:
        stats['selection_rate'] = 0
    
    # Discard rate and reasons
    if not discard_df.empty and 'motivo_principal' in discard_df.columns:
        stats['discard_reasons'] = discard_df['motivo_principal'].value_counts().to_dict()
    else:
        stats['discard_reasons'] = {}
    
    # Average selection metrics
    if not selection_df.empty:
        stats['avg_selection_age'] = selection_df['idade'].mean() if 'idade' in selection_df.columns else 0
        stats['avg_selection_weight'] = selection_df['peso'].mean() if 'peso' in selection_df.columns else 0
        stats['avg_backfat'] = selection_df['espessura_toucinho'].mean() if 'espessura_toucinho' in selection_df.columns else 0
    else:
        stats['avg_selection_age'] = 0
        stats['avg_selection_weight'] = 0
        stats['avg_backfat'] = 0
    
    return stats

# Add after the last function in the file

# File path for mortality records
MORTALITY_FILE = "data/mortality.csv"

def load_mortality_records():
    """Load mortality records from CSV or create empty DataFrame if file doesn't exist"""
    if os.path.exists(MORTALITY_FILE):
        return pd.read_csv(MORTALITY_FILE)
    else:
        return pd.DataFrame({
            'id_morte': [],
            'id_animal': [],
            'data_morte': [],
            'causa_morte': [],
            'categoria': [],
            'idade_dias': [],
            'peso_morte': [],
            'local_morte': [],  # Ex: Maternidade, Creche, etc.
            'necropsia': [],    # Realizou necropsia? (Sim/Não)
            'resultado_necropsia': [],
            'medidas_preventivas': [],
            'responsavel': [],
            'observacao': []
        })

def save_mortality_records(df):
    """Save mortality records to CSV"""
    df.to_csv(MORTALITY_FILE, index=False)

def calculate_mortality_statistics(mortality_df, start_date=None, end_date=None, category=None):
    """Calculate mortality statistics for the given period and category"""
    if mortality_df.empty:
        return {
            'total_deaths': 0,
            'deaths_by_cause': {},
            'deaths_by_location': {},
            'avg_age_death': 0,
            'mortality_rate': 0
        }

    # Convert dates
    mortality_df['data_morte'] = pd.to_datetime(mortality_df['data_morte'])

    # Apply date filters if provided
    if start_date:
        mortality_df = mortality_df[mortality_df['data_morte'] >= pd.to_datetime(start_date)]
    if end_date:
        mortality_df = mortality_df[mortality_df['data_morte'] <= pd.to_datetime(end_date)]

    # Apply category filter if provided
    if category:
        mortality_df = mortality_df[mortality_df['categoria'] == category]

    # Calculate statistics
    stats = {
        'total_deaths': len(mortality_df),
        'deaths_by_cause': mortality_df['causa_morte'].value_counts().to_dict(),
        'deaths_by_location': mortality_df['local_morte'].value_counts().to_dict(),
        'avg_age_death': mortality_df['idade_dias'].mean() if 'idade_dias' in mortality_df.columns else 0,
    }

    return stats

def generate_mortality_report(mortality_df, animals_df, start_date=None, end_date=None):
    """Generate a detailed mortality report"""
    if mortality_df.empty:
        return pd.DataFrame()

    # Merge with animals data
    report_df = pd.merge(
        mortality_df,
        animals_df[['id_animal', 'identificacao', 'categoria', 'data_nascimento']],
        on='id_animal',
        how='left'
    )

    # Apply date filters
    if start_date:
        report_df = report_df[report_df['data_morte'] >= pd.to_datetime(start_date)]
    if end_date:
        report_df = report_df[report_df['data_morte'] <= pd.to_datetime(end_date)]

    # Calculate additional metrics
    report_df['idade_morte'] = (pd.to_datetime(report_df['data_morte']) - 
                               pd.to_datetime(report_df['data_nascimento'])).dt.days

    return report_df.sort_values('data_morte', ascending=False)

def load_vaccines():
    """Load vaccines data from CSV or create empty DataFrame if file doesn't exist"""
    if os.path.exists(VACCINES_FILE):
        return pd.read_csv(VACCINES_FILE)
    else:
        return pd.DataFrame({
            'id_vacina': [],
            'nome': [],
            'fabricante': [],
            'tipo': [],  # Ex: Bacteriana, Viral, etc.
            'forma_aplicacao': [],  # Ex: Intramuscular, Subcutânea
            'dose_padrao': [],
            'unidade_dose': [],  # Ex: mL, mg
            'intervalo_minimo': [],  # Dias entre doses
            'validade_dias': [],
            'observacao': []
        })

def save_vaccines(df):
    """Save vaccines data to CSV"""
    df.to_csv(VACCINES_FILE, index=False)

def load_vaccination_protocols():
    """Load vaccination protocols data from CSV or create empty DataFrame if file doesn't exist"""
    if os.path.exists(VACCINATION_PROTOCOLS_FILE):
        return pd.read_csv(VACCINATION_PROTOCOLS_FILE)
    else:
        return pd.DataFrame({
            'id_protocolo': [],
            'nome_protocolo': [],
            'categoria_animal': [],  # Ex: Matriz, Leitão, etc.
            'idade_aplicacao': [],  # Idade em dias
            'id_vacina': [],
            'dose': [],
            'intervalo_reforco': [],  # Dias até o reforço
            'prioridade': [],  # Alta, Média, Baixa
            'obrigatoria': [],  # True/False
            'observacao': []
        })

def save_vaccination_protocols(df):
    """Save vaccination protocols data to CSV"""
    df.to_csv(VACCINATION_PROTOCOLS_FILE, index=False)

def load_vaccination_records():
    """Load vaccination records data from CSV or create empty DataFrame if file doesn't exist"""
    if os.path.exists(VACCINATION_RECORDS_FILE):
        return pd.read_csv(VACCINATION_RECORDS_FILE)
    else:
        return pd.DataFrame({
            'id_registro': [],
            'id_animal': [],
            'id_vacina': [],
            'id_protocolo': [],  # Pode ser nulo se for vacinação avulsa
            'data_aplicacao': [],
            'dose_aplicada': [],
            'via_aplicacao': [],
            'lote_vacina': [],
            'data_validade': [],
            'responsavel': [],
            'local_aplicacao': [],  # Ex: Pescoço, Pernil
            'reacao': [],  # Registrar reações adversas
            'observacao': []
        })

def save_vaccination_records(df):
    """Save vaccination records data to CSV"""
    df.to_csv(VACCINATION_RECORDS_FILE, index=False)

def calculate_next_vaccinations(animal_id, animals_df, protocols_df, records_df):
    """Calculate next vaccinations needed for an animal based on protocols and history"""
    if animal_id not in animals_df['id_animal'].values:
        return pd.DataFrame()  # Animal não encontrado
    
    animal = animals_df[animals_df['id_animal'] == animal_id].iloc[0]
    categoria = animal['categoria']

    # Filtrar protocolos para a categoria do animal
    protocolos_categoria = protocols_df[protocols_df['categoria_animal'] == categoria]

    if protocolos_categoria.empty:
        return pd.DataFrame()  # Sem protocolos para esta categoria

    # Calcular idade do animal em dias
    if pd.isna(animal['data_nascimento']):
        return pd.DataFrame()  # Data de nascimento necessária

    idade_dias = calculate_age(pd.to_datetime(animal['data_nascimento']).date())

    # Verificar vacinas já aplicadas
    vacinas_aplicadas = records_df[records_df['id_animal'] == animal_id]

    proximas_vacinas = []
    for _, protocolo in protocolos_categoria.iterrows():
        # Verificar se a idade é adequada
        if idade_dias >= protocolo['idade_aplicacao']:
            # Verificar se já foi aplicada
            if vacinas_aplicadas.empty or not any(
                (vacinas_aplicadas['id_protocolo'] == protocolo['id_protocolo']) &
                (pd.to_datetime(vacinas_aplicadas['data_aplicacao']).dt.date >= 
                 (datetime.now().date() - timedelta(days=protocolo['intervalo_reforco'])))
            ):
                proximas_vacinas.append({
                    'id_protocolo': protocolo['id_protocolo'],
                    'nome_protocolo': protocolo['nome_protocolo'],
                    'id_vacina': protocolo['id_vacina'],
                    'idade_aplicacao': protocolo['idade_aplicacao'],
                    'prioridade': protocolo['prioridade'],
                    'status': 'Pendente',
                    'data_prevista': (datetime.now() + timedelta(days=1)).date()
                })

    return pd.DataFrame(proximas_vacinas)

def get_vaccination_history(animal_id, records_df, vaccines_df):
    """Get complete vaccination history for an animal"""
    if records_df.empty or animal_id not in records_df['id_animal'].values:
        return pd.DataFrame()

    # Filtrar registros do animal
    historico = records_df[records_df['id_animal'] == animal_id].copy()

    # Adicionar informações da vacina
    if not vaccines_df.empty:
        historico = pd.merge(
            historico,
            vaccines_df[['id_vacina', 'nome', 'fabricante']],
            on='id_vacina',
            how='left'
        )

    return historico.sort_values('data_aplicacao', ascending=False)

def generate_vaccination_report(start_date, end_date, records_df, animals_df, vaccines_df):
    """Generate vaccination report for a specific period"""
    if records_df.empty:
        return pd.DataFrame()

    # Filtrar registros pelo período
    mask = (pd.to_datetime(records_df['data_aplicacao']) >= pd.to_datetime(start_date)) & \
           (pd.to_datetime(records_df['data_aplicacao']) <= pd.to_datetime(end_date))

    period_records = records_df[mask].copy()

    if period_records.empty:
        return pd.DataFrame()

    # Adicionar informações dos animais e vacinas
    if not animals_df.empty:
        period_records = pd.merge(
            period_records,
            animals_df[['id_animal', 'identificacao', 'categoria']],
            on='id_animal',
            how='left'
        )

    if not vaccines_df.empty:
        period_records = pd.merge(
            period_records,
            vaccines_df[['id_vacina', 'nome', 'fabricante']],
            on='id_vacina',
            how='left'
        )

    return period_records.sort_values('data_aplicacao', ascending=False)

def load_heat_detection():
    """Load heat detection data from CSV or create empty DataFrame if file doesn't exist"""
    if os.path.exists(HEAT_DETECTION_FILE):
        return pd.read_csv(HEAT_DETECTION_FILE)
    else:
        return pd.DataFrame({
            'id_rufia': [],
            'id_animal': [],  # ID do rufião
            'nome': [],
            'status': [],  # Ativo/Inativo
            'data_inicio': [],
            'data_fim': [],  # Pode ser null se ainda estiver ativo
            'observacao': []
        })

def save_heat_detection(df):
    """Save heat detection data to CSV"""
    df.to_csv(HEAT_DETECTION_FILE, index=False)

def load_heat_records():
    """Load heat records data from CSV or create empty DataFrame if file doesn't exist"""
    if os.path.exists(HEAT_RECORDS_FILE):
        return pd.read_csv(HEAT_RECORDS_FILE)
    else:
        return pd.DataFrame({
            'id_registro': [],
            'id_rufia': [],
            'id_matriz': [],
            'data_deteccao': [],
            'hora_deteccao': [],
            'intensidade_cio': [],  # Forte, Médio, Fraco
            'comportamento': [],    # Reflexo, Monta, Aceitação
            'duracao_minutos': [],
            'sinais_externos': [],  # Vermelhidão, Inchaço, etc
            'confirmado': [],       # True/False
            'responsavel': [],
            'observacao': []
        })

def save_heat_records(df):
    """Save heat records data to CSV"""
    df.to_csv(HEAT_RECORDS_FILE, index=False)

def calculate_heat_interval(matriz_id, heat_records_df):
    """Calculate interval between heat detections for a specific sow"""
    if heat_records_df.empty or matriz_id not in heat_records_df['id_matriz'].values:
        return None

    # Get records for the specific sow
    matriz_records = heat_records_df[
        (heat_records_df['id_matriz'] == matriz_id) & 
        (heat_records_df['confirmado'] == True)
    ].copy()

    if len(matriz_records) < 2:
        return None

    # Sort by detection date
    matriz_records['data_deteccao'] = pd.to_datetime(matriz_records['data_deteccao'])
    matriz_records = matriz_records.sort_values('data_deteccao')

    # Calculate intervals
    intervals = matriz_records['data_deteccao'].diff().dt.days

    return {
        'last_interval': intervals.iloc[-1],
        'avg_interval': intervals.mean(),
        'min_interval': intervals.min(),
        'max_interval': intervals.max()
    }

def generate_heat_report(heat_records_df, animals_df, start_date=None, end_date=None):
    """Generate report of heat detections"""
    if heat_records_df.empty:
        return pd.DataFrame()

    # Make a copy to avoid modifying original
    report_df = heat_records_df.copy()

    # Convert date column to datetime
    report_df['data_deteccao'] = pd.to_datetime(report_df['data_deteccao'])

    # Merge with animals data
    report_df = pd.merge(
        report_df,
        animals_df[['id_animal', 'identificacao', 'categoria']],
        left_on='id_matriz',
        right_on='id_animal',
        how='left'
    )

    # Apply date filters
    if start_date:
        report_df = report_df[report_df['data_deteccao'].dt.date >= pd.to_datetime(start_date).date()]
    if end_date:
        report_df = report_df[report_df['data_deteccao'].dt.date <= pd.to_datetime(end_date).date()]

    return report_df.sort_values('data_deteccao', ascending=False)

def predict_next_heat(matriz_id, heat_records_df):
    """Predict next heat date based on historical data"""
    intervals = calculate_heat_interval(matriz_id, heat_records_df)

    if not intervals:
        return None

    # Get last heat date
    last_heat = heat_records_df[
        (heat_records_df['id_matriz'] == matriz_id) & 
        (heat_records_df['confirmado'] == True)
    ]['data_deteccao'].max()

    if pd.isna(last_heat):
        return None

    # Use average interval to predict next heat
    last_heat = pd.to_datetime(last_heat)
    next_heat = last_heat + timedelta(days=round(intervals['avg_interval']))

    return {
        'last_heat': last_heat.date(),
        'predicted_next': next_heat.date(),
        'confidence': 'Alta' if 20 <= intervals['avg_interval'] <= 22 else 'Média'
    }

# Add after the existing file paths
EMPLOYEES_FILE = "data/employees.csv"

def load_employees():
    """Load employees data from CSV or create empty DataFrame if file doesn't exist"""
    # Define a estrutura vazia padrão
    empty_df = pd.DataFrame({
        'id_colaborador': [],
        'nome': [],
        'matricula': [],
        'cargo': [],
        'setor': [],
        'data_admissao': [],
        'status': [],  # Ativo/Inativo
        'ultimo_acesso': [],
        'observacao': []
    })
    
    if os.path.exists(EMPLOYEES_FILE):
        try:
            # Tenta carregar o arquivo CSV
            df = pd.read_csv(EMPLOYEES_FILE)
            
            # Verifica se o DataFrame não está vazio
            if not df.empty:
                return df
            else:
                # Se estiver vazio, retorna a estrutura padrão
                return empty_df
        except (pd.errors.EmptyDataError, pd.errors.ParserError):
            # Se ocorrer erro de arquivo vazio ou formato incorreto, retorna a estrutura padrão
            return empty_df
    else:
        # Se o arquivo não existir, retorna a estrutura padrão
        return empty_df

def save_employees(df):
    """Save employees data to CSV"""
    df.to_csv(EMPLOYEES_FILE, index=False)

def authenticate_employee(matricula):
    """Authenticate employee by registration number"""
    employees_df = load_employees()

    if employees_df.empty:
        return None
        
    # Converte a matrícula para string para garantir a comparação correta
    matricula_str = str(matricula)
    # Garante que as matrículas no DataFrame também são strings
    employees_df['matricula'] = employees_df['matricula'].astype(str)

    employee = employees_df[
        (employees_df['matricula'] == matricula_str) & 
        (employees_df['status'] == 'Ativo')
    ]

    if not employee.empty:
        # Update last access
        # Primeiro, certifique-se de que a coluna ultimo_acesso tem o tipo de dados correto (string/object)
        if 'ultimo_acesso' not in employees_df.columns:
            employees_df['ultimo_acesso'] = None
        
        # Garante que a coluna seja do tipo object (string) antes de atribuir um valor string
        if not pd.api.types.is_object_dtype(employees_df['ultimo_acesso']):
            employees_df['ultimo_acesso'] = employees_df['ultimo_acesso'].astype(str)
        
        # Atualiza o último acesso
        employees_df.loc[
            employees_df['matricula'] == matricula_str, 
            'ultimo_acesso'
        ] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        save_employees(employees_df)
        return employee.iloc[0].to_dict()

    return None

def check_developer_access(user):
    """Verifica se o usuário tem acesso de desenvolvedor"""
    if user and 'cargo' in user:
        return user['cargo'] == 'Desenvolvedor'
    return False

def load_permissions_map():
    """
    Carrega o mapeamento de permissões por cargo de um arquivo JSON ou retorna o mapeamento padrão.
    
    Returns:
        dict: Mapeamento de permissões por cargo
    """
    # Caminho para o arquivo de configuração de permissões
    permission_file = "data/permissions.json"
    
    # Mapeamento padrão de permissões por cargo
    default_permissions_map = {
        # Administrador tem todas as permissões
        'Administrador': [
            'admin',
            'edit',
            'view_reports',
            'manage_users',
            'manage_animals',
            'manage_reproduction',
            'manage_health',
            'manage_growth',
            'export_data',
            'import_data'
        ],
        
        # Desenvolvedor tem permissões administrativas e de sistema
        'Desenvolvedor': [
            'admin',
            'edit',
            'view_reports',
            'manage_users',
            'manage_animals',
            'manage_reproduction',
            'manage_health',
            'manage_growth',
            'export_data',
            'import_data',
            'developer_tools',
            'system_config'
        ],
        
        # Gerente tem permissões administrativas, sem acesso de desenvolvedor
        'Gerente': [
            'admin',
            'edit',
            'view_reports',
            'manage_users',
            'manage_animals',
            'manage_reproduction',
            'manage_health',
            'manage_growth',
            'export_data', 
            'import_data'
        ],
        
        # Técnico tem permissões de edição e visualização, sem permissões administrativas
        'Técnico': [
            'edit',
            'view_reports', 
            'manage_animals', 
            'manage_reproduction',
            'manage_health',
            'manage_growth'
        ],
        
        # Operador tem permissões básicas de registro
        'Operador': [
            'edit',
            'manage_animals',
            'manage_health',
            'view_reports'
        ],
        
        # Visitante tem apenas permissões de visualização
        'Visitante': [
            'view_reports'
        ]
    }
    
    # Verificar se o arquivo de permissões existe
    if os.path.exists(permission_file):
        try:
            import json
            with open(permission_file, 'r') as f:
                return json.load(f)
        except:
            # Se houver erro ao carregar, retorna o mapeamento padrão
            return default_permissions_map
    else:
        # Se o arquivo não existir, retorna o mapeamento padrão
        return default_permissions_map
    
def save_permissions_map(permissions_map):
    """
    Salva o mapeamento de permissões por cargo em um arquivo JSON.
    
    Args:
        permissions_map (dict): Mapeamento de permissões por cargo para salvar
        
    Returns:
        bool: True se salvo com sucesso, False caso contrário
    """
    # Caminho para o arquivo de configuração de permissões
    permission_file = "data/permissions.json"
    
    try:
        # Garantir que o diretório data existe
        if not os.path.exists("data"):
            os.makedirs("data")
            
        import json
        with open(permission_file, 'w') as f:
            json.dump(permissions_map, f, indent=4)
        return True
    except Exception as e:
        print(f"Erro ao salvar permissões: {str(e)}")
        return False

def check_permission(user, permission_type):
    """
    Verifica se o usuário tem a permissão especificada com base em seu cargo
    
    Args:
        user: Dicionário com dados do usuário atual
        permission_type: Tipo de permissão a verificar ('admin', 'edit', 'view_reports', etc.)
        
    Returns:
        bool: True se o usuário tem a permissão, False caso contrário
    """
    if not user or 'cargo' not in user:
        return False
        
    # Carregar o mapeamento de permissões
    permissions_map = load_permissions_map()
    
    # Obtém as permissões do cargo do usuário, ou uma lista vazia se o cargo não estiver mapeado
    user_permissions = permissions_map.get(user['cargo'], [])
    
    # Verifica se a permissão solicitada está na lista de permissões do usuário
    return permission_type in user_permissions
    
def register_employee(nome, matricula, cargo, setor, observacao=""):
    """Register a new employee"""
    employees_df = load_employees()
    
    # Converte a matrícula para string
    matricula_str = str(matricula)
    
    # Garante que as matrículas no DataFrame também são strings
    if not employees_df.empty:
        employees_df['matricula'] = employees_df['matricula'].astype(str)

    # Check if registration number already exists
    if not employees_df.empty and matricula_str in employees_df['matricula'].values:
        return False, "Matrícula já cadastrada"

    # Create new employee record
    new_employee = {
        'id_colaborador': str(uuid.uuid4()),
        'nome': nome,
        'matricula': matricula_str,
        'cargo': cargo,
        'setor': setor,
        'data_admissao': datetime.now().strftime('%Y-%m-%d'),
        'status': 'Ativo',
        'ultimo_acesso': None,
        'observacao': observacao
    }

    # Add to DataFrame
    if employees_df.empty:
        employees_df = pd.DataFrame([new_employee])
    else:
        employees_df = pd.concat([employees_df, pd.DataFrame([new_employee])], ignore_index=True)

    # Save updated DataFrame
    save_employees(employees_df)
    return True, "Colaborador cadastrado com sucesso"

def update_employee_status(matricula, new_status):
    """Update employee status (Active/Inactive)"""
    employees_df = load_employees()
    
    # Converte a matrícula para string
    matricula_str = str(matricula)
    
    # Garante que as matrículas no DataFrame também são strings
    if not employees_df.empty:
        employees_df['matricula'] = employees_df['matricula'].astype(str)

    if employees_df.empty or matricula_str not in employees_df['matricula'].values:
        return False, "Colaborador não encontrado"

    employees_df.loc[
        employees_df['matricula'] == matricula_str, 
        'status'
    ] = new_status

    save_employees(employees_df)
    return True, f"Status atualizado para {new_status}"
    
# Funções para o sistema de recria

def load_recria():
    """Load recria data from CSV or create empty DataFrame if file doesn't exist"""
    if os.path.exists(RECRIA_FILE):
        return pd.read_csv(RECRIA_FILE)
    else:
        return pd.DataFrame({
            'id_recria': [],
            'id_animal': [],           # ID do animal em recria
            'identificacao': [],       # Identificação do animal (brinco, etc.)
            'data_entrada': [],        # Data de entrada na recria
            'peso_entrada': [],        # Peso na entrada (kg)
            'origem': [],              # Origem do animal (Desmame, Compra, etc.)
            'id_lote': [],             # ID do lote de recria
            'data_saida': [],          # Data de saída da recria
            'peso_saida': [],          # Peso na saída (kg)
            'destino': [],             # Destino (Terminação, Reprodução, Venda, etc.)
            'status': [],              # Status (Ativo, Finalizado, etc.)
            'fase_recria': [],         # Fase da recria (Fase 1, Fase 2, etc.)
            'observacao': []
        })

def save_recria(df):
    """Save recria data to CSV"""
    df.to_csv(RECRIA_FILE, index=False)

def load_recria_lotes():
    """Load recria batches data from CSV or create empty DataFrame if file doesn't exist"""
    if os.path.exists(RECRIA_LOTES_FILE):
        return pd.read_csv(RECRIA_LOTES_FILE)
    else:
        return pd.DataFrame({
            'id_lote': [],
            'codigo': [],              # Código do lote
            'data_formacao': [],       # Data de formação do lote
            'quantidade_inicial': [],  # Quantidade inicial de animais
            'idade_media': [],         # Idade média dos animais (dias)
            'peso_medio_inicial': [],  # Peso médio inicial (kg)
            'id_baia': [],             # Baia onde o lote está alojado
            'data_encerramento': [],   # Data de encerramento do lote
            'quantidade_final': [],    # Quantidade final de animais
            'peso_medio_final': [],    # Peso médio final (kg)
            'gpd': [],                 # Ganho de peso diário (kg)
            'ca': [],                  # Conversão alimentar
            'mortalidade': [],         # Taxa de mortalidade (%)
            'status': [],              # Status (Ativo, Finalizado, etc.)
            'responsavel': [],         # Responsável pelo lote
            'observacao': []
        })

def save_recria_lotes(df):
    """Save recria batches data to CSV"""
    df.to_csv(RECRIA_LOTES_FILE, index=False)

def load_recria_pesagens():
    """Load recria weighing data from CSV or create empty DataFrame if file doesn't exist"""
    if os.path.exists(RECRIA_PESAGENS_FILE):
        return pd.read_csv(RECRIA_PESAGENS_FILE)
    else:
        return pd.DataFrame({
            'id_pesagem': [],
            'id_animal': [],           # ID do animal pesado
            'id_lote': [],             # ID do lote (quando pesagem em grupo)
            'data_pesagem': [],        # Data da pesagem
            'peso': [],                # Peso (kg)
            'tipo_pesagem': [],        # Individual ou Grupo
            'fase_recria': [],         # Fase da recria
            'idade_dias': [],          # Idade em dias
            'ganho_desde_ultima': [],  # Ganho desde a última pesagem (kg)
            'gpd_periodo': [],         # Ganho de peso diário no período (g/dia)
            'responsavel': [],         # Responsável pela pesagem
            'observacao': []
        })

def save_recria_pesagens(df):
    """Save recria weighing data to CSV"""
    df.to_csv(RECRIA_PESAGENS_FILE, index=False)

def load_recria_transferencias():
    """Load recria transfers data from CSV or create empty DataFrame if file doesn't exist"""
    if os.path.exists(RECRIA_TRANSFERENCIAS_FILE):
        return pd.read_csv(RECRIA_TRANSFERENCIAS_FILE)
    else:
        return pd.DataFrame({
            'id_transferencia': [],
            'id_animal': [],           # ID do animal transferido
            'id_lote_origem': [],      # ID do lote de origem
            'id_lote_destino': [],     # ID do lote de destino
            'id_baia_origem': [],      # ID da baia de origem
            'id_baia_destino': [],     # ID da baia de destino
            'data_transferencia': [],  # Data da transferência
            'motivo': [],              # Motivo da transferência
            'peso_transferencia': [],  # Peso na transferência (kg)
            'fase_origem': [],         # Fase de recria de origem
            'fase_destino': [],        # Fase de recria de destino
            'responsavel': [],         # Responsável pela transferência
            'observacao': []
        })

def save_recria_transferencias(df):
    """Save recria transfers data to CSV"""
    df.to_csv(RECRIA_TRANSFERENCIAS_FILE, index=False)

def load_recria_alimentacao():
    """Load recria feeding data from CSV or create empty DataFrame if file doesn't exist"""
    if os.path.exists(RECRIA_ALIMENTACAO_FILE):
        return pd.read_csv(RECRIA_ALIMENTACAO_FILE)
    else:
        return pd.DataFrame({
            'id_alimentacao': [],
            'id_lote': [],             # ID do lote alimentado
            'data_inicio': [],         # Data de início do fornecimento
            'data_fim': [],            # Data de fim do fornecimento
            'tipo_racao': [],          # Tipo de ração
            'quantidade_kg': [],       # Quantidade fornecida (kg)
            'custo_kg': [],            # Custo por kg (R$)
            'custo_total': [],         # Custo total (R$)
            'consumo_animal_dia': [],  # Consumo médio por animal por dia (kg)
            'fase_recria': [],         # Fase da recria
            'responsavel': [],         # Responsável pelo registro
            'observacao': []
        })

def save_recria_alimentacao(df):
    """Save recria feeding data to CSV"""
    df.to_csv(RECRIA_ALIMENTACAO_FILE, index=False)

def load_recria_medicacao():
    """Load recria medication data from CSV or create empty DataFrame if file doesn't exist"""
    if os.path.exists(RECRIA_MEDICACAO_FILE):
        return pd.read_csv(RECRIA_MEDICACAO_FILE)
    else:
        return pd.DataFrame({
            'id_medicacao': [],
            'id_animal': [],           # ID do animal medicado (quando individual)
            'id_lote': [],             # ID do lote (quando medicação coletiva)
            'data_aplicacao': [],      # Data da aplicação
            'medicamento': [],         # Nome do medicamento
            'via_aplicacao': [],       # Via de aplicação
            'dose': [],                # Dose aplicada
            'unidade_dose': [],        # Unidade da dose (ml, mg, etc.)
            'motivo': [],              # Motivo da medicação
            'tipo_aplicacao': [],      # Individual ou Coletiva
            'periodo_carencia': [],    # Período de carência (dias)
            'data_fim_carencia': [],   # Data do fim da carência
            'responsavel': [],         # Responsável pela aplicação
            'observacao': []
        })

def save_recria_medicacao(df):
    """Save recria medication data to CSV"""
    df.to_csv(RECRIA_MEDICACAO_FILE, index=False)

def criar_lote_recria(codigo, data_formacao, quantidade_inicial, idade_media, 
                      peso_medio_inicial, id_baia, responsavel, observacao=""):
    """Create a new recria batch"""
    lotes_df = load_recria_lotes()
    
    # Verificar se já existe um lote com o mesmo código
    if not lotes_df.empty and codigo in lotes_df['codigo'].values:
        return False, "Já existe um lote com este código"
    
    # Criar novo lote
    novo_lote = {
        'id_lote': str(uuid.uuid4()),
        'codigo': codigo,
        'data_formacao': data_formacao,
        'quantidade_inicial': quantidade_inicial,
        'idade_media': idade_media,
        'peso_medio_inicial': peso_medio_inicial,
        'id_baia': id_baia,
        'data_encerramento': None,
        'quantidade_final': None,
        'peso_medio_final': None,
        'gpd': None,
        'ca': None,
        'mortalidade': 0,
        'status': 'Ativo',
        'responsavel': responsavel,
        'observacao': observacao
    }
    
    # Adicionar ao DataFrame
    if lotes_df.empty:
        lotes_df = pd.DataFrame([novo_lote])
    else:
        lotes_df = pd.concat([lotes_df, pd.DataFrame([novo_lote])], ignore_index=True)
    
    # Salvar DataFrame atualizado
    save_recria_lotes(lotes_df)
    return True, "Lote de recria criado com sucesso", novo_lote['id_lote']

def adicionar_animal_recria(id_animal, identificacao, data_entrada, peso_entrada, 
                          origem, id_lote, fase_recria, observacao=""):
    """Add an animal to recria"""
    recria_df = load_recria()
    
    # Verificar se o animal já está em recria
    if not recria_df.empty and id_animal in recria_df[recria_df['status'] == 'Ativo']['id_animal'].values:
        return False, "Animal já está em recria"
    
    # Criar novo registro de recria
    nova_recria = {
        'id_recria': str(uuid.uuid4()),
        'id_animal': id_animal,
        'identificacao': identificacao,
        'data_entrada': data_entrada,
        'peso_entrada': peso_entrada,
        'origem': origem,
        'id_lote': id_lote,
        'data_saida': None,
        'peso_saida': None,
        'destino': None,
        'status': 'Ativo',
        'fase_recria': fase_recria,
        'observacao': observacao
    }
    
    # Adicionar ao DataFrame
    if recria_df.empty:
        recria_df = pd.DataFrame([nova_recria])
    else:
        recria_df = pd.concat([recria_df, pd.DataFrame([nova_recria])], ignore_index=True)
    
    # Atualizar a quantidade de animais no lote
    lotes_df = load_recria_lotes()
    if not lotes_df.empty and id_lote in lotes_df['id_lote'].values:
        # Somar 1 à quantidade atual (se necessário)
        pass
    
    # Salvar DataFrame atualizado
    save_recria(recria_df)
    return True, "Animal adicionado à recria com sucesso"

def registrar_pesagem_recria(id_animal, data_pesagem, peso, tipo_pesagem, 
                           fase_recria, id_lote=None, responsavel=None, observacao=None):
    """Register a new weighing for a recria animal"""
    pesagens_df = load_recria_pesagens()
    recria_df = load_recria()
    
    # Verificar se o animal está em recria
    if id_animal and not recria_df.empty and id_animal not in recria_df[recria_df['status'] == 'Ativo']['id_animal'].values:
        return False, "Animal não encontrado na recria ou não está ativo"
    
    # Obter a idade do animal
    idade_dias = None
    if id_animal:
        animals_df = load_animals()
        animal = animals_df[animals_df['id_animal'] == id_animal]
        if not animal.empty and not pd.isna(animal['data_nascimento'].iloc[0]):
            data_nascimento = pd.to_datetime(animal['data_nascimento'].iloc[0])
            idade_dias = (pd.to_datetime(data_pesagem) - data_nascimento).days
    
    # Calcular ganho desde a última pesagem
    ganho_desde_ultima = None
    gpd_periodo = None
    
    if id_animal and not pesagens_df.empty:
        ultimas_pesagens = pesagens_df[
            (pesagens_df['id_animal'] == id_animal) & 
            (pd.to_datetime(pesagens_df['data_pesagem']) < pd.to_datetime(data_pesagem))
        ].sort_values('data_pesagem', ascending=False)
        
        if not ultimas_pesagens.empty:
            ultima_pesagem = ultimas_pesagens.iloc[0]
            peso_anterior = ultima_pesagem['peso']
            data_anterior = pd.to_datetime(ultima_pesagem['data_pesagem'])
            dias_desde_ultima = (pd.to_datetime(data_pesagem) - data_anterior).days
            
            if dias_desde_ultima > 0:
                ganho_desde_ultima = float(peso) - float(peso_anterior)
                gpd_periodo = ganho_desde_ultima * 1000 / dias_desde_ultima  # g/dia
    
    # Criar novo registro de pesagem
    nova_pesagem = {
        'id_pesagem': str(uuid.uuid4()),
        'id_animal': id_animal,
        'id_lote': id_lote,
        'data_pesagem': data_pesagem,
        'peso': peso,
        'tipo_pesagem': tipo_pesagem,
        'fase_recria': fase_recria,
        'idade_dias': idade_dias,
        'ganho_desde_ultima': ganho_desde_ultima,
        'gpd_periodo': gpd_periodo,
        'responsavel': responsavel,
        'observacao': observacao
    }
    
    # Adicionar ao DataFrame
    if pesagens_df.empty:
        pesagens_df = pd.DataFrame([nova_pesagem])
    else:
        pesagens_df = pd.concat([pesagens_df, pd.DataFrame([nova_pesagem])], ignore_index=True)
    
    # Salvar DataFrame atualizado
    save_recria_pesagens(pesagens_df)
    return True, "Pesagem registrada com sucesso"

def transferir_animal_recria(id_animal, id_lote_destino, id_baia_destino, data_transferencia, 
                           motivo, peso_transferencia, fase_destino, responsavel, observacao=None):
    """Transfer an animal to another recria batch"""
    recria_df = load_recria()
    lotes_df = load_recria_lotes()
    transferencias_df = load_recria_transferencias()
    
    # Verificar se o animal está em recria
    if not recria_df.empty and id_animal not in recria_df[recria_df['status'] == 'Ativo']['id_animal'].values:
        return False, "Animal não encontrado na recria ou não está ativo"
    
    # Obter informações do animal
    animal_recria = recria_df[recria_df['id_animal'] == id_animal].iloc[0]
    id_lote_origem = animal_recria['id_lote']
    fase_origem = animal_recria['fase_recria']
    
    # Obter a baia de origem
    id_baia_origem = None
    if not lotes_df.empty and id_lote_origem in lotes_df['id_lote'].values:
        id_baia_origem = lotes_df[lotes_df['id_lote'] == id_lote_origem]['id_baia'].iloc[0]
    
    # Criar novo registro de transferência
    nova_transferencia = {
        'id_transferencia': str(uuid.uuid4()),
        'id_animal': id_animal,
        'id_lote_origem': id_lote_origem,
        'id_lote_destino': id_lote_destino,
        'id_baia_origem': id_baia_origem,
        'id_baia_destino': id_baia_destino,
        'data_transferencia': data_transferencia,
        'motivo': motivo,
        'peso_transferencia': peso_transferencia,
        'fase_origem': fase_origem,
        'fase_destino': fase_destino,
        'responsavel': responsavel,
        'observacao': observacao
    }
    
    # Adicionar ao DataFrame de transferências
    if transferencias_df.empty:
        transferencias_df = pd.DataFrame([nova_transferencia])
    else:
        transferencias_df = pd.concat([transferencias_df, pd.DataFrame([nova_transferencia])], ignore_index=True)
    
    # Atualizar o registro de recria
    recria_df.loc[recria_df['id_animal'] == id_animal, 'id_lote'] = id_lote_destino
    recria_df.loc[recria_df['id_animal'] == id_animal, 'fase_recria'] = fase_destino
    
    # Registrar a pesagem da transferência
    registrar_pesagem_recria(
        id_animal=id_animal,
        data_pesagem=data_transferencia,
        peso=peso_transferencia,
        tipo_pesagem='Individual',
        fase_recria=fase_destino,
        id_lote=id_lote_destino,
        responsavel=responsavel,
        observacao=f"Pesagem de transferência: {motivo}"
    )
    
    # Salvar DataFrames atualizados
    save_recria_transferencias(transferencias_df)
    save_recria(recria_df)
    return True, "Animal transferido com sucesso"

def registrar_alimentacao_recria(id_lote, data_inicio, data_fim, tipo_racao, quantidade_kg, 
                               custo_kg, fase_recria, responsavel, observacao=None):
    """Register feeding for a recria batch"""
    alimentacao_df = load_recria_alimentacao()
    lotes_df = load_recria_lotes()
    
    # Verificar se o lote existe
    if not lotes_df.empty and id_lote not in lotes_df['id_lote'].values:
        return False, "Lote não encontrado"
    
    # Calcular custo total
    custo_total = float(quantidade_kg) * float(custo_kg)
    
    # Calcular consumo médio por animal por dia
    consumo_animal_dia = None
    if not lotes_df.empty:
        lote = lotes_df[lotes_df['id_lote'] == id_lote].iloc[0]
        quantidade_animais = lote['quantidade_inicial']
        if quantidade_animais > 0:
            dias = (pd.to_datetime(data_fim) - pd.to_datetime(data_inicio)).days
            if dias > 0:
                consumo_animal_dia = float(quantidade_kg) / quantidade_animais / dias
    
    # Criar novo registro de alimentação
    nova_alimentacao = {
        'id_alimentacao': str(uuid.uuid4()),
        'id_lote': id_lote,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'tipo_racao': tipo_racao,
        'quantidade_kg': quantidade_kg,
        'custo_kg': custo_kg,
        'custo_total': custo_total,
        'consumo_animal_dia': consumo_animal_dia,
        'fase_recria': fase_recria,
        'responsavel': responsavel,
        'observacao': observacao
    }
    
    # Adicionar ao DataFrame
    if alimentacao_df.empty:
        alimentacao_df = pd.DataFrame([nova_alimentacao])
    else:
        alimentacao_df = pd.concat([alimentacao_df, pd.DataFrame([nova_alimentacao])], ignore_index=True)
    
    # Salvar DataFrame atualizado
    save_recria_alimentacao(alimentacao_df)
    return True, "Alimentação registrada com sucesso"

def registrar_medicacao_recria(data_aplicacao, medicamento, via_aplicacao, dose, unidade_dose, 
                           motivo, tipo_aplicacao, periodo_carencia, responsavel, 
                           id_animal=None, id_lote=None, observacao=None):
    """Register medication for recria animal(s)"""
    medicacao_df = load_recria_medicacao()
    
    # Validar dados
    if tipo_aplicacao == 'Individual' and not id_animal:
        return False, "ID do animal é obrigatório para medicação individual"
    
    if tipo_aplicacao == 'Coletiva' and not id_lote:
        return False, "ID do lote é obrigatório para medicação coletiva"
    
    # Calcular data de fim da carência
    data_fim_carencia = None
    if periodo_carencia:
        data_fim_carencia = (pd.to_datetime(data_aplicacao) + pd.Timedelta(days=int(periodo_carencia))).strftime('%Y-%m-%d')
    
    # Criar novo registro de medicação
    nova_medicacao = {
        'id_medicacao': str(uuid.uuid4()),
        'id_animal': id_animal,
        'id_lote': id_lote,
        'data_aplicacao': data_aplicacao,
        'medicamento': medicamento,
        'via_aplicacao': via_aplicacao,
        'dose': dose,
        'unidade_dose': unidade_dose,
        'motivo': motivo,
        'tipo_aplicacao': tipo_aplicacao,
        'periodo_carencia': periodo_carencia,
        'data_fim_carencia': data_fim_carencia,
        'responsavel': responsavel,
        'observacao': observacao
    }
    
    # Adicionar ao DataFrame
    if medicacao_df.empty:
        medicacao_df = pd.DataFrame([nova_medicacao])
    else:
        medicacao_df = pd.concat([medicacao_df, pd.DataFrame([nova_medicacao])], ignore_index=True)
    
    # Salvar DataFrame atualizado
    save_recria_medicacao(medicacao_df)
    return True, "Medicação registrada com sucesso"

def finalizar_recria(id_animal, data_saida, peso_saida, destino, observacao=None):
    """Finish recria for an animal"""
    recria_df = load_recria()
    
    # Verificar se o animal está em recria
    if not recria_df.empty and id_animal not in recria_df[recria_df['status'] == 'Ativo']['id_animal'].values:
        return False, "Animal não encontrado na recria ou não está ativo"
    
    # Atualizar registro de recria
    recria_df.loc[recria_df['id_animal'] == id_animal, 'data_saida'] = data_saida
    recria_df.loc[recria_df['id_animal'] == id_animal, 'peso_saida'] = peso_saida
    recria_df.loc[recria_df['id_animal'] == id_animal, 'destino'] = destino
    recria_df.loc[recria_df['id_animal'] == id_animal, 'status'] = 'Finalizado'
    recria_df.loc[recria_df['id_animal'] == id_animal, 'observacao'] = observacao
    
    # Registrar pesagem final
    registrar_pesagem_recria(
        id_animal=id_animal,
        data_pesagem=data_saida,
        peso=peso_saida,
        tipo_pesagem='Individual',
        fase_recria=recria_df[recria_df['id_animal'] == id_animal]['fase_recria'].iloc[0],
        id_lote=recria_df[recria_df['id_animal'] == id_animal]['id_lote'].iloc[0],
        observacao=f"Pesagem de saída: {destino}"
    )
    
    # Salvar DataFrame atualizado
    save_recria(recria_df)
    return True, "Recria finalizada com sucesso"

def finalizar_lote_recria(id_lote, data_encerramento, peso_medio_final, gpd, ca, observacao=None):
    """Finish a recria batch"""
    lotes_df = load_recria_lotes()
    recria_df = load_recria()
    
    # Verificar se o lote existe
    if not lotes_df.empty and id_lote not in lotes_df['id_lote'].values:
        return False, "Lote não encontrado"
    
    # Verificar se o lote já está finalizado
    if lotes_df[lotes_df['id_lote'] == id_lote]['status'].iloc[0] == 'Finalizado':
        return False, "Lote já está finalizado"
    
    # Contar animais ativos no lote
    quantidade_final = 0
    if not recria_df.empty:
        quantidade_final = len(recria_df[(recria_df['id_lote'] == id_lote) & (recria_df['status'] == 'Ativo')])
    
    # Calcular mortalidade
    mortalidade = 0
    if not lotes_df.empty:
        quantidade_inicial = lotes_df[lotes_df['id_lote'] == id_lote]['quantidade_inicial'].iloc[0]
        if quantidade_inicial > 0:
            mortalidade = (quantidade_inicial - quantidade_final) / quantidade_inicial * 100
    
    # Atualizar registro do lote
    lotes_df.loc[lotes_df['id_lote'] == id_lote, 'data_encerramento'] = data_encerramento
    lotes_df.loc[lotes_df['id_lote'] == id_lote, 'quantidade_final'] = quantidade_final
    lotes_df.loc[lotes_df['id_lote'] == id_lote, 'peso_medio_final'] = peso_medio_final
    lotes_df.loc[lotes_df['id_lote'] == id_lote, 'gpd'] = gpd
    lotes_df.loc[lotes_df['id_lote'] == id_lote, 'ca'] = ca
    lotes_df.loc[lotes_df['id_lote'] == id_lote, 'mortalidade'] = mortalidade
    lotes_df.loc[lotes_df['id_lote'] == id_lote, 'status'] = 'Finalizado'
    lotes_df.loc[lotes_df['id_lote'] == id_lote, 'observacao'] = observacao
    
    # Salvar DataFrame atualizado
    save_recria_lotes(lotes_df)
    return True, "Lote de recria finalizado com sucesso"

def obter_lotes_recria_ativos():
    """Get active recria batches"""
    lotes_df = load_recria_lotes()
    
    if lotes_df.empty:
        return pd.DataFrame()
    
    # Retornar apenas lotes ativos
    return lotes_df[lotes_df['status'] == 'Ativo']

def obter_animais_recria_ativos(id_lote=None, fase=None):
    """Get active recria animals"""
    recria_df = load_recria()
    
    if recria_df.empty:
        return pd.DataFrame()
    
    # Filtrar por status ativo
    animais = recria_df[recria_df['status'] == 'Ativo']
    
    # Filtrar por lote se especificado
    if id_lote:
        animais = animais[animais['id_lote'] == id_lote]
    
    # Filtrar por fase se especificada
    if fase:
        animais = animais[animais['fase_recria'] == fase]
    
    return animais

def calcular_estatisticas_recria(id_lote=None, fase=None, periodo_inicio=None, periodo_fim=None):
    """Calculate recria statistics"""
    recria_df = load_recria()
    lotes_df = load_recria_lotes()
    pesagens_df = load_recria_pesagens()
    alimentacao_df = load_recria_alimentacao()
    medicacao_df = load_recria_medicacao()
    
    stats = {}
    
    # Filtrar por lote se especificado
    if id_lote:
        recria_df = recria_df[recria_df['id_lote'] == id_lote]
        pesagens_df = pesagens_df[pesagens_df['id_lote'] == id_lote]
        alimentacao_df = alimentacao_df[alimentacao_df['id_lote'] == id_lote]
        medicacao_df = medicacao_df[medicacao_df['id_lote'] == id_lote]
    
    # Filtrar por fase se especificada
    if fase:
        recria_df = recria_df[recria_df['fase_recria'] == fase]
        pesagens_df = pesagens_df[pesagens_df['fase_recria'] == fase]
        alimentacao_df = alimentacao_df[alimentacao_df['fase_recria'] == fase]
    
    # Filtrar por período se especificado
    if periodo_inicio and periodo_fim:
        pesagens_df = pesagens_df[
            (pd.to_datetime(pesagens_df['data_pesagem']) >= pd.to_datetime(periodo_inicio)) &
            (pd.to_datetime(pesagens_df['data_pesagem']) <= pd.to_datetime(periodo_fim))
        ]
        alimentacao_df = alimentacao_df[
            (pd.to_datetime(alimentacao_df['data_inicio']) >= pd.to_datetime(periodo_inicio)) &
            (pd.to_datetime(alimentacao_df['data_fim']) <= pd.to_datetime(periodo_fim))
        ]
        medicacao_df = medicacao_df[
            (pd.to_datetime(medicacao_df['data_aplicacao']) >= pd.to_datetime(periodo_inicio)) &
            (pd.to_datetime(medicacao_df['data_aplicacao']) <= pd.to_datetime(periodo_fim))
        ]
    
    # Estatísticas gerais
    stats['total_animais_ativos'] = len(recria_df[recria_df['status'] == 'Ativo'])
    stats['total_lotes_ativos'] = len(lotes_df[lotes_df['status'] == 'Ativo'])
    
    # Estatísticas de peso e ganho
    if not pesagens_df.empty:
        stats['peso_medio'] = pesagens_df['peso'].mean()
        stats['gpd_medio'] = pesagens_df['gpd_periodo'].mean()
        
        # Calcular distribuição de pesos
        stats['distribuicao_pesos'] = {}
        bins = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, float('inf')]
        labels = ['0-5kg', '5-10kg', '10-15kg', '15-20kg', '20-25kg', 
                  '25-30kg', '30-35kg', '35-40kg', '40-45kg', '45-50kg', '>50kg']
        
        pesagens_df['faixa_peso'] = pd.cut(
            pesagens_df['peso'],
            bins=bins,
            labels=labels,
            right=False
        )
        
        stats['distribuicao_pesos'] = pesagens_df['faixa_peso'].value_counts().to_dict()
    
    # Estatísticas de alimentação
    if not alimentacao_df.empty:
        stats['consumo_total'] = alimentacao_df['quantidade_kg'].sum()
        stats['custo_total_alimentacao'] = alimentacao_df['custo_total'].sum()
        
        if stats['total_animais_ativos'] > 0:
            stats['custo_medio_animal'] = stats['custo_total_alimentacao'] / stats['total_animais_ativos']
        else:
            stats['custo_medio_animal'] = 0
        
        # Consumo por tipo de ração
        stats['consumo_por_tipo'] = alimentacao_df.groupby('tipo_racao')['quantidade_kg'].sum().to_dict()
    
    # Estatísticas de medicação
    if not medicacao_df.empty:
        stats['total_medicacoes'] = len(medicacao_df)
        stats['medicacoes_individuais'] = len(medicacao_df[medicacao_df['tipo_aplicacao'] == 'Individual'])
        stats['medicacoes_coletivas'] = len(medicacao_df[medicacao_df['tipo_aplicacao'] == 'Coletiva'])
        
        # Medicações por motivo
        stats['medicacoes_por_motivo'] = medicacao_df.groupby('motivo').size().to_dict()
    
    return stats