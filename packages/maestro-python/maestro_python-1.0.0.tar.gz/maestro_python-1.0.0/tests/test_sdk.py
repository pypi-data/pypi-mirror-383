#!/usr/bin/env python3
"""
Test script to verify the drop-in replacement SDK works.
Run this after starting the Docker services.
"""

# Instead of: from openai import OpenAI
from maestro.openai import OpenAI

def test_drop_in_replacement_chat():
    # Same exact usage as real OpenAI SDK - uses OPENAI_API_KEY env var
    client = OpenAI()
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello! How are you?"}
            ],
            temperature=0.7,
            max_tokens=50
        )
        
        print("✅ SDK replacement works!")
        print(f"Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌Chat Completions SDK test failed: {e}")
        return False

def test_drop_in_replacement_responses():
    client = OpenAI()

    try:
        response = client.responses.create(
                model="gpt-4o-mini",
                input="How are you?"
                )
        print("✅ SDK replacement works!")
        print(f"Response: {response}")
        return True 
    except Exception as e:
        print(f"NOPE. {e}")
        return False 


if __name__ == "__main__":
    print("Testing Langswift SDK drop-in replacement...")
    test_drop_in_replacement_chat()
    print("Testing v1/responses")
    test_drop_in_replacement_responses()
