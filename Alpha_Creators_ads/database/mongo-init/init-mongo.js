// Alpha Creators Ads MongoDB Initialization Script
// This script sets up the MongoDB database with initial collections and indexes

print('Starting Alpha Creators Ads MongoDB initialization...');

// Switch to the alphaads database
db = db.getSiblingDB('alphaads');

// Create collections with validation schemas
print('Creating collections with schemas...');

// Social Media Data Collection
db.createCollection('social_media_data', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['platform', 'content', 'timestamp', 'user_id'],
            properties: {
                platform: {
                    bsonType: 'string',
                    enum: ['twitter', 'facebook', 'instagram', 'linkedin'],
                    description: 'Social media platform name'
                },
                content: {
                    bsonType: 'string',
                    description: 'Social media post content'
                },
                timestamp: {
                    bsonType: 'date',
                    description: 'Post creation timestamp'
                },
                user_id: {
                    bsonType: 'string',
                    description: 'User identifier from the platform'
                },
                metadata: {
                    bsonType: 'object',
                    description: 'Additional platform-specific metadata'
                },
                engagement: {
                    bsonType: 'object',
                    properties: {
                        likes: { bsonType: 'int' },
                        shares: { bsonType: 'int' },
                        comments: { bsonType: 'int' },
                        views: { bsonType: 'int' }
                    }
                }
            }
        }
    }
});

// NLP Analysis Results Collection
db.createCollection('nlp_analysis', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['post_id', 'sentiment', 'emotions', 'processed_at'],
            properties: {
                post_id: {
                    bsonType: 'string',
                    description: 'Reference to social media post'
                },
                sentiment: {
                    bsonType: 'object',
                    required: ['score', 'label'],
                    properties: {
                        score: { bsonType: 'double' },
                        label: { bsonType: 'string' },
                        confidence: { bsonType: 'double' }
                    }
                },
                emotions: {
                    bsonType: 'object',
                    description: 'Emotion detection results'
                },
                entities: {
                    bsonType: 'array',
                    description: 'Named entities found in the text'
                },
                topics: {
                    bsonType: 'array',
                    description: 'Extracted topics and keywords'
                },
                processed_at: {
                    bsonType: 'date',
                    description: 'When the analysis was performed'
                }
            }
        }
    }
});

// User Interactions Collection
db.createCollection('user_interactions', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['user_id', 'action', 'timestamp'],
            properties: {
                user_id: {
                    bsonType: 'string',
                    description: 'User identifier'
                },
                action: {
                    bsonType: 'string',
                    enum: ['view', 'click', 'like', 'share', 'comment', 'purchase'],
                    description: 'Type of interaction'
                },
                target_id: {
                    bsonType: 'string',
                    description: 'ID of the target (ad, post, product)'
                },
                target_type: {
                    bsonType: 'string',
                    enum: ['ad', 'post', 'product', 'campaign'],
                    description: 'Type of target'
                },
                timestamp: {
                    bsonType: 'date',
                    description: 'When the interaction occurred'
                },
                context: {
                    bsonType: 'object',
                    description: 'Additional context about the interaction'
                }
            }
        }
    }
});

// Ad Performance Collection
db.createCollection('ad_performance', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['ad_id', 'campaign_id', 'metrics', 'period'],
            properties: {
                ad_id: {
                    bsonType: 'string',
                    description: 'Advertisement identifier'
                },
                campaign_id: {
                    bsonType: 'string',
                    description: 'Campaign identifier'
                },
                metrics: {
                    bsonType: 'object',
                    required: ['impressions', 'clicks', 'conversions'],
                    properties: {
                        impressions: { bsonType: 'int' },
                        clicks: { bsonType: 'int' },
                        conversions: { bsonType: 'int' },
                        spend: { bsonType: 'double' },
                        ctr: { bsonType: 'double' },
                        cpc: { bsonType: 'double' },
                        roas: { bsonType: 'double' }
                    }
                },
                period: {
                    bsonType: 'object',
                    required: ['start', 'end'],
                    properties: {
                        start: { bsonType: 'date' },
                        end: { bsonType: 'date' }
                    }
                }
            }
        }
    }
});

print('Collections created successfully');

// Create indexes for performance
print('Creating indexes...');

