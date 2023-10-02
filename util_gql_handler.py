from dotenv import load_dotenv
import os
import requests

load_dotenv()

TOKEN = os.getenv('START_TOKEN')
URL = os.getenv('START_URL')
HEADERS = {
    'Authorization': 'Bearer ' + TOKEN
}

def makeGqlRequest(gqlString, variables):
    query = {
        "query" : gqlString,
        "variables" : variables,
        "operationName" : gqlString.split("(")[0].split("query ")[-1]
    }

    response = requests.post(URL, json=query, headers=HEADERS)
    response = response.json()
    if "errors" in response:
        raise SyntaxError(response['errors'][0]['message'])
    
    else:
        return response['data']





