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
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.models.database import get_db
from app.models import models
from app.schemas import words

# Create a router instance for defining endpoints
router = APIRouter()

# Define a POST endpoint to create a new word entry
"""
 -The endpoint accepts a WordCreate schema as input and returns a Word schema as a response

"""
# 
@router.post("/", response_model=words.Word)
def create_word(word: words.WordCreate, db: Session = Depends(get_db)):
    # Check if the word already exists in the database
    db_word = db.query(models.WordsList).filter(
        models.WordsList.words_detector == word.words_detector
    ).first()
    if db_word:
        raise HTTPException(status_code=400, detail="Word already exists")
    # Create a new word entry and add it to the database
    db_word = models.WordsList(words_detector=word.words_detector)
    db.add(db_word)
    db.commit()
    db.refresh(db_word)
    return db_word

# Define a GET endpoint to retrieve a list of words
"""
 -The endpoint accepts optional query parameters for pagination 
 -Query the database to retrieve words with pagination

"""
@router.get("/", response_model=List[words.Word])
def get_words(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.WordsList).offset(skip).limit(limit).all()
