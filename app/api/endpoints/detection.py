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
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import pysrt
import ffmpeg
import random
from app.models.database import get_db
from app.models import models
from app.schemas import videos
from app.core.config import get_settings
from app.services.speech import SpeechService

# Create an API router for video processing endpoints
router = APIRouter()
settings = get_settings()
speech_service = SpeechService()

# Endpoint to process subtitle files for a given video ID
"""
    - Fetches the video details from the database.
    - Loads the subtitle (SRT) file.
    - Checks each line of subtitles for words in database.
    - Stores detected words and their timestamps in the database.
"""
@router.post("/process-srt/{video_id}", response_model=List[videos.DetectedWord])
async def process_srt(video_id: int, db: Session = Depends(get_db)):
    # Fetch video details from the database if it hasn't been checked yet
    video = db.query(models.VideoInfo).filter(
        models.VideoInfo.id == video_id,
        models.VideoInfo.movie_check_status == "not_check"
    ).first()
    
    if not video:
        # Raise error if video is not found or already processed
        raise HTTPException(status_code=404, detail="Video not found or already processed")
    
    # Fetch the list of words to detect
    words_list = db.query(models.WordsList).all()
    if not words_list:
        raise HTTPException(status_code=404, detail="No words to check")
    
    detected_words = []
     # Load the subtitle file
    srt_file = pysrt.open(video.movie_srt_path)
    
    # Check each subtitle line for specified words
    for line in srt_file:
        for word in words_list:
            if word.words_detector.lower() in line.text.lower():
                """
                -Record the start and stop time of the detected word
                -Replace ths ',' to '.' so we can works with it 

                """
                start_time = str(line.start).replace(",", ".")
                stop_time = str(line.end).replace(",", ".")
                
                # Add detection to the database
                db_detection = models.SrtDetectorWords(
                    movie_name=video.movie_name,
                    words=word.words_detector,
                    srt_start_time=start_time,
                    srt_stop_time=stop_time
                )
                db.add(db_detection)
                detected_words.append(db_detection)
    
    # Mark the video as "checked" and save changes
    video.movie_check_status = "checked"
    db.commit()
    
    return detected_words  # Return the detected words

# Endpoint to process audio segments of a video based on SRT detections
"""
    - Extracts audio based on SRT word detections.
    - Generates audio files for each detected word.
    - Adds background tasks to process audio using speech-to-text services(you can use google speech).
"""
@router.post("/process-audio/{video_id}", response_model=List[videos.DetectedWord])
async def process_audio(
    video_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Fetch video details if its subtitles have already been processed
    video = db.query(models.VideoInfo).filter(
        models.VideoInfo.id == video_id,
        models.VideoInfo.movie_check_status == "checked"
    ).first()
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found or not processed by SRT")
    
    # Fetch detections for the given video
    detections = db.query(models.SrtDetectorWords).filter(
        models.SrtDetectorWords.movie_name == video.movie_name
    ).all()
    
    if not detections:
        raise HTTPException(status_code=404, detail="No detections found for this video")
    
    # List to store processed audio segments
    processed_words = []  
    gen_number_set = set() 
    
    for detection in detections:
        try:
            # Generate a unique number for the audio file
            create_number = random.randint(1, 1001)
            while create_number in gen_number_set:
                create_number = random.randint(1, 1001)
            gen_number_set.add(create_number)
            
            # Create the output filename for the audio segment
            output_file = f"upload_folder/sound_folder/{video.movie_name}-{create_number}.wav"
            
            # Use ffmpeg to extract the audio segment from the video
            """
            - Note: ffmpeg should be installed in your machine 
            """
            video_input = ffmpeg.input(video.movie_path, ss=detection.srt_start_time, t=detection.srt_stop_time)
            output_stream = ffmpeg.output(video_input, output_file, codec='libmp3lame', bitrate='320k')
            ffmpeg.run(output_stream, overwrite_output=True)
            
            # Create a database entry for the audio
            db_detection = models.MovieDetectorWords(
                movie_name=video.movie_name,
                words=detection.words,
                movie_start_time=detection.srt_start_time,
                movie_stop_time=detection.srt_stop_time,
                sound_file_path=output_file
            )
            db.add(db_detection)
            processed_words.append(db_detection)
            
            # Add a background task to process the audio using the speech service(you can use google speech)
            background_tasks.add_task(
                speech_service.process_audio,
                movie_name=video.movie_name,
                audio_file_path=output_file,
                words_list=[detection.words],
                db=db
            )
            
        except ffmpeg.Error as e:
            # Handle ffmpeg errors during audio extraction
            error_message = e.stderr.decode() if e.stderr else "Unknown error"
            raise HTTPException(
                status_code=500,
                detail=f"Error processing audio segment: {error_message}"
            )
    
    db.commit()  # Commit the processed audio segments to the database
    return processed_words  # Return the processed audio segments

# Endpoint to fetch detections for a specific video
"""
    - Queries the database for all word detections linked to the video.
    - Returns the list of detected words along with their timestamps.
"""
@router.get("/detections/{video_name}", response_model=List[videos.DetectedWord])
async def get_detections(video_name: str, db: Session = Depends(get_db)):
    detections = db.query(models.MovieDetectorWords).filter(
        models.MovieDetectorWords.movie_name == video_name
    ).all()
    
    if not detections:
        raise HTTPException(status_code=404, detail="No detections found for this video")
    
    return detections

# Endpoint to fetch speech-to-text results for a specific video
"""
    - Queries the database for speech-to-text results linked to the video.
    - Returns the list of words and their timestamps from the audio analysis.
"""
@router.get("/speech-results/{video_name}", response_model=List[videos.DetectedWord])
async def get_speech_results(video_name: str, db: Session = Depends(get_db)):
    results = db.query(models.MovieSpeechResponse).filter(
        models.MovieSpeechResponse.movie_name == video_name
    ).all()
    
    if not results:
        raise HTTPException(status_code=404, detail="No speech results found for this video")
    
    return results
