import json

def load_config():
    with open('config.json', encoding='utf-8') as json_data:
        d = json.load(json_data)
        return d