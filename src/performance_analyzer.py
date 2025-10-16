"""
Performance Analysis module for campaign metrics and AI-powered insights.
Analyzes engagement data and provides optimization recommendations.
"""
from openai import OpenAI
from typing import Dict, List
import json
from datetime import datetime
import random
from config import Config


class PerformanceAnalyzer:
    """Analyzes campaign performance and generates AI-powered insights."""
    
    def __init__(self, api_key: str = None, model: str = None):
        """Initialize the analyzer with OpenAI client."""
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.model = model or Config.OPENAI_MODEL
        self.client = OpenAI(api_key=self.api_key)
    
    def simulate_campaign_performance(self, campaign_id: str, 
                                     persona: str,
                                     contacts_sent: int) -> Dict:
        """
        Simulate realistic campaign performance metrics.
        Useful for testing and demos when real data isn't available.
        
        Args:
            campaign_id: Campaign identifier
            persona: Target persona (founders/creatives/operations)
            contacts_sent: Number of contacts the campaign was sent to
            
        Returns:
            Dictionary with performance metrics
        """
        # Different personas have different engagement patterns
        engagement_profiles = {
            'founders': {
                'open_rate': (0.22, 0.35),  # Higher open rates
                'click_rate': (0.08, 0.15),  # Good click-through
                'unsubscribe_rate': (0.002, 0.008)
            },
            'creatives': {
                'open_rate': (0.25, 0.40),  # Highest open rates
                'click_rate': (0.10, 0.18),  # Highest engagement
                'unsubscribe_rate': (0.001, 0.005)
            },
            'operations': {
                'open_rate': (0.18, 0.28),  # More selective
                'click_rate': (0.06, 0.12),  # Practical clickers
                'unsubscribe_rate': (0.003, 0.010)
            }
        }
        
        profile = engagement_profiles.get(persona, engagement_profiles['creatives'])
        
        # Generate realistic metrics with some randomness
        open_rate = random.uniform(*profile['open_rate'])
        click_rate = random.uniform(*profile['click_rate'])
        unsubscribe_rate = random.uniform(*profile['unsubscribe_rate'])
        
        opens = int(contacts_sent * open_rate)
        clicks = int(contacts_sent * click_rate)
        unsubscribes = int(contacts_sent * unsubscribe_rate)
        
        return {
            'campaign_id': campaign_id,
            'persona': persona,
            'contacts_sent': contacts_sent,
            'opens': opens,
            'clicks': clicks,
            'unsubscribes': unsubscribes,
            'open_rate': open_rate,
            'click_rate': click_rate,
            'unsubscribe_rate': unsubscribe_rate,
            'click_to_open_rate': clicks / opens if opens > 0 else 0,
            'recorded_at': datetime.now().isoformat()
        }
    
    def calculate_metrics(self, raw_data: Dict) -> Dict:
        """
        Calculate derived metrics from raw campaign data.
        
        Args:
            raw_data: Raw campaign data with counts
            
        Returns:
            Dictionary with calculated rates and metrics
        """
        sent = raw_data.get('sent', 0)
        opens = raw_data.get('opens', 0)
        clicks = raw_data.get('clicks', 0)
        bounces = raw_data.get('bounces', 0)
        unsubscribes = raw_data.get('unsubscribes', 0)
        
        # Calculate rates
        metrics = {
            'contacts_sent': sent,
            'opens': opens,
            'clicks': clicks,
            'bounces': bounces,
            'unsubscribes': unsubscribes,
            'open_rate': opens / sent if sent > 0 else 0,
            'click_rate': clicks / sent if sent > 0 else 0,
            'click_to_open_rate': clicks / opens if opens > 0 else 0,
            'bounce_rate': bounces / sent if sent > 0 else 0,
            'unsubscribe_rate': unsubscribes / sent if sent > 0 else 0,
            'engagement_score': self._calculate_engagement_score(
                opens, clicks, unsubscribes, sent
            )
        }
        
        return metrics
    
    def _calculate_engagement_score(self, opens: int, clicks: int, 
                                   unsubscribes: int, sent: int) -> float:
        """
        Calculate a composite engagement score (0-100).
        
        Formula weights:
        - Opens: 30%
        - Clicks: 50%
        - Unsubscribes: -20%
        """
        if sent == 0:
            return 0.0
        
        open_score = (opens / sent) * 30
        click_score = (clicks / sent) * 50
        unsub_penalty = (unsubscribes / sent) * 20
        
        score = max(0, min(100, (open_score + click_score - unsub_penalty) * 100))
        return round(score, 2)
    
    def generate_performance_insights(self, performance_data: List[Dict],
                                     campaign_context: Dict) -> Dict:
        """
        Generate AI-powered insights from campaign performance data.
        
        Args:
            performance_data: List of performance metrics by persona
            campaign_context: Context about the campaign (topic, title, etc.)
            
        Returns:
            Dictionary with insights and recommendations
        """
        # Prepare performance summary
        summary = self._format_performance_summary(performance_data)
        
        system_prompt = """You are a data analyst specializing in email marketing performance.
Analyze campaign metrics and provide actionable insights and recommendations.
Be specific, data-driven, and focus on concrete next steps."""
        
        user_prompt = f"""Analyze this email campaign performance:

Campaign: {campaign_context.get('title', 'Unknown')}
Topic: {campaign_context.get('topic', 'Unknown')}

Performance by Persona:
{summary}

Provide:
1. Key Insights: What patterns or standouts do you see?
2. Best Performing Segment: Which persona engaged most and why?
3. Improvement Opportunities: Where can we optimize?
4. Recommendations: 3-5 specific, actionable recommendations for future campaigns
5. Content Suggestions: What content angles or formats to try next?

Format as JSON with keys: "key_insights", "best_segment", "opportunities", "recommendations" (list), "content_suggestions" (list)
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        insights = json.loads(response.choices[0].message.content)
        
        # Add metadata
        insights['generated_at'] = datetime.now().isoformat()
        insights['campaign'] = campaign_context.get('title', 'Unknown')
        insights['analyzed_segments'] = len(performance_data)
        
        return insights
    
    def _format_performance_summary(self, performance_data: List[Dict]) -> str:
        """Format performance data into readable summary."""
        lines = []
        
        for data in performance_data:
            persona = data.get('persona', 'Unknown').upper()
            sent = data.get('contacts_sent', 0)
            open_rate = data.get('open_rate', 0) * 100
            click_rate = data.get('click_rate', 0) * 100
            unsub_rate = data.get('unsubscribe_rate', 0) * 100
            engagement = data.get('engagement_score', 0)
            
            lines.append(
                f"{persona}:\n"
                f"  Sent: {sent} | Opens: {open_rate:.1f}% | Clicks: {click_rate:.1f}% | "
                f"Unsubs: {unsub_rate:.2f}% | Engagement Score: {engagement:.1f}/100"
            )
        
        return "\n".join(lines)
    
    def compare_to_benchmarks(self, metrics: Dict) -> Dict:
        """
        Compare campaign metrics to industry benchmarks.
        
        Args:
            metrics: Campaign metrics
            
        Returns:
            Comparison analysis
        """
        # Industry benchmarks for B2B SaaS email marketing
        benchmarks = {
            'open_rate': 0.21,  # 21%
            'click_rate': 0.10,  # 10%
            'unsubscribe_rate': 0.005  # 0.5%
        }
        
        comparison = {
            'metrics': metrics,
            'benchmarks': benchmarks,
            'performance': {}
        }
        
        for metric, benchmark in benchmarks.items():
            actual = metrics.get(metric, 0)
            diff = actual - benchmark
            diff_percent = (diff / benchmark * 100) if benchmark > 0 else 0
            
            if diff > 0:
                status = 'above'
            elif diff < 0:
                status = 'below'
            else:
                status = 'at'
            
            comparison['performance'][metric] = {
                'actual': actual,
                'benchmark': benchmark,
                'difference': diff,
                'difference_percent': diff_percent,
                'status': status
            }
        
        return comparison
    
    def identify_trends(self, historical_data: List[Dict]) -> Dict:
        """
        Identify trends in historical campaign performance.
        
        Args:
            historical_data: List of historical performance records
            
        Returns:
            Trend analysis
        """
        if len(historical_data) < 2:
            return {
                'status': 'insufficient_data',
                'message': 'Need at least 2 campaigns for trend analysis'
            }
        
        # Group by persona
        by_persona = {}
        for data in historical_data:
            persona = data.get('persona', 'unknown')
            if persona not in by_persona:
                by_persona[persona] = []
            by_persona[persona].append(data)
        
        trends = {}
        
        for persona, records in by_persona.items():
            if len(records) < 2:
                continue
            
            # Calculate average metrics
            avg_open = sum(r.get('open_rate', 0) for r in records) / len(records)
            avg_click = sum(r.get('click_rate', 0) for r in records) / len(records)
            
            # Simple trend direction (comparing first half to second half)
            mid = len(records) // 2
            first_half_open = sum(r.get('open_rate', 0) for r in records[:mid]) / mid
            second_half_open = sum(r.get('open_rate', 0) for r in records[mid:]) / (len(records) - mid)
            
            first_half_click = sum(r.get('click_rate', 0) for r in records[:mid]) / mid
            second_half_click = sum(r.get('click_rate', 0) for r in records[mid:]) / (len(records) - mid)
            
            trends[persona] = {
                'campaigns_analyzed': len(records),
                'avg_open_rate': avg_open,
                'avg_click_rate': avg_click,
                'open_rate_trend': 'improving' if second_half_open > first_half_open else 'declining',
                'click_rate_trend': 'improving' if second_half_click > first_half_click else 'declining',
                'open_rate_change': second_half_open - first_half_open,
                'click_rate_change': second_half_click - first_half_click
            }
        
        return {
            'status': 'success',
            'personas_analyzed': len(trends),
            'trends': trends,
            'analyzed_at': datetime.now().isoformat()
        }
    
    def suggest_optimization(self, metrics: Dict, content_context: Dict) -> List[str]:
        """
        Suggest specific optimizations based on performance.
        
        Args:
            metrics: Performance metrics
            content_context: Context about the content
            
        Returns:
            List of optimization suggestions
        """
        suggestions = []
        
        open_rate = metrics.get('open_rate', 0)
        click_rate = metrics.get('click_rate', 0)
        cto_rate = metrics.get('click_to_open_rate', 0)
        
        # Subject line optimization
        if open_rate < 0.20:
            suggestions.append(
                "Subject Line: Open rate is below 20%. Try A/B testing subject lines with "
                "personalization, numbers, or urgency to improve opens."
            )
        
        # Content engagement optimization
        if click_rate < 0.08:
            suggestions.append(
                "Call-to-Action: Click rate is low. Strengthen your CTAs with action verbs, "
                "create urgency, and ensure links are prominent and compelling."
            )
        
        # Email design optimization
        if cto_rate < 0.30:
            suggestions.append(
                "Email Design: Click-to-open rate is under 30%. Improve email layout, "
                "use more visuals, and make CTAs more prominent."
            )
        
        # Timing optimization
        if open_rate > 0.25 and click_rate < 0.10:
            suggestions.append(
                "⏰ Send Time: Good opens but low clicks suggests timing issues. "
                "Test different send times (Tuesday-Thursday, 10am or 2pm often perform well)."
            )
        
        # Segmentation optimization
        if open_rate < 0.22:
            suggestions.append(
                "👥 Segmentation: Consider further segmenting your audience based on "
                "engagement history and interests for more personalized content."
            )
        
        # If performance is good
        if open_rate > 0.30 and click_rate > 0.12:
            suggestions.append(
                "✨ Strong Performance! Consider using this as a template for future campaigns. "
                "Document what worked well (timing, subject line, content angle)."
            )
        
        return suggestions if suggestions else [
            "Performance is within normal ranges. Continue monitoring and testing variations."
        ]
    
    def generate_performance_report(self, campaign_data: Dict,
                                   performance_by_persona: List[Dict],
                                   insights: Dict) -> str:
        """
        Generate a formatted performance report.
        
        Args:
            campaign_data: Campaign information
            performance_by_persona: Performance metrics for each persona
            insights: AI-generated insights
            
        Returns:
            Formatted report string
        """
        report_lines = [
            "=" * 70,
            "CAMPAIGN PERFORMANCE REPORT",
            "=" * 70,
            "",
            f"Campaign: {campaign_data.get('title', 'Unknown')}",
            f"Topic: {campaign_data.get('topic', 'Unknown')}",
            f"Send Date: {campaign_data.get('send_date', 'Unknown')}",
            "",
            "-" * 70,
            "PERFORMANCE BY PERSONA",
            "-" * 70,
            ""
        ]
        
        # Add performance data for each persona
        for perf in performance_by_persona:
            persona = perf.get('persona', 'Unknown').upper()
            report_lines.extend([
                f"{persona}:",
                f"   Contacts Sent: {perf.get('contacts_sent', 0)}",
                f"   Open Rate: {perf.get('open_rate', 0) * 100:.1f}%",
                f"   Click Rate: {perf.get('click_rate', 0) * 100:.1f}%",
                f"   Unsubscribe Rate: {perf.get('unsubscribe_rate', 0) * 100:.2f}%",
                f"   Engagement Score: {perf.get('engagement_score', 0):.1f}/100",
                ""
            ])
        
        # Add AI insights
        report_lines.extend([
            "-" * 70,
            "KEY INSIGHTS",
            "-" * 70,
            "",
            insights.get('key_insights', 'No insights available'),
            "",
            f"Best Performing Segment: {insights.get('best_segment', 'N/A')}",
            "",
            "Recommendations:",
        ])
        
        for i, rec in enumerate(insights.get('recommendations', []), 1):
            report_lines.append(f"{i}. {rec}")
        
        report_lines.extend([
            "",
            "=" * 70
        ])
        
        return "\n".join(report_lines)

