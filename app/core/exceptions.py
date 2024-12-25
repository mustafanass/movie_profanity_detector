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
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Union

# Custom exception for detector-related errors
class DetectorException(Exception):
    def __init__(self, message: str):
        # Initialize the exception with a custom message
        self.message = message

# Custom exception handler for DetectorException
async def detector_exception_handler(
    request: Request,
    exc: DetectorException
) -> JSONResponse:
    # Return a JSON response with a status code of 400 and the exception message
    return JSONResponse(
        status_code=400,
        content={"message": exc.message}
    )

# Custom exception for file upload errors
class FileUploadError(Exception):
    def __init__(
        self,
        message: str = "File upload error",
        errors: Union[str, list] = None
    ):
        # Initialize the exception with a message and optional error details
        self.message = message
        self.errors = errors

# Custom exception handler for FileUploadError
async def file_upload_exception_handler(
    request: Request,
    exc: FileUploadError
) -> JSONResponse:
    # Return a JSON response with a status code of 400, the exception message, and any additional error details
    return JSONResponse(
        status_code=400,
        content={
            "message": exc.message,
            "errors": exc.errors
        }
    )
