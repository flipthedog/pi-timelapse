import argparse
from datetime import datetime
import os
import yaml

from PiCameraTimeLapse import PiTimeLapse

today_str = datetime.now().strftime("%Y_%m_%d")
current_cwd = os.getcwd() + "/"

parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter
)

parser.add_argument(
    "-c",
    "--config",
    type=str,
    default="config.yaml",
    help="Optional location of config file for additional options, (default: %(default)s)"
)

args = parser.parse_args()

if args.config == None or args.config == "":

    print("No config file found at: ", args.config)
    print("exiting ...")
    raise Exception(f"{args.config} file not found")

else:
    
    with open(args.config, mode='r', encoding="utf-8") as file:
        config = yaml.safe_load(file)
    
    if config['project_name'] is not None:
        project_name = config['project_name']
    
    if config['interval'] is not None:
        interval = config['interval']
    
    if config['number_of_images'] is not None:
        number_of_images = config['number_of_images']
    
    if config['resolution'] is not None:
        resolution = (config['resolution']['width'], config['resolution']['height'])
    
    if config['file_type'] is not None:
        file_type = config['file_type']
    
    if config['save_local'] != None:
        save_local = config['save_local']

    if config['save_local'] != None and config['local_save_location'] != "":
        local_save_location = config['local_save_location']
    else:
        local_save_location = current_cwd + "/" + project_name

    if config['save_to_s3'] is not None and config['s3_bucket_name'] is not None:
        save_to_s3 = config['save_to_s3']
        s3_bucket_name = config['s3_bucket_name']
        s3_path = config['project_name']

    if config['night_mode'] is not None:
        night_mode = config['night_mode']
    
    if config['exposure_time'] is not None:
        exposure_time = config['exposure_time']

if os.path.exists(local_save_location):
    pass
else:
    os.mkdir(local_save_location)

timelapse = PiTimeLapse(
    project_name=project_name,
    interval=interval,
    number_of_images=number_of_images,
    resolution=resolution,
    file_type=file_type,
    local_save_directory=local_save_location,
    save_local=save_local, 
    save_to_s3=save_to_s3,
    s3_bucket_name=s3_bucket_name,
    s3_path=s3_path,
    night_mode=night_mode,
    exposure_time=exposure_time
)
