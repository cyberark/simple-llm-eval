import os

from dotenv import load_dotenv

load_dotenv()

from openai import OpenAI

assert 'OPENAI_API_KEY' in os.environ, 'Please set the OPENAI_API_KEY environment variable.'

client = OpenAI()

completion = client.chat.completions.create(model='gpt-4.1-mini', messages=[{
    'role': 'user',
    'content': 'Write a one-sentence bedtime story about a unicorn.'
}])

print(completion.choices[0].message.content)
