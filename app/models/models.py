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

from sqlalchemy import Column, Integer, String
from .database import Base

# Define the WordsList table
class WordsList(Base):
    __tablename__ = "movie_words_lists"  # Table name in the database
    
    id = Column(Integer, primary_key=True, index=True)
    words_detector = Column(String(200))

# Define the VideoInfo table
class VideoInfo(Base):
    __tablename__ = "movie_video_info"  # Table name in the database
    
    id = Column(Integer, primary_key=True, index=True)
    movie_name = Column(String(200))
    movie_path = Column(String(200))
    movie_srt_path = Column(String(200))
    movie_check_status = Column(String(200))

# Define the SrtDetectorWords table
class SrtDetectorWords(Base):
    __tablename__ = "srt_detector_words"  # Table name in the database
    
    id = Column(Integer, primary_key=True, index=True)
    movie_name = Column(String(200))
    words = Column(String(200))
    srt_start_time = Column(String(200))
    srt_stop_time = Column(String(200))

# Define the MovieDetectorWords table
class MovieDetectorWords(Base):
    __tablename__ = "movie_detector_words"  # Table name in the database
    
    id = Column(Integer, primary_key=True, index=True)
    movie_name = Column(String(200))
    words = Column(String(200))
    movie_start_time = Column(String(200))
    movie_stop_time = Column(String(200))
    sound_file_path = Column(String(200))

# Define the MovieSpeechResponse table
class MovieSpeechResponse(Base):
    __tablename__ = "movie_speech_resposn"  # Table name in the database
    
    id = Column(Integer, primary_key=True, index=True)
    movie_name = Column(String(200))
    words = Column(String(200))
    movie_start_time = Column(String(200))
    movie_stop_time = Column(String(200))
