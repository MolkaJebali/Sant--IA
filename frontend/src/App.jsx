import React, { useState, useEffect } from 'react';
import AuthForm from './components/AuthForm';
import Chat from './components/Chat';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [language, setLanguage] = useState('Français');
  const [conversations, setConversations] = useState([]);
  const [activeConvId, setActiveConvId] = useState(null);
  const [isGuest, setIsGuest] = useState(false);
  const [view, setView] = useState('chat'); // 'chat' or 'dashboard'
  const [user, setUser] = useState(null);

  useEffect(() => {
    if (token) {
      fetchUserData();
      fetchConversations();
    } else if (isGuest) {
      setUser({ first_name: 'Invité', last_name: '', age: 0, phone: 'N/A' });
    }
  }, [token, isGuest]);

  const fetchUserData = async () => {
    try {
      const res = await fetch('/api/auth/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.status === 401) {
        handleLogout();
        return;
      }
      const data = await res.json();
      if (data && (data.email || data.first_name)) {
        setUser({ ...data });
      }
    } catch (err) {
      console.error(err);
    }
  };

  const fetchConversations = async () => {
    try {
      const res = await fetch('/api/conversations', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.status === 401) {
        handleLogout();
        return;
      }
      const data = await res.json();
      setConversations(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleLogin = (newToken) => {
    localStorage.setItem('token', newToken);
    setToken(newToken);
    setIsGuest(false);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setIsGuest(false);
    setUser(null);
    setConversations([]);
    setActiveConvId(null);
    setView('chat');
  };

  const handleNewChat = async () => {
    setView('chat');
    if (!token) {
      setActiveConvId(-1);
      return;
    }
    try {
      const res = await fetch('/api/conversations', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await res.json();
      setConversations([data, ...conversations]);
      setActiveConvId(data.id);
    } catch (err) {
      console.error(err);
    }
  };

  const handleRename = async (id, title) => {
    if (!token) return;
    try {
      const formData = new FormData();
      formData.append('title', title);
      await fetch(`/api/conversations/${id}`, {
        method: 'PUT',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });
      fetchConversations();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id) => {
    if (!token) return;
    try {
      await fetch(`/api/conversations/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (activeConvId === id) setActiveConvId(null);
      fetchConversations();
    } catch (err) {
      console.error(err);
    }
  };

  const showChat = token || isGuest;

  return (
    <div className="min-h-screen w-full flex bg-[#0f172a] overflow-hidden">
      {showChat ? (
        <>
          <Sidebar 
            conversations={conversations}
            activeConvId={activeConvId}
            onSelectConv={(id) => { setActiveConvId(id); setView('chat'); }}
            onNewChat={handleNewChat}
            onRename={handleRename}
            onDelete={handleDelete}
            language={language}
            setLanguage={setLanguage}
            currentView={view}
            setView={setView}
          />
          <main className="flex-1 flex items-center justify-center p-8">
            {view === 'chat' ? (
              <Chat 
                token={token} 
                language={language} 
                activeConvId={activeConvId}
                user={user}
                onLogout={handleLogout} 
                onMessageSent={(type) => {
                  if (type === 'user') fetchUserData();
                  else fetchConversations();
                }}
              />
            ) : (
              <Dashboard user={user} language={language} token={token} />
            )}
          </main>
        </>
      ) : (
        <div className="flex-1 flex items-center justify-center p-4">
          <AuthForm 
            onLoginSuccess={handleLogin} 
            onGuestMode={() => setIsGuest(true)}
          />
        </div>
      )}
    </div>
  );
}

export default App;
