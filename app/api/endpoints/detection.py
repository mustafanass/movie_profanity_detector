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
from DetectorService import DetectorService
from app.models.database import get_db
from app.models import models
from app.schemas import videos
from app.core.config import get_settings
from app.services.speech import SpeechService

# Create an API router and settings for video processing endpoints
router = APIRouter()
settings = get_settings()
speech_service = SpeechService()


# Endpoint to process subtitle files for a given video ID
@router.post("/process-srt/{video_id}",
             response_model=List[videos.DetectedWord])
async def process_srt(video_id: int, db: Session = Depends(get_db)):
    # Fetch video details from the database if it hasn't been checked yet
    video = db.query(models.VideoInfo).filter(
        models.VideoInfo.id == video_id,
        models.VideoInfo.movie_check_status == "not_check").first()

    if not video:
        raise HTTPException(status_code=404,
                            detail="Video not found or already processed")

    # Fetch the list of words to detect
    words_list = db.query(models.WordsList).all()
    if not words_list:
        raise HTTPException(status_code=404, detail="No words to check")

    # Prepare a list of words (strings) from the database records
    word_strings = [word.words_detector for word in words_list]

    # Use the asynchronous method to process the SRT file
    srt_detections = await DetectorService.check_srt_async(
        video.movie_srt_path, word_strings)

    # srt_detections is a list of dicts:
    db_detections = []
    for detection in srt_detections:
        db_detection = models.SrtDetectorWords(
            movie_name=video.movie_name,
            words=detection["word"],
            srt_start_time=detection["start_time"],
            srt_stop_time=detection["stop_time"])
        db.add(db_detection)
        db_detections.append(db_detection)

    # Mark the video as "checked" and save changes
    video.movie_check_status = "checked"
    db.commit()

    return db_detections


# Endpoint to process audio segments of a video based on SRT detections
@router.post("/process-audio/{video_id}",
             response_model=List[videos.DetectedWord])
async def process_audio(video_id: int,
                        background_tasks: BackgroundTasks,
                        db: Session = Depends(get_db)):
    # Fetch video details if its subtitles have already been processed
    video = db.query(models.VideoInfo).filter(
        models.VideoInfo.id == video_id,
        models.VideoInfo.movie_check_status == "checked").first()

    if not video:
        raise HTTPException(status_code=404,
                            detail="Video not found or not processed by SRT")

    # Fetch detections for the given video from the database
    detections = db.query(models.SrtDetectorWords).filter(
        models.SrtDetectorWords.movie_name == video.movie_name).all()

    if not detections:
        raise HTTPException(status_code=404,
                            detail="No detections found for this video")

    # Convert detection objects into dictionaries expected by the async service method.
    detection_dicts = []
    for detection in detections:
        detection_dicts.append({
            "word": detection.words,
            "start_time": detection.srt_start_time,
            "stop_time": detection.srt_stop_time,
            # Optionally, include additional fields such as context if needed.
        })

    # Call the asynchronous method to extract audio segments concurrently.
    audio_results = await DetectorService.extract_audio_segments(
        video.movie_path, detection_dicts, video.movie_name)

    # audio_results is a list of dictionaries that include an "audio_path" key along with the original detection data.
    processed_words = []
    for result in audio_results:
        # Create a new database record for each processed audio segment.
        db_detection = models.MovieDetectorWords(
            movie_name=video.movie_name,
            words=result["word"],
            movie_start_time=result["start_time"],
            movie_stop_time=result["stop_time"],
            sound_file_path=result["audio_path"])
        db.add(db_detection)
        processed_words.append(db_detection)

        # Optionally, add a background task to further process the audio (e.g., speech-to-text)
        background_tasks.add_task(speech_service.process_audio,
                                  movie_name=video.movie_name,
                                  audio_file_path=result["audio_path"],
                                  words_list=[result["word"]],
                                  db=db)

    # Commit all changes to the database.
    db.commit()
    return processed_words  # Return the list of processed audio segments


# Endpoint to fetch detections for a specific video
@router.get("/detections/{video_name}",
            response_model=List[videos.DetectedWord])
async def get_detections(video_name: str, db: Session = Depends(get_db)):
    detections = db.query(models.MovieDetectorWords).filter(
        models.MovieDetectorWords.movie_name == video_name).all()

    if not detections:
        raise HTTPException(status_code=404,
                            detail="No detections found for this video")

    return detections


# Endpoint to fetch speech-to-text results for a specific video
@router.get("/speech-results/{video_name}",
            response_model=List[videos.DetectedWord])
async def get_speech_results(video_name: str, db: Session = Depends(get_db)):
    results = db.query(models.MovieSpeechResponse).filter(
        models.MovieSpeechResponse.movie_name == video_name).all()

    if not results:
        raise HTTPException(status_code=404,
                            detail="No speech results found for this video")

    return results
