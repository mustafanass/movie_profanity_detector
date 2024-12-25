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
from pathlib import Path
import pysrt
from typing import List, Dict, Any
import ffmpeg
import random
import os
from app.core.config import get_settings

# Initialize settings for the application
settings = get_settings()

# Service class for handling detection and audio extraction operations
"""
 -(check_srt) Check SRT file for profanity words
 -(extract_audio_segments) Extract audio segments from video based on detected words
"""
class DetectorService:
    @staticmethod
    def check_srt(srt_path: str, words_list: List[str]) -> List[Dict[str, Any]]:
        detected_words = []
        srt_file = pysrt.open(srt_path)
        # Iterate through each line in the SRT file
        for line in srt_file:
            for word in words_list:
                # Case-insensitive match
                if word.lower() in line.text.lower(): 
                    detected_words.append({
                        "word": word,
                        "start_time": str(line.start).replace(",", "."),
                        "stop_time": str(line.end).replace(",", "."),
                        "context": line.text
                    })
        
        return detected_words
    

    @staticmethod
    async def extract_audio_segments(
        video_path: str,
        detections: List[Dict[str, Any]],
        movie_name: str
    ) -> List[Dict[str, Any]]:
        audio_segments = []
        gen_number_set = set()
        
        for detection in detections:
            try:
                # Generate random unique number for the audio file name
                create_number = random.randint(1, 1001) 
                # Ensure Generated number is unique
                while create_number in gen_number_set:
                    create_number = random.randint(1, 1001)
                gen_number_set.add(create_number)
                
                # Create the output file path for the audio segment
                output_file = os.path.join(
                    settings.SOUND_OUTPUT_DIR,
                    f"{movie_name}-{create_number}.wav"
                )
                
                # Extract the audio segment using ffmpeg
                video_input = ffmpeg.input(
                    video_path,
                    ss=detection["start_time"],
                    t=detection["stop_time"]
                )
                output_stream = ffmpeg.output(
                    video_input,
                    output_file,
                    codec='libmp3lame',
                    bitrate='320k'
                )
                ffmpeg.run(output_stream)
                
                # Append the detection and audio path to the list
                audio_segments.append({
                    **detection,
                    "audio_path": output_file
                })
            # Handle ffmpeg errors
            except ffmpeg.Error as e:
                print(f"Error extracting audio segment: {str(e)}")
                continue
        
        return audio_segments
