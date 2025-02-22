import pytest
import requests
import pandas as pd

def test_bulk_requests():
    df = pd.read_csv("data/API-input-sample.csv")
    url = "http://localhost:8000/match_company"
    for _, row in df.iterrows():
        input_name = row.get("input_name")
        if not input_name:
            input_name = ""
        input_phone = row.get("input_phone")
        if not input_phone:
            input_phone = ""
        input_website = row.get("input_website")
        if not input_website:
            input_website = ""
        input_facebook = row.get("input_facebook")
        if not input_facebook:
            input_facebook = ""
        json_data = {
            "company_name": input_name,
            "company_website": input_phone,
            "company_phone": input_website,
            "company_facebook": input_facebook
        }
        response = requests.post(url, json=json_data)
        print(response.text)
        assert response.status_code == 200