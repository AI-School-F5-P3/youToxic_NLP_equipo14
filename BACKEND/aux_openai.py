import os
from openai import OpenAI                                                                                                                                                                                                        
from dotenv import load_dotenv
import pandas as pd
import time

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

## Set the API key and model name
client = OpenAI()

def classify_texts(df, assistant_id):
    classifications = []

    for text in df['comment']:
        # Create a new thread
        thread = client.beta.threads.create()

        # Add a message to the thread
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=text
        )

        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id
        )

        # Wait for the run to complete
        while run.status != "completed":
            time.sleep(1)  # Wait for 1 second before checking again
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        # Retrieve the assistant's message
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        assistant_message = messages.data[0].content[0].text.value

        classifications.append(assistant_message)

    # Add the classifications in the is_toxic column
    df['is_toxic'] = classifications

    return df


