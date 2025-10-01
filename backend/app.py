from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Sample data
groups = [
]

# Join requests data
join_requests = [
    {"id": 1, "user": "alex", "group_id": 3, "status": "pending", "requested_at": "2025-09-30T10:00:00Z"},
    {"id": 2, "user": "cory", "group_id": 1, "status": "pending", "requested_at": "2025-09-30T11:00:00Z"},
    {"id": 3, "user": "alex", "group_id": 4, "status": "pending", "requested_at": "2025-09-30T12:00:00Z"}
]

trades = [
    {
        "id": 1,
        "symbol": "AAPL",
        "quantity": 100,
        "price": 150.50,
        "type": "buy",
        "timestamp": "2025-09-29T10:00:00Z",
        "user": "alex",
        "group_id": 1
    },
    {
        "id": 2,
        "symbol": "GOOGL",
        "quantity": 50,
        "price": 2750.25,
        "type": "sell",
        "timestamp": "2025-09-29T11:30:00Z",
        "user": "alex",
        "group_id": 1
    },
    {
        "id": 3,
        "symbol": "BTC",
        "quantity": 2,
        "price": 43000.00,
        "type": "buy",
        "timestamp": "2025-09-29T12:00:00Z",
        "user": "alex",
        "group_id": 2
    }
]

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
    
    new_trade = {
        "id": len(trades) + 1,
        "symbol": data['symbol'].upper(),
        "quantity": int(data['quantity']),
        "price": float(data['price']),
        "type": data['type'].lower(),
        "timestamp": data.get('timestamp', "2025-09-29T12:00:00Z"),
        "user": data.get('user', 'alex'),
        "group_id": int(data['group_id'])
    }
    
    trades.append(new_trade)
    return jsonify({"trade": new_trade}), 201

@app.route('/api/trades/<int:trade_id>', methods=['DELETE'])
def delete_trade(trade_id):
    global trades
    trades = [trade for trade in trades if trade['id'] != trade_id]
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
    
    return jsonify({"message": "Join request rejected"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
