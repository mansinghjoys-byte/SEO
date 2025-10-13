import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { LayoutDashboard, Globe, Search, Bot, CreditCard, Menu, LogOut, TrendingUp, AlertCircle, CheckCircle } from 'lucide-react';
import api from '../utils/api';
import { toast } from 'sonner';

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [sites, setSites] = useState([]);
  const [stats, setStats] = useState({ totalSites: 0, avgScore: 0, issues: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const response = await api.get('/sites/');
      setSites(response.data);
      
      const avgScore = response.data.reduce((acc, site) => acc + (site.seo_score || 0), 0) / response.data.length || 0;
      setStats({
        totalSites: response.data.length,
        avgScore: Math.round(avgScore),
        issues: response.data.filter(s => (s.seo_score || 0) < 70).length
      });
    } catch (error) {
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
      {/* Sidebar */}
      <aside className="fixed left-0 top-0 h-full w-64 glass p-6" data-testid="sidebar">
        <div className="flex items-center space-x-2 mb-8">
          <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center text-white font-bold">
            RF
          </div>
          <span className="text-xl font-bold">RankForge</span>
        </div>

        <nav className="space-y-2">
          <Link to="/dashboard" className="flex items-center space-x-3 px-4 py-3 rounded-xl bg-blue-50 text-blue-600 font-medium" data-testid="nav-dashboard">
            <LayoutDashboard className="w-5 h-5" />
            <span>Dashboard</span>
          </Link>
          <Link to="/sites" className="flex items-center space-x-3 px-4 py-3 rounded-xl hover:bg-slate-100 transition-colors" data-testid="nav-sites">
            <Globe className="w-5 h-5" />
            <span>Sites</span>
          </Link>
          <Link to="/ai-agents" className="flex items-center space-x-3 px-4 py-3 rounded-xl hover:bg-slate-100 transition-colors" data-testid="nav-agents">
            <Bot className="w-5 h-5" />
            <span>AI Agents</span>
          </Link>
          <Link to="/billing" className="flex items-center space-x-3 px-4 py-3 rounded-xl hover:bg-slate-100 transition-colors" data-testid="nav-billing">
            <CreditCard className="w-5 h-5" />
            <span>Billing</span>
          </Link>
        </nav>

        <div className="absolute bottom-6 left-6 right-6">
          <div className="card p-4 mb-4">
            <div className="text-sm text-slate-600 mb-1">Credits</div>
            <div className="text-2xl font-bold" data-testid="credits-display">{user?.credits || 0}</div>
          </div>
          <Button variant="outline" className="w-full" onClick={logout} data-testid="logout-btn">
            <LogOut className="w-4 h-4 mr-2" />
            Logout
          </Button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="ml-64 p-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold mb-2" data-testid="dashboard-title">Welcome back, {user?.full_name}!</h1>
            <p className="text-slate-600">Here's what's happening with your SEO</p>
          </div>

          {/* Stats */}
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <div className="card" data-testid="stat-sites">
              <div className="flex items-center justify-between mb-4">
                <Globe className="w-10 h-10 text-blue-600" />
                <span className="text-sm text-slate-600">Total Sites</span>
              </div>
              <div className="text-3xl font-bold">{stats.totalSites}</div>
            </div>
            <div className="card" data-testid="stat-score">
              <div className="flex items-center justify-between mb-4">
                <TrendingUp className="w-10 h-10 text-green-600" />
                <span className="text-sm text-slate-600">Avg SEO Score</span>
              </div>
              <div className="text-3xl font-bold">{stats.avgScore}/100</div>
            </div>
            <div className="card" data-testid="stat-issues">
              <div className="flex items-center justify-between mb-4">
                <AlertCircle className="w-10 h-10 text-amber-600" />
                <span className="text-sm text-slate-600">Sites Need Attention</span>
              </div>
              <div className="text-3xl font-bold">{stats.issues}</div>
            </div>
          </div>

          {/* Sites List */}
          <div className="card">
            <h2 className="text-xl font-bold mb-4">Your Sites</h2>
            {loading ? (
              <div className="text-center py-8"><div className="spinner mx-auto"></div></div>
            ) : sites.length === 0 ? (
              <div className="text-center py-12">
                <Globe className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                <p className="text-slate-600 mb-4">No sites added yet</p>
                <Link to="/sites">
                  <Button data-testid="add-first-site-btn">Add Your First Site</Button>
                </Link>
              </div>
            ) : (
              <div className="space-y-3">
                {sites.map((site) => (
                  <Link to={`/audits/${site.site_id}`} key={site.site_id} className="block">
                    <div className="p-4 rounded-xl border border-slate-200 hover:border-blue-300 hover:shadow-md transition-all" data-testid={`site-${site.site_id}`}>
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-semibold text-lg">{site.name}</div>
                          <div className="text-sm text-slate-600">{site.url}</div>
                        </div>
                        <div className="text-right">
                          {site.seo_score ? (
                            <div className={`text-2xl font-bold ${
                              site.seo_score >= 80 ? 'text-green-600' :
                              site.seo_score >= 60 ? 'text-amber-600' : 'text-red-600'
                            }`}>
                              {site.seo_score}/100
                            </div>
                          ) : (
                            <Button size="sm">Run Audit</Button>
                          )}
                        </div>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
