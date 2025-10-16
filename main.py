"""
Main pipeline orchestrator for the AI Content Pipeline.
Coordinates content generation, distribution, and performance analysis.
"""
import sys
from datetime import datetime
from typing import Dict, List
import json

from config import Config
from src.content_generator import ContentGenerator
from src.crm_integration import CRMIntegration
from src.performance_analyzer import PerformanceAnalyzer
from src.data_storage import DataStorage


class ContentPipeline:
    """Main pipeline orchestrator for automated content marketing."""
    
    def __init__(self):
        """Initialize all pipeline components."""
        print("Initializing AI Content Pipeline...")
        
        # Validate configuration
        try:
            Config.validate()
        except ValueError as e:
            print(f"Configuration Error: {e}")
            print("\nPlease copy .env.example to .env and add your API keys.")
            sys.exit(1)
        
        # Initialize modules
        self.content_gen = ContentGenerator()
        self.crm = CRMIntegration()
        self.analyzer = PerformanceAnalyzer()
        self.storage = DataStorage(Config.DATABASE_PATH)
        
        print("All systems initialized\n")
    
    def run_full_pipeline(self, topic: str, test_mode: bool = True) -> Dict:
        """
        Execute the complete pipeline from content generation to analysis.
        
        Args:
            topic: Blog post topic
            test_mode: If True, uses mock contacts; if False, uses real CRM data
            
        Returns:
            Dictionary with complete pipeline results
        """
        print("=" * 70)
        print(f"PIPELINE EXECUTION: {topic}")
        print("=" * 70)
        print()
        
        results = {
            'topic': topic,
            'started_at': datetime.now().isoformat(),
            'status': 'in_progress'
        }
        
        try:
            # Step 1: Generate Content
            print("STEP 1: Generating Content")
            print("-" * 70)
            content_results = self._generate_content(topic)
            results['content'] = content_results
            
            # Step 2: Distribute via CRM
            print("\nSTEP 2: Distributing Content")
            print("-" * 70)
            distribution_results = self._distribute_content(
                content_results, 
                test_mode
            )
            results['distribution'] = distribution_results
            
            # Step 3: Collect Performance Data
            print("\nSTEP 3: Collecting Performance Data")
            print("-" * 70)
            performance_results = self._collect_performance(
                distribution_results,
                content_results
            )
            results['performance'] = performance_results
            
            # Step 4: Generate Insights
            print("\nSTEP 4: Analyzing & Generating Insights")
            print("-" * 70)
            insights = self._generate_insights(
                performance_results,
                content_results
            )
            results['insights'] = insights
            
            # Mark as complete
            results['status'] = 'completed'
            results['completed_at'] = datetime.now().isoformat()
            
            # Print summary
            self._print_summary(results)
            
            return results
        
        except Exception as e:
            print(f"\nPipeline Error: {e}")
            results['status'] = 'error'
            results['error'] = str(e)
            return results
    
    def _generate_content(self, topic: str) -> Dict:
        """Generate blog post and newsletter variations."""
        print(f"Generating blog post about: {topic}")
        
        # Generate blog post
        blog = self.content_gen.generate_blog_post(topic)
        print(f"Blog post created: {blog['title']}")
        print(f"  Word count: {blog['word_count']}")
        
        # Save to database
        # Convert outline to string if it's not already
        outline_str = blog['outline'] if isinstance(blog['outline'], str) else str(blog['outline'])
        
        content_id = self.storage.save_content(
            topic=topic,
            blog_title=blog['title'],
            blog_content=blog['content'],
            blog_outline=outline_str,
            word_count=blog['word_count']
        )
        print(f"Saved to database (ID: {content_id})")
        
        # Generate newsletter variations
        print("\nGenerating personalized newsletters...")
        newsletters = self.content_gen.generate_newsletter_variations(
            blog_title=blog['title'],
            blog_content=blog['content']
        )
        
        newsletter_ids = {}
        for persona, newsletter in newsletters.items():
            newsletter_id = self.storage.save_newsletter(
                content_id=content_id,
                persona=persona,
                subject_line=newsletter['subject_line'],
                body=newsletter['body'],
                word_count=newsletter['word_count']
            )
            newsletter_ids[persona] = newsletter_id
            print(f"{Config.PERSONAS[persona]['name']}: \"{newsletter['subject_line']}\"")
        
        # Export to JSON
        json_path = f"data/content_{content_id}.json"
        self.storage.export_to_json(content_id, json_path)
        print(f"\nContent exported to: {json_path}")
        
        return {
            'content_id': content_id,
            'blog': blog,
            'newsletters': newsletters,
            'newsletter_ids': newsletter_ids
        }
    
    def _distribute_content(self, content_results: Dict, test_mode: bool) -> Dict:
        """Distribute newsletters to segmented audiences."""
        
        # Create or get test contacts
        if test_mode:
            print("Using test contacts (mock data)...")
            contacts = self._create_test_contacts()
        else:
            print("Using real CRM contacts...")
            # In production, would fetch from CRM
            contacts = []
        
        # Create campaign
        campaign_name = f"{content_results['blog']['title']} - {datetime.now().strftime('%Y-%m-%d')}"
        
        # Segment contacts by persona
        segmented = self.crm.segment_contacts_by_persona(contacts)
        
        campaign_results = {}
        campaign_ids = {}
        
        # Send to each persona segment
        for persona, persona_contacts in segmented.items():
            if not persona_contacts:
                print(f"No contacts for {persona}, skipping...")
                continue
            
            newsletter = content_results['newsletters'][persona]
            
            # Send campaign
            send_result = self.crm.send_email_to_contacts(
                contacts=persona_contacts,
                subject=newsletter['subject_line'],
                body=newsletter['body'],
                campaign_name=f"{campaign_name} - {persona}"
            )
            
            campaign_results[persona] = send_result
            
            # Save campaign to database
            campaign_id = self.storage.create_campaign(
                content_id=content_results['content_id'],
                campaign_name=f"{campaign_name} - {persona}",
                hubspot_campaign_id=send_result.get('campaign_id')
            )
            campaign_ids[persona] = campaign_id
            
            print(f"Sent to {len(persona_contacts)} {persona}: {send_result.get('campaign_id')}")
        
        return {
            'campaign_name': campaign_name,
            'campaign_results': campaign_results,
            'campaign_ids': campaign_ids,
            'contacts': contacts
        }
    
    def _collect_performance(self, distribution_results: Dict, 
                            content_results: Dict) -> Dict:
        """Collect and store performance metrics."""
        
        performance_data = {}
        
        for persona, campaign_result in distribution_results['campaign_results'].items():
            campaign_id_str = campaign_result.get('campaign_id')
            
            # Get analytics (simulated for demo)
            print(f"Collecting metrics for {persona}...")
            
            # Simulate performance data
            contacts_sent = campaign_result.get('contacts_sent', 0)
            simulated_perf = self.analyzer.simulate_campaign_performance(
                campaign_id=campaign_id_str,
                persona=persona,
                contacts_sent=contacts_sent
            )
            
            performance_data[persona] = simulated_perf
            
            # Save to database
            campaign_db_id = distribution_results['campaign_ids'][persona]
            self.storage.save_campaign_performance(
                campaign_id=campaign_db_id,
                persona=persona,
                metrics=simulated_perf
            )
            
            print(f"{persona}: Open Rate: {simulated_perf['open_rate']*100:.1f}%, "
                  f"Click Rate: {simulated_perf['click_rate']*100:.1f}%")
        
        return {
            'by_persona': performance_data,
            'collected_at': datetime.now().isoformat()
        }
    
    def _generate_insights(self, performance_results: Dict, 
                          content_results: Dict) -> Dict:
        """Generate AI-powered performance insights."""
        
        performance_list = list(performance_results['by_persona'].values())
        
        campaign_context = {
            'title': content_results['blog']['title'],
            'topic': content_results['blog'].get('topic', 'Unknown'),
            'word_count': content_results['blog']['word_count']
        }
        
        print("Generating AI-powered insights...")
        insights = self.analyzer.generate_performance_insights(
            performance_data=performance_list,
            campaign_context=campaign_context
        )
        
        # Save insights to database
        for persona, campaign_id in content_results.get('newsletter_ids', {}).items():
            # Ensure insight_text is a string
            insight_text = insights.get('key_insights', '')
            if isinstance(insight_text, list):
                insight_text = '\n'.join(str(item) for item in insight_text)
            elif not isinstance(insight_text, str):
                insight_text = str(insight_text)
            
            # Ensure recommendations is a JSON string
            recommendations = insights.get('recommendations', [])
            if not isinstance(recommendations, str):
                recommendations = json.dumps(recommendations)
            
            self.storage.save_insight(
                campaign_id=campaign_id,
                insight_text=insight_text,
                recommendations=recommendations
            )
        
        print(f"Insights generated")
        print(f"\nBest Performing Segment: {insights.get('best_segment', 'N/A')}")
        
        # Generate optimization suggestions
        for persona, perf in performance_results['by_persona'].items():
            suggestions = self.analyzer.suggest_optimization(
                metrics=perf,
                content_context=campaign_context
            )
            insights[f'{persona}_suggestions'] = suggestions
        
        return insights
    
    def _create_test_contacts(self) -> List[Dict]:
        """Create test contacts for demo purposes."""
        test_contacts = [
            # Founders
            {'email': 'john.founder@agency.com', 'first_name': 'John', 'last_name': 'Smith', 
             'persona': 'founders', 'company': 'Creative Agency Co'},
            {'email': 'sarah.ceo@studio.com', 'first_name': 'Sarah', 'last_name': 'Johnson',
             'persona': 'founders', 'company': 'Studio Labs'},
            {'email': 'mike.owner@design.com', 'first_name': 'Mike', 'last_name': 'Williams',
             'persona': 'founders', 'company': 'Design House'},
            
            # Creatives
            {'email': 'emma.designer@agency.com', 'first_name': 'Emma', 'last_name': 'Davis',
             'persona': 'creatives', 'company': 'Creative Agency Co'},
            {'email': 'alex.creative@studio.com', 'first_name': 'Alex', 'last_name': 'Brown',
             'persona': 'creatives', 'company': 'Studio Labs'},
            {'email': 'chris.artist@design.com', 'first_name': 'Chris', 'last_name': 'Martinez',
             'persona': 'creatives', 'company': 'Design House'},
            
            # Operations
            {'email': 'lisa.ops@agency.com', 'first_name': 'Lisa', 'last_name': 'Wilson',
             'persona': 'operations', 'company': 'Creative Agency Co'},
            {'email': 'david.manager@studio.com', 'first_name': 'David', 'last_name': 'Anderson',
             'persona': 'operations', 'company': 'Studio Labs'},
            {'email': 'jennifer.ops@design.com', 'first_name': 'Jennifer', 'last_name': 'Taylor',
             'persona': 'operations', 'company': 'Design House'},
        ]
        
        # Create contacts in CRM and database
        for contact in test_contacts:
            # Create in CRM
            crm_result = self.crm.create_or_update_contact(
                email=contact['email'],
                first_name=contact['first_name'],
                last_name=contact['last_name'],
                persona=contact['persona'],
                company=contact.get('company')
            )
            
            # Store in database
            self.storage.save_contact(
                email=contact['email'],
                first_name=contact['first_name'],
                last_name=contact['last_name'],
                persona=contact['persona'],
                company=contact.get('company'),
                hubspot_contact_id=crm_result.get('contact_id')
            )
            
            contact['contact_id'] = crm_result.get('contact_id')
        
        print(f"Created {len(test_contacts)} test contacts")
        
        return test_contacts
    
    def _print_summary(self, results: Dict):
        """Print a summary of pipeline execution."""
        print("\n" + "=" * 70)
        print("PIPELINE EXECUTION SUMMARY")
        print("=" * 70)
        print(f"\nStatus: {results['status'].upper()}")
        print(f"Blog: {results['content']['blog']['title']}")
        print(f"Campaigns Sent: {len(results['distribution']['campaign_results'])}")
        
        print("\nPerformance Overview:")
        for persona, perf in results['performance']['by_persona'].items():
            print(f"  {persona.capitalize():12} | "
                  f"Open: {perf['open_rate']*100:5.1f}% | "
                  f"Click: {perf['click_rate']*100:5.1f}% | "
                  f"Score: {perf.get('engagement_score', 0):5.1f}/100")
        
        print(f"\nTop Recommendation:")
        recs = results['insights'].get('recommendations', [])
        if recs:
            print(f"   {recs[0]}")
        
        print("\n" + "=" * 70)
    
    def generate_content_only(self, topic: str) -> Dict:
        """Generate content without distribution (useful for testing)."""
        return self._generate_content(topic)
    
    def get_campaign_history(self, limit: int = 10) -> List[Dict]:
        """Retrieve campaign history from database."""
        return self.storage.get_all_campaigns()[:limit]
    
    def analyze_historical_trends(self, limit: int = 20) -> Dict:
        """Analyze trends from historical campaigns."""
        historical_data = self.storage.get_historical_performance(limit)
        return self.analyzer.identify_trends(historical_data)


