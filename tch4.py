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
import plotly.graph_objects as go
import plotly.express as px
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller, acf, pacf
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima.model import ARIMA
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')
import streamlit as st
from prophet import Prophet

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
    Nesta página, apresentamos a evolução histórica do preço do Petróleo Brent, um dos principais benchmarks mundiais. Desde a Guerra do Golfo em 1990, passando pela crise financeira de 2008 e os impactos das tensões geopolíticas e da pandemia de COVID-19, o gráfico a seguir mostra como eventos globais influenciaram significativamente o mercado de petróleo. Analisando essas flutuações, podemos entender melhor a volatilidade deste mercado e os fatores que impulsionam as mudanças nos preços.
    """)
    df_petroleo_filtered = df_petroleo[(df_petroleo['data'] >= '2014-01-01') & (df_petroleo['data'] < '2024-01-01')]
    fig = px.line(df_petroleo_filtered, x='data', y='preco_petroleo', template='plotly_white', width=1000, height=600)
    fig.update_layout(title="Evolução do Petróleo Brent", xaxis_title="Data", yaxis_title="Dólares por Barril")
    st.plotly_chart(fig)

    st.write("""
    Primeira grande alta foi em Outubro de 1990. Essa alta se deu por conta da guerra entre Iraque e Kwait.
    A segunda grande alta se deu em Julho de 2008 devido a atrasos no potencial retorno do petróleo iraniano aos mercados globais e a considerações dos Estados Unidos e aliados europeus de proibir importações de petróleo russo.
    As negociações para reviver o acordo nuclear de 2015 do Irã com as potências mundiais produziram a queda do valor do barril do petróleo.
    Em Outubro 2018 vemos uma queda brusca decorrente do assassinato do jornalista saudita Jamal Khashoggi, crítico do príncipe-herdeiro Mohamed bin Salman e exilado nos Estados Unidos.
    Depois disso temos a queda de Abril de 2020, decorrente do início da pandemia do COVID-19 e os dois picos de Março e Julho de 2022 decorrentes da Guerra entre Ucrânia e Rússia.
    """)

with tab1:
    st.subheader("Análise de Tendências e Sazonalidade")
    st.write("""
    A análise de tendências e sazonalidade nos permite decompor o preço do petróleo em seus componentes fundamentais. Utilizando a decomposição sazonal, identificamos as tendências subjacentes e os padrões sazonais que afetam os preços ao longo do tempo. Esta abordagem revela as flutuações cíclicas e ajuda a prever futuros comportamentos do mercado, fornecendo uma visão mais clara sobre a dinâmica de longo prazo do petróleo Brent.
    """)
    df_ajustado = df_petroleo.set_index('data', drop=True)
    resultados = seasonal_decompose(df_ajustado, period=12, model='multiplicative')

    fig_obs = px.line(resultados.observed.reset_index(), x='data', y='preco_petroleo', template='plotly_white', title="Observado")
    fig_trend = px.line(resultados.trend.reset_index(), x='data', y='preco_petroleo', template='plotly_white', title="Tendência")
    fig_seasonal = px.line(resultados.seasonal.reset_index(), x='data', y='preco_petroleo', template='plotly_white', title="Sazonalidade")
    fig_resid = px.line(resultados.resid.reset_index(), x='data', y='preco_petroleo', template='plotly_white', title="Resíduos")

    col1, col2 = st.columns(2)
    col1.plotly_chart(fig_obs)
    col2.plotly_chart(fig_trend)
    
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig_seasonal)
    col2.plotly_chart(fig_resid)

with tab2:
    st.subheader("Teste de Estacionaridade e Transformações de Série Temporal")
    st.write("""
    Para modelar adequadamente a série temporal do preço do petróleo, é crucial determinar se a série é estacionária. A estacionaridade é uma propriedade essencial para muitas técnicas de modelagem de séries temporais. Nesta página, utilizamos o Teste ADF (Dickey-Fuller Aumentado) para verificar a estacionaridade e aplicamos transformações, como logaritmos e diferenciação, para estabilizar a variância e tornar a série mais adequada para análise preditiva.
    """)
    X = df_ajustado.preco_petroleo.values
    result = adfuller(X)

    st.write("Teste ADF")
    st.write(f"Teste Estatístico: {result[0]}")
    st.write(f"P-Value: {result[1]}")
    st.write("Valores críticos:")
    for key, value in result[4].items():
        st.write(f"\t{key}: {value}")

    ma = df_ajustado.rolling(12).mean()
    df_ajustado = df_ajustado.reset_index()
    fig_ma = px.line(df_ajustado, x='data', y='preco_petroleo', template='plotly_white', title="Média Móvel (12 Meses)")
    fig_ma.add_scatter(x=ma.index, y=ma['preco_petroleo'], mode='lines', name='Média Móvel', line=dict(color='red'))

    st.plotly_chart(fig_ma)

    df_ajustado_log = np.log(df_ajustado.set_index('data'))
    ma_log = df_ajustado_log.rolling(12).mean()

    fig_ma_log = px.line(df_ajustado_log.reset_index(), x='data', y='preco_petroleo', template='plotly_white', title="Logaritmo e Média Móvel (12 Meses)")
    fig_ma_log.add_scatter(x=ma_log.index, y=ma_log['preco_petroleo'], mode='lines', name='Média Móvel', line=dict(color='red'))

    st.plotly_chart(fig_ma_log)

    df_s = (df_ajustado_log - ma_log).dropna()
    ma_s = df_s.rolling(12).mean()
    std = df_s.rolling(12).std()

    fig_s = px.line(df_s.reset_index(), x='data', y='preco_petroleo', template='plotly_white', title="Série Transformada")
    fig_s.add_scatter(x=ma_s.index, y=ma_s['preco_petroleo'], mode='lines', name='Média Móvel', line=dict(color='red'))
    fig_s.add_scatter(x=std.index, y=std['preco_petroleo'], mode='lines', name='Desvio Padrão', line=dict(color='green'))

    st.plotly_chart(fig_s)

    X_s = df_s.preco_petroleo.values
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
    A análise de autocorrelação (ACF) e autocorrelação parcial (PACF) nos ajuda a identificar dependências temporais na série de preços do petróleo. Estes gráficos são fundamentais para selecionar os parâmetros apropriados para modelos ARIMA (Autoregressive Integrated Moving Average). Ao entender a relação entre valores passados e presentes, podemos construir modelos mais precisos e robustos para previsão dos preços futuros.
    """)
    df_diff = df_s.diff(1).dropna()
    ma_diff = df_diff.rolling(12).mean()
    std_diff = df_diff.rolling(12).std()

    fig_diff = px.line(df_diff.reset_index(), x='data', y='preco_petroleo', template='plotly_white', title="Diferença da Série")
    fig_diff.add_scatter(x=ma_diff.index, y=ma_diff['preco_petroleo'], mode='lines', name='Média Móvel', line=dict(color='red'))
    fig_diff.add_scatter(x=std_diff.index, y=std_diff['preco_petroleo'], mode='lines', name='Desvio Padrão', line=dict(color='green'))

    st.plotly_chart(fig_diff)

    X_diff = df_diff.preco_petroleo.dropna().values
    result_diff = adfuller(X_diff)

    st.write("Teste ADF")
    st.write(f"Teste Estatístico: {result_diff[0]}")
    st.write(f"P-Value: {result_diff[1]}")
    st.write("Valores críticos:")
    for key, value in result_diff[4].items():
        st.write(f"\t{key}: {value}")

    lag_acf = acf(df_diff.dropna(), nlags=25)
    lag_pacf = pacf(df_diff.dropna(), nlags=25)

    fig_acf = px.line(x=range(len(lag_acf)), y=lag_acf, template='plotly_white', title="ACF")
    fig_acf.add_scatter(x=[-1.96/np.sqrt(len(df_diff.dropna())), 1.96/np.sqrt(len(df_diff.dropna()))], y=[0, 0], mode='lines', line=dict(color='gray', dash='dash'))

    fig_pacf = px.line(x=range(len(lag_pacf)), y=lag_pacf, template='plotly_white', title="PACF")
    fig_pacf.add_scatter(x=[-1.96/np.sqrt(len(df_diff.dropna())), 1.96/np.sqrt(len(df_diff.dropna()))], y=[0, 0], mode='lines', line=dict(color='gray', dash='dash'))

    st.plotly_chart(fig_acf)
    st.plotly_chart(fig_pacf)

