import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { LayoutDashboard, Globe, Bot, CreditCard, LogOut, Plus, Search } from 'lucide-react';
import api from '../utils/api';
import { toast } from 'sonner';

export default function Keywords() {
  const { siteId } = useParams();
  const { user, logout } = useAuth();
  const [keywords, setKeywords] = useState([]);
  const [seedKeyword, setSeedKeyword] = useState('');
  const [loading, setLoading] = useState(false);
  const [isResearchOpen, setIsResearchOpen] = useState(false);

  useEffect(() => {
    fetchKeywords();
  }, [siteId]);

  const fetchKeywords = async () => {
    try {
      const response = await api.get(`/keywords/site/${siteId}`);
      setKeywords(response.data);
    } catch (error) {
      toast.error('Failed to load keywords');
    }
  };

  const researchKeywords = async (e) => {
    e.preventDefault();
    if (user?.credits < 2) {
      toast.error('Insufficient credits');
      return;
    }
    setLoading(true);
    try {
      const response = await api.post(`/keywords/research?seed_keyword=${seedKeyword}`);
      toast.success(`Found ${response.data.keywords.length} keywords!`);
      setSeedKeyword('');
      setIsResearchOpen(false);
      fetchKeywords();
    } catch (error) {
      toast.error('Research failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
      <aside className="fixed left-0 top-0 h-full w-64 glass p-6"><div className="flex items-center space-x-2 mb-8"><div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center text-white font-bold">RF</div><span className="text-xl font-bold">RankForge</span></div><nav className="space-y-2"><Link to="/dashboard" className="flex items-center space-x-3 px-4 py-3 rounded-xl hover:bg-slate-100 transition-colors"><LayoutDashboard className="w-5 h-5" /><span>Dashboard</span></Link><Link to="/sites" className="flex items-center space-x-3 px-4 py-3 rounded-xl hover:bg-slate-100 transition-colors"><Globe className="w-5 h-5" /><span>Sites</span></Link><Link to="/ai-agents" className="flex items-center space-x-3 px-4 py-3 rounded-xl hover:bg-slate-100 transition-colors"><Bot className="w-5 h-5" /><span>AI Agents</span></Link><Link to="/billing" className="flex items-center space-x-3 px-4 py-3 rounded-xl hover:bg-slate-100 transition-colors"><CreditCard className="w-5 h-5" /><span>Billing</span></Link></nav><div className="absolute bottom-6 left-6 right-6"><div className="card p-4 mb-4"><div className="text-sm text-slate-600 mb-1">Credits</div><div className="text-2xl font-bold">{user?.credits || 0}</div></div><Button variant="outline" className="w-full" onClick={logout}><LogOut className="w-4 h-4 mr-2" />Logout</Button></div></aside>
      <main className="ml-64 p-8"><div className="max-w-7xl mx-auto"><div className="flex items-center justify-between mb-8"><div><h1 className="text-3xl font-bold mb-2">Keyword Research</h1><p className="text-slate-600">Discover and track profitable keywords</p></div><Dialog open={isResearchOpen} onOpenChange={setIsResearchOpen}><DialogTrigger asChild><Button data-testid="research-keywords-btn"><Search className="w-4 h-4 mr-2" />Research Keywords</Button></DialogTrigger><DialogContent><DialogHeader><DialogTitle>Keyword Research</DialogTitle></DialogHeader><form onSubmit={researchKeywords} className="space-y-4"><div><Input placeholder="Enter seed keyword" value={seedKeyword} onChange={(e) => setSeedKeyword(e.target.value)} required data-testid="seed-keyword-input" /></div><Button type="submit" className="w-full" disabled={loading} data-testid="research-submit-btn">{loading ? 'Researching...' : 'Research Keywords'}</Button></form></DialogContent></Dialog></div><div className="card"><div className="overflow-x-auto"><table className="w-full"><thead><tr className="border-b"><th className="text-left py-3 px-4">Keyword</th><th className="text-left py-3 px-4">Search Volume</th><th className="text-left py-3 px-4">Difficulty</th><th className="text-left py-3 px-4">Intent</th></tr></thead><tbody>{keywords.map((kw) => (<tr key={kw.keyword_id} className="border-b hover:bg-slate-50" data-testid={`keyword-row-${kw.keyword_id}`}><td className="py-3 px-4 font-medium">{kw.keyword}</td><td className="py-3 px-4">{kw.search_volume || 'N/A'}</td><td className="py-3 px-4"><span className={`px-2 py-1 rounded text-xs ${(kw.difficulty || 0) > 70 ? 'bg-red-100 text-red-700' : (kw.difficulty || 0) > 40 ? 'bg-amber-100 text-amber-700' : 'bg-green-100 text-green-700'}`}>{kw.difficulty || 'N/A'}</span></td><td className="py-3 px-4"><span className="text-sm text-slate-600">{kw.intent || 'Unknown'}</span></td></tr>))}</tbody></table></div></div></div></main>
    </div>
  );
}
