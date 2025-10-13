import json, os
CONFIG_FILE = os.path.expanduser("~/.dockai_config.json")

def get_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def set_config(key, value):
    data = get_config()
    data[key] = value
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def delete_config(key):
    data = get_config()
    if key in data:
        del data[key]
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=2)
