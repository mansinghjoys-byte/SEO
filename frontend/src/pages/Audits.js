import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { LayoutDashboard, Globe, Bot, CreditCard, LogOut, Search, CheckCircle, Target, ChevronDown, ChevronUp } from 'lucide-react';
import api from '../utils/api';
import { toast } from 'sonner';

export default function Audits() {
  const { siteId } = useParams();
  const { user, logout } = useAuth();
  const [site, setSite] = useState(null);
  const [audits, setAudits] = useState([]);
  const [currentAudit, setCurrentAudit] = useState(null);
  const [loading, setLoading] = useState(false);
  const [expandedIssue, setExpandedIssue] = useState(null);

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
      toast.success('✅ Audit completed! Check your detailed recommendations below.');
      setCurrentAudit(response.data);
      fetchSiteAndAudits();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Audit failed');
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      default:
        return 'bg-blue-100 text-blue-800 border-blue-300';
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical':
        return '🔴';
      case 'high':
        return '🟠';
      case 'medium':
        return '🟡';
      default:
        return '🔵';
    }
  };

  const prioritizedIssues = currentAudit?.issues ? [...currentAudit.issues].sort((a, b) => {
    const severityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
    return severityOrder[a.severity] - severityOrder[b.severity];
  }) : [];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
      {/* Sidebar */}
      <aside className="fixed left-0 top-0 h-full w-64 bg-white/80 backdrop-blur-xl border-r border-slate-200 p-6 z-40">
        <div className="flex items-center space-x-2 mb-8">
          <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center text-white font-bold">RF</div>
          <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">RankForge</span>
        </div>
        <nav className="space-y-2">
          <Link to="/dashboard" className="flex items-center space-x-3 px-4 py-3 rounded-xl hover:bg-slate-100 transition-colors text-slate-700 hover:text-blue-600">
            <LayoutDashboard className="w-5 h-5" />
            <span>Dashboard</span>
          </Link>
          <Link to="/sites" className="flex items-center space-x-3 px-4 py-3 rounded-xl bg-blue-50 text-blue-600 font-semibold">
            <Globe className="w-5 h-5" />
            <span>Sites & Audits</span>
          </Link>
          <Link to="/ai-agents" className="flex items-center space-x-3 px-4 py-3 rounded-xl hover:bg-slate-100 transition-colors text-slate-700 hover:text-blue-600">
            <Bot className="w-5 h-5" />
            <span>AI Agents</span>
          </Link>
          <Link to="/billing" className="flex items-center space-x-3 px-4 py-3 rounded-xl hover:bg-slate-100 transition-colors text-slate-700 hover:text-blue-600">
            <CreditCard className="w-5 h-5" />
            <span>Billing</span>
          </Link>
        </nav>
        <div className="absolute bottom-6 left-6 right-6">
          <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl p-4 mb-4 border border-blue-200">
            <div className="text-sm text-slate-600 mb-1">Available Credits</div>
            <div className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">{user?.credits || 0}</div>
            <div className="text-xs text-slate-500 mt-1">5 credits per audit</div>
          </div>
          <Button variant="outline" className="w-full" onClick={logout}>
            <LogOut className="w-4 h-4 mr-2" />
            Logout
          </Button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="ml-64 p-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                SEO Audit Results
              </h1>
              <div className="flex items-center space-x-2 text-slate-600">
                <Globe className="w-4 h-4" />
                <span className="font-medium">{site?.name}</span>
                <span className="text-slate-400">•</span>
                <span className="text-sm">{site?.url}</span>
              </div>
            </div>
            <Button 
              onClick={runAudit} 
              disabled={loading}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-6 py-6 text-lg"
              data-testid="run-audit-btn"
            >
              {loading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Analyzing...
                </>
              ) : (
                <>
                  Run New Audit <Search className="w-5 h-5 ml-2" />
                </>
              )}
            </Button>
          </div>

          {currentAudit ? (
            <div className="space-y-8">
              {/* Score Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <ScoreCard
                  title="Overall SEO Score"
                  score={currentAudit.seo_score}
                  icon="🎯"
                  gradient="from-blue-500 to-purple-500"
                />
                <ScoreCard
                  title="Technical SEO"
                  score={currentAudit.technical_score}
                  icon="⚙️"
                  gradient="from-green-500 to-teal-500"
                />
                <ScoreCard
                  title="On-Page SEO"
                  score={currentAudit.onpage_score}
                  icon="📄"
                  gradient="from-orange-500 to-red-500"
                />
                <ScoreCard
                  title="Off-Page SEO"
                  score={currentAudit.offpage_score}
                  icon="🔗"
                  gradient="from-purple-500 to-pink-500"
                />
              </div>

              {/* AI Recommendations Section */}
              <div className="bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 rounded-2xl p-8 border-2 border-blue-200 shadow-xl">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center text-2xl">
                    🤖
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-slate-800">AI-Powered Recommendations</h2>
                    <p className="text-slate-600">Step-by-step guide to improve your rankings</p>
                  </div>
                </div>
                
                <div className="bg-white rounded-xl p-6 shadow-lg">
                  {currentAudit.recommendations.map((rec, index) => (
                    <div key={index} className="prose prose-sm max-w-none">
                      <div className="whitespace-pre-wrap text-slate-700 leading-relaxed">
                        {rec}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Issues Section */}
              <div className="bg-white rounded-2xl p-8 shadow-lg border border-slate-200">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-slate-800">
                      Issues Found ({prioritizedIssues.length})
                    </h2>
                    <p className="text-slate-600 text-sm mt-1">
                      Click on any issue to see detailed fix instructions
                    </p>
                  </div>
                  <div className="flex items-center space-x-4 text-sm">
                    <div className="flex items-center space-x-2">
                      <span className="w-3 h-3 bg-red-500 rounded-full"></span>
                      <span>Critical: {prioritizedIssues.filter(i => i.severity === 'critical').length}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="w-3 h-3 bg-orange-500 rounded-full"></span>
                      <span>High: {prioritizedIssues.filter(i => i.severity === 'high').length}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="w-3 h-3 bg-yellow-500 rounded-full"></span>
                      <span>Medium: {prioritizedIssues.filter(i => i.severity === 'medium').length}</span>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  {prioritizedIssues.map((issue, index) => (
                    <div 
                      key={index} 
                      className={`border-2 rounded-xl overflow-hidden transition-all duration-300 ${
                        expandedIssue === index ? 'shadow-lg' : 'shadow-sm hover:shadow-md'
                      } ${getSeverityColor(issue.severity)}`}
                      data-testid={`issue-${index}`}
                    >
                      <div 
                        className="p-6 cursor-pointer"
                        onClick={() => setExpandedIssue(expandedIssue === index ? null : index)}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-3 mb-3">
                              <span className="text-2xl">{getSeverityIcon(issue.severity)}</span>
                              <span className={`text-xs font-bold px-3 py-1 rounded-full uppercase ${getSeverityColor(issue.severity)}`}>
                                {issue.severity} Priority
                              </span>
                              <span className="text-xs px-3 py-1 bg-slate-100 text-slate-600 rounded-full">
                                {issue.category}
                              </span>
                            </div>
                            <h3 className="text-xl font-bold text-slate-800 mb-2">
                              {issue.title}
                            </h3>
                            <p className="text-slate-700 leading-relaxed">
                              {issue.description}
                            </p>
                          </div>
                          <button className="ml-4 p-2 hover:bg-white rounded-lg transition-colors">
                            {expandedIssue === index ? (
                              <ChevronUp className="w-6 h-6 text-slate-600" />
                            ) : (
                              <ChevronDown className="w-6 h-6 text-slate-600" />
                            )}
                          </button>
                        </div>

                        {expandedIssue === index && (
                          <div className="mt-6 pt-6 border-t-2 border-current/20">
                            <div className="bg-white rounded-xl p-6 shadow-inner">
                              <div className="flex items-center space-x-2 mb-4">
                                <CheckCircle className="w-6 h-6 text-green-600" />
                                <h4 className="text-lg font-bold text-slate-800">How to Fix This:</h4>
                              </div>
                              <div className="prose prose-sm max-w-none">
                                <p className="text-slate-700 whitespace-pre-wrap leading-relaxed">
                                  {issue.fix}
                                </p>
                              </div>
                              
                              <div className="mt-6 flex items-center justify-between pt-4 border-t border-slate-200">
                                <div className="flex items-center space-x-4 text-sm text-slate-600">
                                  <div className="flex items-center space-x-2">
                                    <Target className="w-4 h-4" />
                                    <span>Impact: +{issue.impact_score} SEO points</span>
                                  </div>
                                </div>
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    navigator.clipboard.writeText(issue.fix);
                                    toast.success('Fix instructions copied!');
                                  }}
                                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors"
                                >
                                  📋 Copy Instructions
                                </button>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Past Audits */}
              {audits.length > 1 && (
                <div className="bg-white rounded-2xl p-8 shadow-lg border border-slate-200">
                  <h2 className="text-2xl font-bold text-slate-800 mb-6">Audit History</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {audits.slice(1, 7).map((audit, index) => (
                      <button
                        key={index}
                        onClick={() => setCurrentAudit(audit)}
                        className="p-4 border-2 border-slate-200 rounded-xl hover:border-blue-400 hover:shadow-md transition-all text-left"
                      >
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-2xl font-bold text-blue-600">{audit.seo_score}</span>
                          <span className="text-xs text-slate-500">
                            {new Date(audit.created_at).toLocaleDateString()}
                          </span>
                        </div>
                        <div className="text-sm text-slate-600">
                          {audit.issues.length} issues found
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-24 bg-white rounded-2xl shadow-lg">
              <div className="w-24 h-24 bg-gradient-to-br from-blue-100 to-purple-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <Search className="w-12 h-12 text-blue-600" />
              </div>
              <h2 className="text-2xl font-bold text-slate-800 mb-3">No Audits Yet</h2>
              <p className="text-slate-600 mb-8 max-w-md mx-auto">
                Run your first SEO audit to get detailed, beginner-friendly recommendations on how to improve your website's search rankings.
              </p>
              <Button 
                onClick={runAudit} 
                disabled={loading}
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-6 text-lg"
              >
                {loading ? 'Running Audit...' : '🚀 Run Your First Audit'}
              </Button>
              <p className="text-sm text-slate-500 mt-4">Costs 5 credits • Takes about 30 seconds</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

const ScoreCard = ({ title, score, icon, gradient }) => {
  const getScoreLabel = (score) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Needs Work';
    return 'Critical';
  };

  return (
    <div className={`bg-gradient-to-br ${gradient} rounded-2xl p-6 text-white shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1`}>
      <div className="flex items-center justify-between mb-4">
        <span className="text-3xl">{icon}</span>
        <span className="text-sm font-medium bg-white/20 px-3 py-1 rounded-full">
          {getScoreLabel(score)}
        </span>
      </div>
      <div className="text-sm font-medium mb-1 opacity-90">{title}</div>
      <div className="text-4xl font-bold mb-2">{score}<span className="text-2xl opacity-75">/100</span></div>
      <div className="w-full bg-white/20 rounded-full h-2 mt-3">
        <div 
          className="bg-white rounded-full h-2 transition-all duration-500"
          style={{ width: `${score}%` }}
        ></div>
      </div>
    </div>
  );
};
