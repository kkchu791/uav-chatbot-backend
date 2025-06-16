# Description
A UAV Chabot that analyzes flight logs that uses Open AI Assistant API.
This is built in FastAPI.

# Fill in .env file with your open API Key and Open AI Assistant ID
OPENAI_API_KEY=YOUR_OPENAI_API_KEY

OPENAI_ASSISTANT_ID=YOUR_OPENAI_ASSISTANT_ID

# Directions on running frontend here

https://github.com/kkchu791/uAVLogViewer/

# Command to run:
1. Create virtual environment
python3 -m venv venv

2. Activate it
source venv/bin/activate

3. Install dependencies
pip install -r requirements.txt

4. Fill in .env with your OpenAI keys

5. Run the server
uvicorn main:app --reload
