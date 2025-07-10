import yaml
import os

def load_strategies(file_path='strategies.yaml'):
    if not os.path.exists(file_path):
        return {"stocks": [], "etfs": []}
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
        return {
            "stocks": data.get("stocks", []),
            "etfs": data.get("etfs", [])
        }
