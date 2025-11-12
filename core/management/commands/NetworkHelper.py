import requests
from requests.auth import HTTPBasicAuth

class NetworkHelper:
    def __init__(self, base_url, username=None, password=None):
        self.base_url = base_url.rstrip("/") + "/"
        self.auth = HTTPBasicAuth(username, password) if username and password else None

    def safe_json(self, response):
        try:
            return response.json()
        except Exception:
            return response.text

    def get(self, endpoint, params=None):
        url = self.base_url + endpoint.lstrip("/")
        resp = requests.get(url, params=params, auth=self.auth)
        return resp.status_code, self.safe_json(resp)

    def post(self, endpoint, data=None):
        url = self.base_url + endpoint.lstrip("/")
        resp = requests.post(url, json=data, auth=self.auth)
        return resp.status_code, self.safe_json(resp)

    def put(self, endpoint, data=None):
        url = self.base_url + endpoint.lstrip("/")
        resp = requests.put(url, json=data, auth=self.auth)
        return resp.status_code, self.safe_json(resp)

    def delete(self, endpoint):
        url = self.base_url + endpoint.lstrip("/")
        resp = requests.delete(url, auth=self.auth)
        return resp.status_code, self.safe_json(resp)
