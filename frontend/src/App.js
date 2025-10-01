import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Login from './Login';
import Groups from './Groups';
import GroupTrades from './GroupTrades';
import './App.css';

// Configure axios base URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001/api';
axios.defaults.baseURL = API_BASE_URL;

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentUser, setCurrentUser] = useState('');
  const [currentView, setCurrentView] = useState('groups'); // 'groups' or 'group-trades'
  const [selectedGroup, setSelectedGroup] = useState(null);

  // Check authentication status on component mount
  useEffect(() => {
    const isLoggedIn = localStorage.getItem('isLoggedIn');
    const username = localStorage.getItem('username');
    
    if (isLoggedIn === 'true' && username) {
      setIsAuthenticated(true);
      setCurrentUser(username);
    }
  }, []);

  const handleLogin = (username) => {
    setIsAuthenticated(true);
    setCurrentUser(username);
  };

  const handleLogout = () => {
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('username');
    setIsAuthenticated(false);
    setCurrentUser('');
    setCurrentView('groups');
    setSelectedGroup(null);
  };

  const handleGroupSelect = (group) => {
    setSelectedGroup(group);
    setCurrentView('group-trades');
  };

  const handleBackToGroups = () => {
    setCurrentView('groups');
    setSelectedGroup(null);
  };

  // Show login page if not authenticated
  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div className="app-container">
      {/* Header */}
      <div className="app-header">
        <div className="header-content">
          <div className="header-left">
            <h1>TradeCircle</h1>
            <p>Track and manage your trades with groups</p>
          </div>
          <div className="user-info">
            <span>Welcome, {currentUser}!</span>
            <button onClick={handleLogout} className="btn btn-logout">
              Logout
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="app-content">
        {currentView === 'groups' && (
          <Groups 
            onGroupSelect={handleGroupSelect}
            currentUser={currentUser}
          />
        )}
        
        {currentView === 'group-trades' && selectedGroup && (
          <GroupTrades 
            group={selectedGroup}
            onBack={handleBackToGroups}
            currentUser={currentUser}
          />
        )}
      </div>
    </div>
  );
}

export default App;
