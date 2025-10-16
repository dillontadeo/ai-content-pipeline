# AI-Powered Marketing Content Pipeline

An intelligent, automated marketing pipeline that generates, distributes, and optimizes blog and newsletter content using AI and CRM integrations.

---

## Overview


1. Generates blog posts and personalized newsletters using AI
2. Distributes content to segmented audiences via CRM
3. Collects engagement metrics (opens, clicks, etc.)
4. Analyzes performance using AI-powered insights
5. Optimizes future content based on data

### The Problem We Solve

Marketing teams spend countless hours creating content, manually segmenting audiences, sending campaigns, and analyzing results. This pipeline automates 90% of that workflow while maintaining quality and personalization.

---

## Architecture Overview

### System Flow Diagram

```
User Input (Topic)
       |
       v
Content Generator (OpenAI GPT-4)
├── Blog Post (400-600 words)
└── 3 Newsletters (persona-specific)
       |
       v
Data Storage (SQLite Database)
       |
       v
CRM Integration (HubSpot/Mock)
├── Contact Management
└── Email Distribution
       |
       v
Performance Analyzer
├── Metrics Collection
├── Trend Analysis
└── AI Insights
       |
       v
Dashboard (Flask Web UI)
└── Visualization & Control
```

### Component Architecture

The system consists of five main modules:

1. **Content Generator** (`src/content_generator.py`)
   - Generates blog posts using OpenAI GPT-4
   - Creates 3 personalized newsletter variations
   - Optimizes subject lines and suggests next topics

2. **CRM Integration** (`src/crm_integration.py`)
   - Integrates with HubSpot API
   - Manages contacts and segmentation
   - Distributes campaigns via email
   - Operates in mock mode without API key

3. **Performance Analyzer** (`src/performance_analyzer.py`)
   - Collects engagement metrics
   - Generates AI-powered insights
   - Compares to industry benchmarks
   - Identifies trends over time

4. **Data Storage** (`src/data_storage.py`)
   - SQLite database for persistence
   - Stores content, campaigns, contacts, metrics
   - Exports to JSON format

5. **Pipeline Orchestrator** (`main.py`)
   - Coordinates all modules
   - Executes end-to-end workflow
   - Handles error management

6. **Web Dashboard** (`dashboard.py`)
   - Flask-based web interface
   - Real-time analytics visualization
   - Interactive campaign management

---

## Tools, APIs, and Models Used

### Core Technologies

**Programming Language:**
- Python 3.8+

**AI/ML:**
- OpenAI API (GPT-4 or GPT-3.5-turbo)
  - Used for blog post generation
  - Used for newsletter personalization
  - Used for performance insights generation

**CRM Integration:**
- HubSpot API
  - Contact management
  - Email campaign distribution
  - Campaign tracking
  - Mock mode available when API key not provided

**Data Storage:**
- SQLite
  - Local database for all data persistence
  - 6 tables for content, campaigns, metrics, contacts, insights

**Web Framework:**
- Flask 3.0+
  - REST API endpoints
  - Dashboard UI serving
  - CORS enabled

**Additional Libraries:**
- pandas: Data analysis
- python-dotenv: Configuration management
- requests: HTTP client
- hubspot-api-client: HubSpot integration

### API Models

**OpenAI:**
- Model: gpt-4 (default) or gpt-3.5-turbo
- Temperature: 0.7-0.9 for creative content
- Response format: JSON mode for structured output

**HubSpot:**
- Contacts API: Create/update contacts
- Lists API: Segmentation
- Marketing Email API: Campaign distribution (conceptual)

---

## Assumptions Made

### Content Generation

1. **Blog Length**: 400-600 words is sufficient for demonstration purposes
2. **Personas**: Three audience segments (Founders, Creatives, Operations) are adequate for showcasing personalization
3. **Language**: English-only content is acceptable
4. **Content Quality**: AI-generated content is production-ready without human editing

### CRM Integration

1. **Mock Mode**: System fully functional without HubSpot API key
   - All CRM operations are simulated with realistic responses
   - Email sending is mocked (not actual SMTP delivery)
   - Campaign IDs and contact IDs are generated locally

2. **HubSpot API**: When API key is provided, system uses real HubSpot endpoints
   - Actual contact creation/updates
   - Real campaign tracking
   - API rate limits are respected

### Performance Metrics

1. **Simulated Data**: Engagement metrics are generated algorithmically
   - Based on realistic industry patterns
   - Different personas have different engagement profiles:
     - Founders: 22-32% open rate, 8-14% click rate
     - Creatives: 25-38% open rate, 10-17% click rate (highest engagement)
     - Operations: 18-26% open rate, 6-11% click rate

2. **Real Data**: System can integrate with actual HubSpot analytics when available

### Database

1. **SQLite**: Sufficient for demonstration and development
   - Single file database
   - No external dependencies
   - Easily upgradable to PostgreSQL for production

2. **Data Retention**: No automatic cleanup implemented (all data persists)

### Testing

1. **Test Contacts**: 9 mock contacts created automatically (3 per persona)
2. **Email Delivery**: Actual emails are not sent in mock mode
3. **API Costs**: Each pipeline run uses ~4-5 OpenAI API calls (approximately $0.10-0.20)

