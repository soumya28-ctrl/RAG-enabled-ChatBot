# RAG-enabled YouTube Chatbot

This project is an AI-powered **YouTube RAG Chatbot** that allows users to ask questions about any YouTube video and receive contextually relevant answers based on the video's transcript. The chatbot uses **OpenAI's GPT-3.5** to process the questions and generate human-like responses, while **FAISS** is used for efficient search and retrieval of video content.

The system retrieves video transcripts using the **YouTube Transcript API**, processes them into manageable chunks, and stores them in **FAISS** for fast retrieval. Once the transcript is processed, users can interact with the chatbot in any language to ask questions about the video content.

## Features

- **Multilingual Support**: Ask questions in any language, and the chatbot will respond accordingly.
- **Real-Time Interaction**: Provides answers in real-time using **OpenAI GPT-3.5** for context-aware responses.
- **Video Transcript Processing**: Extracts transcripts using the **YouTube Transcript API** and processes them into chunks.
- **Fast Search with FAISS**: Uses **FAISS** to retrieve relevant parts of the video transcript efficiently.
- **Simple Interface**: The user only needs to input a YouTube URL to get started.

## Technologies Used

- **Streamlit**: Frontend UI for user interaction.
- **OpenAI GPT-3.5**: For generating responses to user questions.
- **FAISS**: For fast, vector-based search of video content.
- **YouTube Transcript API**: To fetch video transcripts for processing.
- **LangChain**: For information retrieval and text splitting.

## How to Use

1. **Provide Your OpenAI API Key**:
   - The chatbot requires an OpenAI API key for generating responses.
   - In the `app.py` file, hardcode your API key in the `API_KEY` variable:
     ```python
     API_KEY = "sk-your-openai-api-key-here"
     ```
   - Alternatively, you can set the OpenAI API key as an environment variable:
     ```bash
     export OPENAI_API_KEY="sk-your-openai-api-key-here"
     ```

2. **Input YouTube URL**:
   - Paste any YouTube video URL that you would like to process. The system will extract the transcript for you.

3. **Ask Questions**:
   - After the transcript is processed, you can start asking any question related to the video. The system will generate answers based on the transcript content.



Would you like further adjustments or additions to this README file?
