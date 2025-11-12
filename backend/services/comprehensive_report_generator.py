"""
Comprehensive SEO Report Generator
Generates detailed, downloadable SEO audit reports in PDF and DOCX formats
Similar to professional SEO audit reports with all sections and recommendations
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from io import BytesIO
import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from core.database import get_database
from services.seo_audit import SEOAuditService
from services.advanced_crawler import AdvancedSEOCrawler
from groq import AsyncGroq
from core.config import get_settings

settings = get_settings()


class ComprehensiveReportGenerator:
    """Generate detailed SEO audit reports with all findings and recommendations"""
    
    def __init__(self):
        self.groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)
    
    async def generate_report_data(self, site_id: str, user_id: str) -> Dict[str, Any]:
        """
        Collect all data needed for comprehensive report
        """
        db = await get_database()
        
        # Get site info
        site = await db.sites.find_one({'site_id': site_id, 'user_id': user_id}, {'_id': 0})
        if not site:
            raise ValueError("Site not found")
        
        # Get latest audit
        latest_audit = await db.audits.find_one(
            {'site_id': site_id, 'user_id': user_id},
            {'_id': 0}
        ).sort('created_at', -1)
        
        # Get deep analysis if available
        deep_analysis = await db.deep_analyses.find_one(
            {'site_id': site_id, 'user_id': user_id},
            {'_id': 0}
        ).sort('created_at', -1)
        
        # Get LLM visibility data
        llm_visibility = await db.llm_visibility_checks.find_one(
            {'site_id': site_id, 'user_id': user_id},
            {'_id': 0}
        ).sort('created_at', -1)
        
        # Get recommendations
        recommendations = await db.recommendations.find_one(
            {'site_id': site_id, 'user_id': user_id},
            {'_id': 0}
        ).sort('created_at', -1)
        
        # Get competitor data
        competitor_discovery = await db.competitor_analyses.find_one(
            {'site_id': site_id, 'user_id': user_id, 'analysis_type': 'discovery'},
            {'_id': 0}
        ).sort('created_at', -1)
        
        # Get backlink data
        backlink_analysis = await db.backlink_analyses.find_one(
            {'site_id': site_id, 'user_id': user_id},
            {'_id': 0}
        ).sort('created_at', -1)
        
        # Get content intelligence
        content_gaps = await db.content_analyses.find_one(
            {'site_id': site_id, 'user_id': user_id, 'analysis_type': 'gap_analysis'},
            {'_id': 0}
        ).sort('created_at', -1)
        
        # Compile comprehensive report data
        report_data = {
            'site': site,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'audit': latest_audit,
            'deep_analysis': deep_analysis,
            'llm_visibility': llm_visibility,
            'recommendations': recommendations,
            'competitors': competitor_discovery,
            'backlinks': backlink_analysis,
            'content_gaps': content_gaps,
        }
        
        return report_data
    
    async def generate_docx_report(self, report_data: Dict[str, Any]) -> BytesIO:
        """
        Generate comprehensive DOCX report similar to SAPRO sample
        """
        doc = Document()
        
        # Set document properties
        site_url = report_data['site']['url']
        site_name = site_url.replace('https://', '').replace('http://', '').replace('www.', '')
        
        # Title
        title = doc.add_heading(f'SEO Audit – {site_name}', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        subtitle = doc.add_heading('Website Issues & SEO Recommendations', level=2)
        subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_paragraph(f'Generated on: {report_data["generated_at"]}')
        doc.add_paragraph(f'Website: {site_url}')
        doc.add_paragraph()
        
        # Executive Summary
        doc.add_heading('Executive Summary', 1)
        audit = report_data.get('audit', {})
        if audit:
            doc.add_paragraph(f'Overall SEO Score: {audit.get("seo_score", 0)}/100')
            doc.add_paragraph(f'Technical SEO Score: {audit.get("technical_score", 0)}/100')
            doc.add_paragraph(f'On-Page SEO Score: {audit.get("onpage_score", 0)}/100')
            doc.add_paragraph(f'Off-Page SEO Score: {audit.get("offpage_score", 0)}/100')
        doc.add_paragraph()
        
        # 1. TECHNICAL SEO SECTION
        doc.add_heading('Technical SEO', 1)
        
        if audit and audit.get('issues'):
            technical_issues = [issue for issue in audit['issues'] if issue.get('category') == 'technical']
            
            issue_count = 1
            for issue in technical_issues:
                doc.add_heading(f"{issue_count}. {issue.get('title')}", level=2)
                
                # Importance
                p = doc.add_paragraph()
                runner = p.add_run('Importance: ')
                runner.bold = True
                p.add_run(issue.get('description', ''))
                
                # Solution
                p = doc.add_paragraph()
                runner = p.add_run('Solution: ')
                runner.bold = True
                p.add_run(issue.get('fix', ''))
                
                doc.add_paragraph()
                issue_count += 1
        
        # 2. CORE WEB VITALS & PERFORMANCE
        doc.add_heading('Core Web Vitals & Performance', 1)
        
        if audit and audit.get('crawl_data'):
            perf = audit['crawl_data'].get('performance', {})
            doc.add_heading('Insights (Desktop & Mobile)', level=2)
            
            if perf:
                doc.add_paragraph(f"• Desktop Performance: {perf.get('desktop_score', 'N/A')}")
                doc.add_paragraph(f"• Mobile Performance: {perf.get('mobile_score', 'N/A')}")
                doc.add_paragraph(f"• Load Time: {perf.get('load_time_seconds', 'N/A')} seconds")
                doc.add_paragraph(f"• Page Size: {perf.get('html_size_kb', 'N/A')} KB")
                
                # Recommendations
                p = doc.add_paragraph()
                runner = p.add_run('Action Priority: ')
                runner.bold = True
                doc.add_paragraph('• Fix caching and render blocking issues')
                doc.add_paragraph('• Optimize image delivery')
                doc.add_paragraph('• Implement preload and font display optimizations')
                doc.add_paragraph('• Review and reduce legacy JS dependencies')
        
        doc.add_paragraph()
        
        # 3. ON-PAGE SEO
        doc.add_heading('On-Page SEO', 1)
        
        if audit and audit.get('issues'):
            onpage_issues = [issue for issue in audit['issues'] if issue.get('category') == 'on-page']
            
            issue_count = 1
            for issue in onpage_issues:
                doc.add_heading(f"{issue_count}. {issue.get('title')}", level=2)
                
                # Importance
                p = doc.add_paragraph()
                runner = p.add_run('Importance: ')
                runner.bold = True
                p.add_run(issue.get('description', ''))
                
                # Solution
                p = doc.add_paragraph()
                runner = p.add_run('Solution: ')
                runner.bold = True
                p.add_run(issue.get('fix', ''))
                
                doc.add_paragraph()
                issue_count += 1
        
        # 4. WEBSITE CONTENT ISSUES
        doc.add_heading('Website Content Issues', 1)
        
        content_gaps_data = report_data.get('content_gaps', {})
        if content_gaps_data:
            gaps = content_gaps_data.get('results', {}).get('gaps', [])
            if gaps:
                doc.add_heading('Content Gaps Identified:', level=2)
                for gap in gaps[:5]:  # Top 5 gaps
                    doc.add_paragraph(f"• {gap.get('topic', 'N/A')}", style='List Bullet')
                    doc.add_paragraph(f"  Priority: {gap.get('priority', 'N/A')}")
        else:
            doc.add_paragraph('Issue: Low word count on key pages')
            p = doc.add_paragraph()
            runner = p.add_run('Recommendation: ')
            runner.bold = True
            p.add_run('Expand page content to at least 800-1000 words with keyword-rich, value-driven copy.')
        
        doc.add_paragraph()
        
        # 5. OFF-PAGE SEO
        doc.add_heading('Off-Page SEO', 1)
        
        backlink_data = report_data.get('backlinks', {})
        if backlink_data:
            results = backlink_data.get('results', {})
            doc.add_heading('Backlink Analysis', level=2)
            
            summary = results.get('summary', {})
            doc.add_paragraph(f"• Total Backlinks Analyzed: {summary.get('total_opportunities', 0)}")
            doc.add_paragraph(f"• High Authority Sources: {summary.get('high_authority_count', 0)}")
            
            opportunities = results.get('opportunities', [])[:5]
            if opportunities:
                doc.add_heading('Top Backlink Opportunities:', level=3)
                for opp in opportunities:
                    doc.add_paragraph(f"• {opp.get('domain', 'N/A')} (Authority: {opp.get('authority_score', 'N/A')})")
        else:
            doc.add_heading('1. Low Domain Authority', level=2)
            p = doc.add_paragraph()
            runner = p.add_run('Solution: ')
            runner.bold = True
            p.add_run('Earn backlinks from high-authority, relevant domains through digital PR, guest posts, and content collaborations.')
            doc.add_paragraph()
            
            doc.add_heading('2. Focus on Quality Backlinks', level=2)
            p = doc.add_paragraph()
            runner = p.add_run('Solution: ')
            runner.bold = True
            p.add_run('Build content worth citing (whitepapers, insights, case studies). Target industry-relevant sites with higher domain authority.')
        
        doc.add_paragraph()
        
        # 6. GEO & AEO (LLM VISIBILITY)
        doc.add_heading('GEO & AEO (AI Search Optimization)', 1)
        
        llm_data = report_data.get('llm_visibility', {})
        if llm_data:
            results = llm_data.get('results', {})
            doc.add_heading('LLM Visibility Score', level=2)
            doc.add_paragraph(f"Overall Score: {results.get('overall_score', 0)}/100")
            
            visibility_by_llm = results.get('visibility_by_llm', [])
            if visibility_by_llm:
                doc.add_heading('Visibility by AI Platform:', level=3)
                for llm in visibility_by_llm:
                    doc.add_paragraph(f"• {llm.get('name', 'N/A')}: {llm.get('score', 0)}/100")
            
            recommendations_list = results.get('recommendations', [])
            if recommendations_list:
                doc.add_heading('Recommendations:', level=3)
                for rec in recommendations_list[:5]:
                    doc.add_paragraph(f"• {rec}", style='List Bullet')
        else:
            doc.add_heading('Issue: Pages not ranking on AI Overview', level=2)
            p = doc.add_paragraph()
            runner = p.add_run('Solution: ')
            runner.bold = True
            p.add_run('Optimize on-page content with clear topical focus, E-E-A-T signals, and conversational long-tail keywords. Strengthen internal linking and add structured data.')
            doc.add_paragraph()
            
            doc.add_heading('Issue: FAQs not used in content', level=2)
            p = doc.add_paragraph()
            runner = p.add_run('Solution: ')
            runner.bold = True
            p.add_run('Add structured FAQ sections using Schema markup on key service and "About" pages.')
        
        doc.add_paragraph()
        
        # 7. COMPETITOR ANALYSIS
        doc.add_heading('Competitor Analysis', 1)
        
        competitor_data = report_data.get('competitors', {})
        if competitor_data:
            results = competitor_data.get('results', {})
            competitors = results.get('competitors', [])[:5]  # Top 5 competitors
            
            if competitors:
                doc.add_heading('Top Competitors:', level=2)
                for comp in competitors:
                    doc.add_paragraph(f"• {comp.get('domain', 'N/A')} (Relevance: {comp.get('relevance_score', 0)}/100)")
                
                doc.add_paragraph()
                doc.add_heading('Competitive Insights:', level=2)
                doc.add_paragraph('Analyze competitor backlinks, content strategies, and social media presence to identify opportunities.')
        
        # 8. ACTIONABLE RECOMMENDATIONS
        doc.add_heading('Prioritized Action Plan', 1)
        
        recs_data = report_data.get('recommendations', {})
        if recs_data:
            results = recs_data.get('results', {})
            categories = results.get('by_category', {})
            
            for category, items in categories.items():
                if items:
                    cat_title = category.replace('_', ' ').title()
                    doc.add_heading(cat_title, level=2)
                    
                    for item in items[:3]:  # Top 3 per category
                        doc.add_paragraph(f"• {item.get('title', 'N/A')}", style='List Bullet')
                        if item.get('steps'):
                            for step in item.get('steps', [])[:3]:
                                doc.add_paragraph(f"  - {step}", style='List Number')
        else:
            doc.add_heading('High Priority Tasks:', level=2)
            doc.add_paragraph('1. Fix critical technical SEO issues (HTTPS, page speed, mobile responsiveness)')
            doc.add_paragraph('2. Optimize meta titles and descriptions for all pages')
            doc.add_paragraph('3. Create comprehensive content (800+ words) with proper heading structure')
            doc.add_paragraph('4. Build high-quality backlinks from relevant domains')
            doc.add_paragraph('5. Implement structured data (Schema.org) for rich snippets')
        
        doc.add_paragraph()
        
        # 9. ANALYTICS AND REPORTING
        doc.add_heading('Analytics and Reporting', 1)
        
        doc.add_heading('Issue: Setup and Verify Tracking', level=2)
        p = doc.add_paragraph()
        runner = p.add_run('Solution: ')
        runner.bold = True
        p.add_run('Implement and verify Google Tag Manager and GA4 setup sitewide. Request and verify Google Search Console access to monitor search visibility, fix crawl/index issues, and track keyword performance.')
        
        # Save to BytesIO
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        return buffer
    
    async def generate_pdf_report(self, report_data: Dict[str, Any]) -> BytesIO:
        """
        Generate comprehensive PDF report
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=8,
            spaceBefore=8,
            fontName='Helvetica-Bold'
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            spaceAfter=6,
            alignment=TA_JUSTIFY
        )
        
        # Build content
        story = []
        
        # Title
        site_url = report_data['site']['url']
        site_name = site_url.replace('https://', '').replace('http://', '').replace('www.', '')
        
        story.append(Paragraph(f'SEO Audit – {site_name}', title_style))
        story.append(Paragraph('Website Issues & SEO Recommendations', heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph(f'Generated on: {report_data["generated_at"]}', body_style))
        story.append(Paragraph(f'Website: {site_url}', body_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Executive Summary
        story.append(Paragraph('Executive Summary', heading_style))
        
        audit = report_data.get('audit', {})
        if audit:
            summary_data = [
                ['Metric', 'Score'],
                ['Overall SEO Score', f"{audit.get('seo_score', 0)}/100"],
                ['Technical SEO', f"{audit.get('technical_score', 0)}/100"],
                ['On-Page SEO', f"{audit.get('onpage_score', 0)}/100"],
                ['Off-Page SEO', f"{audit.get('offpage_score', 0)}/100"],
            ]
            
            t = Table(summary_data, colWidths=[3*inch, 2*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(t)
            story.append(Spacer(1, 0.3*inch))
        
        # Technical SEO Issues
        story.append(Paragraph('Technical SEO', heading_style))
        
        if audit and audit.get('issues'):
            technical_issues = [issue for issue in audit['issues'] if issue.get('category') == 'technical']
            
            for idx, issue in enumerate(technical_issues[:10], 1):
                story.append(Paragraph(f"{idx}. {issue.get('title')}", subheading_style))
                story.append(Paragraph(f"<b>Importance:</b> {issue.get('description', '')}", body_style))
                story.append(Paragraph(f"<b>Solution:</b> {issue.get('fix', '')}", body_style))
                story.append(Spacer(1, 0.1*inch))
        
        story.append(PageBreak())
        
        # On-Page SEO
        story.append(Paragraph('On-Page SEO', heading_style))
        
        if audit and audit.get('issues'):
            onpage_issues = [issue for issue in audit['issues'] if issue.get('category') == 'on-page']
            
            for idx, issue in enumerate(onpage_issues[:10], 1):
                story.append(Paragraph(f"{idx}. {issue.get('title')}", subheading_style))
                story.append(Paragraph(f"<b>Importance:</b> {issue.get('description', '')}", body_style))
                story.append(Paragraph(f"<b>Solution:</b> {issue.get('fix', '')}", body_style))
                story.append(Spacer(1, 0.1*inch))
        
        # LLM Visibility
        story.append(PageBreak())
        story.append(Paragraph('GEO & AEO (AI Search Optimization)', heading_style))
        
        llm_data = report_data.get('llm_visibility', {})
        if llm_data:
            results = llm_data.get('results', {})
            story.append(Paragraph(f"<b>Overall LLM Visibility Score:</b> {results.get('overall_score', 0)}/100", body_style))
            story.append(Spacer(1, 0.1*inch))
        
        # Recommendations
        story.append(Paragraph('Prioritized Action Plan', heading_style))
        
        recs_data = report_data.get('recommendations', {})
        if recs_data:
            results = recs_data.get('results', {})
            categories = results.get('by_category', {})
            
            for category, items in list(categories.items())[:3]:
                if items:
                    cat_title = category.replace('_', ' ').title()
                    story.append(Paragraph(cat_title, subheading_style))
                    
                    for item in items[:3]:
                        story.append(Paragraph(f"• {item.get('title', 'N/A')}", body_style))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer
