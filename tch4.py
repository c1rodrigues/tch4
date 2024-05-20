# -*- coding: utf-8 -*-
"""
Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1A0ndMgKNOn14sULlEfP8dslQ2gP6ncnF
"""

# Importações necessárias
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller, acf, pacf
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')
import streamlit as st
from prophet import Prophet
import plotly.express as px

# Configuração da página do Streamlit
st.set_page_config(layout="wide")

# Títulos
st.write("# Tech-Challenge")

# Importando dados
df = pd.read_html('http://www.ipeadata.gov.br/ExibeSerie.aspx?module=m&serid=1650971490&oper=view', encoding='UTF-8', decimal=',', thousands='.')
df_petroleo = df[2]
df_petroleo.reset_index(drop=True, inplace=True)
new_header = ['data', 'preco_petroleo']
df_petroleo = df_petroleo[1:]
df_petroleo.columns = new_header
df_petroleo['data'] = pd.to_datetime(df_petroleo['data'])
df_petroleo['preco_petroleo'] = df_petroleo['preco_petroleo'].astype(float)

# Verificar dados
df_petroleo.isnull().sum()
df_petroleo.info()

# Criando abas na aplicação
tab0, tab1, tab2, tab3, tab4 = st.tabs(['Evolução do Preço do Petróleo Brent', 'Análise de Tendências e Sazonalidade', 'Teste de Estacionaridade e Transformações de Série Temporal', 'Análise de Autocorrelação e Autocorrelação Parcial', 'Previsão de Preços com Prophet'])
st.set_option('deprecation.showPyplotGlobalUse', False)

with tab0:
    st.subheader("Evolução do Preço do Petróleo Brent")
    st.write("""
    O preço do Petróleo Brent, um dos principais benchmarks globais para o petróleo, tem uma história rica e tumultuada. Desde o início da década de 1990, vimos flutuações significativas que refletem eventos geopolíticos e econômicos. Em outubro de 1990, a invasão do Kuwait pelo Iraque desencadeou uma subida acentuada nos preços. Mais tarde, em julho de 2008, os preços dispararam novamente devido a tensões envolvendo o retorno do petróleo iraniano aos mercados globais e as considerações sobre a proibição das importações de petróleo russo pelos EUA e aliados europeus.
    
    O gráfico abaixo ilustra essas e outras variações, como a queda brusca em outubro de 2018 após o assassinato do jornalista saudita Jamal Khashoggi e o impacto da pandemia de COVID-19 em abril de 2020. Mais recentemente, a guerra entre Ucrânia e Rússia causou picos nos preços em março e julho de 2022. Este panorama nos ajuda a entender como os eventos globais influenciam o mercado de petróleo.
    """)
    df_petroleo_filtered = df_petroleo[(df_petroleo['data'] >= '2014-01-01') & (df_petroleo['data'] < '2024-01-01')]
    fig = px.line(df_petroleo_filtered, x='data', y='preco_petroleo', template='plotly_white', width=1000, height=600)
    fig.update_layout(title="Evolução do Petróleo Brent", xaxis_title="Data", yaxis_title="Dólares por Barril")
    st.plotly_chart(fig)

    st.write("""
    **Principais Eventos:**
    - **Outubro de 1990:** Guerra entre Iraque e Kuwait.
    - **Julho de 2008:** Tensão envolvendo o petróleo iraniano e russo.
    - **Outubro de 2018:** Assassinato de Jamal Khashoggi.
    - **Abril de 2020:** Impacto da pandemia de COVID-19.
    - **Março e Julho de 2022:** Guerra entre Ucrânia e Rússia.
    """)

