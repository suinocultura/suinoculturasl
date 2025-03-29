import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import base64
import os
import sys

# Configurações da página
st.set_page_config(
    page_title="Início | Sistema Suinocultura",
    page_icon="🏠",
    layout="wide"
)

# Definição de cores para tema escuro moderno
bg_primary = "#1A1A24"
bg_secondary = "#0E1117" 
text_color = "#FAFAFA"
text_muted = "#B8B8C7"
card_bg = "#23232F"
card_border = "#33334B"
section_bg = "#23232F"
stats_bg = "#2A2A38"

# Cores do sistema
primary_color = "#6BCB77"  # Verde mais moderno
secondary_color = "#4D96FF"  # Azul
accent_color = "#FF6B6B"  # Vermelho/Rosa
highlight_color = "#FFD166"  # Amarelo/Dourado
purple_color = "#9C6ADE"  # Roxo

st.markdown(f"""
<style>
    /* Estilos base e tipografia */
    .main-title {{
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, {primary_color}, {secondary_color});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
        text-align: center;
        letter-spacing: -0.5px;
    }}
    
    .subtitle {{
        font-size: 1.5rem;
        color: {text_muted};
        margin-bottom: 2rem;
        text-align: center;
        font-weight: 300;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
    }}
    
    /* Seções e containers */
    .header-section {{
        padding: 3rem 2rem;
        background: linear-gradient(145deg, {bg_primary}, {section_bg});
        border-radius: 16px;
        margin-bottom: 3rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        text-align: center;
        border: 1px solid {card_border};
    }}
    
    /* Cards e elementos interativos */
    .feature-card {{
        background: linear-gradient(145deg, {card_bg}, {bg_primary});
        border-radius: 16px;
        padding: 1.8rem;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
        height: 100%;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border: 1px solid {card_border};
        position: relative;
        overflow: hidden;
    }}
    
    .feature-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, {primary_color}, {secondary_color});
    }}
    
    .feature-card:hover {{
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 15px 30px rgba(0, 0, 0, 0.25);
        border-color: rgba(107, 203, 119, 0.5);
    }}
    
    .feature-title {{
        font-size: 1.3rem;
        font-weight: 700;
        color: {primary_color};
        margin-bottom: 0.8rem;
    }}
    
    .feature-icon {{
        font-size: 2.5rem;
        margin-bottom: 1.2rem;
        background: linear-gradient(135deg, {primary_color}, {secondary_color});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline-block;
    }}
    
    /* Títulos e cabeçalhos */
    .section-title {{
        font-size: 2.2rem;
        font-weight: 700;
        color: {text_color};
        margin: 2.5rem 0 1.8rem 0;
        padding-bottom: 0.8rem;
        position: relative;
        text-align: center;
    }}
    
    .section-title::after {{
        content: '';
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 100px;
        height: 4px;
        background: linear-gradient(90deg, {primary_color}, {secondary_color});
        border-radius: 2px;
    }}
    
    /* Cards de estatísticas */
    .stats-card {{
        background: linear-gradient(145deg, {stats_bg}, {card_bg});
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        height: 100%;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
        border: 1px solid {card_border};
        transition: all 0.3s ease;
    }}
    
    .stats-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
    }}
    
    .stats-number {{
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, {primary_color}, {secondary_color});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.1;
        margin-bottom: 0.5rem;
    }}
    
    .stats-label {{
        font-size: 1.1rem;
        color: {text_muted};
        font-weight: 500;
    }}
    
    /* Seções de rodapé e categorias */
    .footer-section {{
        margin-top: 4rem;
        padding: 2rem;
        background: linear-gradient(145deg, {bg_primary}, {section_bg});
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        border: 1px solid {card_border};
    }}
    
    .category-section {{
        margin-top: 2.5rem;
        padding: 2rem;
        background: linear-gradient(145deg, {section_bg}, {bg_primary});
        border-radius: 16px;
        margin-bottom: 2.5rem;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
        border: 1px solid {card_border};
    }}
    
    /* Cards de módulos */
    .module-card {{
        background: linear-gradient(145deg, {card_bg}, {bg_primary});
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
        margin-bottom: 1.2rem;
        position: relative;
        border: 1px solid {card_border};
        transition: all 0.3s ease;
        overflow: hidden;
    }}
    
    .module-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 5px;
        height: 100%;
        background-color: #4F8A10;
    }}
    
    .module-card:hover {{
        transform: translateX(5px);
        box-shadow: 0 12px 20px rgba(0, 0, 0, 0.2);
    }}
    
    /* Outros elementos */
    .screenshot-container {{
        border: 1px solid {card_border};
        border-radius: 16px;
        overflow: hidden;
        margin: 1.5rem 0;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
    }}
    
    .benefits-list li {{
        margin-bottom: 1rem;
        padding-left: 2rem;
        position: relative;
        font-size: 1.05rem;
    }}
    
    .benefits-list li:before {{
        content: '\\2713';
        color: {primary_color};
        position: absolute;
        left: 0;
        font-weight: bold;
        font-size: 1.2rem;
    }}
    
    /* Cores para áreas diferentes */
    .admin-color {{ 
        color: {secondary_color}; 
        border-color: {secondary_color} !important; 
    }}
    .admin-color::before {{ background-color: {secondary_color} !important; }}
    
    .repro-color {{ 
        color: {accent_color}; 
        border-color: {accent_color} !important; 
    }}
    .repro-color::before {{ background-color: {accent_color} !important; }}
    
    .cresc-color {{ 
        color: {purple_color}; 
        border-color: {purple_color} !important; 
    }}
    .cresc-color::before {{ background-color: {purple_color} !important; }}
    
    .saude-color {{ 
        color: {primary_color}; 
        border-color: {primary_color} !important; 
    }}
    .saude-color::before {{ background-color: {primary_color} !important; }}
    
    .gestao-color {{ 
        color: {highlight_color}; 
        border-color: {highlight_color} !important; 
    }}
    .gestao-color::before {{ background-color: {highlight_color} !important; }}
    
    /* Depoimentos */
    .testimonial {{
        font-style: italic;
        background: linear-gradient(145deg, {section_bg}, {card_bg});
        padding: 2rem;
        border-radius: 16px;
        position: relative;
        margin: 3rem 0;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
        border: 1px solid {card_border};
    }}
    
    .testimonial:before {{
        content: '\\"\\"\\"';
        position: absolute;
        top: -30px;
        left: 20px;
        font-size: 4rem;
        background: linear-gradient(135deg, {primary_color}, {secondary_color});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        opacity: 0.7;
    }}
    
    /* Cards de guia */
    .guide-card {{
        background: linear-gradient(145deg, #2A3B17, #1F2A10);
        border-radius: 16px;
        padding: 1.8rem;
        margin: 1.5rem 0;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
        border: 1px solid #3A4F1F;
        position: relative;
        overflow: hidden;
    }}
    
    .guide-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 5px;
        height: 100%;
        background-color: #689f38;
    }}
    
    /* Melhorias gerais */
    p, li {{
        font-size: 1.05rem;
        line-height: 1.6;
    }}
    
    /* Efeito de destaque para textos */
    .highlight-text {{
        background: linear-gradient(90deg, {primary_color}, {secondary_color});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }}
</style>


""", unsafe_allow_html=True)



