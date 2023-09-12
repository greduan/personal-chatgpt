from dotenv import load_dotenv
from flask import Flask, render_template, request

from db import create_tables, add_conversation, fetch_conversation, get_db_conn, \
    add_message, fetch_all_conversations, fetch_conversation_next_id
from openai_helper import get_chatcompletion, get_conversation_chatcompletion

load_dotenv()
create_tables()

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/conversation/<int:conversation_id>')
def index_conversation(conversation_id: int):
    return render_template('index_conversation.html', conversation_id=str(conversation_id))


@app.route('/conversations.turbo')
def conversation_list_turbo():
    conversations = fetch_all_conversations()
    conversation_id = request.args.get('conversation_id')
    return render_template(
        'conversation_list.html',
        conversations=conversations,
        conversation_id=int(conversation_id),
    )


@app.route('/conversation/new.turbo')
def new_conversation_turbo():
    conversation = {
        'messages': [],
    }
    return render_template('conversation.html', conversation=conversation)


@app.route('/conversation/<int:conversation_id>.turbo')
def one_conversation_turbo(conversation_id: int):
    conversation = fetch_conversation(conversation_id)
    return render_template('conversation.html', conversation=conversation)


@app.route('/chat', methods=['POST'])
def chat():
    conversation_id = request.form['conversation_id'] or None
    conversation = fetch_conversation(conversation_id=conversation_id)
    new_conversation = None

    if conversation is None:
        conversation_id = fetch_conversation_next_id()
        messages = [
            {'role': 'system', 'content': 'Pretend you are an expert.'},
            {'role': 'user', 'content': request.form['content']},
        ]
        completion_message = {
            'role': 'assistant',
            'content': get_conversation_chatcompletion(messages),
        }
        messages += [completion_message]
        conversation = {
            'summary': get_chatcompletion('Summarize the following prompt into no more than 10 words.', request.form['content']),
            'messages': messages,
        }
        new_conversation = add_conversation(c, summary=conversation['summary'])
        new_messages = conversation['messages']
    else:
        messages = conversation['messages']
        new_messages = [
            {'role': 'user', 'content': request.form['content']},
        ]
        completion_message = {
            'role': 'assistant',
            'content': get_conversation_chatcompletion(messages + new_messages),
        }
        new_messages += [completion_message]

    conn = get_db_conn()
    c = conn.cursor()

    if new_conversation is not None:
        add_conversation(c, summary=conversation['summary'])

    for message in new_messages:
        add_message(
            c,
            conversation_id=conversation_id,
            role=message['role'],
            content=message['content'],
        )

    conn.commit()
    conn.close()

    updated_conversation = fetch_conversation(conversation_id)

    return render_template('conversation.html', conversation=updated_conversation)


if __name__ == '__main__':
    app.run(port=8080, debug=True)
