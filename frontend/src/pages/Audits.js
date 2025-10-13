import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { LayoutDashboard, Globe, Bot, CreditCard, LogOut, Search, AlertTriangle } from 'lucide-react';
import api from '../utils/api';
import { toast } from 'sonner';

export default function Audits() {
  const { siteId } = useParams();
  const { user, logout } = useAuth();
  const [site, setSite] = useState(null);
  const [audits, setAudits] = useState([]);
  const [currentAudit, setCurrentAudit] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchSiteAndAudits();
  }, [siteId]);

  const fetchSiteAndAudits = async () => {
    try {
      const [siteRes, auditsRes] = await Promise.all([
        api.get(`/sites/${siteId}`),
        api.get(`/audits/site/${siteId}`)
      ]);
      setSite(siteRes.data);
      setAudits(auditsRes.data);
      if (auditsRes.data.length > 0) {
        setCurrentAudit(auditsRes.data[0]);
      }
    } catch (error) {
      toast.error('Failed to load audit data');
    }
  };

  const runAudit = async () => {
    if (user?.credits < 5) {
      toast.error('Insufficient credits. Please upgrade your plan.');
      return;
    }
    setLoading(true);
    try {
      const response = await api.post('/audits/', { site_id: siteId });
      toast.success('Audit completed!');
      setCurrentAudit(response.data);
      fetchSiteAndAudits();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Audit failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
      <aside className="fixed left-0 top-0 h-full w-64 glass p-6">
        <div className="flex items-center space-x-2 mb-8"><div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center text-white font-bold">RF</div><span className="text-xl font-bold">RankForge</span></div>
        <nav className="space-y-2"><Link to="/dashboard" className="flex items-center space-x-3 px-4 py-3 rounded-xl hover:bg-slate-100 transition-colors"><LayoutDashboard className="w-5 h-5" /><span>Dashboard</span></Link><Link to="/sites" className="flex items-center space-x-3 px-4 py-3 rounded-xl hover:bg-slate-100 transition-colors"><Globe className="w-5 h-5" /><span>Sites</span></Link><Link to="/ai-agents" className="flex items-center space-x-3 px-4 py-3 rounded-xl hover:bg-slate-100 transition-colors"><Bot className="w-5 h-5" /><span>AI Agents</span></Link><Link to="/billing" className="flex items-center space-x-3 px-4 py-3 rounded-xl hover:bg-slate-100 transition-colors"><CreditCard className="w-5 h-5" /><span>Billing</span></Link></nav>
        <div className="absolute bottom-6 left-6 right-6"><div className="card p-4 mb-4"><div className="text-sm text-slate-600 mb-1">Credits</div><div className="text-2xl font-bold">{user?.credits || 0}</div></div><Button variant="outline" className="w-full" onClick={logout}><LogOut className="w-4 h-4 mr-2" />Logout</Button></div>
      </aside>
      <main className="ml-64 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-8"><div><h1 className="text-3xl font-bold mb-2">SEO Audit - {site?.name}</h1><p className="text-slate-600">{site?.url}</p></div><Button onClick={runAudit} disabled={loading} data-testid="run-audit-btn">{loading ? 'Running...' : 'Run New Audit'} <Search className="w-4 h-4 ml-2" /></Button></div>
          {currentAudit ? (<div className="space-y-6"><div className="grid md:grid-cols-4 gap-4"><div className="card"><div className="text-sm text-slate-600 mb-1">Overall Score</div><div className={`text-3xl font-bold ${currentAudit.seo_score >= 80 ? 'text-green-600' : currentAudit.seo_score >= 60 ? 'text-amber-600' : 'text-red-600'}`}>{currentAudit.seo_score}/100</div></div><div className="card"><div className="text-sm text-slate-600 mb-1">Technical</div><div className="text-3xl font-bold text-blue-600">{currentAudit.technical_score}/100</div></div><div className="card"><div className="text-sm text-slate-600 mb-1">On-Page</div><div className="text-3xl font-bold text-purple-600">{currentAudit.onpage_score}/100</div></div><div className="card"><div className="text-sm text-slate-600 mb-1">Off-Page</div><div className="text-3xl font-bold text-green-600">{currentAudit.offpage_score}/100</div></div></div><div className="card"><h2 className="text-xl font-bold mb-4">Issues Found</h2><div className="space-y-3">{currentAudit.issues.map((issue, index) => (<div key={index} className="p-4 border border-slate-200 rounded-xl" data-testid={`issue-${index}`}><div className="flex items-start justify-between mb-2"><div className="flex items-center space-x-2"><AlertTriangle className={`w-5 h-5 ${issue.severity === 'critical' ? 'text-red-600' : issue.severity === 'high' ? 'text-amber-600' : 'text-blue-600'}`} /><span className={`text-xs px-2 py-1 rounded-full ${issue.severity === 'critical' ? 'bg-red-100 text-red-700' : issue.severity === 'high' ? 'bg-amber-100 text-amber-700' : 'bg-blue-100 text-blue-700'}`}>{issue.severity}</span></div><span className="text-sm text-slate-500">{issue.category}</span></div><h3 className="font-semibold mb-2">{issue.title}</h3><p className="text-sm text-slate-600 mb-3">{issue.description}</p><div className="p-3 bg-blue-50 rounded-lg"><p className="text-sm text-blue-900"><strong>Fix:</strong> {issue.fix}</p></div></div>))}</div></div><div className="card"><h2 className="text-xl font-bold mb-4">AI Recommendations</h2><ul className="space-y-2">{currentAudit.recommendations.map((rec, index) => (<li key={index} className="flex items-start space-x-2"><span className="text-green-600 mt-1">•</span><span className="text-slate-700">{rec}</span></li>))}</ul></div></div>) : (<div className="text-center py-16"><Search className="w-16 h-16 text-slate-300 mx-auto mb-4" /><p className="text-slate-600 mb-4">No audits yet. Run your first audit to get started!</p><Button onClick={runAudit} disabled={loading}>Run First Audit</Button></div>)}
        </div>
      </main>
    </div>
  );
}
