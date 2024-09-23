import pandas as pd
import os

import logging
logger = logging.getLogger("STOCK_EXCHANGE_APP")

DATA_PATH = "/stock_price_data_files"
OUT_PATH = "/stock_price_predictions"


def get_input_files(stock_exchange: str, 
                    number_files: int) -> list[str]:
    input_dir = os.path.realpath(os.path.curdir) + DATA_PATH + "/" + stock_exchange
    if not os.path.exists(input_dir):
        example_dir = os.path.realpath(os.path.curdir) + DATA_PATH + "/" + "<folders with stock exchange data>"
        raise Exception(f"Could not find input data files! Please make sure the data files are in the correct path! Example: {example_dir}")
    else:
        stock_symbols = [s.replace(".csv", "") for s in os.listdir(input_dir)]
        # return exactly as many symbols as files to be read
        if len(stock_symbols) > number_files:
            logger.warning(f"There are MORE input files ({len(stock_symbols)}) than the number required for processing ({number_files}). Will only process the first {number_files} (for {stock_symbols[:number_files]}) number of files.", 
                           exc_info=False,
                           stacklevel=2)
            return stock_symbols[:number_files]
        if len(stock_symbols) < number_files:
            logger.warning(f"There are LESS input files ({len(stock_symbols)}) than the number required for processing ({number_files}). Will process all files (for {stock_symbols}).", 
                           exc_info=False,
                           stacklevel=2)
        
        return stock_symbols
    

def read_input_data(stock_exchange: str, stock_symbol: str) -> pd.DataFrame:
    # 1st API/Function that, for each file provided, returns 10 consecutive data points starting from a random timestamp.
    input_dir = os.path.realpath(os.path.curdir) + DATA_PATH + "/" + stock_exchange
    input_file = input_dir + "/" + stock_symbol + ".csv"
    logger.debug(f"Sampling {input_file} ... ")
    
    input_data = pd.read_csv(input_file, names=["id", "timestamp", "price"])
    if input_data.shape[0] == 0:
        logger.error(f"There is no data for Stock Exchange = {stock_exchange} and Stock Symbol = {stock_symbol}. Will not use it for prediction.")
        return None
    input_data.timestamp = pd.to_datetime(input_data.timestamp, format="%d-%m-%Y")
    
    try:
        sampled_data = pd.DataFrame()
        while sampled_data.shape[0] < 10:
            random_row = input_data.sample()
            sampled_data = input_data[input_data["timestamp"] >= random_row.iloc[0]["timestamp"]].sort_values(by="timestamp")[:10]
    except Exception as err:
        logger.exception(err)

    return sampled_data


def write_output_data(stock_exchange: str, stock_symbol: str, output: pd.DataFrame):
    output_dir = os.path.realpath(os.path.curdir) + OUT_PATH + "/" + stock_exchange
    if not os.path.exists(output_dir):
        logger.info("Output directories do not exist, will create them.")
        os.makedirs(output_dir)
    
    output.timestamp = output.timestamp.dt.strftime("%d-%m-%Y")
    output.to_csv(output_dir + "/" + stock_symbol + ".csv" , index=False, header=False)