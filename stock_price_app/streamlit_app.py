import streamlit as st
import plotly.express as px

import utils as u, models as m

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("STOCK_EXCHANGE_APP")

STOCK_EXCHANGES = ["LSE", "NASDAQ", "NYSE"]

st.set_page_config(layout="wide")
st.title("Stock Exchange App")

st.sidebar.header("Input Data")
st.sidebar.subheader(f"Processing stock exchanges: {STOCK_EXCHANGES} ")
input_form = st.sidebar.form("input_form")

number_files = input_form.number_input("Number of files to process", min_value=1, max_value=2)
model = input_form.selectbox(
    "Model to use for prediction",
    ("Basic", "ARIMA"),
    placeholder="Select model...",
)
stock_exchanges = STOCK_EXCHANGES

submit_button = input_form.form_submit_button('Generate predictions')

if submit_button:
    st.markdown(f"""
                - Processing stock exchanges - *{STOCK_EXCHANGES}*.
                - Processing *{number_files}* file(s) with input data for each stock exchange.
                - Using model ***{model}***.
                """)

    for stock_exchange in stock_exchanges:
        stock_symbols = u.get_input_files(stock_exchange, number_files)

        logger.info(f"Processing [{stock_exchange}] -- Found data files for: {stock_symbols} .")
        st.markdown(f"""> Processing **{stock_exchange}** -- Found data files for: **{stock_symbols}**.""")
        for stock_symbol in stock_symbols:
            input_data = u.read_input_data(stock_exchange, stock_symbol)
            if input_data is not None:
                prediction = m.predict(input_data, model.lower())
                u.write_output_data(stock_exchange, stock_symbol, prediction)
                
                prediction["type"] = "input"
                prediction.loc[prediction.tail(3).index, "type"] = "prediction"
                
                fig = px.line(prediction, x="timestamp", y="price", markers=True, color_discrete_sequence=["#A7B2E6"])
                fig.add_scatter(x=prediction.tail(3)['timestamp'], y=prediction.tail(3)['price'], mode='lines', name='Prediction', line=dict(color='#7A6174'))
                fig.update_layout(title=f"Input and Predicted Stock Price for {stock_exchange} - {stock_symbol}", 
                                xaxis_title='Day', yaxis_title='Stock Price')
                fig.update_xaxes(showgrid=True)
                fig.update_yaxes(showgrid=True)
                
                st.plotly_chart(fig,
                                theme="streamlit",
                                use_container_width=True)
            else:
                st.markdown(f"""> **No data found for {stock_exchange} - {stock_symbol}.** """)
            
else:
    st.subheader("Please use the sidebar to set input parameters.")
    