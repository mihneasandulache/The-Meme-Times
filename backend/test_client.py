#!/usr/bin/env python3
"""
Test client for the News Curation API
"""

import requests
import json
from typing import Dict, Any

class NewsAPIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def health_check(self) -> Dict[str, Any]:
        """Check if the API is running"""
        try:
            response = requests.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def curate_news(self, interests: list, age: int, city: str, country: str) -> Dict[str, Any]:
        """Request news curation"""
        payload = {
            "interests": interests,
            "age": age,
            "city": city,
            "country": country
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/curate-news",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "status_code": getattr(e.response, 'status_code', None)}

def main():
    """Test the API"""
    client = NewsAPIClient()
    
    # Test health check
    print("🔍 Testing health check...")
    health = client.health_check()
    print(f"Health check result: {health}")
    
    if "error" in health:
        print("❌ API is not running. Please start the server first.")
        return
    
    # Test news curation
    print("\n📰 Testing news curation...")
    
    # Example user profile
    test_profile = {
        "interests": ["Gaming", "Movies", "Technology"],
        "age": 25,
        "city": "Bucharest",
        "country": "Romania"
    }
    
    print(f"User profile: {json.dumps(test_profile, indent=2)}")
    
    result = client.curate_news(**test_profile)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        if "status_code" in result:
            print(f"Status code: {result['status_code']}")
    else:
        print("✅ Success! Retrieved articles:")
        articles = result.get("articles", [])
        
        for i, article in enumerate(articles, 1):
            print(f"\n--- Article {i} ---")
            print(f"Title: {article['title']}")
            print(f"Summary: {article['article_summary'][:100]}...")
            print(f"Source: {article['source_link']}")
            print(f"Photo: {article['photo_path']}")
        
        print(f"\nTotal articles retrieved: {len(articles)}")

# Example usage scenarios
def test_different_profiles():
    """Test with different user profiles"""
    client = NewsAPIClient()
    
    test_profiles = [
        {
            "name": "Teen Gamer",
            "profile": {
                "interests": ["Gaming", "Movies", "Social Media"],
                "age": 16,
                "city": "Bucharest",
                "country": "Romania"
            }
        },
        {
            "name": "Young Professional",
            "profile": {
                "interests": ["Technology", "Business", "Travel"],
                "age": 28,
                "city": "Cluj-Napoca",
                "country": "Romania"
            }
        },
        {
            "name": "Senior Citizen",
            "profile": {
                "interests": ["Health", "Politics", "Culture"],
                "age": 65,
                "city": "Timisoara",
                "country": "Romania"
            }
        }
    ]
    
    for test_case in test_profiles:
        print(f"\n{'='*50}")
        print(f"Testing profile: {test_case['name']}")
        print(f"{'='*50}")
        
        result = client.curate_news(**test_case['profile'])
        
        if "error" in result:
            print(f"❌ Error for {test_case['name']}: {result['error']}")
        else:
            articles = result.get("articles", [])
            print(f"✅ Retrieved {len(articles)} articles for {test_case['name']}")
            
            # Show first article as sample
            if articles:
                first_article = articles[0]
                print(f"Sample article: {first_article['title'][:50]}...")

if __name__ == "__main__":
    print("🧪 News Curation API Test Client")
    print("=" * 40)
    
    # Run basic test
    main()
    
    # Uncomment to test different profiles
    # print("\n" + "="*60)
    # print("TESTING DIFFERENT PROFILES")
    # print("="*60)
    # test_different_profiles()