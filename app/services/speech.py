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
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models import models
from app.core.exceptions import DetectorException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SpeechService:
    """
    Mock implementation of speech-to-text service for development.
    Note: This implementation is for testing and development purposes only.
    Replace this with the Google Speech-to-Text service in production.
    """
    
    def __init__(self):
        """Initialize the mock speech service."""
        logger.info("Initializing Speech Service in mock mode")
        # Placeholder for the real speech-to-text client (set to None in mock mode)
        self.client = None
    
    def _mock_process_timestamps(
        self,
        movie_name: str,
        words_list: List[str],
        db: Session
    ) -> None:
        """
        Create mock timestamps for detected words.

        This method simulates the detection of words and assigns
        mock timestamps for each detected word.

        Args:
            movie_name: Name of the movie being processed.
            words_list: List of words to create mock detections for.
            db: Database session for storing results.
        """
        try:
            current_time = 0.0
            for word in words_list:
                # Simulate 2-second intervals for each word detection.
                start_time = current_time
                end_time = current_time + 2.0

                # Create a mock speech response entry for the database.
                speech_response = models.MovieSpeechResponse(
                    movie_name=movie_name,
                    words=word,
                    movie_start_time=str(start_time),
                    movie_stop_time=str(end_time)
                )
                db.add(speech_response)
                current_time += 3.0  # Add a 1-second gap between detections.

            # Commit the simulated results to the database.
            db.commit()
            
        except Exception as e:
            # Rollback in case of any error during the database operation.
            db.rollback()
            raise DetectorException(f"Error creating mock timestamps: {str(e)}")
    
    def _create_mock_stats(self, words_list: List[str]) -> Dict[str, Any]:
        """
        Generate mock statistics for speech processing.

        Args:
            words_list: List of words being processed.

        Returns:
            A dictionary containing mock statistics, including
            confidence scores, word counts, and processing duration.
        """
        return {
            "total_words_processed": len(words_list),
            "words_detected": len(words_list),
            "confidence_scores": [0.95] * len(words_list),  # Mock confidence scores.
            "average_confidence": 0.95,  # Mock average confidence.
            "processing_duration": f"{len(words_list) * 2.5:.2f}s"  # Mock duration based on word count.
        }
    
    async def process_audio(
        self,
        movie_name: str,
        words_list: List[str],
        db: Session
    ) -> Dict[str, Any]:
        """
        Mock implementation of audio processing.

        Simulates the detection of words in audio files without processing
        actual audio. Generates timestamps and statistics for the given words.

        Args:
            movie_name: Name of the movie being processed.
            words_list: List of words to detect.
            db: Database session for storing results.

        Returns:
            A dictionary containing mock processing results and statistics.
        """
        logger.info(f"Mock processing audio for movie: {movie_name}")
        logger.info(f"Processing {len(words_list)} words")
        
        try:
            # Simulate the detection of words and save timestamps.
            self._mock_process_timestamps(movie_name, words_list, db)
            
            # Generate mock processing statistics.
            stats = self._create_mock_stats(words_list)
            
            logger.info(f"Successfully processed mock audio for {movie_name}")
            
            return {
                "success": True,
                "movie_name": movie_name,
                "statistics": stats,
                "message": "Audio processed in mock mode (Google Speech-to-Text disabled)"
            }
            
        except Exception as e:
            # Log and raise an error if processing fails.
            error_msg = f"Error in mock processing: {str(e)}"
            logger.error(error_msg)
            db.rollback()
            raise DetectorException(error_msg)

    async def get_speech_results(
        self,
        movie_name: str,
        db: Session
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieve mock speech-to-text results for a specific movie.

        Args:
            movie_name: Name of the movie.
            db: Database session for querying results.

        Returns:
            A list of speech recognition results or mock data if no results exist.
        """
        logger.info(f"Getting mock speech results for movie: {movie_name}")
        
        try:
            # Query the database for existing results.
            results = db.query(models.MovieSpeechResponse).filter(
                models.MovieSpeechResponse.movie_name == movie_name
            ).all()
            
            if not results:
                # Return mock data if no results are found.
                logger.info(f"No results found for {movie_name}, returning mock data")
                return [{
                    "word": "mock_word",
                    "start_time": "0.0",
                    "stop_time": "1.0",
                    "confidence": 0.95  # Mock confidence score.
                }]
            
            # Convert database results to dictionary format.
            return [{
                "word": result.words,
                "start_time": result.movie_start_time,
                "stop_time": result.movie_stop_time,
                "confidence": 0.95  # Mock confidence score.
            } for result in results]
            
        except Exception as e:
            # Log and raise an error if retrieval fails.
            error_msg = f"Error retrieving mock results: {str(e)}"
            logger.error(error_msg)
            raise DetectorException(error_msg)

    async def batch_process_audio(
        self,
        movie_name: str,
        audio_files: List[str],
        words_list: List[str],
        db: Session
    ) -> List[Dict[str, Any]]:
        """
        Mock implementation of batch audio processing.

        Simulates the processing of multiple audio files in a batch.

        Args:
            movie_name: Name of the movie.
            audio_files: List of audio file paths (not used in mock mode).
            words_list: List of words to detect.
            db: Database session for storing results.

        Returns:
            A list of processing results for each audio file.
        """
        logger.info(f"Batch processing {len(audio_files)} audio files for {movie_name}")
        
        results = []
        for audio_file in audio_files:
            try:
                # Simulate audio processing for each file.
                result = await self.process_audio(
                    movie_name=movie_name,
                    words_list=words_list,
                    db=db
                )
                results.append(result)
                
            except Exception as e:
                # Log and add the error to the results if processing fails.
                logger.error(f"Error processing {audio_file}: {str(e)}")
                results.append({
                    "success": False,
                    "audio_file": audio_file,
                    "error": str(e)
                })
        
        return results
