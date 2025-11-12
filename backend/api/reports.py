"""
API endpoints for comprehensive SEO report generation and download
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from core.dependencies import get_current_user
from core.database import get_database
from services.comprehensive_report_generator import ComprehensiveReportGenerator
from services.billing import CREDIT_COSTS
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix='/reports', tags=['Reports'])

# Report generation cost
REPORT_GENERATION_COST = 15  # 15 credits for comprehensive report


@router.post('/generate/{site_id}')
async def generate_comprehensive_report(
    site_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate comprehensive SEO report with all audit data
    Cost: 15 credits
    """
    db = await get_database()
    
    # Check credits
    if current_user['credits'] < REPORT_GENERATION_COST:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f'Insufficient credits. Report generation requires {REPORT_GENERATION_COST} credits.'
        )
    
    # Verify site ownership
    site = await db.sites.find_one({'site_id': site_id, 'user_id': current_user['user_id']}, {'_id': 0})
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Site not found'
        )
    
    # Check if site has audit data
    audit = await db.audits.find_one({'site_id': site_id, 'user_id': current_user['user_id']}, {'_id': 0})
    if not audit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='No audit data found. Please run an SEO audit first.'
        )
    
    try:
        # Generate report data
        generator = ComprehensiveReportGenerator()
        report_data = await generator.generate_report_data(site_id, current_user['user_id'])
        
        # Store report metadata
        report_id = str(uuid.uuid4())
        report_doc = {
            'report_id': report_id,
            'site_id': site_id,
            'user_id': current_user['user_id'],
            'report_type': 'comprehensive_seo_audit',
            'status': 'completed',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'site_url': site['url'],
            'seo_score': audit.get('seo_score', 0)
        }
        
        await db.reports.insert_one(report_doc)
        
        # Deduct credits
        await db.users.update_one(
            {'user_id': current_user['user_id']},
            {'$inc': {'credits': -REPORT_GENERATION_COST}}
        )
        
        # Log transaction
        await db.credit_transactions.insert_one({
            'user_id': current_user['user_id'],
            'amount': -REPORT_GENERATION_COST,
            'type': 'report_generation',
            'description': f'Comprehensive SEO report for {site["url"]}',
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
        return {
            'success': True,
            'report_id': report_id,
            'message': 'Report generated successfully',
            'credits_used': REPORT_GENERATION_COST,
            'download_urls': {
                'pdf': f'/api/reports/download/{report_id}/pdf',
                'docx': f'/api/reports/download/{report_id}/docx'
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Report generation failed: {str(e)}'
        )


@router.get('/download/{report_id}/pdf')
async def download_pdf_report(
    report_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Download comprehensive SEO report as PDF
    """
    db = await get_database()
    
    # Verify report ownership
    report = await db.reports.find_one({
        'report_id': report_id,
        'user_id': current_user['user_id']
    }, {'_id': 0})
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Report not found'
        )
    
    try:
        # Generate report data
        generator = ComprehensiveReportGenerator()
        report_data = await generator.generate_report_data(
            report['site_id'],
            current_user['user_id']
        )
        
        # Generate PDF
        pdf_buffer = await generator.generate_pdf_report(report_data)
        
        # Create filename
        site_name = report['site_url'].replace('https://', '').replace('http://', '').replace('www.', '').replace('/', '_')
        filename = f"SEO_Audit_{site_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        return StreamingResponse(
            pdf_buffer,
            media_type='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'PDF generation failed: {str(e)}'
        )


@router.get('/download/{report_id}/docx')
async def download_docx_report(
    report_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Download comprehensive SEO report as DOCX
    """
    db = await get_database()
    
    # Verify report ownership
    report = await db.reports.find_one({
        'report_id': report_id,
        'user_id': current_user['user_id']
    }, {'_id': 0})
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Report not found'
        )
    
    try:
        # Generate report data
        generator = ComprehensiveReportGenerator()
        report_data = await generator.generate_report_data(
            report['site_id'],
            current_user['user_id']
        )
        
        # Generate DOCX
        docx_buffer = await generator.generate_docx_report(report_data)
        
        # Create filename
        site_name = report['site_url'].replace('https://', '').replace('http://', '').replace('www.', '').replace('/', '_')
        filename = f"SEO_Audit_{site_name}_{datetime.now().strftime('%Y%m%d')}.docx"
        
        return StreamingResponse(
            docx_buffer,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'DOCX generation failed: {str(e)}'
        )


@router.get('/history/{site_id}')
async def get_report_history(
    site_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all reports generated for a site
    """
    db = await get_database()
    
    # Verify site ownership
    site = await db.sites.find_one({'site_id': site_id, 'user_id': current_user['user_id']}, {'_id': 0})
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Site not found'
        )
    
    # Get all reports for this site
    reports = await db.reports.find(
        {'site_id': site_id, 'user_id': current_user['user_id']},
        {'_id': 0}
    ).sort('created_at', -1).to_list(50)
    
    return {
        'success': True,
        'site_url': site['url'],
        'total_reports': len(reports),
        'reports': reports
    }


@router.get('/all')
async def get_all_reports(current_user: dict = Depends(get_current_user)):
    """
    Get all reports for current user
    """
    db = await get_database()
    
    # Get all reports
    reports = await db.reports.find(
        {'user_id': current_user['user_id']},
        {'_id': 0}
    ).sort('created_at', -1).to_list(100)
    
    return {
        'success': True,
        'total_reports': len(reports),
        'reports': reports
    }
