import os
import openai

openai.api_key = os.environ.get('OPENAI_API_KEY')


def get_chatcompletion(frame: str, prompt: str):
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {'role': 'system', 'content': frame},
            {'role': 'user', 'content': prompt},
        ],
    )
    response_content = response.choices[0].message.content
    return response_content


def get_conversation_chatcompletion(messages):
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=list(messages),
    )
    response_content = response.choices[0].message.content
    return response_content