with tab1:
    st.subheader("Análise de Tendências e Sazonalidade")
    st.write("""
    A decomposição sazonal é uma ferramenta poderosa para entender os componentes subjacentes de uma série temporal. No caso do preço do petróleo Brent, a decomposição nos permite isolar a tendência de longo prazo, os padrões sazonais e as flutuações residuais.
    
    A tendência nos mostra a direção geral do mercado ao longo do tempo, enquanto a sazonalidade revela padrões recorrentes que ocorrem em intervalos regulares. Os resíduos representam a variação que não pode ser explicada pela tendência ou sazonalidade e podem indicar eventos inesperados ou anomalias no mercado.
    
    A análise abaixo detalha esses componentes, oferecendo uma visão clara de como cada um contribui para a evolução do preço do petróleo Brent.
    """)
    df_ajustado = df_petroleo.set_index('data', drop=True)
    resultados = seasonal_decompose(df_ajustado, period=12, model='multiplicative')

    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(15, 10))
    resultados.observed.plot(ax=ax1, legend=False)
    ax1.set_title('Observado')
    resultados.trend.plot(ax=ax2, legend=False)
    ax2.set_title('Tendência')
    resultados.seasonal.plot(ax=ax3, legend=False)
    ax3.set_title('Sazonalidade')
    resultados.resid.plot(ax=ax4, legend=False)
    ax4.set_title('Resíduos')
    plt.tight_layout()
    st.pyplot(fig)

with tab2:
    st.subheader("Teste de Estacionaridade e Transformações de Série Temporal")
    st.write("""
    Antes de aplicar modelos de séries temporais, é crucial verificar se a série é estacionária. Uma série é considerada estacionária se suas propriedades estatísticas, como média e variância, permanecem constantes ao longo do tempo. Para isso, utilizamos o Teste ADF (Dickey-Fuller Aumentado).
    
    No caso do preço do petróleo Brent, aplicamos transformações como a diferenciação e o logaritmo para estabilizar a variância e tornar a série mais próxima da estacionaridade. Abaixo, apresentamos os resultados do Teste ADF e visualizações das transformações aplicadas.
    """)
    X = df_ajustado['preco_petroleo'].values
    result = adfuller(X)

    st.write("Teste ADF")
    st.write(f"Teste Estatístico: {result[0]}")
    st.write(f"P-Value: {result[1]}")
    st.write("Valores críticos:")
    for key, value in result[4].items():
        st.write(f"\t{key}: {value}")

    ma = df_ajustado.rolling(12).mean()

    f, ax = plt.subplots(figsize=(15, 5))
    df_ajustado.plot(ax=ax, legend=False)
    ma.plot(ax=ax, legend=False, color='r')
    plt.tight_layout()
    st.pyplot(f)

    df_ajustado_log = np.log(df_ajustado)
    ma_log = df_ajustado_log.rolling(12).mean()

    f, ax = plt.subplots(figsize=(15, 5))
    df_ajustado_log.plot(ax=ax, legend=False)
    ma_log.plot(ax=ax, legend=False, color='r')
    plt.tight_layout()
    st.pyplot(f)

    df_s = (df_ajustado_log - ma_log).dropna()
    ma_s = df_s.rolling(12).mean()
    std = df_s.rolling(12).std()

    f, ax = plt.subplots(figsize=(15, 5))
    df_s.plot(ax=ax, legend=False)
    ma_s.plot(ax=ax, legend=False, color='r')
    std.plot(ax=ax, legend=False, color='g')
    plt.tight_layout()
    st.pyplot(f)

    X_s = df_s['preco_petroleo'].values
    result_s = adfuller(X_s)

    st.write("Teste ADF")
    st.write(f"Teste Estatístico: {result_s[0]}")
    st.write(f"P-Value: {result_s[1]}")
    st.write("Valores críticos:")
    for key, value in result_s[4].items():
        st.write(f"\t{key}: {value}")

