# import cv2 as cv
import numpy as np

import sys

# To load picamera
sys.path.append('/usr/lib/python3/dist-packages')

import os
import io

import time
from datetime import datetime
from threading import Timer

from picamera2 import Picamera2

import boto3
from botocore.exceptions import ClientError

from io import BytesIO
from PIL import Image

import yaml

import libcamera

class PiTimeLapse:

    def __init__(self, project_name, interval=300, length_of_timelapse="", resolution=(1920, 1080), file_type="jpeg", \
         local_save_directory=None, save_to_s3=False, s3_bucket_location="", night_mode=True, exposure_time=10000000) -> None:
        
        print("Starting the timelapse")
        
        self.today_date = datetime.now().strftime("%Y_%m_%d")

        self.storage = ""
        self.current_cwd = os.getcwd()

        self.project_name = project_name + "_" + self.today_date

        if local_save_directory is not None:
            self.local_save_directory = local_save_directory
        else: 
            self.local_save_directory = self.current_cwd

        with open("/home/pi/Projects/pi-timelapse/aws_details.conf", "r") as file:
            self.aws_config = yaml.safe_load(file)

        self.save_path = self.local_save_directory + "/timelapse/" + self.project_name

        self.interval = interval # interval in seconds
        self.length_time = 0 # total length that the timelapse will be, in hours

        self.number_of_pictures = 120
        
        self.pictures_taken = 0

        self.file_type = file_type

        self.stream = BytesIO()
        self.PIL_image = None
        self.cv_image = None

        self.camera = Picamera2()
        
        self.camera_config = self.camera.create_still_configuration(
            main={"size": (2560, 1440)}, 
            transform=libcamera.Transform(vflip=1, hflip=1)
        )

        self.camera.configure(self.camera_config)
        
        if night_mode:
            self.camera.set_controls({
                "ExposureTime":exposure_time,
                "AnalogueGain": 1.0
            })

        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.aws_config['aws_access_key_id'],
            aws_secret_access_key=self.aws_config['aws_secret_access_key']
        )

        # if not os.path.exists(self.project_name):
            
        #     os.makedirs(self.project_name)

        self.t = RepeatTimer(self.interval, self.take_picture)
        self.t.start()

    def take_picture(self):
        
        self.stream = BytesIO()

        current_epoch = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        printable_epoch = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

        self.camera.start()
        
        time.sleep(2)

        file_name = self.project_name + "_" + str(current_epoch) + "." + str(self.file_type)
        file_path = self.save_path + '/' + file_name

        self.camera.capture_file(self.stream, format=self.file_type)
        
        self.camera.stop()

        self.stream.seek(0)

        self.PIL_image = Image.open(self.stream).convert('RGB')

        print("Took a picture at: ", str(datetime.now()) , " saved to: ", file_path)

        self.upload_to_s3(None, file_path=file_path, file_name=self.project_name + "/" + file_name)

        self.pictures_taken += 1

        if self.pictures_taken > self.number_of_pictures:
            print("Ending timelapse: " + str(datetime.now()))
            self.__exit__()


    def upload_to_s3(self, object, file_path, file_name):

        img_bytes = io.BytesIO()

        self.PIL_image.save(img_bytes, format="JPEG")

        b_image = img_bytes.getvalue()
        
        if file_path is not None:
            try:
                print(self.aws_config['s3_bucket'])
                # self.s3_client.upload_file(file_path, self.aws_config['s3_bucket'], file_name)
                self.s3_client.put_object(
                    Body=b_image,
                    Bucket=self.aws_config['s3_bucket'],
                    Key=file_name
                )
            except ClientError as e:
                print("Error", e)
        
        print("upload to s3:", file_name," #: ", self.pictures_taken)

    def __exit__(self):
        print("Exiting...")
        self.camera.stop()
        self.t.cancel()

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

if __name__ == '__main__':

    picamera_timelapse = PiTimeLapse("night_timelapse")