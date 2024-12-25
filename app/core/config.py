# Copyright (C) 2024 Mustafa Naseer
#
# This file is part of Movie Profanity Detector application.
#
# Movie Profanity Detector is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation version 3 of the License.
#
# Movie Profanity Detector is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Movie Profanity Detector. If not, see <http://www.gnu.org/licenses/>.

# Import necessary modules and dependencies
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List
from pathlib import Path
import os
import json

# Define a Settings class to manage application configuration
class Settings(BaseSettings):
    # General project settings
    PROJECT_NAME: str  # Name of the project
    DEBUG: bool  # Debug mode flag
    ENVIRONMENT: str  # Environment type (development, production)

    # Server settings
    HOST: str  # Host address
    PORT: int  # Port number

    # Database settings
    BASE_DIR: str = str(Path(__file__).resolve().parent.parent.parent)  # Base directory of the project
    DATABASE_URL: str  # Database connection URL

    # Directories for file uploads and output
    VIDEO_UPLOAD_DIR: str  # Directory for video uploads
    SRT_UPLOAD_DIR: str  # Directory for (SRT) uploads
    SOUND_OUTPUT_DIR: str  # Directory for sound output files

    # File upload settings
    MAX_UPLOAD_SIZE: int  # Maximum allowed size for file uploads (in .env file prefer is 100MB )
    ALLOWED_EXTENSIONS: List[str]  # List of allowed file extensions for uploads

    # API settings
    API_V1_PREFIX: str  # API version prefix

    # Method to get the video upload directory path
    def get_video_upload_path(self) -> str:
        # Combine base directory with the video upload directory
        path = os.path.join(self.BASE_DIR, self.VIDEO_UPLOAD_DIR)
        # Ensure the directory exists
        os.makedirs(path, exist_ok=True)
        return path

    # Method to get the subtitle upload directory path
    def get_srt_upload_path(self) -> str:
        path = os.path.join(self.BASE_DIR, self.SRT_UPLOAD_DIR)
        os.makedirs(path, exist_ok=True)
        return path

    # Method to get the sound output directory path
    def get_sound_output_path(self) -> str:
        path = os.path.join(self.BASE_DIR, self.SOUND_OUTPUT_DIR)
        os.makedirs(path, exist_ok=True)
        return path

    # Property to validate and parse allowed extensions
    @property
    def allowed_extensions_list(self) -> List[str]:
        if isinstance(self.ALLOWED_EXTENSIONS, str):
            return json.loads(self.ALLOWED_EXTENSIONS)
        return self.ALLOWED_EXTENSIONS

    # Configuration for environment variables and settings behavior
    model_config = SettingsConfigDict(
        env_file=".env",  # Path to the environment file
        env_file_encoding="utf-8",  # Encoding of the environment file
        case_sensitive=True,  # Make environment variable names case-sensitive
        extra="allow"
    )

# Function to get a cached instance of settings
@lru_cache()
def get_settings() -> Settings:
    return Settings()

# Create a settings instance for global use
settings = get_settings()
