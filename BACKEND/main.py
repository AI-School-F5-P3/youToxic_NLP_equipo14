from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any, Optional
import json
from datetime import datetime
import os
import uuid
from fastapi.middleware.cors import CORSMiddleware
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import re
from pathlib import Path
import pandas as pd

from fastapi.staticfiles import StaticFiles
from aux import *
from aux_openai import *
from aux_db import *

app = FastAPI(title="Youtube Watchdog",
             description="A web application to monitor and analyze YouTube content for offensive language",
             version="1.0.0")


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScanVideoRequest(BaseModel):
    video_url: str

class ChatRequest(BaseModel):
    user_input: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    timestamp: str

class ScanVideoResponse(BaseModel):
    scan_result: List[Dict[str, Any]]

class ModRequest(BaseModel):
    model_name: str

class ModResponse(BaseModel):
    status: str
    message: str

class ReportRequest(BaseModel):
    report_type: str

class ReportResponse(BaseModel):
    status: str
    message: str




# Mount the images directory to make it accessible via HTTP
app.mount("/images", StaticFiles(directory="images"), name="images")

initialize_database()

#loaded_model, loaded_tokenizer = load_model_and_tokenizer(1)
global loaded_model, loaded_tokenizer

def classify_text(text):
    global loaded_model, loaded_tokenizer

    inputs = loaded_tokenizer(text, return_tensors="pt")
    outputs = loaded_model(**inputs)
    logits = outputs.logits
    predicted_class = int(logits.argmax(1))
    return predicted_class

def generate_response(user_input: str) -> str:
    try:
        prediction = classify_text(user_input)
        if prediction == 0:
            return 'The input is acceptable.'
        else:
            return 'The input contains offensive language.'
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        return f"I apologize, but I encountered an error: {str(e)}"



@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # Generate response without any conversation context
    bot_response = generate_response(request.user_input)
    
    # Create new conversation ID for each request
    conversation_id = str(uuid.uuid4())
    
    # Get current timestamp
    current_time = datetime.now().isoformat()
    
    return ChatResponse(
        response=bot_response,
        conversation_id=conversation_id,
        timestamp=current_time
    )


@app.post("/scan_video", response_model=ScanVideoResponse)
async def scan_video(request: ScanVideoRequest):
    try:
        
        cleaner = TextCleaner()
        # Get the video URL from the request
        video_url = request.video_url
        
        # Get comments using the video URL

        comments_df = get_video_comments(API_KEY, video_url)
        comments_df['comment'] = comments_df['comment'].apply(cleaner.clean_text)
        comments_df['is_toxic'] = comments_df['comment'].apply(classify_text)
        comments_df['is_toxic'] = comments_df['is_toxic'].apply(lambda x: "Yes" if x == 1 else "No")
        comments_df['published_at'] = pd.to_datetime(comments_df['published_at'], format='%d/%m/%Y %H:%M:%S')

        write_df_to_excel(comments_df, video_url, 'Data/current_video.xlsx') # Guarda el análisis en excel
        
        #Function to develop in aux_db
        store_db(video_url, comments_df)

        response_df = comments_df.copy()
        response_df = response_df[['author', 'comment','is_toxic']]
        
        # Convert DataFrame to list of dictionaries
        scan_result = response_df.to_dict('records')
        
        return ScanVideoResponse(scan_result=scan_result)
    
    except Exception as e:
        print(f"Error scanning video: {str(e)}")
        raise HTTPException(status_code=500, detail="Error scanning video")