# Cabeçalho da página com elementos mais modernos
st.markdown('<div class="header-section">', unsafe_allow_html=True)
st.markdown('<h1 class="main-title">Sistema Suinocultura</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Plataforma completa para gestão moderna de granjas suinícolas</p>', unsafe_allow_html=True)

# Badge de versão moderna
st.markdown(f'''
<div style="display: flex; justify-content: center; margin-bottom: 2rem;">
    <div style="background: linear-gradient(90deg, {primary_color}, {secondary_color}); 
                border-radius: 50px; padding: 8px 16px; 
                box-shadow: 0 5px 15px rgba(0,0,0,0.15);">
        <span style="color: white; font-weight: 600; font-size: 0.9rem;">Versão 2025.3 ⚡</span>
    </div>
</div>
''', unsafe_allow_html=True)

# Breve introdução com destaque
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown(f"""
    <div style="line-height: 1.8; font-size: 1.15rem;">
    O <span class="highlight-text">Sistema Suinocultura</span> é uma solução abrangente projetada especialmente para o 
    <strong>gerenciamento eficiente de operações em granjas suinícolas</strong>. 
    <br/><br/>
    Desenvolvido com <span style="color: {secondary_color}; font-weight: 600;">tecnologia moderna</span> e uma 
    <span style="color: {accent_color}; font-weight: 600;">interface intuitiva</span>, 
    o sistema oferece ferramentas poderosas para todas as etapas da produção suína, desde o cadastro de animais 
    até análises detalhadas de produtividade e saúde do rebanho.
    </div>
    """, unsafe_allow_html=True)

