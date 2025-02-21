import argparse
import pandas as pd
import logging
import time

from scraping import do_web_scraping

logging.basicConfig(filename="main.log", filemode="w", level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("scrapy")

HARDCODED_HEADER_CSV = "domain"

def get_websites(csv_path):
    df = pd.read_csv(csv_path)
    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str)
    parser.add_argument("--output", type=str)
    parser.add_argument("--type", type=str)
    args = parser.parse_args()

    websites = get_websites(args.input)
    websites = websites[1:]
    websites = websites[HARDCODED_HEADER_CSV].tolist()

    start_time = time.time()
    resulted_df = do_web_scraping(websites, args.output, args.type)
    end_time = time.time()
    delta = end_time - start_time
    logger.info(f"Scraping with {args.type} took: {int(delta // 60)} mins and {int(delta % 60)} secs")
    resulted_df.to_csv(args.output, index=False)
