# Extract settings in ./config/config.json
# Variablize every setting for individual use.

import json

class Config():
    def __init__(self):
        self.config_file = 'config\config_example.json'   # 'config\config_example.json; for windows but for linux change this to './config/config_example.json
        self.config_dict = {}
        self.read_configjson()

    def read_configjson(self):
        try:
            with open(self.config_file) as data_file:
                config = json.load(data_file)
                self.config_dict = config
                return self.config_dict

        except Exception as e:
            print(f"There was an error reading config from: {self.config_file}")
            print(e)


if __name__ == '__main__': 
    _cfg = Config()
    config_dict = _cfg.read_configjson()
    print("*** config.json contents ***")
    for k, v in config_dict.items():
        print(f"{k} : {v}")

    print("")
    print("*** config_vsearch() test ***")
    test = config_dict.get('dest_wallet')
    print(test)

