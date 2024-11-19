from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker, relationship
import logging
from datetime import datetime, timezone

import pandas as pd
from sqlalchemy import select

import os

# Set up logging
logging.basicConfig(level=logging.INFO, filename='app.log', filemode='a',
                   format='%(asctime)s - %(levelname)s - %(message)s')

# Define the DATABASE_URL with sqlite
DATABASE_URL = 'sqlite:///DB/youtube_comments.db'   # local sqlite

# Create engine and base
engine = create_engine(DATABASE_URL)



class Base(DeclarativeBase):
    pass

# Define the two table models
class Video(Base):
    __tablename__ = 'videos'
    
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True, nullable=False)
    comments = relationship("Comment", back_populates="video")

class Comment(Base):
    __tablename__ = 'comments'
    
    id = Column(Integer, primary_key=True)
    video_id = Column(Integer, ForeignKey('videos.id'), nullable=False)
    author = Column(String, nullable=False)
    comment = Column(String, nullable=False)
    likes = Column(Integer)
    published_at = Column(DateTime)  # Removed timezone awareness
    is_toxic = Column(Boolean)
    
    video = relationship("Video", back_populates="comments")


# Create session factory
Session = sessionmaker(bind=engine)

def initialize_database():
    """Initialize database by creating all tables if they don't exist."""
    try:
        Base.metadata.create_all(engine)
        logging.info("Database initialized successfully")
        return True
    except Exception as e:
        logging.error(f"Error initializing database: {str(e)}")
        return False

def safe_str(value):
    """Convert any value to string, replacing None with 'N/A'"""
    return 'N/A' if value is None else str(value)

def safe_float(value):
    """Convert value to formatted float string, handling None values"""
    return 'N/A' if value is None else f"{float(value):.2f}"


from datetime import datetime, timezone

def store_db(video_url: str, data):
    """
    Store video comments in the database. If the video URL exists, only add new comments.
    If the video doesn't exist, create a new video entry and add all comments.
    
    Args:
        video_url (str): The URL of the video
        data (pd.DataFrame): DataFrame containing comment data
    """
    try:
        session = Session()
        
        # Check if video exists
        video = session.query(Video).filter_by(url=video_url).first()
        
        if not video:
            # Create new video entry
            video = Video(url=video_url)
            session.add(video)
            session.commit()
            logging.info(f"Created new video entry for URL: {video_url}")
            
            # Add all comments
            for _, row in data.iterrows():
                # Convert timestamp to naive datetime for storage
                naive_datetime = row['published_at'].tz_localize(None)
                
                comment = Comment(
                    video_id=video.id,
                    author=row['author'],
                    comment=row['comment'],
                    likes=row['likes'],
                    published_at=naive_datetime,
                    is_toxic=True if row['is_toxic'] == 'Yes' else False
                )
                session.add(comment)
            
            session.commit()
            logging.info(f"Added {len(data)} comments for new video: {video_url}")
            
        else:
            # Get the latest comment date for this video
            latest_comment = (session.query(Comment)
                            .filter_by(video_id=video.id)
                            .order_by(Comment.published_at.desc())
                            .first())
            
            if latest_comment:
                # Convert the DataFrame's timestamps to naive datetime for comparison
                naive_timestamps = data['published_at'].apply(lambda x: x.tz_localize(None))
                latest_naive = latest_comment.published_at
                
                # Create a mask for filtering
                new_comments = data[naive_timestamps > latest_naive]
            else:
                new_comments = data
            
            # Add only new comments
            for _, row in new_comments.iterrows():
                # Convert timestamp to naive datetime for storage
                naive_datetime = row['published_at'].tz_localize(None)
                
                comment = Comment(
                    video_id=video.id,
                    author=row['author'],
                    comment=row['comment'],
                    likes=row['likes'],
                    published_at=naive_datetime,
                    is_toxic=True if row['is_toxic'] == 'Yes' else False
                )
                session.add(comment)
            
            session.commit()
            logging.info(f"Added {len(new_comments)} new comments for existing video: {video_url}")
            
        return True
        
    except Exception as e:
        session.rollback()
        logging.error(f"Error storing data in database: {str(e)}")
        raise
        
    finally:
        session.close()



def export_comments_to_excel():
    """
    Export all comments from the database to an Excel file.
    The comments will be ordered by published_at date and saved to 'Data/historical_data.xlsx'
    """
    try:
        # Create Data directory if it doesn't exist
        os.makedirs('Data', exist_ok=True)
        
        session = Session()
        
        # Query to get all comments with video URLs, ordered by published_at
        query = select(
            Comment.author,
            Comment.comment,
            Comment.likes,
            Comment.published_at,
            Comment.is_toxic,
            Video.url.label('video_url')
        ).join(Video).order_by(Comment.published_at)
        
        # Execute query and fetch all results
        results = session.execute(query).all()
        
        # Convert results to DataFrame
        data = pd.DataFrame(results, columns=['author', 'comment', 'likes', 'published_at', 'is_toxic', 'video_url'])
        
        # Convert boolean is_toxic to 'Yes'/'No'
        data['is_toxic'] = data['is_toxic'].map({True: 'Yes', False: 'No'})
        
        # Convert datetime to the specified format
        data['published_at'] = data['published_at'].dt.strftime('%d/%m/%Y %H:%M:%S')
        
        # Save to Excel
        data.to_excel('Data/historical_data.xlsx', index=False)
        
        logging.info(f"Successfully exported {len(data)} comments to Data/historical_data.xlsx")
        return True
        
    except Exception as e:
        logging.error(f"Error exporting comments to Excel: {str(e)}")
        raise
        
    finally:
        session.close()