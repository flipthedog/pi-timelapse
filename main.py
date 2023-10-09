import argparse
from datetime import datetime
import os
import yaml

from PiCameraTimeLapse import PiTimeLapse

today_str = datetime.now().strftime("%m_%d_%Y")
current_cwd = os.getcwd()

parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter
)

parser.add_argument(
    "project_name",
    type=str,
    default= "timelapse_" + today_str,
    help="Project name for timelapse, (default: %(default)s)"
)

parser.add_argument(
    "-i",
    "--interval",
    type=int,
    default=300,
    help="interval in seconds between captures, (default: %(default)s)"
)

parser.add_argument(
    "-n",
    "--number",
    type=int,
    default=-1,
    help="Number of captures to take before ending, (default: %(default)s), -1 for continuous"
)

parser.add_argument(
    "-l",
    "--log",
    type=str,
    default=current_cwd,
    help="Log file location, (default: %(default)s)"
)

parser.add_argument(
    "-c",
    "--config",
    type=str,
    default="config.yaml",
    help="Optional location of config file for additional options, (default: %(default)s)"
)

args = parser.parse_args()

project_name = args.project_name
interval = args.interval

if args.config is None or args.config is "":

    print("No config file found at: ", args.config)
    print("Loading default parameters")

    resolution = (1920, 1080)
    file_type = ".jpg"
    local = True
    local_save_location = project_name
    save_to_s3 = False
    s3_bucket_location = ""

else:
    
    with open(current_cwd + args.config, mode='r', encoding="utf-8") as file:
        config = yaml.safe_load(file)
    
    if config['project_name'] is not None:
        project_name = config['project_name']
    
    if config['interval'] is not None:
        interval = config['interval']
    
    if config['']

timelapse = PiTimeLapse(
    project_name=project_name,
    interval=interval,
    length_of_timelapse="",
    resolution= resolution,
    file_type=file_type,
    local_save_directory=local_save_location,
    save_to_s3=save_to_s3,
    s3_bucket_location=s3_bucket_location
)
