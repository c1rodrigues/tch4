# -*- coding: utf-8 -*-
"""pega_dados_ipe.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1A0ndMgKNOn14sULlEfP8dslQ2gP6ncnF
"""

# Commented out IPython magic to ensure Python compatibility.
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import seaborn as sns
# %matplotlib inline

from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.stattools import acf, pacf
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima.model import ARIMA

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

import warnings
warnings.filterwarnings('ignore')
import streamlit as st

from prophet import Prophet

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
tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs(['Evolução do Preço do Petróleo Brent', 'Análise de Tendências e Sazonalidade', 'Teste de Estacionaridade e Transformações de Série Temporal', 'Análise de Autocorrelação e Autocorrelação Parcial', 'Previsão de Preços com Prophet', 'Modelagem ARIMA'])
st.set_option('deprecation.showPyplotGlobalUse', False)

with tab0:
    st.subheader("Evolução do Preço do Petróleo Brent")
    st.write("""
    Nesta página, apresentamos a evolução histórica do preço do Petróleo Brent, um dos principais benchmarks mundiais. Desde a Guerra do Golfo em 1990, passando pela crise financeira de 2008 e os impactos das tensões geopolíticas e da pandemia de COVID-19, o gráfico a seguir mostra como eventos globais influenciaram significativamente o mercado de petróleo. Analisando essas flutuações, podemos entender melhor a volatilidade deste mercado e os fatores que impulsionam as mudanças nos preços.
    """)
    fig = px.line(df_petroleo, x='data', y='preco_petroleo', template='plotly_white')
    fig.update_layout(title="Evolução do Petróleo Brent", xaxis_title=" ", yaxis_title="Dolares por Barril")
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
    Nesta página, focamos na análise de tendências e sazonalidade do preço do petróleo Brent. A análise de séries temporais nos permite decompor a série em componentes que revelam padrões ocultos nos dados. Utilizando a decomposição sazonal, podemos identificar as tendências subjacentes, os padrões sazonais e os resíduos.

    A imagem a seguir ilustra a decomposição do preço do petróleo Brent:
    
    - **Primeiro Gráfico (Observado):** Este gráfico mostra os preços observados do petróleo Brent de janeiro de 2022 a maio de 2024. Aqui, podemos ver claramente as flutuações no preço do petróleo durante esse período, refletindo eventos e influências econômicas e geopolíticas.
    
    - **Segundo Gráfico (Tendência):** Este gráfico mostra a tendência subjacente dos preços do petróleo. Ele suaviza as flutuações diárias para revelar a direção geral do mercado ao longo do tempo. Podemos observar períodos de aumento e queda prolongados, que podem ser atribuídos a mudanças estruturais no mercado, como políticas de produção de petróleo ou mudanças na demanda global.
    
    - **Terceiro Gráfico (Sazonalidade):** Este gráfico mostra os padrões sazonais no preço do petróleo. A sazonalidade captura as flutuações que ocorrem em intervalos regulares devido a fatores recorrentes, como variações sazonais na demanda ou oferta. Podemos ver que o preço do petróleo tende a seguir um padrão repetitivo ao longo do tempo.
    
    - **Quarto Gráfico (Resíduos):** Este gráfico mostra os resíduos, ou seja, as variações que não são explicadas pela tendência ou sazonalidade. Os resíduos representam a componente aleatória dos dados, incluindo os choques imprevisíveis no mercado de petróleo, como desastres naturais ou eventos geopolíticos inesperados.
    
    Através dessa análise de decomposição, podemos entender melhor como diferentes componentes contribuem para a variação do preço do petróleo Brent. Essa visão é crucial para investidores, economistas e formuladores de políticas, permitindo-lhes tomar decisões informadas baseadas em uma compreensão profunda dos padrões históricos e das dinâmicas de mercado.
    """)
    df_ajustado = df_petroleo[(df_petroleo['data'] > '2022-01-01') & (df_petroleo['data'] <= '2024-05-01')]
    df_ajustado = df_ajustado.set_index('data', drop=True)
    resultados = seasonal_decompose(df_ajustado, period=5, model='multiplicative')

    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(15, 10))
    resultados.observed.plot(ax=ax1)
    resultados.trend.plot(ax=ax2)
    resultados.seasonal.plot(ax=ax3)
    resultados.resid.plot(ax=ax4)
    plt.tight_layout()
    st.pyplot(fig)

with tab2:
    st.subheader("Teste de Estacionaridade e Transformações de Série Temporal")
    st.write("""
    Para modelar adequadamente a série temporal do preço do petróleo, é crucial determinar se a série é estacionária. A estacionaridade é uma propriedade essencial para muitas técnicas de modelagem de séries temporais. Nesta página, utilizamos o Teste ADF (Dickey-Fuller Aumentado) para verificar a estacionaridade e aplicamos transformações, como logaritmos e diferenciação, para estabilizar a variância e tornar a série mais adequada para análise preditiva.

    A seguir, detalhamos as etapas do processo:

    - **Primeiro Gráfico (Média Móvel):** Este gráfico mostra a série temporal original do preço do petróleo Brent juntamente com a média móvel de 12 períodos. A média móvel ajuda a suavizar a série, permitindo uma melhor visualização das tendências subjacentes.

    - **Segundo Gráfico (Logaritmo da Série):** Aplicamos a transformação logarítmica à série temporal para estabilizar a variância. Isso é útil quando a série apresenta variações de amplitude que aumentam com o nível da série.

    - **Terceiro Gráfico (Média Móvel do Logaritmo):** Após a transformação logarítmica, calculamos a média móvel de 12 períodos da série logarítmica para continuar suavizando os dados.

    - **Quarto Gráfico (Série Transformada):** Por fim, subtraímos a média móvel logarítmica da série logarítmica original para obter uma série estacionária. Também são exibidas a média móvel e o desvio padrão da série transformada para ilustrar a redução de variabilidade.
    """)

    df_ajustado = df[(df['data'] > '2022-01-01') & (df['data'] <= '2024-05-01')]
    df_ajustado = df_ajustado.set_index('data', drop=True)

    X = df_ajustado['preco_petroleo'].values
    result = adfuller(X)

    st.write("Teste ADF")
    st.write(f"Teste Estatístico: {result[0]}")
    st.write(f"P-Value: {result[1]}")
    st.write("Valores críticos:")
    for key, value in result[4].items():
        st.write(f"\t{key}: {value}")

    ma = df_ajustado.rolling(12).mean()

    f, ax = plt.subplots()
    df_ajustado.plot(ax=ax, legend=False, title="Média Móvel")
    ma.plot(ax=ax, legend=False, color='r')
    plt.tight_layout()
    st.pyplot(f)

    df_ajustado_log = np.log(df_ajustado)
    ma_log = df_ajustado_log.rolling(12).mean()

    f, ax = plt.subplots()
    df_ajustado_log.plot(ax=ax, legend=False, title="Logaritmo da Série")
    ma_log.plot(ax=ax, legend=False, color='r')
    plt.tight_layout()
    st.pyplot(f)

    df_s = (df_ajustado_log - ma_log).dropna()
    ma_s = df_s.rolling(12).mean()
    std = df_s.rolling(12).std()

    f, ax = plt.subplots()
    df_s.plot(ax=ax, legend=False, title="Série Transformada")
    ma_s.plot(ax=ax, legend=False, color='r')
    std.plot(ax=ax, legend=False, color='g')
    plt.tight_layout()
    st.pyplot(f)

    X_s = df_s['preco_petroleo'].values
    result_s = adfuller(X_s)

    st.write("Teste ADF (Série Transformada)")
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
    df_diff = df_s.diff(1)
    ma_diff = df_diff.rolling(12).mean()
    std_diff = df_diff.rolling(12).std()

    f, ax = plt.subplots()
    df_diff.plot(ax=ax, legend=False)
    ma_diff.plot(ax=ax, legend=False, color='r')
    std_diff.plot(ax=ax, legend=False, color='g')
    plt.tight_layout()
    st.pyplot(f)

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

    f, ax = plt.subplots()
    ax.plot(lag_acf)
    ax.axhline(y=-1.96/(np.sqrt((len(df_diff) -1))), linestyle='--', color='gray', linewidth=.7)
    ax.axhline(y=0, linestyle='--', color='gray', linewidth=.7)
    ax.axhline(y=1.96/(np.sqrt((len(df_diff) -1))), linestyle='--', color='gray', linewidth=.7)
    ax.set_title("ACF")
    plt.tight_layout()
    st.pyplot(f)

    f, ax = plt.subplots()
    ax.plot(lag_pacf)
    ax.axhline(y=-1.96/(np.sqrt((len(df_diff) -1))), linestyle='--', color='gray', linewidth=.7)
    ax.axhline(y=0, linestyle='--', color='gray', linewidth=.7)
    ax.axhline(y=1.96/(np.sqrt((len(df_diff) -1))), linestyle='--', color='gray', linewidth=.7)
    ax.set_title("PACF")
    plt.tight_layout()
    st.pyplot(f)

    st.pyplot(plot_acf(df_ajustado.preco_petroleo))
    st.pyplot(plot_pacf(df_ajustado.preco_petroleo))

with tab4:
    st.subheader("Previsão de Preços com Prophet")
    st.write("""
    A previsão de preços do petróleo é uma tarefa complexa, mas crucial para decisões econômicas e estratégicas. Utilizando o modelo Prophet, desenvolvemos previsões baseadas em dados históricos ajustados. Nesta página, mostramos como o Prophet pode capturar a sazonalidade diária e realizar previsões para períodos futuros. Além disso, comparamos as previsões com os valores reais para calcular a precisão do modelo, usando a métrica MAPE (Erro Percentual Absoluto Médio).
    """)
    df = df_petroleo[(df_petroleo['data'] > '2022-01-01') & (df_petroleo['data'] <= '2024-05-01')]
    df.sort_values('data', ascending=True, inplace=True)
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
    
    f, ax = plt.subplots(figsize=(20, 6))
    modelo.plot(previsao, ax=ax)
    ax.plot(test_and_val_data['ds'], test_and_val_data['y'], '.r')
    st.pyplot(f)

    previsao_cols = ['ds', 'yhat']
    valores_reais_cols = ['ds', 'y']

    previsao = previsao[previsao_cols]
    valores_reais = test_and_val_data[valores_reais_cols]

    resultados = pd.merge(previsao, valores_reais, on='ds', how='inner')
    resultados['erro_percentual_absoluto'] = np.abs((resultados['y'] - resultados['yhat']) / resultados['y']) * 100

    mape = np.mean(resultados['erro_percentual_absoluto'])
    st.write(f"MAPE: {mape:.2f}%")

with tab5:
    st.subheader("Modelagem ARIMA")
    st.write("""
    A modelagem ARIMA é uma abordagem poderosa para análise e previsão de séries temporais. Utilizamos o modelo ARIMA para ajustar os dados transformados do preço do petróleo e avaliar a sua performance. Esta página mostra o ajuste do modelo e a comparação com os valores reais, ajudando a entender a eficácia do ARIMA na previsão do preço do petróleo.
    """)
    modelo = ARIMA(df_diff, order=(2, 1, 2))  # (p, d, q)
    resultado_AR = modelo.fit()

    f, ax = plt.subplots()
    ax.plot(df_diff, label='Valores Diferençados')
    ax.plot(resultado_AR.fittedvalues, color='red', label='Valores Ajustados pelo Modelo')
    ax.set_title('RSS: %.4f' % sum((resultado_AR.fittedvalues - df_diff['preco_petroleo'])**2))
    ax.legend()
    st.pyplot(f)

    # Verifica pontos nulos
    st.write("Pontos nulos no dataframe:")
    st.write(df_diff.isnull().sum())

    # Preenche pontos nulos
    df_diff = df_diff.fillna(method='ffill')
    if df_diff.iloc[0].isnull().any():
        df_diff.iloc[0] = df_diff.iloc[0].fillna(df_diff.iloc[1])
    
    st.write("Pontos nulos após preenchimento:")
    st.write(df_diff.isnull().sum())

    predictions = resultado_AR.fittedvalues
    predictions.index = df_diff.index

    predicted_values = df_ajustado_log['preco_petroleo'].iloc[0] + np.cumsum(predictions)
    mape = mean_absolute_error(df_diff['preco_petroleo'], predicted_values) * 100

    st.write(f"MAPE: {mape:.2f}%")
