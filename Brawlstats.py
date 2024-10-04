import requests

class APIrequests:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://api.brawlstars.com/v1/players/'
        self.headers = {
            "authorization": f"Bearer {self.api_key}"
        }

    def get_player(self, params):
        url = self.base_url + '%23' + params
        try:
            response = requests.get(url, headers=self.headers, timeout=3)
            print(response)  # Print status code or debug info
            return response.text  # Return parsed JSON response
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def get_player_battle_log(self, tag):
        url = f'{self.base_url}%23{tag}/battlelog'
        try:
            response = requests.get(url, headers=self.headers, timeout=3) 
            print("Data retrieved")
            return response.text  
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return None
