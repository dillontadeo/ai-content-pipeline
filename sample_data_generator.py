"""
Sample Data Generator
Creates realistic test data for demonstrating the pipeline without making API calls.
Useful for testing, demos, and development.
"""
from src.data_storage import DataStorage
from datetime import datetime, timedelta
import random


def generate_sample_contacts(storage: DataStorage, count: int = 20):
    """Generate sample contacts across all personas."""
    
    first_names = [
        "Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan", "Sophia", "Mason",
        "Isabella", "William", "Mia", "James", "Charlotte", "Benjamin", "Amelia"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
        "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Wilson"
    ]
    
    companies = [
        "Creative Studio Labs", "Design Agency Co", "Brand Workshop",
        "Pixel Perfect Studios", "Innovation Agency", "The Creative House",
        "Digital Craft", "Studio Momentum", "Visionary Creative"
    ]
    
    personas = ["founders", "creatives", "operations"]
    
    contacts = []
    
    for i in range(count):
        first = random.choice(first_names)
        last = random.choice(last_names)
        persona = random.choice(personas)
        company = random.choice(companies)
        
        email = f"{first.lower()}.{last.lower()}@{company.lower().replace(' ', '')}.com"
        
        contact_id = storage.save_contact(
            email=email,
            first_name=first,
            last_name=last,
            persona=persona,
            company=company,
            hubspot_contact_id=f"mock_{i+1000}"
        )
        
        contacts.append({
            'id': contact_id,
            'email': email,
            'first_name': first,
            'last_name': last,
            'persona': persona,
            'company': company
        })
    
    print(f"Generated {count} sample contacts")
    return contacts


def generate_sample_campaigns(storage: DataStorage, count: int = 5):
    """Generate sample campaigns with content and performance."""
    
    topics = [
        "AI-powered workflow automation for creative teams",
        "Time-saving automation tools every designer needs",
        "How to integrate ChatGPT into your agency workflow",
        "Building efficient project management systems with AI",
        "Measuring ROI on marketing automation investments",
        "Creative automation: Balancing AI and human creativity",
        "Operations optimization through intelligent automation",
        "The future of AI in creative agency workflows"
    ]
    
    personas = ["founders", "creatives", "operations"]
    campaigns_created = []
    
    for i in range(count):
        topic = random.choice(topics)
        
        # Create content
        blog_title = f"{topic.title()} - {i+1}"
        blog_content = f"Sample blog content about {topic}. " * 50  # ~500 words
        blog_outline = "1. Introduction\n2. Main Points\n3. Conclusion"
        
        content_id = storage.save_content(
            topic=topic,
            blog_title=blog_title,
            blog_content=blog_content,
            blog_outline=blog_outline,
            word_count=len(blog_content.split())
        )
        
        # Create newsletters for each persona
        for persona in personas:
            subject_line = f"[Sample] {blog_title} - For {persona}"
            body = f"Sample newsletter for {persona} about {topic}. " * 20
            
            storage.save_newsletter(
                content_id=content_id,
                persona=persona,
                subject_line=subject_line,
                body=body,
                word_count=len(body.split())
            )
        
        # Create campaigns
        campaign_name = f"{blog_title} - Campaign"
        
        for persona in personas:
            campaign_id = storage.create_campaign(
                content_id=content_id,
                campaign_name=f"{campaign_name} - {persona}",
                hubspot_campaign_id=f"sample_camp_{i}_{persona}"
            )
            
            # Generate realistic performance metrics
            engagement_profiles = {
                'founders': {'open': (0.22, 0.32), 'click': (0.08, 0.14)},
                'creatives': {'open': (0.25, 0.38), 'click': (0.10, 0.17)},
                'operations': {'open': (0.18, 0.26), 'click': (0.06, 0.11)}
            }
            
            profile = engagement_profiles[persona]
            contacts_sent = random.randint(30, 100)
            open_rate = random.uniform(*profile['open'])
            click_rate = random.uniform(*profile['click'])
            unsub_rate = random.uniform(0.002, 0.008)
            
            opens = int(contacts_sent * open_rate)
            clicks = int(contacts_sent * click_rate)
            unsubs = int(contacts_sent * unsub_rate)
            
            storage.save_campaign_performance(
                campaign_id=campaign_id,
                persona=persona,
                metrics={
                    'contacts_sent': contacts_sent,
                    'opens': opens,
                    'clicks': clicks,
                    'unsubscribes': unsubs,
                    'open_rate': open_rate,
                    'click_rate': click_rate,
                    'unsubscribe_rate': unsub_rate
                }
            )
            
            # Add insights
            storage.save_insight(
                campaign_id=campaign_id,
                insight_text=f"Sample campaign performed well with {persona} segment.",
                recommendations=f"Continue similar content for {persona}"
            )
            
            campaigns_created.append({
                'campaign_id': campaign_id,
                'persona': persona,
                'blog_title': blog_title
            })
    
    print(f"Generated {count * 3} sample campaigns ({count} content pieces x 3 personas)")
    return campaigns_created


def main():
    """Generate a complete sample dataset."""
    print("\n" + "="*70)
    print("SAMPLE DATA GENERATOR")
    print("="*70 + "\n")
    
    # Initialize storage
    storage = DataStorage()
    
    print("Generating sample data...\n")
    
    # Generate contacts
    contacts = generate_sample_contacts(storage, count=20)
    
    # Generate campaigns
    campaigns = generate_sample_campaigns(storage, count=5)
    
    print("\n" + "="*70)
    print("SAMPLE DATA GENERATION COMPLETE")
    print("="*70)
    print(f"\nCreated:")
    print(f"   - {len(contacts)} contacts")
    print(f"   - {len(campaigns)} campaigns")
    print(f"   - Performance metrics for all campaigns")
    print(f"   - AI-generated insights")
    
    print(f"\nData saved to: data/pipeline.db")
    print(f"\nNext steps:")
    print(f"   1. Run 'python dashboard.py' to view the data")
    print(f"   2. Run 'python main.py' to add more campaigns")
    print(f"   3. Explore the database with any SQLite browser")
    print()


if __name__ == "__main__":
    main()

