# import cv2 as cv
import sys

# To load picamera
sys.path.append('/usr/lib/python3/dist-packages')

import os
import io
import requests

import time
from datetime import datetime, timedelta
from threading import Timer

from picamera2 import Picamera2

import boto3
from botocore.exceptions import ClientError

from io import BytesIO
from PIL import Image

import yaml

import libcamera

from src.conf.picamera_timelapse_conf import TimeLapseConf

class PiTimeLapse:

    def __init__(self, config: TimeLapseConf) -> None:
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
        
        self.config = config

        print("Starting the timelapse")
        print(f"Time/Date: {str(datetime.now())}")

        self.today_date = datetime.now().strftime("%Y_%m_%d")

        self.current_cwd = os.getcwd()

        self.project_name = config.project_name

        print(f"Project Name: {self.project_name}")
        
        self.save_local = config.save_local
        
        # check if the local save path exists
        if not os.path.exists(self.current_cwd + "/" + self.project_name):
            os.makedirs(self.current_cwd + "/" + self.project_name)
        

        if self.save_local:
            self.local_save_path = self.current_cwd + "/" + self.project_name + "/" + config.local_save_path
        else: 
            self.local_save_path = ""

        self.save_to_cloud = config.save_to_cloud

        if config.save_to_cloud:
            self.s3_bucket = config.s3_bucket 
            self.s3_path = config.s3_path

        self.interval = config.interval # interval in seconds
        self.length_time = 0 # total length that the timelapse will be, in hours

        if config.number_of_images == -1:
            self.number_of_pictures = 1e16
        else:    
            self.number_of_pictures = config.number_of_images
        
        self.pictures_taken = 0

        self.file_type = config.file_type

        self.stream = BytesIO()
        self.PIL_image = None
        self.cv_image = None

        self.camera = Picamera2()
        
        self.resolution = (config.resolution.width, config.resolution.height)

        self.camera_config = self.camera.create_still_configuration(
            main={"size": self.resolution}, 
            transform=libcamera.Transform(vflip=1, hflip=1)
        )

        self.camera.configure(self.camera_config)
        
        self.lat = config.latitude
        self.long = config.longitude

        self.s3_client = boto3.client(
            's3'
        )

        self.take_picture()

        self.t = RepeatTimer(self.interval, self.take_picture)
        self.t.start()

    def take_picture(self):
        
        if self.night_mode():
            self.camera.set_controls({
                "ExposureTime":self.config.night_mode_exposure,
                "AnalogueGain": 1.0
            })

        self.stream = BytesIO()

        current_epoch = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        printable_epoch = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

        self.camera.start()
        
        time.sleep(2)

        file_name = self.project_name + "_" + str(current_epoch) + "." + str(self.file_type)
        
        self.camera.capture_file(self.stream, format=self.file_type)
        self.stream.seek(0)
        self.PIL_image = Image.open(self.stream).convert('RGB')
        
        self.camera.stop()

        
        if self.save_local:
            self.PIL_image.save(self.local_save_path + "/" + file_name, format=self.file_type)
            
        print("Took a picture at: ", str(datetime.now()) , " saved to: ", self.s3_path)

        if self.save_to_cloud:
            self.upload_to_s3(None, file_path=self.s3_path, file_name=self.project_name + "/" + file_name)

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
                self.s3_client.put_object(
                    Body=b_image,
                    Bucket=self.s3_bucket,
                    Key=file_name
                )
            except ClientError as e:
                print("Error", e)
        
        print("upload to s3:", file_name," #: ", self.pictures_taken)

    def __exit__(self):
        print("Exiting...")
        self.camera.stop()
        self.t.cancel()

    def get_sunrise_sunset(self):

        url = f"https://api.sunrisesunset.io/json?lat={self.lat}&lng={self.long}&time_format=24"

        response = requests.get(url)

        data = response.json()["results"]
        sunrise = data["sunrise"]
        sunset = data["sunset"]
        first_light = data["first_light"]
        last_light = data["last_light"]

        return sunrise, sunset, first_light, last_light
    
    def night_mode(self):
        """"
        Decide whether we need to engage night mode
        """

        sunrise, sunset, first_light, last_light = self.get_sunrise_sunset()

        current_time = (datetime.now()).strftime("%H:%M:%S")

        if current_time < sunrise:
            print("Night mode on") 
            return True
        elif current_time > last_light:
            print("Night mode on")
            return True
        else:
            print("Night mode off")
            return False
       
class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

if __name__ == '__main__':

    picamera_timelapse = PiTimeLapse("night_timelapse")
