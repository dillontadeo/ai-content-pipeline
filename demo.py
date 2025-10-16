"""
Interactive Demo Script
Showcases all features of the AI Content Pipeline with guided walkthroughs.
"""
import sys
import time
from main import ContentPipeline
from src.data_storage import DataStorage
from config import Config


def print_header(text):
    """Print a styled header."""
    print("\n" + "="*70)
    print(text.center(70))
    print("="*70 + "\n")


def print_section(text):
    """Print a section header."""
    print("\n" + "-"*70)
    print(text)
    print("-"*70)


def pause(message="Press Enter to continue..."):
    """Pause for user input."""
    input(f"\n{message}")


def demo_content_generation():
    """Demo: Content generation only."""
    print_header("DEMO 1: AI CONTENT GENERATION")
    
    print("This demo shows how the system generates:")
    print("  • Blog posts (400-600 words)")
    print("  • 3 personalized newsletter variations")
    print("  • Structured output (JSON)")
    
    pause()
    
    pipeline = ContentPipeline()
    
    print("\n📝 Generating content about: 'AI productivity tools for creative teams'")
    
    results = pipeline.generate_content_only(
        "AI productivity tools for creative teams"
    )
    
    print_section("GENERATED BLOG POST")
    print(f"Title: {results['blog']['title']}")
    print(f"Word Count: {results['blog']['word_count']}")
    print(f"\nOutline:\n{results['blog']['outline']}")
    print(f"\nContent Preview:\n{results['blog']['content'][:300]}...")
    
    print_section("GENERATED NEWSLETTERS")
    for persona, newsletter in results['newsletters'].items():
        persona_name = Config.PERSONAS[persona]['name']
        print(f"\n{persona_name}:")
        print(f"  Subject: {newsletter['subject_line']}")
        print(f"  Preview: {newsletter['body'][:150]}...")
        print(f"  Words: {newsletter['word_count']}")
    
    print(f"\n✅ Content saved! Content ID: {results['content_id']}")
    print(f"📄 Exported to: data/content_{results['content_id']}.json")
    
    pause("Press Enter to continue to next demo...")


def demo_full_pipeline():
    """Demo: Full pipeline execution."""
    print_header("DEMO 2: FULL PIPELINE EXECUTION")
    
    print("This demo runs the complete pipeline:")
    print("  1. Generate content")
    print("  2. Distribute via CRM")
    print("  3. Collect performance metrics")
    print("  4. Generate AI insights")
    
    pause()
    
    pipeline = ContentPipeline()
    
    topic = "Time-saving automation for creative agencies"
    print(f"\n🚀 Running full pipeline for: '{topic}'")
    print("\n(This will take about 60 seconds...)\n")
    
    results = pipeline.run_full_pipeline(topic, test_mode=True)
    
    # The pipeline prints its own summary
    
    pause("Press Enter to continue to next demo...")


def demo_performance_analysis():
    """Demo: Performance analysis and insights."""
    print_header("DEMO 3: PERFORMANCE ANALYSIS")
    
    print("This demo shows how the system:")
    print("  • Tracks engagement metrics")
    print("  • Compares to industry benchmarks")
    print("  • Generates AI-powered insights")
    print("  • Suggests optimizations")
    
    pause()
    
    storage = DataStorage()
    
    # Get historical data
    historical = storage.get_historical_performance(limit=10)
    
    if not historical:
        print("\n⚠️  No campaign data yet. Run demo 2 first to generate data.")
        return
    
    print_section("HISTORICAL PERFORMANCE")
    
    # Calculate averages by persona
    by_persona = {}
    for record in historical:
        persona = record['persona']
        if persona not in by_persona:
            by_persona[persona] = {'count': 0, 'total_open': 0, 'total_click': 0}
        by_persona[persona]['count'] += 1
        by_persona[persona]['total_open'] += record['open_rate']
        by_persona[persona]['total_click'] += record['click_rate']
    
    print(f"\nAnalyzing {len(historical)} campaigns...\n")
    
    for persona, data in by_persona.items():
        avg_open = (data['total_open'] / data['count']) * 100
        avg_click = (data['total_click'] / data['count']) * 100
        print(f"{persona.upper():12} | Campaigns: {data['count']:2} | "
              f"Avg Open: {avg_open:5.1f}% | Avg Click: {avg_click:5.1f}%")
    
    print_section("BENCHMARKS COMPARISON")
    print("\nIndustry Benchmarks (B2B SaaS):")
    print("  Open Rate:   21.0%")
    print("  Click Rate:  10.0%")
    print("  Unsub Rate:   0.5%")
    
    print("\nYour Performance:")
    overall_open = sum(r['open_rate'] for r in historical) / len(historical) * 100
    overall_click = sum(r['click_rate'] for r in historical) / len(historical) * 100
    
    print(f"  Open Rate:  {overall_open:5.1f}% " + 
          ("✓ Above benchmark" if overall_open > 21 else "⚠ Below benchmark"))
    print(f"  Click Rate: {overall_click:5.1f}% " + 
          ("✓ Above benchmark" if overall_click > 10 else "⚠ Below benchmark"))
    
    pause("Press Enter to continue to next demo...")


