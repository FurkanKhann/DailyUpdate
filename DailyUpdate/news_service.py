# news_service.py
import requests
import os
from datetime import datetime, timedelta

class NewsService:
    def __init__(self):
        self.api_key = os.environ.get('NEWS_API_KEY')
        self.base_url = "https://newsapi.org/v2/everything"
    
    def fetch_ai_news(self):
        """Fetch latest AI-related news articles"""
        try:
            if not self.api_key:
                print("⚠️  News API key not configured, using fallback news")
                return self.get_fallback_news()
            
            params = {
                'q': 'artificial intelligence OR machine learning OR AI OR deep learning OR neural networks',
                'language': 'en',
                'sortBy': 'publishedAt',
                'from': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
                'pageSize': 10,
                'apiKey': self.api_key
            }
            
            print("📡 Fetching AI news from API...")
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('articles', [])
            
            news_data = []
            for article in articles:
                if (article.get('title') and 
                    article.get('url') and 
                    article.get('description') and
                    article.get('title') != '[Removed]'):  # Filter removed articles
                    
                    news_data.append({
                        'title': article['title'],
                        'url': article['url'],
                        'description': self._truncate_description(article['description'])
                    })
            
            print(f"✅ Fetched {len(news_data)} articles from API")
            return news_data[:5]  # Return top 5 articles
        
        except requests.RequestException as e:
            print(f"❌ Error fetching news from API: {e}")
            return self.get_fallback_news()
        except Exception as e:
            print(f"❌ Unexpected error in news fetching: {e}")
            return self.get_fallback_news()
    
    def _truncate_description(self, description):
        """Truncate description to reasonable length"""
        if len(description) > 250:
            return description[:247] + '...'
        return description
    
    def get_fallback_news(self):
        """Fallback news in case API fails"""
        return [
            {
                'title': 'Latest Developments in Artificial Intelligence Research',
                'url': 'https://www.nature.com/subjects/machine-learning',
                'description': 'Stay updated with cutting-edge research in AI and machine learning from leading scientific journals and institutions worldwide.'
            },
            {
                'title': 'AI Industry Trends and Market Analysis',
                'url': 'https://www.mckinsey.com/capabilities/quantumblack/our-insights',
                'description': 'Comprehensive analysis of AI adoption trends, market opportunities, and business transformation strategies across industries.'
            },
            {
                'title': 'OpenAI and AI Safety Research Updates',
                'url': 'https://openai.com/research',
                'description': 'Latest research publications and safety developments from OpenAI and other leading AI research organizations.'
            },
            {
                'title': 'Machine Learning Tools and Frameworks',
                'url': 'https://github.com/topics/machine-learning',
                'description': 'Discover new tools, libraries, and frameworks that are shaping the future of machine learning development.'
            },
            {
                'title': 'AI Ethics and Responsible AI Development',
                'url': 'https://www.partnershiponai.org',
                'description': 'Important discussions on AI ethics, bias mitigation, and responsible development practices in artificial intelligence.'
            }
        ]

    def test_api_connection(self):
        """Test if the News API is working"""
        try:
            if not self.api_key:
                return False, "API key not configured"
            
            params = {
                'q': 'test',
                'pageSize': 1,
                'apiKey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=5)
            response.raise_for_status()
            
            return True, "API connection successful"
        
        except Exception as e:
            return False, f"API connection failed: {e}"
