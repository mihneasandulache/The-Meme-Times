# Test script
try:
    import google.generativeai as genai
    import google.cloud.aiplatform as aiplatform
    import requests
    print("✅ All packages installed successfully!")
except ImportError as e:
    print(f"❌ Missing package: {e}")