# Adicionar botões de ação ilustrativos (não funcionais na página de apresentação)
st.markdown(f'''
<div style="display: flex; justify-content: center; gap: 20px; margin-top: 1.5rem; margin-bottom: 1rem;">
    <div style="background: {primary_color}; 
                border-radius: 50px; padding: 10px 24px; 
                box-shadow: 0 5px 15px rgba(0,0,0,0.15); cursor: pointer;
                transition: all 0.3s ease;">
        <span style="color: white; font-weight: 600; font-size: 1rem;">Conhecer Módulos</span>
    </div>
    <div style="background: transparent; border: 2px solid {secondary_color}; 
                border-radius: 50px; padding: 10px 24px; 
                box-shadow: 0 5px 15px rgba(0,0,0,0.1); cursor: pointer;
                transition: all 0.3s ease;">
        <span style="color: {secondary_color}; font-weight: 600; font-size: 1rem;">Download App</span>
    </div>
</div>
''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Seção de estatísticas aprimorada
st.markdown(f'''
<div style="margin: 3rem 0;">
    <h2 class="section-title">Estatísticas do Sistema</h2>
    <p style="text-align: center; max-width: 700px; margin: 0 auto 2rem auto; color: {text_muted}; font-size: 1.1rem;">
        Conheça os números que destacam a abrangência e o poder do Sistema Suinocultura em transformar a gestão de sua granja.
    </p>
</div>
''', unsafe_allow_html=True)

# Adicionando ícones modernos para os cartões de estatísticas
stat1, stat2, stat3, stat4 = st.columns(4)

# Estatística 1 com ícone
with stat1:
    st.markdown(f'''
    <div class="stats-card">
        <div style="margin-bottom: 15px; font-size: 2rem; background: linear-gradient(120deg, {primary_color}, {secondary_color}); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            <span style="font-size: 1.8rem;">📊</span>
        </div>
        <div class="stats-number">27+</div>
        <div class="stats-label">Módulos Especializados</div>
    </div>
    ''', unsafe_allow_html=True)

# Estatística 2 com ícone
with stat2:
    st.markdown(f'''
    <div class="stats-card">
        <div style="margin-bottom: 15px; font-size: 2rem; background: linear-gradient(120deg, {primary_color}, {secondary_color}); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            <span style="font-size: 1.8rem;">⚙️</span>
        </div>
        <div class="stats-number">100%</div>
        <div class="stats-label">Ciclo de Produção Coberto</div>
    </div>
    ''', unsafe_allow_html=True)

# Estatística 3 com ícone
with stat3:
    st.markdown(f'''
    <div class="stats-card">
        <div style="margin-bottom: 15px; font-size: 2rem; background: linear-gradient(120deg, {primary_color}, {secondary_color}); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            <span style="font-size: 1.8rem;">🔍</span>
        </div>
        <div class="stats-number">5</div>
        <div class="stats-label">Categorias Principais</div>
    </div>
    ''', unsafe_allow_html=True)

# Estatística 4 com ícone
with stat4:
    st.markdown(f'''
    <div class="stats-card">
        <div style="margin-bottom: 15px; font-size: 2rem; background: linear-gradient(120deg, {primary_color}, {secondary_color}); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            <span style="font-size: 1.8rem;">📱</span>
        </div>
        <div class="stats-number">2</div>
        <div class="stats-label">Plataformas (Web + Mobile)</div>
    </div>
    ''', unsafe_allow_html=True)

# Seção de recursos principais modernizada
st.markdown(f'''
<div style="margin: 4rem 0 2rem 0;">
    <h2 class="section-title">Principais Recursos</h2>
    <p style="text-align: center; max-width: 700px; margin: 0 auto 2rem auto; color: {text_muted}; font-size: 1.1rem;">
        Conheça as ferramentas poderosas que irão transformar a gestão da sua granja e otimizar seus resultados.
    </p>
</div>
''', unsafe_allow_html=True)

# Primeira linha de recursos com design aprimorado
feat1, feat2, feat3 = st.columns(3)

with feat1:
    st.markdown(f'''
    <div class="feature-card">
        <div class="feature-icon">📊</div>
        <div class="feature-title">Gestão Completa</div>
        <p style="font-size: 1rem; line-height: 1.5; color: {text_color};">
            Controle total sobre todos os aspectos da produção suinícola, desde o manejo de 
            animais até a análise detalhada de <strong>indicadores de desempenho</strong>.
        </p>
        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid {card_border};">
            <span style="font-size: 0.9rem; color: {secondary_color}; font-weight: 500;">Explorar recurso →</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)

