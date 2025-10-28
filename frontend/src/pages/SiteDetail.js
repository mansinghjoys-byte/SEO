import React, { useState, useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { LayoutDashboard, Globe, Bot, CreditCard, LogOut, ArrowLeft, ExternalLink, Link2, TrendingUp, Award } from 'lucide-react';
import api from '../utils/api';
import { toast } from 'sonner';

export default function SiteDetail() {
  const { siteId } = useParams();
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [site, setSite] = useState(null);
  const [loading, setLoading] = useState(true);
  const [backlinksData, setBacklinksData] = useState(null);
  const [scanningBacklinks, setScanningBacklinks] = useState(false);
  const [opportunities, setOpportunities] = useState([]);
  const [showOpportunities, setShowOpportunities] = useState(false);

  useEffect(() => {
    fetchSite();
    fetchLatestBacklinksScan();
  }, [siteId]);

  const fetchSite = async () => {
    try {
      const response = await api.get('/sites/');
      const foundSite = response.data.find(s => s.site_id === siteId);
      if (foundSite) {
        setSite(foundSite);
      } else {
        toast.error('Site not found');
        navigate('/sites');
      }
    } catch (error) {
      toast.error('Failed to load site');
      navigate('/sites');
    } finally {
      setLoading(false);
    }
  };

  const fetchLatestBacklinksScan = async () => {
    try {
      const response = await api.get(`/llm/backlinks/trusted-sources/${siteId}`);
      if (response.data.has_data) {
        setBacklinksData(response.data.scan.result);
      }
    } catch (error) {
      console.error('Failed to load backlinks scan');
    }
  };

  const scanTrustedBacklinks = async () => {
    setScanningBacklinks(true);
    try {
      const response = await api.post('/llm/backlinks/trusted-sources', {
        site_id: siteId,
        deep_scan: false
      });
      
      if (response.data.success) {
        setBacklinksData(response.data);
        toast.success('Trusted backlinks scan completed! (5 credits used)');
      } else {
        toast.error('Backlinks scan failed');
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to scan backlinks');
    } finally {
      setScanningBacklinks(false);
    }
  };

  const fetchOpportunities = async () => {
    try {
      const response = await api.get('/llm/backlinks/opportunities');
      setOpportunities(response.data.opportunities || []);
      setShowOpportunities(true);
    } catch (error) {
      toast.error('Failed to load opportunities');
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  if (!site) {
    return null;
  }

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
          <div className="card p-4 mb-4">
            <div className="text-sm text-slate-600 mb-1">Credits</div>
            <div className="text-2xl font-bold">{user?.credits || 0}</div>
          </div>
          <Button variant="outline" className="w-full" onClick={logout}>
            <LogOut className="w-4 h-4 mr-2" />Logout
          </Button>
        </div>
      </aside>

      <main className="ml-64 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8">
            <Button variant="ghost" onClick={() => navigate('/sites')} className="mb-4">
              <ArrowLeft className="w-4 h-4 mr-2" />Back to Sites
            </Button>
            <div className="flex items-start justify-between">
              <div>
                <h1 className="text-3xl font-bold mb-2">{site.name}</h1>
                <a href={site.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline flex items-center">
                  <span>{site.url}</span>
                  <ExternalLink className="w-4 h-4 ml-2" />
                </a>
              </div>
              {site.seo_score && (
                <div className="card p-6">
                  <div className="text-sm text-slate-600 mb-1">SEO Score</div>
                  <div className={`text-4xl font-bold ${site.seo_score >= 80 ? 'text-green-600' : site.seo_score >= 60 ? 'text-amber-600' : 'text-red-600'}`}>
                    {site.seo_score}/100
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Trusted Backlinks Section */}
          <div className="card mb-8">
            <div className="flex items-center justify-between mb-6">
              <div>
                <div className="flex items-center space-x-2 mb-2">
                  <Link2 className="w-6 h-6 text-blue-600" />
                  <h2 className="text-2xl font-bold">Trusted Backlinks</h2>
                </div>
                <p className="text-slate-600">Identify backlinks from high-authority trusted sources</p>
              </div>
              <div className="flex space-x-2">
                <Button 
                  onClick={scanTrustedBacklinks} 
                  disabled={scanningBacklinks}
                  className="bg-gradient-to-r from-blue-600 to-purple-600"
                >
                  {scanningBacklinks ? 'Scanning...' : 'Scan Backlinks (5 credits)'}
                </Button>
                <Button variant="outline" onClick={fetchOpportunities}>
                  View Opportunities
                </Button>
              </div>
            </div>

            {backlinksData ? (
              <div>
                {/* Summary Cards */}
                <div className="grid md:grid-cols-4 gap-4 mb-6">
                  <div className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl">
                    <div className="text-sm text-blue-600 mb-1">Total Backlinks</div>
                    <div className="text-3xl font-bold text-blue-700">
                      {backlinksData.summary?.total_trusted_backlinks || 0}
                    </div>
                  </div>
                  <div className="p-4 bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl">
                    <div className="text-sm text-purple-600 mb-1">Avg Authority</div>
                    <div className="text-3xl font-bold text-purple-700">
                      {backlinksData.summary?.average_authority?.toFixed(1) || 0}
                    </div>
                  </div>
                  <div className="p-4 bg-gradient-to-br from-green-50 to-green-100 rounded-xl">
                    <div className="text-sm text-green-600 mb-1">Categories</div>
                    <div className="text-3xl font-bold text-green-700">
                      {backlinksData.summary?.categories_represented || 0}
                    </div>
                  </div>
                  <div className="p-4 bg-gradient-to-br from-amber-50 to-amber-100 rounded-xl">
                    <div className="text-sm text-amber-600 mb-1">Top Source</div>
                    <div className="text-lg font-bold text-amber-700">
                      {backlinksData.summary?.highest_authority_source || 'N/A'}
                    </div>
                  </div>
                </div>

                {/* Backlinks List */}
                {backlinksData.backlinks && backlinksData.backlinks.length > 0 && (
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold mb-4">Found Backlinks</h3>
                    <div className="space-y-4">
                      {backlinksData.backlinks.map((backlink, index) => (
                        <div key={index} className="p-4 border border-slate-200 rounded-xl hover:border-blue-300 transition-colors">
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex items-center space-x-3">
                              <Award className="w-5 h-5 text-blue-600" />
                              <div>
                                <h4 className="font-semibold text-lg">{backlink.source}</h4>
                                <a href={backlink.source_url} target="_blank" rel="noopener noreferrer" className="text-sm text-blue-600 hover:underline flex items-center">
                                  {backlink.source_domain}
                                  <ExternalLink className="w-3 h-3 ml-1" />
                                </a>
                              </div>
                            </div>
                            <div className="flex items-center space-x-4">
                              <div className="text-center">
                                <div className="text-xs text-slate-500">Authority</div>
                                <div className="text-lg font-bold text-blue-600">{backlink.domain_authority}</div>
                              </div>
                              <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                                backlink.link_type === 'dofollow' ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-700'
                              }`}>
                                {backlink.link_type}
                              </span>
                              <span className="px-3 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-700">
                                {backlink.category}
                              </span>
                            </div>
                          </div>
                          <p className="text-sm text-slate-600 mb-2">{backlink.context}</p>
                          <div className="flex items-center space-x-4 text-xs text-slate-500">
                            <span>Anchor: <span className="font-medium">{backlink.anchor_text}</span></span>
                            <span>•</span>
                            <span>Traffic: ~{backlink.traffic_estimate?.toLocaleString()}/mo</span>
                            {backlink.engagement?.upvotes && (
                              <>
                                <span>•</span>
                                <span>👍 {backlink.engagement.upvotes}</span>
                              </>
                            )}
                            {backlink.engagement?.comments && (
                              <>
                                <span>•</span>
                                <span>💬 {backlink.engagement.comments}</span>
                              </>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Insights and Recommendations */}
                {backlinksData.insights && (
                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="p-4 bg-blue-50 rounded-xl">
                      <h3 className="font-semibold mb-3 text-blue-900">💪 Strengths</h3>
                      <ul className="space-y-2">
                        {backlinksData.insights.strengths?.map((strength, index) => (
                          <li key={index} className="text-sm text-blue-800 flex items-start">
                            <span className="mr-2">✓</span>
                            <span>{strength}</span>
                          </li>
                        ))}
                        {(!backlinksData.insights.strengths || backlinksData.insights.strengths.length === 0) && (
                          <li className="text-sm text-slate-600">No strengths identified yet</li>
                        )}
                      </ul>
                    </div>
                    <div className="p-4 bg-amber-50 rounded-xl">
                      <h3 className="font-semibold mb-3 text-amber-900">🎯 Opportunities</h3>
                      <ul className="space-y-2">
                        {backlinksData.insights.opportunities?.map((opportunity, index) => (
                          <li key={index} className="text-sm text-amber-800 flex items-start">
                            <span className="mr-2">→</span>
                            <span>{opportunity}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-12">
                <Link2 className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                <p className="text-slate-600 mb-4">No backlinks scan performed yet</p>
                <p className="text-sm text-slate-500">Click "Scan Backlinks" to identify trusted sources linking to your site</p>
              </div>
            )}
          </div>

          {/* Quick Actions */}
          <div className="grid md:grid-cols-3 gap-6">
            <Link to={`/audits/${siteId}`} className="card hover:shadow-lg transition-shadow">
              <TrendingUp className="w-8 h-8 text-blue-600 mb-3" />
              <h3 className="font-semibold mb-2">SEO Audits</h3>
              <p className="text-sm text-slate-600">View detailed SEO analysis</p>
            </Link>
            <Link to={`/keywords/${siteId}`} className="card hover:shadow-lg transition-shadow">
              <Globe className="w-8 h-8 text-purple-600 mb-3" />
              <h3 className="font-semibold mb-2">Keywords</h3>
              <p className="text-sm text-slate-600">Track keyword rankings</p>
            </Link>
            <div className="card hover:shadow-lg transition-shadow cursor-pointer" onClick={() => navigate('/ai-agents')}>
              <Bot className="w-8 h-8 text-green-600 mb-3" />
              <h3 className="font-semibold mb-2">AI Agent</h3>
              <p className="text-sm text-slate-600">Get AI-powered insights</p>
            </div>
          </div>
        </div>
      </main>

      {/* Opportunities Modal */}
      {showOpportunities && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onClick={() => setShowOpportunities(false)}>
          <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[80vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="p-6 border-b sticky top-0 bg-white">
              <h2 className="text-2xl font-bold">Backlink Opportunities</h2>
              <p className="text-slate-600">Trusted sources where you can earn backlinks</p>
            </div>
            <div className="p-6">
              <div className="grid gap-4">
                {opportunities.map((opp, index) => (
                  <div key={index} className="p-4 border border-slate-200 rounded-xl">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h3 className="font-semibold text-lg">{opp.source}</h3>
                        <a href={opp.url} target="_blank" rel="noopener noreferrer" className="text-sm text-blue-600 hover:underline">
                          {opp.domain}
                        </a>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
                          DA {opp.authority}
                        </span>
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                          opp.difficulty === 'easy' ? 'bg-green-100 text-green-700' :
                          opp.difficulty === 'medium' ? 'bg-amber-100 text-amber-700' :
                          'bg-red-100 text-red-700'
                        }`}>
                          {opp.difficulty}
                        </span>
                      </div>
                    </div>
                    <div className="mb-3">
                      <span className="text-xs text-slate-500">{opp.category}</span>
                      <span className="mx-2">•</span>
                      <span className="text-xs text-slate-500">Impact: {opp.potential_impact}</span>
                      <span className="mx-2">•</span>
                      <span className="text-xs text-slate-500">Time: {opp.estimated_time}</span>
                    </div>
                    <div>
                      <p className="text-sm font-medium mb-2">Action Steps:</p>
                      <ol className="text-sm text-slate-600 space-y-1 pl-4">
                        {opp.action_steps?.map((step, i) => (
                          <li key={i}>{i + 1}. {step}</li>
                        ))}
                      </ol>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="p-6 border-t bg-slate-50">
              <Button onClick={() => setShowOpportunities(false)} className="w-full">Close</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
