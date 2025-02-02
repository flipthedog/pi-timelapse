from typing import List, Dict

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Resolution(BaseModel):
    height: int
    width: int

class TimeLapseConf(BaseSettings):

    project_name: str
    interval: int
    number_of_images: int

    resolution: Resolution
    file_type: str

    save_local: bool
    local_save_path: str

    save_to_cloud: bool
    s3_bucket: str
    s3_path: str

    night_mode: bool
    night_mode_exposure: int

    latitude: float
    longitude: float