import React, { useState, useEffect, useRef } from 'react';
import ProfileModal from './ProfileModal';

const Chat = ({ token, language, activeConvId, user, onLogout, onMessageSent }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const [showProfileEdit, setShowProfileEdit] = useState(false);
  const [currentEmotion, setCurrentEmotion] = useState('neutral');
  
  const chatEndRef = useRef(null);
  const audioRef = useRef(new Audio());
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const fileInputRef = useRef(null);

  const t = {
    Français: { 
      welcome: "Bonjour", 
      how: "comment puis-je vous aider ?", 
      placeholder: "Décrivez vos symptômes...", 
      send: "Envoyer",
      online: "En ligne • Intelligence Médicale",
      analyzing: "Analyse en cours...",
      guest: "Invité"
    },
    English: { 
      welcome: "Hello", 
      how: "how can I help you?", 
      placeholder: "Describe your symptoms...", 
      send: "Send",
      online: "Online • Medical AI",
      analyzing: "Analyzing...",
      guest: "Guest"
    },
    العربية: { 
      welcome: "مرحباً", 
      how: "كيف يمكنني مساعدتك؟", 
      placeholder: "صف أعراضك...", 
      send: "إرسال",
      online: "متصل • ذكاء طبي",
      analyzing: "جاري التحليل...",
      guest: "ضيف"
    }
  }[language];

  const isRTL = language === 'العربية';

  useEffect(() => {
    if (activeConvId && activeConvId !== -1) fetchMessages();
    else setMessages([]);
  }, [activeConvId]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchMessages = async () => {
    try {
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
      const res = await fetch(`/api/conversations/${activeConvId}/messages`, { headers });
      const data = await res.json();
      const formatted = data.map(m => ({ role: m.role, content: m.content }));
      setMessages(formatted);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSend = async (textOverride = null) => {
    const textToSend = textOverride || input;
    if (!textToSend.trim()) return;

    const userMsg = { role: 'user', content: textToSend };
    setMessages(prev => [...prev, userMsg]);
    if (!textOverride) setInput('');
    setLoading(true);

    try {
      const headers = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const res = await fetch('/api/chat', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          text: textToSend,
          language: language,
          conversation_id: activeConvId || -1,
          profile: user
        })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'bot', content: data.response }]);
      if (data.emotion) setCurrentEmotion(data.emotion);
      
      if (onMessageSent) onMessageSent();

      if (data.audio) {
        audioRef.current.src = `data:audio/mp3;base64,${data.audio}`;
        audioRef.current.play();
      }
    } catch (err) {
      setMessages(prev => [...prev, { role: 'bot', content: 'Erreur de connexion.' }]);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setLoading(true);
    setMessages(prev => [...prev, { role: 'user', content: `📄 [Analyse : ${file.name}]` }]);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('language', language);

    try {
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
      const res = await fetch('/api/analyze-document', {
        method: 'POST',
        headers,
        body: formData
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'bot', content: data.analysis }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'bot', content: 'Erreur lors de l\'analyse.' }]);
    } finally {
      setLoading(false);
    }
  };

  const toggleRecording = async () => {
    if (isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    } else {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorderRef.current = new MediaRecorder(stream);
        audioChunksRef.current = [];
        mediaRecorderRef.current.ondataavailable = (e) => audioChunksRef.current.push(e.data);
        mediaRecorderRef.current.onstop = async () => {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          const formData = new FormData();
          formData.append('file', audioBlob, 'recording.webm');
          const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
          const res = await fetch('/api/audio', { method: 'POST', headers, body: formData });
          const data = await res.json();
          if (data.text) handleSend(data.text);
        };
        mediaRecorderRef.current.start();
        setIsRecording(true);
      } catch (err) {
        console.error("Microphone error", err);
      }
    }
  };

  const getInitials = () => {
    if (!user) return "U";
    return `${user.first_name?.[0] || ''}${user.last_name?.[0] || ''}`.toUpperCase();
  };

  return (
    <div className={`flex flex-col h-[90vh] w-full glass-card rounded-3xl overflow-hidden animate-fade-in shadow-2xl relative ${isRTL ? 'rtl' : 'ltr'}`} dir={isRTL ? 'rtl' : 'ltr'}>
      <input type="file" ref={fileInputRef} onChange={handleFileUpload} className="hidden" accept="image/*,application/pdf" />
      
      {/* Header */}
      <header className="px-8 py-6 border-b border-white/10 flex justify-between items-center bg-white/5 backdrop-blur-md z-40 relative">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-full bg-gradient-to-br from-primary-500/20 to-primary-700/20 flex items-center justify-center shadow-2xl relative group overflow-hidden border border-white/10">
            <img 
              src={`/avatars/${['stress', 'tristesse', 'confusion', 'joie'].includes(currentEmotion) ? (currentEmotion === 'tristesse' ? 'sadness' : (currentEmotion === 'joie' ? 'neutral' : currentEmotion)) : 'neutral'}.png`} 
              alt="AI Avatar" 
              className="w-full h-full object-cover animate-pulse-slow"
            />
            <div className={`absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-gray-900 ${loading ? 'bg-yellow-400 animate-bounce' : 'bg-green-500'}`}></div>
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">Assistant Santé AI</h1>
            <p className="text-xs text-primary-400 font-medium">{t.online}</p>
          </div>
        </div>

        <div className="flex items-center gap-6">
          <div className="flex items-center gap-3 cursor-pointer group" onClick={() => setShowProfile(!showProfile)}>
            <div className={`text-right hidden sm:block ${isRTL ? 'text-left' : 'text-right'}`}>
              <p className="text-sm font-semibold text-white group-hover:text-primary-400 transition-colors">{user?.first_name} {user?.last_name}</p>
              {user?.email && <p className="text-xs text-gray-400">{user?.email}</p>}
            </div>
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center text-sm font-bold text-white shadow-lg border border-white/20">
              {getInitials()}
            </div>
          </div>

          {token ? (
            <button onClick={onLogout} className="p-3 rounded-xl bg-white/5 hover:bg-red-500/20 text-gray-400 hover:text-red-400 transition-all border border-white/10">🚪</button>
          ) : (
            <button onClick={onLogout} className="px-4 py-2 rounded-xl bg-primary-600/20 hover:bg-primary-600/40 text-primary-400 text-sm font-bold transition-all border border-primary-500/30">Se connecter</button>
          )}
        </div>
      </header>

      {/* Profile Popup */}
      {showProfile && user && (
        <div className="absolute top-24 right-8 w-64 bg-gray-900/95 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-2xl z-[60] animate-fade-in">
          <div className="text-center mb-4">
            <div className="w-16 h-16 rounded-full bg-primary-600 mx-auto flex items-center justify-center text-xl font-bold mb-2">{getInitials()}</div>
            <h3 className="text-white font-bold">{user.first_name} {user.last_name}</h3>
            <p className="text-xs text-gray-400">{user.email}</p>
          </div>
          <div className="space-y-3 border-t border-white/10 pt-4">
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Âge</span>
              <span className="text-gray-200">{user.age} ans</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Tél</span>
              <span className="text-gray-200">{user.phone}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Groupe</span>
              <span className="text-xl font-bold text-red-500">{user.blood_type || 'NC'}</span>
            </div>
            <div className="border-t border-white/5 pt-2">
              <p className="text-[10px] text-gray-500 uppercase font-bold mb-1">Allergies</p>
              <p className="text-xs text-gray-200 truncate">{user.allergies || 'Aucune'}</p>
            </div>
            <div className="border-t border-white/5 pt-2">
              <p className="text-[10px] text-gray-500 uppercase font-bold mb-1">Maladies</p>
              <p className="text-xs text-gray-200 truncate">{user.chronic_diseases || 'Aucune'}</p>
            </div>
            {(!token || user?.first_name === 'Invité') ? (
              <p className="text-[10px] text-primary-400 text-center mt-4">Connectez-vous pour modifier votre profil</p>
            ) : (
              <button 
                onClick={(e) => { 
                  e.stopPropagation(); 
                  setShowProfileEdit(true); 
                  setShowProfile(false); 
                }}
                className="w-full mt-4 py-3 bg-primary-600 hover:bg-primary-500 text-white text-xs font-bold rounded-lg transition-all shadow-md active:scale-95 flex items-center justify-center gap-2 cursor-pointer"
              >
                ✏️ Modifier mon Profil
              </button>
            )}
          </div>
        </div>
      )}

      {showProfileEdit && (
        <ProfileModal 
          user={user} 
          token={token} 
          onClose={() => setShowProfileEdit(false)} 
          onUpdate={() => onMessageSent('user')} 
        />
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-8 space-y-6 custom-scrollbar">
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-center opacity-40">
            <p className="text-4xl mb-4">👋</p>
            <p className="text-lg font-medium">{t.welcome} {user?.first_name}, {t.how}</p>
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`flex items-end gap-3 ${m.role === 'user' ? (isRTL ? 'justify-start' : 'justify-end flex-row-reverse') : (isRTL ? 'justify-end flex-row-reverse' : 'justify-start')} animate-slide-up`}>
            {m.role === 'bot' && (
              <div className="w-10 h-10 rounded-full overflow-hidden border border-white/10 bg-white/5 flex-shrink-0 shadow-lg">
                <img 
                  src={`/avatars/${['stress', 'tristesse', 'confusion', 'joie'].includes(currentEmotion) ? (currentEmotion === 'tristesse' ? 'sadness' : (currentEmotion === 'joie' ? 'neutral' : currentEmotion)) : 'neutral'}.png`} 
                  alt="AI"
                  className="w-full h-full object-cover"
                />
              </div>
            )}
            <div className={`max-w-[80%] p-4 rounded-2xl ${m.role === 'user' ? 'bg-primary-600 text-white rounded-br-none shadow-primary-500/20' : 'bg-white/10 text-gray-200 rounded-tl-none border border-white/5 shadow-xl'}`}>
              <p className="text-sm leading-relaxed">{m.content}</p>
            </div>
            {m.role === 'user' && (
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center text-[10px] font-bold text-white shadow-lg border border-white/20 flex-shrink-0">
                {getInitials()}
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className={`flex ${isRTL ? 'justify-end' : 'justify-start'} animate-pulse`}>
            <div className="bg-white/10 p-4 rounded-2xl border border-white/5 text-xs text-primary-400 font-bold">{t.analyzing}</div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Input */}
      <div className="p-6 bg-white/5 border-t border-white/10">
        <div className="relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder={t.placeholder}
            className={`w-full bg-white/5 border border-white/10 rounded-2xl px-6 py-4 ${isRTL ? 'pl-48 pr-6' : 'pr-48 pl-6'} text-white focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all`}
          />
          <div className={`absolute ${isRTL ? 'left-2' : 'right-2'} flex gap-2`}>
            <button onClick={() => fileInputRef.current.click()} className="p-3 rounded-xl transition-all bg-white/5 text-gray-400 hover:text-white hover:bg-white/10" title="Joindre un document">📎</button>
            <button onClick={toggleRecording} className={`p-3 rounded-xl transition-all shadow-md ${isRecording ? 'bg-red-500 text-white animate-pulse' : 'bg-white/5 text-gray-400 hover:text-white hover:bg-white/10'}`} title="Saisie vocale">🎤</button>
            <button onClick={() => handleSend()} className="px-6 py-2 bg-primary-600 hover:bg-primary-500 text-white rounded-xl font-bold transition-all shadow-lg"> {t.send} </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;
