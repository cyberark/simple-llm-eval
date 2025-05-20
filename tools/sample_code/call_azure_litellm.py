import os

from dotenv import load_dotenv

load_dotenv()

from litellm import completion

assert 'AZURE_OPENAI_API_KEY' in os.environ, 'Please set the AZURE_OPENAI_API_KEY environment variable.'
assert 'AZURE_API_VERSION' in os.environ, 'Please set the AZURE_API_VERSION environment variable.'
assert 'AZURE_API_BASE' in os.environ, 'Please set the AZURE_API_BASE environment variable.'

print(f'{os.environ["AZURE_API_BASE"]=}')
print(f'{os.environ["AZURE_API_VERSION"]=}')
print(f'os.environ["AZURE_OPENAI_API_KEY"]={os.environ["AZURE_OPENAI_API_KEY"][:2]}..{os.environ["AZURE_OPENAI_API_KEY"][-2:]}')

# litellm._turn_on_debug()
response = completion(model='azure/gpt-4.1-mini', messages=[{'content': 'Hello, how are you?', 'role': 'user'}])

print(response.choices[0].message.content)
