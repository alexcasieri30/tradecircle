from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
import json
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tradecircle_secret_key_2025'
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Helper functions for quantity ranges
def parse_quantity_range(quantity_str):
    """Parse quantity range string and return min, max values"""
    if '-' in quantity_str:
        min_qty, max_qty = quantity_str.split('-')
        return int(min_qty), int(max_qty)
    else:
        # Fallback for single numbers
        qty = int(quantity_str)
        return qty, qty

def calculate_total_range(quantity_str, price):
    """Calculate total value range for a quantity range and price"""
    min_qty, max_qty = parse_quantity_range(quantity_str)
    min_total = min_qty * price
    max_total = max_qty * price
    return min_total, max_total

# Data persistence functions
DATA_DIR = '/app/data'
GROUPS_FILE = os.path.join(DATA_DIR, 'groups.json')
TRADES_FILE = os.path.join(DATA_DIR, 'trades.json')
JOIN_REQUESTS_FILE = os.path.join(DATA_DIR, 'join_requests.json')
CHAT_MESSAGES_FILE = os.path.join(DATA_DIR, 'chat_messages.json')

def ensure_data_dir():
    """Ensure data directory exists"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def load_data():
    """Load all data from JSON files"""
    ensure_data_dir()
    
    # Load groups
    try:
        with open(GROUPS_FILE, 'r') as f:
            groups = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        groups = [
        ]
        save_groups(groups)
    
    # Load trades
    try:
        with open(TRADES_FILE, 'r') as f:
            trades = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        trades = [
        ]
        save_trades(trades)
    
    # Load join requests
    try:
        with open(JOIN_REQUESTS_FILE, 'r') as f:
            join_requests = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        join_requests = [
        ]
        save_join_requests(join_requests)
    
    # Load chat messages
    try:
        with open(CHAT_MESSAGES_FILE, 'r') as f:
            chat_messages = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        chat_messages = {}
        save_chat_messages(chat_messages)
    
    return groups, trades, join_requests, chat_messages

def save_groups(groups_data):
    """Save groups data to JSON file"""
    ensure_data_dir()
    with open(GROUPS_FILE, 'w') as f:
        json.dump(groups_data, f, indent=2)

def save_trades(trades_data):
    """Save trades data to JSON file"""
    ensure_data_dir()
    with open(TRADES_FILE, 'w') as f:
        json.dump(trades_data, f, indent=2)

def save_join_requests(join_requests_data):
    """Save join requests data to JSON file"""
    ensure_data_dir()
    with open(JOIN_REQUESTS_FILE, 'w') as f:
        json.dump(join_requests_data, f, indent=2)

def save_chat_messages(chat_messages_data):
    """Save chat messages data to JSON file"""
    ensure_data_dir()
    with open(CHAT_MESSAGES_FILE, 'w') as f:
        json.dump(chat_messages_data, f, indent=2)

# Load initial data
groups, trades, join_requests, chat_messages = load_data()

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "TradeCircle API is running"})

@app.route('/api/trades', methods=['GET'])
def get_trades():
    group_id = request.args.get('group_id', type=int)
    if group_id:
        filtered_trades = [trade for trade in trades if trade.get('group_id') == group_id]
        return jsonify({"trades": filtered_trades})
    return jsonify({"trades": trades})

@app.route('/api/trades', methods=['POST'])
def create_trade():
    data = request.get_json()
    
    if not data or not all(key in data for key in ['symbol', 'quantity', 'price', 'type', 'group_id']):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Validate quantity range
    valid_ranges = ['1-10', '10-100', '100-1000']
    if data['quantity'] not in valid_ranges:
        return jsonify({"error": "Invalid quantity range. Must be one of: " + ", ".join(valid_ranges)}), 400
    
    new_trade = {
        "id": len(trades) + 1,
        "symbol": data['symbol'].upper(),
        "quantity": data['quantity'],  # Keep as range string
        "price": float(data['price']),
        "type": data['type'].lower(),
        "timestamp": data.get('timestamp', "2025-09-29T12:00:00Z"),
        "user": data.get('user', 'alex'),
        "group_id": int(data['group_id'])
    }
    
    trades.append(new_trade)
    save_trades(trades)  # Save to file
    return jsonify({"trade": new_trade}), 201

@app.route('/api/trades/<int:trade_id>', methods=['DELETE'])
def delete_trade(trade_id):
    global trades
    trades = [trade for trade in trades if trade['id'] != trade_id]
    save_trades(trades)  # Save to file
    return jsonify({"message": f"Trade {trade_id} deleted"}), 200

# Groups endpoints
@app.route('/api/groups', methods=['GET'])
def get_groups():
    user = request.args.get('user', 'alex')
    user_groups = [group for group in groups if user in group['members']]
    return jsonify({"groups": user_groups})

@app.route('/api/groups', methods=['POST'])
def create_group():
    data = request.get_json()
    
    if not data or not all(key in data for key in ['name', 'description']):
        return jsonify({"error": "Missing required fields"}), 400
    
    created_by = data.get('created_by', 'alex')
    new_group = {
        "id": len(groups) + 1,
        "name": data['name'],
        "description": data['description'],
        "members": [created_by],
        "admin": created_by,  # Creator becomes admin
        "created_by": created_by,
        "created_at": data.get('created_at', "2025-09-30T12:00:00Z")
    }
    
    groups.append(new_group)
    save_groups(groups)  # Save to file
    return jsonify({"group": new_group}), 201

@app.route('/api/groups/<int:group_id>', methods=['GET'])
def get_group_details(group_id):
    user = request.args.get('user', 'alex')
    group = next((g for g in groups if g['id'] == group_id), None)
    if not group:
        return jsonify({"error": "Group not found"}), 404
    
    # Get trades for this group
    group_trades = [trade for trade in trades if trade.get('group_id') == group_id]
    
    # Get pending join requests if user is admin
    pending_requests = []
    if user == group.get('admin'):
        pending_requests = [req for req in join_requests 
                          if req['group_id'] == group_id and req['status'] == 'pending']
    
    return jsonify({
        "group": group,
        "trades": group_trades,
        "trade_count": len(group_trades),
        "pending_requests": pending_requests,
        "is_admin": user == group.get('admin')
    })

# Search groups endpoint - returns all groups
@app.route('/api/groups/search', methods=['GET'])
def search_groups():
    user = request.args.get('user', 'alex')
    
    # Return all groups with additional info about user's membership status
    groups_with_status = []
    for group in groups:
        group_info = group.copy()
        group_info['is_member'] = user in group['members']
        group_info['has_pending_request'] = any(
            req['user'] == user and req['group_id'] == group['id'] and req['status'] == 'pending'
            for req in join_requests
        )
        groups_with_status.append(group_info)
    
    return jsonify({"groups": groups_with_status})

# Join request endpoints
@app.route('/api/groups/<int:group_id>/join', methods=['POST'])
def request_to_join_group(group_id):
    data = request.get_json()
    user = data.get('user', 'alex')
    
    # Check if group exists
    group = next((g for g in groups if g['id'] == group_id), None)
    if not group:
        return jsonify({"error": "Group not found"}), 404
    
    # Check if user is already a member
    if user in group['members']:
        return jsonify({"error": "User is already a member of this group"}), 400
    
    # Check if there's already a pending request
    existing_request = next(
        (req for req in join_requests 
         if req['user'] == user and req['group_id'] == group_id and req['status'] == 'pending'),
        None
    )
    if existing_request:
        return jsonify({"error": "Join request already pending"}), 400
    
    # Create new join request
    new_request = {
        "id": len(join_requests) + 1,
        "user": user,
        "group_id": group_id,
        "status": "pending",
        "requested_at": data.get('requested_at', "2025-09-30T12:00:00Z")
    }
    
    join_requests.append(new_request)
    save_join_requests(join_requests)  # Save to file
    return jsonify({"message": "Join request sent successfully", "request": new_request}), 201

@app.route('/api/groups/<int:group_id>/join/<int:request_id>/approve', methods=['POST'])
def approve_join_request(group_id, request_id):
    data = request.get_json()
    admin_user = data.get('admin_user')
    
    # Find the join request
    request_obj = next((req for req in join_requests if req['id'] == request_id), None)
    if not request_obj:
        return jsonify({"error": "Join request not found"}), 404
    
    # Find the group
    group = next((g for g in groups if g['id'] == group_id), None)
    if not group:
        return jsonify({"error": "Group not found"}), 404
    
    # Check if user is admin
    if admin_user != group.get('admin'):
        return jsonify({"error": "Only group admin can approve join requests"}), 403
    
    # Add user to group members
    if request_obj['user'] not in group['members']:
        group['members'].append(request_obj['user'])
    
    # Update request status
    request_obj['status'] = 'approved'
    
    # Save both groups and join_requests
    save_groups(groups)
    save_join_requests(join_requests)
    
    return jsonify({"message": "Join request approved", "group": group}), 200

@app.route('/api/groups/<int:group_id>/join/<int:request_id>/reject', methods=['POST'])
def reject_join_request(group_id, request_id):
    data = request.get_json()
    admin_user = data.get('admin_user')
    
    # Find the join request
    request_obj = next((req for req in join_requests if req['id'] == request_id), None)
    if not request_obj:
        return jsonify({"error": "Join request not found"}), 404
    
    # Find the group
    group = next((g for g in groups if g['id'] == group_id), None)
    if not group:
        return jsonify({"error": "Group not found"}), 404
    
    # Check if user is admin
    if admin_user != group.get('admin'):
        return jsonify({"error": "Only group admin can reject join requests"}), 403
    
    # Update request status
    request_obj['status'] = 'rejected'
    
    # Save join_requests
    save_join_requests(join_requests)
    
    return jsonify({"message": "Join request rejected"}), 200

# Chat endpoints
@app.route('/api/groups/<int:group_id>/chat', methods=['GET'])
def get_chat_messages(group_id):
    user = request.args.get('user')
    
    # Find the group
    group = next((g for g in groups if g['id'] == group_id), None)
    if not group:
        return jsonify({"error": "Group not found"}), 404
    
    # Check if user is a member
    if user not in group['members']:
        return jsonify({"error": "Only group members can access chat"}), 403
    
    # Get messages for this group
    group_messages = chat_messages.get(str(group_id), [])
    
    return jsonify({"messages": group_messages}), 200

@app.route('/api/groups/<int:group_id>/chat', methods=['POST'])
def send_chat_message(group_id):
    data = request.get_json()
    user = data.get('user')
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({"error": "Message cannot be empty"}), 400
    
    # Find the group
    group = next((g for g in groups if g['id'] == group_id), None)
    if not group:
        return jsonify({"error": "Group not found"}), 404
    
    # Check if user is a member
    if user not in group['members']:
        return jsonify({"error": "Only group members can send messages"}), 403
    
    # Create new message
    new_message = {
        "id": len(chat_messages.get(str(group_id), [])) + 1,
        "user": user,
        "message": message,
        "timestamp": data.get('timestamp', datetime.now().isoformat())
    }
    
    # Add message to group chat
    if str(group_id) not in chat_messages:
        chat_messages[str(group_id)] = []
    
    chat_messages[str(group_id)].append(new_message)
    
    # Save to file
    save_chat_messages(chat_messages)
    
    return jsonify({"message": new_message}), 201

# WebSocket Events for Real-time Chat
@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')
    emit('connected', {'data': 'Connected to TradeCircle chat server'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')

@socketio.on('join_group_chat')
def handle_join_group_chat(data):
    user = data.get('user')
    group_id = data.get('group_id')
    
    # Verify user is member of the group
    group = next((g for g in groups if g['id'] == group_id), None)
    if not group or user not in group['members']:
        emit('error', {'message': 'Not authorized to join this group chat'})
        return
    
    # Join the room for this group
    room_name = f'group_{group_id}'
    join_room(room_name)
    
    print(f'User {user} joined group {group_id} chat room')
    emit('joined_group_chat', {'group_id': group_id, 'group_name': group['name']})

@socketio.on('leave_group_chat')
def handle_leave_group_chat(data):
    group_id = data.get('group_id')
    user = data.get('user')
    
    room_name = f'group_{group_id}'
    leave_room(room_name)
    
    print(f'User {user} left group {group_id} chat room')

@socketio.on('send_message')
def handle_send_message(data):
    user = data.get('user')
    group_id = data.get('group_id')
    message = data.get('message', '').strip()
    
    if not message:
        emit('error', {'message': 'Message cannot be empty'})
        return
    
    # Verify user is member of the group
    group = next((g for g in groups if g['id'] == group_id), None)
    if not group or user not in group['members']:
        emit('error', {'message': 'Not authorized to send messages to this group'})
        return
    
    # Create new message
    new_message = {
        "id": len(chat_messages.get(str(group_id), [])) + 1,
        "user": user,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    
    # Save message to persistent storage
    if str(group_id) not in chat_messages:
        chat_messages[str(group_id)] = []
    
    chat_messages[str(group_id)].append(new_message)
    save_chat_messages(chat_messages)
    
    # Broadcast message to all users in the group room
    room_name = f'group_{group_id}'
    socketio.emit('new_message', {
        'group_id': group_id,
        'message': new_message
    }, room=room_name)
    
    print(f'Message sent by {user} to group {group_id}: {message}')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    dev = os.getenv("FLASK_ENV")
    socketio.run(app, host='0.0.0.0', port=port, debug=(dev == "development"))
