from flask import Flask, request, jsonify, abort, redirect, url_for, session
from redis import Redis
from pymongo import MongoClient
from datetime import datetime
from functools import wraps

app = Flask(__name__)


# Configure Redis
redis_client = Redis(host='172.17.0.3', port=6379, decode_responses=True)

# Configure MongoDB
mongo_client = MongoClient('mongodb://172.17.0.2:27017/')
db = mongo_client['chatbot_db']
users_collection = db['users']
conversations_collection = db['conversations']

# Predefined responses
faq_responses = {
    "hello": "Hello! How can I assist you today?",
    "services": "Dell offers a wide range of products including laptops, desktops, and servers.",
    "contact": "You can contact Dell support at 1-800-123-DELL.",
    "warranty": "Dell provides various warranty options. For details on your warranty, please visit Dell's official warranty support page.",
    "support": "Dell offers technical support through our website, phone support, and live chat. Visit Dell's support page for more information.",
    "drivers": "You can download drivers for your Dell products from the Dell Support website. Just enter your product's service tag or model number.",
    "returns": "Dell has a return policy for most products. Please check the Dell Returns & Exchanges page for more details.",
    "buying": "To purchase Dell products, visit our official website or contact a Dell sales representative for personalized assistance.",
    "troubleshooting": "For troubleshooting Dell products, visit our Support page for guides and diagnostics tools.",
    "updates": "Dell regularly updates its products with the latest features and fixes. Check the Dell Support page for product updates and patches.",
    "repair": "If you need repairs for your Dell product, you can schedule a repair service through Dell's Support page or contact our repair center."
    # Add more predefined responses here
}

def authenticate(username, password):
    """Authenticate user using basic authentication."""
    if not username or not password:
        return False
    user = users_collection.find_one({'username': username})
    return user and user['password'] == password

@app.route('/register/<username>/<password>', methods=['POST'])
def register(username, password):
    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    # Check if the user already exists
    if users_collection.find_one({'username': username}):
        return jsonify({'error': 'User already exists'}), 400

    # Create a new user
    users_collection.insert_one({'username': username, 'password': password})
    return jsonify({'status': 'User registered successfully'}), 201

def get_bot_response(message):
    return faq_responses.get(message.lower(), "I'm not sure how to help with that.")

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    
    if not authenticate(username, password):
        return jsonify({'error': 'Unauthorized'}), 401
    
    session['username'] = username
    session['chat_id'] = datetime.utcnow().strftime('%Y%m%d%H%M%S')  # Unique chat ID based on timestamp

    return jsonify({'status': 'Logged in successfully'}), 200

@app.route('/chat', methods=['POST'])
def chat():
    if 'username' not in session:
        return jsonify({"error": "Please log in first."}), 401

    username = session['username']
    chat_id = session['chat_id']

    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    user_query = request.json.get('message').lower()

    # Handle logout command
    if user_query == "logout":
        return redirect(url_for('logout'))

    # Store chat in Redis
    chat_key = f"chat:{username}:{chat_id}"
    redis_client.rpush(chat_key, user_query)

    # Handle other queries
    response = get_bot_response(user_query)

    # Store bot response in Redis
    redis_client.rpush(chat_key, response)

    return jsonify({"response": response}), 200

@app.route('/logout', methods=['POST'])
def logout():
    if 'username' not in session:
        return jsonify({"error": "No active session."}), 401

    username = session['username']
    chat_id = session['chat_id']

    # Get the conversation from Redis
    chat_key = f"chat:{username}:{chat_id}"
    conversation = redis_client.lrange(chat_key, 0, -1)
    
    if conversation:
        # Store the conversation in MongoDB
        conversations_collection.insert_one({
            'user_id': username,
            'messages': conversation,  # List of messages
            'timestamp': datetime.utcnow()
        })

        # Clean up Redis
        redis_client.delete(chat_key)

    # Clear the session
    session.pop('username', None)
    session.pop('chat_id', None)

    return jsonify({'status': 'Logged out and conversation saved.'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
