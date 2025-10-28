import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { LayoutDashboard, Globe, Bot, CreditCard, LogOut, Plus, Send } from 'lucide-react';
import api from '../utils/api';
import { toast } from 'sonner';

export default function AIAgents() {
  const { user, logout } = useAuth();
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [sending, setSending] = useState(false);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [newAgentName, setNewAgentName] = useState('');
  const [newAgentPurpose, setNewAgentPurpose] = useState('audit_assistant');
  const [newAgentWebsite, setNewAgentWebsite] = useState('');
  const [sites, setSites] = useState([]);

  useEffect(() => {
    fetchAgents();
    fetchSites();
  }, []);

  const fetchSites = async () => {
    try {
      const response = await api.get('/sites');
      setSites(response.data);
    } catch (error) {
      console.error('Failed to load sites');
    }
  };

  const fetchAgents = async () => {
    try {
      const response = await api.get('/agents/');
      setAgents(response.data);
      if (response.data.length > 0 && !selectedAgent) {
        setSelectedAgent(response.data[0]);
        fetchHistory(response.data[0].agent_id);
      }
    } catch (error) {
      toast.error('Failed to load agents');
    }
  };

  const fetchHistory = async (agentId) => {
    try {
      const response = await api.get(`/agents/${agentId}/history`);
      setMessages(response.data.history);
    } catch (error) {
      console.error('Failed to load chat history');
    }
  };

  const createAgent = async (e) => {
    e.preventDefault();
    try {
      const response = await api.post('/agents/', {
        name: newAgentName,
        purpose: newAgentPurpose,
        website: newAgentWebsite || null,
        context: {}
      });
      toast.success('AI Agent created!');
      setNewAgentName('');
      setNewAgentWebsite('');
      setIsCreateOpen(false);
      fetchAgents();
    } catch (error) {
      toast.error('Failed to create agent');
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !selectedAgent) return;
    setSending(true);
    try {
      const response = await api.post('/agents/chat', {
        agent_id: selectedAgent.agent_id,
        message: newMessage
      });
      setMessages([...messages, 
        { user_message: newMessage, agent_response: response.data.message, timestamp: new Date().toISOString() }
      ]);
      setNewMessage('');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to send message');
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
      <aside className="fixed left-0 top-0 h-full w-64 glass p-6"><div className="flex items-center space-x-2 mb-8"><div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center text-white font-bold">RF</div><span className="text-xl font-bold">RankForge</span></div><nav className="space-y-2"><Link to="/dashboard" className="flex items-center space-x-3 px-4 py-3 rounded-xl hover:bg-slate-100 transition-colors"><LayoutDashboard className="w-5 h-5" /><span>Dashboard</span></Link><Link to="/sites" className="flex items-center space-x-3 px-4 py-3 rounded-xl hover:bg-slate-100 transition-colors"><Globe className="w-5 h-5" /><span>Sites</span></Link><Link to="/ai-agents" className="flex items-center space-x-3 px-4 py-3 rounded-xl bg-blue-50 text-blue-600 font-medium"><Bot className="w-5 h-5" /><span>AI Agents</span></Link><Link to="/billing" className="flex items-center space-x-3 px-4 py-3 rounded-xl hover:bg-slate-100 transition-colors"><CreditCard className="w-5 h-5" /><span>Billing</span></Link></nav><div className="absolute bottom-6 left-6 right-6"><div className="card p-4 mb-4"><div className="text-sm text-slate-600 mb-1">Credits</div><div className="text-2xl font-bold">{user?.credits || 0}</div></div><Button variant="outline" className="w-full" onClick={logout}><LogOut className="w-4 h-4 mr-2" />Logout</Button></div></aside>
      <main className="ml-64 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold mb-2">AI SEO Agents</h1>
              <p className="text-slate-600">Chat with specialized AI assistants</p>
            </div>
            <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
              <DialogTrigger asChild>
                <Button data-testid="create-agent-btn">
                  <Plus className="w-4 h-4 mr-2" />
                  Create Agent
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create AI Agent</DialogTitle>
                </DialogHeader>
                <form onSubmit={createAgent} className="space-y-4">
                  <div>
                    <label className="text-sm font-medium mb-1 block">Agent Name</label>
                    <Input 
                      placeholder="Agent name" 
                      value={newAgentName} 
                      onChange={(e) => setNewAgentName(e.target.value)} 
                      required 
                      data-testid="agent-name-input" 
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-1 block">Purpose</label>
                    <Select value={newAgentPurpose} onValueChange={setNewAgentPurpose}>
                      <SelectTrigger data-testid="agent-purpose-select">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="audit_assistant">SEO Audit Assistant</SelectItem>
                        <SelectItem value="keyword_researcher">Keyword Researcher</SelectItem>
                        <SelectItem value="content_optimizer">Content Optimizer</SelectItem>
                        <SelectItem value="competitor_analyst">Competitor Analyst</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-1 block">Website (Optional)</label>
                    <Select value={newAgentWebsite} onValueChange={setNewAgentWebsite}>
                      <SelectTrigger data-testid="agent-website-select">
                        <SelectValue placeholder="Select a website" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="">None (General Agent)</SelectItem>
                        {sites.map((site) => (
                          <SelectItem key={site.site_id} value={site.url}>
                            {site.url}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <p className="text-xs text-slate-500 mt-1">
                      Link agent to a specific website for context-aware assistance
                    </p>
                  </div>
                  <Button type="submit" className="w-full" data-testid="create-agent-submit-btn">
                    Create Agent
                  </Button>
                </form>
              </DialogContent>
            </Dialog>
          </div><div className="grid lg:grid-cols-4 gap-6"><div className="lg:col-span-1"><div className="card"><h2 className="font-bold mb-4">Your Agents</h2><div className="space-y-2">{agents.map((agent) => (<button key={agent.agent_id} onClick={() => { setSelectedAgent(agent); fetchHistory(agent.agent_id); }} className={`w-full text-left p-3 rounded-xl transition-colors ${selectedAgent?.agent_id === agent.agent_id ? 'bg-blue-50 text-blue-600' : 'hover:bg-slate-50'}`} data-testid={`agent-${agent.agent_id}`}><div className="font-semibold">{agent.name}</div><div className="text-xs text-slate-500">{agent.purpose.replace('_', ' ')}</div></button>))}</div></div></div><div className="lg:col-span-3"><div className="card h-[600px] flex flex-col">{selectedAgent ? (<><div className="border-b pb-4 mb-4"><h2 className="text-xl font-bold">{selectedAgent.name}</h2><p className="text-sm text-slate-600">{selectedAgent.purpose.replace('_', ' ')}</p></div><div className="flex-1 overflow-y-auto mb-4 space-y-4" data-testid="chat-messages">{messages.map((msg, index) => (<div key={index}><div className="flex justify-end mb-2"><div className="bg-blue-600 text-white p-3 rounded-2xl rounded-tr-sm max-w-md">{msg.user_message}</div></div><div className="flex justify-start"><div className="bg-slate-100 p-3 rounded-2xl rounded-tl-sm max-w-md"><div className="whitespace-pre-wrap">{msg.agent_response}</div></div></div></div>))}</div><form onSubmit={sendMessage} className="flex space-x-2"><Input placeholder="Type your message..." value={newMessage} onChange={(e) => setNewMessage(e.target.value)} disabled={sending} data-testid="chat-input" /><Button type="submit" disabled={sending} data-testid="send-message-btn"><Send className="w-4 h-4" /></Button></form></>) : (<div className="flex items-center justify-center h-full"><div className="text-center"><Bot className="w-16 h-16 text-slate-300 mx-auto mb-4" /><p className="text-slate-600">Select an agent to start chatting</p></div></div>)}</div></div></div></div></main>
    </div>
  );
}
