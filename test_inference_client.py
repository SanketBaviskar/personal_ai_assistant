import os
import sys
# Add parent directory to path to import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from huggingface_hub import InferenceClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

client = InferenceClient(token=os.environ.get("HUGGINGFACE_API_KEY"))

completion = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {
            "role": "user",
            "content": "How many 'G's in 'huggingface'?"
        }
    ],
)

print(completion.choices[0].message)
