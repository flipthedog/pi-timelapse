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

    def __init__(self, project_name, interval=300, number_of_images=-1, resolution=(1920, 1080), file_type="jpeg", \
        local_save_directory=None, save_to_s3=False, s3_bucket_name="", s3_path="", night_mode=True, exposure_time=10000000) -> None:
        """Create a timelapse

        Args:
            project_name (__str__): Project name
            interval (int, optional): Interval in seconds. Defaults to 300.
            number_of_images (int, optional): Total number of images, -1 for continuous. Defaults to -1.
            resolution (tuple, optional): Resolution of images to take. Defaults to (1920, 1080).
            file_type (str, optional): File type of image save. Defaults to "jpeg".
            save_to_s3 (bool, optional): Whether to save to AWS S3. Defaults to False.
            s3_bucket_name (str, optional): What bucket name to save to in S3. Defaults to "".
            s3_path (str, optional): What S3 Path to save to. Defaults to "".
            night_mode (bool, optional): Whether to engage night mode for long-exposure shots. Defaults to True.
            exposure_time (int, optional): Total exposure time (micro seconds). Defaults to 10000000 mus.
        """
        
        print("Starting the timelapse")
        print(f"Time/Date: {str(datetime.now())}")

        self.today_date = datetime.now().strftime("%Y_%m_%d")

        self.storage = ""
        self.current_cwd = os.getcwd()

        self.project_name = project_name + "_" + self.today_date

        if local_save_directory is not None:
            self.local_save_directory = local_save_directory
        else: 
            self.local_save_directory = None

        self.save_to_s3 = save_to_s3
        if save_to_s3:
            self.s3_bucket_name = s3_bucket_name
            self.s3_path = s3_path
        
        # with open("/home/pi/Projects/pi-timelapse/aws_details.conf", "r") as file:
        #     self.aws_config = yaml.safe_load(file)

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
            main={"size": resolution}, 
            transform=libcamera.Transform(vflip=0, hflip=0)
        )

        self.camera.configure(self.camera_config)
        
        if night_mode:
            self.camera.set_controls({
                "ExposureTime":exposure_time,
                "AnalogueGain": 1.0
            })

        # self.s3_client = boto3.client(
        #     's3',
        #     aws_access_key_id=self.aws_config['aws_access_key_id'],
        #     aws_secret_access_key=self.aws_config['aws_secret_access_key']
        # )

        self.s3_client = boto3.client(
            's3'
        )

        self.t = RepeatTimer(self.interval, self.take_picture)
        self.t.start()

    def take_picture(self):
        
        self.stream = BytesIO()

        current_epoch = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        printable_epoch = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

        self.camera.start()
        
        time.sleep(2)

        file_name = self.project_name + "_" + str(current_epoch) + "." + str(self.file_type)
        file_path = self.local_save_directory + '/' + file_name


        if self.local_save_directory:
            self.camera.capture_file(file_path, format=self.file_type)
        else:
            self.camera.capture_file(self.stream, format=self.file_type)
            self.stream.seek(0)
            self.PIL_image = Image.open(self.stream).convert('RGB')
        
        self.camera.stop()

        print("Took a picture at: ", str(datetime.now()) , " saved to: ", file_path)

        if self.save_to_s3:
            self.upload_to_s3(None, file_path=file_path, file_name=self.project_name + "/" + file_name)

        self.pictures_taken += 1

        if self.pictures_taken > self.number_of_pictures:
            print("Ending timelapse: " + str(datetime.now()))
            self.__exit__()


    def upload_to_s3(self, object, file_path, file_name):

        img_bytes = io.BytesIO()

        self.PIL_image.save(img_bytes, format=self.file_type)

        b_image = img_bytes.getvalue()
        
        if file_path is not None:
            try:
                print(self.s3_bucket_name)
                # self.s3_client.upload_file(file_path, self.aws_config['s3_bucket'], file_name)
                self.s3_client.put_object(
                    Body=b_image,
                    Bucket=self.s3_bucket_name,
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