with feat2:
    st.markdown(f'''
    <div class="feature-card">
        <div class="feature-icon">🔄</div>
        <div class="feature-title">Ciclo Reprodutivo</div>
        <p style="font-size: 1rem; line-height: 1.5; color: {text_color};">
            Monitoramento completo do ciclo reprodutivo, incluindo <strong>detecção de cio</strong>, inseminação, 
            gestação e maternidade com alertas automáticos.
        </p>
        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid {card_border};">
            <span style="font-size: 0.9rem; color: {accent_color}; font-weight: 500;">Explorar recurso →</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)

with feat3:
    st.markdown(f'''
    <div class="feature-card">
        <div class="feature-icon">📱</div>
        <div class="feature-title">Acesso Mobile</div>
        <p style="font-size: 1rem; line-height: 1.5; color: {text_color};">
            Acesse o sistema em qualquer lugar através do <strong>aplicativo mobile</strong>, permitindo 
            registros e consultas diretamente no campo.
        </p>
        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid {card_border};">
            <span style="font-size: 0.9rem; color: {purple_color}; font-weight: 500;">Explorar recurso →</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)

# Segunda linha de recursos com design aprimorado
feat4, feat5, feat6 = st.columns(3)

with feat4:
    st.markdown(f'''
    <div class="feature-card">
        <div class="feature-icon">🔍</div>
        <div class="feature-title">Rastreabilidade Total</div>
        <p style="font-size: 1rem; line-height: 1.5; color: {text_color};">
            Acompanhamento individual de cada animal do nascimento ao abate, com <strong>histórico completo</strong> 
            de saúde, reprodução e crescimento.
        </p>
        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid {card_border};">
            <span style="font-size: 0.9rem; color: {primary_color}; font-weight: 500;">Explorar recurso →</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)

with feat5:
    st.markdown(f'''
    <div class="feature-card">
        <div class="feature-icon">🏥</div>
        <div class="feature-title">Controle Sanitário</div>
        <p style="font-size: 1rem; line-height: 1.5; color: {text_color};">
            Gestão de vacinas, medicamentos e protocolos sanitários com <strong>calendário 
            inteligente</strong> e alertas automáticos.
        </p>
        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid {card_border};">
            <span style="font-size: 0.9rem; color: {highlight_color}; font-weight: 500;">Explorar recurso →</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)

