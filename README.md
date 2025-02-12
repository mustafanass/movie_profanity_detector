# movie profanity detector

A python and FastApi application for detecting and analyzing profanity in movies through subtitle processing and audio analysis.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Configuration](#configuration)
- [Database Models](#database-models)
- [Services](#services)

## Features
- Upload and manage video files with subtitles (SRT)
- Detect specific words in subtitle files
- Extract and process audio segments
- Mock speech-to-text analysis
- RESTful API endpoints for all operations

## Installation

### Prerequisites
- Python 3.8+
- FFmpeg
- SQLite

### Environment Setup
1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Install dependencies in (requirements.txt) file :
```bash
pip install -r requirements.txt 
```

3. Configure environment variables in `.env`:
```env
PROJECT_NAME=Video Processing API
DEBUG=True
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite:///./app.db
MAX_UPLOAD_SIZE=104857600
ALLOWED_EXTENSIONS=["mp4","avi","srt"]
API_V1_PREFIX=/api/v1
```

## Project Structure
```
app/
├── api/
│   └── endpoints/
│       ├── detection.py    # Word detection endpoints
│       ├── videos.py       # Video upload/management
│       └── words.py        # Words list management
├── core/
│   ├── config.py          # Application configuration
│   └── exceptions.py      # Custom exceptions
├── models/
│   ├── database.py        # Database configuration
│   └── models.py          # SQLAlchemy models
├── schemas/
│   ├── videos.py          # Pydantic models for videos
│   └── words.py           # Pydantic models for words
├── services/
│   ├── detector.py        # Video/audio processing
│   └── speech.py          # Speech-to-text service
└── main.py               # Application entry point
```

## API Endpoints

### Videos
- `POST /api/v1/videos/upload`
  - Upload video with SRT file
  - Parameters:
    - `video_name`: String (form data)
    - `video`: File
    - `srt`: File
  
- `GET /api/v1/videos/`
  - List all videos
  - Parameters:
    - `skip`: int (optional)
    - `limit`: int (optional)

### Word Detection
- `POST /api/v1/detection/process-srt/{video_id}`
  - Process SRT file for word detection
  
- `POST /api/v1/detection/process-audio/{video_id}`
  - Extract and process audio segments
  
- `GET /api/v1/detection/detections/{video_name}`
  - Get word detections for a video
  
- `GET /api/v1/detection/speech-results/{video_name}`
  - Get speech-to-text results

### Words Management
- `POST /api/v1/words/`
  - Add new word to detection list
  
- `GET /api/v1/words/`
  - List all words in detection list

## Database Models

### VideoInfo
- `id`: Integer (Primary Key)
- `movie_name`: String
- `movie_path`: String
- `movie_srt_path`: String
- `movie_check_status`: String

### WordsList
- `id`: Integer (Primary Key)
- `words_detector`: String

### SrtDetectorWords
- `id`: Integer (Primary Key)
- `movie_name`: String
- `words`: String
- `srt_start_time`: String
- `srt_stop_time`: String

### MovieDetectorWords
- `id`: Integer (Primary Key)
- `movie_name`: String
- `words`: String
- `movie_start_time`: String
- `movie_stop_time`: String
- `sound_file_path`: String

## Services

### DetectorService
Handles video processing and word detection:
- SRT file analysis
- Audio segment extraction
- Word timestamp generation

### SpeechService
Mock implementation of speech-to-text service:
- Simulated audio processing
- Mock confidence scores
- Batch processing capabilities

## Asynchronous Processing

The application is updated to fully support asynchronous operations to handle I/O-bound tasks efficiently:

- **SRT File Analysis:**  
  The SRT file is parsed asynchronously using `DetectorService.check_srt_async`, which offloads the file reading and processing to a separate thread via `asyncio.to_thread`.

- **Audio Extraction:**  
  Audio segments are extracted asynchronously using FFmpeg. The `DetectorService.extract_audio_segments` method creates concurrent tasks (using `asyncio.gather`) to run FFmpeg as an asynchronous subprocess. This design ensures that multiple audio extractions can occur in parallel without blocking the main API thread.

These design choices contribute to the scalability and responsiveness of the API.

## Notes
- The speech service is currently in mock mode for development
- File uploads are limited to specified extensions
- Audio is extracted in WAV format
- Timestamps use "." instead of "," for compatibility
- The speech service uses a mock implementation by default. To use Google Speech-to-Text:
  1. Set up Google Cloud credentials
  2. Replace the mock implementation in `speech.py` with Google Speech-to-Text API calls
  3. Update environment variables with Google Cloud configuration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Author
Build and Developed by Mustafa Naseer

This project is intended for development and testing purposes. For production use, please ensure proper configuration of external services and security measures.
