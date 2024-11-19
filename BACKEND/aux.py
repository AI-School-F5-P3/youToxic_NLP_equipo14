from transformers import AutoModelForSequenceClassification, AutoTokenizer

from googleapiclient.discovery import build
import pandas as pd
from urllib.parse import urlparse, parse_qs
import os
import re

import matplotlib.pyplot as plt
import seaborn as sns

from datetime import datetime
from fastapi import HTTPException


# Replace with your API key
API_KEY = "xxxxxxxxxxxxxxx"

def get_video_id(url):
    """Extract video ID from YouTube URL"""
    parsed_url = urlparse(url)
    if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query)['v'][0]
    elif parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    raise ValueError('Invalid YouTube URL')

def get_video_comments(api_key, video_url, max_results=200):
    """
    Fetch comments from a YouTube video and return them in a pandas DataFrame
    
    Parameters:
    api_key (str): YouTube Data API key
    video_url (str): URL of the YouTube video
    max_results (int): Maximum number of comments to fetch
    
    Returns:
    pandas.DataFrame: DataFrame containing comments data
    """
    try:
        # Create YouTube API client
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        # Get video ID from URL
        video_id = get_video_id(video_url)
        
        # Get comments
        comments_list = []
        request = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=max_results,
            textFormat='plainText',
            order='time'
        )
        
        while request and len(comments_list) < max_results:
            response = request.execute()
            
            for item in response['items']:
                comment = item['snippet']['topLevelComment']['snippet']
                comments_list.append({
                    'author': comment['authorDisplayName'],
                    'comment': comment['textDisplay'],
                    'likes': comment['likeCount'],
                    'published_at': comment['publishedAt']
                })
            
            # Get next page of comments if available
            request = youtube.commentThreads().list_next(request, response)
            
        # Create DataFrame
        df = pd.DataFrame(comments_list)
        
        # Convert published_at to datetime
        df['published_at'] = pd.to_datetime(df['published_at'])
        
        return df
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


class TextCleaner():
    def __init__(self):
        pass

    def clean_text(self, text):
        text = text.lower()
        text = re.sub(r'<.*?>', '', text)
        text = re.sub(r'http\S+', '', text)
        text = re.sub(r"what's", "what is ", text)
        text = re.sub(r"\'s", " ", text)
        text = re.sub(r"\'ve", " have ", text)
        text = re.sub(r"can't", "cannot ", text)
        text = re.sub(r"n't", " not ", text)
        text = re.sub(r"i'm", "i am ", text)
        text = re.sub(r"\'re", " are ", text)
        text = re.sub(r"\'d", " would ", text)
        text = re.sub(r"\'ll", " will ", text)
        text = re.sub(r"\'scuse", " excuse ", text)
        text = re.sub('\W', ' ', text)
        text = re.sub('\s+', ' ', text)
        text = re.sub(r'[^\u0000-\u007F]+', '', text) # fuera emojis
        text = text.strip(' ')

        return text



def load_model_and_tokenizer(option: int) -> tuple:
    """
    Load model and tokenizer based on the specified option.
    
    """
    if option not in [1, 2]:
        raise ValueError("Option must be either 1 or 2")
    
    # Define base directory based on option
    if option == 1:
        model_dir = os.path.abspath('Models/deberta_multi')
    else:  # option == 2
        model_dir = os.path.abspath('Models/deberta')
    
    # Verify directory exists
    if not os.path.exists(model_dir):
        raise ValueError(f"Directory does not exist: {model_dir}")
    
    # Load the model and tokenizer
    loaded_model = AutoModelForSequenceClassification.from_pretrained(
        model_dir,
        local_files_only=True
    )
    loaded_tokenizer = AutoTokenizer.from_pretrained(
        model_dir,
        local_files_only=True
    )
    
    return loaded_model, loaded_tokenizer



def write_df_to_excel(df, url, output_path):
    """
    Write DataFrame to Excel after properly handling timezone-aware datetime columns.
    
    """
    # Create a copy to avoid modifying the original DataFrame
    df_copy = df.copy()
    df_copy['url'] = url

    # Identify datetime columns
    datetime_columns = df_copy.select_dtypes(include=['datetime64[ns]', 'datetime64[ns, UTC]']).columns
    
    # Convert timezone-aware columns to timezone-naive
    for col in datetime_columns:
        if hasattr(df_copy[col].dtype, 'tz') and df_copy[col].dtype.tz is not None:
            # Convert to local time and remove timezone info
            df_copy[col] = df_copy[col].dt.tz_localize(None)
    
    try:
        # Write to Excel
        df_copy.to_excel(output_path, index=False)
        print(f"Successfully wrote data to {output_path}")
    except Exception as e:
        print(f"Error writing to Excel: {str(e)}")
        
        # Alternative: Save as CSV if Excel fails
        csv_path = output_path.rsplit('.', 1)[0] + '.csv'
        df_copy.to_csv(csv_path, index=False)
        print(f"Saved data as CSV instead: {csv_path}")