def demo_optimization_features():
    """Demo: Content optimization features."""
    print_header("DEMO 4: CONTENT OPTIMIZATION")
    
    print("This demo showcases advanced features:")
    print("  • Next topic suggestions based on performance")
    print("  • Subject line optimization")
    print("  • Content variation generation")
    
    pause()
    
    pipeline = ContentPipeline()
    storage = DataStorage()
    
    print_section("NEXT TOPIC SUGGESTIONS")
    print("\nAnalyzing past performance to suggest topics...")
    
    historical = storage.get_historical_performance(limit=10)
    suggestions = pipeline.content_gen.suggest_next_topics(
        performance_data=historical,
        num_suggestions=5
    )
    
    print("\nSuggested topics for your next campaign:")
    for i, topic in enumerate(suggestions, 1):
        print(f"{i}. {topic}")
    
    print_section("SUBJECT LINE OPTIMIZATION")
    print("\nOriginal: 'Check out our new AI tools'")
    print("Generating optimized variations...\n")
    
    optimized = pipeline.content_gen.optimize_subject_line(
        "Check out our new AI tools",
        performance_notes="Previous campaign had low open rate"
    )
    
    print("Optimized alternatives:")
    for i, subject in enumerate(optimized, 1):
        print(f"{i}. {subject}")
    
    pause("Press Enter to return to main menu...")


def demo_dashboard_preview():
    """Demo: Dashboard features."""
    print_header("DEMO 5: WEB DASHBOARD")
    
    print("The web dashboard provides:")
    print("  • Real-time analytics visualization")
    print("  • Interactive campaign management")
    print("  • One-click pipeline execution")
    print("  • Performance metrics dashboard")
    
    print("\nTo launch the dashboard:")
    print("  1. Open a terminal")
    print("  2. Run: python dashboard.py")
    print("  3. Open browser to: http://localhost:5000")
    
    print("\nFeatures available in dashboard:")
    print("  ✓ View aggregate analytics")
    print("  ✓ Browse campaign history")
    print("  ✓ Generate new content with custom topics")
    print("  ✓ Run full pipeline with one click")
    print("  ✓ Beautiful, modern UI")
    
    choice = input("\nWould you like to launch the dashboard now? (y/n): ")
    
    if choice.lower() == 'y':
        print("\n🌐 Launching dashboard...")
        print("Opening http://localhost:5000 in your browser...")
        print("\nPress Ctrl+C to stop the server when done.\n")
        time.sleep(2)
        
        import dashboard
        dashboard.main()
    
    pause()


def show_menu():
    """Display the demo menu."""
    print_header("AI CONTENT PIPELINE - INTERACTIVE DEMO")
    
    print("Select a demo to run:\n")
    print("  1. Content Generation Only")
    print("  2. Full Pipeline Execution")
    print("  3. Performance Analysis")
    print("  4. Content Optimization Features")
    print("  5. Web Dashboard Preview")
    print("  6. Run All Demos in Sequence")
    print("  0. Exit")
    
    return input("\nEnter your choice (0-6): ")


def main():
    """Run the interactive demo."""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║         AI CONTENT PIPELINE - INTERACTIVE DEMO                    ║
║         Take-Home Assignment for Palona AI                        ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    print("Welcome! This interactive demo will walk you through all features")
    print("of the AI Content Pipeline.\n")
    
    # Check configuration
    try:
        Config.validate()
        print("✓ Configuration validated")
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\nPlease add your OpenAI API key to the .env file.")
        print("See QUICKSTART.md for instructions.\n")
        return
    
    while True:
        choice = show_menu()
        
        if choice == '0':
            print("\n👋 Thanks for exploring the AI Content Pipeline!")
            print("Check out README.md for more information.\n")
            break
        elif choice == '1':
            demo_content_generation()
        elif choice == '2':
            demo_full_pipeline()
        elif choice == '3':
            demo_performance_analysis()
        elif choice == '4':
            demo_optimization_features()
        elif choice == '5':
            demo_dashboard_preview()
        elif choice == '6':
            print("\n🎬 Running all demos in sequence...\n")
            demo_content_generation()
            demo_full_pipeline()
            demo_performance_analysis()
            demo_optimization_features()
            demo_dashboard_preview()
            print_header("ALL DEMOS COMPLETE!")
        else:
            print("\n❌ Invalid choice. Please enter 0-6.\n")
            time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!")
        sys.exit(0)

