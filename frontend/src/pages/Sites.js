import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { LayoutDashboard, Globe, Bot, CreditCard, LogOut, Plus, ExternalLink, Trash2 } from 'lucide-react';
import api from '../utils/api';
import { toast } from 'sonner';

export default function Sites() {
  const { user, logout } = useAuth();
  const [sites, setSites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [newSiteUrl, setNewSiteUrl] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchSites();
  }, []);

  const fetchSites = async () => {
    try {
      const response = await api.get('/sites/');
      setSites(response.data);
    } catch (error) {
      toast.error('Failed to load sites');
    } finally {
      setLoading(false);
    }
  };

  const handleAddSite = async (e) => {
    e.preventDefault();
    try {
      await api.post('/sites/', { url: newSiteUrl, name: newSiteUrl });
      toast.success('Site added successfully');
      setNewSiteUrl('');
      setIsAddOpen(false);
      fetchSites();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to add site');
    }
  };

  const handleDelete = async (siteId) => {
    if (!confirm('Are you sure you want to delete this site?')) return;
    try {
      await api.delete(`/sites/${siteId}`);
      toast.success('Site deleted');
      fetchSites();
    } catch (error) {
      toast.error('Failed to delete site');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
      <aside className="fixed left-0 top-0 h-full w-64 glass p-6">
        <div className="flex items-center space-x-2 mb-8">
          <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center text-white font-bold">RF</div>
          <span className="text-xl font-bold">RankForge</span>
        </div>
        <nav className="space-y-2">
          <Link to="/dashboard" className="flex items-center space-x-3 px-4 py-3 rounded-xl hover:bg-slate-100 transition-colors">
            <LayoutDashboard className="w-5 h-5" /><span>Dashboard</span>
          </Link>
          <Link to="/sites" className="flex items-center space-x-3 px-4 py-3 rounded-xl bg-blue-50 text-blue-600 font-medium">
            <Globe className="w-5 h-5" /><span>Sites</span>
          </Link>
          <Link to="/ai-agents" className="flex items-center space-x-3 px-4 py-3 rounded-xl hover:bg-slate-100 transition-colors">
            <Bot className="w-5 h-5" /><span>AI Agents</span>
          </Link>
          <Link to="/billing" className="flex items-center space-x-3 px-4 py-3 rounded-xl hover:bg-slate-100 transition-colors">
            <CreditCard className="w-5 h-5" /><span>Billing</span>
          </Link>
        </nav>
        <div className="absolute bottom-6 left-6 right-6">
          <div className="card p-4 mb-4"><div className="text-sm text-slate-600 mb-1">Credits</div><div className="text-2xl font-bold">{user?.credits || 0}</div></div>
          <Button variant="outline" className="w-full" onClick={logout}><LogOut className="w-4 h-4 mr-2" />Logout</Button>
        </div>
      </aside>
      <main className="ml-64 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-8">
            <div><h1 className="text-3xl font-bold mb-2">Your Sites</h1><p className="text-slate-600">Manage and monitor your websites</p></div>
            <Dialog open={isAddOpen} onOpenChange={setIsAddOpen}>
              <DialogTrigger asChild>
                <Button data-testid="add-site-btn"><Plus className="w-4 h-4 mr-2" />Add Site</Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader><DialogTitle>Add New Site</DialogTitle></DialogHeader>
                <form onSubmit={handleAddSite} className="space-y-4">
                  <div><Input placeholder="https://yoursite.com" value={newSiteUrl} onChange={(e) => setNewSiteUrl(e.target.value)} required data-testid="site-url-input" /></div>
                  <Button type="submit" className="w-full" data-testid="add-site-submit-btn">Add Site</Button>
                </form>
              </DialogContent>
            </Dialog>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sites.map((site) => (
              <div key={site.site_id} className="card" data-testid={`site-card-${site.site_id}`}>
                <div className="mb-4"><h3 className="font-semibold text-lg mb-1">{site.name}</h3><a href={site.url} target="_blank" rel="noopener noreferrer" className="text-sm text-blue-600 hover:underline flex items-center"><span className="truncate">{site.url}</span><ExternalLink className="w-3 h-3 ml-1" /></a></div>
                {site.seo_score && (<div className="mb-4 p-3 bg-slate-50 rounded-lg"><div className="text-sm text-slate-600 mb-1">SEO Score</div><div className={`text-2xl font-bold ${site.seo_score >= 80 ? 'text-green-600' : site.seo_score >= 60 ? 'text-amber-600' : 'text-red-600'}`}>{site.seo_score}/100</div></div>)}
                <div className="flex space-x-2">
                  <Link to={`/audits/${site.site_id}`} className="flex-1"><Button variant="outline" className="w-full" size="sm">View Audits</Button></Link>
                  <Link to={`/keywords/${site.site_id}`} className="flex-1"><Button variant="outline" className="w-full" size="sm">Keywords</Button></Link>
                  <Button variant="ghost" size="sm" onClick={() => handleDelete(site.site_id)}><Trash2 className="w-4 h-4 text-red-600" /></Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
