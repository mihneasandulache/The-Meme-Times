from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import json
import os
from pathlib import Path
import uuid
import asyncio
from google import genai
from google.genai.types import (
    GenerateContentConfig,
    GoogleSearch,
    HttpOptions,
    Tool,
)
from google.cloud import aiplatform
import requests
from PIL import Image
import io

app = FastAPI(title="News Curation API", version="1.0.0")

# Pydantic models
class UserProfile(BaseModel):
    interests: List[str]
    age: int
    city: str
    country: str

class Article(BaseModel):
    title: str
    article_summary: str
    source_link: str
    photo_path: str

class NewsResponse(BaseModel):
    articles: List[Article]

# Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyAFoRgBVbN-c9ClGWAML5iT9uUxqE2ytXM")
GOOGLE_CLOUD_KEY = os.getenv("GOOGLE_CLOUD_KEY", "AIzaSyDW6fAyTj3B3TxJ6zU9BACkbrT-JnBgmf8")
PROJECT_ID = "emea-students25otp-2652"
LOCATION = "europe-west1"
IMAGES_DIR = Path("generated_images")
IMAGES_DIR.mkdir(exist_ok=True)

# Initialize Google AI client
client = genai.Client(
    http_options=HttpOptions(api_version="v1"),
    project=PROJECT_ID,
    location=LOCATION,
    vertexai=True
)

# News curation prompt template
NEWS_PROMPT_TEMPLATE = """
# Senior Journalist News Curation Assistant

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
  {{
    "article_title": "string",
    "article_summary": "string (2-4 sentences)",
    "source": "string (working URL)",
    "author_name": "string"
  }}
]
```

## Processing Guidelines
1. **Age Consideration**: Ensure content appropriateness for the specified age group
2. **Geographic Relevance**: Include mix of local and international news
3. **Interest Matching**: Prioritize articles that align with stated interests
4. **Trend Analysis**: Focus on current trending topics within relevant categories
5. **Source Diversity**: Select articles from varied, credible news sources

## User Profile
```json
{{
  "age": {age},
  "city": "{city}",
  "country": "{country}",
  "interests": {interests}
}}
```

Respond with JSON array only. No additional text or explanation.
"""

# Meme generation prompt template
MEME_PROMPT_TEMPLATE = """
Create a HILARIOUS visual that will make people burst out laughing. Based on this news article, make the most ridiculous, absurd, laugh-out-loud cartoon scene possible.

**ABSOLUTELY NO TEXT, WORDS, LETTERS, OR WRITING OF ANY KIND!**

## Make it RIDICULOUSLY FUNNY:
- **Absolutely absurd and over-the-top** - push everything to extreme comedy
- **Slapstick visual humor** - physical comedy that's impossible to not laugh at
- **Wildly exaggerated reactions** - characters with impossibly shocked/confused/panicked faces
- **Ridiculous situations** - turn the article into the most absurd scenario possible
- **Visual gags** - include funny background details and sight gags
- **Cartoon physics** - defy reality for maximum comedy (characters flying, objects exploding, etc.)

## Story Elements:
- Take the main event from the article and make it ABSURDLY FUNNY
- Show characters in the most ridiculous predicament possible
- Use the most over-the-top reactions humanly possible
- Include hilarious consequences and chain reactions
- Make it so funny that just looking at it makes you laugh

## Style:
Cartoon illustration, vibrant colors, MAXIMUM COMEDY, slapstick humor, absurd visual gags, impossibly exaggerated expressions, ridiculous situations, laugh-out-loud funny, **ZERO TEXT - NO WORDS ANYWHERE - PURE VISUAL COMEDY ONLY**

## Article:
Title: {title}
Summary: {summary}
"""

async def generate_news_articles(user_profile: UserProfile) -> List[dict]:
    """Generate curated news articles using Gemini model"""
    try:
        prompt = NEWS_PROMPT_TEMPLATE.format(
            age=user_profile.age,
            city=user_profile.city,
            country=user_profile.country,
            interests=json.dumps(user_profile.interests)
        )
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=GenerateContentConfig(
                tools=[Tool(google_search=GoogleSearch())],
            ),
        )
        
        # Parse JSON response
        articles_json = response.text.strip()
        # Remove any markdown formatting if present
        if articles_json.startswith("```json"):
            articles_json = articles_json.split("```json")[1].split("```")[0].strip()
        elif articles_json.startswith("```"):
            articles_json = articles_json.split("```")[1].split("```")[0].strip()
            
        articles = json.loads(articles_json)
        return articles
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating articles: {str(e)}")

async def generate_meme_image(article: dict) -> str:
    """Generate meme image for an article using Imagen"""
    try:
        # Initialize Vertex AI
        aiplatform.init(project=PROJECT_ID, location=LOCATION)
        
        prompt = MEME_PROMPT_TEMPLATE.format(
            title=article.get("article_title", ""),
            summary=article.get("article_summary", "")
        )
        
        # Generate image using Imagen (this is a simplified example)
        # You'll need to implement the actual Imagen API call based on your setup
        
        # For now, creating a placeholder image path
        image_filename = f"meme_{uuid.uuid4().hex}.png"
        image_path = IMAGES_DIR / image_filename
        
        # TODO: Replace this with actual Imagen API call
        # This is a placeholder - you'll need to implement the actual image generation
        # using Google's Imagen API through Vertex AI
        
        # Create a simple placeholder image for now
        placeholder_img = Image.new('RGB', (512, 512), color='lightblue')
        placeholder_img.save(image_path)
        
        return str(image_path)
        
    except Exception as e:
        print(f"Error generating meme image: {str(e)}")
        # Return a default image path or create a simple placeholder
        default_image = IMAGES_DIR / "default_meme.png"
        if not default_image.exists():
            placeholder_img = Image.new('RGB', (512, 512), color='gray')
            placeholder_img.save(default_image)
        return str(default_image)

@app.get("/")
async def root():
    return {"message": "News Curation API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "news-curation-api"}

@app.post("/curate-news", response_model=NewsResponse)
async def curate_news(user_profile: UserProfile):
    """
    Curate personalized news articles based on user profile
    """
    try:
        # Validate input
        if not user_profile.interests:
            raise HTTPException(status_code=400, detail="At least one interest is required")
        
        if user_profile.age < 1 or user_profile.age > 120:
            raise HTTPException(status_code=400, detail="Age must be between 1 and 120")
        
        # Generate news articles
        raw_articles = await generate_news_articles(user_profile)
        
        # Process articles and generate meme images
        processed_articles = []
        
        for article_data in raw_articles:
            try:
                # Generate meme image for this article
                photo_path = await generate_meme_image(article_data)
                
                # Create Article object
                article = Article(
                    title=article_data.get("article_title", "No Title"),
                    article_summary=article_data.get("article_summary", "No Summary"),
                    source_link=article_data.get("source", ""),
                    photo_path=photo_path
                )
                
                processed_articles.append(article)
                
            except Exception as e:
                print(f"Error processing article: {str(e)}")
                continue
        
        if not processed_articles:
            raise HTTPException(status_code=500, detail="No articles could be processed")
        
        return NewsResponse(articles=processed_articles)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/images/{image_name}")
async def get_image(image_name: str):
    """Serve generated meme images"""
    from fastapi.responses import FileResponse
    
    image_path = IMAGES_DIR / image_name
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(image_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)