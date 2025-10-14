import os.path
from typing import Dict
import yaml
import json

class FileReader:
    def __init__(self, file_path:str):
        self.file_path = file_path


    def _read_config_file(self) -> Dict:
        """ Read and parse configuration from YAML or JSON file"""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Configuration file not found : {self.file_path}")

        with open(self.file_path,'r') as file:
            if self.file_path.endswith(".yaml") or self.file_path.endswith(".yml"):
                return yaml.safe_load(file)
            elif self.file_path.endswith(".json"):
                return json.load(file)
            else:
                raise ValueError("Unsupported file format. Use YAML or JSON")

    def get_config(self)-> Dict:
        return self._read_config_file()




