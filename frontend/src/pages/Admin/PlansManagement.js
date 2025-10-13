import React, { useState, useEffect } from 'react';
import api from '../../utils/api';
import { toast } from 'sonner';

const PlansManagement = () => {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingPlan, setEditingPlan] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    price: 0,
    credits: 0,
    max_sites: 0,
    max_keywords: 0,
    audit_frequency: 'monthly',
    ai_agents: false,
    priority_support: false,
    features: []
  });
  const [featureInput, setFeatureInput] = useState('');

  useEffect(() => {
    loadPlans();
  }, []);

  const loadPlans = async () => {
    try {
      const token = localStorage.getItem('adminToken');
      const response = await api.get('/admin/plans', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPlans(response.data);
    } catch (error) {
      toast.error('Failed to load plans');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingPlan(null);
    setFormData({
      name: '',
      price: 0,
      credits: 0,
      max_sites: 0,
      max_keywords: 0,
      audit_frequency: 'monthly',
      ai_agents: false,
      priority_support: false,
      features: []
    });
    setShowModal(true);
  };

  const handleEdit = (plan) => {
    setEditingPlan(plan);
    setFormData({
      name: plan.name,
      price: plan.price,
      credits: plan.credits,
      max_sites: plan.max_sites,
      max_keywords: plan.max_keywords,
      audit_frequency: plan.audit_frequency,
      ai_agents: plan.ai_agents,
      priority_support: plan.priority_support,
      features: plan.features
    });
    setShowModal(true);
  };

  const handleSave = async () => {
    try {
      const token = localStorage.getItem('adminToken');
      
      if (editingPlan) {
        await api.put(`/admin/plans/${editingPlan.plan_id}`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
        toast.success('Plan updated successfully');
      } else {
        await api.post('/admin/plans', formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
        toast.success('Plan created successfully');
      }
      
      setShowModal(false);
      loadPlans();
    } catch (error) {
      toast.error('Failed to save plan');
    }
  };

  const handleDelete = async (planId) => {
    if (!window.confirm('Are you sure you want to delete this plan?')) return;
    
    try {
      const token = localStorage.getItem('adminToken');
      await api.delete(`/admin/plans/${planId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Plan deleted successfully');
      loadPlans();
    } catch (error) {
      toast.error('Failed to delete plan');
    }
  };

  const addFeature = () => {
    if (featureInput.trim() && !formData.features.includes(featureInput.trim())) {
      setFormData({
        ...formData,
        features: [...formData.features, featureInput.trim()]
      });
      setFeatureInput('');
    }
  };

  const removeFeature = (feature) => {
    setFormData({
      ...formData,
      features: formData.features.filter(f => f !== feature)
    });
  };

  if (loading) {
    return <div className="text-white text-center py-8">Loading plans...</div>;
  }

  return (
    <div className="text-white">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Pricing Plans Management</h2>
        <button
          onClick={handleCreate}
          className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg font-semibold"
        >
          + Create New Plan
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {plans.map((plan) => (
          <div key={plan.plan_id} className="bg-white/5 rounded-lg p-6 border border-white/10">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-xl font-bold">{plan.name}</h3>
                <p className="text-3xl font-bold text-purple-400 mt-2">${plan.price}/mo</p>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => handleEdit(plan)}
                  className="p-2 bg-blue-600/20 hover:bg-blue-600/30 rounded"
                  title="Edit"
                >
                  ✏️
                </button>
                <button
                  onClick={() => handleDelete(plan.plan_id)}
                  className="p-2 bg-red-600/20 hover:bg-red-600/30 rounded"
                  title="Delete"
                >
                  🗑️
                </button>
              </div>
            </div>

            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-300">Credits:</span>
                <span className="font-semibold">{plan.credits}/month</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-300">Max Sites:</span>
                <span className="font-semibold">{plan.max_sites}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-300">Max Keywords:</span>
                <span className="font-semibold">{plan.max_keywords}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-300">Audit Frequency:</span>
                <span className="font-semibold capitalize">{plan.audit_frequency}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-300">AI Agents:</span>
                <span className="font-semibold">{plan.ai_agents ? '✓' : '✗'}</span>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-white/10">
              <p className="text-xs text-slate-400 mb-2">Features:</p>
              <ul className="text-sm space-y-1">
                {plan.features.slice(0, 3).map((feature, idx) => (
                  <li key={idx} className="text-slate-300">• {feature}</li>
                ))}
                {plan.features.length > 3 && (
                  <li className="text-slate-400">+ {plan.features.length - 3} more</li>
                )}
              </ul>
            </div>

            <div className="mt-4">
              <span className={`px-2 py-1 rounded text-xs ${plan.active ? 'bg-green-600/20 text-green-300' : 'bg-red-600/20 text-red-300'}`}>
                {plan.active ? 'Active' : 'Inactive'}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-slate-800 rounded-xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <h3 className="text-2xl font-bold mb-6">
              {editingPlan ? 'Edit Plan' : 'Create New Plan'}
            </h3>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Plan Name</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                    placeholder="Starter"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Price ($)</label>
                  <input
                    type="number"
                    value={formData.price}
                    onChange={(e) => setFormData({...formData, price: parseFloat(e.target.value)})}
                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Credits/Month</label>
                  <input
                    type="number"
                    value={formData.credits}
                    onChange={(e) => setFormData({...formData, credits: parseInt(e.target.value)})}
                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Max Sites</label>
                  <input
                    type="number"
                    value={formData.max_sites}
                    onChange={(e) => setFormData({...formData, max_sites: parseInt(e.target.value)})}
                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Max Keywords</label>
                  <input
                    type="number"
                    value={formData.max_keywords}
                    onChange={(e) => setFormData({...formData, max_keywords: parseInt(e.target.value)})}
                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Audit Frequency</label>
                <select
                  value={formData.audit_frequency}
                  onChange={(e) => setFormData({...formData, audit_frequency: e.target.value})}
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                >
                  <option value="monthly">Monthly</option>
                  <option value="weekly">Weekly</option>
                  <option value="daily">Daily</option>
                </select>
              </div>

              <div className="flex space-x-6">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={formData.ai_agents}
                    onChange={(e) => setFormData({...formData, ai_agents: e.target.checked})}
                    className="w-5 h-5 rounded"
                  />
                  <span>AI Agents Access</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={formData.priority_support}
                    onChange={(e) => setFormData({...formData, priority_support: e.target.checked})}
                    className="w-5 h-5 rounded"
                  />
                  <span>Priority Support</span>
                </label>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Features</label>
                <div className="flex space-x-2 mb-2">
                  <input
                    type="text"
                    value={featureInput}
                    onChange={(e) => setFeatureInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addFeature())}
                    className="flex-1 px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                    placeholder="Add feature"
                  />
                  <button onClick={addFeature} className="px-4 py-2 bg-purple-600 rounded-lg">Add</button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {formData.features.map((feature, idx) => (
                    <span key={idx} className="px-3 py-1 bg-purple-600/30 rounded-full text-sm flex items-center space-x-2">
                      <span>{feature}</span>
                      <button onClick={() => removeFeature(feature)} className="text-red-400">×</button>
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex justify-end space-x-4 mt-6">
              <button
                onClick={() => setShowModal(false)}
                className="px-6 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                className="px-6 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg font-semibold"
              >
                {editingPlan ? 'Update Plan' : 'Create Plan'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PlansManagement;