with tab4:
    st.subheader("Previsão de Preços com Prophet")
    st.write("""
    A previsão de preços do petróleo é uma tarefa complexa, mas crucial para decisões econômicas e estratégicas. Utilizando o modelo Prophet, desenvolvemos previsões baseadas em dados históricos ajustados. Nesta página, mostramos como o Prophet pode capturar a sazonalidade diária e realizar previsões para períodos futuros. Além disso, comparamos as previsões com os valores reais para calcular a precisão do modelo, usando a métrica MAPE (Erro Percentual Absoluto Médio).
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

    fig_forecast = px.line(previsao, x='ds', y='yhat', template='plotly_white', title="Previsão de Preços do Petróleo")
    fig_forecast.add_scatter(x=test_and_val_data['ds'], y=test_and_val_data['y'], mode='markers', name='Valores Reais', marker=dict(color='red'))

    st.plotly_chart(fig_forecast)

    previsao_cols = ['ds', 'yhat']
    valores_reais_cols = ['ds', 'y']

    previsao = previsao[previsao_cols]
    valores_reais = test_and_val_data[valores_reais_cols]

    resultados = pd.merge(previsao, valores_reais, on='ds', how='inner')
    resultados['erro_percentual_absoluto'] = np.abs((resultados['y'] - resultados['yhat']) / resultados['y']) * 100

    mape = np.mean(resultados['erro_percentual_absoluto'])
    st.write(f"MAPE: {mape:.2f}%")
