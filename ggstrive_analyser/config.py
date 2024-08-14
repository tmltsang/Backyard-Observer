import os
import yaml
from functools import reduce

class Config:
    conf = {}

    # constant values which should same for envs
    ASUKA_SPELL_COUNT = 4
    P1 = "p1"
    P2 = "p2"

    @classmethod
    def load(cls, filename):
        if filename != "":
            if cls.conf == {}:
                with open("ggstrive_analyser/conf/%s.yml" % filename, "r") as f:
                    cls.conf = yaml.load(f, Loader=yaml.FullLoader)

    @classmethod
    def get(cls, key):
        if "." not in key:
            return cls.conf.get(key, None)
        else:
            keys = key.split(".")
            return reduce(lambda data, key: data[key], keys, cls.conf)