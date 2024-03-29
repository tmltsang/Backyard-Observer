import os
import yaml
from functools import reduce

class Config(object):
    __filename = None
    
    # constant values which should same for envs
    SERVER = "abc"
    

    def __new__(cls, filename: str):
        if not hasattr(cls, 'instance') or cls.instance.__filename != filename:
            cls.instance = super(Config, cls).__new__(cls)
            cls.instance.load(filename)
        return cls.instance


    def load(self, filename):
        self.__filename = filename
        with open("ggstrive_analyser/conf/%s.yml" % filename, "r") as f:
            self._data = yaml.load(f, Loader=yaml.FullLoader)

    def get(self, key):
        if "." not in key:
            return self._data.get(key, None)
        else:
            keys = key.split(".")
            return reduce(lambda data, key: data[key], keys, self._data)