def main():
    """Main entry point for the pipeline."""
    
    # Initialize pipeline
    pipeline = ContentPipeline()
    
    # Example topic
    topic = "AI-powered workflow automation for creative agencies"
    
    print(f"\nRunning pipeline for topic: '{topic}'\n")
    
    # Run full pipeline
    results = pipeline.run_full_pipeline(topic, test_mode=True)
    
    # Show that we can also suggest next topics
    print("\n" + "=" * 70)
    print("BONUS: Next Topic Suggestions")
    print("=" * 70)
    
    historical_data = pipeline.storage.get_historical_performance(limit=5)
    next_topics = pipeline.content_gen.suggest_next_topics(
        performance_data=historical_data,
        num_suggestions=3
    )
    
    print("\nSuggested topics for next campaign:")
    for i, topic_suggestion in enumerate(next_topics, 1):
        print(f"{i}. {topic_suggestion}")
    
    print("\nPipeline execution complete!")
    print(f"All data saved to: {Config.DATABASE_PATH}")
    
    # Only show content export if pipeline completed successfully
    if results.get('status') == 'completed' and 'content' in results:
        print(f"Content exported to: data/content_{results['content']['content_id']}.json")
    
    print("\nRun the dashboard to visualize results: python dashboard.py")


if __name__ == "__main__":
    main()

