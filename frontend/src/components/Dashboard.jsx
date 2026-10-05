import React, { useState, useEffect } from 'react';
import { 
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip, 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend
} from 'recharts';

const Dashboard = ({ user, language, token }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const t = {
    Français: { title: 'Dashboard Santé Dynamique', total: 'Total des messages', emotions: 'Analyse des Émotions', profile: 'Profil Médical', distribution: 'Répartition Émotionnelle' },
    English: { title: 'Dynamic Health Dashboard', total: 'Total Messages', emotions: 'Emotion Analysis', profile: 'Medical Profile', distribution: 'Emotional Distribution' },
    العربية: { title: 'لوحة التحكم الصحية الديناميكية', total: 'إجمالي الرسائل', emotions: 'تحليل المشاعر', profile: 'الملف الطبي', distribution: 'توزيع المشاعر' }
  }[language];

  const COLORS = ['#ef4444', '#3b82f6', '#10b981', '#94a3b8', '#f59e0b'];

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch('/api/stats', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        setStats(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    if (token) fetchStats();
  }, [token]);

  if (loading) return <div className="p-8 text-white animate-pulse">Chargement des statistiques réelles...</div>;

  return (
    <div className="w-full h-full p-8 overflow-y-auto custom-scrollbar animate-fade-in">
      <h1 className="text-3xl font-bold text-white mb-8 flex items-center gap-4">
        📈 {t.title}
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Total Stats Card */}
        <div className="glass-card p-6 rounded-3xl bg-gradient-to-br from-primary-600/20 to-transparent border-primary-500/20">
          <p className="text-gray-400 text-sm font-bold uppercase mb-2">{t.total}</p>
          <p className="text-5xl font-black text-white">{stats?.total_messages || 0}</p>
          <div className="mt-4 p-3 bg-white/5 rounded-xl text-xs text-primary-400 italic">
            "Chaque message aide l'IA à mieux vous comprendre."
          </div>
        </div>

        {/* Profile Card */}
        <div className="glass-card p-6 rounded-3xl lg:col-span-2">
          <h2 className="text-lg font-bold text-gray-300 mb-6">{t.profile}</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 bg-white/5 rounded-2xl border border-white/10">
              <span className="text-[10px] text-gray-500 uppercase block mb-1">Groupe</span>
              <span className="text-xl font-bold text-red-500">{user?.blood_type || 'NC'}</span>
            </div>
            <div className="p-4 bg-white/5 rounded-2xl border border-white/10">
              <span className="text-[10px] text-gray-500 uppercase block mb-1">Âge</span>
              <span className="text-xl font-bold text-white">{user?.age || 0}</span>
            </div>
            <div className="p-4 bg-white/5 rounded-2xl border border-white/10 overflow-hidden">
              <span className="text-[10px] text-gray-500 uppercase block mb-1">Allergies</span>
              <span className="text-xs font-medium text-gray-200 truncate block">{user?.allergies || 'Aucune'}</span>
            </div>
            <div className="p-4 bg-white/5 rounded-2xl border border-white/10">
              <span className="text-[10px] text-gray-500 uppercase block mb-1">Maladies</span>
              <span className="text-xs font-medium text-gray-200 truncate block">{user?.chronic_diseases || 'Aucune'}</span>
            </div>
          </div>
        </div>

        {/* Emotion Pie Chart */}
        <div className="glass-card p-8 rounded-3xl lg:col-span-1 min-h-[400px]">
          <h2 className="text-lg font-bold text-gray-300 mb-6">{t.distribution}</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={stats?.emotion_data || []}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {(stats?.emotion_data || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                   contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '12px' }}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Emotion Bar Chart */}
        <div className="glass-card p-8 rounded-3xl lg:col-span-2 min-h-[400px]">
          <h2 className="text-lg font-bold text-gray-300 mb-6">{t.emotions}</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats?.emotion_data || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                <XAxis dataKey="name" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '12px' }} />
                <Bar dataKey="value" fill="#3b82f6" radius={[10, 10, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
