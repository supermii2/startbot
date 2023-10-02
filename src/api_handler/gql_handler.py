import requests

from src.utils.get_env import get_start_token, get_start_url

TOKEN = get_start_token()
URL = get_start_url()
HEADERS = {
    'Authorization': 'Bearer ' + TOKEN
}


def make_gql_request(gql_string: str, variables) -> dict:
    query = {
        "query": gql_string,
        "variables": variables,
        "operationName": gql_string.split("(")[0].split("query ")[-1]
    }

    response = requests.post(URL, json=query, headers=HEADERS)
    response = response.json()
    if "errors" in response:
        raise SyntaxError(response['errors'][0]['message'])

    else:
        return response['data']
