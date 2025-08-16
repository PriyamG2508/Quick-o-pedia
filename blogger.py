import os
import requests
import json
import logging
from datetime import datetime
from typing import TypedDict, List, Optional, Dict, Any
import operator
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from pathlib import Path
import time
import re
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('blogging_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- 1. Enhanced State Definition ---
class BloggingState(TypedDict):
    # Topic-related
    trending_topics: List[dict]
    selected_topic: str
    topic_metadata: Dict[str, Any]
    
    # User preferences
    audience: str
    tone: str
    length: str
    keywords: List[str]
    content_type: str  # blog, article, tutorial, etc.
    
    # Content generation
    outline: str
    content: str
    optimized_content: str
    title_suggestions: List[str]
    
    # Quality metrics
    seo_score: int
    readability_score: int
    content_quality_score: int
    
    # Workflow control
    user_feedback: str
    is_complete: bool
    generation_attempts: int
    errors: List[str]
    
    # Metadata
    created_at: str
    word_count: int
    estimated_read_time: int

# --- 2. Enhanced Configuration ---
class BloggingConfig:
    def __init__(self):
        load_dotenv()
        
        # API Configuration
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        # Model settings
        self.model_name = os.getenv("MODEL_NAME", "llama3-70b-8192")
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("MAX_TOKENS", "4000"))
        
        # Content settings
        self.min_word_count = int(os.getenv("MIN_WORD_COUNT", "300"))
        self.max_word_count = int(os.getenv("MAX_WORD_COUNT", "3000"))
        self.max_generation_attempts = int(os.getenv("MAX_GENERATION_ATTEMPTS", "3"))
        
        # Reddit API settings
        self.reddit_user_agent = os.getenv("REDDIT_USER_AGENT", "BloggingAgent/2.0")
        self.reddit_timeout = int(os.getenv("REDDIT_TIMEOUT", "10"))

# --- 3. Enhanced Data Sources ---
class TopicFetcher:
    def __init__(self, config: BloggingConfig):
        self.config = config
        
    def fetch_reddit_topics(self, subreddit: str = "all", limit: int = 25) -> List[dict]:
        """Fetch trending topics from Reddit with enhanced filtering."""
        try:
            logger.info(f"Fetching topics from r/{subreddit}")
            
            url = f'https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}'
            headers = {'User-Agent': self.config.reddit_user_agent}
            
            response = requests.get(url, headers=headers, timeout=self.config.reddit_timeout)
            response.raise_for_status()
            
            data = response.json()
            topics = []
            
            for post in data['data']['children']:
                post_data = post['data']
                
                # Enhanced filtering
                if (post_data['score'] > 1000 and 
                    not post_data['over_18'] and 
                    len(post_data['title']) < 200 and
                    len(post_data['title']) > 10 and
                    not post_data.get('stickied', False)):
                    
                    topics.append({
                        'title': post_data['title'],
                        'score': post_data['score'],
                        'num_comments': post_data['num_comments'],
                        'subreddit': post_data['subreddit'],
                        'created_utc': post_data['created_utc'],
                        'url': post_data.get('url', ''),
                        'selftext': post_data.get('selftext', '')[:200] + '...' if post_data.get('selftext') else ''
                    })
            
            logger.info(f"Successfully fetched {len(topics)} topics")
            return topics[:15]  # Return top 15
            
        except Exception as e:
            logger.error(f"Error fetching Reddit topics: {e}")
            return self._get_fallback_topics()
    
    def _get_fallback_topics(self) -> List[dict]:
        """Fallback topics if API fails."""
        return [
            {'title': 'The Future of Artificial Intelligence in 2024', 'score': 5000, 'num_comments': 200, 'subreddit': 'technology'},
            {'title': 'Climate Change Solutions That Actually Work', 'score': 4500, 'num_comments': 180, 'subreddit': 'environment'},
            {'title': 'Remote Work Best Practices for Productivity', 'score': 4000, 'num_comments': 150, 'subreddit': 'productivity'},
            {'title': 'Cybersecurity Trends Every Developer Should Know', 'score': 3800, 'num_comments': 120, 'subreddit': 'programming'},
            {'title': 'Mental Health in the Digital Age', 'score': 3500, 'num_comments': 190, 'subreddit': 'psychology'}
        ]

