import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(page_title="Analisador de Vacinação", layout="wide")
st.title("📊 Analisador de Dados de Vacinação")
st.markdown("""
    **Como usar:**  
    - Faça upload de um arquivo CSV no formato `data,vacinas,municipio`.  
    - O sistema irá analisar tendências e gerar recomendações automáticas.  
""")

# Upload do arquivo
uploaded_file = st.file_uploader("📤 **Carregue seu arquivo CSV**", type="csv")

if uploaded_file:
    # Carrega e formata os dados
    data = pd.read_csv(uploaded_file)
    data['data'] = pd.to_datetime(data['data'])
    data = data.sort_values('data')
    
    # Seleciona município (se houver múltiplos)
    if 'municipio' in data.columns:
        municipio_selecionado = st.selectbox("📍 **Selecione o município:**", data['municipio'].unique())
        data = data[data['municipio'] == municipio_selecionado]
    
    # Gráfico de tendência
    st.subheader(f"📈 **Dados de Vacinação em {municipio_selecionado if 'municipio' in data.columns else 'Região Selecionada'}**")
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(data['data'], data['vacinas'], marker='o', color='#4CAF50', linewidth=2)
    ax.set_xlabel('Data', fontsize=12)
    ax.set_ylabel('Vacinas Aplicadas', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.6)
    st.pyplot(fig)

    # Cálculo de variação mensal
    data['variacao_percentual'] = data['vacinas'].pct_change() * 100
    data['mes'] = data['data'].dt.strftime('%Y-%m')

    # Identifica quedas significativas (>20%)
    grandes_quedas = data[data['variacao_percentual'] < -20]
    
    # Previsão para os próximos 3 meses (Regressão Linear)
    X = np.array(range(len(data))).reshape(-1, 1)
    y = data['vacinas'].values
    modelo = LinearRegression().fit(X, y)
    futuro = np.array(range(len(data), len(data) + 3)).reshape(-1, 1)
    previsoes = modelo.predict(futuro)
    datas_futuras = [data['data'].iloc[-1] + timedelta(days=30*i) for i in range(1, 4)]

    # Relatório de Análise
    st.subheader("🔍 **Relatório de Análise**")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📉 **Quedas Significativas**")
        if not grandes_quedas.empty:
            for _, row in grandes_quedas.iterrows():
                mes_anterior = data[data['data'] < row['data']].iloc[-1] if not data[data['data'] < row['data']].empty else None
                if mes_anterior is not None:
                    st.write(f"- **{row['mes']}**: Queda de **{abs(row['variacao_percentual']):.1f}%** (de {mes_anterior['vacinas']} para {row['vacinas']})")
                else:
                    st.write(f"- **{row['mes']}**: Queda de **{abs(row['variacao_percentual']):.1f}%** (dados iniciais)")
        else:
            st.write("✅ Nenhuma queda significativa (>20%) identificada.")

    with col2:
        st.markdown("### 🔮 **Previsão para os Próximos 3 Meses**")
        for data_futura, previsao in zip(datas_futuras, previsoes):
            st.write(f"- **{data_futura.strftime('%Y-%m')}**: {int(previsao)} vacinas esperadas")

    # Recomendações Automáticas
    st.subheader("💡 **Recomendações Estratégicas**")
    if not grandes_quedas.empty:
        st.markdown("""
        - **📢 Intensificar campanhas** antes dos meses com histórico de queda.  
        - **🏥 Verificar estoque** em períodos de alta demanda.  
        - **🔍 Investigar causas** das quedas (ex.: problemas de distribuição).  
        """)
    else:
        st.markdown("""
        - **📈 Manter a estratégia atual**, pois não há quedas significativas.  
        - **🔄 Monitorar tendências** para evitar futuras quedas.  
        """)

    # Botão para download do relatório
    st.download_button(
        label="📥 **Baixar Relatório em CSV**",
        data=data.to_csv(index=False).encode('utf-8'),
        file_name=f"relatorio_vacinacao_{municipio_selecionado if 'municipio' in data.columns else 'geral'}.csv",
        mime="text/csv"
    )

# Rodapé
st.markdown("---")
st.caption("Desenvolvido para análise de dados de vacinação | © 2024")