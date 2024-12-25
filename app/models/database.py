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
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import os 

# Ensure the directory for the SQLite database exists 
"""
 -This replaces the 'sqlite:///' prefix in the DATABASE_URL with an empty string to get the directory path
 -Create the database engine using the connection URL from settings
 -The connect_args parameter is used to configure SQLite-specific options
"""
os.makedirs(os.path.dirname(settings.DATABASE_URL.replace('sqlite:///', '')), exist_ok=True)
engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)

"""
 -Create a session maker factory
 -autocommit=False: Changes are committed manually
 -autoflush=False: Changes are not automatically flushed to the database
 -bind=engine: Bind the session to the database engine

"""
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declare the base class for ORM models
Base = declarative_base()

# Initialize the database by creating all tables defined in the ORM models
def init_db():
    Base.metadata.create_all(bind=engine)

# Define a dependency for creating and managing database sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