# --- 4. Content Quality Analyzer ---
class ContentAnalyzer:
    @staticmethod
    def calculate_readability_score(text: str) -> int:
        """Calculate a simple readability score."""
        sentences = len(re.findall(r'[.!?]+', text))
        words = len(text.split())
        
        if sentences == 0:
            return 0
        
        avg_sentence_length = words / sentences
        
        # Simple scoring: penalize very long sentences
        if avg_sentence_length < 15:
            return 85
        elif avg_sentence_length < 20:
            return 75
        elif avg_sentence_length < 25:
            return 65
        else:
            return 50
    
    @staticmethod
    def calculate_seo_score(content: str, topic: str, keywords: List[str]) -> int:
        """Enhanced SEO scoring."""
        score = 60  # Base score
        
        # Check for title (H1)
        if content.strip().startswith("# "):
            score += 15
        
        # Word count optimization
        word_count = len(content.split())
        if 500 <= word_count <= 2000:
            score += 20
        elif word_count < 300:
            score -= 20
        
        # Keyword density check
        content_lower = content.lower()
        topic_lower = topic.lower()
        
        if topic_lower in content_lower:
            score += 10
        
        # Check for keywords
        keyword_count = sum(1 for keyword in keywords if keyword.lower() in content_lower)
        score += min(keyword_count * 3, 15)
        
        # Check for headers (H2, H3)
        if re.search(r'^##\s', content, re.MULTILINE):
            score += 10
        
        return min(score, 100)
    
    @staticmethod
    def calculate_content_quality_score(content: str, outline: str) -> int:
        """Calculate content quality based on structure and completeness."""
        score = 50  # Base score
        
        # Check if content follows outline structure
        outline_headers = re.findall(r'^#+\s(.+)', outline, re.MULTILINE)
        content_headers = re.findall(r'^#+\s(.+)', content, re.MULTILINE)
        
        if len(content_headers) >= len(outline_headers) * 0.7:
            score += 20
        
        # Check for introduction and conclusion
        if "introduction" in content.lower() or content.startswith("# "):
            score += 10
        
        if "conclusion" in content.lower() or "summary" in content.lower():
            score += 10
        
        # Check content depth
        paragraphs = [p for p in content.split('\n\n') if p.strip() and not p.strip().startswith('#')]
        if len(paragraphs) >= 5:
            score += 10
        
        return min(score, 100)

# --- 5. Enhanced Agent Nodes ---
def fetch_trending_topics_node(state: BloggingState) -> dict:
    """Enhanced topic fetching with multiple sources."""
    logger.info("Fetching trending topics...")
    
    config = BloggingConfig()
    fetcher = TopicFetcher(config)
    
    try:
        topics = fetcher.fetch_reddit_topics()
        
        if not topics:
            raise ValueError("No suitable topics found")
        
        logger.info(f"Successfully fetched {len(topics)} topics")
        return {
            "trending_topics": topics,
            "errors": [],
            "created_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in fetch_trending_topics_node: {e}")
        return {
            "trending_topics": [],
            "errors": [str(e)]
        }

def generate_title_suggestions_node(state: BloggingState, llm: ChatGroq) -> dict:
    """Generate multiple title suggestions for the selected topic."""
    logger.info("Generating title suggestions...")
    
    prompt = f"""
    Generate 5 compelling, SEO-friendly blog post titles for the following topic:
    
    Topic: "{state['selected_topic']}"
    Target Audience: {state['audience']}
    Tone: {state['tone']}
    Content Type: {state['content_type']}
    
    Each title should be:
    - Engaging and click-worthy
    - SEO-optimized with relevant keywords
    - Appropriate for the target audience
    - Between 40-60 characters
    
    Return only the titles, numbered 1-5.
    """
    
    try:
        response = llm.invoke(prompt)
        titles = [line.strip() for line in response.content.split('\n') if line.strip() and re.match(r'^\d+\.', line.strip())]
        
        logger.info("Title suggestions generated successfully")
        return {"title_suggestions": titles}
        
    except Exception as e:
        logger.error(f"Error generating titles: {e}")
        return {"title_suggestions": [state['selected_topic']], "errors": state.get('errors', []) + [str(e)]}

def generate_outline_node(state: BloggingState, llm: ChatGroq) -> dict:
    """Enhanced outline generation with better structure."""
    logger.info("Generating detailed outline...")
    
    keywords_str = ", ".join(state.get('keywords', []))
    
    prompt = f"""
    Create a comprehensive, well-structured outline for a {state['content_type']} about:
    
    Topic: "{state['selected_topic']}"
    Target Audience: {state['audience']}
    Tone: {state['tone']}
    Desired Length: {state['length']}
    Keywords to include: {keywords_str}
    
    The outline should include:
    1. An engaging, SEO-optimized title
    2. Introduction with hook and thesis
    3. 4-6 main sections with clear H2 headings
    4. 2-3 subsections (H3) under each main section
    5. Key points and supporting details
    6. Conclusion with call-to-action
    7. Suggested meta description (150 characters)
    
    Format in markdown with proper heading hierarchy.
    """
    
    try:
        response = llm.invoke(prompt)
        logger.info("Outline generated successfully")
        return {"outline": response.content}
        
    except Exception as e:
        logger.error(f"Error generating outline: {e}")
        return {"outline": f"# {state['selected_topic']}\n\nFailed to generate detailed outline.", 
                "errors": state.get('errors', []) + [str(e)]}

