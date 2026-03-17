import shodan
from typing import Dict

class ShodanClient:
    def __init__(self, api_key: str):
        self.api = shodan.Shodan(api_key) if api_key else None

    def search(self, query: str) -> Dict:
        if not self.api:
            raise Exception("SHODAN_API_KEY not configured")
        return self.api.search(query)
