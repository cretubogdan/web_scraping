import os
import uuid
import logging
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed


logger = logging.getLogger("scrapy")

NUM_THREADS = int(os.getenv("NUM_THREADS", 10))

def do_web_scraping(websites, output, type):
    if 'raw_req' == type:
        from task_requests import Task
    elif 'selenium' == type:
        from task_selenium import Task
    else:
        raise ValueError(f"Type: {type} is not a valid form of run")

    columns = ['URL', 'Phone', 'Social']
    data = []

    def process_website(website):
        task = Task(website, uuid.uuid4())
        task.fetch()
        task.run()
        return task.get_result()

    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = [executor.submit(process_website, website) for website in websites]

        for future in as_completed(futures):
            rsp = future.result()
            data.append(rsp)

    df = pd.DataFrame(data, columns=columns)
    df.to_csv(output, index=False)

    return df