# Gradio Chatbot with LM Studio

This repository contains a Gradio chatbot that uses LM Studio as an OpenAI API replacement.

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- LM Studio running on localhost:1234 (follow setup instructions at https://lmstudio.ai/docs/local-server)

## Setup and Running the App

### On Unix-like systems (Linux, macOS)

1. Clone this repository:
   ```
   git clone https://github.com/aiforhumans/gradio-chatbot.git
   cd gradio-chatbot
   ```

2. Run the setup and start script:
   ```
   ./run.sh
   ```

### On Windows

1. Clone this repository:
   ```
   git clone https://github.com/aiforhumans/gradio-chatbot.git
   cd gradio-chatbot
   ```

2. Run the setup and start script:
   ```
   run.bat
   ```

3. Open your web browser and go to `http://localhost:7860` to interact with the chatbot.

## Manual Setup

If you prefer to set up the environment manually:

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - On Unix-like systems:
     ```
     source venv/bin/activate
     ```
   - On Windows:
     ```
     venv\Scripts\activate
     ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Run the app:
   ```
   python app.py
   ```

5. Open your web browser and go to `http://localhost:7860` to interact with the chatbot.

## Deactivating the Virtual Environment

When you're done using the app, you can deactivate the virtual environment:

```
deactivate
```

This will return you to your global Python environment.

## Note

Ensure that LM Studio is running and serving the API on localhost:1234 before starting the Gradio app.