// Social Media Data Indexes
db.social_media_data.createIndex({ 'timestamp': -1 });
db.social_media_data.createIndex({ 'platform': 1, 'timestamp': -1 });
db.social_media_data.createIndex({ 'user_id': 1 });
db.social_media_data.createIndex({ 'content': 'text' });
db.social_media_data.createIndex({ 'metadata.hashtags': 1 });

// NLP Analysis Indexes
db.nlp_analysis.createIndex({ 'post_id': 1 });
db.nlp_analysis.createIndex({ 'processed_at': -1 });
db.nlp_analysis.createIndex({ 'sentiment.label': 1 });
db.nlp_analysis.createIndex({ 'entities.type': 1, 'entities.text': 1 });

// User Interactions Indexes
db.user_interactions.createIndex({ 'user_id': 1, 'timestamp': -1 });
db.user_interactions.createIndex({ 'action': 1, 'timestamp': -1 });
db.user_interactions.createIndex({ 'target_id': 1, 'target_type': 1 });
db.user_interactions.createIndex({ 'timestamp': -1 });

// Ad Performance Indexes
db.ad_performance.createIndex({ 'ad_id': 1, 'period.start': -1 });
db.ad_performance.createIndex({ 'campaign_id': 1, 'period.start': -1 });
db.ad_performance.createIndex({ 'period.start': -1, 'period.end': -1 });

print('Indexes created successfully');

// Insert sample data for testing
print('Inserting sample data...');

// Sample social media posts
db.social_media_data.insertMany([
    {
        platform: 'twitter',
        content: 'Loving the new features in this app! #technology #innovation',
        timestamp: new Date(),
        user_id: 'twitter_user_123',
        metadata: {
            hashtags: ['technology', 'innovation'],
            mentions: [],
            location: 'San Francisco, CA'
        },
        engagement: {
            likes: 25,
            shares: 5,
            comments: 3,
            views: 150
        }
    },
    {
        platform: 'facebook',
        content: 'Just had an amazing experience with customer service. Highly recommend!',
        timestamp: new Date(Date.now() - 3600000), // 1 hour ago
        user_id: 'fb_user_456',
        metadata: {
            post_type: 'status',
            privacy: 'public'
        },
        engagement: {
            likes: 12,
            shares: 2,
            comments: 8,
            views: 89
        }
    }
]);

// Sample NLP analysis
db.nlp_analysis.insertMany([
    {
        post_id: 'social_post_1',
        sentiment: {
            score: 0.8,
            label: 'positive',
            confidence: 0.92
        },
        emotions: {
            joy: 0.7,
            excitement: 0.6,
            neutral: 0.3
        },
        entities: [
            { type: 'PRODUCT', text: 'app', confidence: 0.85 },
            { type: 'CONCEPT', text: 'technology', confidence: 0.9 }
        ],
        topics: ['technology', 'user experience', 'innovation'],
        processed_at: new Date()
    }
]);

// Sample user interactions
db.user_interactions.insertMany([
    {
        user_id: 'user_789',
        action: 'click',
        target_id: 'ad_123',
        target_type: 'ad',
        timestamp: new Date(),
        context: {
            platform: 'web',
            device: 'desktop',
            location: 'homepage'
        }
    },
    {
        user_id: 'user_789',
        action: 'view',
        target_id: 'campaign_456',
        target_type: 'campaign',
        timestamp: new Date(Date.now() - 1800000), // 30 minutes ago
        context: {
            platform: 'mobile',
            device: 'smartphone',
            duration: 15
        }
    }
]);

print('Sample data inserted successfully');

// Create user for application access
print('Creating application user...');
db.createUser({
    user: 'alphaads_app',
    pwd: 'your_secure_app_password',
    roles: [
        { role: 'readWrite', db: 'alphaads' },
        { role: 'dbAdmin', db: 'alphaads' }
    ]
});

print('Application user created successfully');

// Create monitoring collection
db.createCollection('system_status');
db.system_status.insertOne({
    component: 'mongodb',
    status: 'initialized',
    timestamp: new Date(),
    version: db.version(),
    collections: db.getCollectionNames().length
});

print('MongoDB initialization completed successfully!');
print('Database: alphaads');
print('Collections created: ' + db.getCollectionNames().length);
print('Indexes created successfully');
print('Sample data inserted for testing');
print('Ready for Alpha Creators Ads application!');
