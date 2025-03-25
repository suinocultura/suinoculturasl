import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import uuid
import os
import sys
import plotly.express as px
import plotly.graph_objects as go

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import (
    load_animals, 
    load_weight_records, 
    save_weight_records, 
    calculate_age,
    load_caliber_scores,
    save_caliber_scores,
    calculate_body_condition
,
    check_permission
)

st.set_page_config(
    page_title="Peso e Idade",
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


# Função auxiliar para validar medidas de calibre
def validate_caliber_measures(p1, p2, p3):
    if any(x <= 0 for x in [p1, p2, p3]):
        return False, "As medidas devem ser maiores que zero."
    if any(x > 50 for x in [p1, p2, p3]):
        return False, "As medidas não devem ultrapassar 50mm."
    return True, ""

# Início da interface
st.title("Controle de Peso e Idade 🐷")
st.write("Registre e acompanhe o peso e idade dos animais.")

# Load existing data
animals_df = load_animals()
weight_df = load_weight_records()
caliber_df = load_caliber_scores()

# Tab for data entry and visualization
tab1, tab2, tab3 = st.tabs(["Registrar Peso", "Análise de Crescimento", "Score Corporal (Calibre)"])

with tab1:
    st.header("Registrar Novo Peso")
    
    if not animals_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            selected_animal = st.selectbox(
                "Selecione o Animal",
                options=animals_df['id_animal'].tolist(),
                format_func=lambda x: f"{animals_df[animals_df['id_animal'] == x]['identificacao'].iloc[0]} - {animals_df[animals_df['id_animal'] == x]['nome'].iloc[0]}" if animals_df[animals_df['id_animal'] == x]['nome'].iloc[0] else animals_df[animals_df['id_animal'] == x]['identificacao'].iloc[0]
            )
            
            # Display animal information
            if selected_animal:
                animal_info = animals_df[animals_df['id_animal'] == selected_animal].iloc[0]
                st.write(f"**Categoria:** {animal_info['categoria']}")
                
                if 'data_nascimento' in animal_info:
                    birth_date = pd.to_datetime(animal_info['data_nascimento']).date()
                    age_days = calculate_age(birth_date)
                    st.write(f"**Idade:** {age_days} dias ({age_days//30} meses)")
                    
                # Display previous weights
                if not weight_df.empty and selected_animal in weight_df['id_animal'].values:
                    animal_weights = weight_df[weight_df['id_animal'] == selected_animal].sort_values('data_registro', ascending=False)
                    
                    if not animal_weights.empty:
                        last_weight = animal_weights.iloc[0]
                        st.write(f"**Último peso registrado:** {last_weight['peso']} kg em {last_weight['data_registro']}")
                        
                        # Calculate weight gain if there's more than one record
                        if len(animal_weights) > 1:
                            previous_weight = animal_weights.iloc[1]
                            weight_diff = last_weight['peso'] - previous_weight['peso']
                            days_diff = (pd.to_datetime(last_weight['data_registro']) - pd.to_datetime(previous_weight['data_registro'])).days
                            
                            if days_diff > 0:
                                daily_gain = weight_diff / days_diff
                                st.write(f"**Ganho diário:** {daily_gain:.2f} kg/dia")
        with col2:
            data_registro = st.date_input(
                "Data do Registro",
                value=datetime.now().date()
            )
            
            peso = st.number_input("Peso (kg)", min_value=0.0, value=0.0, step=0.1)
            observacao = st.text_area("Observações")
        
        # Submit button
        if st.button("Registrar Peso"):
            if peso <= 0:
                st.error("O peso deve ser maior que zero.")
            else:
                # Create new weight record
                new_weight = {
                    'id_registro': str(uuid.uuid4()),
                    'id_animal': selected_animal,
                    'data_registro': data_registro.strftime('%Y-%m-%d'),
                    'peso': peso,
                    'observacao': observacao
                }
                
                # Add to DataFrame
                if weight_df.empty:
                    weight_df = pd.DataFrame([new_weight])
                else:
                    weight_df = pd.concat([weight_df, pd.DataFrame([new_weight])], ignore_index=True)
                
                # Save updated DataFrame
                save_weight_records(weight_df)
                
                st.success(f"Peso registrado com sucesso!")
                st.rerun()
    else:
        st.warning("Não há animais cadastrados no sistema. Cadastre animais primeiro.")

with tab2:
    st.header("Análise de Crescimento")
    
    if not animals_df.empty and not weight_df.empty:
        # Filter options
        filter_col1, filter_col2 = st.columns([1, 2])
        
        with filter_col1:
            filter_category = st.multiselect(
                "Filtrar por Categoria",
                options=animals_df['categoria'].unique().tolist(),
                default=[]
            )
        
        with filter_col2:
            filter_animal = st.multiselect(
                "Filtrar por Animal",
                options=animals_df['id_animal'].tolist(),
                format_func=lambda x: f"{animals_df[animals_df['id_animal'] == x]['identificacao'].iloc[0]} - {animals_df[animals_df['id_animal'] == x]['nome'].iloc[0]}" if animals_df[animals_df['id_animal'] == x]['nome'].iloc[0] else animals_df[animals_df['id_animal'] == x]['identificacao'].iloc[0],
                default=[]
            )
        
        # Prepare data
        merged_df = pd.merge(weight_df, animals_df, on='id_animal')
        
        # Apply filters
        filtered_df = merged_df.copy()
        
        if filter_category:
            filtered_df = filtered_df[filtered_df['categoria'].isin(filter_category)]
            
        if filter_animal:
            filtered_df = filtered_df[filtered_df['id_animal'].isin(filter_animal)]
        
        if not filtered_df.empty:
            # Growth curve
            st.subheader("Curva de Crescimento")
            
            # Convert dates for plotting
            filtered_df['data_registro'] = pd.to_datetime(filtered_df['data_registro'])
            
            # Individual animal weight curve
            if filter_animal and len(filter_animal) <= 5:  # Limit to 5 animals for clarity
                fig = px.line(
                    filtered_df,
                    x='data_registro',
                    y='peso',
                    color='identificacao',
                    markers=True,
                    labels={
                        'data_registro': 'Data',
                        'peso': 'Peso (kg)',
                        'identificacao': 'Animal'
                    },
                    title='Evolução de Peso por Animal'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Average weight by category and age
            st.subheader("Peso Médio por Categoria e Idade")
            
            # Add age information
            filtered_df['data_nascimento'] = pd.to_datetime(filtered_df['data_nascimento'])
            filtered_df['idade_dias'] = filtered_df.apply(
                lambda row: (row['data_registro'] - row['data_nascimento']).days, 
                axis=1
            )
            
            # Group by category and age bracket (monthly)
            filtered_df['idade_meses'] = (filtered_df['idade_dias'] / 30).astype(int)
            
            # Filter out potentially erroneous age data
            age_filtered_df = filtered_df[filtered_df['idade_dias'] >= 0]
            
            if not age_filtered_df.empty:
                avg_by_category_age = age_filtered_df.groupby(['categoria', 'idade_meses'])['peso'].mean().reset_index()
                
                fig = px.line(
                    avg_by_category_age,
                    x='idade_meses',
                    y='peso',
                    color='categoria',
                    markers=True,
                    labels={
                        'idade_meses': 'Idade (meses)',
                        'peso': 'Peso Médio (kg)',
                        'categoria': 'Categoria'
                    },
                    title='Peso Médio por Categoria e Idade'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Weight gain analysis
                st.subheader("Análise de Ganho de Peso")
                
                # Calculate daily weight gain for animals with multiple records
                animal_ids = filtered_df['id_animal'].unique()
                gain_data = []
                
                for animal_id in animal_ids:
                    animal_records = filtered_df[filtered_df['id_animal'] == animal_id].sort_values('data_registro')
                    
                    if len(animal_records) >= 2:
                        for i in range(len(animal_records) - 1):
                            current = animal_records.iloc[i]
                            next_record = animal_records.iloc[i + 1]
                            
                            days_diff = (next_record['data_registro'] - current['data_registro']).days
                            
                            if days_diff > 0:
                                weight_diff = next_record['peso'] - current['peso']
                                daily_gain = weight_diff / days_diff
                                
                                gain_data.append({
                                    'id_animal': animal_id,
                                    'identificacao': current['identificacao'],
                                    'categoria': current['categoria'],
                                    'idade_inicial': current['idade_dias'],
                                    'periodo_dias': days_diff,
                                    'ganho_total': weight_diff,
                                    'ganho_diario': daily_gain
                                })
                
                if gain_data:
                    gain_df = pd.DataFrame(gain_data)
                    
                    # Average daily gain by category
                    st.subheader("Ganho Médio Diário por Categoria")
                    avg_gain_by_category = gain_df.groupby('categoria')['ganho_diario'].mean().reset_index()
                    
                    fig = px.bar(
                        avg_gain_by_category,
                        x='categoria',
                        y='ganho_diario',
                        labels={
                            'categoria': 'Categoria',
                            'ganho_diario': 'Ganho Médio Diário (kg/dia)'
                        },
                        title='Ganho Médio Diário por Categoria'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Top performers
                    st.subheader("Melhores Desempenhos de Ganho de Peso")
                    top_gainers = gain_df.sort_values('ganho_diario', ascending=False).head(10)
                    
                    st.dataframe(
                        top_gainers[[
                            'identificacao', 'categoria', 'idade_inicial', 
                            'periodo_dias', 'ganho_total', 'ganho_diario'
                        ]].rename(columns={
                            'identificacao': 'Identificação',
                            'categoria': 'Categoria',
                            'idade_inicial': 'Idade Inicial (dias)',
                            'periodo_dias': 'Período (dias)',
                            'ganho_total': 'Ganho Total (kg)',
                            'ganho_diario': 'Ganho Diário (kg/dia)'
                        }).style.format({
                            'Ganho Total (kg)': '{:.2f}',
                            'Ganho Diário (kg/dia)': '{:.2f}'
                        }),
                        use_container_width=True
                    )
                else:
                    st.info("Não há dados suficientes para calcular o ganho de peso. Registre mais medições por animal.")
            else:
                st.info("Não há dados válidos de idade para análise.")
            
            # Weight distribution
            st.subheader("Distribuição de Peso por Categoria")
            
            fig = px.box(
                filtered_df,
                x='categoria',
                y='peso',
                labels={
                    'categoria': 'Categoria',
                    'peso': 'Peso (kg)'
                },
                title='Distribuição de Peso por Categoria'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum dado encontrado com os filtros selecionados.")
    else:
        st.info("Não há dados suficientes. Registre animais e seus pesos primeiro.")

with tab3:
    st.header("Medição de Score Corporal com Calibre")

    # Explicação do sistema de calibre
    with st.expander("ℹ️ Como funciona o Score Corporal?", expanded=False):
        st.markdown("""
        ### Sistema de Score Corporal com Calibre

        O score corporal é uma medida importante para avaliar a condição física dos animais.
        São realizadas medições em 3 pontos específicos:

        1. **P1 - Primeira vértebra lombar**
           * Mede a gordura na região lombar
           * Indica reserva energética posterior

        2. **P2 - Última costela**
           * Ponto principal de referência
           * Determina o score final
           * Medida mais importante

        3. **P3 - Última vértebra torácica**
           * Entre a penúltima e última costela
           * Complementa a avaliação

        ### Interpretação do Score
        | Score | Medida P2 | Condição | Ação Recomendada |
        |-------|-----------|----------|------------------|
        | 1 | < 10mm | Muito Magra | Atenção urgente |
        | 2 | 10-13mm | Magra | Aumentar alimentação |
        | 3 | 14-19mm | Ideal | Manter manejo |
        | 4 | 20-25mm | Gorda | Reduzir ração |
        | 5 | > 25mm | Muito Gorda | Dieta restrita |
        """)

        st.image("https://www.vetbizz.com.br/wp-content/uploads/2020/09/medicao-1.jpg",
                 caption="Pontos de medição com calibre",
                 use_column_width=True)

    # Registro de nova medição
    st.subheader("📏 Nova Medição")

    if not animals_df.empty:
        col1, col2 = st.columns(2)

        with col1:
            # Seleção do animal
            selected_animal = st.selectbox(
                "🐷 Selecione o Animal",
                options=animals_df['id_animal'].tolist(),
                format_func=lambda x: f"{animals_df[animals_df['id_animal'] == x]['identificacao'].iloc[0]} ({animals_df[animals_df['id_animal'] == x]['categoria'].iloc[0]})",
                key="caliber_animal"
            )

            if selected_animal:
                animal_info = animals_df[animals_df['id_animal'] == selected_animal].iloc[0]

                # Informações do animal
                with st.container():
                    st.markdown("""
                    <style>
                    .animal-info {
                        background-color: #f0f2f6;
                        padding: 10px;
                        border-radius: 5px;
                        margin: 10px 0;
                    }
                    </style>
                    """, unsafe_allow_html=True)

                    st.markdown('<div class="animal-info">', unsafe_allow_html=True)
                    st.write(f"**🏷️ Categoria:** {animal_info['categoria']}")

                    if 'data_nascimento' in animal_info and pd.notna(animal_info['data_nascimento']):
                        birth_date = pd.to_datetime(animal_info['data_nascimento']).date()
                        age_days = calculate_age(birth_date)
                        st.write(f"**📅 Idade:** {age_days} dias ({age_days//30} meses)")

                    # Último score registrado
                    if not caliber_df.empty and selected_animal in caliber_df['id_animal'].values:
                        last_score = caliber_df[caliber_df['id_animal'] == selected_animal].sort_values('data_medicao', ascending=False).iloc[0]
                        score = last_score['score']

                        # Emoji indicador
                        indicator = {
                            1: "🔴",  # Muito magra
                            2: "🟡",  # Magra
                            3: "🟢",  # Ideal
                            4: "🟡",  # Gorda
                            5: "🔴"   # Muito gorda
                        }.get(score, "⚪")

                        st.write(f"**{indicator} Último Score:** {score}")
                        st.write(f"**📅 Medição anterior:** {pd.to_datetime(last_score['data_medicao']).strftime('%d/%m/%Y')}")
                    st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            # Formulário de medição
            with st.form("form_caliber"):
                st.markdown("### 📏 Medidas")

                data_medicao = st.date_input(
                    "📅 Data da Medição",
                    value=datetime.now().date()
                )

                p1 = st.number_input(
                    "P1 - Primeira vértebra lombar (mm)",
                    min_value=0.0,
                    max_value=50.0,
                    value=15.0,
                    step=0.5,
                    format="%.1f",
                    help="Medida na região lombar"
                )

                p2 = st.number_input(
                    "P2 - Última costela (mm)",
                    min_value=0.0,
                    max_value=50.0,
                    value=16.0,
                    step=0.5,
                    format="%.1f",
                    help="Medida principal para o score"
                )

                p3 = st.number_input(
                    "P3 - Última vértebra torácica (mm)",
                    min_value=0.0,
                    max_value=50.0,
                    value=15.5,
                    step=0.5,
                    format="%.1f",
                    help="Medida complementar"
                )

                # Cálculo do score
                condition, score = calculate_body_condition(p2)

                # Visual do resultado
                col_score1, col_score2 = st.columns(2)
                with col_score1:
                    st.metric("Score", f"{score}/5")
                with col_score2:
                    st.info(f"**Condição:** {condition}")

                tecnico = st.text_input(
                    "👨‍⚕️ Técnico Responsável",
                    help="Nome do responsável pela medição"
                )

                observacao = st.text_area(
                    "📝 Observações",
                    help="Anotações adicionais sobre a medição"
                )

                submitted = st.form_submit_button("✅ Registrar Medição")

                if submitted:
                    valid, message = validate_caliber_measures(p1, p2, p3)

                    if not valid:
                        st.error(message)
                    elif not tecnico:
                        st.error("Por favor, informe o técnico responsável.")
                    else:
                        # Criar novo registro
                        new_score = {
                            'id_score': str(uuid.uuid4()),
                            'id_animal': selected_animal,
                            'data_medicao': data_medicao.strftime('%Y-%m-%d'),
                            'p1': p1,
                            'p2': p2,
                            'p3': p3,
                            'score': score,
                            'condition': condition,
                            'tecnico': tecnico,
                            'observacao': observacao
                        }

                        # Adicionar ao DataFrame
                        if caliber_df.empty:
                            caliber_df = pd.DataFrame([new_score])
                        else:
                            caliber_df = pd.concat([caliber_df, pd.DataFrame([new_score])], ignore_index=True)

                        # Salvar dados
                        save_caliber_scores(caliber_df)

                        st.success(f"✅ Score registrado com sucesso!\nScore: {score} - {condition}")
                        st.rerun()
    else:
        st.warning("⚠️ Não há animais cadastrados. Por favor, cadastre animais primeiro.")

    # Histórico e análise
    if not caliber_df.empty:
        st.markdown("---")
        st.header("📊 Histórico de Medições")

        # Filtros
        col_filter1, col_filter2 = st.columns([1, 2])

        with col_filter1:
            # Filtro por categoria
            merged_df = pd.merge(caliber_df, animals_df, on='id_animal')
            filter_category = st.multiselect(
                "🏷️ Categoria",
                options=sorted(animals_df['categoria'].unique()),
                default=[]
            )

        with col_filter2:
            # Filtro por animal
            filter_animal = st.multiselect(
                "🐷 Animal",
                options=animals_df['id_animal'].tolist(),
                format_func=lambda x: f"{animals_df[animals_df['id_animal'] == x]['identificacao'].iloc[0]} ({animals_df[animals_df['id_animal'] == x]['categoria'].iloc[0]})",
                default=[]
            )

        # Aplicar filtros
        filtered_df = merged_df.copy()

        if filter_category:
            filtered_df = filtered_df[filtered_df['categoria'].isin(filter_category)]

        if filter_animal:
            filtered_df = filtered_df[filtered_df['id_animal'].isin(filter_animal)]

        if not filtered_df.empty:
            # Tabela de histórico
            display_df = filtered_df[[
                'identificacao', 'categoria', 'data_medicao',
                'p1', 'p2', 'p3', 'score', 'condition'
            ]].copy()

            display_df['data_medicao'] = pd.to_datetime(display_df['data_medicao']).dt.strftime('%d/%m/%Y')

            display_df.columns = [
                'Identificação', 'Categoria', 'Data',
                'P1 (mm)', 'P2 (mm)', 'P3 (mm)',
                'Score', 'Condição'
            ]

            st.dataframe(
                display_df.sort_values('Data', ascending=False),
                hide_index=True,
                use_container_width=True
            )

            # Gráficos
            st.subheader("📈 Análise de Scores")

            col1, col2 = st.columns(2)

            with col1:
                # Score por categoria
                fig = px.box(
                    filtered_df,
                    x='categoria',
                    y='score',
                    labels={
                        'categoria': 'Categoria',
                        'score': 'Score (1-5)'
                    },
                    title='Score por Categoria'
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Distribuição de condições
                condition_counts = filtered_df['condition'].value_counts()
                fig = px.pie(
                    values=condition_counts.values,
                    names=condition_counts.index,
                    title='Distribuição de Condições'
                )
                st.plotly_chart(fig, use_container_width=True)

            # Evolução temporal
            if filter_animal and len(filter_animal) <= 5:
                st.subheader("📈 Evolução do Score")

                filtered_df['data_medicao'] = pd.to_datetime(filtered_df['data_medicao'])

                fig = px.line(
                    filtered_df,
                    x='data_medicao',
                    y='score',
                    color='identificacao',
                    markers=True,
                    labels={
                        'data_medicao': 'Data',
                        'score': 'Score',
                        'identificacao': 'Animal'
                    }
                )

                fig.add_hline(y=1, line_dash="dash", line_color="red", annotation_text="Muito Magra")
                fig.add_hline(y=2, line_dash="dash", line_color="orange", annotation_text="Magra")
                fig.add_hline(y=3, line_dash="dash", line_color="green", annotation_text="Ideal")
                fig.add_hline(y=4, line_dash="dash", line_color="orange", annotation_text="Gorda")
                fig.add_hline(y=5, line_dash="dash", line_color="red", annotation_text="Muito Gorda")

                st.plotly_chart(fig, use_container_width=True)

            # Exportar dados
            st.markdown("---")
            if st.button("📥 Exportar Dados"):
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    "📥 Baixar CSV",
                    data=csv,
                    file_name="scores_calibre.csv",
                    mime="text/csv"
                )
        else:
            st.info("Nenhum dado encontrado com os filtros selecionados.")
    else:
        st.info("Não há medições registradas. Utilize o formulário acima para registrar.")