---

## Instructions to Run Locally

### Prerequisites

- Python 3.8 or higher installed
- OpenAI API key (required)
- HubSpot API key (optional - system works without it)

### Step-by-Step Setup

#### 1. Clone the Repository

```bash
cd ai-content-pipeline
```

#### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the example file
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

Edit `.env` and add your API keys:

```
# REQUIRED: OpenAI API Key
OPENAI_API_KEY=sk-your-actual-key-here
OPENAI_MODEL=gpt-4

# OPTIONAL: HubSpot API Key (system works without it)
HUBSPOT_API_KEY=your_hubspot_key_here
HUBSPOT_ACCOUNT_ID=your_account_id_here

# Content Settings (defaults provided)
BLOG_MIN_WORDS=400
BLOG_MAX_WORDS=600
NEWSLETTER_MAX_WORDS=250

# Database
DATABASE_PATH=data/pipeline.db

# Flask Dashboard
FLASK_PORT=5000
FLASK_ENV=development
```


### Running the Pipeline

#### Option 1: Full Pipeline (Command Line)

Run the complete pipeline from content generation to analysis:

```bash
python main.py
```

**What happens:**
1. Generates blog post about "AI-powered workflow automation"
2. Creates 3 personalized newsletters
3. Sends to test contacts (mock mode)
4. Collects performance metrics
5. Generates AI-powered insights
6. Displays summary report

**Output:**
- Console summary with metrics
- Database records in `data/pipeline.db`
- JSON export in `data/content_X.json`

**Execution time:** Approximately 2-3 minutes

#### Open Web Dashboard

Launch the interactive dashboard:

```bash
python dashboard.py
```

Then open your browser to: **http://localhost:5000**

**Dashboard Features:**
- View real-time analytics
- Browse campaign history
- Generate new content with custom topics
- Run full pipeline with one click
- See performance insights
- Export data


## Project Structure

```
ai-content-pipeline/
│
├── config.py                 # Configuration management
├── main.py                   # Main pipeline orchestrator
├── dashboard.py              # Web dashboard (Flask)
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (not in git)
├── .gitignore               # Git ignore rules
│
├── src/                      # Core modules
│   ├── __init__.py
│   ├── content_generator.py  # AI content generation
│   ├── crm_integration.py    # HubSpot CRM integration
│   ├── performance_analyzer.py # Metrics & insights
│   └── data_storage.py       # Database operations
│
├── data/                     # Data storage (gitignored)
│   ├── pipeline.db          # SQLite database
│   └── content_*.json       # Exported content
│
├── templates/               # Web templates
│   └── dashboard.html       # Dashboard UI
│
└── README.md                # This file
```

---

## Database Schema

The system uses SQLite with the following tables:

**content**
- id, topic, blog_title, blog_content, blog_outline, word_count, created_at

**newsletters**
- id, content_id, persona, subject_line, body, word_count, created_at

**campaigns**
- id, content_id, campaign_name, send_date, status, hubspot_campaign_id

**campaign_performance**
- id, campaign_id, persona, contacts_sent, opens, clicks, unsubscribes
- open_rate, click_rate, unsubscribe_rate, recorded_at

**contacts**
- id, email, first_name, last_name, persona, company
- hubspot_contact_id, created_at, updated_at

**performance_insights**
- id, campaign_id, insight_text, recommendations, created_at

---

## Features

### 1. AI Content Generation

- Generate blog posts (400-600 words) with outline
- Create 3 personalized newsletter variations:
  - Founders: ROI, growth, efficiency focus
  - Creatives: Inspiration, time-saving tools focus
  - Operations: Workflows, integrations, reliability focus
- Store content in structured format (SQLite + JSON export)
- Uses OpenAI GPT-4 for high-quality content

### 2. CRM + Newsletter Distribution

- HubSpot API integration
- Create/update contacts with segmentation
- Send personalized newsletters to each segment
- Log campaigns with IDs and timestamps
- Mock mode for testing without API keys

### 3. Performance Logging & Analysis

- Fetch/simulate campaign metrics (open rate, click rate, etc.)
- Store historical performance data
- AI-powered performance summaries with recommendations
- Compare to industry benchmarks

### 4. Advanced Optimizations (Bonus)

- AI-driven content optimization
  - Next topic suggestions based on engagement
  - Subject line optimization
  - A/B testing variations
- Trend analysis from historical data
- Benchmark comparisons (industry standards)

### 5. Web Dashboard (Bonus)

- Modern, responsive UI
- Real-time analytics overview
- Campaign history visualization
- Trigger pipeline execution from UI
- Generate content without distribution

---

## Performance Metrics

The system tracks and analyzes:

- **Open Rate**: Percentage of emails opened
- **Click Rate**: Percentage of emails clicked
- **Click-to-Open Rate**: Percentage of opens that clicked
- **Unsubscribe Rate**: Percentage who unsubscribed
- **Engagement Score**: Composite score (0-100)

### Industry Benchmarks (B2B SaaS)

- Open Rate: 21%
- Click Rate: 10%
- Unsubscribe Rate: 0.5%

Performance is compared against these benchmarks with AI-generated insight.