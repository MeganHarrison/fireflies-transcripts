"""
Test the OpenAI API key
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
print(f"API Key loaded: {api_key[:20]}...{api_key[-20:]}")

try:
    client = OpenAI(api_key=api_key)
    
    # Test with a simple embedding
    print("\nTesting embedding generation...")
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input="This is a test"
    )
    
    print(f"✅ Success! Embedding dimension: {len(response.data[0].embedding)}")
    print(f"Model used: {response.model}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    
    # Try different models
    print("\nTrying alternative models...")
    models = ["text-embedding-3-small", "text-embedding-3-large"]
    
    for model in models:
        try:
            response = client.embeddings.create(
                model=model,
                input="This is a test"
            )
            print(f"✅ {model} works! Dimension: {len(response.data[0].embedding)}")
        except Exception as e:
            print(f"❌ {model} failed: {str(e)[:100]}")