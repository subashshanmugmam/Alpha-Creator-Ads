"""
Mock Database System for Development
Simulates MongoDB operations with in-memory storage
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import uuid
# from bson import ObjectId  # Not needed for mock

class MockObjectId:
    """Mock ObjectId for development"""
    def __init__(self, oid: str = None):
        self.oid = oid or str(uuid.uuid4()).replace('-', '')[:24]
    
    def __str__(self):
        return self.oid
    
    def __repr__(self):
        return f"ObjectId('{self.oid}')"

class MockDatabase:
    """Mock database for development testing"""
    
    def __init__(self):
        self.collections = {
            'users': [],
            'campaigns': [],
            'ads': [],
            'analytics': [],
            'ai_generations': [],
            'campaign_optimizations': []
        }
        self._init_sample_data()
    
    def _init_sample_data(self):
        """Initialize with sample data"""
        # Sample user
        user_id = MockObjectId()
        self.collections['users'].append({
            '_id': user_id,
            'email': 'demo@alphacreatorads.com',
            'username': 'demouser',
            'fullName': 'Demo User',
            'passwordHash': '$2b$12$demo.hash.for.development.only',
            'role': 'user',
            'subscription': {
                'plan': 'professional',
                'status': 'active',
                'startDate': datetime.utcnow() - timedelta(days=30),
                'endDate': datetime.utcnow() + timedelta(days=335)
            },
            'preferences': {
                'theme': 'light',
                'language': 'en',
                'notifications': {'email': True, 'push': True},
                'defaultCurrency': 'USD'
            },
            'apiUsage': {
                'adsGenerated': 25,
                'apiCallsThisMonth': 150,
                'quotaLimit': 1000
            },
            'createdAt': datetime.utcnow() - timedelta(days=30),
            'updatedAt': datetime.utcnow(),
            'isVerified': True,
            'isActive': True
        })
        
        # Sample campaigns
        campaign_id_1 = MockObjectId()
        campaign_id_2 = MockObjectId()
        
        self.collections['campaigns'].extend([
            {
                '_id': campaign_id_1,
                'userId': user_id,
                'name': 'Brand Awareness Q4 2024',
                'description': 'Holiday season brand awareness campaign',
                'objective': 'brand_awareness',
                'status': 'active',
                'budget': {'amount': 2000, 'currency': 'USD', 'type': 'total'},
                'targeting': {
                    'demographics': {'ageRange': '25-45', 'gender': 'all'},
                    'interests': ['marketing', 'business', 'technology'],
                    'locations': ['US', 'CA', 'UK']
                },
                'platforms': ['facebook', 'instagram', 'google'],
                'analytics': {
                    'impressions': 45000,
                    'clicks': 1350,
                    'conversions': 85,
                    'spent': 750.50,
                    'ctr': 3.0,
                    'cpc': 0.56,
                    'cpa': 8.83
                },
                'createdAt': datetime.utcnow() - timedelta(days=15),
                'updatedAt': datetime.utcnow() - timedelta(days=1)
            },
            {
                '_id': campaign_id_2,
                'userId': user_id,
                'name': 'Lead Generation Campaign',
                'description': 'B2B lead generation for SaaS products',
                'objective': 'lead_generation',
                'status': 'paused',
                'budget': {'amount': 1000, 'currency': 'USD', 'type': 'monthly'},
                'targeting': {
                    'demographics': {'ageRange': '30-55', 'gender': 'all'},
                    'interests': ['software', 'saas', 'business'],
                    'locations': ['US', 'CA']
                },
                'platforms': ['linkedin', 'google'],
                'analytics': {
                    'impressions': 15000,
                    'clicks': 450,
                    'conversions': 35,
                    'spent': 425.00,
                    'ctr': 3.0,
                    'cpc': 0.94,
                    'cpa': 12.14
                },
                'createdAt': datetime.utcnow() - timedelta(days=25),
                'updatedAt': datetime.utcnow() - timedelta(days=3)
            }
        ])
        
        # Sample ads
        ad_id_1 = MockObjectId()
        ad_id_2 = MockObjectId()
        
        self.collections['ads'].extend([
            {
                '_id': ad_id_1,
                'userId': user_id,
                'campaignId': campaign_id_1,
                'title': 'Transform Your Business with AI',
                'description': 'Discover how AI can revolutionize your marketing strategy',
                'type': 'promotional',
                'format': 'single_image',
                'status': 'active',
                'content': {
                    'headline': 'AI-Powered Marketing Revolution',
                    'primaryText': 'Join thousands of businesses using AI to boost ROI by 300%',
                    'callToAction': 'Learn More',
                    'images': ['https://example.com/ad-image-1.jpg']
                },
                'analytics': {
                    'impressions': 25000,
                    'clicks': 750,
                    'conversions': 45,
                    'spent': 420.00,
                    'ctr': 3.0,
                    'cpc': 0.56
                },
                'createdAt': datetime.utcnow() - timedelta(days=10),
                'updatedAt': datetime.utcnow() - timedelta(days=1)
            },
            {
                '_id': ad_id_2,
                'userId': user_id,
                'campaignId': campaign_id_2,
                'title': 'SaaS Growth Accelerator',
                'description': 'Scale your SaaS business faster than ever',
                'type': 'lead_generation',
                'format': 'video',
                'status': 'active',
                'content': {
                    'headline': 'Scale Your SaaS 10x Faster',
                    'primaryText': 'Get qualified leads and reduce acquisition costs',
                    'callToAction': 'Start Free Trial',
                    'videos': ['https://example.com/ad-video-1.mp4']
                },
                'analytics': {
                    'impressions': 12000,
                    'clicks': 360,
                    'conversions': 28,
                    'spent': 280.00,
                    'ctr': 3.0,
                    'cpc': 0.78
                },
                'createdAt': datetime.utcnow() - timedelta(days=8),
                'updatedAt': datetime.utcnow() - timedelta(days=2)
            }
        ])
        
        # Sample analytics data
        for i in range(30):  # Last 30 days
            date = datetime.utcnow() - timedelta(days=i)
            self.collections['analytics'].append({
                '_id': MockObjectId(),
                'userId': user_id,
                'campaignId': campaign_id_1,
                'adId': ad_id_1,
                'timestamp': date,
                'impressions': 800 + (i * 50),
                'clicks': 24 + (i * 2),
                'conversions': 2 + (i // 5),
                'spent': 15.50 + (i * 1.2),
                'platform': 'facebook'
            })

class MockCollection:
    """Mock MongoDB collection"""
    
    def __init__(self, data: List[Dict]):
        self.data = data
    
    async def find_one(self, query: Dict) -> Optional[Dict]:
        """Find single document"""
        for doc in self.data:
            if self._matches(doc, query):
                return doc
        return None
    
    def find(self, query: Dict = None, projection: Dict = None):
        """Find multiple documents"""
        query = query or {}
        results = [doc for doc in self.data if self._matches(doc, query)]
        return MockCursor(results, projection)
    
    async def insert_one(self, document: Dict):
        """Insert single document"""
        doc_id = MockObjectId()
        document['_id'] = doc_id
        self.data.append(document)
        return MockInsertResult(doc_id)
    
    async def update_one(self, query: Dict, update: Dict):
        """Update single document"""
        for i, doc in enumerate(self.data):
            if self._matches(doc, query):
                if '$set' in update:
                    doc.update(update['$set'])
                if '$inc' in update:
                    for key, value in update['$inc'].items():
                        keys = key.split('.')
                        current = doc
                        for k in keys[:-1]:
                            current = current.setdefault(k, {})
                        current[keys[-1]] = current.get(keys[-1], 0) + value
                return MockUpdateResult(1)
        return MockUpdateResult(0)
    
    async def delete_one(self, query: Dict):
        """Delete single document"""
        for i, doc in enumerate(self.data):
            if self._matches(doc, query):
                del self.data[i]
                return MockDeleteResult(1)
        return MockDeleteResult(0)
    
    async def count_documents(self, query: Dict = None) -> int:
        """Count documents"""
        query = query or {}
        return len([doc for doc in self.data if self._matches(doc, query)])
    
    def aggregate(self, pipeline: List[Dict]):
        """Aggregate operation (simplified)"""
        # Simplified aggregation for demo
        return MockCursor(self.data)
    
    def _matches(self, doc: Dict, query: Dict) -> bool:
        """Check if document matches query"""
        if not query:
            return True
        
        for key, value in query.items():
            if key.startswith('$'):
                continue  # Skip operators for now
            
            keys = key.split('.')
            current = doc
            
            try:
                for k in keys:
                    current = current[k]
                
                if current != value:
                    return False
            except (KeyError, TypeError):
                return False
        
        return True

class MockCursor:
    """Mock MongoDB cursor"""
    
    def __init__(self, data: List[Dict], projection: Dict = None):
        self.data = data
        self.projection = projection
        self._index = 0
    
    def sort(self, key: str, direction: int = 1):
        """Sort results"""
        reverse = direction == -1
        try:
            self.data.sort(key=lambda x: x.get(key, 0), reverse=reverse)
        except:
            pass
        return self
    
    def skip(self, count: int):
        """Skip documents"""
        self.data = self.data[count:]
        return self
    
    def limit(self, count: int):
        """Limit documents"""
        self.data = self.data[:count]
        return self
    
    async def to_list(self, length: int = None):
        """Convert to list"""
        return self.data[:length] if length else self.data
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if self._index >= len(self.data):
            raise StopAsyncIteration
        doc = self.data[self._index]
        self._index += 1
        return doc

class MockInsertResult:
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id

class MockUpdateResult:
    def __init__(self, modified_count):
        self.modified_count = modified_count

class MockDeleteResult:
    def __init__(self, deleted_count):
        self.deleted_count = deleted_count

# Global mock database instance
mock_db = MockDatabase()

async def get_mock_db():
    """Get mock database instance"""
    
    class MockDB:
        def __init__(self):
            self.users = MockCollection(mock_db.collections['users'])
            self.campaigns = MockCollection(mock_db.collections['campaigns'])
            self.ads = MockCollection(mock_db.collections['ads'])
            self.analytics = MockCollection(mock_db.collections['analytics'])
            self.ai_generations = MockCollection(mock_db.collections['ai_generations'])
            self.campaign_optimizations = MockCollection(mock_db.collections['campaign_optimizations'])
        
        async def command(self, cmd):
            """Mock database command"""
            return {"ok": 1}
    
    return MockDB()

def init_mock_database():
    """Initialize mock database"""
    logger = __import__('logging').getLogger(__name__)
    logger.info("✅ Mock database initialized with sample data")
    return mock_db