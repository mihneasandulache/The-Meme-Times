import json
import requests
import google.generativeai as genai
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict
import base64
import os
from typing import Dict, List, Any
import time

class NewsMemeGenerator:
    def __init__(self, gemini_api_key: str, google_cloud_project_id: str, 
                 google_cloud_location: str = "us-central1"):
        """
        Initialize the NewsMemeGenerator with API credentials.
        
        Args:
            gemini_api_key: Your Gemini API key
            google_cloud_project_id: Your Google Cloud project ID
            google_cloud_location: Google Cloud location for Imagen
        """
        # Configure Gemini
        genai.configure(api_key=gemini_api_key)
        
        # Initialize Vertex AI for Imagen
        aiplatform.init(project=google_cloud_project_id, location=google_cloud_location)
        
        self.project_id = google_cloud_project_id
        self.location = google_cloud_location
        
        # Load prompts
        self.news_crawl_prompt = self._load_news_crawl_prompt()
        self.meme_generation_prompt = self._load_meme_generation_prompt()
    
    def _load_news_crawl_prompt(self) -> str:
        """Load the news crawl prompt template."""
        return """# Senior Journalist News Curation Assistant

## Role and Expertise

You are a senior journalist with expertise in identifying trending and relevant news across all fields. Your specialty is matching current events to specific audience profiles based on demographics and interests.

## Task Overview

Analyze the provided client profile and curate 5 highly relevant news articles that align with their age, location, and interests. Use web search capabilities to find the most current and trending stories.

## Requirements

### Research Process

- Search the internet for the latest news relevant to the client's profile
- Prioritize trending stories from the past 7 days
- Consider age-appropriate content for the specified demographic
- Factor in geographic relevance (local and international news)
- Match articles to stated interests while introducing complementary topics

### Content Quality Standards

- Select articles from reputable news sources
- Ensure all links are functional and accessible
- Verify author attribution when available
- Prioritize original reporting over aggregated content

### Output Specifications

- Return ONLY valid JSON format
- Include exactly 5 articles
- Each article summary must be 2-4 sentences
- Provide working source URLs which should be the exact URL from where you extracted the article
- Include author names when available
- Use only english even if the article is in any other language

## Output Format
```json
[
  {
    "article_title": "string",
    "article_summary": "string (2-4 sentences)",
    "source": "string (working URL)",
    "author_name": "string"
  }
]
```

## Processing Guidelines

1. **Age Consideration**: Ensure content appropriateness for the specified age group
2. **Geographic Relevance**: Include mix of local (Romanian/Bucharest) and international news
3. **Interest Matching**: Prioritize articles that align with stated interests
4. **Trend Analysis**: Focus on current trending topics within relevant categories
5. **Source Diversity**: Select articles from varied, credible news sources

## Output Requirements

- Respond with JSON array only
- No additional text or explanation
- Ensure all URLs are functional
- Verify article summaries are concise and informative

---

## User Profile

{user_profile}"""

    def _load_meme_generation_prompt(self) -> str:
        """Load the meme generation prompt template."""
        return """# Visual Meme Generation Prompt for Google Generative Media

## Objective

Create a hilarious, text-free meme image based on the provided news article that uses pure visual comedy and situational humor to capture the essence of the story in an entertaining way.

## Visual Style Guidelines

- **Format**: Single impactful visual scene without any text overlay
- **Layout**: Full visual composition focused on comedic storytelling
- **Image Quality**: High contrast, vibrant colors, cartoon-like or photorealistic style
- **Aspect Ratio**: Square (1:1) for optimal social media sharing
- **Clarity**: Crystal clear visual narrative that doesn't require text explanation

## Content Requirements

### Visual Storytelling Elements

- **Pure Visual Comedy**: Use facial expressions, body language, and situational humor
- **Exaggerated Reactions**: Over-the-top expressions and poses for maximum comedic impact
- **Visual Metaphors**: Creative representations of the article's main concept
- **Relatable Scenarios**: Universal situations people can instantly understand
- **Character Expressions**: Shocked, confused, excited, or frustrated faces as appropriate

### Scene Composition

- Create a single, powerful visual moment that encapsulates the article
- Use cartoon-style characters or anthropomorphic animals for enhanced humor
- Include visual props, settings, or scenarios that relate to the article topic
- Focus on reaction shots, before/after comparisons, or absurd situations
- Emphasize physical comedy and visual gags

### Humor Techniques

- **Exaggeration**: Amplify emotions and reactions beyond realistic proportions
- **Absurdist Elements**: Add unexpected or surreal visual elements
- **Visual Irony**: Show contradictions or unexpected outcomes through imagery
- **Slapstick Comedy**: Physical humor and comedic mishaps
- **Anthropomorphism**: Give human characteristics to objects or animals related to the topic

## Technical Specifications

- **Resolution**: High quality suitable for social media sharing
- **Color Profile**: RGB, vibrant and eye-catching colors
- **Visual Impact**: Strong visual contrast and dynamic composition
- **File Optimization**: Suitable for web sharing and mobile viewing
- **No Text**: Absolutely no written words, letters, or text overlays

## Creative Guidelines

1. **Deep Article Analysis**: Extract the most specific and unique details from the article
2. **Story Identification**: Find the narrative arc within the news story (what happened, to whom, and what was the result)
3. **Comedy Amplification**: Take the real events and push them to hilariously absurd extremes
4. **Character Development**: Create a visual protagonist who experiences the article's events in an exaggerated way
5. **Specific Scene Creation**: Design a scene that someone familiar with the article would immediately recognize
6. **Fun Factor Maximization**: Prioritize entertainment value and laugh-out-loud moments
7. **Story Completion**: Ensure the visual tells a complete, satisfying story from start to finish

## Visual Story Examples Based on Article Types

- **Tech Malfunction**: Show a character's escalating panic as their device fails in increasingly ridiculous ways, mirroring the specific tech issue from the article
- **Sports Upset**: Depict a character's emotional rollercoaster from confidence to shock, specifically reflecting the teams/players mentioned in the article
- **Weather Event**: Create a character's journey through the exact weather phenomenon described, with absurdly exaggerated preparations or reactions
- **Gaming Release**: Show a gamer's transformation from excitement to the specific reaction mentioned in gaming news (bugs, delays, features)
- **Movie/Entertainment**: Visualize a fan's emotional journey through the specific plot twist, casting news, or entertainment development from the article

## Story-Driven Requirements

- **Narrative Clarity**: The visual story should be immediately understandable and engaging
- **Specific Details**: Include visual references that tie directly to article specifics (locations, people, objects, events)
- **Entertainment Priority**: Focus on creating the most fun, engaging, and shareable visual story possible
- **Article Authenticity**: Stay true to the actual events while making them hilariously entertaining

---

## Article Input

{article_json}"""

    def test_gemini_connection(self) -> bool:
        """Test if Gemini API is working correctly."""
        try:
            print("🔍 DEBUG: Testing basic Gemini connection...")
            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            
            response = model.generate_content("Say 'Hello, I am working correctly!'")
            print(f"✅ DEBUG: Basic Gemini test response: {response.text}")
            return True
            
        except Exception as e:
            print(f"❌ DEBUG: Basic Gemini test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_gemini_with_tools(self) -> bool:
        """Test if Gemini API with tools is working correctly."""
        try:
            print("🔍 DEBUG: Testing Gemini with search tools...")
            model = genai.GenerativeModel(
                model_name="gemini-2.0-flash-exp",
                tools='google_search_retrieval'
            )
            
            response = model.generate_content("What is the current weather in London? Just give me a brief answer.")
            print(f"✅ DEBUG: Gemini with tools test response: {response.text}")
            return True
            
        except Exception as e:
            print(f"❌ DEBUG: Gemini with tools test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def curate_news(self, user_profile: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Use Gemini API with grounding to curate news articles based on user profile.
        
        Args:
            user_profile: Dictionary containing age, city, country, and interests
            
        Returns:
            List of curated news articles
        """
        print("🔍 DEBUG: Starting news curation...")
        print(f"🔍 DEBUG: User profile: {user_profile}")
        
        try:
            # Configure the model with grounding
            print("🔍 DEBUG: Configuring Gemini model...")
            model = genai.GenerativeModel(
                model_name="gemini-2.0-flash-exp",
                tools='google_search_retrieval'  # Enable grounding with Google Search
            )
            print("✅ DEBUG: Model configured successfully")
            
            # Format the prompt with user profile
            prompt = self.news_crawl_prompt.format(
                user_profile=json.dumps(user_profile, indent=2)
            )
            print("🔍 DEBUG: Formatted prompt length:", len(prompt))
            print("🔍 DEBUG: First 500 chars of prompt:", prompt[:500])
            
            # Generate content with grounding
            print("🔍 DEBUG: Sending request to Gemini...")
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=4000,
                )
            )
            print("✅ DEBUG: Received response from Gemini")
            
            # Debug the raw response
            print("🔍 DEBUG: Raw response type:", type(response))
            print("🔍 DEBUG: Response attributes:", dir(response))
            
            # Check if response has text
            if hasattr(response, 'text'):
                print("🔍 DEBUG: Response text length:", len(response.text))
                print("🔍 DEBUG: First 1000 chars of response:", response.text[:1000])
                print("🔍 DEBUG: Last 500 chars of response:", response.text[-500:])
            else:
                print("❌ DEBUG: Response has no 'text' attribute")
                if hasattr(response, 'parts'):
                    print("🔍 DEBUG: Response parts:", response.parts)
                if hasattr(response, 'candidates'):
                    print("🔍 DEBUG: Response candidates:", response.candidates)
                return []
            
            # Check for safety filters or other issues
            if hasattr(response, 'prompt_feedback'):
                print("🔍 DEBUG: Prompt feedback:", response.prompt_feedback)
            
            # Parse the JSON response
            try:
                print("🔍 DEBUG: Attempting to parse JSON directly...")
                articles = json.loads(response.text)
                print("✅ DEBUG: Successfully parsed JSON directly")
                print("🔍 DEBUG: Number of articles found:", len(articles))
                return articles
                
            except json.JSONDecodeError as json_error:
                print(f"❌ DEBUG: JSON decode error: {json_error}")
                print("🔍 DEBUG: Attempting to extract JSON from markdown...")
                
                # Try to extract JSON from the response if it's wrapped in markdown
                text = response.text.strip()
                print("🔍 DEBUG: Stripped text length:", len(text))
                print("🔍 DEBUG: Text starts with:", text[:100])
                print("🔍 DEBUG: Text ends with:", text[-100:])
                
                if text.startswith('```json'):
                    print("🔍 DEBUG: Found JSON markdown wrapper")
                    text = text[7:]
                if text.endswith('```'):
                    text = text[:-3]
                
                print("🔍 DEBUG: Cleaned text for JSON parsing:")
                print("🔍 DEBUG: Cleaned text length:", len(text))
                print("🔍 DEBUG: First 500 chars:", text[:500])
                
                try:
                    articles = json.loads(text.strip())
                    print("✅ DEBUG: Successfully parsed JSON after cleaning")
                    print("🔍 DEBUG: Number of articles found:", len(articles))
                    return articles
                except json.JSONDecodeError as json_error2:
                    print(f"❌ DEBUG: JSON decode error after cleaning: {json_error2}")
                    print("🔍 DEBUG: Attempting line-by-line analysis...")
                    
                    # Try to find where the JSON might be malformed
                    lines = text.split('\n')
                    for i, line in enumerate(lines[:20]):  # Check first 20 lines
                        print(f"🔍 DEBUG: Line {i}: {repr(line)}")
                    
                    return []
                
        except Exception as e:
            print(f"❌ ERROR curating news: {e}")
            print(f"❌ ERROR type: {type(e)}")
            import traceback
            print("❌ ERROR traceback:")
            traceback.print_exc()
            return []

    def generate_meme(self, article: Dict[str, str], output_path: str = "meme.png") -> str:
        """
        Generate a meme image using Imagen based on the article.
        
        Args:
            article: Dictionary containing article information
            output_path: Path to save the generated image
            
        Returns:
            Path to the generated image file
        """
        try:
            # Format the meme generation prompt
            article_json = json.dumps(article, indent=2)
            meme_prompt = self.meme_generation_prompt.format(article_json=article_json)
            
            # Use Gemini to create a concise image generation prompt
            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            
            simplification_prompt = f"""
            Based on this detailed meme generation prompt and article, create a concise, specific image generation prompt (max 150 words) that focuses on the key visual elements for creating a hilarious meme image:

            {meme_prompt}

            Return only the simplified image generation prompt, nothing else.
            """
            
            response = model.generate_content(simplification_prompt)
            simplified_prompt = response.text.strip()
            
            print(f"Generated image prompt: {simplified_prompt}")
            
            # Generate image using Imagen via Vertex AI
            endpoint = aiplatform.Endpoint(
                endpoint_name=f"projects/{self.project_id}/locations/{self.location}/endpoints/imagen"
            )
            
            # Alternative approach using the Vertex AI Imagen API directly
            imagen_url = f"https://{self.location}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/imagen-3.0-generate-001:predict"
            
            # You'll need to implement OAuth2 authentication here
            # For now, using a simplified approach with the aiplatform library
            
            # Using the aiplatform predict method
            instances = [
                {
                    "prompt": simplified_prompt,
                    "sampleCount": 1,
                    "aspectRatio": "1:1",
                    "safetyFilterLevel": "block_some",
                    "personGeneration": "allow_adult"
                }
            ]
            
            # This is a placeholder - you'll need to implement the actual Imagen API call
            # based on your specific setup and authentication method
            
            print("Note: Imagen API call needs to be implemented with proper authentication")
            print("Please refer to Google Cloud documentation for Imagen API integration")
            
            return output_path
            
        except Exception as e:
            print(f"Error generating meme: {e}")
            return ""

    def run_complete_pipeline(self, user_profile: Dict[str, Any], output_dir: str = "./memes/") -> Dict[str, Any]:
        """
        Run the complete pipeline: curate news and generate memes.
        
        Args:
            user_profile: User profile for news curation
            output_dir: Directory to save generated memes
            
        Returns:
            Dictionary containing articles and meme paths
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Step 1: Curate news articles
        print("Curating news articles...")
        articles = self.curate_news(user_profile)
        
        if not articles:
            print("No articles found")
            return {"articles": [], "memes": []}
        
        print(f"Found {len(articles)} articles")
        
        # Step 2: Generate memes for each article
        results = {
            "articles": articles,
            "memes": []
        }
        
        for i, article in enumerate(articles):
            print(f"Generating meme for article {i+1}: {article.get('article_title', 'Untitled')}")
            
            meme_path = os.path.join(output_dir, f"meme_{i+1}.png")
            generated_path = self.generate_meme(article, meme_path)
            
            results["memes"].append({
                "article_index": i,
                "article_title": article.get("article_title", ""),
                "meme_path": generated_path
            })
            
            # Add a small delay to avoid rate limiting
            time.sleep(2)
        
        return results


# Example usage
def main():
    print("🚀 Starting News Meme Generator...")
    
    # Configuration
    GEMINI_API_KEY = "your_gemini_api_key_here"
    GOOGLE_CLOUD_PROJECT_ID = "your_google_cloud_project_id_here"
    GOOGLE_CLOUD_LOCATION = "us-central1"
    
    # Debug configuration
    print("🔍 DEBUG: Configuration check...")
    print(f"🔍 DEBUG: API Key set: {'Yes' if GEMINI_API_KEY != 'your_gemini_api_key_here' else 'NO - PLEASE SET YOUR API KEY'}")
    print(f"🔍 DEBUG: Project ID set: {'Yes' if GOOGLE_CLOUD_PROJECT_ID != 'your_google_cloud_project_id_here' else 'NO - USING PLACEHOLDER'}")
    print(f"🔍 DEBUG: Location: {GOOGLE_CLOUD_LOCATION}")
    
    if GEMINI_API_KEY == "your_gemini_api_key_here":
        print("❌ ERROR: You need to set your actual Gemini API key!")
        print("Get your API key from: https://makersuite.google.com/app/apikey")
        return
    
    # Test API key format
    if not GEMINI_API_KEY.startswith('AI'):
        print("⚠️  WARNING: Gemini API keys usually start with 'AI'. Double-check your key.")
    
    # Initialize the generator
    try:
        print("🔍 DEBUG: Initializing NewsMemeGenerator...")
        generator = NewsMemeGenerator(
            gemini_api_key=GEMINI_API_KEY,
            google_cloud_project_id=GOOGLE_CLOUD_PROJECT_ID,
            google_cloud_location=GOOGLE_CLOUD_LOCATION
        )
        print("✅ DEBUG: Generator initialized successfully")
    except Exception as e:
        print(f"❌ ERROR initializing generator: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test basic connectivity first
    print("🔍 DEBUG: Running connectivity tests...")
    
    if not generator.test_gemini_connection():
        print("❌ ERROR: Basic Gemini connection failed. Check your API key.")
        return
        
    if not generator.test_gemini_with_tools():
        print("❌ ERROR: Gemini with tools failed. This might be a permissions issue.")
        print("💡 TIP: Make sure your API key has access to search/grounding features.")
        # Continue anyway to see what happens
    
    # Example user profile
    user_profile = {
        "age": 15,
        "city": "Bucharest",
        "country": "Romania",
        "interests": ["Gaming", "Movies", "Partying"]
    }
    print(f"🔍 DEBUG: Using user profile: {user_profile}")
    
    # Test just the news curation first
    print("🔍 DEBUG: Testing news curation only...")
    articles = generator.curate_news(user_profile)
    
    if articles:
        print(f"✅ DEBUG: Successfully got {len(articles)} articles")
        for i, article in enumerate(articles):
            print(f"🔍 DEBUG: Article {i+1}: {article}")
    else:
        print("❌ DEBUG: No articles returned - check the detailed debug output above")
        return
    
    # If news curation works, run the complete pipeline
    print("🔍 DEBUG: Running complete pipeline...")
    results = generator.run_complete_pipeline(user_profile)
    
    # Print results
    print("\n" + "="*50)
    print("PIPELINE RESULTS")
    print("="*50)
    
    print(f"\nCurated {len(results['articles'])} articles:")
    for i, article in enumerate(results['articles']):
        print(f"\n{i+1}. {article.get('article_title', 'Untitled')}")
        print(f"   Summary: {article.get('article_summary', 'No summary')}")
        print(f"   Source: {article.get('source', 'No source')}")
        print(f"   Author: {article.get('author_name', 'Unknown')}")
    
    print(f"\nGenerated {len(results['memes'])} memes:")
    for meme in results['memes']:
        print(f"- {meme['article_title']}: {meme['meme_path']}")


if __name__ == "__main__":
    main()