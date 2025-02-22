import os
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from elasticsearch import Elasticsearch

from .helper import format_phone_number, clean_social_media


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
    # es.indices.delete(index=INDEX)
    if not es.indices.exists(index=INDEX):
        es.indices.create(index=INDEX, ignore=400, body={
            "mappings": {
                "properties": {
                    "domain": {"type": "keyword"},
                    "company_commercial_name": {"type": "text"},
                    "company_legal_name": {"type": "text"},
                    "company_all_available_names": {"type": "text"},
                    "phone_number": {"type": "keyword"},
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
    should_clauses = []

    if company_info.company_name:
        should_clauses.append({
            "multi_match": {
                "query": company_info.company_name,
                "fields": ["company_commercial_name", "company_legal_name", "company_all_available_names"],
                "operator": "or",
                "fuzziness": "AUTO"
            }
        })
    if company_info.company_website:
        should_clauses.append({
            "match": {"domain": company_info.company_website}
        })
    if company_info.company_phone:
        phone = format_phone_number(company_info.company_phone)
        should_clauses.append({
            "match": {"phone_number": phone}
        })
    if company_info.company_facebook:
        social_media = clean_social_media(company_info.company_facebook)
        should_clauses.append({
            "match": {
                "social_media": {
                    "query": social_media,
                    "fuzziness": "AUTO"
                }
            }
        })
    query = {
        "query": {
            "bool": {
                "should": should_clauses,
                "minimum_should_match": 1
            }
        }
    }

    rsp = es.search(index=INDEX, body=query)
    if len(rsp['hits']['hits']):
        return rsp['hits']['hits'][0]
    return None