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
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import words, videos, detection
from app.models.database import engine, init_db
from app.models import models
from app.core.config import settings
# Initialize the database and create tables if they don't exist
init_db()

# Create FastAPI application instance with project settings
app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG
)

# Configure Cross-Origin Resource Sharing (CORS) middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the words router with a prefix and tag for API documentation
app.include_router(words.router, prefix=f"{settings.API_V1_PREFIX}/words", tags=["words"])

# Include the videos router with a prefix and tag for API documentation
app.include_router(videos.router, prefix=f"{settings.API_V1_PREFIX}/videos", tags=["videos"])

# Include the detection router with a prefix and tag for API documentation
app.include_router(detection.router, prefix=f"{settings.API_V1_PREFIX}/detection", tags=["detection"])

# Define the root endpoint
@app.get("/")
async def root():
    # Return a success message with project information
    return {
        "status": "success",
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "environment": settings.ENVIRONMENT
    }
