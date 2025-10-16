"""
AI Content Generator for the marketing pipeline.
Generates blog posts and personalized newsletters using OpenAI API.
"""
from openai import OpenAI
from typing import Dict, List, Tuple
import json
from config import Config


class ContentGenerator:
    """Generates marketing content using AI."""
    
    def __init__(self, api_key: str = None, model: str = None):
        """Initialize the content generator with OpenAI client."""
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.model = model or Config.OPENAI_MODEL
        self.client = OpenAI(api_key=self.api_key)
        self.personas = Config.PERSONAS
    
    def generate_blog_post(self, topic: str) -> Dict[str, str]:
        """
        Generate a blog post outline and draft.
        
        Args:
            topic: The blog post topic/idea
            
        Returns:
            Dictionary containing title, outline, content, and word_count
        """
        system_prompt = """You are an expert content writer for NovaMind, an AI startup 
that helps small creative agencies automate their daily workflows (think Notion + Zapier + ChatGPT combined).
Write engaging, informative content that demonstrates thought leadership in the AI automation space."""
        
        user_prompt = f"""Create a blog post about: {topic}

Requirements:
- Length: {Config.BLOG_MIN_WORDS}-{Config.BLOG_MAX_WORDS} words
- Target audience: Small creative agencies and tech-forward professionals
- Tone: Professional yet approachable, innovative, forward-thinking
- Include actionable insights and real-world applications

Please provide:
1. A compelling title
2. A structured outline (3-5 main sections)
3. The full blog post content

Format your response as JSON with keys: "title", "outline", "content"
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
        
        result = json.loads(response.choices[0].message.content)
        
        # with word count
        result['word_count'] = len(result['content'].split())
        
        return result
    
    def generate_newsletter_variations(self, blog_title: str, blog_content: str) -> Dict[str, Dict]:
        """
        Generate personalized newsletter variations for each persona.
        
        Args:
            blog_title: The blog post title
            blog_content: The full blog post content
            
        Returns:
            Dictionary with persona keys containing subject_line, body, and word_count
        """
        newsletters = {}
        
        for persona_key, persona_info in self.personas.items():
            newsletter = self._generate_single_newsletter(
                blog_title=blog_title,
                blog_content=blog_content,
                persona_key=persona_key,
                persona_info=persona_info
            )
            newsletters[persona_key] = newsletter
        
        return newsletters
    
    def _generate_single_newsletter(self, blog_title: str, blog_content: str,
                                   persona_key: str, persona_info: Dict) -> Dict:
        """Generate a newsletter for a specific persona."""
        system_prompt = f"""You are crafting a personalized newsletter for NovaMind's audience.
This specific version targets: {persona_info['name']}
Their key interests: {persona_info['focus']}
Desired tone: {persona_info['tone']}"""
        
        user_prompt = f"""Based on this blog post, create a personalized newsletter email:

Blog Title: {blog_title}

Blog Content (excerpt):
{blog_content[:500]}...

Requirements:
- Maximum length: {Config.NEWSLETTER_MAX_WORDS} words
- Compelling subject line (under 60 characters)
- Hook the reader immediately
- Highlight aspects most relevant to {persona_info['name']}
- Include a clear call-to-action (Read the full blog)
- Personalized tone: {persona_info['tone']}
- Focus on: {persona_info['focus']}

Format your response as JSON with keys: "subject_line", "body"
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.8
        )
        
        result = json.loads(response.choices[0].message.content)
        result['word_count'] = len(result['body'].split())
        result['persona'] = persona_key
        
        return result
    
    def generate_content_variations(self, blog_title: str, blog_content: str, 
                                   num_variations: int = 3) -> List[Dict]:
        """
        Generate multiple variations of newsletter content for A/B testing.
        
        Args:
            blog_title: The blog post title
            blog_content: The blog post content
            num_variations: Number of variations to generate
            
        Returns:
            List of variation dictionaries
        """
        variations = []
        
        for i in range(num_variations):
            system_prompt = f"""You are creating variation #{i+1} of a newsletter.
Make each variation distinctly different in approach, hook, and structure."""
            
            user_prompt = f"""Create a unique newsletter variation about this blog post:

Title: {blog_title}
Content Preview: {blog_content[:400]}...

This is variation {i+1} of {num_variations}. Make it distinctly different from typical approaches.

Variation focus:
- Variation 1: Data-driven and metric-focused
- Variation 2: Story-driven with case study angle  
- Variation 3: Problem-solution framework

Maximum {Config.NEWSLETTER_MAX_WORDS} words.
Format as JSON with keys: "subject_line", "body", "approach"
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.9
            )
            
            variation = json.loads(response.choices[0].message.content)
            variation['variation_number'] = i + 1
            variation['word_count'] = len(variation['body'].split())
            variations.append(variation)
        
        return variations
    
    def suggest_next_topics(self, performance_data: List[Dict], 
                           num_suggestions: int = 5) -> List[str]:
        """
        Use AI to suggest next blog topics based on performance data.
        
        Args:
            performance_data: Historical performance metrics
            num_suggestions: Number of topic suggestions to generate
            
        Returns:
            List of suggested topics
        """
        if not performance_data:
            # default suggestions if no performance data
            return [
                "AI-powered workflow automation for creative teams",
                "Integrating ChatGPT into your agency's daily operations",
                "Time-saving tools every creative professional should know",
                "How to measure ROI on automation investments",
                "Building custom automation workflows without code"
            ]
        
        # prepare performance summary
        perf_summary = self._summarize_performance(performance_data)
        
        system_prompt = """You are a content strategist for NovaMind. 
Analyze performance data to suggest high-performing blog topics."""
        
        user_prompt = f"""Based on this performance data, suggest {num_suggestions} blog topics:

Performance Summary:
{perf_summary}

Context: NovaMind helps small creative agencies automate workflows using AI.

Suggest topics that:
1. Build on successful themes
2. Address audience interests (founders, creatives, operations managers)
3. Are timely and relevant to AI/automation trends
4. Drive engagement and conversions

Return as JSON with key "topics" containing a list of topic strings.
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.8
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get('topics', [])
    
    def _summarize_performance(self, performance_data: List[Dict]) -> str:
        """Create a text summary of performance data for AI analysis."""
        summary_lines = []
        
        for data in performance_data[:10]:  # Last 10 campaigns
            summary_lines.append(
                f"Topic: {data.get('topic', 'Unknown')} | "
                f"Persona: {data.get('persona', 'Unknown')} | "
                f"Open Rate: {data.get('open_rate', 0):.1%} | "
                f"Click Rate: {data.get('click_rate', 0):.1%}"
            )
        
        return "\n".join(summary_lines)
    
    def optimize_subject_line(self, original_subject: str, 
                             performance_notes: str = "") -> List[str]:
        """
        Generate optimized subject line variations.
        
        Args:
            original_subject: The original subject line
            performance_notes: Optional performance feedback
            
        Returns:
            List of optimized subject line alternatives
        """
        system_prompt = """You are an email marketing expert specializing in subject line optimization."""
        
        user_prompt = f"""Optimize this email subject line:

Original: "{original_subject}"

{f"Performance feedback: {performance_notes}" if performance_notes else ""}

Generate 5 alternative subject lines that:
- Are under 60 characters
- Create curiosity or urgency
- Are clear and benefit-focused
- Avoid spam trigger words
- Test different approaches (question, number, benefit, urgency, curiosity)

Return as JSON with key "subject_lines" containing a list of strings.
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.9
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get('subject_lines', [])