def generate_plots(report_type: str):
    try:
        # Create directory for plots if it doesn't exist
        plots_dir = "images"
        os.makedirs(plots_dir, exist_ok=True)
        
        
        
        # Generate different plots based on report type
        if report_type == "current":

            # Read data
            data = pd.read_excel('Data/current_video.xlsx')
            
            # Convert published_at to datetime
            data['published_at'] = pd.to_datetime(data['published_at'], format='%d/%m/%Y %H:%M:%S')
            
            # Create binary toxic indicator
            data['toxic_binary'] = data['is_toxic'].map({'Yes': 'Toxic', 'No': 'Neutral'})

            # Plot 1: Overall Toxic comments distribution
            plt.figure(figsize=(10, 6))
            toxic_counts = data['toxic_binary'].value_counts()
            sns.barplot(x=toxic_counts.index, y=toxic_counts.values)
            plt.title("Distribution of Toxic vs Neutral Comments")
            plt.ylabel("Number of Comments")
            plt.xlabel("Comment Type")
            
            # Add value labels on top of bars
            for i, v in enumerate(toxic_counts.values):
                plt.text(i, v, str(v), ha='center', va='bottom')
            
            plot1_path = os.path.join(plots_dir, 'toxic_distribution.png')
            plt.savefig(plot1_path, bbox_inches='tight', dpi=300)
            plt.close()
            
            # Plot 2: Toxic comments distribution over time
            plt.figure(figsize=(12, 6))
            
            # Group by date and toxic status
            data['date'] = data['published_at'].dt.date
            time_distribution = pd.crosstab(data['date'], data['toxic_binary'])
            
            # Create stacked bar plot
            time_distribution.plot(kind='bar', stacked=True)
            plt.title("Distribution of Comments Over Time")
            plt.xlabel("Date")
            plt.ylabel("Number of Comments")
            plt.legend(title="Comment Type")
            plt.xticks(rotation=45)
            
            # Format x-axis to show dates nicely
            plt.gca().xaxis.set_major_locator(plt.MaxNLocator(10))
            
            plot2_path = os.path.join(plots_dir, 'toxic_time_distribution.png')
            plt.savefig(plot2_path, bbox_inches='tight', dpi=300)
            plt.close()
            
            # Plot 3: Hourly distribution of toxic comments
            plt.figure(figsize=(12, 6))
            data['hour'] = data['published_at'].dt.hour
            hourly_distribution = pd.crosstab(data['hour'], data['toxic_binary'])
            
            hourly_distribution.plot(kind='bar', stacked=True)
            plt.title("Hourly Distribution of Comments")
            plt.xlabel("Hour of Day")
            plt.ylabel("Number of Comments")
            plt.legend(title="Comment Type")
            
            plot3_path = os.path.join(plots_dir, 'toxic_hourly_distribution.png')
            plt.savefig(plot3_path, bbox_inches='tight', dpi=300)
            plt.close()
            
        
        elif report_type == "historical":
            # Read data
            data = pd.read_excel('Data/historical_data.xlsx')
            
            # Convert published_at to datetime
            data['published_at'] = pd.to_datetime(data['published_at'], format='%d/%m/%Y %H:%M:%S')
            
            # Create binary toxic indicator
            data['toxic_binary'] = data['is_toxic'].map({'Yes': 'Toxic', 'No': 'Neutral'})

            # Plot 1: Overall Toxic comments distribution
            plt.figure(figsize=(10, 6))
            toxic_counts = data['toxic_binary'].value_counts()
            sns.barplot(x=toxic_counts.index, y=toxic_counts.values)
            plt.title("Historical Distribution of Toxic vs Neutral Comments")
            plt.ylabel("Number of Comments")
            plt.xlabel("Comment Type")
            
            # Add value labels on top of bars
            for i, v in enumerate(toxic_counts.values):
                plt.text(i, v, str(v), ha='center', va='bottom')
            
            plot1_path = os.path.join(plots_dir, 'toxic_distribution_h.png')
            plt.savefig(plot1_path, bbox_inches='tight', dpi=300)
            plt.close()
            
            # Plot 2: Toxic comments distribution over time
            plt.figure(figsize=(12, 6))
            
            # Group by date and toxic status
            data['date'] = data['published_at'].dt.date
            time_distribution = pd.crosstab(data['date'], data['toxic_binary'])
            
            # Create stacked bar plot
            time_distribution.plot(kind='bar', stacked=True)
            plt.title("Historical Distribution of Comments Over Time")
            plt.xlabel("Date")
            plt.ylabel("Number of Comments")
            plt.legend(title="Comment Type")
            plt.xticks(rotation=45)
            
            # Format x-axis to show dates nicely
            plt.gca().xaxis.set_major_locator(plt.MaxNLocator(10))
            
            plot2_path = os.path.join(plots_dir, 'toxic_time_distribution_h.png')
            plt.savefig(plot2_path, bbox_inches='tight', dpi=300)
            plt.close()
            
            # Plot 3: Hourly distribution of toxic comments
            plt.figure(figsize=(12, 6))
            data['hour'] = data['published_at'].dt.hour
            hourly_distribution = pd.crosstab(data['hour'], data['toxic_binary'])
            
            hourly_distribution.plot(kind='bar', stacked=True)
            plt.title("Historical Hourly Distribution of Comments")
            plt.xlabel("Hour of Day")
            plt.ylabel("Number of Comments")
            plt.legend(title="Comment Type")
            
            plot3_path = os.path.join(plots_dir, 'toxic_hourly_distribution_h.png')
            plt.savefig(plot3_path, bbox_inches='tight', dpi=300)
            plt.close()
        
        # Return paths of generated plots
        if report_type == 'current':
            return {
                "plot_paths": [
                    os.path.join(plots_dir, 'toxic_distribution.png'),
                    os.path.join(plots_dir, 'toxic_time_distribution.png'),
                    os.path.join(plots_dir, 'toxic_hourly_distribution.png'),
                ]
            }
        else: 
            return {
                "plot_paths": [
                    os.path.join(plots_dir, 'toxic_distribution_h.png'),
                    os.path.join(plots_dir, 'toxic_time_distribution_h.png'),
                    os.path.join(plots_dir, 'toxic_hourly_distribution_h.png'),
                ]
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating plots: {str(e)}")
