import os

from dotenv import load_dotenv

load_dotenv()

from litellm import completion

assert 'VERTEXAI_PROJECT' in os.environ, 'Please set the VERTEXAI_PROJECT environment variable.'
assert 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ, 'Please set the GOOGLE_APPLICATION_CREDENTIALS environment variable.'
assert 'VERTEXAI_LOCATION' in os.environ, 'Please set the VERTEXAI_LOCATION environment variable.'

response = completion(model='vertex_ai/gemini-2.0-flash', messages=[{'content': 'Hello, how are you?', 'role': 'user'}])

print(response.choices[0].message.content)
