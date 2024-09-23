import numpy as np
import pandas as pd
import datetime

from darts import TimeSeries
from darts.models import AutoARIMA


def construct_prediction(input_data: pd.DataFrame, predictions_values: list[float]):
    stock_id = input_data.iloc[-1]["id"]
    
    first_date = input_data.iloc[-1]["timestamp"] + datetime.timedelta(days=1)
    second_date = input_data.iloc[-1]["timestamp"] + datetime.timedelta(days=2)
    third_date = input_data.iloc[-1]["timestamp"] + datetime.timedelta(days=3)
    
    prediction = pd.DataFrame([[stock_id, first_date, predictions_values[0]],
                [stock_id, second_date, predictions_values[1]],
                [stock_id, third_date, predictions_values[2]]], columns=list(input_data.columns))

    return pd.concat([input_data, prediction], ignore_index=True)


def arima_predict(input_data: pd.DataFrame):
    # Fit an Arima and use it for prediction
    darts_series = TimeSeries.from_dataframe(input_data, "timestamp", "price")
    model = AutoARIMA()
    model.fit(darts_series)
    prediction = model.predict(3)
    
    return construct_prediction(input_data, list(prediction.all_values().flatten()))


def basic_predict(input_data: pd.DataFrame):
    # Stock-ID, Timestamp (dd-mm-yyyy), stock price value
    # first predicted (n+1) data point is same as the 2nd highest value present in the 10 data points
    # n+2 data point has half the difference between n and n +1
    # n+3 data point has 1/4th the difference between n+1 and n+2
    first_price = input_data.nlargest(2, columns=["price"]).iloc[1]["price"]
    second_price = abs(input_data.iloc[-1]["price"] - first_price)/2
    third_price = abs(first_price - second_price)*0.25
    
    return construct_prediction(input_data, [first_price, second_price, third_price])


def predict(input_data: pd.DataFrame, model: str="basic") -> pd.DataFrame:
    if model == "arima":
        return arima_predict(input_data)
    else:
        return basic_predict(input_data)