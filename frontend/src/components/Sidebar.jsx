import React, { useState, useEffect } from 'react';

const Sidebar = ({ 
  conversations, 
  activeConvId, 
  onSelectConv, 
  onNewChat, 
  onRename, 
  onDelete, 
  language, 
  setLanguage,
  currentView,
  setView 
}) => {
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState('');

  const t = {
    Français: { new: 'Nouvelle Discussion', history: 'Historique', lang: 'Langue', chat: 'Chat', dashboard: 'Dashboard' },
    English: { new: 'New Chat', history: 'History', lang: 'Language', chat: 'Chat', dashboard: 'Dashboard' },
    العربية: { new: 'محادثة جديدة', history: 'السجل', lang: 'اللغة', chat: 'محادثة', dashboard: 'الإحصائيات' }
  }[language];

  const emergencies = {
    Français: { title: 'Urgences Tunisie', samu: 'SAMU : 190', pc: 'Prot. Civile : 198', police: 'Police : 197' },
    English: { title: 'Tunisia Emergency', samu: 'SAMU: 190', pc: 'Civ. Protection: 198', police: 'Police: 197' },
    العربية: { title: 'طوارئ تونس', samu: 'الإسعاف: 190', pc: 'الحماية المدنية: 198', police: 'الشرطة: 197' }
  }[language];

  return (
    <div className={`w-80 h-full bg-white/5 backdrop-blur-xl border-r border-white/10 flex flex-col transition-all duration-300 ${language === 'العربية' ? 'order-last border-l border-r-0' : ''}`}>
      <div className="p-6 space-y-4">
        {/* Navigation Tabs */}
        <div className="flex bg-white/5 p-1 rounded-xl">
          <button 
            onClick={() => setView('chat')}
            className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all ${currentView === 'chat' ? 'bg-primary-600 text-white' : 'text-gray-400 hover:text-white'}`}
          >
            💬 {t.chat}
          </button>
          <button 
            onClick={() => setView('dashboard')}
            className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all ${currentView === 'dashboard' ? 'bg-primary-600 text-white' : 'text-gray-400 hover:text-white'}`}
          >
            📊 {t.dashboard}
          </button>
        </div>

        <button 
          onClick={onNewChat}
          className="w-full py-4 px-6 bg-primary-600 hover:bg-primary-500 text-white rounded-2xl font-bold transition-all shadow-lg shadow-primary-900/20 flex items-center justify-center gap-3"
        >
          <span className="text-xl">+</span> {t.new}
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-4 space-y-2 custom-scrollbar">
        <p className="px-4 text-xs font-bold text-gray-500 uppercase tracking-widest mb-4">{t.history}</p>
        {conversations.map(conv => (
          <div 
            key={conv.id}
            onClick={() => onSelectConv(conv.id)}
            className={`group relative p-4 rounded-xl cursor-pointer transition-all border ${
              activeConvId === conv.id 
                ? 'bg-primary-500/20 border-primary-500/50 text-white' 
                : 'bg-transparent border-transparent text-gray-400 hover:bg-white/5 hover:text-gray-200'
            }`}
          >
            {editingId === conv.id ? (
              <input 
                autoFocus
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                onBlur={() => { onRename(conv.id, editTitle); setEditingId(null); }}
                onKeyPress={(e) => e.key === 'Enter' && (onRename(conv.id, editTitle), setEditingId(null))}
                className="bg-transparent border-none focus:ring-0 w-full p-0 text-sm"
              />
            ) : (
              <p className="text-sm truncate pr-8">{conv.title || 'Discussion Sans Titre'}</p>
            )}
            
            <div className="absolute right-2 top-1/2 -translate-y-1/2 flex opacity-0 group-hover:opacity-100 transition-opacity gap-1">
              <button 
                onClick={(e) => { e.stopPropagation(); setEditingId(conv.id); setEditTitle(conv.title); }}
                className="p-1 hover:text-primary-400"
              >
                ✏️
              </button>
              <button 
                onClick={(e) => { e.stopPropagation(); onDelete(conv.id); }}
                className="p-1 hover:text-red-400"
              >
                🗑️
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="px-6 py-4 border-t border-white/5 bg-red-500/5">
        <p className="text-[10px] font-bold text-red-400 uppercase tracking-wider mb-2">{emergencies.title}</p>
        <div className="grid grid-cols-1 gap-1 text-[11px] font-semibold text-gray-300">
          <div className="flex justify-between"><span>🚑 {emergencies.samu}</span></div>
          <div className="flex justify-between"><span>🚒 {emergencies.pc}</span></div>
          <div className="flex justify-between"><span>🚔 {emergencies.police}</span></div>
        </div>
      </div>

      <div className="p-6 border-t border-white/10 bg-black/20">
        <label className="text-xs font-bold text-gray-500 uppercase block mb-3">{t.lang}</label>
        <select 
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="Français" className="bg-gray-900">🇫🇷 Français</option>
          <option value="English" className="bg-gray-900">🇺🇸 English</option>
          <option value="العربية" className="bg-gray-900">🇸🇦 العربية</option>
        </select>
      </div>
    </div>
  );
};

export default Sidebar;
