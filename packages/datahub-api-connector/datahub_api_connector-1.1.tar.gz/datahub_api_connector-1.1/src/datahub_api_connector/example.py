from src.datahub_api_connector import ApiConnector as api

sources = api(account_id=920, request_timeout=5, log_level="DEBUG").get('sources', DisplayLevel='Light').json()
print(f"Found {len(sources)} sources")