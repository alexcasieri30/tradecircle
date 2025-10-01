import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Groups.css';

const Groups = ({ onGroupSelect, currentUser }) => {
  const [groups, setGroups] = useState([]);
  const [allGroups, setAllGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchLoading, setSearchLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [newGroup, setNewGroup] = useState({
    name: '',
    description: ''
  });

  useEffect(() => {
    fetchGroups();
  }, []);

  const fetchGroups = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`/groups?user=${currentUser}`);
      setGroups(response.data.groups);
      setError('');
    } catch (err) {
      setError('Failed to fetch groups. Please check if the backend is running.');
      console.error('Error fetching groups:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewGroup(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleCreateGroup = async (e) => {
    e.preventDefault();
    
    if (!newGroup.name || !newGroup.description) {
      setError('Please fill in all fields');
      return;
    }

    try {
      const response = await axios.post('/groups', {
        ...newGroup,
        created_by: currentUser,
        created_at: new Date().toISOString()
      });
      
      setGroups(prev => [...prev, response.data.group]);
      setNewGroup({ name: '', description: '' });
      setShowCreateForm(false);
      setSuccess('Group created successfully!');
      setError('');
      
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to create group. Please try again.');
      console.error('Error creating group:', err);
    }
  };

  const handleGroupClick = (group) => {
    onGroupSelect(group);
  };

  const handleSearchGroups = async () => {
    try {
      setSearchLoading(true);
      const response = await axios.get(`/groups/search?user=${currentUser}`);
      setAllGroups(response.data.groups);
      setShowSearchResults(true);
      setError('');
    } catch (err) {
      setError('Failed to search groups. Please try again.');
      console.error('Error searching groups:', err);
    } finally {
      setSearchLoading(false);
    }
  };

  const handleJoinRequest = async (groupId) => {
    try {
      const response = await axios.post(`/groups/${groupId}/join`, {
        user: currentUser,
        requested_at: new Date().toISOString()
      });
      
      setSuccess('Join request sent successfully!');
      setError('');
      
      // Update the local state to reflect the pending request
      setAllGroups(prev => prev.map(group => 
        group.id === groupId 
          ? { ...group, has_pending_request: true }
          : group
      ));
      
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to send join request.');
      console.error('Error sending join request:', err);
    }
  };

  const handleBackToMyGroups = () => {
    setShowSearchResults(false);
    setAllGroups([]);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="groups-container">
      <div className="groups-header">
        <h2>{showSearchResults ? 'All Groups' : 'Your Groups'}</h2>
        <div className="header-buttons">
          {showSearchResults ? (
            <button 
              className="btn btn-secondary"
              onClick={handleBackToMyGroups}
            >
              ← Back to My Groups
            </button>
          ) : (
            <>
              <button 
                className="btn btn-search"
                onClick={handleSearchGroups}
                disabled={searchLoading}
              >
                {searchLoading ? 'Searching...' : 'Search Groups'}
              </button>
              <button 
                className="btn btn-primary"
                onClick={() => setShowCreateForm(!showCreateForm)}
              >
                {showCreateForm ? 'Cancel' : 'Create Group'}
              </button>
            </>
          )}
        </div>
      </div>

      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      {/* Create Group Form */}
      {showCreateForm && (
        <div className="create-group-form">
          <h3>Create New Group</h3>
          <form onSubmit={handleCreateGroup}>
            <div className="form-group">
              <label htmlFor="name">Group Name:</label>
              <input
                type="text"
                id="name"
                name="name"
                value={newGroup.name}
                onChange={handleInputChange}
                placeholder="e.g., Tech Stocks Group"
                required
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="description">Description:</label>
              <textarea
                id="description"
                name="description"
                value={newGroup.description}
                onChange={handleInputChange}
                placeholder="Describe what this group focuses on..."
                rows="3"
                required
              />
            </div>
            
            <div className="form-actions">
              <button type="submit" className="btn btn-primary">
                Create Group
              </button>
              <button 
                type="button" 
                className="btn btn-secondary"
                onClick={() => setShowCreateForm(false)}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Groups List */}
      <div className="groups-grid">
        {(loading || searchLoading) ? (
          <div className="loading">
            {searchLoading ? 'Searching groups...' : 'Loading groups...'}
          </div>
        ) : showSearchResults ? (
          // Search Results View
          allGroups.length === 0 ? (
            <div className="no-groups">
              <p>No groups found in search results.</p>
            </div>
          ) : (
            allGroups.map(group => (
              <div 
                key={group.id} 
                className={`group-card ${!group.is_member ? 'group-card-search' : ''}`}
                onClick={group.is_member ? () => handleGroupClick(group) : undefined}
              >
                <div className="group-header">
                  <h3>{group.name}</h3>
                  <span className="group-members-count">
                    {group.members.length} member{group.members.length !== 1 ? 's' : ''}
                  </span>
                </div>
                
                <p className="group-description">{group.description}</p>
                
                {/* Members Section */}
                <div className="group-members-section">
                  <h4 className="members-title">Members:</h4>
                  <div className="members-list">
                    {group.members.map((member, index) => (
                      <span key={index} className="member-tag">
                        {member}
                      </span>
                    ))}
                  </div>
                </div>
                
                <div className="group-footer">
                  <span className="group-creator">
                    Created by {group.created_by}
                  </span>
                  <span className="group-date">
                    {formatDate(group.created_at)}
                  </span>
                </div>
                
                <div className="group-action">
                  {group.is_member ? (
                    <span className="click-hint">Click to view trades →</span>
                  ) : group.has_pending_request ? (
                    <span className="request-status pending">Join request pending</span>
                  ) : (
                    <button 
                      className="btn btn-join"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleJoinRequest(group.id);
                      }}
                    >
                      Request to Join
                    </button>
                  )}
                </div>
              </div>
            ))
          )
        ) : (
          // User's Groups View
          groups.length === 0 ? (
            <div className="no-groups">
              <p>No groups found. Create your first group to get started!</p>
            </div>
          ) : (
            groups.map(group => (
              <div 
                key={group.id} 
                className="group-card"
                onClick={() => handleGroupClick(group)}
              >
                <div className="group-header">
                  <h3>{group.name}</h3>
                  <span className="group-members-count">
                    {group.members.length} member{group.members.length !== 1 ? 's' : ''}
                  </span>
                </div>
                
                <p className="group-description">{group.description}</p>
                
                {/* Members Section */}
                <div className="group-members-section">
                  <h4 className="members-title">Members:</h4>
                  <div className="members-list">
                    {group.members.map((member, index) => (
                      <span key={index} className="member-tag">
                        {member}
                      </span>
                    ))}
                  </div>
                </div>
                
                <div className="group-footer">
                  <span className="group-creator">
                    Created by {group.created_by}
                  </span>
                  <span className="group-date">
                    {formatDate(group.created_at)}
                  </span>
                </div>
                
                <div className="group-action">
                  <span className="click-hint">Click to view trades →</span>
                </div>
              </div>
            ))
          )
        )}
      </div>
    </div>
  );
};

export default Groups;
