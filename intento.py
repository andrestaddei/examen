import streamlit as st 
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Configuración de estilo de Seaborn
sns.set(style="whitegrid")

# Configuración de estilo general de la página
st.set_page_config(
    page_title="Simulador de instrumentos Allianz Patrimonial",
    page_icon=":chart_with_upwards_trend:",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Estilos CSS para mejorar la apariencia
st.markdown(
    """
    <style>
    .main {
        background-color: #f7f9fc;
    }
    .stTextInput, .stSelectbox {
        width: 100%;
    }
    .title {
        font-size: 2.5rem;
        font-weight: 600;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 20px;
    }
    .subtitle {
        font-size: 1.5rem;
        font-weight: 500;
        color: #1f77b4;
        margin-bottom: 15px;
    }
    .info-box {
        background-color: #666666;
        padding: 10px;
        border-radius: 5px;
        color: white;
    }
    .footer {
        text-align: center;
        margin-top: 20px;
        font-size: 0.9rem;
        color: #666;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.image(r"C:\Users\amtad\Documents\ClasePython\Allianz.svg", width=200)

# Título de la aplicación
st.markdown('<h1 class="title">Simulador de instrumentos Allianz Patrimonial</h1>', unsafe_allow_html=True)

# Lista de ETFs populares para el selector
etf_symbols = ['SPY', 'IVV', 'VOO', 'QQQ', 'DIA', 'EFA', 'IEMG', 'AGG', 'GLD', 'SLV', 'XLK', 'XLF', 'XLE']

# Selector de múltiples ETFs
etf_symbols_selected = st.multiselect('🔍 Selecciona uno o más ETFs:', etf_symbols)

# Lista de periodos y selección
st.markdown('<h2 class="subtitle">Selecciona un período:</h2>', unsafe_allow_html=True)
periodos = ['1mo', '3mo', '6mo', '1y', 'ytd', '5y', '10y']
periodo_seleccionado = st.selectbox('', periodos)

# Lista para almacenar la información de cada ETF
etf_data = []

# Si hay ETFs seleccionados
if etf_symbols_selected:
    inversion_inicial = 100  # Inversión inicial en pesos

    for symbol in etf_symbols_selected:
        plt.figure(figsize=(12, 6))
        
        try:
            # Obtener datos históricos de cada ETF
            etf = yf.Ticker(symbol)
            datos = etf.history(period=periodo_seleccionado)
            
            # Verificar si se obtuvieron datos para el ETF
            if not datos.empty:
                # Calcular el rendimiento histórico
                precio_inicial = datos['Close'].iloc[0]
                precio_final = datos['Close'].iloc[-1]
                rendimiento = ((precio_final - precio_inicial) / precio_inicial) * 100

                # Graficar la línea de cierre para cada ETF
                sns.lineplot(data=datos, x=datos.index, y='Close', label=f'{symbol} - Rendimiento: {rendimiento:.2f}%')
                
                # Mostrar información básica del ETF y su rendimiento
                st.markdown(f'<h3 class="title">Información del ETF {symbol}</h3>', unsafe_allow_html=True)
                st.markdown(
                    f"""
                    <div class="info-box">
                        <p><strong>Nombre:</strong> {etf.info.get('longName', 'No disponible')}</p>
                        <p><strong>Categoría:</strong> {etf.info.get('category', 'No disponible')}</p>
                        <p><strong>Rendimiento histórico ({periodo_seleccionado}):</strong> {rendimiento:.2f}%</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Cálculo del dinero final invertido
                dinero_final = inversion_inicial * (1 + (rendimiento / 100))
                st.markdown(f"<h3>Si hubieras invertido {inversion_inicial} pesos en {symbol}, tendrías: {dinero_final:.2f} pesos.</h3>", unsafe_allow_html=True)

                # Mostrar gráfico de precios de cierre de los ETFs seleccionados
                st.title(f"Rendimiento histórico de {symbol}")
                plt.title(f"Precios de Cierre de {symbol}", fontsize=16, color="#1f77b4")
                plt.xlabel("Fecha", fontsize=12)
                plt.ylabel("Precio de Cierre (USD)", fontsize=12)
                plt.legend()
                st.pyplot(plt)

                # Gráfica de bandas de volatilidad
                st.title(f"Volatilidad de {symbol}")
                datos['MA20'] = datos['Close'].rolling(window=20).mean()  # Media móvil de 20 días
                datos['Upper'] = datos['MA20'] + 2 * datos['Close'].rolling(window=20).std()  # Banda superior
                datos['Lower'] = datos['MA20'] - 2 * datos['Close'].rolling(window=20).std()  # Banda inferior

                # Crear gráfico de bandas de volatilidad
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(datos.index, datos['Close'], label=f'{symbol} Precio de Cierre', color='blue')
                ax.plot(datos.index, datos['MA20'], label='Media Móvil (20 días)', color='orange')
                ax.fill_between(datos.index, datos['Upper'], datos['Lower'], color='grey', alpha=0.3, label='Bandas de Volatilidad')

                ax.set_title(f'Bandas de Volatilidad para {symbol}', fontsize=16, color="#1f77b4")
                ax.set_xlabel("Fecha", fontsize=12)
                ax.set_ylabel("Precio de Cierre (USD)", fontsize=12)
                ax.legend()
                
                st.pyplot(fig)

                # Reflexión sobre el riesgo del ETF seleccionado
                st.title("Análisis de Riesgo")
                # Calcular la desviación estándar de los precios de cierre
                volatilidad = datos['Close'].pct_change().std() * np.sqrt(252)  # Anualizando la volatilidad

                # Cálculo de alfa y beta
                mercado = yf.Ticker('^GSPC')  # Usar el S&P 500 como benchmark
                datos_mercado = mercado.history(period=periodo_seleccionado)
                datos_mercado['Rendimiento'] = datos_mercado['Close'].pct_change()

                # Rendimiento del ETF
                datos['Rendimiento'] = datos['Close'].pct_change()

                # Cálculo de beta
                covarianza = np.cov(datos['Rendimiento'].dropna(), datos_mercado['Rendimiento'].dropna())[0][1]
                beta = covarianza / datos_mercado['Rendimiento'].var()

                # Cálculo de alfa (usando la fórmula de Capital Asset Pricing Model - CAPM)
                rendimiento_esperado = 0.0427  # RFUSA
                alfa = rendimiento - (rendimiento_esperado + beta * (datos_mercado['Rendimiento'].mean() - rendimiento_esperado))

                # Guardar los datos en la lista para el cuadro comparativo
                etf_data.append({
                    'ETF': symbol,
                    'Rendimiento Histórico (%)': rendimiento,
                    'Volatilidad Anualizada (%)': volatilidad * 100,
                    'Beta': beta,
                    'Alfa': alfa
                })

                 # Mostrar la reflexión sobre el riesgo
                st.markdown(f"<h3>Riesgo asociado al ETF {symbol}</h3>", unsafe_allow_html=True)
                st.markdown(
                    f"""
                    <div class="info-box">
                        <p><strong>Volatilidad anualizada:</strong> {volatilidad:.2%}</p>
                        <p><strong>Beta:</strong> {beta:.2f}</p>
                        <p><strong>Alfa:</strong> {alfa:.2f}</p>
                        <p>La volatilidad es una medida del riesgo del ETF. Una volatilidad más alta implica que el ETF ha tenido fluctuaciones más significativas en su precio, lo que puede traducirse en mayores riesgos, pero también en mayores oportunidades de rendimiento.</p>
                        <p>El beta indica la sensibilidad del ETF en relación al mercado: un beta mayor a 1 sugiere que el ETF es más volátil que el mercado, mientras que un beta menor a 1 sugiere que es menos volátil. Por otro lado, el alfa mide el rendimiento ajustado al riesgo: un alfa positivo indica que el ETF ha superado el rendimiento esperado, mientras que un alfa negativo indica lo contrario.</p>
                        <p>Es importante considerar tu perfil de riesgo antes de invertir. Si tienes una alta tolerancia al riesgo, puedes optar por ETFs con mayor volatilidad; si prefieres estabilidad, busca ETFs con menor volatilidad.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )



            else:
                st.warning(f"No se encontraron datos para el ETF: {symbol}")

        except Exception as e:
            st.error(f"Error al obtener información para el símbolo: {symbol}. Detalle del error: {str(e)}")

    # Crear un DataFrame con los datos del cuadro comparativo
    if etf_data:
        st.title("Cuadro Comparativo de ETFs Seleccionados")
        df_etf = pd.DataFrame(etf_data)
        
        # Formato condicional de la tabla
        styled_df = df_etf.style.format({
            'Rendimiento Histórico (%)': "{:.2f}%",
            'Volatilidad Anualizada (%)': "{:.2f}%",
            'Beta': "{:.2f}",
            'Alfa': "{:.2f}"
        }).background_gradient(
            subset=['Rendimiento Histórico (%)'], cmap='Greens'
        ).background_gradient(
            subset=['Volatilidad Anualizada (%)'], cmap='Oranges'
        ).background_gradient(
            subset=['Beta'], cmap='Blues'
        ).background_gradient(
            subset=['Alfa'], cmap='Purples'
        ).set_table_styles(
            [{
                'selector': 'thead th',
                'props': [('font-size', '1.1em'), ('font-weight', 'bold'), ('background-color', '#1f77b4'), ('color', 'white')]
            }]
        ).set_properties(**{'text-align': 'center'})

        st.dataframe(styled_df)

# Footer de la página
st.markdown(
    """
    <div class="footer">
        <p>Powered by Yahoo Finance y Streamlit | Diseñado para facilitar la consulta de ETFs</p>
        <p>Elaborado por: Andres Taddei 0232911</p>
    </div>
    """,
    unsafe_allow_html=True,
)