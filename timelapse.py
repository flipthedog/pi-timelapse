import argparse
from datetime import datetime
import os
import yaml

from PiCameraTimeLapse import PiTimeLapse

today_str = datetime.now().strftime("%Y_%m_%d")
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
    "-p",
    "--path",
    type=str,
    default=current_cwd,
    help="Path to create a project folder in and save images to, (default: %(default)s)"
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
    "-rw",
    "--width",
    type=int,
    default=1920,
    help="Pixel resolution width, (default: %(default)s)"
)

parser.add_argument(
    "-rh",
    "--height",
    type=int,
    default=1920,
    help="Pixel resolution height, (default: %(default)s)"
)

parser.add_argument(
    "-ni",
    "--night",
    type=bool,
    default=False,
    help="Night mode, will use long-exposure shots, (default: %(default)s)"
)

parser.add_argument(
    "-e",
    "--exposure",
    type=int,
    default=10000000,
    help="Exposure time in micro-seconds (mus), (default: %(default)s)"
)

parser.add_argument(
    "-f",
    "--file_type",
    type=str,
    default="jpeg",
    help="File type to save images as, (default: %(default)s)"
)

args = parser.parse_args()

project_name = args.project_name
local_save_location = args.path + "/" + args.project_name
interval = args.interval
number = args.number
width = args.width
height = args.height
night_mode = args.night
exposure_time = args.exposure
file_type = args.file_type

print(local_save_location)

if os.path.exists(local_save_location):
    pass
else:
    os.mkdir(local_save_location)

timelapse = PiTimeLapse(
    project_name=project_name,
    interval=interval,
    number_of_images=number,
    resolution=(width, height),
    file_type=file_type,
    local_save_directory=local_save_location,
    save_to_s3=False,
    s3_bucket_name="",
    s3_path="",
    night_mode=night_mode,
    exposure_time=exposure_time
)
