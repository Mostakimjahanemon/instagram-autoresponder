import os
import json
import requests
from flask import Flask, request

app = Flask(__name__)

# Get credentials from environment variables
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN', 'mytoken123')

# Auto reply rules
REPLIES = {
    'hi': 'Hi there! How are you doing? 😊',
    'hello': 'Hello! Nice to meet you! 😊',
    'hey': 'Hey! What can I do for you? 😊',
    'how are you': "I'm doing great, thanks for asking! 😊",
    'help': 'I can help you! Just send me a message 😊',
}

DEFAULT_REPLY = "Thanks for your message! I'll get back to you soon 😊"

def send_message(recipient_id, message_text):
    url = f'https://graph.instagram.com/v18.0/me/messages'
    headers = {'Content-Type': 'application/json'}
    data = {
        'recipient': {'id': recipient_id},
        'message': {'text': message_text},
        'access_token': ACCESS_TOKEN
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def get_reply(message_text):
    message_lower = message_text.lower().strip()
    for keyword, reply in REPLIES.items():
        if keyword in message_lower:
            return reply
    return DEFAULT_REPLY

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if mode == 'subscribe' and token == VERIFY_TOKEN:
        return challenge, 200
    return 'Forbidden', 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if data.get('object') == 'instagram':
        for entry in data.get('entry', []):
            for messaging in entry.get('messaging', []):
                sender_id = messaging['sender']['id']
                if 'message' in messaging:
                    message_text = messaging['message'].get('text', '')
                    if message_text:
                        reply = get_reply(message_text)
                        send_message(sender_id, reply)
    return 'OK', 200

@app.route('/')
def home():
    return 'Instagram Bot is Running! 🤖'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)