def generate_content_node(state: BloggingState, llm: ChatGroq) -> dict:
    """Enhanced content generation with quality controls."""
    logger.info("Generating blog content...")
    
    attempt = state.get('generation_attempts', 0) + 1
    
    length_guidelines = {
        "Short": "300-600 words",
        "Medium": "600-1200 words", 
        "Long": "1200-2500 words"
    }
    
    prompt = f"""
    Write a complete, high-quality {state['content_type']} based on this outline:
    
    {state['outline']}
    
    Guidelines:
    - Target Audience: {state['audience']}
    - Tone: {state['tone']}
    - Length: {length_guidelines.get(state['length'], 'Medium length')}
    - Keywords to naturally incorporate: {', '.join(state.get('keywords', []))}
    
    Requirements:
    - Write in markdown format
    - Include proper headings (H1, H2, H3)
    - Add engaging introduction and strong conclusion
    - Use bullet points and numbered lists where appropriate
    - Include actionable insights and examples
    - Ensure smooth transitions between sections
    - Optimize for readability and SEO
    
    Write the complete article without any meta-commentary.
    """
    
    try:
        response = llm.invoke(prompt)
        content = response.content
        
        # Calculate metrics
        word_count = len(content.split())
        read_time = max(1, word_count // 200)  # Assume 200 WPM reading speed
        
        logger.info(f"Content generated: {word_count} words, ~{read_time} min read")
        
        return {
            "content": content,
            "word_count": word_count,
            "estimated_read_time": read_time,
            "generation_attempts": attempt
        }
        
    except Exception as e:
        logger.error(f"Error generating content: {e}")
        return {
            "content": f"# {state['selected_topic']}\n\nFailed to generate content.",
            "word_count": 0,
            "estimated_read_time": 0,
            "generation_attempts": attempt,
            "errors": state.get('errors', []) + [str(e)]
        }

def content_optimization_node(state: BloggingState) -> dict:
    """Enhanced content optimization with multiple quality metrics."""
    logger.info("Optimizing content for SEO and readability...")
    
    content = state['content']
    analyzer = ContentAnalyzer()
    
    # Ensure proper title format
    if not content.strip().startswith("# "):
        # Use the first title suggestion or fallback to topic
        title = state.get('title_suggestions', [state['selected_topic']])[0]
        if title.startswith(('1.', '2.', '3.', '4.', '5.')):
            title = title.split('.', 1)[1].strip()
        content = f"# {title}\n\n{content}"
    
    # Calculate quality scores
    seo_score = analyzer.calculate_seo_score(
        content, 
        state['selected_topic'], 
        state.get('keywords', [])
    )
    
    readability_score = analyzer.calculate_readability_score(content)
    quality_score = analyzer.calculate_content_quality_score(content, state['outline'])
    
    logger.info(f"Optimization complete - SEO: {seo_score}, Readability: {readability_score}, Quality: {quality_score}")
    
    return {
        "optimized_content": content,
        "seo_score": seo_score,
        "readability_score": readability_score,
        "content_quality_score": quality_score
    }

# --- 6. Enhanced Conditional Logic ---
def decide_workflow_path(state: BloggingState) -> str:
    """Enhanced decision logic for workflow control."""
    logger.info("Evaluating workflow path...")
    
    feedback = state.get("user_feedback", "").lower().strip()
    attempts = state.get("generation_attempts", 0)
    
    if feedback == "approve":
        logger.info("User approved content - finishing workflow")
        return "end"
    elif attempts >= 3:
        logger.info("Maximum attempts reached - finishing workflow")
        return "end"
    elif feedback in ["regenerate", "revise", "improve"]:
        logger.info("User requested regeneration")
        return "regenerate"
    else:
        logger.info("User provided feedback - regenerating with improvements")
        return "regenerate"

# --- 7. Enhanced User Interface ---
class UserInterface:
    @staticmethod
    def display_topics(topics: List[dict]):
        """Display topics in a formatted way."""
        print("\n🔥 Trending Topics Available:")
        print("=" * 60)
        
        for i, topic in enumerate(topics, 1):
            print(f"{i:2d}. {topic['title']}")
            print(f"    📊 Score: {topic['score']:,} | 💬 Comments: {topic['num_comments']} | 📍 r/{topic['subreddit']}")
            if topic.get('selftext'):
                print(f"    📝 Preview: {topic['selftext']}")
            print()
    
    @staticmethod
    def get_user_preferences() -> dict:
        """Get user preferences with validation."""
        print("\n📋 Content Configuration:")
        print("-" * 30)
        
        # Target audience
        audience_options = ["Beginners", "Intermediate", "Advanced", "General Public", "Professionals", "Students"]
        print(f"Audience options: {', '.join(audience_options)}")
        audience = input("👥 Target audience: ").strip() or "General Public"
        
        # Tone options
        tone_options = ["Professional", "Casual", "Friendly", "Authoritative", "Conversational", "Technical"]
        print(f"Tone options: {', '.join(tone_options)}")
        tone = input("🎭 Desired tone: ").strip() or "Conversational"
        
        # Length options
        length_options = ["Short (300-600 words)", "Medium (600-1200 words)", "Long (1200+ words)"]
        print(f"Length options: {', '.join(length_options)}")
        length = input("📏 Content length: ").strip() or "Medium"
        length = length.split()[0]  # Extract just "Short", "Medium", or "Long"
        
        # Content type
        content_types = ["Blog Post", "Tutorial", "Guide", "Analysis", "Review", "Opinion Piece"]
        print(f"Content types: {', '.join(content_types)}")
        content_type = input("📄 Content type: ").strip() or "Blog Post"
        
        # Keywords
        keywords_input = input("🔍 Keywords (comma-separated, optional): ").strip()
        keywords = [k.strip() for k in keywords_input.split(",") if k.strip()] if keywords_input else []
        
        return {
            "audience": audience,
            "tone": tone,
            "length": length,
            "content_type": content_type,
            "keywords": keywords
        }
    
    @staticmethod
    def display_content_summary(state: BloggingState):
        """Display content summary and metrics."""
        print("\n" + "=" * 60)
        print("📊 CONTENT GENERATION COMPLETE")
        print("=" * 60)
        
        print(f"📝 Word Count: {state.get('word_count', 0):,}")
        print(f"⏱️ Estimated Read Time: {state.get('estimated_read_time', 0)} minutes")
        print(f"🔍 SEO Score: {state.get('seo_score', 0)}/100")
        print(f"📖 Readability Score: {state.get('readability_score', 0)}/100")
        print(f"⭐ Content Quality Score: {state.get('content_quality_score', 0)}/100")
        print(f"🔄 Generation Attempts: {state.get('generation_attempts', 0)}")
        
        print("\n📄 CONTENT PREVIEW:")
        print("-" * 40)
        content = state.get('optimized_content', '')
        preview_length = min(800, len(content))
        print(content[:preview_length])
        if len(content) > preview_length:
            print("\n... [Content truncated for preview] ...")

def save_content_to_file(state: BloggingState) -> str:
    """Save the generated content to a file."""
    try:
        # Create output directory
        output_dir = Path("generated_content")
        output_dir.mkdir(exist_ok=True)
        
        # Generate filename
        topic_slug = re.sub(r'[^\w\s-]', '', state['selected_topic'])
        topic_slug = re.sub(r'[-\s]+', '-', topic_slug).strip('-').lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{topic_slug}_{timestamp}.md"
        
        filepath = output_dir / filename
        
        # Prepare content with metadata
        metadata = f"""---
title: "{state['selected_topic']}"
audience: "{state['audience']}"
tone: "{state['tone']}"
length: "{state['length']}"
content_type: "{state['content_type']}"
keywords: {state.get('keywords', [])}
word_count: {state.get('word_count', 0)}
read_time: {state.get('estimated_read_time', 0)}
seo_score: {state.get('seo_score', 0)}
readability_score: {state.get('readability_score', 0)}
quality_score: {state.get('content_quality_score', 0)}
created_at: "{state.get('created_at', datetime.now().isoformat())}"
---

"""
        
        full_content = metadata + state.get('optimized_content', '')
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        logger.info(f"Content saved to {filepath}")
        return str(filepath)
        
    except Exception as e:
        logger.error(f"Error saving content: {e}")
        return ""

# --- 8. Main Application ---
class BloggingAgent:
    def __init__(self):
        self.config = BloggingConfig()
        self.llm = ChatGroq(
            temperature=self.config.temperature,
            model_name=self.config.model_name,
            max_tokens=self.config.max_tokens
        )
        self.ui = UserInterface()
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the enhanced workflow graph."""
        workflow = StateGraph(BloggingState)
        
        # Add nodes
        workflow.add_node("fetch_topics", fetch_trending_topics_node)
        workflow.add_node("generate_titles", lambda state: generate_title_suggestions_node(state, self.llm))
        workflow.add_node("generate_outline", lambda state: generate_outline_node(state, self.llm))
        workflow.add_node("generate_content", lambda state: generate_content_node(state, self.llm))
        workflow.add_node("optimize_content", content_optimization_node)
        
        # Set entry point
        workflow.set_entry_point("fetch_topics")
        
        # Add edges
        workflow.add_edge("fetch_topics", "generate_titles")
        workflow.add_edge("generate_titles", "generate_outline")
        workflow.add_edge("generate_outline", "generate_content")
        workflow.add_edge("generate_content", "optimize_content")
        
        # Add conditional edge for regeneration
        workflow.add_conditional_edges(
            "optimize_content",
            decide_workflow_path,
            {
                "regenerate": "generate_content",
                "end": END
            }
        )
        
        return workflow.compile()
    
    def run(self):
        """Main execution method."""
        print("🚀 Welcome to the Enhanced AI Blogging Agent!")
        print("=" * 50)
        
        try:
            # Stage 1: Fetch topics
            logger.info("Starting topic fetching phase")
            initial_state = self.workflow.invoke({})
            
            if not initial_state.get('trending_topics'):
                print("❌ Could not fetch topics. Please check your internet connection and try again.")
                return
            
            # Stage 2: Topic selection
            self.ui.display_topics(initial_state['trending_topics'])
            
            try:
                choice = int(input("👉 Select a topic number: ")) - 1
                if choice < 0 or choice >= len(initial_state['trending_topics']):
                    raise IndexError
                selected_topic_data = initial_state['trending_topics'][choice]
                selected_topic = selected_topic_data['title']
            except (ValueError, IndexError):
                print("⚠️ Invalid selection. Using the first topic.")
                selected_topic_data = initial_state['trending_topics'][0]
                selected_topic = selected_topic_data['title']
            
            print(f"\n✅ Selected: \"{selected_topic}\"")
            
            # Stage 3: Get user preferences
            preferences = self.ui.get_user_preferences()
            
            # Stage 4: Content generation loop
            generation_state = {
                "selected_topic": selected_topic,
                "topic_metadata": selected_topic_data,
                "user_feedback": "",
                "generation_attempts": 0,
                "errors": [],
                **preferences
            }
            
            while True:
                print(f"\n🔄 Starting content generation (Attempt {generation_state.get('generation_attempts', 0) + 1})")
                
                # Generate content
                final_state = self.workflow.invoke(generation_state)
                
                # Display results
                self.ui.display_content_summary(final_state)
                
                # Get user feedback
                print("\n" + "=" * 40)
                print("Options:")
                print("- Type 'approve' to finish and save")
                print("- Type 'regenerate' to create new content")
                print("- Provide specific feedback for improvements")
                
                feedback = input("\n💭 Your feedback: ").strip()
                
                if feedback.lower() == 'approve':
                    # Save content
                    filepath = save_content_to_file(final_state)
                    print(f"\n🎉 Content approved and saved!")
                    if filepath:
                        print(f"📁 Saved to: {filepath}")
                    break
                
                elif final_state.get('generation_attempts', 0) >= self.config.max_generation_attempts:
                    print(f"\n⚠️ Maximum attempts ({self.config.max_generation_attempts}) reached.")
                    save_anyway = input("Save current version anyway? (y/n): ").strip().lower()
                    if save_anyway == 'y':
                        filepath = save_content_to_file(final_state)
                        if filepath:
                            print(f"📁 Saved to: {filepath}")
                    break
                
                else:
                    # Continue with feedback
                    generation_state = {
                        **final_state,
                        "user_feedback": feedback
                    }
                    print("\n🔄 Regenerating content with your feedback...")
        
        except KeyboardInterrupt:
            print("\n\n⚠️ Process interrupted by user.")
            logger.info("Process interrupted by user")
        
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            logger.error(f"Application error: {e}")
        
        finally:
            print("\n👋 Thank you for using the AI Blogging Agent!")

# --- 9. Entry Point ---
if __name__ == "__main__":
    agent = BloggingAgent()
    agent.run()