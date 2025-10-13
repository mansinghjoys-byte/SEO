import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { LayoutDashboard, Globe, Bot, CreditCard, LogOut, Check, Crown, Zap } from 'lucide-react';
import api from '../utils/api';
import { toast } from 'sonner';

export default function Billing() {
  const { user, logout, updateUser } = useAuth();
  const [plans, setPlans] = useState({});
  const [transactions, setTransactions] = useState([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [plansRes, transactionsRes] = await Promise.all([
        api.get('/billing/plans'),
        api.get('/billing/transactions')
      ]);
      setPlans(plansRes.data.plans);
      setTransactions(transactionsRes.data.transactions);
    } catch (error) {
      toast.error('Failed to load billing data');
    }
  };

  const upgradePlan = async (planKey) => {
    try {
      const response = await api.post('/billing/upgrade', { plan: planKey });
      if (response.data.approve_url) {
        window.open(response.data.approve_url, '_blank');
        toast.success('Redirecting to PayPal...');
      } else {
        toast.success('Plan updated!');
        const userRes = await api.get('/auth/me');
        updateUser(userRes.data);
      }
    } catch (error) {
      toast.error('Failed to upgrade plan');
    }
  };

  const pricingData = [
    { key: 'free', name: 'Free', price: 0, color: 'slate' },
    { key: 'starter', name: 'Starter', price: 49, color: 'blue' },
    { key: 'growth', name: 'Growth', price: 79, color: 'purple' },
    { key: 'professional', name: 'Professional', price: 149, color: 'green' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
      <aside className="fixed left-0 top-0 h-full w-64 glass p-6"><div className="flex items-center space-x-2 mb-8"><div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center text-white font-bold">RF</div><span className="text-xl font-bold">RankForge</span></div><nav className="space-y-2"><Link to="/dashboard" className="flex items-center space-x-3 px-4 py-3 rounded-xl hover:bg-slate-100 transition-colors"><LayoutDashboard className="w-5 h-5" /><span>Dashboard</span></Link><Link to="/sites" className="flex items-center space-x-3 px-4 py-3 rounded-xl hover:bg-slate-100 transition-colors"><Globe className="w-5 h-5" /><span>Sites</span></Link><Link to="/ai-agents" className="flex items-center space-x-3 px-4 py-3 rounded-xl hover:bg-slate-100 transition-colors"><Bot className="w-5 h-5" /><span>AI Agents</span></Link><Link to="/billing" className="flex items-center space-x-3 px-4 py-3 rounded-xl bg-blue-50 text-blue-600 font-medium"><CreditCard className="w-5 h-5" /><span>Billing</span></Link></nav><div className="absolute bottom-6 left-6 right-6"><div className="card p-4 mb-4"><div className="text-sm text-slate-600 mb-1">Credits</div><div className="text-2xl font-bold">{user?.credits || 0}</div></div><Button variant="outline" className="w-full" onClick={logout}><LogOut className="w-4 h-4 mr-2" />Logout</Button></div></aside>
      <main className="ml-64 p-8"><div className="max-w-7xl mx-auto"><div className="mb-8"><h1 className="text-3xl font-bold mb-2">Billing & Plans</h1><p className="text-slate-600">Manage your subscription and credits</p></div><div className="card mb-8"><div className="flex items-center justify-between"><div><div className="text-sm text-slate-600 mb-1">Current Plan</div><div className="text-2xl font-bold capitalize">{user?.plan || 'Free'}</div></div><div><div className="text-sm text-slate-600 mb-1">Available Credits</div><div className="text-2xl font-bold text-blue-600">{user?.credits || 0}</div></div><div><Zap className="w-12 h-12 text-amber-500" /></div></div></div><div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">{pricingData.map((plan) => {const planInfo = plans[plan.key]; return planInfo ? (<div key={plan.key} className={`card ${user?.plan === plan.key ? 'ring-4 ring-blue-600' : ''}`} data-testid={`plan-${plan.key}`}><div className="mb-4"><h3 className="text-xl font-bold mb-2">{planInfo.name}</h3><div><span className="text-4xl font-bold">${planInfo.price}</span><span className="text-slate-600">/mo</span></div></div><div className="text-sm text-slate-600 mb-4">{planInfo.credits_per_month} credits/month</div><ul className="space-y-2 mb-6">{planInfo.features.map((feature, i) => (<li key={i} className="flex items-start text-sm"><Check className="w-4 h-4 text-green-600 mr-2 mt-0.5 flex-shrink-0" /><span>{feature}</span></li>))}</ul><Button className="w-full" variant={user?.plan === plan.key ? 'outline' : 'default'} onClick={() => upgradePlan(plan.key)} disabled={user?.plan === plan.key} data-testid={`upgrade-${plan.key}-btn`}>{user?.plan === plan.key ? 'Current Plan' : planInfo.price === 0 ? 'Downgrade' : 'Upgrade'}</Button></div>) : null;})}</div><div className="card"><h2 className="text-xl font-bold mb-4">Transaction History</h2><div className="overflow-x-auto"><table className="w-full"><thead><tr className="border-b"><th className="text-left py-3 px-4">Date</th><th className="text-left py-3 px-4">Description</th><th className="text-right py-3 px-4">Credits</th></tr></thead><tbody>{transactions.map((tx, index) => (<tr key={index} className="border-b hover:bg-slate-50"><td className="py-3 px-4">{new Date(tx.timestamp).toLocaleDateString()}</td><td className="py-3 px-4">{tx.description}</td><td className={`py-3 px-4 text-right font-semibold ${tx.amount > 0 ? 'text-green-600' : 'text-red-600'}`}>{tx.amount > 0 ? '+' : ''}{tx.amount}</td></tr>))}</tbody></table></div></div></div></main>
    </div>
  );
}
