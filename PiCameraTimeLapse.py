import cv2 as cv

import os
import time

from datetime import datetime
from threading import Timer

from picamera import PiCamera


class PiTimeLapse:

    def __init__(self, project_name, interval=5, length_of_timelapse="", resolution=(1920, 1080), file_type="*.jpg", local_save_directory=None, save_to_s3=False, s3_bucket_location="") -> None:
        
        self.storage = ""
        self.current_cwd = os.getcwd()

        self.project_name = project_name

        if local_save_directory is not None:
            self.local_save_directory = local_save_directory
        else: 
            self.local_save_directory = self.current_cwd

        self.save_path = self.local_save_directory + "/" + self.project_name

        self.interval = 0 # interval in seconds
        self.length_time = 0 # total length that the timelapse will be

        self.number_of_pictures = 0

        self.file_type = file_type

        self.camera = PiCamera()
        self.camera.resolution = resolution

        if not os.path.exists(self.save_path):
            
            os.makedirs(self.save_path)

        self.t = RepeatTimer(self.interval, self.take_picture)
        self.t.start()

    def take_picture(self):
        
        current_epoch = datetime.now().strftime("%Y-%m-%d_%H|%M|%S")

        self.camera.start_preview()
        
        time.sleep(2)

        file_path = self.save_path + '/' + self.project_name + "_" + str(current_epoch) + str(self.file_type)

        self.camera.capture(file_path)

        print("Took a picture at: ", str(datetime.now()) , " saved to: ", file_path)

    def upload_to_s3(self):
        pass

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

if __name__ == '__main__':

    picamera_timelapse = PiTimeLapse("timelapse/first_test")