import base64
import requests

import utils.definitions as definitions


def check_sql_syntax(query):
    """
    Verify if the generated SQL query has valid syntax using the EverSQL API.
    Args:
        query (str): The SQL query to validate.
    Returns:
        bool: True if the query is valid, False if invalid, None if an error occurs.
    """

    # Check if the URL for the SQL syntax validation API is defined
    if not definitions.URL_API_SQL_VALIDATOR:
        print("⚠️ URL for the SQL syntax validation API is not defined.")
        return None

    # Make the query
    response = requests.post(
        definitions.URL_API_SQL_VALIDATOR,
        files={'query': (None, base64.b64encode(query.encode()).decode())}
    )

    # Analize the response from the API
    result = response.json()
    error_desc = result.get("error_desc")

    # Result interpretation based on HTTP status code
    if response.status_code == 400:
        print(f"⚠️ The query is invalid. Description: {error_desc}")
        return False
    elif response.status_code == 200 and error_desc == "":
        print("✅ The query is valid.")
        return True
    else:
        print(f"Unexpected error: {response.status_code}")
        return None
