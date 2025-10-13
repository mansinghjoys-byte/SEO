import React, { useState, useEffect } from 'react';
import api from '../../utils/api';
import { toast } from 'sonner';

const UsersManagement = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedUser, setSelectedUser] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [creditAction, setCreditAction] = useState({ credits: 0, action: 'add' });

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const token = localStorage.getItem('adminToken');
      const response = await api.get('/admin/users?limit=100', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUsers(response.data);
    } catch (error) {
      toast.error('Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleCreditsUpdate = async () => {
    try {
      const token = localStorage.getItem('adminToken');
      await api.put(`/admin/users/${selectedUser.user_id}/credits`, creditAction, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Credits updated successfully');
      setShowModal(false);
      loadUsers();
    } catch (error) {
      toast.error('Failed to update credits');
    }
  };

  const handlePlanUpdate = async (userId, newPlan) => {
    try {
      const token = localStorage.getItem('adminToken');
      await api.put(`/admin/users/${userId}/plan?plan=${newPlan}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Plan updated successfully');
      loadUsers();
    } catch (error) {
      toast.error('Failed to update plan');
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!window.confirm('Are you sure? This will delete the user and ALL their data!')) return;
    
    try {
      const token = localStorage.getItem('adminToken');
      await api.delete(`/admin/users/${userId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('User deleted successfully');
      loadUsers();
    } catch (error) {
      toast.error('Failed to delete user');
    }
  };

  if (loading) {
    return <div className="text-white text-center py-8">Loading users...</div>;
  }

  return (
    <div className="text-white">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">User Management</h2>
        <div className="text-slate-300">
          Total Users: <span className="font-bold text-white">{users.length}</span>
        </div>
      </div>

      <div className="bg-white/5 rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-white/5">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">User</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Plan</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Credits</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Sites</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Audits</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Joined</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/10">
              {users.map((user) => (
                <tr key={user.user_id} className="hover:bg-white/5 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="font-medium">{user.full_name}</div>
                      <div className="text-sm text-slate-400">{user.email}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <select
                      value={user.plan}
                      onChange={(e) => handlePlanUpdate(user.user_id, e.target.value)}
                      className="px-2 py-1 bg-white/5 border border-white/10 rounded text-sm"
                    >
                      <option value="free">Free</option>
                      <option value="starter">Starter</option>
                      <option value="growth">Growth</option>
                      <option value="professional">Professional</option>
                      <option value="agency">Agency</option>
                      <option value="enterprise">Enterprise</option>
                    </select>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <button
                      onClick={() => {
                        setSelectedUser(user);
                        setCreditAction({ credits: 0, action: 'add' });
                        setShowModal(true);
                      }}
                      className="text-purple-400 hover:text-purple-300 font-semibold"
                    >
                      {user.credits} 💳
                    </button>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-slate-300">{user.total_sites}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-slate-300">{user.total_audits}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                    {new Date(user.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <button
                      onClick={() => handleDeleteUser(user.user_id)}
                      className="text-red-400 hover:text-red-300 text-sm"
                      title="Delete User"
                    >
                      🗑️ Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Credits Modal */}
      {showModal && selectedUser && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-slate-800 rounded-xl p-6 max-w-md w-full">
            <h3 className="text-xl font-bold mb-4">Manage Credits</h3>
            <p className="text-slate-300 mb-4">
              User: <span className="font-semibold text-white">{selectedUser.full_name}</span>
              <br />
              Current Credits: <span className="font-semibold text-purple-400">{selectedUser.credits}</span>
            </p>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Action</label>
                <select
                  value={creditAction.action}
                  onChange={(e) => setCreditAction({...creditAction, action: e.target.value})}
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                >
                  <option value="add">Add Credits</option>
                  <option value="subtract">Subtract Credits</option>
                  <option value="set">Set Credits</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Amount</label>
                <input
                  type="number"
                  value={creditAction.credits}
                  onChange={(e) => setCreditAction({...creditAction, credits: parseInt(e.target.value) || 0})}
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                  placeholder="Enter amount"
                />
              </div>

              {creditAction.action !== 'set' && (
                <div className="bg-purple-600/20 border border-purple-500/30 rounded-lg p-3 text-sm">
                  New Balance: <span className="font-bold">
                    {creditAction.action === 'add'
                      ? selectedUser.credits + (creditAction.credits || 0)
                      : Math.max(0, selectedUser.credits - (creditAction.credits || 0))}
                  </span>
                </div>
              )}
            </div>

            <div className="flex justify-end space-x-4 mt-6">
              <button
                onClick={() => setShowModal(false)}
                className="px-6 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={handleCreditsUpdate}
                className="px-6 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg font-semibold"
              >
                Update Credits
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UsersManagement;