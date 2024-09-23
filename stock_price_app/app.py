import argparse

import utils as u, models as m

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("STOCK_EXCHANGE_APP")

STOCK_EXCHANGES = ["LSE", "NASDAQ", "NYSE"]

def analyse_stock_exchanges(number_files: int, 
                            model: str,
                            stock_exchanges: list[str] = STOCK_EXCHANGES):
    
    for stock_exchange in stock_exchanges:
        stock_symbols = u.get_input_files(stock_exchange, number_files)

        logger.info(f"Processing [{stock_exchange}] -- Found data files for: {stock_symbols} .")
        for stock_symbol in stock_symbols:
            input_data = u.read_input_data(stock_exchange, stock_symbol)
            if input_data is not None:
                prediction = m.predict(input_data, model)
                u.write_output_data(stock_exchange, stock_symbol, prediction)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Predict next 3 values of Stock price.')
    parser.add_argument('--N', required=True, type=int, choices=[1,2],
                        help='(integer) the number of files to be processed')
    parser.add_argument('--model', required=False, type=str, choices=["basic","arima"], default="basic",
                        help='(str) model to be used for prediction')

    args = parser.parse_args()
    logger.info(f"Processing [{args.N}] file(s) with input data for each stock exchange. Using model [{args.model}]")
    
    analyse_stock_exchanges(args.N, args.model)
    
    logger.info("Done.")
    