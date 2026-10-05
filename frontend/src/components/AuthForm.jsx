import React, { useState } from 'react';

const AuthForm = ({ onLoginSuccess, onGuestMode }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    first_name: '',
    last_name: '',
    phone: '',
    age: '',
    password: '',
    password_confirm: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const url = isLogin ? '/api/auth/login' : '/api/auth/signup';
    
    try {
      let body;
      let headers = {};

      if (isLogin) {
        // OAuth2 login expects form data
        const loginData = new FormData();
        loginData.append('username', formData.email); // standard field name for OAuth2
        loginData.append('password', formData.password);
        body = loginData;
      } else {
        body = JSON.stringify(formData);
        headers['Content-Type'] = 'application/json';
      }

      const response = await fetch(url, {
        method: 'POST',
        headers: headers,
        body: body
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Une erreur est survenue');
      }

      if (isLogin) {
        localStorage.setItem('token', data.access_token);
        onLoginSuccess(data.access_token);
      } else {
        alert('Inscription réussie ! Vous pouvez maintenant vous connecter.');
        setIsLogin(true);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md p-8 glass-card rounded-2xl animate-fade-in">
      <div className="flex justify-center mb-8">
        <div className="flex bg-white/5 p-1 rounded-xl">
          <button 
            onClick={() => setIsLogin(true)}
            className={`px-6 py-2 rounded-lg transition-all ${isLogin ? 'bg-primary-500 text-white' : 'text-gray-400 hover:text-white'}`}
          >
            Connexion
          </button>
          <button 
            onClick={() => setIsLogin(false)}
            className={`px-6 py-2 rounded-lg transition-all ${!isLogin ? 'bg-primary-500 text-white' : 'text-gray-400 hover:text-white'}`}
          >
            Inscription
          </button>
        </div>
      </div>

      <h2 className="text-2xl font-bold text-center mb-6 text-white">
        {isLogin ? 'Bon retour parmi nous' : 'Créer un compte'}
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-200 text-sm">
            {error}
          </div>
        )}

        {!isLogin && (
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1">Prénom</label>
              <input
                type="text"
                name="first_name"
                required
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                onChange={handleChange}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1">Nom</label>
              <input
                type="text"
                name="last_name"
                required
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                onChange={handleChange}
              />
            </div>
          </div>
        )}

        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1">Email</label>
          <input
            type="email"
            name="email"
            required
            className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
            onChange={handleChange}
          />
        </div>

        {!isLogin && (
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1">Téléphone</label>
              <input
                type="tel"
                name="phone"
                required
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                onChange={handleChange}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1">Âge</label>
              <input
                type="number"
                name="age"
                required
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                onChange={handleChange}
              />
            </div>
          </div>
        )}

        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1">Mot de passe</label>
          <input
            type="password"
            name="password"
            required
            className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
            onChange={handleChange}
          />
        </div>

        {!isLogin && (
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1">Confirmer le mot de passe</label>
            <input
              type="password"
              name="password_confirm"
              required
              className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              onChange={handleChange}
            />
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full py-4 bg-primary-600 hover:bg-primary-500 text-white rounded-2xl font-bold transition-all shadow-lg shadow-primary-900/20 disabled:opacity-50 mt-4"
        >
          {loading ? '...' : (isLogin ? 'Se connecter' : 'Créer le compte')}
        </button>

        <button
          type="button"
          onClick={onGuestMode}
          className="w-full py-3 bg-white/5 hover:bg-white/10 text-gray-300 rounded-2xl font-medium transition-all mt-3 border border-white/10"
        >
          Continuer en mode invité
        </button>
      </form>
    </div>
  );
};

export default AuthForm;
