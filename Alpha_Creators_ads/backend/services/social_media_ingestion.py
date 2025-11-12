"""
Social media data ingestion service.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import httpx
from dataclasses import dataclass

from core.config import settings
from services.kafka_producer import KafkaProducer

logger = logging.getLogger(__name__)


@dataclass
class SocialMediaPost:
    """Social media post data structure"""
    platform: str
    post_id: str
    content: str
    author_id: str
    author_username: str
    posted_at: datetime
    engagement_count: int = 0
    likes_count: int = 0
    shares_count: int = 0
    comments_count: int = 0
    media_urls: List[str] = None
    hashtags: List[str] = None
    mentions: List[str] = None
    raw_data: Dict[str, Any] = None


class TwitterAPI:
    """Twitter API v2 integration"""
    
    def __init__(self):
        self.bearer_token = settings.TWITTER_BEARER_TOKEN
        self.base_url = "https://api.twitter.com/2"
        self.client = httpx.AsyncClient()
        
    async def get_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        return {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }
    
    async def search_tweets(self, query: str, max_results: int = 100) -> List[SocialMediaPost]:
        """Search for tweets"""
        if not self.bearer_token:
            logger.warning("Twitter Bearer Token not configured")
            return []
            
        try:
            headers = await self.get_headers()
            params = {
                "query": query,
                "max_results": max_results,
                "tweet.fields": "created_at,public_metrics,author_id,context_annotations",
                "user.fields": "username,name",
                "expansions": "author_id"
            }
            
            response = await self.client.get(
                f"{self.base_url}/tweets/search/recent",
                headers=headers,
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                return await self._parse_tweets(data)
            else:
                logger.error(f"Twitter API error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching tweets: {e}")
            return []
    
    async def _parse_tweets(self, data: Dict) -> List[SocialMediaPost]:
        """Parse Twitter API response"""
        posts = []
        tweets = data.get("data", [])
        users = {user["id"]: user for user in data.get("includes", {}).get("users", [])}
        
        for tweet in tweets:
            user = users.get(tweet["author_id"], {})
            
            post = SocialMediaPost(
                platform="twitter",
                post_id=tweet["id"],
                content=tweet["text"],
                author_id=tweet["author_id"],
                author_username=user.get("username", "unknown"),
                posted_at=datetime.fromisoformat(tweet["created_at"].replace("Z", "+00:00")),
                engagement_count=sum(tweet.get("public_metrics", {}).values()),
                likes_count=tweet.get("public_metrics", {}).get("like_count", 0),
                shares_count=tweet.get("public_metrics", {}).get("retweet_count", 0),
                comments_count=tweet.get("public_metrics", {}).get("reply_count", 0),
                hashtags=self._extract_hashtags(tweet["text"]),
                mentions=self._extract_mentions(tweet["text"]),
                raw_data=tweet
            )
            posts.append(post)
            
        return posts
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        import re
        return re.findall(r'#\w+', text)
    
    def _extract_mentions(self, text: str) -> List[str]:
        """Extract mentions from text"""
        import re
        return re.findall(r'@\w+', text)


class FacebookAPI:
    """Facebook Graph API integration"""
    
    def __init__(self):
        self.access_token = settings.FACEBOOK_ACCESS_TOKEN
        self.base_url = "https://graph.facebook.com/v18.0"
        self.client = httpx.AsyncClient()
    
    async def get_public_posts(self, keywords: List[str]) -> List[SocialMediaPost]:
        """Get public posts mentioning keywords"""
        if not self.access_token:
            logger.warning("Facebook Access Token not configured")
            return []
        
        # Note: Facebook Graph API has limited public post access
        # This is a simplified implementation
        posts = []
        
        try:
            for keyword in keywords:
                params = {
                    "q": keyword,
                    "type": "post",
                    "access_token": self.access_token,
                    "fields": "id,message,created_time,from,engagement"
                }
                
                response = await self.client.get(
                    f"{self.base_url}/search",
                    params=params
                )
                
                if response.status_code == 200:
                    data = response.json()
                    posts.extend(await self._parse_facebook_posts(data))
                    
        except Exception as e:
            logger.error(f"Error fetching Facebook posts: {e}")
            
        return posts
    
    async def _parse_facebook_posts(self, data: Dict) -> List[SocialMediaPost]:
        """Parse Facebook API response"""
        posts = []
        
        for item in data.get("data", []):
            if "message" in item:
                post = SocialMediaPost(
                    platform="facebook",
                    post_id=item["id"],
                    content=item["message"],
                    author_id=item.get("from", {}).get("id", "unknown"),
                    author_username=item.get("from", {}).get("name", "unknown"),
                    posted_at=datetime.fromisoformat(item["created_time"].replace("Z", "+00:00")),
                    engagement_count=item.get("engagement", {}).get("count", 0),
                    raw_data=item
                )
                posts.append(post)
                
        return posts


class SocialMediaIngestionService:
    """Main social media data ingestion service"""
    
    def __init__(self):
        self.twitter_api = TwitterAPI()
        self.facebook_api = FacebookAPI()
        self.kafka_producer = KafkaProducer()
        self.active_keywords = [
            "excited", "happy", "frustrated", "angry", "sad", "love", "hate",
            "buying", "shopping", "purchase", "deal", "sale", "discount",
            # Add more emotional and intent keywords
        ]
        
    async def start_ingestion(self):
        """Start continuous data ingestion"""
        logger.info("Starting social media data ingestion...")
        
        while True:
            try:
                # Collect from all platforms
                all_posts = []
                
                # Twitter
                for keyword in self.active_keywords[:5]:  # Limit to avoid rate limiting
                    twitter_posts = await self.twitter_api.search_tweets(
                        query=f"{keyword} -is:retweet lang:en",
                        max_results=100
                    )
                    all_posts.extend(twitter_posts)
                    
                # Facebook (limited public access)
                facebook_posts = await self.facebook_api.get_public_posts(
                    self.active_keywords[:3]
                )
                all_posts.extend(facebook_posts)
                
                # Send to Kafka for processing
                for post in all_posts:
                    await self.kafka_producer.send_message(
                        topic="social_media_posts",
                        message=self._serialize_post(post)
                    )
                
                logger.info(f"Collected {len(all_posts)} posts")
                
                # Wait before next collection cycle
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"Error in ingestion cycle: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    def _serialize_post(self, post: SocialMediaPost) -> Dict:
        """Serialize post for Kafka"""
        return {
            "platform": post.platform,
            "post_id": post.post_id,
            "content": post.content,
            "author_id": post.author_id,
            "author_username": post.author_username,
            "posted_at": post.posted_at.isoformat(),
            "engagement_count": post.engagement_count,
            "likes_count": post.likes_count,
            "shares_count": post.shares_count,
            "comments_count": post.comments_count,
            "media_urls": post.media_urls or [],
            "hashtags": post.hashtags or [],
            "mentions": post.mentions or [],
            "raw_data": post.raw_data or {},
            "ingested_at": datetime.utcnow().isoformat()
        }
    
    async def stop_ingestion(self):
        """Stop data ingestion"""
        logger.info("Stopping social media data ingestion...")
        await self.kafka_producer.close()


# Singleton instance
ingestion_service = SocialMediaIngestionService()
