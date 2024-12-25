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

from pydantic import BaseModel
from typing import Optional

# Base schema for video information
class VideoBase(BaseModel):
    movie_name: str
    movie_check_status: str = "not_check"

# Schema for creating a video entry
class VideoCreate(VideoBase):
    movie_path: str
    movie_srt_path: str

# Schema for representing a video entry, including its ID
class Video(VideoBase):
    id: int
    movie_path: str
    movie_srt_path: str

    class Config:
        from_attributes = True  # Allow population of fields from ORM attributes

# Schema for detected words in a movie or subtitle
class DetectedWord(BaseModel):
    movie_name: str
    words: str
    start_time: str
    stop_time: str
    sound_file_path: Optional[str] = None

    class Config:
        from_attributes = True  # Allow population of fields from ORM attributes
