import React, { useState, useEffect } from 'react';
import api from '../../utils/api';
import { toast } from 'sonner';

const SEOSettings = () => {
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    keywords: [],
    og_title: '',
    og_description: '',
    og_image: '',
    twitter_card: 'summary_large_image',
    twitter_title: '',
    twitter_description: '',
    twitter_image: '',
    canonical_url: '',
    robots: 'index, follow',
    json_ld: {}
  });
  const [keywordInput, setKeywordInput] = useState('');
  const [jsonLdInput, setJsonLdInput] = useState('');

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const token = localStorage.getItem('adminToken');
      const response = await api.get('/admin/seo-settings', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSettings(response.data);
      setFormData({
        title: response.data.title || '',
        description: response.data.description || '',
        keywords: response.data.keywords || [],
        og_title: response.data.og_title || '',
        og_description: response.data.og_description || '',
        og_image: response.data.og_image || '',
        twitter_card: response.data.twitter_card || 'summary_large_image',
        twitter_title: response.data.twitter_title || '',
        twitter_description: response.data.twitter_description || '',
        twitter_image: response.data.twitter_image || '',
        canonical_url: response.data.canonical_url || '',
        robots: response.data.robots || 'index, follow',
        json_ld: response.data.json_ld || {}
      });
      setJsonLdInput(JSON.stringify(response.data.json_ld || {}, null, 2));
    } catch (error) {
      toast.error('Failed to load SEO settings');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleAddKeyword = () => {
    if (keywordInput.trim() && !formData.keywords.includes(keywordInput.trim())) {
      setFormData({
        ...formData,
        keywords: [...formData.keywords, keywordInput.trim()]
      });
      setKeywordInput('');
    }
  };

  const handleRemoveKeyword = (keyword) => {
    setFormData({
      ...formData,
      keywords: formData.keywords.filter(k => k !== keyword)
    });
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const token = localStorage.getItem('adminToken');
      
      // Parse JSON-LD
      let jsonLd = {};
      if (jsonLdInput.trim()) {
        try {
          jsonLd = JSON.parse(jsonLdInput);
        } catch (e) {
          toast.error('Invalid JSON-LD format');
          setSaving(false);
          return;
        }
      }

      const updateData = {
        ...formData,
        json_ld: jsonLd
      };

      await api.put('/admin/seo-settings', updateData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      toast.success('SEO settings updated successfully!');
      loadSettings();
    } catch (error) {
      toast.error('Failed to update SEO settings');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="text-white text-center py-8">
        <div className="spinner mx-auto mb-4"></div>
        <p>Loading SEO settings...</p>
      </div>
    );
  }

  return (
    <div className="text-white space-y-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Global SEO Settings</h2>
        <button
          onClick={handleSave}
          disabled={saving}
          className="px-6 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-800 rounded-lg font-semibold transition-colors"
        >
          {saving ? 'Saving...' : 'Save Changes'}
        </button>
      </div>

      {/* Basic Meta Tags */}
      <div className="bg-white/5 rounded-lg p-6 space-y-4">
        <h3 className="text-xl font-semibold mb-4">Basic Meta Tags</h3>
        
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Title Tag (50-60 characters optimal)
          </label>
          <input
            type="text"
            name="title"
            value={formData.title}
            onChange={handleChange}
            className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
            placeholder="RankForge - AI-Powered SEO Platform"
          />
          <p className="text-xs text-slate-400 mt-1">{formData.title.length} characters</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Meta Description (150-160 characters optimal)
          </label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            rows={3}
            className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
            placeholder="Advanced AI-powered SEO analysis and optimization platform"
          />
          <p className="text-xs text-slate-400 mt-1">{formData.description.length} characters</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Keywords
          </label>
          <div className="flex space-x-2 mb-2">
            <input
              type="text"
              value={keywordInput}
              onChange={(e) => setKeywordInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddKeyword())}
              className="flex-1 px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Add keyword and press Enter"
            />
            <button
              onClick={handleAddKeyword}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg"
            >
              Add
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {formData.keywords.map((keyword, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-purple-600/30 rounded-full text-sm flex items-center space-x-2"
              >
                <span>{keyword}</span>
                <button
                  onClick={() => handleRemoveKeyword(keyword)}
                  className="text-red-400 hover:text-red-300"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Canonical URL
          </label>
          <input
            type="url"
            name="canonical_url"
            value={formData.canonical_url}
            onChange={handleChange}
            className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
            placeholder="https://rankforge.com"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Robots Meta Tag
          </label>
          <select
            name="robots"
            value={formData.robots}
            onChange={handleChange}
            className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="index, follow">index, follow</option>
            <option value="noindex, follow">noindex, follow</option>
            <option value="index, nofollow">index, nofollow</option>
            <option value="noindex, nofollow">noindex, nofollow</option>
          </select>
        </div>
      </div>

      {/* Open Graph Tags */}
      <div className="bg-white/5 rounded-lg p-6 space-y-4">
        <h3 className="text-xl font-semibold mb-4">Open Graph (Facebook/LinkedIn)</h3>
        
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            OG Title
          </label>
          <input
            type="text"
            name="og_title"
            value={formData.og_title}
            onChange={handleChange}
            className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
            placeholder="Leave empty to use main title"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            OG Description
          </label>
          <textarea
            name="og_description"
            value={formData.og_description}
            onChange={handleChange}
            rows={2}
            className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
            placeholder="Leave empty to use main description"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            OG Image URL (1200x630 recommended)
          </label>
          <input
            type="url"
            name="og_image"
            value={formData.og_image}
            onChange={handleChange}
            className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
            placeholder="https://example.com/og-image.jpg"
          />
        </div>
      </div>

      {/* Twitter Card Tags */}
      <div className="bg-white/5 rounded-lg p-6 space-y-4">
        <h3 className="text-xl font-semibold mb-4">Twitter Card</h3>
        
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Card Type
          </label>
          <select
            name="twitter_card"
            value={formData.twitter_card}
            onChange={handleChange}
            className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="summary">Summary</option>
            <option value="summary_large_image">Summary Large Image</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Twitter Title
          </label>
          <input
            type="text"
            name="twitter_title"
            value={formData.twitter_title}
            onChange={handleChange}
            className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
            placeholder="Leave empty to use OG title or main title"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Twitter Description
          </label>
          <textarea
            name="twitter_description"
            value={formData.twitter_description}
            onChange={handleChange}
            rows={2}
            className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
            placeholder="Leave empty to use OG description or main description"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Twitter Image URL
          </label>
          <input
            type="url"
            name="twitter_image"
            value={formData.twitter_image}
            onChange={handleChange}
            className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
            placeholder="Leave empty to use OG image"
          />
        </div>
      </div>

      {/* JSON-LD Structured Data */}
      <div className="bg-white/5 rounded-lg p-6 space-y-4">
        <h3 className="text-xl font-semibold mb-4">JSON-LD Structured Data</h3>
        <p className="text-sm text-slate-300 mb-2">
          Add structured data for rich snippets in search results
        </p>
        
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            JSON-LD Schema
          </label>
          <textarea
            value={jsonLdInput}
            onChange={(e) => setJsonLdInput(e.target.value)}
            rows={12}
            className="w-full px-4 py-2 bg-black/30 border border-white/10 rounded-lg text-white font-mono text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
            placeholder={`{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "RankForge",
  "description": "AI-Powered SEO Platform",
  "url": "https://rankforge.com"
}`}
          />
          <p className="text-xs text-slate-400 mt-1">
            Must be valid JSON format. Use schema.org types.
          </p>
        </div>
      </div>

      <div className="flex justify-end">
        <button
          onClick={handleSave}
          disabled={saving}
          className="px-8 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-800 rounded-lg font-semibold text-lg transition-colors"
        >
          {saving ? 'Saving Changes...' : 'Save All Settings'}
        </button>
      </div>
    </div>
  );
};

export default SEOSettings;
