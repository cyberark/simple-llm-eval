import os

from dotenv import load_dotenv

load_dotenv()

from litellm import completion

assert 'OPENAI_API_KEY' in os.environ, 'Please set the OPENAI_API_KEY environment variable.'

response = completion(model='gpt-4o', messages=[{'content': 'Hello, how are you?', 'role': 'user'}])

print(response.choices[0].message.content)
