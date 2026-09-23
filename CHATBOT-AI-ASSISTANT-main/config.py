import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get OpenAI API key from environment variable
apikey = os.getenv('OPENAI_API_KEY') 