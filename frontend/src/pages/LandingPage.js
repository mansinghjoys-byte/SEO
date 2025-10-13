import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Search, TrendingUp, Zap, BarChart3, Users, Shield, ArrowRight, Sparkles, CheckCircle2, Rocket } from 'lucide-react';
import { Button } from '../components/ui/button';

export default function LandingPage() {
  const [email, setEmail] = useState('');

  const features = [
    {
      icon: <Search className="w-12 h-12 text-blue-600" />,
      title: 'AI-Powered Site Audits',
      description: 'Comprehensive SEO analysis with actionable insights powered by advanced AI',
    },
    {
      icon: <TrendingUp className="w-12 h-12 text-purple-600" />,
      title: 'Keyword Research',
      description: 'Discover profitable keywords and track rankings in real-time',
    },
    {
      icon: <Zap className="w-12 h-12 text-amber-600" />,
      title: 'Automated Optimization',
      description: 'Fix SEO issues automatically and improve rankings faster',
    },
    {
      icon: <BarChart3 className="w-12 h-12 text-green-600" />,
      title: 'Advanced Analytics',
      description: 'Track performance, monitor competitors, and measure ROI',
    },
    {
      icon: <Sparkles className="w-12 h-12 text-pink-600" />,
      title: 'AI SEO Agents',
      description: 'Chat with specialized AI agents for personalized SEO guidance',
    },
    {
      icon: <Shield className="w-12 h-12 text-indigo-600" />,
      title: 'Enterprise Security',
      description: 'SOC 2 compliant with enterprise-grade security features',
    },
  ];

  const pricingPlans = [
    {
      name: 'Free',
      price: 0,
      credits: 20,
      features: ['1 website', 'Monthly audits', '10 keywords', 'Basic recommendations'],
      cta: 'Get Started',
      highlighted: false,
    },
    {
      name: 'Growth',
      price: 79,
      credits: 200,
      features: ['5 websites', 'Daily audits', '100 keywords', 'AI agents', 'Competitor tracking'],
      cta: 'Start Free Trial',
      highlighted: true,
    },
    {
      name: 'Professional',
      price: 149,
      credits: 500,
      features: ['10 websites', 'Real-time monitoring', '500 keywords', 'API access', 'Priority support'],
      cta: 'Contact Sales',
      highlighted: false,
    },
  ];

  return (
    <div className="min-h-screen">
      {/* Navigation */}
      <nav className="glass fixed top-0 left-0 right-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link to="/" className="flex items-center space-x-2">
              <Rocket className="w-8 h-8 text-blue-600" />
              <span className="text-2xl font-bold gradient-text">RankForge</span>
            </Link>
            <div className="flex space-x-4">
              <Link to="/login">
                <Button variant="ghost" data-testid="login-btn">Login</Button>
              </Link>
              <Link to="/register">
                <Button data-testid="register-btn" className="btn-primary">Get Started Free</Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center fade-in">
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold mb-6 leading-tight">
              Rank Higher with
              <span className="gradient-text block mt-2">AI-Powered SEO</span>
            </h1>
            <p className="text-xl text-slate-600 mb-8 max-w-3xl mx-auto">
              Transform your website's search rankings with intelligent SEO automation.
              Get actionable insights, fix issues automatically, and grow your organic traffic.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
              <Link to="/register">
                <Button size="lg" className="btn-primary text-lg px-8 py-6" data-testid="hero-cta-btn">
                  Start Free Trial <ArrowRight className="ml-2 w-5 h-5" />
                </Button>
              </Link>
              <Button size="lg" variant="outline" className="text-lg px-8 py-6" data-testid="demo-btn">
                Watch Demo
              </Button>
            </div>
            <div className="flex items-center justify-center space-x-8 text-sm text-slate-500">
              <div className="flex items-center">
                <CheckCircle2 className="w-5 h-5 text-green-600 mr-2" />
                <span>20 Free Credits</span>
              </div>
              <div className="flex items-center">
                <CheckCircle2 className="w-5 h-5 text-green-600 mr-2" />
                <span>No Credit Card</span>
              </div>
              <div className="flex items-center">
                <CheckCircle2 className="w-5 h-5 text-green-600 mr-2" />
                <span>Cancel Anytime</span>
              </div>
            </div>
          </div>

          {/* Hero Image/Dashboard Preview */}
          <div className="mt-20 scale-in">
            <div className="glass p-8 rounded-3xl shadow-2xl">
              <div className="aspect-video bg-gradient-to-br from-blue-100 to-purple-100 rounded-2xl flex items-center justify-center">
                <div className="text-center">
                  <BarChart3 className="w-24 h-24 text-blue-600 mx-auto mb-4 floating" />
                  <p className="text-lg text-slate-600">Dashboard Preview</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Powerful SEO Features</h2>
            <p className="text-xl text-slate-600 max-w-2xl mx-auto">
              Everything you need to dominate search rankings
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="card hover:scale-105 transition-transform duration-300"
                data-testid={`feature-card-${index}`}
              >
                <div className="mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                <p className="text-slate-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="glass p-16 rounded-3xl">
            <div className="grid md:grid-cols-4 gap-8 text-center">
              <div>
                <div className="text-5xl font-bold gradient-text mb-2">10K+</div>
                <div className="text-slate-600">Websites Optimized</div>
              </div>
              <div>
                <div className="text-5xl font-bold gradient-text mb-2">85%</div>
                <div className="text-slate-600">Ranking Improvement</div>
              </div>
              <div>
                <div className="text-5xl font-bold gradient-text mb-2">500K+</div>
                <div className="text-slate-600">Keywords Tracked</div>
              </div>
              <div>
                <div className="text-5xl font-bold gradient-text mb-2">24/7</div>
                <div className="text-slate-600">Monitoring</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-20 bg-white/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Simple, Transparent Pricing</h2>
            <p className="text-xl text-slate-600">Start free, scale as you grow</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {pricingPlans.map((plan, index) => (
              <div
                key={index}
                className={`card relative ${
                  plan.highlighted ? 'ring-4 ring-blue-600 scale-105 shadow-2xl' : ''
                }`}
                data-testid={`pricing-plan-${index}`}
              >
                {plan.highlighted && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-1 rounded-full text-sm font-semibold">
                      Most Popular
                    </span>
                  </div>
                )}
                <div className="text-center mb-6">
                  <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                  <div className="mb-2">
                    <span className="text-5xl font-bold">${plan.price}</span>
                    <span className="text-slate-600">/month</span>
                  </div>
                  <p className="text-sm text-slate-600">{plan.credits} credits/month</p>
                </div>
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="flex items-center text-slate-700">
                      <CheckCircle2 className="w-5 h-5 text-green-600 mr-3 flex-shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>
                <Link to="/register">
                  <Button
                    className={`w-full ${
                      plan.highlighted ? 'btn-primary' : ''
                    }`}
                    variant={plan.highlighted ? 'default' : 'outline'}
                    data-testid={`pricing-cta-${index}`}
                  >
                    {plan.cta}
                  </Button>
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="glass p-12 rounded-3xl text-center">
            <h2 className="text-4xl font-bold mb-4">Ready to Dominate Search Rankings?</h2>
            <p className="text-xl text-slate-600 mb-8">
              Join thousands of businesses growing their organic traffic with AI-powered SEO
            </p>
            <Link to="/register">
              <Button size="lg" className="btn-primary text-lg px-8 py-6" data-testid="footer-cta-btn">
                Start Your Free Trial <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Rocket className="w-8 h-8 text-blue-400" />
                <span className="text-2xl font-bold">RankForge</span>
              </div>
              <p className="text-slate-400">AI-powered SEO platform for modern businesses</p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-slate-400">
                <li><a href="#" className="hover:text-white">Features</a></li>
                <li><a href="#" className="hover:text-white">Pricing</a></li>
                <li><a href="#" className="hover:text-white">API</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-slate-400">
                <li><a href="#" className="hover:text-white">About</a></li>
                <li><a href="#" className="hover:text-white">Blog</a></li>
                <li><a href="#" className="hover:text-white">Careers</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Support</h4>
              <ul className="space-y-2 text-slate-400">
                <li><a href="#" className="hover:text-white">Help Center</a></li>
                <li><a href="#" className="hover:text-white">Contact</a></li>
                <li><a href="#" className="hover:text-white">Status</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-slate-800 mt-12 pt-8 text-center text-slate-400">
            <p>&copy; 2025 RankForge. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
