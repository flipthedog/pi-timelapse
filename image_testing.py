from picamera2 import Picamera2
import numpy as np
import libcamera
import time
from PIL import Image

from io import BytesIO


camera = Picamera2()
camera.options["quality"] = 95
camera.options["compress_level"] = 2

camera_config = camera.create_still_configuration(
    main={"size": (1280, 720)}, 
    transform=libcamera.Transform(vflip=1, hflip=1)
)
camera.configure(camera_config)

camera.start()
        
time.sleep(1)

stream = BytesIO()

camera.capture_file(stream, format="jpeg")
metadata = camera.capture_metadata()
stream.seek(0)
PIL_image = Image.open(stream).convert('RGB')

np_image = np.array(PIL_image)
brightness = np.average(np.linalg.norm(np_image, axis=2)) / np.sqrt(3)

print(int(brightness))
PIL_image.save("test2.jpeg")

camera.stop()
