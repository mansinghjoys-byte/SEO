"""
Progress Tracking & Analytics Service
Tracks improvements over time and provides insights
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for tracking progress and analytics"""
    
    async def track_visibility_progress(
        self,
        site_id: str,
        current_data: Dict[str, Any],
        historical_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Track visibility score changes over time
        """
        try:
            current_score = current_data.get('overall_score', 0)
            
            # Calculate trends
            if historical_data:
                previous = historical_data[-1]
                previous_score = previous.get('overall_score', 0)
                change = current_score - previous_score
                
                # Calculate trend
                if len(historical_data) >= 3:
                    last_3_scores = [h.get('overall_score', 0) for h in historical_data[-3:]]
                    last_3_scores.append(current_score)
                    trend = self._calculate_trend(last_3_scores)
                else:
                    trend = 'insufficient_data'
            else:
                change = 0
                trend = 'baseline'
            
            return {
                'success': True,
                'current_score': current_score,
                'change': round(change, 1),
                'change_percentage': round((change / previous_score * 100) if historical_data and previous_score > 0 else 0, 1),
                'trend': trend,
                'historical_scores': [h.get('overall_score', 0) for h in historical_data[-10:]],
                'tracked_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f'Progress tracking error: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    def _calculate_trend(self, scores: List[float]) -> str:
        """Calculate trend from score history"""
        if len(scores) < 2:
            return 'insufficient_data'
        
        # Simple linear trend
        diffs = [scores[i] - scores[i-1] for i in range(1, len(scores))]
        avg_change = sum(diffs) / len(diffs)
        
        if avg_change > 2:
            return 'rapidly_improving'
        elif avg_change > 0.5:
            return 'improving'
        elif avg_change > -0.5:
            return 'stable'
        elif avg_change > -2:
            return 'declining'
        else:
            return 'rapidly_declining'
    
    async def generate_task_completion_report(
        self,
        site_id: str,
        tasks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate task completion statistics
        """
        try:
            total_tasks = len(tasks)
            completed = len([t for t in tasks if t.get('completed')])
            in_progress = len([t for t in tasks if t.get('status') == 'in_progress'])
            
            completion_rate = (completed / total_tasks * 100) if total_tasks > 0 else 0
            
            # Group by priority
            by_priority = {
                'critical': {'total': 0, 'completed': 0},
                'high': {'total': 0, 'completed': 0},
                'medium': {'total': 0, 'completed': 0},
                'low': {'total': 0, 'completed': 0}
            }
            
            for task in tasks:
                priority = task.get('priority', 'medium')
                if priority in by_priority:
                    by_priority[priority]['total'] += 1
                    if task.get('completed'):
                        by_priority[priority]['completed'] += 1
            
            return {
                'success': True,
                'total_tasks': total_tasks,
                'completed': completed,
                'in_progress': in_progress,
                'pending': total_tasks - completed - in_progress,
                'completion_rate': round(completion_rate, 1),
                'by_priority': by_priority,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f'Task report error: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    async def calculate_roi(
        self,
        tasks_completed: List[Dict[str, Any]],
        visibility_improvement: float,
        time_spent_hours: float
    ) -> Dict[str, Any]:
        """
        Calculate ROI for completed tasks
        """
        try:
            # Estimate impact
            total_impact = sum(self._parse_impact(t.get('impact', '')) for t in tasks_completed)
            
            roi_metrics = {
                'tasks_completed': len(tasks_completed),
                'time_invested_hours': time_spent_hours,
                'visibility_improvement': round(visibility_improvement, 1),
                'estimated_impact_points': round(total_impact, 1),
                'efficiency_score': round(total_impact / time_spent_hours, 2) if time_spent_hours > 0 else 0,
                'top_performers': sorted(
                    tasks_completed,
                    key=lambda t: self._parse_impact(t.get('impact', '')),
                    reverse=True
                )[:5]
            }
            
            return {
                'success': True,
                'roi': roi_metrics,
                'calculated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f'ROI calculation error: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    def _parse_impact(self, impact_str: str) -> float:
        """Parse impact string to numeric value"""
        # Extract number from strings like "+15 points" or "high"
        import re
        
        if not impact_str:
            return 0
        
        # Try to extract number
        numbers = re.findall(r'\d+', str(impact_str))
        if numbers:
            return float(numbers[0])
        
        # Map text to values
        impact_map = {
            'high': 15,
            'very_high': 20,
            'medium': 10,
            'low': 5
        }
        
        return impact_map.get(str(impact_str).lower(), 10)
    
    async def generate_weekly_report(
        self,
        site_id: str,
        week_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate weekly progress report
        """
        try:
            report = {
                'site_id': site_id,
                'week_ending': datetime.utcnow().isoformat(),
                'summary': {
                    'visibility_change': week_data.get('visibility_change', 0),
                    'tasks_completed': week_data.get('tasks_completed', 0),
                    'new_mentions': week_data.get('new_mentions', 0),
                    'content_published': week_data.get('content_published', 0)
                },
                'highlights': week_data.get('highlights', []),
                'next_week_focus': week_data.get('upcoming_priorities', []),
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return {
                'success': True,
                'report': report
            }
            
        except Exception as e:
            logger.error(f'Weekly report error: {str(e)}')
            return {'success': False, 'error': str(e)}