with tab3:
    st.subheader("Análise de Autocorrelação e Autocorrelação Parcial")
    st.write("""
    A autocorrelação (ACF) e a autocorrelação parcial (PACF) são ferramentas essenciais para entender a relação entre os valores passados e presentes de uma série temporal. No contexto do preço do petróleo Brent, essas análises nos ajudam a identificar a presença de padrões ou ciclos que podem ser utilizados na modelagem preditiva.
    
    O gráfico ACF mostra a correlação de uma série com suas próprias versões defasadas ao longo do tempo, enquanto o gráfico PACF ajuda a identificar a ordem apropriada de um modelo ARIMA (Autoregressive Integrated Moving Average). Abaixo, apresentamos os gráficos ACF e PACF para o preço do petróleo Brent, destacando os lags significativos.
    """)
    df_diff = df_s.diff(1).dropna()
    ma_diff = df_diff.rolling(12).mean()
    std_diff = df_diff.rolling(12).std()

    f, ax = plt.subplots(figsize=(15, 5))
    df_diff.plot(ax=ax, legend=False)
    ma_diff.plot(ax=ax, legend=False, color='r')
    std_diff.plot(ax=ax, legend=False, color='g')
    plt.tight_layout()
    st.pyplot(f)

    X_diff = df_diff['preco_petroleo'].values
    result_diff = adfuller(X_diff)

    st.write("Teste ADF")
    st.write(f"Teste Estatístico: {result_diff[0]}")
    st.write(f"P-Value: {result_diff[1]}")
    st.write("Valores críticos:")
    for key, value in result_diff[4].items():
        st.write(f"\t{key}: {value}")

    lag_acf = acf(df_diff, nlags=25)
    lag_pacf = pacf(df_diff, nlags=25)

    f, ax = plt.subplots(figsize=(15, 5))
    ax.plot(lag_acf)
    ax.axhline(y=-1.96/np.sqrt(len(df_diff)), linestyle='--', color='gray', linewidth=.7)
    ax.axhline(y=0, linestyle='--', color='gray', linewidth=.7)
    ax.axhline(y=1.96/np.sqrt(len(df_diff)), linestyle='--', color='gray', linewidth=.7)
    ax.set_title("ACF")
    plt.tight_layout()
    st.pyplot(f)

    f, ax = plt.subplots(figsize=(15, 5))
    ax.plot(lag_pacf)
    ax.axhline(y=-1.96/np.sqrt(len(df_diff)), linestyle='--', color='gray', linewidth=.7)
    ax.axhline(y=0, linestyle='--', color='gray', linewidth=.7)
    ax.axhline(y=1.96/np.sqrt(len(df_diff)), linestyle='--', color='gray', linewidth=.7)
    ax.set_title("PACF")
    plt.tight_layout()
    st.pyplot(f)

    st.pyplot(plot_acf(df_ajustado['preco_petroleo'], lags=25))
    st.pyplot(plot_pacf(df_ajustado['preco_petroleo'], lags=25))

with tab4:
    st.subheader("Previsão de Preços com Prophet")
    st.write("""
    Prever o preço do petróleo é uma tarefa desafiadora devido à sua natureza volátil e dependente de múltiplos fatores globais. Utilizamos o modelo Prophet, desenvolvido pelo Facebook, que é particularmente eficaz para séries temporais com fortes componentes sazonais e múltiplos efeitos de feriados.
    
    O Prophet permite a captura da sazonalidade diária, semanal e anual, proporcionando previsões robustas mesmo com dados históricos relativamente curtos. Abaixo, apresentamos as previsões geradas pelo Prophet para o preço do petróleo Brent, comparando com os valores reais para avaliar a precisão do modelo através do MAPE (Erro Percentual Absoluto Médio).
    """)
    df = df_petroleo[(df_petroleo['data'] > '2014-01-01') & (df_petroleo['data'] <= '2024-01-01')]
    df = df.reset_index(drop=True)
    df = df.rename(columns={'data': 'ds', 'preco_petroleo': 'y'})

    train_size = int(len(df) * 0.7)
    val_size = int(len(df) * 0.15)
    test_size = len(df) - train_size - val_size

    train_data, test_and_val_data = np.split(df, [train_size])
    val_data, test_data = np.split(test_and_val_data, [val_size])

    st.write(f'Training data size: {train_data.shape}')
    st.write(f'Testing data size: {test_data.shape}')

    modelo = Prophet(daily_seasonality=True)
    modelo.fit(train_data)
    dataFramefuture = modelo.make_future_dataframe(periods=20, freq='M')
    previsao = modelo.predict(dataFramefuture)

    fig, ax = plt.subplots(figsize=(20, 6))
    modelo.plot(previsao, ax=ax)
    ax.plot(test_and_val_data['ds'], test_and_val_data['y'], '.r')
    st.pyplot(fig)

    previsao_cols = ['ds', 'yhat']
    valores_reais_cols = ['ds', 'y']

    previsao = previsao[previsao_cols]
    valores_reais = test_and_val_data[valores_reais_cols]

    resultados = pd.merge(previsao, valores_reais, on='ds', how='inner')
    resultados['erro_percentual_absoluto'] = np.abs((resultados['y'] - resultados['yhat']) / resultados['y']) * 100

    mape = np.mean(resultados['erro_percentual_absoluto'])
    st.write(f"MAPE: {mape:.2f}%")
