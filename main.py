from dotenv import load_dotenv
from flask import Flask, render_template, request
import openai
import os

load_dotenv()

app = Flask(__name__)

openai.api_key = os.environ.get('OPENAI_API_KEY')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/conversations')
def conversation_list():
    # TODO: Fetch conversations and render them
    conversations = []
    return render_template('conversation_list.html', conversations=conversations)


@app.route('/conversation/new')
def new_conversation():
    conversation = {
        'messages': [],
    }
    return render_template('conversation.html', conversation=conversation)


@app.route('/conversation/<int:conversation_id>')
def conversation(conversation_id: str):
    conversation = {
        'messages': [],
    }
    return render_template('conversation.html', conversation=conversation)


@app.route('/chat', methods=['POST'])
def chat():
    prompt = request.form['content']
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {'role': 'system', 'content': 'Pretend you are an expert.'},
            {'role': 'user', 'content': prompt},
        ],
    )
    response_content = response.choices[0].message.content

    # TODO: Save to DB using request.form['id']

    conversation = {
        'messages': [
            {'role': 'user', 'content': request.form['content']},
            {'role': 'assistant', 'content': response_content},
        ]
    }

    return render_template('conversation.html', conversation=conversation)


if __name__ == '__main__':
    app.run(port=8080, debug=True)
