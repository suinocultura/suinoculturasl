import streamlit as st
import pandas as pd
import uuid
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
from utils import (
    load_animals,
    load_maternity,
    save_maternity,
    load_litters,
    save_litters,
    load_piglets,
    save_piglets,
    load_weaning,
    save_weaning,
    load_pens,
    load_pen_allocations,
    save_pen_allocations,
    calculate_weaning_metrics,
    get_available_pens
,
    check_permission
)

# Configuração da página
st.set_page_config(
    page_title="Desmame - Sistema de Gestão de Suinocultura",
    page_icon="🐷",
    layout="wide"
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
if not check_permission(st.session_state.current_user, 'manage_growth'):
    st.error("Você não tem permissão para acessar esta página.")
    st.stop()


# Carregar dados
animals_df = load_animals()
maternity_df = load_maternity()
litters_df = load_litters()
piglets_df = load_piglets()
weaning_df = load_weaning()
pens_df = load_pens()
pen_allocations_df = load_pen_allocations()

# Título da página
st.title("Desmame 🐖")
st.markdown("""
Registre e gerencie o processo de desmame dos leitões, com alocação para creche e retorno das matrizes para gestação.
""")

# Abas para diferentes funcionalidades
tab1, tab2 = st.tabs(["Registrar Desmame", "Histórico e Estatísticas"])

with tab1:
    st.header("Registrar Novo Desmame")
    
    # Obter leitegadas ativas (com leitões vivos e sem desmame registrado)
    leitegadas_ativas = []
    
    if not litters_df.empty and not piglets_df.empty:
        # Verificar quais leitegadas têm leitões vivos
        for _, litter in litters_df.iterrows():
            litter_id = litter['id_leitegada']
            
            # Contar leitões vivos nesta leitegada
            if litter_id in piglets_df['id_leitegada'].values:
                vivos = len(piglets_df[(piglets_df['id_leitegada'] == litter_id) & 
                                       (piglets_df['status_atual'] == 'Vivo')])
                
                # Verificar se já existe desmame para esta leitegada
                desmame_existente = False
                if not weaning_df.empty and litter_id in weaning_df['id_leitegada'].values:
                    desmame_existente = True
                
                if vivos > 0 and not desmame_existente:
                    leitegadas_ativas.append(litter_id)
    
    if not leitegadas_ativas:
        st.warning("Não há leitegadas disponíveis para desmame. Cadastre leitões ou verifique se todas as leitegadas já foram desmamadas.")
    else:
        # Preparar informações para exibição no select
        litters_info = []
        for litter_id in leitegadas_ativas:
            litter_data = litters_df[litters_df['id_leitegada'] == litter_id].iloc[0]
            matriz_id = litter_data['id_animal']
            matriz_info = "Desconhecida"
            
            if not animals_df.empty and matriz_id in animals_df['id_animal'].values:
                matriz_info = animals_df[animals_df['id_animal'] == matriz_id]['identificacao'].iloc[0]
            
            # Contar leitões vivos
            vivos = len(piglets_df[(piglets_df['id_leitegada'] == litter_id) & 
                                  (piglets_df['status_atual'] == 'Vivo')])
            
            # Calcular idade da leitegada
            data_parto = pd.to_datetime(litter_data['data_parto']).date()
            idade_dias = (datetime.now().date() - data_parto).days
            
            litters_info.append({
                'id_leitegada': litter_id,
                'matriz': matriz_info,
                'data_parto': data_parto,
                'idade_dias': idade_dias,
                'vivos': vivos
            })
        
        # Ordenar por idade (mais velhos primeiro)
        litters_info = sorted(litters_info, key=lambda x: x['idade_dias'], reverse=True)
        
        # Selecionar leitegada para desmame
        selected_litter = st.selectbox(
            "Selecione a Leitegada para Desmame",
            options=[l['id_leitegada'] for l in litters_info],
            format_func=lambda x: next(f"Matriz: {l['matriz']} - Parto: {l['data_parto'].strftime('%d/%m/%Y')} - Idade: {l['idade_dias']} dias - Leitões: {l['vivos']}" 
                                      for l in litters_info if l['id_leitegada'] == x)
        )
        
        # Obter detalhes da leitegada selecionada
        selected_info = next(l for l in litters_info if l['id_leitegada'] == selected_litter)
        litter_data = litters_df[litters_df['id_leitegada'] == selected_litter].iloc[0]
        
        # Mostrar detalhes da leitegada
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Matriz", selected_info['matriz'])
        with col2:
            st.metric("Idade dos Leitões", f"{selected_info['idade_dias']} dias")
        with col3:
            st.metric("Leitões Vivos", selected_info['vivos'])
        
        # Formulário de desmame
        st.subheader("Informações do Desmame")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Data do desmame
            data_desmame = st.date_input(
                "Data do Desmame",
                value=datetime.now().date()
            )
            
            # Calcular idade exata ao desmame
            data_parto = pd.to_datetime(litter_data['data_parto']).date()
            idade_desmame = (data_desmame - data_parto).days
            st.write(f"**Idade ao Desmame:** {idade_desmame} dias")
            
            # Total de leitões desmamados
            total_desmamados = st.number_input(
                "Total de Leitões Desmamados",
                min_value=1,
                max_value=selected_info['vivos'],
                value=selected_info['vivos']
            )
            
            # Peso total ao desmame
            peso_total = st.number_input(
                "Peso Total dos Leitões (kg)",
                min_value=1.0,
                max_value=500.0,
                value=float(total_desmamados * 6.0),  # Estimativa de 6kg por leitão
                step=0.5,
                format="%.1f"
            )
            
            # Calcular peso médio
            peso_medio = peso_total / total_desmamados if total_desmamados > 0 else 0
            st.metric("Peso Médio por Leitão (kg)", round(peso_medio, 2))
            
            # Ganho médio diário
            # Obter peso médio ao nascer
            peso_nascer = litter_data['peso_medio']
            ganho_diario = ((peso_medio - peso_nascer) * 1000) / idade_desmame if idade_desmame > 0 else 0
            st.metric("Ganho Médio Diário (g/dia)", round(ganho_diario))
        
        with col2:
            # Destino dos leitões
            destino_leitoes = st.selectbox(
                "Destino dos Leitões",
                options=["Creche", "Venda", "Outro"]
            )
            
            # Baia de destino (se for Creche)
            id_baia_destino = None
            if destino_leitoes == "Creche":
                # Filtrar baias de creche disponíveis
                creche_pens = pens_df[pens_df['setor'] == 'Creche'] if not pens_df.empty else pd.DataFrame()
                
                if creche_pens.empty:
                    st.error("Não há baias de creche cadastradas. Por favor, cadastre uma baia no setor 'Creche' primeiro.")
                else:
                    available_pens = get_available_pens(creche_pens, pen_allocations_df, 'Leitão')
                    
                    if available_pens.empty:
                        st.error("Não há baias de creche disponíveis no momento.")
                    else:
                        # Verificar capacidade disponível
                        for _, pen in available_pens.iterrows():
                            if pen['vagas_disponiveis'] >= total_desmamados:
                                id_baia_destino = st.selectbox(
                                    "Baia de Destino na Creche",
                                    options=available_pens['id_baia'].tolist(),
                                    format_func=lambda x: f"{available_pens[available_pens['id_baia'] == x]['identificacao'].iloc[0]} ({available_pens[available_pens['id_baia'] == x]['ocupacao_atual'].iloc[0]}/{available_pens[available_pens['id_baia'] == x]['capacidade'].iloc[0]} ocupada)"
                                )
                                break
                        
                        if id_baia_destino is None:
                            st.error(f"Não há baias com capacidade para {total_desmamados} leitões. Considere dividir o lote ou liberar espaço nas baias existentes.")
            
            # Destino da matriz
            destino_matriz = st.selectbox(
                "Destino da Matriz",
                options=["Gestação", "Descarte", "Outro"]
            )
            
            # Observações
            observacao = st.text_area(
                "Observações",
                placeholder="Informações adicionais sobre o desmame...",
                height=122
            )
        
        # Botão para confirmar desmame
        pode_desmamar = (destino_leitoes != "Creche" or id_baia_destino is not None)
        
        if st.button("Registrar Desmame", disabled=not pode_desmamar):
            # 1. Criar registro de desmame
            id_desmame = str(uuid.uuid4())
            
            novo_desmame = {
                'id_desmame': id_desmame,
                'id_leitegada': selected_litter,
                'id_animal_mae': litter_data['id_animal'],
                'data_desmame': data_desmame.strftime('%Y-%m-%d'),
                'idade_desmame': idade_desmame,
                'total_desmamados': total_desmamados,
                'peso_total_desmame': peso_total,
                'peso_medio_desmame': peso_medio,
                'ganho_medio_diario': ganho_diario,
                'destino_leitoes': destino_leitoes,
                'destino_matriz': destino_matriz,
                'id_baia_destino': id_baia_destino,
                'observacao': observacao
            }
            
            # Adicionar ao DataFrame
            if weaning_df.empty:
                weaning_df = pd.DataFrame([novo_desmame])
            else:
                weaning_df = pd.concat([weaning_df, pd.DataFrame([novo_desmame])], ignore_index=True)
            
            # Salvar DataFrame atualizado
            save_weaning(weaning_df)
            
            # 2. Atualizar status dos leitões
            if not piglets_df.empty:
                litter_piglets = piglets_df[(piglets_df['id_leitegada'] == selected_litter) & 
                                           (piglets_df['status_atual'] == 'Vivo')]
                
                # Limitar ao número de leitões desmamados
                piglets_to_update = litter_piglets.head(total_desmamados)
                
                # Atualizar status para "Desmamado"
                for idx in piglets_to_update.index:
                    piglets_df.loc[idx, 'status_atual'] = 'Desmamado'
                    piglets_df.loc[idx, 'data_status'] = data_desmame.strftime('%Y-%m-%d')
                    
                    # Adicionar à observação existente
                    atual_obs = piglets_df.loc[idx, 'observacao']
                    nova_obs = f"{atual_obs}\nDesmamado em {data_desmame.strftime('%d/%m/%Y')} com peso de {peso_medio:.2f} kg" if atual_obs else f"Desmamado em {data_desmame.strftime('%d/%m/%Y')} com peso de {peso_medio:.2f} kg"
                    piglets_df.loc[idx, 'observacao'] = nova_obs
                
                # Salvar DataFrame atualizado
                save_piglets(piglets_df)
            
            # 3. Finalizar maternidade para a matriz
            if not maternity_df.empty:
                # Encontrar a entrada de maternidade correspondente
                maternity_id = litter_data['id_maternidade'] if 'id_maternidade' in litter_data else None
                
                if maternity_id and maternity_id in maternity_df['id_maternidade'].values:
                    # Marcar como finalizada
                    maternity_df.loc[maternity_df['id_maternidade'] == maternity_id, 'data_saida'] = data_desmame.strftime('%Y-%m-%d')
                    maternity_df.loc[maternity_df['id_maternidade'] == maternity_id, 'status'] = 'Finalizada'
                    
                    # Atualizar observação
                    current_obs = maternity_df.loc[maternity_df['id_maternidade'] == maternity_id, 'observacao'].iloc[0]
                    new_obs = f"{current_obs}\nSaída por desmame em {data_desmame.strftime('%d/%m/%Y')}" if current_obs else f"Saída por desmame em {data_desmame.strftime('%d/%m/%Y')}"
                    maternity_df.loc[maternity_df['id_maternidade'] == maternity_id, 'observacao'] = new_obs
                    
                    # Salvar DataFrame atualizado
                    save_maternity(maternity_df)
                    
                    # 4. Atualizar categoria da matriz
                    matriz_id = litter_data['id_animal']
                    if matriz_id in animals_df['id_animal'].values:
                        animals_df.loc[animals_df['id_animal'] == matriz_id, 'categoria'] = 'Matriz'
                        
                    # 5. Atualizar alocação de baia para a matriz (finalizar)
                    if not pen_allocations_df.empty:
                        # Encontrar alocação ativa da matriz
                        matriz_alocacoes = pen_allocations_df[(pen_allocations_df['id_animal'] == matriz_id) & 
                                                              (pen_allocations_df['data_saida'].isna())]
                        
                        if not matriz_alocacoes.empty:
                            for idx in matriz_alocacoes.index:
                                pen_allocations_df.loc[idx, 'data_saida'] = data_desmame.strftime('%Y-%m-%d')
                                pen_allocations_df.loc[idx, 'motivo_saida'] = 'Desmame'
                                pen_allocations_df.loc[idx, 'status'] = 'Inativo'
                                
                                # Atualizar observação
                                current_pen_obs = pen_allocations_df.loc[idx, 'observacao']
                                new_pen_obs = f"{current_pen_obs}\nSaída por desmame em {data_desmame.strftime('%d/%m/%Y')}" if current_pen_obs else f"Saída por desmame em {data_desmame.strftime('%d/%m/%Y')}"
                                pen_allocations_df.loc[idx, 'observacao'] = new_pen_obs
                            
                            # Salvar DataFrame atualizado
                            save_pen_allocations(pen_allocations_df)
                
            # 6. Se os leitões forem para creche, criar alocação de baia para eles
            if destino_leitoes == "Creche" and id_baia_destino:
                # Criar uma única alocação para o lote de leitões
                nova_alocacao = {
                    'id_alocacao': str(uuid.uuid4()),
                    'id_baia': id_baia_destino,
                    'id_animal': None,  # Não é um animal específico, é um lote
                    'data_entrada': data_desmame.strftime('%Y-%m-%d'),
                    'data_saida': None,
                    'motivo_saida': None,
                    'status': 'Ativo',
                    'observacao': f"Lote de {total_desmamados} leitões desmamados - Leitegada ID: {selected_litter}"
                }
                
                # Adicionar ao DataFrame de alocações
                if pen_allocations_df.empty:
                    pen_allocations_df = pd.DataFrame([nova_alocacao])
                else:
                    pen_allocations_df = pd.concat([pen_allocations_df, pd.DataFrame([nova_alocacao])], ignore_index=True)
                
                # Salvar DataFrame atualizado
                save_pen_allocations(pen_allocations_df)
            
            st.success("Desmame registrado com sucesso!")
            st.rerun()

with tab2:
    st.header("Histórico de Desmames e Estatísticas")
    
    if weaning_df.empty:
        st.info("Ainda não há registros de desmame. Utilize a aba 'Registrar Desmame' para criar o primeiro registro.")
    else:
        # Preparar dados para visualização
        display_weaning = weaning_df.copy()
        display_weaning['data_desmame'] = pd.to_datetime(display_weaning['data_desmame'])
        
        # Adicionar informação da matriz
        if not animals_df.empty:
            display_weaning['matriz'] = display_weaning['id_animal_mae'].apply(
                lambda x: animals_df[animals_df['id_animal'] == x]['identificacao'].iloc[0] 
                if x in animals_df['id_animal'].values else "Desconhecida"
            )
        else:
            display_weaning['matriz'] = "Desconhecida"
        
        # Métricas gerais
        st.subheader("Métricas de Desmame")
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Total de desmames
        total_desmames = len(display_weaning)
        
        # Média de idade ao desmame
        idade_media = display_weaning['idade_desmame'].mean()
        
        # Média de peso ao desmame
        peso_medio = display_weaning['peso_medio_desmame'].mean()
        
        # Média de ganho diário
        ganho_medio = display_weaning['ganho_medio_diario'].mean()
        
        with col1:
            st.metric("Total de Desmames", total_desmames)
            
        with col2:
            st.metric("Idade Média (dias)", f"{idade_media:.1f}")
            
        with col3:
            st.metric("Peso Médio (kg)", f"{peso_medio:.2f}")
            
        with col4:
            st.metric("Ganho Médio (g/dia)", f"{ganho_medio:.0f}")
        
        # Gráficos e análises
        col1, col2 = st.columns(2)
        
        with col1:
            # Evolução do peso ao desmame
            st.subheader("Evolução do Peso ao Desmame")
            
            fig = px.line(
                display_weaning.sort_values('data_desmame'),
                x='data_desmame',
                y='peso_medio_desmame',
                markers=True,
                labels={
                    'data_desmame': 'Data do Desmame',
                    'peso_medio_desmame': 'Peso Médio (kg)'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Relação entre idade e peso ao desmame
            st.subheader("Relação Idade x Peso ao Desmame")
            
            fig = px.scatter(
                display_weaning,
                x='idade_desmame',
                y='peso_medio_desmame',
                color='ganho_medio_diario',
                size='total_desmamados',
                hover_name='matriz',
                labels={
                    'idade_desmame': 'Idade ao Desmame (dias)',
                    'peso_medio_desmame': 'Peso Médio (kg)',
                    'ganho_medio_diario': 'GMD (g/dia)',
                    'total_desmamados': 'Leitões Desmamados'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Tabela de histórico de desmames
        st.subheader("Histórico de Desmames")
        
        # Formatar para exibição
        display_df = display_weaning[[
            'matriz', 'data_desmame', 'idade_desmame', 'total_desmamados',
            'peso_medio_desmame', 'ganho_medio_diario', 'destino_leitoes'
        ]].copy()
        
        display_df['data_desmame'] = display_df['data_desmame'].dt.strftime('%d/%m/%Y')
        
        st.dataframe(
            display_df.rename(columns={
                'matriz': 'Matriz',
                'data_desmame': 'Data do Desmame',
                'idade_desmame': 'Idade (dias)',
                'total_desmamados': 'Leitões Desmamados',
                'peso_medio_desmame': 'Peso Médio (kg)',
                'ganho_medio_diario': 'GMD (g/dia)',
                'destino_leitoes': 'Destino dos Leitões'
            }).sort_values('Data do Desmame', ascending=False),
            use_container_width=True,
            hide_index=True
        )
        
        # Exportar dados
        if st.button("Exportar Dados de Desmame (CSV)"):
            csv = display_weaning.to_csv(index=False)
            st.download_button(
                label="Baixar CSV",
                data=csv,
                file_name=f"desmames_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )