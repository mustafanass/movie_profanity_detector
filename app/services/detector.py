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
import asyncio
from app.core.config import get_settings

# Initialize settings for the application
settings = get_settings()

# Service class for handling detection and audio extraction operations
"""
 -(check_srt) Check SRT file for profanity words .
 -(check_srt_async) Use (check_srt) as asynchronous method .
 -(extract_audio_segments) Extract audio segments from video based on detected words .
 -(extract_audio_segments_async) Use (extract_audio_segments) as asynchronous method .
"""
class DetectorService:
    @staticmethod
    async def check_srt_async(srt_path: str, words_list: List[str]) -> List[Dict[str, Any]]:
        return await asyncio.to_thread(DetectorService.check_srt, srt_path, words_list)
                
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
                        # Replace the (",") with (".") because ffmpeg does not support (,)
                        "start_time": str(line.start).replace(",", "."),
                        "stop_time": str(line.end).replace(",", "."),
                        "context": line.text
                    })
        
        return detected_words
        
    @staticmethod
    async def extract_audio_segment_async(video_path: str, detection: Dict[str, Any], movie_name: str) -> str:
        # Generate a unique file name as before
        create_number = random.randint(1, 1001)
        output_file = os.path.join(
            settings.SOUND_OUTPUT_DIR,
            f"{movie_name}-{create_number}.wav"
        )

        # Prepare the FFmpeg command
        command = [
            "ffmpeg",
            "-ss", detection["start_time"],
            "-i", video_path,
            "-t", detection["stop_time"],
            "-acodec", "libmp3lame",
            "-b:a", "320k",
            output_file,
            "-y"  # Overwrite output file if it exists
        ]

        # Launch the FFmpeg process asynchronously
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_message = stderr.decode().strip()
            raise Exception(f"FFmpeg error: {error_message}")

        return output_file

    @staticmethod
    async def extract_audio_segments(video_path: str, detections: List[Dict[str, Any]], movie_name: str) -> List[Dict[str, Any]]:
        # Create a list of tasks using the asynchronous extraction method
        tasks = [
            DetectorService.extract_audio_segment_async(video_path, detection, movie_name)
            for detection in detections
        ]

        # Run all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        audio_segments = []
        for detection, result in zip(detections, results):
            if isinstance(result, Exception):
                print(f"Error extracting audio segment for detection {detection}: {result}")
            else:
                audio_segments.append({
                    **detection,
                    "audio_path": result
                })

        return audio_segments

