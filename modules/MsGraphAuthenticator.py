import logging, msal

def graph_bearer_token (tenant_id, client_id, secret, scope):
    app = msal.ConfidentialClientApplication(
        client_id,
        authority= "https://login.microsoftonline.com/" + tenant_id,
        client_credential=secret,
    )

    # Firstly, look up a token from cache
    # Since we are looking for token for the current app, NOT for an end user,
    # notice we give account parameter as None.
    result = app.acquire_token_silent(scope, account=None)
    if not result:
        logging.info("No suitable token exists in cache. Let's get a new one from AAD.")
        result = app.acquire_token_for_client(scopes=scope)

    if "access_token" in result:
        logging.info("Authentication succeeded. Token acquired")
        return result["access_token"]

    else:
        logging.critical("Authentication failed: " + result.get("error_description", "No error description available"))
        raise Exception(
            "Authentication failed: " + result.get("error_description", "No error description available"))