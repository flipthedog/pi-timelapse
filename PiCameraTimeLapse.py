import cv2 as cv
import numpy as np

import sys

# To load picamera
sys.path.append('/usr/lib/python3/dist-packages')

import os
import time

from datetime import datetime
from threading import Timer

from picamera2 import Picamera2

import boto3

from botocore.exceptions import ClientError

from io import BytesIO

from PIL import Image

class PiTimeLapse:

    def __init__(self, project_name, interval=300, length_of_timelapse="", resolution=(1920, 1080), file_type="jpeg", \
         local_save_directory=None, save_to_s3=False, s3_bucket_location="") -> None:
        
        print("Starting the timelapse")
        
        self.storage = ""
        self.current_cwd = "/home/pi/Projects/pi-timelapse"

        self.project_name = project_name

        if local_save_directory is not None:
            self.local_save_directory = local_save_directory
        else: 
            self.local_save_directory = self.current_cwd

        self.save_path = self.local_save_directory + "/timelapse/" + self.project_name

        self.interval = interval # interval in seconds
        self.length_time = 0 # total length that the timelapse will be, in hours

        self.number_of_pictures = (self.length_time * 60 * 60) / self.interval
        self.pictures_taken = 0

        self.file_type = file_type

        self.stream = BytesIO()
        self.PIL_image = None
        self.cv_image = None

        self.camera = Picamera2()
        self.camera.resolution = resolution

        self.s3_client = boto3.client(
            's3'
        )

        if not os.path.exists(self.save_path):
            
            os.makedirs(self.save_path)

        self.t = RepeatTimer(self.interval, self.take_picture)
        self.t.start()

    def take_picture(self):
        
        self.stream = BytesIO()

        current_epoch = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        printable_epoch = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

        self.camera.start_preview()
        
        time.sleep(2)

        file_name = self.project_name + "_" + str(current_epoch) + "." + str(self.file_type)
        file_path = self.save_path + '/' + file_name

        self.camera.capture(self.stream, format=self.file_type)
        # self.camera.capture(file_path)
        
        self.stream.seek(0)

        self.PIL_image = Image.open(self.stream).convert('RGB')
        self.cv_image = np.array(self.PIL_image)
        self.cv_image = self.cv_image[:, :, ::-1].copy()

        size = self.cv_image.shape

        self.cv_image = cv.putText(self.cv_image, org=(0,size[0]-20), fontFace=0, text=str(current_epoch), \
                        fontScale=1, color=(0,255,0), thickness=2)
        
        # print(file_path)
        # cv.imwrite(file_path, self.cv_image)

        print("Took a picture at: ", str(datetime.now()) , " saved to: ", file_path)

        self.upload_to_s3(None, file_path=file_path, file_name=file_name)

        self.pictures_taken += 1

    def upload_to_s3(self, object, file_path, file_name):
        
        b_image = cv.imencode('.jpeg', self.cv_image)[1].tobytes()
        
        if file_path is not None:
            try:
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
        self.t.cancel()

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

if __name__ == '__main__':

    picamera_timelapse = PiTimeLapse("first_test")