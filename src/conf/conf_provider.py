import yaml
import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

print(os.getcwd())

from src.conf.picamera_timelapse_conf import TimeLapseConf

class ConfProvider:

    def __init__(self):
        self.conf = None
    
    def _load(self) -> TimeLapseConf:
        with open('conf/config.yaml', "r", encoding="utf-8") as file:
            conf = yaml.safe_load(file)

        timelapse_conf = TimeLapseConf(**conf)
        return timelapse_conf

    def get_conf(self) -> TimeLapseConf:
        if self.conf is None:
            self.conf = self._load()
        return self.conf

if __name__ == "__main__":
    conf_provider = ConfProvider()
    conf = conf_provider.get_conf()
    print(conf)