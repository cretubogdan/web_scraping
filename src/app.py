from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

class CompanyInfo(BaseModel):
    company_name: str
    company_website: str
    company_phone: str
    company_facebook: str

@app.post("/match_company")
async def match_company(company_info: CompanyInfo):
    return "Works"