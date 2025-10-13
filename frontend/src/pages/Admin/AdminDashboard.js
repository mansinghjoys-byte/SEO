import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../utils/api';
import { toast } from 'sonner';
import SEOSettings from './SEOSettings';
import PlansManagement from './PlansManagement';
import UsersManagement from './UsersManagement';
import SystemMonitoring from './SystemMonitoring';

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('adminToken');
    if (!token) {
      navigate('/admin/login');
      return;
    }

    loadStats();
  }, [navigate]);

  const loadStats = async () => {
    try {
      const token = localStorage.getItem('adminToken');
      const response = await api.get('/admin/stats', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStats(response.data);
    } catch (error) {
      if (error.response?.status === 401 || error.response?.status === 403) {
        toast.error('Session expired. Please login again.');
        localStorage.removeItem('adminToken');
        navigate('/admin/login');
      } else {
        toast.error('Failed to load statistics');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('adminToken');
    localStorage.removeItem('adminUser');
    toast.success('Logged out successfully');
    navigate('/admin/login');
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'seo', label: 'SEO Settings', icon: '🔍' },
    { id: 'plans', label: 'Pricing Plans', icon: '💳' },
    { id: 'users', label: 'Users', icon: '👥' },
    { id: 'monitoring', label: 'System Monitoring', icon: '📈' }
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="bg-black/30 backdrop-blur-lg border-b border-white/10 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <div className="text-2xl font-bold text-white">
                🛡️ RankForge Admin
              </div>
              <div className="hidden md:block px-3 py-1 bg-purple-600/30 rounded-full text-purple-200 text-sm">
                Super Administrator
              </div>
            </div>
            
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-red-600/20 hover:bg-red-600/30 text-red-300 rounded-lg transition-colors duration-200 flex items-center space-x-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              <span>Logout</span>
            </button>
          </div>
        </div>
      </header>

      {/* Stats Overview */}
      {stats && activeTab === 'overview' && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <StatCard
              icon="👥"
              label="Total Users"
              value={stats.total_users}
              subtext={`+${stats.new_users_today} today`}
              color="purple"
            />
            <StatCard
              icon="🌐"
              label="Total Sites"
              value={stats.total_sites}
              color="blue"
            />
            <StatCard
              icon="📊"
              label="Total Audits"
              value={stats.total_audits}
              subtext={`${stats.audits_today} today`}
              color="green"
            />
            <StatCard
              icon="💰"
              label="Revenue"
              value={`$${stats.revenue.toFixed(2)}`}
              color="yellow"
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <StatCard
              icon="🔑"
              label="Keywords Tracked"
              value={stats.total_keywords}
              color="indigo"
            />
            <StatCard
              icon="🤖"
              label="Active AI Agents"
              value={stats.active_agents}
              color="pink"
            />
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="bg-white/5 backdrop-blur-lg rounded-xl border border-white/10 overflow-hidden">
          {/* Tab Navigation */}
          <div className="flex flex-wrap border-b border-white/10 bg-black/20">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-4 text-sm font-medium transition-colors duration-200 flex items-center space-x-2 ${
                  activeTab === tab.id
                    ? 'bg-purple-600/30 text-white border-b-2 border-purple-500'
                    : 'text-slate-300 hover:text-white hover:bg-white/5'
                }`}
              >
                <span>{tab.icon}</span>
                <span className="hidden sm:inline">{tab.label}</span>
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'overview' && stats && (
              <div className="text-white">
                <h2 className="text-2xl font-bold mb-4">System Overview</h2>
                <p className="text-slate-300">
                  Welcome to the RankForge admin dashboard. Use the tabs above to manage different aspects of the platform.
                </p>
                
                <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-white/5 p-4 rounded-lg">
                    <h3 className="font-semibold mb-2">Quick Actions</h3>
                    <ul className="space-y-2 text-sm text-slate-300">
                      <li>• Manage global SEO settings</li>
                      <li>• Create and edit pricing plans</li>
                      <li>• View and manage users</li>
                      <li>• Monitor system health</li>
                    </ul>
                  </div>
                  <div className="bg-white/5 p-4 rounded-lg">
                    <h3 className="font-semibold mb-2">System Status</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-slate-300">Backend:</span>
                        <span className="text-green-400">✓ Running</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-300">Database:</span>
                        <span className="text-green-400">✓ Connected</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-300">Credits System:</span>
                        <span className="text-green-400">✓ Active</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'seo' && <SEOSettings />}
            {activeTab === 'plans' && <PlansManagement />}
            {activeTab === 'users' && <UsersManagement />}
            {activeTab === 'monitoring' && <SystemMonitoring />}
          </div>
        </div>
      </div>
    </div>
  );
};

const StatCard = ({ icon, label, value, subtext, color = 'purple' }) => {
  const colorClasses = {
    purple: 'from-purple-600/20 to-purple-800/20 border-purple-500/30',
    blue: 'from-blue-600/20 to-blue-800/20 border-blue-500/30',
    green: 'from-green-600/20 to-green-800/20 border-green-500/30',
    yellow: 'from-yellow-600/20 to-yellow-800/20 border-yellow-500/30',
    indigo: 'from-indigo-600/20 to-indigo-800/20 border-indigo-500/30',
    pink: 'from-pink-600/20 to-pink-800/20 border-pink-500/30'
  };

  return (
    <div className={`bg-gradient-to-br ${colorClasses[color]} backdrop-blur-lg rounded-xl p-6 border`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-slate-300 text-sm font-medium mb-1">{label}</p>
          <p className="text-white text-3xl font-bold">{value}</p>
          {subtext && <p className="text-slate-400 text-xs mt-1">{subtext}</p>}
        </div>
        <div className="text-3xl">{icon}</div>
      </div>
    </div>
  );
};

export default AdminDashboard;
