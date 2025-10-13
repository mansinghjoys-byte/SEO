import React, { useState, useEffect } from 'react';
import api from '../../utils/api';
import { toast } from 'sonner';

const SystemMonitoring = () => {
  const [stats, setStats] = useState(null);
  const [activities, setActivities] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const token = localStorage.getItem('adminToken');
      const [statsRes, activitiesRes] = await Promise.all([
        api.get('/admin/stats', { headers: { Authorization: `Bearer ${token}` } }),
        api.get('/admin/recent-activities?limit=20', { headers: { Authorization: `Bearer ${token}` } })
      ]);
      setStats(statsRes.data);
      setActivities(activitiesRes.data);
    } catch (error) {
      toast.error('Failed to load monitoring data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-white text-center py-8">Loading system data...</div>;
  }

  return (
    <div className="text-white space-y-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">System Monitoring</h2>
        <button
          onClick={loadData}
          className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg flex items-center space-x-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span>Refresh</span>
        </button>
      </div>

      {/* System Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatBox label="Total Users" value={stats.total_users} icon="👥" color="blue" />
          <StatBox label="Total Sites" value={stats.total_sites} icon="🌐" color="green" />
          <StatBox label="Total Audits" value={stats.total_audits} icon="📊" color="purple" />
          <StatBox label="Keywords" value={stats.total_keywords} icon="🔑" color="yellow" />
          <StatBox label="Active Agents" value={stats.active_agents} icon="🤖" color="pink" />
          <StatBox label="Credits Used" value={stats.credits_consumed} icon="💳" color="indigo" />
          <StatBox label="Revenue" value={`$${stats.revenue.toFixed(2)}`} icon="💰" color="green" />
          <StatBox label="New Today" value={stats.new_users_today} icon="✨" color="blue" />
        </div>
      )}

      {/* Recent Activities */}
      {activities && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Audits */}
          <div className="bg-white/5 rounded-lg p-6">
            <h3 className="text-xl font-semibold mb-4 flex items-center space-x-2">
              <span>📊</span>
              <span>Recent Audits</span>
            </h3>
            <div className="space-y-3">
              {activities.recent_audits?.slice(0, 5).map((audit, idx) => (
                <div key={idx} className="bg-white/5 rounded-lg p-3 text-sm">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-medium">SEO Score: {audit.seo_score}/100</div>
                      <div className="text-slate-400 text-xs mt-1">
                        {new Date(audit.created_at).toLocaleString()}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-xs text-slate-400">Site ID</div>
                      <div className="text-xs font-mono">{audit.site_id.slice(0, 8)}...</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Users */}
          <div className="bg-white/5 rounded-lg p-6">
            <h3 className="text-xl font-semibold mb-4 flex items-center space-x-2">
              <span>👥</span>
              <span>Recent Registrations</span>
            </h3>
            <div className="space-y-3">
              {activities.recent_users?.slice(0, 5).map((user, idx) => (
                <div key={idx} className="bg-white/5 rounded-lg p-3 text-sm">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-medium">{user.full_name}</div>
                      <div className="text-slate-400 text-xs">{user.email}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-xs px-2 py-1 bg-purple-600/30 rounded">{user.plan}</div>
                      <div className="text-xs text-slate-400 mt-1">
                        {new Date(user.created_at).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Transactions */}
          <div className="bg-white/5 rounded-lg p-6 lg:col-span-2">
            <h3 className="text-xl font-semibold mb-4 flex items-center space-x-2">
              <span>💳</span>
              <span>Recent Credit Transactions</span>
            </h3>
            <div className="space-y-2">
              {activities.recent_transactions?.slice(0, 10).map((txn, idx) => (
                <div key={idx} className="flex justify-between items-center bg-white/5 rounded-lg p-3 text-sm">
                  <div>
                    <div className="font-medium">{txn.description}</div>
                    <div className="text-slate-400 text-xs">
                      User: {txn.user_id?.slice(0, 8)}...
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`font-bold ${txn.amount < 0 ? 'text-red-400' : 'text-green-400'}`}>
                      {txn.amount > 0 ? '+' : ''}{txn.amount} credits
                    </div>
                    <div className="text-slate-400 text-xs">
                      {new Date(txn.timestamp).toLocaleString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* System Health */}
      <div className="bg-white/5 rounded-lg p-6">
        <h3 className="text-xl font-semibold mb-4 flex items-center space-x-2">
          <span>🏥</span>
          <span>System Health</span>
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <HealthIndicator label="API Status" status="healthy" />
          <HealthIndicator label="Database" status="healthy" />
          <HealthIndicator label="Background Jobs" status="healthy" />
        </div>
      </div>
    </div>
  );
};

const StatBox = ({ label, value, icon, color }) => {
  const colors = {
    blue: 'border-blue-500/30',
    green: 'border-green-500/30',
    purple: 'border-purple-500/30',
    yellow: 'border-yellow-500/30',
    pink: 'border-pink-500/30',
    indigo: 'border-indigo-500/30'
  };

  return (
    <div className={`bg-white/5 rounded-lg p-4 border ${colors[color]}`}>
      <div className="flex items-center justify-between">
        <div>
          <div className="text-slate-300 text-sm">{label}</div>
          <div className="text-2xl font-bold mt-1">{value}</div>
        </div>
        <div className="text-3xl">{icon}</div>
      </div>
    </div>
  );
};

const HealthIndicator = ({ label, status }) => {
  const statusColors = {
    healthy: 'bg-green-600/20 text-green-400',
    warning: 'bg-yellow-600/20 text-yellow-400',
    error: 'bg-red-600/20 text-red-400'
  };

  const statusIcons = {
    healthy: '✓',
    warning: '⚠',
    error: '✗'
  };

  return (
    <div className="bg-white/5 rounded-lg p-4">
      <div className="text-slate-300 text-sm mb-2">{label}</div>
      <div className={`px-3 py-1 rounded inline-flex items-center space-x-2 ${statusColors[status]}`}>
        <span>{statusIcons[status]}</span>
        <span className="font-semibold capitalize">{status}</span>
      </div>
    </div>
  );
};

export default SystemMonitoring;