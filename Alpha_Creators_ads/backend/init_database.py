"""
MongoDB Database Initialization Script for Alpha Creator Ads
Creates collections, indexes, and sample data
"""

from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
from datetime import datetime, timedelta
import os
from typing import Dict, Any

class DatabaseInitializer:
    def __init__(self, mongodb_url: str = "mongodb://localhost:27017", db_name: str = "alpha_creator_ads"):
        self.client = MongoClient(mongodb_url)
        self.db = self.client[db_name]
        
    def create_collections(self):
        """Create all required collections"""
        collections = [
            'users',
            'campaigns', 
            'ads',
            'analytics',
            'audience_segments',
            'ai_generations'
        ]
        
        for collection_name in collections:
            if collection_name not in self.db.list_collection_names():
                self.db.create_collection(collection_name)
                print(f"✅ Created collection: {collection_name}")
            else:
                print(f"📋 Collection already exists: {collection_name}")
                
    def create_indexes(self):
        """Create performance-critical indexes"""
        
        # Users collection indexes
        self.db.users.create_index("email", unique=True)
        self.db.users.create_index("username", unique=True) 
        self.db.users.create_index("createdAt")
        
        # Campaigns collection indexes
        self.db.campaigns.create_index([("userId", ASCENDING), ("status", ASCENDING)])
        self.db.campaigns.create_index("createdAt", direction=DESCENDING)
        self.db.campaigns.create_index("status")
        
        # Ads collection indexes
        self.db.ads.create_index([("campaignId", ASCENDING), ("status", ASCENDING)])
        self.db.ads.create_index([("userId", ASCENDING), ("aiGenerated", ASCENDING)])
        self.db.ads.create_index("createdAt", direction=DESCENDING)
        
        # Analytics collection indexes (time-series optimization)
        self.db.analytics.create_index([("campaignId", ASCENDING), ("timestamp", DESCENDING)])
        self.db.analytics.create_index("timestamp", direction=DESCENDING)
        self.db.analytics.create_index([("userId", ASCENDING), ("timestamp", DESCENDING)])
        
        # Audience segments indexes
        self.db.audience_segments.create_index([("userId", ASCENDING), ("createdAt", DESCENDING)])
        
        # AI generations indexes
        self.db.ai_generations.create_index([("userId", ASCENDING), ("createdAt", DESCENDING)])
        self.db.ai_generations.create_index("type")
        
        print("✅ All indexes created successfully")
        
    def create_sample_data(self):
        """Create sample data for testing"""
        
        # Sample user
        sample_user = {
            "email": "demo@alphaads.com",
            "username": "demo_user",
            "passwordHash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewbURSH3E3CXqzD2",  # "password123"
            "fullName": "Demo User",
            "avatar": "https://avatar.example.com/demo.jpg",
            "role": "user",
            "subscription": {
                "plan": "pro",
                "status": "active",
                "startDate": datetime.utcnow(),
                "endDate": datetime.utcnow() + timedelta(days=30),
                "features": ["ai_generation", "analytics", "multi_platform"]
            },
            "preferences": {
                "theme": "light",
                "language": "en",
                "notifications": {
                    "email": True,
                    "push": True,
                    "sms": False
                },
                "defaultCurrency": "USD"
            },
            "apiUsage": {
                "adsGenerated": 45,
                "apiCallsThisMonth": 1250,
                "quotaLimit": 5000
            },
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "lastLogin": datetime.utcnow(),
            "isVerified": True,
            "isActive": True
        }
        
        # Insert sample user if not exists
        if not self.db.users.find_one({"email": "demo@alphaads.com"}):
            user_result = self.db.users.insert_one(sample_user)
            user_id = user_result.inserted_id
            print("✅ Created sample user")
        else:
            user_id = self.db.users.find_one({"email": "demo@alphaads.com"})["_id"]
            print("📋 Sample user already exists")
            
        # Sample campaign
        sample_campaign = {
            "userId": user_id,
            "name": "Summer Product Launch",
            "description": "Promoting our new summer collection to young professionals",
            "status": "active",
            "objective": "conversions",
            "budget": {
                "total": 5000.00,
                "spent": 1250.75,
                "currency": "USD",
                "dailyLimit": 200.00
            },
            "targeting": {
                "demographics": {
                    "ageRange": {"min": 25, "max": 45},
                    "gender": ["all"],
                    "locations": ["United States", "Canada"],
                    "languages": ["en"]
                },
                "interests": ["technology", "fashion", "lifestyle"],
                "behaviors": ["online_shopper", "mobile_user"],
                "customAudiences": []
            },
            "schedule": {
                "startDate": datetime.utcnow() - timedelta(days=7),
                "endDate": datetime.utcnow() + timedelta(days=23),
                "timezone": "UTC",
                "dayParting": {
                    "monday": ["09:00-18:00"],
                    "tuesday": ["09:00-18:00"],
                    "wednesday": ["09:00-18:00"],
                    "thursday": ["09:00-18:00"],
                    "friday": ["09:00-18:00"]
                }
            },
            "platforms": ["google", "facebook", "instagram"],
            "ads": [],
            "performance": {
                "impressions": 125000,
                "clicks": 3750,
                "conversions": 187,
                "ctr": 3.0,
                "cpc": 0.33,
                "roas": 4.2,
                "lastUpdated": datetime.utcnow()
            },
            "createdAt": datetime.utcnow() - timedelta(days=7),
            "updatedAt": datetime.utcnow()
        }
        
        # Insert sample campaign if not exists
        if not self.db.campaigns.find_one({"name": "Summer Product Launch"}):
            campaign_result = self.db.campaigns.insert_one(sample_campaign)
            campaign_id = campaign_result.inserted_id
            print("✅ Created sample campaign")
        else:
            campaign_id = self.db.campaigns.find_one({"name": "Summer Product Launch"})["_id"]
            print("📋 Sample campaign already exists")
            
        # Sample ad
        sample_ad = {
            "campaignId": campaign_id,
            "userId": user_id,
            "type": "text",
            "content": {
                "headline": "Transform Your Summer Style",
                "description": "Discover our exclusive summer collection with 30% off for early birds. Premium quality, unbeatable prices.",
                "cta": "Shop Now",
                "body": "Don't miss out on the hottest trends this summer. Limited time offer!",
                "images": [
                    "https://images.example.com/summer-collection-1.jpg",
                    "https://images.example.com/summer-collection-2.jpg"
                ],
                "videos": []
            },
            "aiGenerated": True,
            "generationParams": {
                "model": "gpt-4",
                "prompt": "Create an engaging ad for summer fashion collection targeting young professionals",
                "emotionalTone": "exciting",
                "targetAudience": "young professionals",
                "productCategory": "fashion"
            },
            "status": "active",
            "platform": "facebook",
            "performance": {
                "impressions": 45000,
                "clicks": 1350,
                "conversions": 67,
                "engagement": 2250,
                "spend": 445.50
            },
            "abTesting": {
                "isTestAd": True,
                "testGroup": "A",
                "winnerDeclared": False
            },
            "createdAt": datetime.utcnow() - timedelta(days=5),
            "updatedAt": datetime.utcnow(),
            "publishedAt": datetime.utcnow() - timedelta(days=5)
        }
        
        # Insert sample ad if not exists
        if not self.db.ads.find_one({"content.headline": "Transform Your Summer Style"}):
            self.db.ads.insert_one(sample_ad)
            print("✅ Created sample ad")
        else:
            print("📋 Sample ad already exists")
            
        print("✅ Sample data setup complete")
        
    def initialize(self):
        """Run complete database initialization"""
        print("🚀 Initializing Alpha Creator Ads Database...")
        print("=" * 50)
        
        self.create_collections()
        print()
        self.create_indexes()
        print()
        self.create_sample_data()
        print()
        print("🎉 Database initialization complete!")
        print("=" * 50)
        
    def get_stats(self):
        """Get database statistics"""
        stats = {
            "users": self.db.users.count_documents({}),
            "campaigns": self.db.campaigns.count_documents({}),
            "ads": self.db.ads.count_documents({}),
            "analytics": self.db.analytics.count_documents({}),
            "audience_segments": self.db.audience_segments.count_documents({}),
            "ai_generations": self.db.ai_generations.count_documents({})
        }
        
        print("📊 Database Statistics:")
        for collection, count in stats.items():
            print(f"   {collection}: {count} documents")
            
        return stats

if __name__ == "__main__":
    # Initialize database
    db_init = DatabaseInitializer()
    db_init.initialize()
    db_init.get_stats()