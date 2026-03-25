from flask import Flask, request, jsonify
from flask_cors import CORS
from threading import Thread
from dotenv import load_dotenv
import os
import requests

load_dotenv()
token = os.getenv('TOKEN')

#define flask app
app = Flask('')
CORS(app)

@app.route('/send_score', methods=['POST'])
async def send_score():
    data = request.json
    score = data.get('score')
    user_id = data.get('user_id')
    chat_id = data.get('chat_id')
    message_id = data.get('message_id')
    
    if user_id is None or score is None or chat_id is None or message_id is None:
        return jsonify({'error': 'Invalid data'}), 400

    try:
        set_game_score(token, user_id, score, chat_id, message_id)
        return jsonify({'status': 'Score updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def set_game_score(token, user_id, score, chat_id, message_id, force=False, disable_edit_message=False):
    url = f"https://api.telegram.org/bot{token}/setGameScore"
    
    payload = {
        'user_id': user_id,
        'score': score,
        'chat_id': chat_id,
        'message_id': message_id,
        'force': force,
        'disable_edit_message': disable_edit_message
    }

    response = requests.post(url, data=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")

#create route for home page
@app.route('/')
def main():
    return "server online!"

#Run our flask app in a thread so that the bot and website can run simultaneously.
def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    server = Thread(target=run)
    server.start()
