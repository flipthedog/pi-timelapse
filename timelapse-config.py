import argparse
from datetime import datetime
import os
import yaml

from src.picamera_timelapse import PiTimeLapse
from src.conf.conf_provider import ConfProvider

today_str = datetime.now().strftime("%Y_%m_%d")
current_cwd = os.getcwd() + "/"

# Load config file

config = ConfProvider().get_conf()

timelapse = PiTimeLapse(
    config=config,
)
