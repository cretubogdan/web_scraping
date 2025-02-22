import os
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from elasticsearch import Elasticsearch


es = Elasticsearch(
    [{"scheme": "http", "host": "localhost", "port": 9200}],
    basic_auth=[os.getenv("ES_USER"), os.getenv("ES_PASS")]
)
INDEX = "companies"

class CompanyInfo(BaseModel):
    company_name: str
    company_website: str
    company_phone: str
    company_facebook: str


async def lifespan(app: FastAPI):
    if not es.indices.exists(index=INDEX):
        es.indices.create(index=INDEX, ignore=400, body={
            "mappings": {
                "properties": {
                    "domain": {"type": "text"},
                    "company_commercial_name": {"type": "text"},
                    "company_legal_name": {"type": "text"},
                    "company_all_available_names": {"type": "text"},
                    "phone_number": {"type": "text"},
                    "social_media": {"type": "text"}
                }
            }
        })
        dataset = os.getenv("DATASET")
        df = pd.read_csv(dataset)
        df = df.fillna('')
        for index, row in df.iterrows():
            doc = {
                "domain": row["domain"],
                "company_commercial_name": row["company_commercial_name"],
                "company_legal_name": row["company_legal_name"],
                "company_all_available_names": row["company_all_available_names"],
                "phone_number": row["phone_number"],
                "social_media": row["social_media"]
            }
            es.index(index=INDEX, document=doc)
    yield
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

@app.post("/match_company")
async def match_company(company_info: CompanyInfo):
    return "Works"