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

from pydantic import BaseModel

# Base schema for words, used as a foundation for other schemas
class WordBase(BaseModel):
    words_detector: str

# Schema for creating a new word entry, inheriting from WordBase
class WordCreate(WordBase):
    pass  # No additional fields

# Schema for representing a word entry, including its ID
class Word(WordBase):
    id: int

    class Config:
        from_attributes = True