with feat6:
    st.markdown(f'''
    <div class="feature-card">
        <div class="feature-icon">🔐</div>
        <div class="feature-title">Sistema de Permissões</div>
        <p style="font-size: 1rem; line-height: 1.5; color: {text_color};">
            Controle de acesso baseado em funções, garantindo que cada usuário 
            acesse apenas as <strong>informações relevantes</strong>.
        </p>
        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid {card_border};">
            <span style="font-size: 0.9rem; color: {secondary_color}; font-weight: 500;">Explorar recurso →</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)

# Módulos e categorias
st.markdown('<h2 class="section-title">Módulos do Sistema</h2>', unsafe_allow_html=True)

# Seção Administração
st.markdown('<div class="category-section">', unsafe_allow_html=True)
st.markdown('<h3 style="color: #1E88E5;">🔹 ADMINISTRAÇÃO</h3>', unsafe_allow_html=True)
st.markdown("""
Esta categoria contém os módulos relacionados à gestão administrativa da granja, 
incluindo controle de usuários, configurações e cadastro básico de animais.
""")

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="module-card admin-color">', unsafe_allow_html=True)
    st.markdown('#### 🔧 Administração')
    st.markdown("""
    Módulo para configurações gerais do sistema, incluindo:
    - Parâmetros globais da granja
    - Configuração do calendário suíno
    - Personalização da interface
    - Gerenciamento de backups
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="module-card admin-color">', unsafe_allow_html=True)
    st.markdown('#### 🐷 Cadastro Animal')
    st.markdown("""
    Gerenciamento completo do cadastro de animais:
    - Registro de novos animais com identificação única
    - Integração com sistemas de brincos/chips eletrônicos
    - Controle de genealogia e linhagens genéticas
    - Histórico completo por animal
    """)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="module-card admin-color">', unsafe_allow_html=True)
    st.markdown('#### 👥 Colaboradores')
    st.markdown("""
    Controle de usuários e permissões do sistema:
    - Cadastro de funcionários e usuários
    - Definição de papéis e responsabilidades
    - Sistema avançado de permissões por módulo
    - Registro de atividades por usuário
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
st.markdown('</div>', unsafe_allow_html=True)

# Seção Reprodução
st.markdown('<div class="category-section">', unsafe_allow_html=True)
st.markdown('<h3 style="color: #D81B60;">🔹 REPRODUÇÃO</h3>', unsafe_allow_html=True)
st.markdown("""
Categoria que engloba todos os módulos relacionados ao ciclo reprodutivo dos suínos, 
desde a detecção de cio até a maternidade.
""")

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="module-card repro-color">', unsafe_allow_html=True)
    st.markdown('#### 🔄 Ciclo Reprodutivo')
    st.markdown("""
    Visão geral e gestão do ciclo reprodutivo:
    - Acompanhamento das fases do ciclo reprodutivo
    - Painel visual com status de cada matriz
    - Previsão de eventos reprodutivos importantes
    - Gestão de grupos de matrizes
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="module-card repro-color">', unsafe_allow_html=True)
    st.markdown('#### 💉 Inseminação')
    st.markdown("""
    Controle do processo de inseminação artificial:
    - Programação de inseminações
    - Registro de doses de sêmen utilizadas
    - Associação com reprodutores/centrais de IA
    - Análise de taxas de sucesso por técnica/reprodutor
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="module-card repro-color">', unsafe_allow_html=True)
    st.markdown('#### 🐗 Rufia')
    st.markdown("""
    Gerenciamento da detecção de cio com rufião:
    - Programação de passagens do rufião
    - Registro de detecções e sintomas de cio
    - Histórico de manifestações de cio
    - Alertas para matrizes que não manifestaram cio
    """)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="module-card repro-color">', unsafe_allow_html=True)
    st.markdown('#### 🤰 Gestação')
    st.markdown("""
    Acompanhamento completo da gestação:
    - Confirmação de prenhez
    - Monitoramento do desenvolvimento fetal
    - Registro de ocorrências na gestação
    - Previsão de partos com alertas
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="module-card repro-color">', unsafe_allow_html=True)
    st.markdown('#### 🔍 Irmãs Cio')
    st.markdown("""
    Ferramenta para identificação de matrizes relacionadas em cio:
    - Análise de padrões de cio por linhagem
    - Identificação de grupos genéticos com sincronização
    - Planejamento de inseminação em grupo
    - Comparativo de desempenho reprodutivo entre irmãs
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
st.markdown('</div>', unsafe_allow_html=True)

# Seção Crescimento
st.markdown('<div class="category-section">', unsafe_allow_html=True)
st.markdown('<h3 style="color: #8E24AA;">🔹 CRESCIMENTO</h3>', unsafe_allow_html=True)
st.markdown("""
Nesta categoria encontram-se todos os módulos relacionados ao desenvolvimento físico dos animais, 
incluindo controle de peso, alojamento e fases específicas como creche e desmame.
""")

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="module-card cresc-color">', unsafe_allow_html=True)
    st.markdown('#### ⚖️ Peso/Idade')
    st.markdown("""
    Monitoramento do desenvolvimento físico:
    - Registro de pesagens periódicas
    - Cálculo de ganho médio diário
    - Comparativo com tabelas de referência
    - Gráficos evolutivos de peso por idade
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="module-card cresc-color">', unsafe_allow_html=True)
    st.markdown('#### 👪 Maternidade')
    st.markdown("""
    Gestão completa da fase de maternidade:
    - Registro de partos com detalhes
    - Acompanhamento de leitões por leitegada
    - Controle de mamada e peso dos leitões
    - Tratamentos e ocorrências na maternidade
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="module-card cresc-color">', unsafe_allow_html=True)
    st.markdown('#### 🏫 Creche')
    st.markdown("""
    Controle da fase de creche:
    - Formação de lotes de desmamados
    - Monitoramento de uniformidade
    - Registro de consumo alimentar
    - Avaliação de desempenho por lote
    """)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="module-card cresc-color">', unsafe_allow_html=True)
    st.markdown('#### 🏠 Baias')
    st.markdown("""
    Gerenciamento de instalações e alojamentos:
    - Cadastro de instalações da granja
    - Controle de ocupação de baias
    - Histórico de alojamento por animal
    - Planejamento de transferências
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="module-card cresc-color">', unsafe_allow_html=True)
    st.markdown('#### 🐽 Desmame')
    st.markdown("""
    Controle do processo de desmame:
    - Programação de desmames
    - Registro de pesos ao desmame
    - Formação de lotes uniformes
    - Indicadores de eficiência da lactação
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="module-card cresc-color">', unsafe_allow_html=True)
    st.markdown('#### ✅ Seleção Leitoas')
    st.markdown("""
    Processo de seleção de futuras matrizes:
    - Critérios de seleção personalizáveis
    - Avaliação morfológica e genética
    - Registro de características desejáveis
    - Classificação e ranking de candidatas
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
st.markdown('</div>', unsafe_allow_html=True)

# Seção Saúde
st.markdown('<div class="category-section">', unsafe_allow_html=True)
st.markdown('<h3 style="color: #43A047;">🔹 SAÚDE</h3>', unsafe_allow_html=True)
st.markdown("""
Categoria dedicada ao controle sanitário e saúde do rebanho, incluindo vacinações, tratamentos e registro de mortalidade.
""")

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="module-card saude-color">', unsafe_allow_html=True)
    st.markdown('#### 💉 Vacinas')
    st.markdown("""
    Gerenciamento completo de vacinações:
    - Protocolo de vacinação por categoria
    - Registro de aplicações e doses
    - Calendário automatizado de vacinação
    - Controle de estoque de vacinas
    """)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="module-card saude-color">', unsafe_allow_html=True)
    st.markdown('#### ☠️ Mortalidade')
    st.markdown("""
    Registro e análise de mortalidade:
    - Cadastro detalhado de óbitos
    - Classificação por causa e categoria
    - Análise de tendências de mortalidade
    - Alertas para índices acima do esperado
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
st.markdown('</div>', unsafe_allow_html=True)

# Seção Gestão e Relatórios
st.markdown('<div class="category-section">', unsafe_allow_html=True)
st.markdown('<h3 style="color: #F57C00;">🔹 GESTÃO E RELATÓRIOS</h3>', unsafe_allow_html=True)
st.markdown("""
Esta categoria reúne os módulos analíticos e gerenciais, com foco em indicadores de desempenho e relatórios.
""")

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="module-card gestao-color">', unsafe_allow_html=True)
    st.markdown('#### 📊 GESTÃO')
    st.markdown("""
    Painel de controle principal da granja:
    - Indicadores-chave de desempenho (KPIs)
    - Visão consolidada dos principais números
    - Metas e comparativos de produtividade
    - Alertas de desvios importantes
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="module-card gestao-color">', unsafe_allow_html=True)
    st.markdown('#### 🏥 SAÚDE')
    st.markdown("""
    Análise abrangente da saúde do plantel:
    - Indicadores sanitários consolidados
    - Histórico de ocorrências sanitárias
    - Análise de eficácia de tratamentos
    - Tendências em saúde animal
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="module-card gestao-color">', unsafe_allow_html=True)
    st.markdown('#### 📝 RELATÓRIOS')
    st.markdown("""
    Relatórios especializados para gestão:
    - Relatórios personalizáveis por período
    - Exportação em múltiplos formatos
    - Análises comparativas e históricas
    - Indicadores técnicos e produtivos
    """)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="module-card gestao-color">', unsafe_allow_html=True)
    st.markdown('#### 🏭 PRODUÇÃO')
    st.markdown("""
    Acompanhamento dos índices produtivos:
    - Análise de eficiência reprodutiva
    - Métricas de produtividade por categoria
    - Estatísticas de produção por período
    - Projeções e planejamento produtivo
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="module-card gestao-color">', unsafe_allow_html=True)
    st.markdown('#### 🚀 DESENVOLVIMENTO')
    st.markdown("""
    Ferramentas para análise e melhoria contínua:
    - Análise de tendências produtivas
    - Identificação de oportunidades de melhoria
    - Benchmarking interno e externo
    - Projetos de desenvolvimento produtivo
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="module-card gestao-color">', unsafe_allow_html=True)
    st.markdown('#### 📋 Relatórios')
    st.markdown("""
    Relatórios detalhados específicos:
    - Relatórios por animal/categoria
    - Históricos completos individuais
    - Análises detalhadas por evento
    - Exportação e compartilhamento facilitados
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
st.markdown('</div>', unsafe_allow_html=True)

# Módulos especiais
st.markdown('<div class="category-section">', unsafe_allow_html=True)
st.markdown('<h3>⚙️ MÓDULOS ESPECIAIS</h3>', unsafe_allow_html=True)
st.markdown("""
Módulos avançados para funcionalidades específicas e desenvolvimento do sistema.
""")

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="module-card">', unsafe_allow_html=True)
    st.markdown('#### ⚙️ Recria')
    st.markdown("""
    Gerenciamento da fase de recria:
    - Formação e controle de lotes
    - Registro de alimentação por fase
    - Monitoramento de ganho de peso
    - Avaliação de conversão alimentar
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="module-card">', unsafe_allow_html=True)
    st.markdown('#### 📥 Download Aplicativo')
    st.markdown("""
    Acesso à versão mobile do sistema:
    - Download do aplicativo Android
    - Instruções de instalação e configuração
    - Sincronização com a versão web
    - Funcionalidades offline
    """)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="module-card">', unsafe_allow_html=True)
    st.markdown('#### 🛠️ Sistema Desenvolvedor')
    st.markdown("""
    Ferramentas avançadas para desenvolvedores:
    - Configurações técnicas do sistema
    - Gerenciamento de componentes Streamlit
    - Ferramentas de backup e manutenção
    - Gerador de APK WebView personalizado
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
st.markdown('</div>', unsafe_allow_html=True)

# Benefícios e diferenciais
st.markdown('<h2 class="section-title">Benefícios e Diferenciais</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown('<h4>📈 Aumento da Produtividade</h4>')
    st.markdown("""
    <ul class="benefits-list">
        <li>Redução do tempo gasto em registros manuais</li>
        <li>Identificação rápida de animais com problemas</li>
        <li>Tomada de decisão baseada em dados</li>
        <li>Automatização de cálculos e análises</li>
        <li>Planejamento otimizado de atividades</li>
    </ul>
    """, unsafe_allow_html=True)
    
    st.markdown('<h4>🔄 Integração Total</h4>')
    st.markdown("""
    <ul class="benefits-list">
        <li>Todos os módulos integrados em uma única plataforma</li>
        <li>Fluxo de informação contínuo entre setores</li>
        <li>Versão mobile sincronizada com a web</li>
        <li>Possibilidade de exportação e importação de dados</li>
        <li>Integração com equipamentos de identificação eletrônica</li>
    </ul>
    """, unsafe_allow_html=True)

with col2:
    st.markdown('<h4>👁️ Visibilidade Completa</h4>')
    st.markdown("""
    <ul class="benefits-list">
        <li>Visão do histórico completo de cada animal</li>
        <li>Dashboards interativos com indicadores-chave</li>
        <li>Relatórios detalhados em tempo real</li>
        <li>Rastreabilidade total do nascimento ao abate</li>
        <li>Alertas proativos para eventos importantes</li>
    </ul>
    """, unsafe_allow_html=True)
    
    st.markdown('<h4>📱 Acessibilidade</h4>')
    st.markdown("""
    <ul class="benefits-list">
        <li>Interface intuitiva para usuários de todos os níveis</li>
        <li>Acesso via aplicativo móvel para uso no campo</li>
        <li>Disponível em múltiplos dispositivos</li>
        <li>Funcionamento parcial offline com sincronização</li>
        <li>Atualização automática de novas funcionalidades</li>
    </ul>
    """, unsafe_allow_html=True)

# Exemplo de dashboard
st.markdown('<h2 class="section-title">Exemplos de Visualizações</h2>', unsafe_allow_html=True)

# Alguns gráficos de exemplo para ilustrar o sistema
col1, col2 = st.columns(2)

with col1:
    # Gráfico de exemplo 1 - Distribuição de animais por categoria
    labels = ['Matrizes', 'Leitões Maternidade', 'Creche', 'Recria', 'Engorda', 'Reprodutores']
    values = [120, 380, 450, 520, 630, 15]
    
    fig = px.pie(
        names=labels, 
        values=values, 
        title='Distribuição do Plantel por Categoria',
        color_discrete_sequence=px.colors.sequential.Viridis
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
    st.plotly_chart(fig, use_container_width=True)
    
    # Gráfico de exemplo 3 - Eficiência Reprodutiva
    months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun']
    taxa_parto = [86, 88, 85, 89, 90, 91]
    leitoes_vivos = [12.4, 12.5, 12.8, 12.7, 13.1, 13.2]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=taxa_parto, name='Taxa de Parto (%)', 
                           line=dict(color='royalblue', width=3)))
    
    fig.add_trace(go.Bar(x=months, y=leitoes_vivos, name='Leitões Nascidos Vivos',
                       marker_color='lightgreen'))
    
    fig.update_layout(
        title='Eficiência Reprodutiva',
        xaxis_title='Mês',
        legend=dict(x=0, y=1.1, orientation='h'),
        yaxis=dict(title='Taxa de Parto (%)'),
        yaxis2=dict(title='Leitões Nascidos Vivos', overlaying='y', side='right')
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Gráfico de exemplo 2 - Ganho de peso por fase
    categories = ['Maternidade', 'Creche', 'Crescimento', 'Terminação']
    gpd = [0.25, 0.45, 0.78, 0.92]
    
    fig = px.bar(
        x=categories, 
        y=gpd, 
        title='Ganho de Peso Diário por Fase (kg)',
        color=gpd,
        color_continuous_scale='Viridis',
        text=[f"{x:.2f} kg" for x in gpd]
    )
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)
    
    # Gráfico de exemplo 4 - Mortalidade por fase
    data = pd.DataFrame({
        'Fase': ['Maternidade', 'Creche', 'Crescimento', 'Terminação'],
        'Meta': [8, 2, 1, 0.8],
        'Real': [7.2, 1.8, 1.2, 0.7]
    })
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=data['Fase'],
        y=data['Real'],
        name='Mortalidade Real (%)',
        marker_color='indianred'
    ))
    
    fig.add_trace(go.Scatter(
        x=data['Fase'],
        y=data['Meta'],
        name='Meta (%)',
        mode='lines+markers',
        line=dict(color='royalblue', width=3)
    ))
    
    fig.update_layout(
        title='Mortalidade por Fase vs. Meta',
        xaxis_title='Fase de Produção',
        yaxis_title='Taxa de Mortalidade (%)',
        legend=dict(x=0, y=1.1, orientation='h')
    )
    st.plotly_chart(fig, use_container_width=True)

# Guia rápido para início
st.markdown('<h2 class="section-title">Guia Rápido de Início</h2>', unsafe_allow_html=True)

st.markdown('<div class="guide-card">', unsafe_allow_html=True)
st.markdown("""
#### 1. Configuração Inicial
1. Cadastre os usuários do sistema com suas respectivas permissões
2. Configure os parâmetros básicos da granja (tamanho, capacidade, etc.)
3. Importe ou cadastre os dados do plantel atual
4. Defina os protocolos sanitários e reprodutivos
""")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="guide-card">', unsafe_allow_html=True)
st.markdown("""
#### 2. Uso Diário
1. Registre os eventos reprodutivos (cios, inseminações, partos)
2. Atualize os dados de peso e transferências entre fases
3. Registre ocorrências sanitárias e tratamentos
4. Consulte os relatórios e dashboards para análise contínua
""")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="guide-card">', unsafe_allow_html=True)
st.markdown("""
#### 3. Análise Gerencial
1. Acompanhe semanalmente os KPIs no painel de gestão
2. Gere relatórios mensais para análise comparativa
3. Identifique pontos de melhoria através das tendências
4. Tome decisões estratégicas baseadas nos dados consolidados
""")
st.markdown('</div>', unsafe_allow_html=True)

# Rodapé com design moderno
st.markdown('<div class="footer-section">', unsafe_allow_html=True)
st.markdown(f'<div style="display: flex; flex-direction: column; align-items: center; gap: 1.5rem;">', unsafe_allow_html=True)

# Título do rodapé
st.markdown(f'<div><h3 style="font-size: 1.8rem; margin-bottom: 0.5rem; background: linear-gradient(90deg, {primary_color}, {secondary_color}); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700;">Sistema Suinocultura</h3>', unsafe_allow_html=True)
st.markdown(f'<p style="font-size: 1.1rem; color: {text_muted}; max-width: 600px; margin: 0 auto;">Desenvolvido para otimizar o gerenciamento de granjas suinícolas através de tecnologia avançada.</p></div>', unsafe_allow_html=True)

# Seção de recursos
st.markdown('<div style="display: flex; gap: 2rem; margin: 1rem 0;">', unsafe_allow_html=True)

# Suporte Técnico
st.markdown(f'''
<div style="text-align: center;">
    <div style="font-size: 1.5rem; margin-bottom: 0.5rem; color: {primary_color};">🔧</div>
    <div style="font-weight: 600; margin-bottom: 0.2rem; color: {text_color};">Suporte Técnico</div>
    <div style="font-size: 0.9rem; color: {text_muted};">Disponível 24/7</div>
</div>
''', unsafe_allow_html=True)

# App Mobile
st.markdown(f'''
<div style="text-align: center;">
    <div style="font-size: 1.5rem; margin-bottom: 0.5rem; color: {secondary_color};">📱</div>
    <div style="font-weight: 600; margin-bottom: 0.2rem; color: {text_color};">App Mobile</div>
    <div style="font-size: 0.9rem; color: {text_muted};">Acesso em Campo</div>
</div>
''', unsafe_allow_html=True)

# Atualizações
st.markdown(f'''
<div style="text-align: center;">
    <div style="font-size: 1.5rem; margin-bottom: 0.5rem; color: {accent_color};">🔄</div>
    <div style="font-weight: 600; margin-bottom: 0.2rem; color: {text_color};">Atualizações</div>
    <div style="font-size: 0.9rem; color: {text_muted};">Mensais</div>
</div>
''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # Fecha a div dos recursos

# Separador
st.markdown(f'<div style="width: 50%; height: 1px; background: linear-gradient(90deg, transparent, {card_border}, transparent); margin: 0.5rem 0;"></div>', unsafe_allow_html=True)

# Copyright
st.markdown(f'<div style="font-size: 0.9rem; color: {text_muted};">© 2025 Sistema Suinocultura | Todos os direitos reservados</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # Fecha a div flex
st.markdown('</div>', unsafe_allow_html=True)  # Fecha a div footer-section