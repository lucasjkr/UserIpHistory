import requests, json

def graph_bearer_token (tenant_id, client_id, client_secret, scope):
    # Construct the token endpoint URL
    token_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'

    # Prepare the data for the POST request
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': scope,
        'grant_type': 'client_credentials'
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Make the POST request to obtain the token
    response = requests.post(token_url, data=data, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        token = response.json().get('access_token')
        return f'Bearer {token}'
    else:
        print(f'Failed to obtain token: {response.status_code}')
        print(response.json())
        exit()