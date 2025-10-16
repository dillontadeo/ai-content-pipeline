"""
Web dashboard for the AI Content Pipeline.
Provides a visual interface to view campaigns, trigger workflows, and analyze performance.
"""
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json

from config import Config
from src.data_storage import DataStorage
from src.performance_analyzer import PerformanceAnalyzer
from main import ContentPipeline


app = Flask(__name__)
CORS(app)
app.secret_key = Config.FLASK_SECRET_KEY

# Initialize components
storage = DataStorage(Config.DATABASE_PATH)
analyzer = PerformanceAnalyzer()
pipeline = None  # Will be initialized when needed


@app.route('/')
def index():
    """Dashboard home page."""
    return render_template('dashboard.html')


@app.route('/api/campaigns')
def get_campaigns():
    """Get all campaigns."""
    try:
        campaigns = storage.get_all_campaigns()
        return jsonify({
            'status': 'success',
            'campaigns': campaigns,
            'count': len(campaigns)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/campaign/<int:campaign_id>')
def get_campaign_details(campaign_id):
    """Get detailed campaign information."""
    try:
        # Get campaign performance
        performance = storage.get_campaign_performance(campaign_id)
        
        return jsonify({
            'status': 'success',
            'campaign_id': campaign_id,
            'performance': performance
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/content/<int:content_id>')
def get_content(content_id):
    """Get content and newsletters."""
    try:
        content = storage.get_content(content_id)
        newsletters = storage.get_newsletters_for_content(content_id)
        
        return jsonify({
            'status': 'success',
            'content': content,
            'newsletters': newsletters
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/analytics/overview')
def get_analytics_overview():
    """Get overall analytics overview."""
    try:
        # Get recent performance data
        historical = storage.get_historical_performance(limit=20)
        
        if not historical:
            return jsonify({
                'status': 'success',
                'message': 'No data available yet',
                'total_campaigns': 0
            })
        
        # Calculate aggregates
        total_campaigns = len(set(h['campaign_name'] for h in historical))
        avg_open_rate = sum(h['open_rate'] for h in historical) / len(historical)
        avg_click_rate = sum(h['click_rate'] for h in historical) / len(historical)
        
        # Performance by persona
        by_persona = {}
        for record in historical:
            persona = record['persona']
            if persona not in by_persona:
                by_persona[persona] = {
                    'count': 0,
                    'total_open_rate': 0,
                    'total_click_rate': 0
                }
            by_persona[persona]['count'] += 1
            by_persona[persona]['total_open_rate'] += record['open_rate']
            by_persona[persona]['total_click_rate'] += record['click_rate']
        
        # Calculate averages
        persona_stats = {}
        for persona, data in by_persona.items():
            persona_stats[persona] = {
                'campaigns': data['count'],
                'avg_open_rate': data['total_open_rate'] / data['count'],
                'avg_click_rate': data['total_click_rate'] / data['count']
            }
        
        return jsonify({
            'status': 'success',
            'total_campaigns': total_campaigns,
            'total_sends': sum(h['contacts_sent'] for h in historical),
            'avg_open_rate': avg_open_rate,
            'avg_click_rate': avg_click_rate,
            'by_persona': persona_stats,
            'recent_campaigns': historical[:5]
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/trends')
def get_trends():
    """Get performance trends."""
    try:
        historical = storage.get_historical_performance(limit=20)
        trends = analyzer.identify_trends(historical)
        
        return jsonify({
            'status': 'success',
            'trends': trends
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/pipeline/run', methods=['POST'])
def run_pipeline():
    """Trigger a new pipeline execution."""
    try:
        data = request.get_json()
        topic = data.get('topic')
        
        if not topic:
            return jsonify({
                'status': 'error',
                'message': 'Topic is required'
            }), 400
        
        # Initialize pipeline if needed
        global pipeline
        if pipeline is None:
            pipeline = ContentPipeline()
        
        # Run pipeline
        results = pipeline.run_full_pipeline(topic, test_mode=True)
        
        return jsonify({
            'status': 'success',
            'message': 'Pipeline executed successfully',
            'results': {
                'content_id': results['content']['content_id'],
                'blog_title': results['content']['blog']['title'],
                'campaigns_sent': len(results['distribution']['campaign_results']),
                'performance': results['performance']
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/pipeline/generate', methods=['POST'])
def generate_content():
    """Generate content without distribution."""
    try:
        data = request.get_json()
        topic = data.get('topic')
        
        if not topic:
            return jsonify({
                'status': 'error',
                'message': 'Topic is required'
            }), 400
        
        # Initialize pipeline if needed
        global pipeline
        if pipeline is None:
            pipeline = ContentPipeline()
        
        # Generate content only
        results = pipeline.generate_content_only(topic)
        
        return jsonify({
            'status': 'success',
            'message': 'Content generated successfully',
            'content_id': results['content_id'],
            'blog': results['blog'],
            'newsletters': {
                persona: {
                    'subject_line': newsletter['subject_line'],
                    'body_preview': newsletter['body'][:200] + '...',
                    'word_count': newsletter['word_count']
                }
                for persona, newsletter in results['newsletters'].items()
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })


def main():
    """Run the dashboard."""
    print(f"Starting dashboard on http://localhost:{Config.FLASK_PORT}")
    print(f"Database: {Config.DATABASE_PATH}")
    print(f"\nOpen your browser to: http://localhost:{Config.FLASK_PORT}")
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(
        host='0.0.0.0',
        port=Config.FLASK_PORT,
        debug=(Config.FLASK_ENV == 'development')
    )


if __name__ == '__main__':
    main()

