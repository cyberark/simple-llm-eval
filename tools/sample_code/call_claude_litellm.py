import os

from dotenv import load_dotenv

load_dotenv()

from litellm import completion

assert 'ANTHROPIC_API_KEY' in os.environ, 'Please set the ANTHROPIC_API_KEY environment variable.'

response = completion(model='claude-3-5-haiku-latest', messages=[{'content': 'Hello, how are you?', 'role': 'user'}])

print(response.choices[0].message.content)
