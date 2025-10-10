class MedKey:
    def __init__(self, base_url: str | None = None, api_key: str | None = None):
        self.base_url = base_url or "https://api.usemedkey.com"
        self.api_key = api_key
