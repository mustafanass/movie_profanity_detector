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
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import List
import shutil
import os
from app.models.database import get_db
from app.models import models
from app.schemas import videos
from app.core.config import get_settings

# Initialize an API router for organizing video-related endpoints
router = APIRouter()
settings = get_settings()

def allowed_file(filename: str) -> bool:
    """
    - Ensures the uploaded file has an extension that matches the allowed list in settings.
    - Returns True if valid, otherwise False.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in settings.ALLOWED_EXTENSIONS

@router.post("/upload", response_model=videos.Video)
async def upload_video(
    # Form field to receive the video name and video file and SRT file and DB sessions
    video_name: str = Form(...),  
    video: UploadFile = File(...),
    srt: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Endpoint to upload a video and its corresponding SRT file.

    - Validates file types using the allowed_file function.
    - Saves the uploaded video and SRT files to designated directories.
    - Adds a record to the database for the uploaded video.
    """
    # Check if the uploaded files have valid extensions
    if not (allowed_file(video.filename) and allowed_file(srt.filename)):
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    # Save the uploaded video file to the designated directory
    video_path = os.path.join(settings.VIDEO_UPLOAD_DIR, video.filename)
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(video.file, buffer)
    
    # Save the uploaded SRT file to the designated directory
    srt_path = os.path.join(settings.SRT_UPLOAD_DIR, srt.filename)
    with open(srt_path, "wb") as buffer:
        shutil.copyfileobj(srt.file, buffer)
    
    # Create a new record in the database for the uploaded video
    db_video = models.VideoInfo(
        movie_name=video_name,
        movie_path=f"upload_folder/video_upload/videos/{video.filename}",
        movie_srt_path=f"upload_folder/video_upload/srtfiles/{srt.filename}",
        movie_check_status="not_check"
    )
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video

@router.get("/", response_model=List[videos.Video])
def get_videos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    - Supports pagination using 'skip' and 'limit' query parameters.
    - Returns a list of video records from the database.
    """
    return db.query(models.VideoInfo).offset(skip).limit(limit).all()
