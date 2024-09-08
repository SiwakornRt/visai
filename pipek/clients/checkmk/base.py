class BasedAPI:
    def __init__(self, http_client, based_api_url: str = ""):
        self.http_client = http_client
        self.based_api_url = based_api_url

    def update_based_api_url(self, based_api_url: str):
        self.based_api_url = based_api_url

    def get(self, endpoint: str, params: dict = {}):
        url = f"{self.based_api_url}{endpoint}"

        # print(">", url, params)

        response = self.http_client.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print("http error:", response.status_code)

        return {}
