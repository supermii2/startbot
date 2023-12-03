import os
import requests
from dotenv import load_dotenv


def get_start_token():
    load_dotenv()
    return os.getenv('START_TOKEN')


TOKEN = get_start_token()
URL = "https://api.start.gg/gql/alpha"
HEADERS = {
    'Authorization': 'Bearer ' + TOKEN
}


def gql_request(request_json: dict) -> dict:
    response = requests.post(URL, json=request_json, headers=HEADERS)
    response = response.json()
    if "errors" in response:
        raise SyntaxError(response['errors'][0]['message'])

    else:
        return response['data']


def mutate_request(gql_string: str, variables: dict) -> dict:
    request_json = {
        "query": gql_string,
        "variables": variables,
        "operationName": gql_string.split("(")[0].split("mutation ")[-1]
    }
    return gql_request(request_json)


def query_request(gql_string: str, variables: dict) -> dict:
    request_json = {
        "query": gql_string,
        "variables": variables,
        "operationName": gql_string.split("(")[0].split("query ")[-1]
    }
    return gql_request(request_json)
