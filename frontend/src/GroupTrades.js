import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './GroupTrades.css';

const GroupTrades = ({ group, onBack, currentUser }) => {
  const [trades, setTrades] = useState([]);
  const [pendingRequests, setPendingRequests] = useState([]);
  const [isAdmin, setIsAdmin] = useState(false);
  const [activeTab, setActiveTab] = useState('trades');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [newTrade, setNewTrade] = useState({
    symbol: '',
    quantity: '',
    price: '',
    type: 'buy'
  });

  useEffect(() => {
    fetchGroupTrades();
  }, [group.id]);

  const fetchGroupTrades = async () => {
    try {
      setLoading(true);
      // Get group details with admin info and pending requests
      const response = await axios.get(`/groups/${group.id}?user=${currentUser}`);
      setTrades(response.data.trades);
      setPendingRequests(response.data.pending_requests || []);
      setIsAdmin(response.data.is_admin || false);
      setError('');
    } catch (err) {
      setError('Failed to fetch group data.');
      console.error('Error fetching group data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewTrade(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!newTrade.symbol || !newTrade.quantity || !newTrade.price) {
      setError('Please fill in all fields');
      return;
    }

    try {
      const response = await axios.post('/trades', {
        ...newTrade,
        group_id: group.id,
        user: currentUser,
        timestamp: new Date().toISOString()
      });
      
      setTrades(prev => [...prev, response.data.trade]);
      setNewTrade({ symbol: '', quantity: '', price: '', type: 'buy' });
      setShowAddForm(false);
      setSuccess('Trade added successfully!');
      setError('');
      
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to add trade. Please try again.');
      console.error('Error adding trade:', err);
    }
  };

  const handleDelete = async (tradeId) => {
    try {
      await axios.delete(`/trades/${tradeId}`);
      setTrades(prev => prev.filter(trade => trade.id !== tradeId));
      setSuccess('Trade deleted successfully!');
      setError('');
      
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to delete trade. Please try again.');
      console.error('Error deleting trade:', err);
    }
  };

  const handleApproveRequest = async (requestId) => {
    try {
      await axios.post(`/groups/${group.id}/join/${requestId}/approve`, {
        admin_user: currentUser
      });
      
      // Remove from pending requests
      setPendingRequests(prev => prev.filter(req => req.id !== requestId));
      setSuccess('Join request approved!');
      setError('');
      
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to approve request.');
      console.error('Error approving request:', err);
    }
  };

  const handleRejectRequest = async (requestId) => {
    try {
      await axios.post(`/groups/${group.id}/join/${requestId}/reject`, {
        admin_user: currentUser
      });
      
      // Remove from pending requests
      setPendingRequests(prev => prev.filter(req => req.id !== requestId));
      setSuccess('Join request rejected.');
      setError('');
      
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to reject request.');
      console.error('Error rejecting request:', err);
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const getTotalValue = () => {
    return trades.reduce((total, trade) => {
      const value = trade.quantity * trade.price;
      return total + (trade.type === 'buy' ? value : -value);
    }, 0);
  };

  return (
    <div className="group-trades-container">
      {/* Header */}
      <div className="group-trades-header">
        <div className="header-left">
          <button onClick={onBack} className="btn btn-back">
            ← Back to Groups
          </button>
          <div className="group-info">
            <h2>{group.name}</h2>
            <p>{group.description}</p>
          </div>
        </div>
        <div className="header-right">
          <div className="group-stats">
            <div className="stat">
              <span className="stat-value">{trades.length}</span>
              <span className="stat-label">Trades</span>
            </div>
            <div className="stat">
              <span className={`stat-value ${getTotalValue() >= 0 ? 'positive' : 'negative'}`}>
                {formatPrice(Math.abs(getTotalValue()))}
              </span>
              <span className="stat-label">Net Position</span>
            </div>
          </div>
        </div>
      </div>

      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      {/* Action Bar */}
      <div className="action-bar">
        <button 
          className="btn btn-primary"
          onClick={() => setShowAddForm(!showAddForm)}
        >
          {showAddForm ? 'Cancel' : 'Add Trade'}
        </button>
      </div>

      {/* Admin Tabs */}
      {isAdmin && (
        <div className="admin-tabs">
          <button 
            className={`tab-button ${activeTab === 'trades' ? 'active' : ''}`}
            onClick={() => setActiveTab('trades')}
          >
            Trades ({trades.length})
          </button>
          <button 
            className={`tab-button ${activeTab === 'requests' ? 'active' : ''}`}
            onClick={() => setActiveTab('requests')}
          >
            Join Requests ({pendingRequests.length})
          </button>
        </div>
      )}

      {/* Add Trade Form */}
      {showAddForm && (
        <div className="add-trade-form">
          <h3>Add New Trade to {group.name}</h3>
          <form onSubmit={handleSubmit}>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="symbol">Symbol:</label>
                <input
                  type="text"
                  id="symbol"
                  name="symbol"
                  value={newTrade.symbol}
                  onChange={handleInputChange}
                  placeholder="e.g., AAPL"
                  required
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="quantity">Quantity:</label>
                <input
                  type="number"
                  id="quantity"
                  name="quantity"
                  value={newTrade.quantity}
                  onChange={handleInputChange}
                  placeholder="e.g., 100"
                  min="1"
                  required
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="price">Price:</label>
                <input
                  type="number"
                  id="price"
                  name="price"
                  value={newTrade.price}
                  onChange={handleInputChange}
                  placeholder="e.g., 150.50"
                  step="0.01"
                  min="0"
                  required
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="type">Type:</label>
                <select
                  id="type"
                  name="type"
                  value={newTrade.type}
                  onChange={handleInputChange}
                  required
                >
                  <option value="buy">Buy</option>
                  <option value="sell">Sell</option>
                </select>
              </div>
            </div>
            
            <button type="submit" className="btn btn-primary">Add Trade</button>
          </form>
        </div>
      )}

      {/* Content Section */}
      <div className="content-section">
        {activeTab === 'trades' ? (
          // Trades Tab Content
          <div className="trades-section">
            <h3>Group Trades</h3>
            
            {loading ? (
              <div className="loading">Loading trades...</div>
            ) : trades.length === 0 ? (
              <div className="no-trades">
                <p>No trades found in this group. Add your first trade above!</p>
              </div>
            ) : (
              <div className="trades-grid">
                {trades.map(trade => (
                  <div key={trade.id} className="trade-card">
                    <div className="trade-header">
                      <div className="trade-symbol">{trade.symbol}</div>
                      <div className={`trade-type trade-type-${trade.type}`}>
                        {trade.type.toUpperCase()}
                      </div>
                    </div>
                    
                    <div className="trade-details">
                      <div className="trade-detail">
                        <span className="detail-label">Quantity:</span>
                        <span className="detail-value">{trade.quantity}</span>
                      </div>
                      <div className="trade-detail">
                        <span className="detail-label">Price:</span>
                        <span className="detail-value">{formatPrice(trade.price)}</span>
                      </div>
                      <div className="trade-detail">
                        <span className="detail-label">Total:</span>
                        <span className="detail-value">
                          {formatPrice(trade.quantity * trade.price)}
                        </span>
                      </div>
                      <div className="trade-detail">
                        <span className="detail-label">By:</span>
                        <span className="detail-value">{trade.user}</span>
                      </div>
                      <div className="trade-detail">
                        <span className="detail-label">Date:</span>
                        <span className="detail-value">{formatDate(trade.timestamp)}</span>
                      </div>
                    </div>
                    
                    {trade.user === currentUser && (
                      <div className="trade-actions">
                        <button 
                          onClick={() => handleDelete(trade.id)}
                          className="btn btn-danger btn-small"
                        >
                          Delete
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          // Join Requests Tab Content (Admin Only)
          <div className="requests-section">
            <h3>Pending Join Requests</h3>
            
            {loading ? (
              <div className="loading">Loading requests...</div>
            ) : pendingRequests.length === 0 ? (
              <div className="no-requests">
                <p>No pending join requests.</p>
              </div>
            ) : (
              <div className="requests-grid">
                {pendingRequests.map(request => (
                  <div key={request.id} className="request-card">
                    <div className="request-header">
                      <div className="request-user">{request.user}</div>
                      <div className="request-date">
                        {formatDate(request.requested_at)}
                      </div>
                    </div>
                    
                    <div className="request-info">
                      <p>wants to join <strong>{group.name}</strong></p>
                    </div>
                    
                    <div className="request-actions">
                      <button 
                        onClick={() => handleApproveRequest(request.id)}
                        className="btn btn-approve"
                      >
                        Approve
                      </button>
                      <button 
                        onClick={() => handleRejectRequest(request.id)}
                        className="btn btn-reject"
                      >
                        Reject
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default GroupTrades;