@app.post("/scan_video_openai", response_model=ScanVideoResponse)
async def scan_video(request: ScanVideoRequest):
    print("Scanopenai request received")
    try:
        
        cleaner = TextCleaner()
        # Get the video URL from the request
        video_url = request.video_url
        
        # Get comments using the video URL

        comments_df = get_video_comments(API_KEY, video_url)
        
        comments_df['comment'] = comments_df['comment'].apply(cleaner.clean_text)

        # CALL OPENAI Classifier
        assistant_id = "asst_olrQEhkZlnX4sexNK53sKgJc"
        comments_df = classify_texts(comments_df, assistant_id)

        comments_df['is_toxic'] = comments_df['is_toxic'].apply(lambda x: "Yes" if x == "Toxic" else "No")

        write_df_to_excel(comments_df, video_url, 'Data/current_video.xlsx') # Guarda el análisis en excel
        #save in database, with tables url, comments
        store_db(video_url, comments_df)

        response_df = comments_df.copy()
        response_df = response_df[['author', 'comment','is_toxic']]
        
        # Convert DataFrame to list of dictionaries
        scan_result = response_df.to_dict('records')
        
        return ScanVideoResponse(scan_result=scan_result)
    
    except Exception as e:
        print(f"Error scanning video: {str(e)}")
        raise HTTPException(status_code=500, detail="Error scanning video")
    
    
@app.post("/model_def", response_model=ModResponse)
async def chat(request: ModRequest):

    global loaded_model, loaded_tokenizer
    try:
        # Determine which option to use based on model name
        if request.model_name == "just_en":
            option = 2
        elif request.model_name == "multi_lang":
            option = 1
        else:
            return ModResponse(
                status="error",
                message=f"Invalid model name: {request.model_name}. Must be 'just_en' or 'multi_lang'"
            )
        
        # Load model and tokenizer

        print(f'model change request received {request.model_name}')
        loaded_model, loaded_tokenizer = load_model_and_tokenizer(option)
        
        
        return ModResponse(
            status="success",
            message=f"Successfully loaded model: {request.model_name}"
        )
    
    except Exception as e:
        return ModResponse(
            status="error",
            message=f"Error loading model: {str(e)}"
        )
    

@app.post("/get_reports", response_model=ReportResponse)
async def get_reports(request: ReportRequest):
    try:
        if request.report_type not in ["current", "historical"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid report type: {request.report_type}. Must be 'current' or 'historical'"
            )
        
        # Generate plots
        print(f"Report requested: {request.report_type}")
        
        # Verify that the images directory exists
        images_dir = Path("images")
        if not images_dir.exists():
            images_dir.mkdir(parents=True)
            
        if request.report_type == "current":# Generate the plots
            generate_plots(request.report_type)
        else:
            export_comments_to_excel()
            generate_plots(request.report_type)
            

        
        # Verify that all required files exist
        required_files = [
            "toxic_distribution.png",
            "toxic_time_distribution.png",
            "toxic_hourly_distribution.png",
            "toxic_distribution_h.png",
            "toxic_time_distribution_h.png",
            "toxic_hourly_distribution_h.png"
        ]
        
        for file in required_files:
            if not (images_dir / file).exists():
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to generate required plot: {file}"
                )
        
        return ReportResponse(
            status="success",
            message=f"Successfully generated {request.report_type} reports"
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating reports: {str(e)}"
        )



@app.on_event("startup")
async def startup_event():
    global loaded_model, loaded_tokenizer
    try:
        # Default to option 1 (multi_lang) on startup
        loaded_model, loaded_tokenizer = load_model_and_tokenizer(1)
    except Exception as e:
        print(f"Error loading initial model: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException

# Initialize global variables
global loaded_model, loaded_tokenizer
loaded_model = None
loaded_tokenizer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load the model
    global loaded_model, loaded_tokenizer
    try:
        loaded_model, loaded_tokenizer = load_model_and_tokenizer(1)  # Default to option 1 (multi_lang)
        print("Model loaded successfully")
    except Exception as e:
        print(f"Error loading initial model: {str(e)}")
    
    yield  # This line separates startup from shutdown events
    
    # Cleanup (if needed) when the app shutdowns
    loaded_model = None
    loaded_tokenizer = None

# Create FastAPI app with lifespan
app = FastAPI(
    title="Youtube Watchdog",
    description="A web application to monitor and analyze YouTube content for offensive language",
    version="1.0.0",
    lifespan=lifespan
)


"""