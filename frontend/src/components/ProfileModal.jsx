import React, { useState } from 'react';

const ProfileModal = ({ user, token, onClose, onUpdate }) => {
  const [formData, setFormData] = useState({
    age: user.age || '',
    phone: user.phone || '',
    blood_type: user.blood_type || '',
    allergies: user.allergies || '',
    chronic_diseases: user.chronic_diseases || ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch('/api/auth/profile', {
        method: 'PUT',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });
      if (res.ok) {
        onUpdate();
        onClose();
      } else {
        const errorData = await res.json();
        alert(`Erreur : ${errorData.detail || 'Impossible de mettre à jour le profil'}`);
      }
    } catch (err) {
      console.error(err);
      alert("Une erreur de connexion est survenue.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
      <div className="glass-card w-full max-w-md p-8 rounded-3xl shadow-2xl border border-white/20 animate-slide-up">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-white">Modifier mon Profil</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white text-2xl">×</button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase mb-1">Âge</label>
              <input 
                type="number" 
                value={formData.age}
                onChange={(e) => setFormData({...formData, age: e.target.value})}
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2 text-white focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase mb-1">Groupe Sanguin</label>
              <select 
                value={formData.blood_type}
                onChange={(e) => setFormData({...formData, blood_type: e.target.value})}
                className="w-full bg-gray-800 border border-white/10 rounded-xl px-4 py-2 text-white focus:ring-2 focus:ring-primary-500"
              >
                <option value="NC">Non communiqué (NC)</option>
                {['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'].map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-gray-400 uppercase mb-1">Téléphone</label>
            <input 
              type="text" 
              value={formData.phone}
              onChange={(e) => setFormData({...formData, phone: e.target.value})}
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2 text-white"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-gray-400 uppercase mb-1">Allergies</label>
            <textarea 
              value={formData.allergies}
              onChange={(e) => setFormData({...formData, allergies: e.target.value})}
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2 text-white h-20"
              placeholder="Ex: Pénicilline, Pollen..."
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-gray-400 uppercase mb-1">Maladies Chroniques</label>
            <textarea 
              value={formData.chronic_diseases}
              onChange={(e) => setFormData({...formData, chronic_diseases: e.target.value})}
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2 text-white h-20"
              placeholder="Ex: Asthme, Diabète..."
            />
          </div>

          <button 
            type="submit" 
            disabled={loading}
            className="w-full py-4 bg-primary-600 hover:bg-primary-500 text-white rounded-2xl font-bold transition-all shadow-lg"
          >
            {loading ? 'Mise à jour...' : 'Enregistrer les modifications'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ProfileModal;
